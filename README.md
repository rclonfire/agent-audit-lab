# Agent Audit Lab

A working AI support agent for a fictional company, six realistically seeded defects, and the audit harness that catches every one of them with cited evidence.

This repo demonstrates a methodology: grade a deployed AI support agent the way customers experience it — scripted probe conversations, deterministic checks, findings ranked by customer impact, each with a reproduction and a named fix. The same method runs against production agents on Intercom, Zendesk, or anything with a chat surface; the demo agent exists so the whole loop runs standalone.

## What's inside

| Path | What it is |
|---|---|
| `company/FACTS.md` | Canonical fact sheet for Fernwheel, the fictional field-service SaaS |
| `company/DEFECTS.md` | The six seeded defects, one per root-cause class, with the fix map |
| `kb/` | 14 help-center articles the agent answers from |
| `agent/` | The support agent: keyword retrieval, tool stubs, model loop, chat CLI |
| `audit/` | The probe suite and report generator |
| `reports/sample-audit.md` | The audit report a full run produces |
| `tickets/` | Synthetic ticket corpus for realism |

## The six defects

One per root-cause class, all planted in the application layer — a tool stub that lies, a lookup that defaults to success, a keyword-scoped escalation rule, a prompt anti-pattern, two docs that drifted apart, a retrieval scorer that rewards the wrong article. That is where real support-agent quality problems live. `company/DEFECTS.md` has the full map.

## Run it

Requires Python 3.10+ and either an `ANTHROPIC_API_KEY` or the [Claude Code CLI](https://claude.com/claude-code) logged in (the agent uses whichever it finds; no other dependencies).

```bash
# talk to the (defective) agent yourself
python3 agent/chat.py

# run the full audit: 11 probes, 6 seeded defects, report with evidence
./demo.sh
```

The audit prints a probe-by-probe scorecard and writes `reports/sample-audit.md`: findings ranked by severity, transcript evidence, exact reproduction steps, root-cause class, and the fix for each.

## Why this exists

AI support agents get shipped, billed per resolution, and left unmeasured. The gap between "answered" and "answered correctly" is invisible until someone probes it deliberately. This lab is the deliberate probe, published as working code.

Everything here is clean-room and synthetic: Fernwheel is invented, every name and email is fictional (`*.example` domains only), and no real company's data, prompts, or configuration appear anywhere.

## License

MIT
