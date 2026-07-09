# HA - Battery Status Manager

A Home Assistant custom integration that monitors battery levels across your devices, sends smart notifications, and gives you a weekly overview — so you always know which batteries need attention.

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/hacs/integration)
[![GitHub release](https://img.shields.io/github/v/release/OleSint/ha-battery-status-manager)](https://github.com/OleSint/ha-battery-status-manager/releases)

---
## ☕ Support this project

If this integration saves you time, consider supporting its development:

[![GitHub Sponsors](https://img.shields.io/badge/Sponsor-%E2%9D%A4-red?logo=github)](https://github.com/sponsors/OleSint)

This project is and will remain free and open source.
--- 
<br>
---

## English

### Features

- **Monitoring scope** — Monitor all batteries, select by device, or pick individual entities. When monitoring all, you can exclude specific entities.
- **Warning threshold** (⚠️) — Notification when a battery falls below a configurable level (default: 20 %).
- **Critical threshold** (🚨) — Optional second, lower threshold for urgent alerts (default: 10 %).
- **Rapid drain detection** — Alert when a battery drops by a set amount within a defined time window.
- **Depletion forecast** — Estimates days until empty based on the measured drain rate; included in notifications.
- **Notification channels** — Choose one or more `notify.*` services (e.g. mobile app, email, Telegram).
- **Time window** — Restrict notifications to certain hours (supports overnight windows like 22:00–07:00).
- **Active days** — Choose which days of the week notifications may be sent.
- **Reminder** — Opt-in: resend notification if a battery is still below threshold after N hours.
- **Weekly report** — Opt-in: receive a weekly summary with battery counts, critical/warning states, recoveries, and a 7-day forecast.
- **Hysteresis** — Prevents notification storms: a battery that triggered a warning won't re-notify until it recovers above the threshold by a safety margin.

### Installation via HACS

1. In HACS, go to **Integrations → ⋮ → Custom repositories**.
2. Add `https://github.com/OleSint/ha-battery-status-manager` as type **Integration**.
3. Search for **Battery Status Manager** and click **Download**.
4. Restart Home Assistant.
5. Go to **Settings → Devices & Services → Add Integration** and search for **Battery Status Manager**.

### Configuration

Setup runs as a guided wizard:

| Step | What you configure |
|---|---|
| Monitoring scope | All / by device / by entity; exclusion list for "All" |
| Thresholds | Warning %, critical %, rapid drain % and timeframe |
| Notifications | Services, title, time window, active days, reminder |
| Weekly report | Enable, day and time |

All settings can be changed later via **Configure** on the integration card.

### Requirements

- Home Assistant 2023.6 or newer
- At least one configured `notify.*` service

---

## Deutsch

### Funktionen

- **Überwachungsbereich** — Alle Batterien, Auswahl nach Gerät oder nach einzelnen Entitäten. Bei „Alle" können einzelne Entitäten ausgeschlossen werden.
- **Warn-Schwellenwert** (⚠️) — Benachrichtigung, wenn ein Akku unter einen konfigurierbaren Wert fällt (Standard: 20 %).
- **Kritischer Schwellenwert** (🚨) — Optionaler zweiter, niedrigerer Schwellenwert für dringende Meldungen (Standard: 10 %).
- **Starker Ladestandsverlust** — Alarm, wenn ein Akku innerhalb eines definierten Zeitraums stark abfällt.
- **Entleerungsprognose** — Schätzt die verbleibenden Tage bis zur Entladung anhand der gemessenen Entladerate; wird in Benachrichtigungen angezeigt.
- **Benachrichtigungskanäle** — Ein oder mehrere `notify.*`-Dienste wählbar (z. B. Mobile App, E-Mail, Telegram).
- **Zeitfenster** — Benachrichtigungen nur in bestimmten Stunden senden (auch über Mitternacht, z. B. 22:00–07:00).
- **Aktive Wochentage** — Auswahl, an welchen Tagen Benachrichtigungen gesendet werden dürfen.
- **Erinnerung** — Opt-in: erneute Benachrichtigung, wenn der Akku nach N Stunden weiterhin unter dem Schwellenwert liegt.
- **Wöchentlicher Bericht** — Opt-in: wöchentliche Zusammenfassung mit Akku-Übersicht, Warn-/Kritikzustand, Erholungen und 7-Tage-Prognose.
- **Hysterese** — Verhindert Benachrichtigungsflut: Ein Akku, der eine Warnung ausgelöst hat, wird erst wieder benachrichtigt, wenn er sich deutlich erholt hat.

### Installation über HACS

1. In HACS: **Integrationen → ⋮ → Benutzerdefinierte Repositories**.
2. `https://github.com/OleSint/ha-battery-status-manager` als Typ **Integration** hinzufügen.
3. Nach **Battery Status Manager** suchen und **Herunterladen** klicken.
4. Home Assistant neu starten.
5. **Einstellungen → Geräte & Dienste → Integration hinzufügen** → **Battery Status Manager** suchen.

### Konfiguration

Die Einrichtung erfolgt als geführter Assistent:

| Schritt | Inhalt |
|---|---|
| Überwachungsbereich | Alle / nach Gerät / nach Entität; Ausschlussliste bei „Alle" |
| Schwellenwerte | Warn-%, Kritisch-%, Starkverlust % und Zeitraum |
| Benachrichtigungen | Dienste, Titel, Zeitfenster, Wochentage, Erinnerung |
| Wöchentlicher Bericht | Aktivieren, Tag und Uhrzeit |

Alle Einstellungen können nachträglich über **Konfigurieren** auf der Integrationskarte geändert werden.

### Voraussetzungen

- Home Assistant 2023.6 oder neuer
- Mindestens ein konfigurierter `notify.*`-Dienst

---

## Links

- [Documentation (EN)](docs/en.md)
- [Dokumentation (DE)](docs/de.md)
- [Documentation (FR)](docs/fr.md)
- [Documentatie (NL)](docs/nl.md)
- [Documentación (ES)](docs/es.md)
- [Issue Tracker](https://github.com/OleSint/ha-battery-status-manager/issues)

## License

[The Unlicense](LICENSE) — public domain, use freely, no attribution required.
