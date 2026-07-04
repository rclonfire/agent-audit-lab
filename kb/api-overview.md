# Fernwheel API overview

The Fernwheel API gives you programmatic access to the jobs, invoices, customers, and team data in your account. Use it to build internal reports, sync records with other systems, or automate routine bookkeeping tasks.

## Availability

The API is available on the Fleet plan only. If your account is on a different plan, the API section does not appear in Settings. Contact billing@fernwheel.example to upgrade.

## Generate an API token

Every request must include a token tied to your account. To create one:

1. Sign in to Fernwheel as an account owner or admin.
2. Go to Settings > API.
3. Click Generate token.
4. Enter a label that describes where the token will be used, such as "Reporting script".
5. Click Create, then copy the token. Fernwheel shows the full value once. Store it in a secure location.

To revoke a token, return to Settings > API and click Revoke next to its label. Revocation takes effect immediately.

## Authentication

The API is REST-based and returns JSON. Send your token in the Authorization header of every request:

```
GET /v1/jobs
Host: api.fernwheel.example
Authorization: Bearer fw_live_xxxxxxxxxxxx
```

Requests without a valid token return a 401 response.

## Endpoint groups

The base URL is `https://api.fernwheel.example/v1`. Endpoints are grouped as follows:

- **Jobs** (`/jobs`): create, read, update, and cancel jobs; read job status history.
- **Jobs export** (`/exports/jobs`): request a CSV export of jobs filtered by date range, status, or assigned technician.
- **Invoices** (`/invoices`): create and read invoices, record payments, and void invoices.
- **Invoices export** (`/exports/invoices`): request a CSV export of invoices for a date range, formatted for import into QuickBooks or other accounting tools.
- **Customers** (`/customers`): manage customer records, service addresses, and contact details.
- **Team** (`/team`): read technician profiles, roles, and availability.
- **Webhooks** (`/webhooks`): register URLs that receive event notifications when jobs or invoices change.

## Run an export

1. Send a POST request to the export endpoint with your filters in the request body.
2. Read the `export_id` from the response.
3. Poll `GET /exports/{export_id}` until `status` is `complete`.
4. Download the file from the `download_url` in the response.

For endpoint-level request and response schemas, see the API reference at developers.fernwheel.example.
