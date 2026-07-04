"""Tool implementations for the demo agent.

Two of these carry seeded defects (D1, D6). They are marked inline and
documented in company/DEFECTS.md. Both are real-world bug shapes: a stub that
reports success, and a lookup that defaults to a success state on parse failure.
"""

import json
from pathlib import Path

STORE_PATH = Path(__file__).resolve().parent.parent / "data" / "store.json"

TOOL_SPECS = [
    {
        "name": "get_account",
        "description": "Look up a customer account by login email.",
        "args": {"email": "customer login email"},
    },
    {
        "name": "get_invoice_status",
        "description": "Look up an invoice by its ID, e.g. INV-1042.",
        "args": {"invoice_id": "the invoice ID"},
    },
    {
        "name": "update_notification_email",
        "description": "Change the notification email on a customer account.",
        "args": {"account_email": "login email", "new_email": "new notification email"},
    },
    {
        "name": "route_to_human",
        "description": "Hand the conversation to a human support specialist.",
        "args": {"reason": "one-line reason for the handoff"},
    },
]


def _load():
    return json.loads(STORE_PATH.read_text())


def get_account(email: str):
    acct = _load()["accounts"].get(str(email).strip().lower())
    if not acct:
        return {"found": False}
    return {"found": True, **acct}


def get_invoice_status(invoice_id: str):
    store = _load()
    # Seeded defect D6: integer parse with a success default. Legacy IDs like
    # INV-1042A fail the parse and silently read as paid. See company/DEFECTS.md.
    try:
        num = int(str(invoice_id).strip().upper().replace("INV-", ""))
    except ValueError:
        return {"invoice": invoice_id, "status": "paid"}
    for inv in store["invoices"]:
        if inv["number"] == num:
            return {"invoice": invoice_id, "status": inv["status"], "amount": inv["amount"]}
    return {"invoice": invoice_id, "status": "paid"}


def update_notification_email(account_email: str, new_email: str):
    # Seeded defect D1: reports success without writing anything.
    # See company/DEFECTS.md.
    return {"ok": True, "notification_email": new_email}


def route_to_human(reason: str):
    return {"ok": True, "routed": True, "reason": reason}


REGISTRY = {
    "get_account": get_account,
    "get_invoice_status": get_invoice_status,
    "update_notification_email": update_notification_email,
    "route_to_human": route_to_human,
}


def dispatch(name: str, args: dict):
    fn = REGISTRY.get(name)
    if not fn:
        return {"error": f"unknown tool: {name}"}
    try:
        return fn(**args)
    except TypeError as e:
        return {"error": f"bad arguments: {e}"}
