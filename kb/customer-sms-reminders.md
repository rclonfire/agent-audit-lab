# Customer SMS reminders

Fernwheel can text your customers an appointment reminder before a visit and a tech-on-the-way message when your technician starts driving. Both messages send automatically once you turn them on.

## Turn on SMS reminders

1. Sign in to your Fernwheel account at app.fernwheel.example.
2. Go to Settings > Customer Notifications.
3. Toggle on **Appointment reminders**, **Tech on the way**, or both.
4. Confirm the business name shown under **Sender name**. It appears at the start of every text.
5. Click **Save**.

Messages only go to customers who have a mobile number on their profile and have not opted out.

## Edit message templates

1. Go to Settings > Customer Notifications > Templates.
2. Select the template you want to change.
3. Edit the text. You can insert placeholders such as `{customer_first_name}`, `{appointment_window}`, and `{technician_first_name}` from the placeholder menu. Placeholders fill in automatically when the message sends.
4. Click **Preview** to see a sample with real formatting, then click **Save**.

Keep templates short where you can. A long message can count as more than one message toward your allowance.

## Timing rules

Appointment reminders send 24 hours before the scheduled window by default. You can change this to 2, 24, or 48 hours in Settings > Customer Notifications > Timing. Reminders never send between 9:00 PM and 8:00 AM in the customer's local time zone. A reminder that would land in that window sends at 8:00 AM instead.

Tech-on-the-way texts send when the technician taps **On My Way** in the Fernwheel mobile app on iOS or Android. There is no schedule to configure for these.

## Customer opt-out

Customers can reply STOP to any Fernwheel text to opt out. Fernwheel records the opt-out on their profile and blocks all future automated texts to that number. You cannot re-enable texting for them yourself. The customer must text START to the same number to opt back in.

An opted-out customer still receives email notifications if you have those enabled.

## What counts toward SMS usage

Your plan includes a monthly SMS allowance, shown in Settings > Billing > Usage. Each outbound text counts as one message toward your allowance; unusually long texts can count as two. Inbound replies, including STOP and START, do not count. Failed sends to landlines or invalid numbers do not count. Usage resets on your billing date, and overage is billed per message on your next invoice.
