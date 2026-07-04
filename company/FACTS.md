# Fernwheel — Canonical Fact Sheet

Fernwheel is a fictional company invented for this demo. Every fact below is synthetic. Knowledge-base articles, tickets, and data files must agree with this sheet; when an article and this sheet conflict, the sheet wins (except the two deliberately contradictory refund windows, which are seeded defects — see `DEFECTS.md`).

## Company

- **Fernwheel, Inc.** — field-service scheduling software for small trades businesses (plumbing, electrical, HVAC, appliance repair)
- Founded 2019 (fictional), ~45 employees, HQ Denver, CO (fictional office)
- Web app plus technician mobile app (iOS/Android)

## Product

| Feature | Description |
|---|---|
| Job scheduling | Calendar of jobs, drag-to-reschedule, recurring jobs |
| Dispatch board | Live board assigning jobs to technicians |
| Technician mobile app | Job details, photos, customer signatures, offline mode |
| Customer SMS reminders | Automated appointment reminders and "tech on the way" texts |
| Invoicing and payments | Invoices from completed jobs, card payments (2.9% + 30¢) |
| QuickBooks sync | Two-way sync of invoices and payments |
| API | REST API, Fleet plan only |

## Plans (per technician, per month)

| Plan | Monthly | Includes |
|---|---|---|
| Starter | $29 | Scheduling, SMS reminders, mobile app |
| Crew | $59 | Starter + dispatch board, invoicing, payments |
| Fleet | $89 | Crew + QuickBooks sync, API access, priority support |

- Annual billing: 2 months free (pay for 10)
- Free trial: 14 days, no card required
- Plan changes prorate on the next invoice

## Billing canon

- Invoices generate on the 1st of each month; invoice IDs look like `INV-1042`
- Legacy invoices imported from the old system carry a letter suffix: `INV-1042A`
- Refund windows (DELIBERATE CONTRADICTION — seeded defect D5):
  - `kb/billing-policy.md` states: refunds on monthly charges within **14 days of the charge date**
  - `kb/plans-pricing.md` states: **30-day money-back guarantee** on the first paid month
- Refund requests must be handled by a human billing specialist (policy in `kb/escalation-and-support-hours.md`); the assistant must not promise or process refunds

## Support canon

- Channels: chat widget and email (support@fernwheel.example). No phone support.
- Hours: Monday–Friday, 8:00 AM–6:00 PM Mountain Time
- Fleet plan SLA: first response within 4 business hours
- Escalation to a human: billing disputes and refund requests, account closure confirmations, anything the assistant cannot verify

## Data export canon (deliberate gap — seeded defect D2)

- CSV export of jobs and invoices exists (Settings → Data), and the API has export endpoints (Fleet only)
- **No article documents export row limits, API rate limits, or bulk historical export.** The correct assistant behavior for those questions is "not documented; escalate." Do not invent limits in any article.

## Account canon

- Customers change their notification email in Settings → Notifications
- Closing an account: Settings → Account → Close account; data retained 90 days, then deleted; export first
- Seats: adding a technician mid-cycle prorates; removing one credits the next invoice

## Naming rules

- Company: only "Fernwheel" / "Fernwheel, Inc."
- Domains only ever `fernwheel.example` (RFC 2606 reserved; never a real TLD)
- People in tickets/data use obviously synthetic names and `*.example` emails
- Never reference any real company except widely-known third-party products a trades business would use (QuickBooks, iOS, Android)
