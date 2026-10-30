"""The escalation gate is in agent.py, independent of which model is plugged in."""

import json

import agent


def _scripted(monkeypatch, message):
    def fake(prompt):
        if "Tool call " in prompt:
            return json.dumps({"action": "reply", "text": "Following up."})
        return json.dumps({
            "action": "tool",
            "tool": "route_to_human",
            "args": {"reason": "billing"},
        })

    monkeypatch.setattr(agent, "complete", fake)
    support = agent.SupportAgent()
    support.ask(message)
    tools = [ev for ev in support.events if ev["type"] == "tool_call"]
    return support, tools


def test_refund_keyword_reaches_a_human(monkeypatch):
    support, tools = _scripted(monkeypatch, "I am requesting a refund for my June charge.")
    assert support.escalated is True
    assert tools[0]["result"]["routed"] is True


def test_money_back_without_the_keyword_is_blocked(monkeypatch):
    message = (
        "I want my money back for the June charge. "
        "The dispatch board was down for a week and my crew couldn't see their jobs."
    )
    support, tools = _scripted(monkeypatch, message)
    assert support.escalated is False
    assert tools[0]["result"]["ok"] is False
    assert "handoff denied" in tools[0]["result"]["error"]
