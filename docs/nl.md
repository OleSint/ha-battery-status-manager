# Battery Status Manager — Documentatie (Nederlands)

> **Terug naar:** [README](../README.md) | [EN](en.md) | [DE](de.md) | [FR](fr.md) | [ES](es.md)

---

## Inhoudsopgave

1. [Wat doet deze integratie?](#1-wat-doet-deze-integratie)
2. [Vereisten](#2-vereisten)
3. [Installatie](#3-installatie)
4. [Eerste installatie](#4-eerste-installatie)
5. [Bewakingsomvang](#5-bewakingsomvang)
6. [Drempelwaarden](#6-drempelwaarden)
7. [Meldingen](#7-meldingen)
8. [Wekelijks rapport](#8-wekelijks-rapport)
9. [Instellingen later aanpassen](#9-instellingen-later-aanpassen)
10. [Hoe meldingen werken (technische details)](#10-hoe-meldingen-werken-technische-details)
11. [Problemen oplossen](#11-problemen-oplossen)

---

## 1. Wat doet deze integratie?

Battery Status Manager houdt alle op batterijen werkende apparaten in uw Home Assistant in de gaten en stuurt een melding als actie nodig is. De integratie is ontworpen om eenmaal in te stellen en daarna stil op de achtergrond te werken.

Belangrijkste functies:

- Stuurt een **waarschuwing** wanneer een batterij onder een instelbaar niveau zakt (bijv. 20 %).
- Stuurt een **kritieke melding** wanneer een batterij een gevaarlijk laag niveau bereikt (bijv. 10 %).
- Detecteert **snelle ontlading** (bijv. 20 % verlies in 24 uur) en waarschuwt direct.
- Bevat een **uitputtingsprognose** in elke melding — de integratie schat hoeveel dagen de batterij nog meegaat op basis van de gemeten ontladingssnelheid.
- Stuurt **herinneringen** met instelbare tussenpozen als een batterij laag blijft.
- Genereert optioneel een **wekelijks samenvattingsrapport** op een dag en tijdstip naar keuze.
- Respecteert een **tijdvenster** en **actieve dagen**, zodat u 's nachts niet onnodig gewekt wordt.

---

## 2. Vereisten

- Home Assistant **2023.6** of nieuwer.
- Minimaal één **meldingsservice** geconfigureerd in Home Assistant (bijv. de officiële mobiele app, een Telegram-bot of een e-mailnotificator). Deze verschijnen als `notify.uw_service` in Home Assistant.

---

## 3. Installatie

### Via HACS (aanbevolen)

HACS is de Home Assistant Community Store. Als u dit nog niet heeft, volg dan de [HACS-installatiehandleiding](https://hacs.xyz/docs/use/download/download/).

1. Open HACS in de zijbalk van Home Assistant.
2. Ga naar **Integraties**.
3. Klik op het drie-puntenmenu (⋮) rechtsboven en kies **Aangepaste opslagplaatsen**.
4. Plak `https://github.com/OleSint/ha-battery-status-manager` en selecteer **Integratie** als categorie. Klik op **Toevoegen**.
5. Sluit het venster. Zoek naar **Battery Status Manager** in de HACS-integratielijst.
6. Klik erop en vervolgens op **Downloaden** (rechtsonder).
7. **Herstart Home Assistant** (Instellingen → Systeem → Herstart).

### Handmatige installatie

1. Download de nieuwste versie-ZIP van [GitHub Releases](https://github.com/OleSint/ha-battery-status-manager/releases).
2. Pak het uit en kopieer de map `custom_components/battery_status_manager` naar de map `config/custom_components/` van uw Home Assistant-installatie.
3. Herstart Home Assistant.

---

## 4. Eerste installatie

Na het herstarten:

1. Ga naar **Instellingen → Apparaten en diensten**.
2. Klik op **+ Integratie toevoegen** (rechtsonder).
3. Zoek naar **Battery Status Manager** en klik erop.
4. Volg de installatiewizard (4 stappen, hieronder beschreven).

---

## 5. Bewakingsomvang

In de eerste stap van de wizard kiest u welke batterijen bewaakt worden.

### Optie A — Alle batterijen

Bewaakt elke entiteit in Home Assistant met de apparaatklasse `battery`. Dit is de eenvoudigste optie en omvat automatisch nieuwe apparaten die u later toevoegt.

Na het kiezen van "Alle" kunt u optioneel specifieke entiteiten **uitsluiten** (bijv. een defecte batterijsensor die altijd 0 % toont).

### Optie B — Per apparaat

U ziet een lijst van alle apparaten met minimaal één batterijentiteit. Selecteer één of meerdere apparaten. Alleen batterijentiteiten van de geselecteerde apparaten worden bewaakt.

### Optie C — Per entiteit

U ziet een lijst van alle batterijentiteiten in Home Assistant. Selecteer precies welke bewaakt moeten worden.

---

## 6. Drempelwaarden

### Waarschuwingsdrempel (⚠️)

- **Lage batterij waarschuwing inschakelen** — Schakel dit in om een melding te ontvangen wanneer een batterij onder de waarschuwingsdrempel zakt.
- **Waarschuwingsdrempel (%)** — Het percentage waaronder een waarschuwing wordt verzonden. Standaard: 20 %.

### Kritieke drempel (🚨)

- **Kritieke batterijmelding inschakelen** — Schakel dit in voor een tweede, urgentere melding op een zeer laag niveau.
- **Kritieke drempel (%)** — Moet lager zijn dan de waarschuwingsdrempel. Standaard: 10 %.

### Snelle ontladingsdetectie

- **Snelle ontladingsmelding inschakelen** — Schakel dit in om gewaarschuwd te worden bij ongewoon snelle ontlading.
- **Ontladingsdrempel (%)** — Hoeveel procentpunten verlies een melding triggert. Voorbeeld: 20 %.
- **Observatievenster (uren)** — Over hoeveel uren het verlies wordt gemeten. Voorbeeld: 24 uur.

---

## 7. Meldingen

### Meldingsservices

Selecteer welke `notify.*`-services de meldingen moeten ontvangen. Meerdere keuzes mogelijk. Minimaal één is vereist.

### Meldingstittel

De titel die verschijnt bij pushmeldingen of e-mails. Standaard: `Battery Status Manager`.

### Tijdvenster (optioneel)

Schakel dit in om meldingen te beperken tot een bepaald tijdsbereik.

- **Begin tijdvenster** — Vroegste tijdstip waarop een melding mag worden verzonden. Voorbeeld: `08:00`.
- **Einde tijdvenster** — Laatste tijdstip. Voorbeeld: `20:00`.

Nachtelijke vensters worden correct verwerkt: start `22:00` en einde `07:00` staat meldingen toe tussen 22:00 en 7:00 uur.

> Meldingen die worden onderdrukt omdat ze buiten het tijdvenster vallen, worden **niet in de wachtrij geplaatst** — ze worden gewoon overgeslagen.

### Actieve dagen (optioneel)

Kies de weekdagen waarop meldingen verzonden mogen worden. Standaard zijn alle zeven dagen actief.

### Herinnering (optioneel)

- **Herinnering inschakelen** — Als een batterij na de eerste melding nog steeds onder de drempel ligt, wordt na het ingestelde interval een herinnering gestuurd.
- **Herinneringsinterval (uren)** — Hoe vaak de herinnering wordt herhaald. Voorbeeld: 24 uur.

---

## 8. Wekelijks rapport

Het wekelijkse rapport is volledig optioneel. Wanneer ingeschakeld, stuurt de integratie eens per week een samenvatting.

- **Wekelijks rapport inschakelen** — Schakelt het rapport in.
- **Dag van de week voor rapport** — Op welke dag het rapport wordt verzonden (bijv. maandag).
- **Tijdstip voor rapport** — Op welk tijdstip (bijv. 09:00).

### Inhoud van het rapport

- Totaal aantal bewaakte batterijen.
- Aantal batterijen momenteel onder de waarschuwingsdrempel.
- Aantal batterijen momenteel onder de kritieke drempel.
- Aantal batterijen dat de afgelopen 7 dagen is hersteld of vervangen.
- 7-daagse prognose: batterijen die momenteel boven de drempel liggen maar naar verwachting binnen 7 dagen eronder zullen zakken.

Het rapport wordt maximaal eenmaal per 7-daagse periode verzonden.

---

## 9. Instellingen later aanpassen

Alle instellingen kunnen op elk moment worden gewijzigd:

1. Ga naar **Instellingen → Apparaten en diensten**.
2. Vind de **Battery Status Manager**-kaart.
3. Klik op **Configureren**.
4. Doorloop de wizard opnieuw — uw vorige waarden zijn vooraf ingevuld.

---

## 10. Hoe meldingen werken (technische details)

### Controle-interval

De integratie controleert alle batterijniveaus elke **60 minuten**.

### Één melding per niveau

Wanneer zowel de waarschuwing als de kritieke melding zijn ingeschakeld, stuurt de integratie per controle altijd maar **één** melding — nooit beide tegelijk:

- Batterij onder de **kritieke drempel** → alleen de 🚨 kritieke melding wordt verstuurd. De waarschuwing wordt onderdrukt, omdat de kritieke melding al de meest urgente informatie bevat.
- Batterij onder de **waarschuwingsdrempel** maar boven de kritieke drempel → alleen de ⚠️ waarschuwing wordt verstuurd.

### Hysterese

Om herhaalde meldingen voor hetzelfde evenement te voorkomen:

- Een batterij onder de **waarschuwingsdrempel** triggert een waarschuwing. Er wordt geen nieuwe waarschuwing gestuurd totdat de batterij boven `waarschuwingsdrempel + 5 %` herstelt.
- Een batterij onder de **kritieke drempel** triggert een kritieke melding. Er wordt geen nieuwe gestuurd totdat de batterij boven `kritieke drempel + 3 %` herstelt.

Voorbeeld: waarschuwingsdrempel = 20 %, kritieke drempel = 10 %. Een batterij op 8 % triggert alleen een kritieke melding. Er wordt geen nieuwe kritieke melding gestuurd totdat de batterij boven 13 % stijgt en dan weer onder 10 % zakt. Herstelt de batterij naar 12 % (boven kritiek maar nog onder de waarschuwingsdrempel), dan wordt op dat moment een waarschuwing gestuurd.

### Uitputtingsprognose

De integratie slaat een geschiedenis op van batterijmetingen. Met minimaal 3 datapunten over minimaal 2 uur berekent het een lineaire ontladingssnelheid en extrapoleert hoeveel dagen er nog resteren.

### Gegevensopslag

Alle statusgegevens worden opgeslagen in het bestand `.storage/battery_status_manager` van Home Assistant en blijven bewaard na herstarten.

---

## 11. Problemen oplossen

**Geen melding ontvangen**
- Controleer of een `notify.*`-service correct is geconfigureerd en geselecteerd.
- Controleer het tijdvenster en de actieve dagen.
- Het batterijniveau moet onder de drempel liggen op het moment van de uurlijkse controle.

**Te veel meldingen**
- Hysterese is standaard actief. Controleer of het batterijniveau schommelt rond de drempelwaarde.

**Een entiteit verschijnt niet in de selectielijst**
- Alleen entiteiten met apparaatklasse `battery` en een numerieke waarde (0–100) zijn inbegrepen.

**Het wekelijks rapport komt niet aan**
- Het rapport wordt maximaal eenmaal per 7 dagen verzonden. Controleer de geconfigureerde dag en tijd.

**Iets anders werkt niet**
- Bekijk de Home Assistant logs (Instellingen → Systeem → Logboeken) en zoek naar `battery_status_manager`.
- Maak een issue aan op [GitHub](https://github.com/OleSint/ha-battery-status-manager/issues).
