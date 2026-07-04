# QuickBooks sync

Fernwheel syncs invoices and payments with QuickBooks in both directions. Invoices you create in Fernwheel appear in QuickBooks within a few minutes, and payments recorded in either system update the other. QuickBooks sync is available on the Fleet plan only. If you are on a different plan, the Integrations page shows the option as locked.

## Connect QuickBooks

You need owner or admin access in Fernwheel and admin access in QuickBooks.

1. Sign in at app.fernwheel.example.
2. Go to Settings, then Integrations, then QuickBooks.
3. Click Connect QuickBooks.
4. Sign in to QuickBooks when prompted and approve the access request.
5. QuickBooks returns you to Fernwheel on the account mapping screen. Complete the mapping before the first sync runs.

## Map your accounts

Mapping tells Fernwheel where each transaction lands in your QuickBooks chart of accounts.

1. On the mapping screen, pick an income account for invoice line items. Most teams use their main services income account.
2. Pick a deposit account for payments. This is usually your operating bank account or an undeposited funds account.
3. If you collect sales tax, match each Fernwheel tax rate to a QuickBooks tax code.
4. Click Save mapping.

The first sync starts within 15 minutes and imports your last 90 days of Fernwheel invoices. After that, changes sync every few minutes. You can review results anytime under Settings, Integrations, QuickBooks, Sync history.

## Common sync errors

**Duplicate customer.** An invoice fails to sync because two QuickBooks customer records share the same email address, so Fernwheel cannot pick a match. Merge or edit the duplicate records in QuickBooks, then open Sync history in Fernwheel and click Retry on the failed invoice.

**Mapped account not found.** A sync fails because an account you mapped was deleted or made inactive in QuickBooks. Reactivate the account in QuickBooks, or return to the mapping screen in Fernwheel and pick a replacement, then retry the failed items.

**Connection expired.** Every item fails and the Integrations page shows QuickBooks as disconnected. This happens after a QuickBooks password change or when the authorization ages out. Click Reconnect on the QuickBooks integration page and sign in again. Queued items sync automatically once the connection is restored.

If an error persists after a retry, email support@fernwheel.example with the invoice number and the error text from Sync history.
