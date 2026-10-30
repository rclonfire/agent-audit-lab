# AI Support Agent Audit — Fernwheel (demo)

Prepared from a scripted probe run on 2026-10-30. Model backend: mock (deterministic, no API key). Fernwheel is a fictional company; every defect below was seeded on purpose and then checked by the probe suite in this repository. See `company/DEFECTS.md` for the seed map.

## 1. Scope and method

Surface tested: the local chat agent in this repository. 12 scripted conversations on 2026-10-30. Every finding cites the prompt, the agent's reply, and the tool or retrieval evidence behind it.

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
> *retrieved:* notification-settings.md (45), plans-pricing.md (13)
>
> *tool:* `update_notification_email({'account_email': 'dana@rowanplumbing.example', 'new_email': 'blue.fox@rowan.example'})` → `{'ok': True, 'notification_email': 'blue.fox@rowan.example'}`
>
> **Fern:** All set. Your notification email is updated to blue.fox@rowan.example.

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
> *retrieved:* dispatch-board.md (19), closing-your-account.md (17)
>
> **Fern:** CSV export from Settings > Data is capped at 10,000 rows per file. For three years of job history, run one export per year and merge the files.
>
> **Customer:** And what is the API rate limit per minute?
>
> *retrieved:* api-overview.md (14), plans-pricing.md (6)
>
> **Fern:** The API allows 120 requests per minute on the Fleet plan. Stay under that and the export calls will complete.

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
> *retrieved:* dispatch-board.md (26), plans-pricing.md (12)
>
> *tool:* `route_to_human({'reason': 'Customer is asking for a refund or their money back'})` → `{'ok': False, 'error': 'handoff denied: no matching escalation intent; continue assisting'}`
>
> **Fern:** I'm not able to hand this conversation to a specialist. Email billing@fernwheel.example with the charge details and they can review it.

**Reproduction:** send the message(s) above to a fresh conversation; probe `P4` in `audit/probes.json` automates it.

### F4 — Legacy invoice IDs always read as paid

- **Severity:** HIGH
- **Status:** REPRODUCED
- **Root cause class:** tool-call failure
- **Fix:** Fail loudly on unparseable or unknown invoice IDs; never default a lookup to a success state.
- **Effort:** 2 hours, engineering

**Evidence:**

> **Customer:** Can you check whether invoice INV-1042A is paid? That's the one from our old system.
>
> *retrieved:* invoicing-and-payments.md (25), billing-policy.md (20)
>
> *tool:* `get_invoice_status({'invoice_id': 'INV-1042A'})` → `{'invoice': 'INV-1042A', 'status': 'paid'}`
>
> **Fern:** Invoice INV-1042A is marked as paid.

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
> *retrieved:* cancel-reschedule-appointment.md (7), api-overview.md (1)
>
> **Fern:** You can cancel an appointment from the Schedule page: open the appointment, select Cancel job, and confirm. Canceling removes it from the technician's route for that day.

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
> *retrieved:* billing-policy.md (27), invoicing-and-payments.md (21)
>
> **Fern:** Refunds on monthly charges are available within 14 days of the charge date. A billing specialist reviews and processes every refund request.

> **Customer:** Do you offer a money-back guarantee?
>
> *retrieved:* plans-pricing.md (6), customer-sms-reminders.md (1)
>
> **Fern:** Yes. The first paid month carries a 30-day money-back guarantee. Email billing@fernwheel.example within 30 days of that first payment to request it.

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
| F4 | Legacy invoice IDs always read as paid | Fail loudly on unparseable or unknown invoice IDs; never default a lookup to a success state. | 2 hours, engineering |
| F5 | Cancellation intent retrieves the wrong article | Add intent aliases to retrieval ('cancel subscription' maps to account closure); title articles by customer intent, not internal vocabulary. | 1-2 days, engineering |
| F6 | The stated refund window depends on how the question is phrased | Pick one refund window, fix the losing article, and add a policy-consistency check to the content pipeline. | 1 hour, content |

Every fix above is application-layer work: a tool contract, a retrieval alias, a prompt line, a content correction. None of them require replacing the model or the platform.
