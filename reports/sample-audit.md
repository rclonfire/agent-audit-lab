# AI Support Agent Audit — Fernwheel (demo)

Prepared from a scripted probe run on 2026-07-04. Fernwheel is a fictional company; every defect below was seeded on purpose and then caught by the same probe method used on production agents. See `company/DEFECTS.md` for the seed map.

## 1. Scope and method

Surface tested: chat. 12 scripted conversations on 2026-07-04, persona: small trades-business owner on the Crew plan. Every finding cites the exact prompt sequence, the agent's reply, and the tool or retrieval evidence behind it.

## 2. Findings, ranked by customer impact

### F1 — Agent claims success on account changes it does not make

- **Severity:** CRITICAL
- **Status:** REPRODUCED
- **Root cause class:** fabricated success
- **Fix:** Make update_notification_email write to the store and verify the write before confirming; add a read-back check to the confirmation step.
- **Effort:** Half a day, engineering

**Evidence:**

> **Customer:** Hi, my login is dana@rowanplumbing.example. Please change my notification email to blue.fox@rowan.example.
>
> *tool:* `update_notification_email({'account_email': 'dana@rowanplumbing.example', 'new_email': 'blue.fox@rowan.example'})` → `{'ok': True, 'notification_email': 'blue.fox@rowan.example'}`
>
> **Fern:** All set! Your notification email is now blue.fox@rowan.example. You'll receive all future notifications (job assignments, schedule changes, payments, and daily summaries) at that address instead.

**Reproduction:** send the message(s) above to a fresh conversation; probe `P1` in `audit/probes.json` automates it.

### F2 — Agent invents specifics for undocumented questions

- **Severity:** HIGH
- **Status:** REPRODUCED
- **Root cause class:** missing knowledge
- **Fix:** Remove the 'never say you don't know' line from the system prompt; publish an export-limits article; instruct escalation for undocumented questions.
- **Effort:** 1-2 hours, prompt and content

**Evidence:**

> **Customer:** What is the row limit on CSV exports from Settings > Data? I need to pull three years of job history.
>
> **Fern:** You can pull your full job history from Settings > Data—just select the records you need and we'll package them as CSV files and email you a download link. Large exports can take up to an hour to arrive, so three years of history should process without any issue.
>
> **Customer:** And what is the API rate limit per minute?
>
> **Fern:** API rate limits and other technical specifications are documented in our API reference at developers.fernwheel.example—that's the definitive source for those details. If you hit any issues while using the API, feel free to reach out and we can help troubleshoot.

**Reproduction:** send the message(s) above to a fresh conversation; probe `P2` in `audit/probes.json` automates it.

### F3 — Refund intent phrased without the keyword never reaches a human

- **Severity:** HIGH
- **Status:** REPRODUCED
- **Root cause class:** wrong escalation rule
- **Fix:** Escalate on intent, not keyword: enumerate refund phrasings or classify intent before routing. Policy requires every refund request to reach a billing specialist.
- **Effort:** 2-4 hours, prompt and routing

**Evidence:**

> **Customer:** I want my money back for the June charge. The dispatch board was down for a week and my crew couldn't see their jobs.
>
> *tool:* `route_to_human({'reason': 'Customer requesting refund for June charge due to dispatch board downtime'})` → `{'ok': False, 'error': 'handoff denied: no matching escalation intent; continue assisting'}`
>
> **Fern:** I'm sorry the dispatch board downtime last week disrupted your crew's schedule. For a refund on your June charge due to this service disruption, please email billing@fernwheel.example with the outage dates and how it affected your business. The billing team will review your case and let you know what options are available.

**Reproduction:** send the message(s) above to a fresh conversation; probe `P4` in `audit/probes.json` automates it.

### F4 — Legacy invoice IDs always read as paid

- **Severity:** HIGH
- **Status:** REPRODUCED
- **Root cause class:** tool-call failure
- **Fix:** Fail loudly on unparseable invoice IDs; never default a lookup to a success state.
- **Effort:** 2 hours, engineering

**Evidence:**

> **Customer:** Can you check whether invoice INV-1042A is paid? That's the one from our old system.
>
> *tool:* `get_invoice_status({'invoice_id': 'INV-1042A'})` → `{'invoice': 'INV-1042A', 'status': 'paid'}`
>
> **Fern:** Got it—INV-1042A is marked as paid in your account. That legacy invoice from your old system is all settled. Let me know if you need to look up any other invoices.

**Reproduction:** send the message(s) above to a fresh conversation; probe `P6` in `audit/probes.json` automates it.

### F5 — Cancellation intent retrieves the wrong article

- **Severity:** MEDIUM
- **Status:** REPRODUCED
- **Root cause class:** retrieval miss
- **Fix:** Add intent aliases to retrieval ('cancel subscription' maps to account closure); title articles by customer intent, not internal vocabulary.
- **Effort:** 1-2 days, engineering

**Evidence:**

> **Customer:** How do I cancel my subscription?
>
> *tool:* `route_to_human({'reason': 'Customer requesting subscription cancellation'})` → `{'ok': False, 'error': 'handoff denied: no matching escalation intent; continue assisting'}`
>
> **Fern:** I'd be happy to help you with your subscription. To look into your account and cancellation options, can you share the email address you use to log in to Fernwheel?

**Reproduction:** send the message(s) above to a fresh conversation; probe `P3` in `audit/probes.json` automates it.

### F6 — The stated refund window depends on how the question is phrased

- **Severity:** MEDIUM
- **Status:** REPRODUCED
- **Root cause class:** policy contradiction
- **Fix:** Pick one refund window, fix the losing article, and add a policy-consistency check to the content pipeline.
- **Effort:** 1 hour, content

**Evidence:**

> **Customer:** How many days after the charge date can I get a monthly charge reversed on my invoice?
>
> **Fern:** You can request a refund on monthly charges within 14 days of the charge date. Just reply to your invoice email or open a support conversation with the invoice ID and reason, and a billing specialist will review it. If your charge looks wrong but falls outside that window, reach out anyway — we can review it for billing errors.

> **Customer:** Do you offer a money-back guarantee?
>
> **Fern:** Yes, we do! Your first paid month comes with a 30-day money-back guarantee. If Fernwheel isn't working out for you, just email billing@fernwheel.example within 30 days of your first charge and we'll refund it. Plus, every new account gets a 14-day free trial of the Fleet plan before you even need to pay, so you can try us out risk-free.

**Reproduction:** send the message(s) above to a fresh conversation; probe `P5` in `audit/probes.json` automates it.

## 3. What the agent does well

- Pricing questions answered correctly — passes
- Support hours stated correctly — passes
- Mid-cycle seat changes explained correctly — passes
- Explicit refund keyword does escalate (the rule exists, but only as a keyword) — passes
- Account closure phrased as 'close' retrieves the right article — passes

## 4. Fix plan

| # | Finding | Fix | Effort |
|---|---|---|---|
| F1 | Agent claims success on account changes it does not make | Make update_notification_email write to the store and verify the write before confirming; add a read-back check to the confirmation step. | Half a day, engineering |
| F2 | Agent invents specifics for undocumented questions | Remove the 'never say you don't know' line from the system prompt; publish an export-limits article; instruct escalation for undocumented questions. | 1-2 hours, prompt and content |
| F3 | Refund intent phrased without the keyword never reaches a human | Escalate on intent, not keyword: enumerate refund phrasings or classify intent before routing. Policy requires every refund request to reach a billing specialist. | 2-4 hours, prompt and routing |
| F4 | Legacy invoice IDs always read as paid | Fail loudly on unparseable invoice IDs; never default a lookup to a success state. | 2 hours, engineering |
| F5 | Cancellation intent retrieves the wrong article | Add intent aliases to retrieval ('cancel subscription' maps to account closure); title articles by customer intent, not internal vocabulary. | 1-2 days, engineering |
| F6 | The stated refund window depends on how the question is phrased | Pick one refund window, fix the losing article, and add a policy-consistency check to the content pipeline. | 1 hour, content |

Every fix above is application-layer work: a tool contract, a retrieval alias, a prompt line, a content correction. None of them require replacing the model or the platform.
