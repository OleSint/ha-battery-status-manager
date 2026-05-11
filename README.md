# HA - Battery Status Manager

> 🇩🇪 [Deutsche Version](#deutsche-version) | 🇬🇧 [English Version](#english-version)

---

## Deutsche Version

Eine HACS-Integration für Home Assistant, die Batteriezustände überwacht und Benachrichtigungen sendet.

### Funktionen

- **Flexible Überwachung**: Alle Batterieentitäten, Auswahl nach Gerät oder Auswahl nach einzelnen Entitäten
- **Schwellenwert-Benachrichtigungen**: Benachrichtigung, wenn ein Akku unter einen konfigurierbaren Schwellenwert fällt (z. B. unter 20%)
- **Verlustrate-Benachrichtigungen**: Benachrichtigung, wenn ein Akku innerhalb eines konfigurierbaren Zeitraums stark entladen wird (z. B. mehr als 20% in 24 Stunden)
- **Alle HA-Benachrichtigungsdienste**: Unterstützung aller in Home Assistant konfigurierten `notify`-Dienste
- **Persistenz**: Verlaufs- und Benachrichtigungsdaten werden über Neustarts hinweg gespeichert
- **Nachkonfigurierbar**: Einstellungen können jederzeit über die Integrationsseite angepasst werden

### Installation via HACS

1. HACS in Home Assistant öffnen
2. **Integrationen** → **Benutzerdefinierte Repositories** → `https://github.com/OleSint/ha-battery-status-manager`, Kategorie: **Integration**
3. Nach der Integration suchen: **HA - Battery Status Manager**
4. Installation bestätigen und Home Assistant neu starten
5. Unter **Einstellungen → Integrationen → Integration hinzufügen** nach „Battery Status Manager" suchen

### Konfiguration

Der Setup-Assistent führt durch vier Schritte:

#### 1. Überwachungsbereich

| Option | Beschreibung |
|--------|-------------|
| Alle Batterieentitäten | Überwacht automatisch alle erkannten Batteriesensoren |
| Auswahl nach Gerät | Wähle gezielt Geräte aus; alle Batterieentitäten dieser Geräte werden überwacht |
| Auswahl nach Entität | Wähle einzelne Batterieentitäten aus einer Liste (alle vorausgewählt) |

#### 2. Schwellenwerte

- **Niedrig-Schwellenwert**: Benachrichtigung, wenn Ladestand unter diesen Wert fällt (Standard: 20%)
- **Verlustrate-Erkennung**: Benachrichtigung, wenn Ladestand um mehr als X% in Y Stunden sinkt (Standard: 20% in 24 h, Zeitfenster bis 168 h konfigurierbar)

#### 3. Benachrichtigungsdienste

Alle konfigurierten `notify.*`-Dienste sind als Mehrfachauswahl verfügbar. Der Benachrichtigungstitel ist frei anpassbar.

### Benachrichtigungsbeispiele

```
⚠️ Türsensor Eingang: Batteriestand bei 15% (Schwelle: 20%)
📉 Bewegungsmelder Garten: Batteriestand um 25% innerhalb von 24h gesunken (aktuell: 55%)
```

### Funktionsweise

- Batteriezustände werden **stündlich** geprüft
- Niedrig-Benachrichtigungen haben eine **Hysterese von 5%**: nach dem Versenden wird die Benachrichtigung erst zurückgesetzt, wenn der Ladestand wieder auf `Schwellenwert + 5%` steigt
- Verlustrate-Benachrichtigungen haben einen **Cooldown** in Höhe des konfigurierten Zeitfensters
- Die Integration ist **rein lesend** – sie kann nichts in deiner HA-Konfiguration verändern oder beschädigen

### Anforderungen

- Home Assistant 2023.6.0 oder neuer
- Mindestens ein konfigurierter `notify`-Dienst

### Lizenz

MIT License – Nutzung, Veränderung und Weitergabe ohne Einschränkungen.

---

## English Version

A HACS integration for Home Assistant that monitors battery levels across your devices and sends notifications when batteries run low or drain unusually fast.

### Features

- **Flexible monitoring scope** — monitor all battery entities at once, select specific devices, or hand-pick individual entities
- **Low battery alerts** — get notified when any battery drops below a configurable threshold (e.g. below 20%)
- **Rapid drain detection** — get notified when a battery loses more than a defined percentage within a set time window (e.g. more than 20% within 24 hours)
- **All native HA notification services** — supports every `notify` service configured in your Home Assistant instance, with multi-select
- **Persistent history** — battery level history and notification state survive restarts
- **Fully reconfigurable** — all settings can be changed at any time via the integration's Configure button

### Installation via HACS

1. Open HACS in Home Assistant
2. Go to **Integrations** → **Custom repositories**
3. Add `https://github.com/OleSint/ha-battery-status-manager` as category **Integration**
4. Search for **HA - Battery Status Manager** and install it
5. Restart Home Assistant
6. Go to **Settings → Integrations → Add Integration** and search for **Battery Status Manager**

### Configuration

The setup wizard guides you through four steps:

#### 1. Monitoring scope

| Option | Description |
|--------|-------------|
| All battery entities | Automatically monitors every battery sensor found in HA |
| Select by device | Choose specific devices; all their battery entities are monitored |
| Select by entity | Pick individual battery entities from a list (all pre-selected by default) |

#### 2. Thresholds

- **Low battery threshold** — notification is sent when a battery falls below this value (default: 20%, slider 1–99%)
- **Rapid drain detection** — enable to get notified when a battery drops by more than X% within Y hours (default: 20% in 24 h, window configurable up to 168 h)

#### 3. Notification services

All configured `notify.*` services are available as a multi-select list. You can also set a custom notification title.

### Notification examples

```
⚠️ Front Door Sensor: Battery at 15% (threshold: 20%)
📉 Garden Motion Sensor: Battery dropped 25% within 24h (current: 55%)
```

### How it works

- Battery levels are checked **every hour**
- Low battery notifications include a **5% hysteresis**: once sent, the notification resets only after the battery recovers above `threshold + 5%`, preventing notification spam during fluctuations
- Rapid drain notifications respect a **cooldown** equal to the configured time window before they can fire again for the same entity
- The integration is **read-only** — it cannot break or modify anything in your HA setup

### Requirements

- Home Assistant 2023.6.0 or newer
- At least one configured `notify` service

### License

MIT License — free to use, modify and distribute.
