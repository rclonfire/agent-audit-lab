"""The markdown report cites retrieval, not only tool calls."""

from report import render


def _result(defect, title, events, replies, confirmed=True):
    return {
        "probe": {
            "id": "P0",
            "defect": defect,
            "severity": "HIGH",
            "title": title,
            "root_cause": "example",
            "fix": "fix it",
            "effort": "1 hour",
        },
        "conversations": [{
            "messages": ["hello"],
            "replies": replies,
            "escalated": False,
            "events": events,
        }],
        "checks": [confirmed],
        "confirmed": confirmed,
    }


def test_transcript_includes_retrieval_and_tools():
    results = [
        _result("D3", "Wrong article", [
            {"type": "user", "text": "hello"},
            {"type": "retrieval", "files": [{"file": "cancel-reschedule-appointment.md", "score": 7}]},
            {"type": "reply", "text": "Cancel the appointment."},
        ], ["Cancel the appointment."]),
        _result(None, "Hours are right", [
            {"type": "user", "text": "hello"},
            {"type": "reply", "text": "Monday."},
        ], ["Monday."]),
    ]
    md = render(results, "2026-10-30", "mock (deterministic, no API key)")
    assert "Model backend: mock (deterministic, no API key)." in md
    assert "*retrieved:* cancel-reschedule-appointment.md (7)" in md
    assert "local chat agent in this repository" in md
    assert "Hours are right — passes" in md
    assert "NOT REPRODUCED" not in md


def test_unconfirmed_defect_is_labeled():
    md = render([
        _result("D1", "Missed", [{"type": "user", "text": "hello"}], ["nope"], confirmed=False),
    ], "2026-10-30", "mock")
    assert "NOT REPRODUCED in this run" in md
