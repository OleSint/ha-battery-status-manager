# HA - Battery Status Manager

Eine HACS-Integration für Home Assistant, die Batteriezustände überwacht und Benachrichtigungen sendet.

## Funktionen

- **Flexible Überwachung**: Alle Batterieentitäten, Auswahl nach Gerät oder Auswahl nach einzelnen Entitäten
- **Schwellenwert-Benachrichtigungen**: Benachrichtigung, wenn ein Akku unter einen konfigurierbaren Schwellenwert fällt (z. B. unter 20%)
- **Verlustrate-Benachrichtigungen**: Benachrichtigung, wenn ein Akku innerhalb eines konfigurierbaren Zeitraums stark entladen wird (z. B. mehr als 20% in 24 Stunden)
- **Alle HA-Benachrichtigungsdienste**: Unterstützung aller in Home Assistant konfigurierten `notify`-Dienste
- **Persistenz**: Verlaufs- und Benachrichtigungsdaten werden über Neustarts hinweg gespeichert
- **Nachkonfigurierbar**: Einstellungen können jederzeit über die Integrationsseite angepasst werden

## Installation via HACS

1. HACS in Home Assistant öffnen
2. **Integrationen** → **Benutzerdefinierte Repositories** → https://github.com/OleSint/ha-battery-status-manager, Kategorie: **Integration**
3. Nach der Integration suchen: **HA - Battery Status Manager**
4. Installation bestätigen und Home Assistant neu starten
5. Unter **Einstellungen → Integrationen → Integration hinzufügen** nach „Battery Status Manager" suchen

## Konfiguration

Der Setup-Assistent führt durch vier Schritte:

### 1. Überwachungsbereich
| Option | Beschreibung |
|--------|-------------|
| Alle Batterieentitäten | Überwacht automatisch alle erkannten Batteriesensoren |
| Auswahl nach Gerät | Wähle gezielt Geräte aus; alle Batterieentitäten dieser Geräte werden überwacht |
| Auswahl nach Entität | Wähle einzelne Batterieentitäten aus einer Liste (alle vorausgewählt) |

### 2. Schwellenwerte
- **Niedrig-Schwellenwert**: Benachrichtigung, wenn Ladestand unter diesen Wert fällt (Standard: 20%)
- **Verlust-Schwellenwert**: Benachrichtigung, wenn Ladestand um mindestens X% in Y Stunden sinkt (Standard: 20% in 24h)

### 3. Benachrichtigungsdienste
Alle in Home Assistant konfigurierten `notify`-Dienste sind auswählbar (Mehrfachauswahl möglich).

## Benachrichtigungsbeispiele

```
⚠️ Türsensor Eingang: Batteriestand bei 15% (Schwelle: 20%)
📉 Bewegungsmelder Garten: Batteriestand um 25% innerhalb von 24h gesunken (aktuell: 55%)
```

## Hinweise

- Die Integration prüft Batteriezustände standardmäßig stündlich
- Niedrig-Benachrichtigungen werden erst nach Erholung auf `Schwellenwert + 5%` zurückgesetzt
- Verlust-Benachrichtigungen werden frühestens nach Ablauf des Beobachtungszeitraums erneut gesendet
- Deaktivierte Entitäten werden automatisch ausgeschlossen

## Anforderungen

- Home Assistant 2023.6.0 oder neuer
- Mindestens ein konfigurierter `notify`-Dienst
