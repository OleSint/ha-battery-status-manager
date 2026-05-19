# Battery Status Manager — Documentation (English)

> **Back to:** [README](../README.md) | [DE](de.md) | [FR](fr.md) | [NL](nl.md) | [ES](es.md)

---

## Table of Contents

1. [What does this integration do?](#1-what-does-this-integration-do)
2. [Requirements](#2-requirements)
3. [Installation](#3-installation)
4. [Initial Setup](#4-initial-setup)
5. [Monitoring Scope](#5-monitoring-scope)
6. [Thresholds](#6-thresholds)
7. [Notifications](#7-notifications)
8. [Weekly Report](#8-weekly-report)
9. [Changing Settings Later](#9-changing-settings-later)
10. [How notifications work (technical details)](#10-how-notifications-work-technical-details)
11. [Troubleshooting](#11-troubleshooting)

---

## 1. What does this integration do?

Battery Status Manager keeps an eye on all battery-powered devices in your Home Assistant and notifies you when action is needed. It is designed to be set up once and then work quietly in the background.

Key capabilities:

- Sends a **warning** when a battery drops below a configurable level (e.g. 20 %).
- Sends a **critical alert** when a battery reaches a dangerously low level (e.g. 10 %).
- Detects **rapid battery drain** (e.g. a drop of 20 % within 24 hours) and alerts you immediately.
- Includes a **depletion forecast** in each notification — the integration estimates how many days are left before the battery runs out, based on the measured drain rate.
- Sends **reminders** at configurable intervals if a battery remains low and has not been replaced.
- Generates an optional **weekly summary report** every week on a day and time you choose.
- Respects a **time window** and **active days**, so you are never woken up by a notification at 3 AM.

---

## 2. Requirements

- Home Assistant **2023.6** or newer.
- At least one **notify service** configured in Home Assistant (e.g. the official mobile companion app, a Telegram bot, or an email notifier). These appear as `notify.your_service_name` in Home Assistant.

---

## 3. Installation

### Via HACS (recommended)

HACS is the Home Assistant Community Store. If you do not have it, follow the [HACS installation guide](https://hacs.xyz/docs/use/download/download/) first.

1. Open HACS in the Home Assistant sidebar.
2. Go to **Integrations**.
3. Click the three-dot menu (⋮) in the top-right corner and choose **Custom repositories**.
4. In the dialog, paste `https://github.com/OleSint/ha-battery-status-manager` and select **Integration** as the category. Click **Add**.
5. Close the dialog. Search for **Battery Status Manager** in the HACS integration list.
6. Click on it, then click **Download** (bottom-right).
7. **Restart Home Assistant** (Settings → System → Restart).

### Manual installation

1. Download the latest release ZIP from [GitHub Releases](https://github.com/OleSint/ha-battery-status-manager/releases).
2. Unzip and copy the `custom_components/battery_status_manager` folder into your Home Assistant `config/custom_components/` directory.
3. Restart Home Assistant.

---

## 4. Initial Setup

After restarting:

1. Go to **Settings → Devices & Services**.
2. Click **+ Add Integration** (bottom-right).
3. Search for **Battery Status Manager** and click on it.
4. Follow the setup wizard (4 steps, described below).

---

## 5. Monitoring Scope

The first step of the wizard lets you choose which batteries to monitor.

### Option A — All batteries

Monitors every entity in Home Assistant with device class `battery`. This is the simplest option and automatically includes new devices you add later.

After choosing "All", you can optionally **exclude** specific entities (for example, a battery entity that always shows 0 % because the sensor is broken).

### Option B — By device

You will see a list of all devices that have at least one battery entity. You can select one or more devices. Only battery entities belonging to the selected devices will be monitored.

### Option C — By entity

You will see a list of all battery entities in Home Assistant. You can select exactly which ones to monitor.

---

## 6. Thresholds

### Warning threshold (⚠️)

- **Enable low battery warning** — Turn this on to receive a notification when a battery falls below the warning level.
- **Warning threshold (%)** — The percentage below which a warning is sent. Default: 20 %.

### Critical threshold (🚨)

- **Enable critical battery alert** — Turn this on to receive a second, more urgent notification at a very low level.
- **Critical threshold (%)** — Must be set lower than the warning threshold. Default: 10 %.

### Rapid drain detection

- **Enable rapid drain notification** — Turn this on to be alerted when a battery drains unusually fast.
- **Drain threshold (%)** — How many percentage points must be lost to trigger an alert. Example: 20 % drop.
- **Observation window (hours)** — Over how many hours the drain is measured. Example: 24 hours.

> **Tip:** A rapid drain of 20 % in 24 hours is unusual for most sensor batteries, which typically last months. This is useful to catch batteries that are failing or devices that have been left on accidentally.

---

## 7. Notifications

### Notification services

Select which `notify.*` services should receive the notifications. You can select multiple. At least one is required.

### Notification title

The title / subject line that appears on push notifications or emails. Default: `Battery Status Manager`.

### Time window (optional)

Enable this to restrict notifications to a specific time range.

- **Time window start** — Earliest time at which a notification may be sent. Example: `08:00`.
- **Time window end** — Latest time. Example: `20:00`.

Overnight windows work correctly: setting start to `22:00` and end to `07:00` will allow notifications between 10 PM and 7 AM.

> Notifications that are suppressed because they fall outside the time window are **not queued** — they are simply skipped. The next check (one hour later) will re-evaluate and send if the condition still applies and the time is now within the window.

### Active days (optional)

Choose the days of the week on which notifications may be sent. By default all seven days are active. You could, for example, disable weekends.

### Reminder (optional)

- **Enable reminder** — If a battery remains below the threshold after the initial notification, a reminder is sent after the configured interval.
- **Reminder interval (hours)** — How often the reminder is repeated. Example: 24 hours.

The reminder respects the same time window and active days settings.

---

## 8. Weekly Report

The weekly report is entirely optional. When enabled, the integration sends a summary message once per week.

- **Enable weekly summary report** — Turns on the weekly report.
- **Day of week for report** — Which day the report is sent (e.g. Monday).
- **Time for report** — What time the report is sent (e.g. 09:00).

### What the report contains

- Total number of monitored batteries.
- Number of batteries currently below the warning threshold.
- Number of batteries currently below the critical threshold.
- Number of batteries that recovered or were replaced in the past 7 days.
- A 7-day forecast list: batteries that are currently above the warning threshold but are expected to drop below it within the next 7 days, based on their measured drain rate.

The report is sent at most once per 7-day period. If Home Assistant is offline at the scheduled time, it will send the report the next time the check runs (within the next hour).

---

## 9. Changing Settings Later

All settings can be changed at any time:

1. Go to **Settings → Devices & Services**.
2. Find the **Battery Status Manager** card.
3. Click **Configure**.
4. Work through the wizard again — your previous values are pre-filled.

---

## 10. How notifications work (technical details)

This section is for users who want to understand the logic behind notifications.

### Check interval

The integration checks all battery levels every **60 minutes**. The exact time of the first check depends on when Home Assistant started.

### Hysteresis

To prevent repeated notifications for the same event, the integration uses hysteresis:

- A battery below the **warning threshold** triggers a warning. It will not trigger another warning until it first recovers above `warning threshold + 5 %`.
- A battery below the **critical threshold** triggers a critical alert. It will not trigger another until it first recovers above `critical threshold + 3 %`.

Example: warning threshold = 20 %. A battery at 18 % triggers a warning. It will not trigger again until it rises above 25 % and then drops below 20 % again.

### Depletion forecast

The integration stores a history of battery readings. Using the oldest and newest data points (requiring at least 3 readings over at least 2 hours), it calculates a linear drain rate. From this rate it extrapolates how many days are left until the battery reaches 0 %.

The forecast is included in the notification message when available. If there is not enough data, or if the battery is not actually draining, no forecast is shown.

### Recovery tracking

When a battery recovers above the warning threshold (including the hysteresis margin), the integration records this as a recovery event. This data is used in the weekly report to show how many batteries were replaced or recharged during the past week.

### Data storage

All state data (notification timestamps, history, recoveries) is stored in Home Assistant's `.storage/battery_status_manager` file. This data persists through restarts.

---

## 11. Troubleshooting

**No notification received**
- Check that a `notify.*` service is correctly configured and that you selected it during setup.
- Check the time window and active days settings — the current time/day may be excluded.
- Check the battery level: it must be below the threshold at the time of the hourly check.

**Notifications come too often**
- Hysteresis is active by default. If you are still getting too many, check whether the battery level is fluctuating around the threshold value.

**A specific battery entity does not appear in the selection list**
- Only entities with device class `battery` and a numeric state (0–100) are included. Virtual or template sensors may not qualify.

**The weekly report is not arriving**
- The report is only sent once per 7-day period. Check the configured day and time.
- Home Assistant must be running at or after the scheduled time for the check to trigger.

**Something else is wrong**
- Check the Home Assistant logs (Settings → System → Logs) and search for `battery_status_manager`.
- Open an issue on [GitHub](https://github.com/OleSint/ha-battery-status-manager/issues) with the log output.
