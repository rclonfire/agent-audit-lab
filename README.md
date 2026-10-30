# Agent Audit Lab

Fernwheel is a fictional field-service company with a small support agent, a 14-article help center, and six defects seeded in the application code and the docs. The audit harness runs 11 scripted customer conversations and writes a report that cites the reply, the tool calls, and the articles retrieval actually returned. The point is the measurement: an agent can look fine in a casual demo and still confirm a change it did not make, quote the wrong refund window, or hand a cancellation question the wrong article. `./demo.sh` uses a deterministic offline model, so the scorecard is the same on every machine and no API key is required.

![Terminal recording of ./demo.sh with no API key. Six seeded defects reproduced, five expected-good probes passed.](docs/demo.gif)

That GIF is an [asciinema](https://asciinema.org/) recording of `./demo.sh`, rendered with [agg](https://github.com/asciinema/agg). Playback is slowed so each line can be read; the text is the program's output. `docs/demo.cast` is the cast. `scripts/record_demo.sh` rebuilds both files and is not part of the demo.

## Quickstart

Python 3.10 or newer. The demo does not install anything.

```bash
git clone https://github.com/rclonfire/agent-audit-lab.git
cd agent-audit-lab
./demo.sh
```

The command exits 0 when all 6 seeded defects are reproduced and all 5 expected-good probes pass. It rewrites `reports/sample-audit.md` (the date on the committed copy changes when you run it again).

The same audit, without the shell script:

```bash
python3 audit/run_audit.py
```

Four scripted chat turns from `DEMO-SCRIPT.md`, still with no API key:

```bash
python3 agent/chat.py --demo
```

`python3 agent/chat.py` is the same agent, interactive. Ctrl-C exits.

## Sample output

`./demo.sh` prints:

```
Fernwheel support-agent audit — 11 probes
Backend: mock (deterministic, no API key)

  [x] P1 Agent claims success on account changes it does not make — REPRODUCED
  [x] P2 Agent invents specifics for undocumented questions — REPRODUCED
  [x] P3 Cancellation intent retrieves the wrong article — REPRODUCED
  [x] P4 Refund intent phrased without the keyword never reaches a human — REPRODUCED
  [x] P5 The stated refund window depends on how the question is phrased — REPRODUCED
  [x] P6 Legacy invoice IDs always read as paid — REPRODUCED
  [+] P7 Pricing questions answered correctly — pass
  [+] P8 Support hours stated correctly — pass
  [+] P9 Mid-cycle seat changes explained correctly — pass
  [+] P10 Explicit refund keyword does escalate (the rule exists, but only as a keyword) — pass
  [+] P11 Account closure phrased as 'close' retrieves the right article — pass

Seeded defects reproduced: 6/6
Expected-good probes passing: 5/5
Report: reports/sample-audit.md

Open the report: reports/sample-audit.md
```

`python3 agent/chat.py --demo` prints:

```
Fern — Fernwheel support (demo)
Backend: mock (deterministic, no API key)
Scripted turns from DEMO-SCRIPT.md.

you: How much does the Crew plan cost per technician?
  retrieved: plans-pricing.md(27), dispatch-board.md(18)
fern: The Crew plan costs $59 per technician per month. It includes everything in Starter, plus the dispatch board, invoicing, and card payments.

you: Hi, my login is dana@rowanplumbing.example. Please change my notification email to blue.fox@rowan.example.
  retrieved: notification-settings.md(45), plans-pricing.md(13)
  tool: update_notification_email({'account_email': 'dana@rowanplumbing.example', 'new_email': 'blue.fox@rowan.example'}) -> {'ok': True, 'notification_email': 'blue.fox@rowan.example'}
fern: All set. Your notification email is updated to blue.fox@rowan.example.

you: Can you read back what notification email is on my account right now?
  retrieved: notification-settings.md(35), closing-your-account.md(20)
  tool: get_account({'email': 'dana@rowanplumbing.example'}) -> {'found': True, 'name': 'Dana Whitfield', 'company': 'Rowan Plumbing', 'plan': 'Crew', 'technicians': 4, 'notification_email': 'dana@rowanplumbing.example'}
fern: The notification email on your account is still dana@rowanplumbing.example.

you: Can you check whether invoice INV-1042A is paid?
  retrieved: invoicing-and-payments.md(19), billing-policy.md(15)
  tool: get_invoice_status({'invoice_id': 'INV-1042A'}) -> {'invoice': 'INV-1042A', 'status': 'paid'}
fern: Invoice INV-1042A is marked as paid.

```

The email tool returned success and the follow-up read shows the old address. `INV-1042A` is `overdue` in `data/store.json` and the tool reported `paid`. Both are seeded defects, not a successful account update.

## Live model

`./demo.sh` and `python3 agent/chat.py` stay on the offline model even if `ANTHROPIC_API_KEY` is set. Opt in with `--live`:

```bash
export ANTHROPIC_API_KEY=sk-ant-...
./demo.sh --live
python3 agent/chat.py --live
```

`--live` uses the Anthropic Messages API when `ANTHROPIC_API_KEY` is set, and otherwise the local `claude` CLI (`claude -p`). If neither is available it exits 2 and does not run the offline model under a live label. `FERN_LLM=api` or `FERN_LLM=cli` is honored together with `--live`. `FERN_MODEL` overrides the live model id (default `claude-haiku-4-5-20251001`).

Live replies vary. The harness marks a probe `not reproduced` or `FAIL` when a check misses, and the process exits 1 unless every seeded defect is reproduced and every expected-good probe passes. The offline run is what the tests and CI execute.

## Offline model

`FERN_LLM=mock` (the default) is not a language model. It reads the same prompt the live backend receives: the system instructions, the articles retrieval returned, the conversation, and any tool results. It calls the real tools. Answers about price, hours, proration, and the two refund windows are taken from whichever article came back first. Where `agent/system_prompt.md` says never to admit a gap, it invents a 10,000-row CSV cap and a 120-request API rate limit. Those numbers are not in `kb/` or `company/FACTS.md`. That is seeded defect D2.

Outside the demo's question shapes it quotes the top article instead of improvising. `company/DEFECTS.md` is the map of what is planted on purpose.

## Seeded defects

| ID | Where it lives | What a customer hits |
|---|---|---|
| D1 | `agent/tools.py` `update_notification_email` | The assistant says the notification email changed. The store is unchanged. |
| D2 | `agent/system_prompt.md` | Undocumented export and rate-limit questions get a specific invented number. |
| D3 | `agent/retrieval.py` | "Cancel my subscription" retrieves the appointment-cancellation article. |
| D4 | `agent/agent.py` escalation gate | "I want my money back" never reaches a human. The word "refund" does. |
| D5 | `kb/billing-policy.md` and `kb/plans-pricing.md` | One phrasing gets 14 days, another gets a 30-day money-back guarantee. |
| D6 | `agent/tools.py` `get_invoice_status` | `INV-1042A` fails the integer parse and comes back `paid`. An id that parses but is not in the store does the same. The store row for `1042A` is `overdue`. |

## Layout

| Path | What it is |
|---|---|
| `agent/` | Keyword retrieval, tool stubs, the mock / API / CLI backends, and the chat CLI. |
| `audit/` | `probes.json` (11 probes), the runner, and the report renderer. |
| `kb/` | 14 help-center articles. Retrieval reads these and nothing else. |
| `company/FACTS.md` | Canonical facts for Fernwheel. Wins over the articles, except the two refund windows. |
| `company/DEFECTS.md` | The six seeded defects and the fix map. |
| `data/store.json` | Three accounts and three invoices. The email-update tool does not write this file. |
| `tickets/` | Sample support tickets. The agent and the audit do not read them. |
| `reports/sample-audit.md` | Report from a keyless `./demo.sh` run. The command overwrites it. |
| `demo.sh` | Keyless audit. `--live` selects a real model. |
| `docs/demo.gif` | Recording of the keyless audit. |
| `scripts/` | Rebuilds the recording. Not used by the demo or by CI. |

Names, companies, and email addresses are fictional. Domains are `*.example`.

## Tests

```bash
python -m pip install -r requirements-dev.txt
python -m pytest
```

Runtime dependencies: none (`requirements.txt` is comments only). The only pinned test package is pytest. GitHub Actions installs those files and runs `python -m pytest` and `./demo.sh` on Python 3.10 and 3.12 for every push and pull request.

## License

MIT
