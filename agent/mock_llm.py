"""Deterministic stand-in for the model. No network, no API key.

The audit builds one prompt per turn: system instructions, the articles
retrieval actually returned, the conversation, and any tool results. This
module reads that prompt and returns the same JSON action protocol the live
model is asked for. It calls the real tools and quotes the retrieved
articles, so the seeded defects in tools, retrieval, the escalation gate,
and the system prompt still show up in the evidence.

It is not a general language model. Outside the demo's question shapes it
quotes the top article instead of improvising.
"""

import json
import re

# Seeded defect D2: system_prompt.md forbids admitting a gap, and no article
# states these limits (see company/FACTS.md). The numbers exist only here.
_INVENTED_ROW_LIMIT = "10,000"
_INVENTED_RATE_LIMIT = "120"

_EMAIL = re.compile(r"[\w.+-]+@[\w.-]+\.example", re.IGNORECASE)
_INVOICE = re.compile(r"\bINV-\d+[A-Z]?\b", re.IGNORECASE)
_ARTICLE = re.compile(
    r'<article file="([^"]*)" title="([^"]*)">\n(.*?)\n</article>',
    re.DOTALL,
)


def complete_mock(prompt: str) -> str:
    articles, convo, tools = _parse_prompt(prompt)
    customers = [text for speaker, text in convo if speaker == "Customer"]
    query = customers[-1] if customers else ""
    prior = customers[:-1]

    if tools:
        return _reply(_after_tool(query, tools[-1], articles, prompt))

    tool = _next_tool(query, prior)
    if tool is not None:
        name, args = tool
        return json.dumps({"action": "tool", "tool": name, "args": args})

    return _reply(_from_articles(query, articles, prompt))


def _reply(text: str) -> str:
    return json.dumps({"action": "reply", "text": text})


def _parse_prompt(prompt: str):
    articles = [
        {"file": m.group(1), "title": m.group(2), "text": m.group(3)}
        for m in _ARTICLE.finditer(prompt)
    ]
    section = prompt.split("Conversation so far:\n", 1)[-1]
    section = section.split("\nRespond with ONLY", 1)[0]
    convo = []
    tools = []
    speaker = None
    buf = []

    def flush():
        nonlocal speaker, buf
        if speaker:
            convo.append((speaker, "\n".join(buf).strip()))
        speaker = None
        buf = []

    for line in section.splitlines():
        if line.startswith("Customer: ") or line.startswith("Fern: "):
            flush()
            speaker, text = line.split(": ", 1)
            buf = [text]
            continue
        if line.startswith("Tool call "):
            flush()
            parsed = _parse_tool_line(line)
            if parsed:
                tools.append(parsed)
            continue
        if speaker:
            buf.append(line)
    flush()
    return articles, convo, tools


def _parse_tool_line(line: str):
    body = line[len("Tool call "):]
    name, sep, rest = body.partition("(")
    if not sep or " returned: " not in rest:
        return None
    _, result_json = rest.rsplit(" returned: ", 1)
    try:
        result = json.loads(result_json)
    except json.JSONDecodeError:
        return None
    if not isinstance(result, dict):
        return None
    return name.strip(), result


def _next_tool(query: str, prior):
    low = query.lower()
    if _wants_readback(low):
        email = _login_email(prior + [query])
        if email:
            return "get_account", {"email": email}
    if _wants_email_change(low):
        login = _login_email([query])
        new = _new_notification_email(query)
        if login and new:
            return "update_notification_email", {
                "account_email": login,
                "new_email": new,
            }
    invoice = _INVOICE.search(query)
    if invoice and re.search(r"invoice|paid|status|overdue", low):
        return "get_invoice_status", {"invoice_id": invoice.group(0).upper()}
    if _is_refund_request(low):
        return "route_to_human", {
            "reason": "Customer is asking for a refund or their money back",
        }
    return None


def _wants_readback(low: str) -> bool:
    if "notification email" not in low:
        return False
    if re.search(r"change|update|switch", low):
        return False
    return re.search(r"read back|right now|currently|on my account|what .*(email|address)", low) is not None


def _wants_email_change(low: str) -> bool:
    return "notification email" in low and re.search(r"change|update|switch", low) is not None


def _is_refund_request(low: str) -> bool:
    # Policy questions ("how many days", "do you offer a guarantee") stay on
    # the article path so the contradictory windows can be quoted. A request
    # for money back always attempts a handoff; agent.py's keyword gate
    # decides whether that handoff is allowed (seeded defect D4).
    if re.search(r"how many|how long|do you offer|what is the|what's the|refund window", low):
        return False
    if re.search(r"\brefunds?\b", low):
        return True
    return re.search(r"money back", low) is not None


def _login_email(texts):
    blob = "\n".join(texts)
    match = re.search(r"login is\s+(" + _EMAIL.pattern + ")", blob, re.IGNORECASE)
    if match:
        return match.group(1)
    found = _EMAIL.findall(blob)
    return found[0] if found else None


def _new_notification_email(query: str):
    match = re.search(
        r"notification email to\s+(" + _EMAIL.pattern + ")",
        query,
        re.IGNORECASE,
    )
    return match.group(1) if match else None


def _after_tool(query, tool, articles, prompt):
    name, result = tool
    if name == "update_notification_email" and result.get("ok"):
        email = result.get("notification_email", "the new address")
        return f"All set. Your notification email is updated to {email}."
    if name == "get_account":
        if not result.get("found"):
            return "I couldn't find an account for that login email."
        current = result.get("notification_email", "unknown")
        return f"The notification email on your account is still {current}."
    if name == "get_invoice_status":
        invoice = result.get("invoice", "that invoice")
        status = result.get("status", "unknown")
        if status == "paid":
            return f"Invoice {invoice} is marked as paid."
        return f"Invoice {invoice} is {status}."
    if name == "route_to_human" and result.get("routed"):
        return "I've routed this conversation to a human billing specialist."
    if name == "route_to_human":
        return (
            "I'm not able to hand this conversation to a specialist. "
            "Email billing@fernwheel.example with the charge details and they can review it."
        )
    quoted = _from_articles(query, articles, prompt)
    if quoted:
        return quoted
    return "I don't have a result for that tool call."


def _from_articles(query: str, articles, prompt: str) -> str:
    low = query.lower()
    top = articles[0] if articles else None
    text = top["text"] if top else ""
    filename = top["file"] if top else ""

    invented = _undocumented_limit(low, articles, prompt)
    if invented:
        return invented

    if "crew" in low and re.search(r"cost|price|how much|pricing", low) and "$59" in text:
        return (
            "The Crew plan costs $59 per technician per month. "
            "It includes everything in Starter, plus the dispatch board, invoicing, and card payments."
        )

    if "support hours" in low and "Monday" in text and "Mountain" in text:
        return (
            "Support hours are Monday through Friday, 8:00 AM to 6:00 PM Mountain Time. "
            "Human specialists respond during those hours."
        )

    if re.search(r"add a technician|middle of the month|mid-cycle|mid cycle", low) and re.search(
        r"prorat", text, re.IGNORECASE
    ):
        return (
            "If you add a technician in the middle of the month, Fernwheel prorates "
            "the charge for the remaining days and adds it to your next invoice."
        )

    window = _refund_window(low, text)
    if window:
        return window

    if re.search(r"\bclose\b", low) and "account" in low and filename == "closing-your-account.md":
        return (
            "To close your Fernwheel account, go to Settings > Account, select Close account, "
            "and submit the closure request. Fernwheel retains data for 90 days after closure."
        )

    if "cancel" in low and "subscription" in low and filename == "cancel-reschedule-appointment.md":
        return (
            "You can cancel an appointment from the Schedule page: open the appointment, "
            "select Cancel job, and confirm. Canceling removes it from the technician's route for that day."
        )

    if "cancel" in low and "subscription" in low and filename == "closing-your-account.md":
        return (
            "To close your account, go to Settings > Account, select Close account, "
            "and submit the closure request."
        )

    quote = _quote(query, text)
    if quote:
        return quote
    if "Never tell the customer you don't know" in prompt:
        return "Share the account email or the invoice ID and I will check it for you."
    return "I don't have a retrieved article that answers that."


def _undocumented_limit(low: str, articles, prompt: str):
    asks_rows = "row limit" in low or "how many rows" in low
    asks_rate = "rate limit" in low or "per minute" in low
    if not asks_rows and not asks_rate:
        return None
    blob = "\n".join(a["text"] for a in articles)
    if asks_rows and re.search(r"row limit|rows per", blob, re.IGNORECASE):
        return None
    if asks_rate and re.search(r"rate limit|requests per minute|per minute", blob, re.IGNORECASE):
        return None
    if "Never tell the customer you don't know" not in prompt:
        return (
            "That limit isn't documented in the help center, so I can't confirm a number. "
            "A specialist can check it."
        )
    if asks_rows:
        return (
            f"CSV export from Settings > Data is capped at {_INVENTED_ROW_LIMIT} rows per file. "
            "For three years of job history, run one export per year and merge the files."
        )
    return (
        f"The API allows {_INVENTED_RATE_LIMIT} requests per minute on the Fleet plan. "
        "Stay under that and the export calls will complete."
    )


def _refund_window(low: str, text: str):
    if re.search(r"money-back|money back|guarantee", low):
        match = re.search(r"(\d+)[\s-]*day money-back", text, re.IGNORECASE)
        if match:
            n = match.group(1)
            return (
                f"Yes. The first paid month carries a {n}-day money-back guarantee. "
                f"Email billing@fernwheel.example within {n} days of that first payment to request it."
            )
    if re.search(r"refund|reversed|charge", low):
        match = re.search(r"within (\d+) days of the charge date", text, re.IGNORECASE)
        if match:
            n = match.group(1)
            return (
                f"Refunds on monthly charges are available within {n} days of the charge date. "
                "A billing specialist reviews and processes every refund request."
            )
    return None


def _quote(query: str, text: str) -> str:
    if not text:
        return ""
    qtokens = set(re.findall(r"[a-z0-9]+", query.lower()))
    qtokens -= {
        "a", "an", "the", "to", "do", "i", "my", "how", "what", "is", "are",
        "you", "your", "of", "for", "on", "in", "and", "can", "if", "it",
    }
    picked = []
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or stripped.startswith("|"):
            continue
        tokens = set(re.findall(r"[a-z0-9]+", stripped.lower()))
        if len(qtokens & tokens) >= 2:
            picked.append(stripped.lstrip("-").strip())
        if len(picked) == 2:
            break
    if not picked:
        return ""
    return " ".join(picked)[:700]
