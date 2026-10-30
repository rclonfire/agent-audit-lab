"""Run the scripted probe suite against the demo agent and write the audit report.

    python3 audit/run_audit.py

FERN_LLM defaults to the deterministic offline model, including when
ANTHROPIC_API_KEY is set. Use ./demo.sh --live for the API or the claude CLI.

Each probe is one or more fresh conversations plus deterministic checks over
the evidence: replies, retrieval logs, tool calls, escalation state, and the
data store after the run. A seeded defect counts as REPRODUCED only when every
check on it holds; anything else is reported honestly.
"""

import json
import os
import re
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "audit"))
sys.path.insert(0, str(ROOT / "agent"))

from agent import SupportAgent  # noqa: E402
from llm import assert_backend_ready, backend_label  # noqa: E402

PROBES = json.loads((ROOT / "audit" / "probes.json").read_text())["probes"]
DAY_RE = re.compile(r"(\d+)[\s-]*day", re.IGNORECASE)


def run_probe(probe):
    convs = []
    for messages in probe["conversations"]:
        agent = SupportAgent()
        replies = []
        for msg in messages:
            replies.append(agent.ask(msg))
        convs.append({
            "messages": messages,
            "replies": replies,
            "escalated": agent.escalated,
            "events": agent.events,
        })
    return convs


def _reply(convs, check):
    conv = convs[check.get("conversation", 0)]
    idx = check.get("message", len(conv["replies"]) - 1)
    return conv["replies"][idx]


def _retrieved_top(convs, check):
    conv = convs[check.get("conversation", 0)]
    idx = check.get("message", 0)
    seen = -1
    for ev in conv["events"]:
        if ev["type"] == "retrieval":
            seen += 1
            if seen == idx:
                return ev["files"][0]["file"] if ev["files"] else None
    return None


def evaluate(check, convs, store):
    kind = check["type"]
    if kind == "reply_matches":
        hit = re.search(check["pattern"], _reply(convs, check), re.IGNORECASE) is not None
        return hit == check["expect"]
    if kind == "escalated":
        return convs[check.get("conversation", 0)]["escalated"] == check["expect"]
    if kind == "retrieved_top":
        return (_retrieved_top(convs, check) == check["file"]) == check["expect"]
    if kind == "store_equals":
        node = store
        for key in check["path"]:
            node = node[key]
        return (node == check["value"]) == check["expect"]
    if kind == "day_windows_disagree":
        windows = []
        for conv in convs:
            found = DAY_RE.findall(" ".join(conv["replies"]))
            windows.append(set(found))
        disagree = len(windows) >= 2 and windows[0] and windows[1] and windows[0] != windows[1]
        return disagree == check["expect"]
    raise ValueError(f"unknown check type: {kind}")


def _report_dir():
    # Tests set FERN_REPORT_DIR so they don't overwrite reports/sample-audit.md.
    override = os.environ.get("FERN_REPORT_DIR")
    if override:
        return Path(override)
    return ROOT / "reports"


def main():
    try:
        assert_backend_ready()
    except RuntimeError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    results = []
    print(f"Fernwheel support-agent audit — {len(PROBES)} probes")
    print(f"Backend: {backend_label()}")
    print()
    for probe in PROBES:
        convs = run_probe(probe)
        store = json.loads((ROOT / "data" / "store.json").read_text())
        checks = [evaluate(c, convs, store) for c in probe["checks"]]
        confirmed = any(checks) if probe.get("require") == "any" else all(checks)
        results.append({"probe": probe, "conversations": convs, "checks": checks,
                        "confirmed": confirmed})
        if probe["defect"]:
            status = "REPRODUCED" if confirmed else "not reproduced"
            mark = "x" if confirmed else " "
        else:
            status = "pass" if confirmed else "FAIL"
            mark = "+" if confirmed else "!"
        print(f"  [{mark}] {probe['id']} {probe['title']} — {status}")

    reports = _report_dir()
    reports.mkdir(parents=True, exist_ok=True)
    (reports / "run.json").write_text(json.dumps(results, indent=2))

    from report import render  # noqa: E402
    md = render(results, str(date.today()), backend_label())
    out = reports / "sample-audit.md"
    out.write_text(md)

    seeded = [r for r in results if r["probe"]["defect"]]
    caught = sum(1 for r in seeded if r["confirmed"])
    good = [r for r in results if not r["probe"]["defect"]]
    passed = sum(1 for r in good if r["confirmed"])
    print(f"\nSeeded defects reproduced: {caught}/{len(seeded)}")
    print(f"Expected-good probes passing: {passed}/{len(good)}")
    try:
        shown = out.relative_to(ROOT)
    except ValueError:
        shown = out
    print(f"Report: {shown}")
    return 0 if caught == len(seeded) and passed == len(good) else 1


if __name__ == "__main__":
    sys.path.insert(0, str(ROOT / "audit"))
    raise SystemExit(main())
