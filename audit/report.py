"""Render probe results into the audit-report format."""

SEVERITY_ORDER = {"CRITICAL": 0, "HIGH": 1, "MEDIUM": 2, "LOW": 3}


def _transcript(conv):
    lines = []
    for i, msg in enumerate(conv["messages"]):
        lines.append(f"> **Customer:** {msg}")
        tool_lines = []
        started = False
        for ev in conv["events"]:
            if ev["type"] == "user" and ev["text"] == msg:
                started = True
                continue
            if started and ev["type"] == "user":
                break
            if started and ev["type"] == "tool_call":
                tool_lines.append(
                    f"> *tool:* `{ev['tool']}({ev['args']})` → `{ev['result']}`")
        lines.extend(tool_lines)
        if i < len(conv["replies"]):
            lines.append(f"> **Fern:** {conv['replies'][i]}")
    return "\n>\n".join(lines)


def render(results, run_date):
    seeded = sorted(
        (r for r in results if r["probe"]["defect"]),
        key=lambda r: SEVERITY_ORDER.get(r["probe"].get("severity", "LOW"), 9),
    )
    good = [r for r in results if not r["probe"]["defect"]]
    n_convs = sum(len(r["conversations"]) for r in results)

    out = []
    out.append("# AI Support Agent Audit — Fernwheel (demo)")
    out.append("")
    out.append(f"Prepared from a scripted probe run on {run_date}. Fernwheel is a "
               "fictional company; every defect below was seeded on purpose and "
               "then caught by the same probe method used on production agents. "
               "See `company/DEFECTS.md` for the seed map.")
    out.append("")
    out.append("## 1. Scope and method")
    out.append("")
    out.append(f"Surface tested: chat. {n_convs} scripted conversations on "
               f"{run_date}, persona: small trades-business owner on the Crew plan. "
               "Every finding cites the exact prompt sequence, the agent's reply, "
               "and the tool or retrieval evidence behind it.")
    out.append("")
    out.append("## 2. Findings, ranked by customer impact")

    for idx, r in enumerate(seeded, 1):
        p = r["probe"]
        status = "REPRODUCED" if r["confirmed"] else "NOT REPRODUCED in this run"
        out.append("")
        out.append(f"### F{idx} — {p['title']}")
        out.append("")
        out.append(f"- **Severity:** {p['severity']}")
        out.append(f"- **Status:** {status}")
        out.append(f"- **Root cause class:** {p['root_cause']}")
        out.append(f"- **Fix:** {p['fix']}")
        out.append(f"- **Effort:** {p['effort']}")
        out.append("")
        out.append("**Evidence:**")
        out.append("")
        for conv in r["conversations"]:
            out.append(_transcript(conv))
            out.append("")
        out.append(f"**Reproduction:** send the message(s) above to a fresh "
                   f"conversation; probe `{p['id']}` in `audit/probes.json` "
                   "automates it.")

    out.append("")
    out.append("## 3. What the agent does well")
    out.append("")
    for r in good:
        mark = "passes" if r["confirmed"] else "FAILED this run"
        out.append(f"- {r['probe']['title']} — {mark}")

    out.append("")
    out.append("## 4. Fix plan")
    out.append("")
    out.append("| # | Finding | Fix | Effort |")
    out.append("|---|---|---|---|")
    for idx, r in enumerate(seeded, 1):
        p = r["probe"]
        out.append(f"| F{idx} | {p['title']} | {p['fix']} | {p['effort']} |")
    out.append("")
    out.append("Every fix above is application-layer work: a tool contract, a "
               "retrieval alias, a prompt line, a content correction. None of "
               "them require replacing the model or the platform.")
    out.append("")
    return "\n".join(out)
