# Opdracht 21 nov: van losse modi naar één begeleide ervaring

Start een sessie met: "Lees CLAUDE.md, docs/STATUS.md en docs/OPDRACHT-21nov.md en voer de opdracht uit."

## Visie in één zin
Een nieuwe bezoeker wordt in één minuut door het luchtruim geleid en kiest dan zelf: **kaart verkennen**, **vliegen met missies** of **vrij vliegen**. Vliegen voelt als een echte flightsim. De app leert je de regels zonder te betuttelen.

## Volgorde
0 → 1 → 2 → 3 → 4 → 5 → 6. Eerst de kleine dingen die Christian direct merkt. Het grote blok (5, tutorial) begint met een mock of screenshot, zodat Christian kan bijsturen. Per blok werk je zo:
1. eerst een test die faalt, daarna de bouw;
2. `--quick` draaien;
3. een preview-link naar Christian sturen.

## 0. Live zetten wat klaar is
- Op `wip/live-21nov` staan:
  - de ENR 5.5-terreinen;
  - de liggende sonde;
  - de fix voor de terreinmeldingen.
- Draai de volledige suite en zet het daarna live (eerst `release/<datum>` bewaren).

## 1. Besturing desktop zoals MSFS (S–M)
- **Toetsen:**
  - W en ↑ = neus omlaag;
  - S en ↓ = neus omhoog;
  - A en ← = links;
  - D en → = rechts.
- **Looping:**
  - Blijf je trekken (S vasthouden), dan maakt het toestel een volledige looping.
  - De bestaande looping blijft ("geniaal", Boyd).
- **Stuurknoppen op het scherm:**
  - Op desktop weghalen.
  - Op mobiel blijven ze, naast kantelen.
- **Ballon:** zie open vraag 1.

## 2. Sneltoetskaart vóór de vlucht (S)
- Eén compacte kaart met de toetsen van het gekozen toestel, plus Spatie, pauze en tempo.
- Met elke toets of tik ga je verder. "Niet meer tonen" wordt onthouden.
- Je opent hem weer met `?` of `H`.

## 3. Keerpunten met Spatie (S)
- Bereik je een keerpunt, dan verschijnt de melding: "Keerpunt bereikt — Spatie: volgende".
- Na het laatste keerpunt meldt de app dat de missie geslaagd is, met uitleg. Spatie start dan de volgende missie.
- Op mobiel tik je op de melding.

## 4. Herkenningspunten: precies genoeg (M)
- Loop alle punten langs met de regels uit het archief (backlog sprint 2). Een punt moet:
  - zichtbaar zijn vanaf 1500–3000 ft;
  - een unieke vorm hebben;
  - op de ICAO-kaart of in de lesstof staan;
  - landelijk toepasbaar zijn (OSM-tags).
- **Eerst een tabel** (houden / weg / toevoegen, met reden) die Christian goedkeurt. Pas daarna bouwen.
- Zeker toevoegen:
  - de grote **bruggen over Maas en Waal** (Grave, Nijmegen: Waalbrug en De Oversteek; de regio loopt nu tot 52,15 N);
  - knooppunten;
  - kanalen;
  - vliegvelden met de vorm van de baan.
- Verdacht overbodig: sluis Heumen en kerken zonder geverifieerde hoogte.
- **Klaar als:** er elke ±10 km één of twee duidelijke punten zijn, en geen enkel punt de regels niet haalt.

## 5. Tutorial en startflow (L, hoofdblok)
1. **Intro van ±1 minuut** op basis van de bestaande rondleiding, ingekort tot de kern. "Overslaan" is altijd zichtbaar.
2. **Keuzescherm** met drie tegels:
   - **Kaart verkennen**;
   - **Vliegen met missies**;
   - **Vrij vliegen** (luchtruim aan/uit).
3. **Toestelkeuze** vóór elke vlucht, met één zin uitleg per toestel.
4. **Sneltoetskaart** (blok 2). Daarna start de vlucht.
5. Een terugkerende bezoeker slaat de intro over en komt direct op het keuzescherm. In het menu staat "Rondleiding opnieuw".
6. **Menu's herindelen** volgens deze flow:
   - één hoofdmenu;
   - de drie keuzes;
   - Toestel, Weergave en Over/disclaimer.
   - Wat overbodig is, gaat weg. De UI blijft ≤ ⅓ van het scherm.
- **Klaar als:** een nieuwe tester zonder uitleg binnen 2 minuten in de modus van zijn keuze vliegt, op desktop én op mobiel.

## 6. Ballon realistischer (M; tip van Gemini, eerst controleren tegen de AIP of de praktijk)
- **Windprofiel:**
  - De ruiming en de snelheidstoename zitten vooral in de onderste 500–1500 ft. Bijvoorbeeld van 6 kt aan de grond naar 15–20 kt op 3000 ft, met 25–40° ruiming.
  - Daarboven blijft de wind ongeveer gelijk.
- **Traagheid:**
  - Na het branden duurt het 5–10 s voordat de ballon stijgt.
  - Normale stijg- en daalsnelheid: 300–500 ft/min, maximaal ~1000 ft/min.
  - Op ×1 verandert de hoogte nooit in één keer.
- **Dagdeel:**
  - Avond: rustig, met een duidelijke ruiming.
  - Overdag: thermiek, onrustig. Toon de hint "in de praktijk vaar je vooral 's ochtends vroeg of 's avonds" als praktijk, niet als regel.
- **Missie:**
  - Start ZW van Eindhoven en vaar langs de CTR zonder erin te drijven.
  - **Controleer eerst** de bovenkant van de CTR en de ondergrenzen van de TMA's (AIP EHEH AD 2.17, ENR 2.1). "Boven de CTR maar onder de TMA" kan alleen als daar ruimte tussen zit.

## Open vragen aan Christian
1. **Ballon:** W/↑ = branden en S/↓ = dalen (voorstel; een ballon heeft geen neus)? Of ook hier S = omhoog?
2. **Vrij vliegen:** luchtruim standaard aan of uit?
3. **Na de laatste missie:** opnieuw beginnen, of terug naar het keuzescherm?

## Al gedaan (21 nov)
- Blok 0 (behalve live), 1, 2, 3 en de bruggen uit blok 4: zie STATUS. Herkenningspunten-tabel: `docs/herkenningspunten-voorstel.md`.
- Liergebieden: de meldingen kwamen elke 4 s terug. Dat was een bug, niet zo bedoeld. Nu krijg je één melding per nadering, net als bij luchtruim (`d_enr55_sites`).
