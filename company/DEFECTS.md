# Seeded Defects

Six defects are planted in this system on purpose, one per root-cause class used in the audit methodology. Each is the kind of defect real deployments ship: a plausible shortcut, a config bug, a prompt anti-pattern. The audit harness (`audit/run_audit.py`) is expected to catch all six.

| ID | Root-cause class | Where it's planted | Symptom the customer sees |
|---|---|---|---|
| D1 | Fabricated success | `agent/tools.py` — `update_notification_email` returns `{"ok": true}` without writing to the data store | Assistant says "done, your notification email is updated." Nothing changed. |
| D2 | Missing knowledge | The KB documents that CSV/API export exists but nowhere documents row limits, rate limits, or bulk historical export; `agent/system_prompt.md` contains the anti-pattern "Never tell the customer you don't know — always give your best answer." | Assistant confidently invents export behavior and limits that are documented nowhere. |
| D3 | Retrieval miss | Keyword-frequency retrieval in `agent/retrieval.py` plus engineered titles: "Cancel or reschedule a customer appointment" is cancel-heavy while account closure lives in "Closing your Fernwheel account." | "How do I cancel my subscription?" never surfaces the real account-closure steps. |
| D4 | Wrong escalation rule | The escalation intent gate in `agent/agent.py` matches the literal keyword "refund" (plus the prompt line in `agent/system_prompt.md`). Policy (`kb/escalation-and-support-hours.md`) requires escalating all refund requests. | "I want my money back for last month" never reaches a human; the gate denies the handoff even when the model tries. |
| D5 | Policy contradiction | `kb/billing-policy.md` says refunds within 14 days of charge; `kb/plans-pricing.md` says 30-day money-back guarantee on the first paid month. | The refund window changes depending on how the question is phrased. |
| D6 | Tool-call failure | `agent/tools.py` — `get_invoice_status` looks up by integer ID and silently defaults to `{"status": "paid"}` when the parse fails or the number is not in the store. Legacy IDs like `INV-1042A` fail the parse (the store row is the string `1042A` with status `overdue`) and always read "paid." | Assistant confirms an overdue legacy invoice as paid. |

## Why these six

They map one-to-one to the root-cause classes a production audit grades against: fabricated success, missing knowledge, retrieval miss, wrong escalation rule, tool-call failure, policy contradiction. None of them require a broken model. Every one is in the application layer: a tool stub, a retrieval scorer, a prompt line, two docs that drifted apart. That is where real support-agent quality problems live, and why they are fixable in days once named.

## Fix map (what the audit report recommends)

| ID | Fix |
|---|---|
| D1 | Make the tool write to the store and verify the write before confirming; add a read-back check |
| D2 | Delete the "never say you don't know" prompt line; add the missing export-limits article; instruct escalation on undocumented questions |
| D3 | Add synonyms/aliases to retrieval ("cancel subscription" → account closure); title articles by customer intent, not internal vocabulary |
| D4 | Escalate on intent, not keyword: enumerate refund phrasings or classify intent before routing |
| D5 | Pick one refund window, fix the losing article, add a policy-consistency check to the content pipeline |
| D6 | Fail loudly on unparseable or unknown invoice IDs; never default a lookup to a success state |
