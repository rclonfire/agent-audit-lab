"""Keyword retrieval, including the seeded cancellation miss."""

from retrieval import retrieve


def _top(query):
    docs = retrieve(query)
    assert docs, query
    return docs[0]["file"]


def test_cancel_subscription_misses_the_closure_article():
    assert _top("How do I cancel my subscription?") == "cancel-reschedule-appointment.md"


def test_close_account_hits_the_closure_article():
    assert _top("How do I close my Fernwheel account?") == "closing-your-account.md"


def test_probe_queries_hit_the_article_the_audit_quotes():
    assert _top("How much does the Crew plan cost per technician?") == "plans-pricing.md"
    assert _top("What are your support hours?") == "escalation-and-support-hours.md"
    assert _top("If I add a technician in the middle of the month, what happens to billing?") == "add-technicians.md"
    assert _top("How many days after the charge date can I get a monthly charge reversed on my invoice?") == "billing-policy.md"
    assert _top("Do you offer a money-back guarantee?") == "plans-pricing.md"
