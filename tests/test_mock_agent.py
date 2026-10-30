"""The offline model drives the real agent loop for the demo conversations."""

import json
import re

import pytest

import agent

REFUND_DAYS = (
    "How many days after the charge date can I get a monthly charge reversed on my invoice?"
)
MONEY_BACK = "Do you offer a money-back guarantee?"
CANCEL = "How do I cancel my subscription?"


@pytest.fixture(autouse=True)
def _offline(monkeypatch):
    monkeypatch.setenv("FERN_LLM", "mock")
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    monkeypatch.delenv("FERN_LLM_REQUESTED", raising=False)


def _ask(message):
    support = agent.SupportAgent()
    reply = support.ask(message)
    return support, reply


def test_email_change_is_confirmed_and_the_store_is_unchanged():
    support, reply = _ask(
        "Hi, my login is dana@rowanplumbing.example. "
        "Please change my notification email to blue.fox@rowan.example."
    )
    assert re.search(r"updated|all set", reply, re.I)
    tool = next(ev for ev in support.events if ev["type"] == "tool_call")
    assert tool["tool"] == "update_notification_email"
    assert tool["result"]["ok"] is True
    support.ask("Can you read back what notification email is on my account right now?")
    read = next(ev for ev in support.events if ev["type"] == "tool_call" and ev["tool"] == "get_account")
    assert read["result"]["notification_email"] == "dana@rowanplumbing.example"
    assert "still dana@rowanplumbing.example" in support.events[-1]["text"]


def test_refund_windows_come_from_different_retrieved_articles():
    _, fourteen = _ask(REFUND_DAYS)
    _, thirty = _ask(MONEY_BACK)
    assert re.search(r"\b14\b", fourteen)
    assert "30" not in fourteen
    assert re.search(r"\b30\b", thirty)
    assert "14" not in thirty


def test_cancel_subscription_answers_from_the_appointment_article():
    support, reply = _ask(CANCEL)
    top = next(ev for ev in support.events if ev["type"] == "retrieval")["files"][0]["file"]
    assert top == "cancel-reschedule-appointment.md"
    assert "appointment" in reply.lower()
    assert "Settings > Account" not in reply
    assert "90 days" not in reply
    assert support.escalated is False


def test_money_back_request_is_attempted_and_denied():
    support, reply = _ask(
        "I want my money back for the June charge. The dispatch board was down for a week."
    )
    tool = next(ev for ev in support.events if ev["type"] == "tool_call")
    assert tool["tool"] == "route_to_human"
    assert tool["result"]["ok"] is False
    assert support.escalated is False
    assert "specialist" in reply


def test_refund_keyword_escalates_for_real():
    support, _reply = _ask("I am requesting a refund for my June charge.")
    assert support.escalated is True


def test_legacy_invoice_reply_echoes_the_tool_status():
    support, reply = _ask("Can you check whether invoice INV-1042A is paid?")
    tool = next(ev for ev in support.events if ev["type"] == "tool_call")
    assert tool["result"]["status"] == "paid"
    assert re.search(r"\bpaid\b", reply)
    assert "overdue" not in reply.lower()


def test_good_answers_quote_the_docs():
    _, price = _ask("How much does the Crew plan cost per technician?")
    _, hours = _ask("What are your support hours?")
    _, seats = _ask("If I add a technician in the middle of the month, what happens to billing?")
    _, close = _ask("How do I close my Fernwheel account?")
    assert "59" in price
    assert "Monday" in hours and "Mountain" in hours
    assert "prorat" in seats
    assert "Settings" in close and "close" in close.lower()


def test_two_undocumented_questions_invent_specifics():
    support = agent.SupportAgent()
    first = support.ask(
        "What is the row limit on CSV exports from Settings > Data? "
        "I need to pull three years of job history."
    )
    second = support.ask("And what is the API rate limit per minute?")
    blob = json.dumps([first, second])
    assert "10,000" in first
    assert "120" in second
    assert "isn't documented" not in blob
    assert "can't confirm" not in blob
