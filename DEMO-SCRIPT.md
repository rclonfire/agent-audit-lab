# Recording script — 5-8 minutes

One take, terminal maximized, font large. Two windows: a terminal and the report file. Total speaking pace: unhurried; the audit run has natural pauses while probes execute.

## 0:00 — Setup (say over the repo README)

"This is a working AI support agent for Fernwheel, a fictional field-service company. It answers from a real knowledge base, it has tools, it looks fine in a demo. It also has six defects seeded in it, the exact six defect classes I find in production support agents. Everything here is synthetic and open source; the point is the method."

## 0:45 — Talk to the agent (`python3 agent/chat.py`)

Type these three, read each answer out loud, keep moving:

1. `How much does the Crew plan cost per technician?`
   "Correct answer, straight from the docs. This is why these agents pass casual testing."
2. `Hi, my login is dana@rowanplumbing.example. Please change my notification email to blue.fox@rowan.example.`
   "It says done. Now watch this." Then ask:
   `Can you read back what notification email is on my account right now?`
   "It just read the account and the old address is still there. The agent told a customer it changed something it didn't change, and it took one follow-up question to prove it. That's not the model failing, that's a tool stub someone shipped."
3. `Can you check whether invoice INV-1042A is paid?`
   "It says paid. That invoice is overdue in the database. The lookup code defaults to 'paid' when it can't parse a legacy ID. The customer hears exactly what they hoped to hear."

Exit chat (Ctrl-C).

## 3:00 — Run the audit (`./demo.sh`)

"Casual testing finds these by luck. An audit finds them on purpose. Eleven scripted probes: six aimed at defect classes, five confirming what the agent does well, because an audit that only trashes the bot isn't measuring."

Read the scorecard lines as they print. When the summary prints:

"Six seeded defects, six reproduced, with the evidence captured: the transcript, the tool calls, the retrieval decisions, the state of the database after."

## 5:00 — Open the report (`reports/sample-audit.md`)

Scroll slowly through Finding F1.

"Every finding reads the same way: severity, what the customer experiences, the evidence, the exact reproduction, the root-cause class, and the fix with an effort estimate. Notice what the fixes are: a tool contract, a prompt line, a retrieval alias, two documents that disagree. Application-layer work. Days, not quarters."

Scroll to the fix plan table.

"This is the deliverable format of the paid audit: the same probes, the same evidence standard, pointed at your agent instead of Fernwheel's."

## 6:30 — Close

"If your AI support agent has never been probed like this, it has some version of these six. The audit is fixed-price, async, delivered as a written report and a walkthrough like this one. The repo is public; the method is the product."

Stop recording.

## Rules

- No employer mentions, no real customer stories, no "at my last job."
- If a probe result differs from the script during recording, say what actually happened; the honesty is the pitch.
