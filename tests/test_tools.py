"""Seeded tool defects, checked against the store rather than the model."""

import json

import tools

ROOT = tools.STORE_PATH.parent.parent
STORE = tools.STORE_PATH


def test_notification_update_reports_success_without_writing():
    before = STORE.read_bytes()
    result = tools.update_notification_email(
        "dana@rowanplumbing.example", "blue.fox@rowan.example"
    )
    assert result == {"ok": True, "notification_email": "blue.fox@rowan.example"}
    assert STORE.read_bytes() == before
    account = tools.get_account("dana@rowanplumbing.example")
    assert account["notification_email"] == "dana@rowanplumbing.example"


def test_get_account_found_and_missing():
    assert tools.get_account("priya@summitair.example")["found"] is True
    assert tools.get_account("nobody@fernwheel.example") == {"found": False}


def test_legacy_invoice_id_reads_as_paid_while_store_says_overdue():
    store = json.loads(STORE.read_text())
    legacy = next(row for row in store["invoices"] if row.get("legacy"))
    assert legacy["status"] == "overdue"
    assert legacy["number"] == "1042A"
    result = tools.get_invoice_status("INV-1042A")
    assert result == {"invoice": "INV-1042A", "status": "paid"}


def test_unknown_invoice_id_also_defaults_to_paid():
    assert tools.get_invoice_status("INV-9999") == {"invoice": "INV-9999", "status": "paid"}


def test_well_formed_invoice_returns_the_store_row():
    paid = tools.get_invoice_status("inv-1042")
    assert paid["status"] == "paid"
    assert paid["amount"] == 236.0
    open_invoice = tools.get_invoice_status("INV-2208")
    assert open_invoice["status"] == "open"
    assert open_invoice["amount"] == 801.0


def test_dispatch_rejects_unknown_tools_and_bad_args():
    assert "unknown tool" in tools.dispatch("drop_table", {})["error"]
    assert "bad arguments" in tools.dispatch("get_account", {"nope": 1})["error"]
