# Status — lees dit eerst

*Bijgewerkt: 25 nov 2026, nacht (geplande sessie). Backlog: **`docs/BACKLOG.md`** (enige lijst); uitwerking: `docs/OPDRACHT-23nov.md`.*

## Live
- https://luchtruim3d.nl = `main` = live-gang 25 nov (zie LOG): fixes Evoluon-klaring, knipperende labels, lieren als één cilinder.
  Terugdraaien: `release/2026-11-25` (= live van 22 nov + docs), daarvoor `release/2026-11-22`, `release/2026-11-21`, `release/2026-11-15`.
- Regio: Eindhoven + Arnhem–Nijmegen tot 52.15 N, AIRAC 11-2026.
- **Afgerond (Christian 23 nov):** kantelen op mobiel → niet meer aanpassen, alleen bij een bug.

## Eerstvolgende sessie (vr 27 nov 22:47) — in deze volgorde
0. **AIRAC-wissel 26 nov (AMDT 12-2026):** data-acties draaien do 26 nov. `git fetch origin data/lvnl data/eaip` → `python tools/build_airspace.py --bbox 4.75,51.2,6.25,52.15 --check` + `python tools/aip_check.py`, footer bijwerken.
1. **Malden:** overlappende cilinders zweef (groen) en model (oranje) → één volume of "gedeeld, niet gelijktijdig"; één melding (opdracht A3).
2. **Herkenningspunten:** A50-brug kwartslag gedraaid → oriëntatie uit OSM voor alle modellen; samen met `wip/herkenning-22nov`.
3. **Voorbeeldcircuit Eindhoven + missie "Land op Eindhoven" eruit** (`optCirc`, `optCircRw`, `buildCirc`, `missionEHEH`, `missionTick` + tests).
4. **Missies: progressie** easy → medium → lang/moeilijk, sterren, leerdoel (opdracht B). `d_missions_flown` vliegt elke missie nu echt uit: gebruik dat als basis voor de missiegenerator.

## Koers (Christian 22–23 nov) — top 5, even zwaar, bronnen moeten kloppen
1. Game-ervaring (opdracht B–D) · 2. procedureel landschap (Veluwezoom, Malden als kruis in het bos) · 3. heel NL (eerst data naar `data/*.json`) · 4. missies motor/zweef/ballon · 5. live eAIP/AIRAC/NOTAM (primaire bron: LVNL → Eurocontrol NOP → EAD Basic).
- Daarnaast: cookieloze teller (F), feedbackkanaal route A (I), categorisering educatie (J, klein blok per sessie).

## Half af
- `wip/herkenning-22nov`: bruggen/knooppunten afmaken + oriëntatiefix (zie punt 2). Bevat ook bos in `fetch_osm.py`.
- Feedbackkanaal route A: stappenplan voor Christians eenmalige setup nog voorbereiden.

## Wacht op Christian
- Vught 's avonds onzichtbaar: niet te reproduceren (EHP29 = H24 volgens ENR 5.1, in de app op elk tijdstip zichtbaar; test `d_h24_always`). Zie je het nog: screenshot met tijd en modus.

## Werkwijze-notities
- Cloud: `tools/e2e.py` valt terug op `/opt/pw-browsers/chromium`. Volledige suite duurt nu ±70 min (nieuwe missie-uitvliegtest).
- Overpass/eAIP/Geoportaal alleen via GitHub Actions bereikbaar; luchtruim3d.nl niet vanuit de cloud (deploy via GitHub controleren).
- Budget: 2 × ±25% per week (geplande sessies di+vr 22:47); weeklimiet niet afleesbaar → voorzichtig schatten.
- NOTAM: geen NOTAMs in de app tot er een geverifieerde primaire bron is; FAA alleen ter vergelijking.
- Oudere notities: zie `docs/LOG.md`.
