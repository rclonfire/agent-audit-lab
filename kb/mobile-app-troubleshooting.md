# Technician Mobile App Troubleshooting

This article covers the most common issues technicians hit in the Fernwheel mobile app. If a step below does not resolve the problem, email support@fernwheel.example with your device model and app version.

## Minimum supported versions

The app requires iOS 16 or later and Android 11 or later. Older versions can install the app but will not receive updates and may fail to sync. Check your app version under Settings > About in the app.

## Login problems

1. Confirm you are entering the email address your dispatcher added to your technician profile, not a personal address.
2. Tap Forgot Password on the sign-in screen and follow the reset link sent to that address. The link expires after 30 minutes.
3. If you see "Account inactive," your admin has deactivated your profile. Ask them to re-enable it under Team > Technicians in the web portal.
4. If sign-in spins and times out, switch from Wi-Fi to cellular (or the reverse) and try again.

## Offline mode and syncing

The app stores your assigned jobs, customer details, and forms on the device, so you can keep working without a connection. Job notes, checklists, signatures, and status changes queue on the device while you are offline.

When the connection returns, the app syncs queued changes automatically within about a minute. A cloud icon with a number in the top bar shows how many changes are waiting. To force a sync, pull down on the job list. If two people edit the same job while one is offline, the most recent save wins, and the earlier version stays available in the job's activity log.

## Photo upload failures

1. Open the job and check the photo thumbnail. A yellow badge means the upload is queued; a red badge means it failed.
2. Tap the red badge, then tap Retry Upload.
3. Confirm the app has camera and photo permissions in your device settings.
4. Photos over 25 MB will not upload. Retake the photo at standard resolution if needed.
5. Failed photos stay on your device until they upload, so do not delete the app while uploads are pending.

## Notifications not arriving

1. On iOS, go to Settings > Notifications > Fernwheel and turn on Allow Notifications.
2. On Android, go to Settings > Apps > Fernwheel > Notifications and enable all categories.
3. In the app, open Settings > Notifications and confirm job assignments and schedule changes are switched on.
4. Disable battery optimization for the app on Android, since it can delay alerts.
