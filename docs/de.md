# Battery Status Manager — Dokumentation (Deutsch)

> **Zurück zu:** [README](../README.md) | [EN](en.md) | [FR](fr.md) | [NL](nl.md) | [ES](es.md)

---

## Inhaltsverzeichnis

1. [Was macht diese Integration?](#1-was-macht-diese-integration)
2. [Voraussetzungen](#2-voraussetzungen)
3. [Installation](#3-installation)
4. [Ersteinrichtung](#4-ersteinrichtung)
5. [Überwachungsbereich](#5-überwachungsbereich)
6. [Schwellenwerte](#6-schwellenwerte)
7. [Benachrichtigungen](#7-benachrichtigungen)
8. [Wöchentlicher Bericht](#8-wöchentlicher-bericht)
9. [Einstellungen nachträglich ändern](#9-einstellungen-nachträglich-ändern)
10. [Wie Benachrichtigungen funktionieren (technische Details)](#10-wie-benachrichtigungen-funktionieren-technische-details)
11. [Fehlerbehebung](#11-fehlerbehebung)

---

## 1. Was macht diese Integration?

Der Battery Status Manager überwacht alle akkubetriebenen Geräte in Home Assistant und benachrichtigt dich, wenn Handlungsbedarf besteht. Er ist darauf ausgelegt, einmal eingerichtet zu werden und danach still im Hintergrund zu laufen.

Wichtigste Funktionen:

- Sendet eine **Warnung**, wenn ein Akku unter einen konfigurierbaren Wert fällt (z. B. 20 %).
- Sendet eine **kritische Meldung**, wenn ein Akku einen gefährlich niedrigen Stand erreicht (z. B. 10 %).
- Erkennt **starken Ladestandsverlust** (z. B. 20 % Verlust innerhalb von 24 Stunden) und gibt sofort Alarm.
- Enthält eine **Entleerungsprognose** in jeder Benachrichtigung — die Integration schätzt auf Basis der gemessenen Entladerate, wie viele Tage der Akku noch hält.
- Sendet **Erinnerungen** in konfigurierbaren Abständen, falls ein Akku weiterhin leer bleibt.
- Erstellt optional einen **wöchentlichen Zusammenfassungsbericht** an einem frei wählbaren Tag und zu einer frei wählbaren Uhrzeit.
- Respektiert ein **Zeitfenster** und **aktive Wochentage**, damit du nachts nicht unnötig geweckt wirst.

---

## 2. Voraussetzungen

- Home Assistant **2023.6** oder neuer.
- Mindestens ein **Benachrichtigungsdienst** in Home Assistant (z. B. die offizielle Mobile App, ein Telegram-Bot oder ein E-Mail-Dienst). Diese erscheinen als `notify.dein_dienst` in Home Assistant.

---

## 3. Installation

### Über HACS (empfohlen)

HACS ist der Home Assistant Community Store. Falls du ihn noch nicht hast, folge der [HACS-Installationsanleitung](https://hacs.xyz/docs/use/download/download/).

1. Öffne HACS in der Home Assistant Seitenleiste.
2. Gehe zu **Integrationen**.
3. Klicke auf das Drei-Punkte-Menü (⋮) oben rechts und wähle **Benutzerdefinierte Repositories**.
4. Füge `https://github.com/OleSint/ha-battery-status-manager` ein und wähle **Integration** als Kategorie. Klicke auf **Hinzufügen**.
5. Schließe den Dialog. Suche nach **Battery Status Manager** in der HACS-Integrationsliste.
6. Klicke darauf und dann auf **Herunterladen** (unten rechts).
7. **Starte Home Assistant neu** (Einstellungen → System → Neustart).

### Manuelle Installation

1. Lade das aktuelle Release-ZIP von [GitHub Releases](https://github.com/OleSint/ha-battery-status-manager/releases) herunter.
2. Entpacke es und kopiere den Ordner `custom_components/battery_status_manager` in das Verzeichnis `config/custom_components/` deiner Home Assistant-Installation.
3. Starte Home Assistant neu.

---

## 4. Ersteinrichtung

Nach dem Neustart:

1. Gehe zu **Einstellungen → Geräte & Dienste**.
2. Klicke auf **+ Integration hinzufügen** (unten rechts).
3. Suche nach **Battery Status Manager** und klicke darauf.
4. Folge dem Einrichtungsassistenten (4 Schritte, unten beschrieben).

---

## 5. Überwachungsbereich

Im ersten Schritt des Assistenten wählst du aus, welche Batterien überwacht werden sollen.

### Option A — Alle Batterien

Überwacht jede Entität in Home Assistant mit der Geräteklasse `battery`. Das ist die einfachste Option und schließt automatisch neue Geräte ein, die du später hinzufügst.

> **Neue Geräte werden automatisch erkannt.** Wenn du ein neues Gerät zu Home Assistant hinzufügst, wird es ab der nächsten stündlichen Prüfung automatisch überwacht — ohne dass du die Konfiguration anpassen musst.

Nach der Auswahl „Alle" kannst du optional bestimmte Entitäten **ausschließen** (z. B. einen Batteriesensor, der dauerhaft 0 % anzeigt, weil er defekt ist).

### Option B — Nach Gerät

Du siehst eine Liste aller Geräte, die mindestens eine Batterieentität haben. Wähle ein oder mehrere Geräte aus. Nur Batterieentitäten der gewählten Geräte werden überwacht.

> **Neue Geräte werden nicht automatisch hinzugefügt.** Wenn du ein neues Gerät zu Home Assistant hinzufügst und es überwachen möchtest, gehe auf **Konfigurieren** auf der Integrationskarte und füge es manuell zur Auswahl hinzu.

### Option C — Nach Entität

Du siehst eine Liste aller Batterieentitäten in Home Assistant. Wähle genau aus, welche überwacht werden sollen.

> **Neue Entitäten werden nicht automatisch hinzugefügt.** Wenn du ein neues Gerät hinzufügst, gehe auf **Konfigurieren** und ergänze die neue Entität in der Auswahl.

---

## 6. Schwellenwerte

### Warn-Schwellenwert (⚠️)

- **Warnung bei niedrigem Ladestand aktivieren** — Aktivieren, um eine Benachrichtigung zu erhalten, wenn ein Akku den Warn-Wert unterschreitet.
- **Warn-Schwellenwert (%)** — Prozentwert, unter dem eine Warnung gesendet wird. Standard: 20 %.

### Kritischer Schwellenwert (🚨)

- **Kritische Benachrichtigung aktivieren** — Aktivieren, um eine zweite, dringendere Meldung bei sehr niedrigem Stand zu erhalten.
- **Kritischer Schwellenwert (%)** — Muss niedriger als der Warn-Schwellenwert sein. Standard: 10 %.

### Starker Ladestandsverlust

- **Benachrichtigung bei starkem Ladestandsverlust aktivieren** — Aktivieren, um bei ungewöhnlich schneller Entladung gewarnt zu werden.
- **Verlust-Schwellenwert (%)** — Wie viele Prozentpunkte Verlust eine Meldung auslösen. Beispiel: 20 %.
- **Beobachtungszeitraum (Stunden)** — Über wie viele Stunden der Verlust gemessen wird. Beispiel: 24 Stunden.

> **Tipp:** Ein Verlust von 20 % in 24 Stunden ist für die meisten Sensorakkus ungewöhnlich, die normalerweise monatelang halten. Diese Funktion ist hilfreich, um fehlerhafte Akkus oder versehentlich aktive Geräte zu erkennen.

### Gerät meldet sich nicht mehr (📵)

- **Benachrichtigung wenn Gerät nicht mehr erreichbar** — Aktivieren, um benachrichtigt zu werden, wenn ein Gerät, das bisher einen Akkustand gemeldet hat, gar keine Daten mehr sendet.
- **Wartezeit bis zur Meldung** — Wie lange das Gerät still sein muss, bevor die Meldung gesendet wird: **12 Stunden** oder **24 Stunden**.

Das ist oft das zuverlässigste Zeichen für eine vollständig leere Batterie: Das Gerät verschwindet einfach aus Home Assistant, weil es keine Energie mehr hat, um sich zu melden.

> Die Meldung wird nur gesendet, wenn das Gerät zuvor mindestens einmal einen gültigen Akkustand gemeldet hat. Neue Geräte, die noch nie sichtbar waren, werden ignoriert. Sobald das Gerät wieder online ist, wird die Meldung automatisch zurückgesetzt.

---

## 7. Benachrichtigungen

### Benachrichtigungsdienste

Wähle aus, welche `notify.*`-Dienste die Benachrichtigungen erhalten sollen. Mehrfachauswahl möglich. Mindestens einer ist erforderlich.

### Betreff / Titel der Benachrichtigung

Der Titel, der bei Push-Benachrichtigungen oder E-Mails erscheint. Standard: `Battery Status Manager`.

### Zeitfenster (optional)

Aktivieren, um Benachrichtigungen auf einen bestimmten Zeitraum einzuschränken.

- **Beginn des Zeitfensters** — Frühester Zeitpunkt, ab dem benachrichtigt wird. Beispiel: `08:00`.
- **Ende des Zeitfensters** — Spätester Zeitpunkt. Beispiel: `20:00`.

Zeitfenster über Mitternacht werden korrekt behandelt: Start `22:00` und Ende `07:00` erlaubt Benachrichtigungen zwischen 22:00 und 7:00 Uhr.

> Benachrichtigungen, die aufgrund des Zeitfensters unterdrückt werden, werden **nicht in eine Warteschlange gestellt** — sie werden einfach übersprungen. Bei der nächsten Prüfung (eine Stunde später) wird erneut geprüft und ggf. gesendet, wenn der Zustand immer noch zutrifft und die Zeit im erlaubten Fenster liegt.

### Aktive Wochentage (optional)

Wähle die Wochentage, an denen Benachrichtigungen gesendet werden dürfen. Standardmäßig sind alle sieben Tage aktiv. Du kannst z. B. das Wochenende deaktivieren.

### Erinnerung (optional)

- **Erinnerung aktivieren** — Wenn ein Akku nach der ersten Benachrichtigung weiterhin unter dem Schwellenwert liegt, wird nach dem konfigurierten Intervall eine Erinnerung gesendet.
- **Erinnerungsintervall (Stunden)** — Wie oft die Erinnerung wiederholt wird. Beispiel: 24 Stunden.

Die Erinnerung respektiert ebenfalls Zeitfenster und aktive Wochentage.

---

## 8. Wöchentlicher Bericht

Der wöchentliche Bericht ist vollständig optional. Wenn er aktiviert ist, sendet die Integration einmal pro Woche eine Zusammenfassung.

- **Wöchentlichen Bericht aktivieren** — Aktiviert den Wochenbericht.
- **Wochentag für den Bericht** — An welchem Tag der Bericht gesendet wird (z. B. Montag).
- **Uhrzeit für den Bericht** — Zu welcher Uhrzeit (z. B. 09:00).

### Inhalt des Berichts

- Gesamtzahl der überwachten Batterien.
- Anzahl der Batterien aktuell unter dem Warn-Schwellenwert.
- Anzahl der Batterien aktuell unter dem kritischen Schwellenwert.
- Anzahl der Batterien, die sich in den letzten 7 Tagen erholt haben oder ausgetauscht wurden.
- 7-Tage-Prognose: Batterien, die aktuell noch über dem Warn-Schwellenwert liegen, aber voraussichtlich innerhalb der nächsten 7 Tage darunter fallen werden.

Der Bericht wird maximal einmal pro 7-Tage-Zeitraum gesendet. Falls Home Assistant zur geplanten Zeit nicht läuft, wird der Bericht beim nächsten Check (innerhalb der nächsten Stunde) nachgeholt.

---

## 9. Einstellungen nachträglich ändern

Alle Einstellungen können jederzeit geändert werden:

1. Gehe zu **Einstellungen → Geräte & Dienste**.
2. Suche die Karte **Battery Status Manager**.
3. Klicke auf **Konfigurieren**.
4. Durchlaufe den Assistenten erneut — deine bisherigen Werte sind vorausgefüllt.

---

## 10. Wie Benachrichtigungen funktionieren (technische Details)

### Prüfintervall

Die Integration prüft alle Akkustände alle **60 Minuten**. Der genaue Zeitpunkt der ersten Prüfung hängt davon ab, wann Home Assistant gestartet wurde.

### Eine Benachrichtigung pro Stufe

Wenn Warnung und kritische Meldung beide aktiviert sind, sendet die Integration pro Prüfzyklus immer nur **eine** Benachrichtigung — nie beide gleichzeitig:

- Akku unter dem **kritischen Schwellenwert** → nur die 🚨 kritische Meldung wird gesendet. Die Warnung wird unterdrückt, da die kritische Meldung bereits die dringendere Information enthält.
- Akku unter dem **Warn-Schwellenwert**, aber über dem kritischen → nur die ⚠️ Warnung wird gesendet.

### Hysterese

Um wiederholte Benachrichtigungen für dasselbe Ereignis zu verhindern, verwendet die Integration Hysterese:

- Ein Akku unter dem **Warn-Schwellenwert** löst eine Warnung aus. Er löst keine weitere aus, bis er sich zunächst über `Warn-Schwellenwert + 5 %` erholt hat.
- Ein Akku unter dem **kritischen Schwellenwert** löst eine kritische Meldung aus. Er löst keine weitere aus, bis er sich über `Kritischer Schwellenwert + 3 %` erholt hat.

Beispiel: Warn-Schwellenwert = 20 %, kritischer Schwellenwert = 10 %. Ein Akku bei 8 % löst nur eine kritische Meldung aus. Er löst keine erneute kritische Meldung aus, bis er über 13 % gestiegen und dann wieder unter 10 % gefallen ist. Erholt er sich auf 12 % (über kritisch, aber noch unter Warn-Schwellenwert), wird an diesem Punkt eine Warnung gesendet.

### Entleerungsprognose

Die Integration speichert eine Historie der Akkustand-Messungen. Anhand der ältesten und neuesten Datenpunkte (mindestens 3 Messungen über mindestens 2 Stunden) berechnet sie eine lineare Entladerate. Daraus wird extrapoliert, wie viele Tage der Akku noch bis zur vollständigen Entladung hat.

Die Prognose wird in der Benachrichtigung angezeigt, wenn sie verfügbar ist. Wenn nicht genügend Daten vorliegen oder der Akku nicht tatsächlich entlädt, wird keine Prognose angezeigt.

### Erholungsverfolgung

Wenn ein Akku den Warn-Schwellenwert (einschließlich Hysterese-Marge) wieder überschreitet, wird dies als Erholungsereignis gespeichert. Diese Daten fließen in den Wochenbericht ein.

### Datenspeicherung

Alle Zustandsdaten (Benachrichtigungszeitstempel, Verlauf, Erholungen) werden in der Datei `.storage/battery_status_manager` in Home Assistant gespeichert. Diese Daten bleiben nach Neustarts erhalten.

---

## 11. Fehlerbehebung

**Keine Benachrichtigung erhalten**
- Prüfe, ob ein `notify.*`-Dienst korrekt konfiguriert und in der Integration ausgewählt ist.
- Prüfe Zeitfenster und aktive Wochentage — der aktuelle Zeitpunkt/Tag könnte ausgeschlossen sein.
- Prüfe den Akkustand: Er muss zum Zeitpunkt der stündlichen Prüfung unter dem Schwellenwert liegen.

**Zu viele Benachrichtigungen**
- Die Hysterese ist standardmäßig aktiv. Wenn der Akkustand um den Schwellenwert herum schwankt, kann es trotzdem zu mehreren Meldungen kommen.

**Eine bestimmte Entität erscheint nicht in der Auswahlliste**
- Nur Entitäten mit der Geräteklasse `battery` und einem numerischen Zustand (0–100) werden berücksichtigt. Virtuelle oder Template-Sensoren können ausgeschlossen sein.

**Der Wochenbericht kommt nicht an**
- Der Bericht wird nur einmal pro 7-Tage-Zeitraum gesendet. Prüfe den konfigurierten Tag und die Uhrzeit.
- Home Assistant muss zur geplanten Zeit oder danach laufen, damit der Check ausgelöst wird.

**Etwas anderes stimmt nicht**
- Prüfe die Home Assistant Logs (Einstellungen → System → Protokolle) und suche nach `battery_status_manager`.
- Eröffne ein Issue auf [GitHub](https://github.com/OleSint/ha-battery-status-manager/issues) mit dem Protokollinhalt.
