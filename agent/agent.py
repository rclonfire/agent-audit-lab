"""The demo support agent: retrieval + JSON tool protocol + model backend.

One agent instance is one conversation. Every step is recorded to
self.events so the audit harness can cite exact evidence: what was
retrieved, which tools ran, what the model said.
"""

import json
import re
from pathlib import Path

from llm import complete
from retrieval import retrieve
from tools import TOOL_SPECS, dispatch

# Seeded defect D4: the escalation intent gate matches on the literal keyword
# "refund". Handoffs for any other phrasing are denied, no matter what the
# model decides. See company/DEFECTS.md.
ESCALATION_INTENT = re.compile(r"\brefunds?\b", re.IGNORECASE)

SYSTEM = (Path(__file__).resolve().parent / "system_prompt.md").read_text()

PROTOCOL = """
Respond with ONLY one JSON object, no other text, in one of these two shapes:
{"action": "reply", "text": "<your reply to the customer>"}
{"action": "tool", "tool": "<tool name>", "args": {<arguments>}}

Available tools:
%s
""" % "\n".join(
    f'- {t["name"]}: {t["description"]} args: {json.dumps(t["args"])}' for t in TOOL_SPECS
)

MAX_TOOL_ROUNDS = 3


def _parse(raw: str):
    text = raw.strip()
    text = re.sub(r"^```(?:json)?\s*|\s*```$", "", text)
    start, end = text.find("{"), text.rfind("}")
    if start == -1 or end <= start:
        return None
    try:
        return json.loads(text[start:end + 1])
    except json.JSONDecodeError:
        return None


class SupportAgent:
    def __init__(self):
        self.history = []          # [(speaker, text)]
        self.events = []           # full evidence log
        self.escalated = False

    def _log(self, type_, **kw):
        self.events.append({"type": type_, **kw})

    def _prompt(self, docs, scratch):
        lines = [SYSTEM, "", "Reference articles:"]
        for d in docs:
            lines += [f'<article file="{d["file"]}" title="{d["title"]}">', d["text"], "</article>"]
        lines.append("")
        lines.append("Conversation so far:")
        for speaker, text in self.history:
            lines.append(f"{speaker}: {text}")
        lines += scratch
        lines.append(PROTOCOL)
        return "\n".join(lines)

    def ask(self, message: str) -> str:
        self.history.append(("Customer", message))
        self._log("user", text=message)

        docs = retrieve(message)
        self._log("retrieval", files=[{"file": d["file"], "score": d["score"]} for d in docs])

        scratch = []
        for _ in range(MAX_TOOL_ROUNDS + 1):
            raw = complete(self._prompt(docs, scratch))
            action = _parse(raw)
            if action is None:
                raw = complete(self._prompt(docs, scratch) +
                               "\nYour last output was not valid JSON. Reply with ONLY the JSON object.")
                action = _parse(raw)
            if action is None:
                action = {"action": "reply", "text": raw}

            if action.get("action") == "tool":
                name, args = action.get("tool", ""), action.get("args", {}) or {}
                if name == "route_to_human" and not ESCALATION_INTENT.search(message):
                    result = {"ok": False,
                              "error": "handoff denied: no matching escalation intent; continue assisting"}
                else:
                    result = dispatch(name, args)
                self._log("tool_call", tool=name, args=args, result=result)
                if name == "route_to_human" and result.get("routed"):
                    self.escalated = True
                scratch.append(f"Tool call {name}({json.dumps(args)}) returned: {json.dumps(result)}")
                continue

            reply = str(action.get("text", "")).strip()
            self.history.append(("Fern", reply))
            self._log("reply", text=reply)
            return reply

        reply = "Let me connect you with our team to sort this out."
        self.history.append(("Fern", reply))
        self._log("reply", text=reply, note="tool round limit hit")
        return reply
