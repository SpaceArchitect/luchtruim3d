# Log — beslissingen en lessen (nieuwste onderaan, één regel per stuk)

Oudere geschiedenis: claude.ai-project `claude/03-beslissingen-log.md` en `claude/sprints/`.

- 2026-11-09 Bron = LVNL-MapServer `geoservices.lvnl.nl/arcgis/rest/services/VFRchart/*` (GeoJSON); alleen bereikbaar via de browser op de pc.
- 2026-11-09 three.js met een lokale platte projectie; data ingebakken in `index.html`.
- 2026-11-10 Landen: het toestel stopt, de simulatie loopt door. Tijdsafhankelijk luchtruim volgens AIP GEN 2.1 §6 (feestdagen).
- 2026-11-14 Live op luchtruim3d.nl via GitHub Pages; publiceren = push naar `main`.
- 2026-11-15 Labels vervagen afgewezen: een label is er óf niet. Alle groepen standaard aan. Gevaren gaan voor.
- 2026-11-15 Teruggedraaid naar 053d823 na de kantel-bug op live. Les: sensortests met realistische ruis; geen fix na de laatste test.
- 2026-11-20 Nieuwe briefing (`CLAUDE.md`): doel boven proces, geen sprints/PI/DFMEA/verplicht panel. Testen evenredig (quick per commit, volledig vóór `main`). Eén omgeving voor cloud + pc via `tools/setup.py`. Repo = geheugen (`docs/STATUS.md`, `docs/LOG.md`).
- 2026-11-21 Kantelen geleidelijk (dode zone 8°, vol bij 35°/30°) op verzoek van Christian; knoppen/toetsen blijven vol.
- 2026-11-21 Missies: elk rond één echt conflict; startpunt berekend uit de LVNL-data (vrij, rechte lijn door het lesgebied) zodat AIRAC-wijzigingen niets breken. Ballon: alleen starts waarvoor een hoogteplan bestaat.
- 2026-11-21 Uitbreiding: luchtruim landelijk in één keer (klein), landschap/AIP/missies per regio. Arnhem–Nijmegen eerst; full reset vóór 10 dec voor "heel NL"; data vóór Mexico binnen.
- 2026-11-21 Push naar `main` door Claude werd tegengehouden door de veiligheidscheck → publiceren alleen na Christians expliciete "ok, live".
- 2026-11-21 LVNL (gis@lvnl.nl): Geoportaal is de aangewezen bron (AIRAC-updates, licentie in metadata); niet bouwen op de VFR-chart-services. GitHub Actions (akkoord Christian) bereikt het Geoportaal wel, de eAIP niet.
- 2026-11-21 Draaimoment: oorzaak bocht = vertraagde schermstandwissel (rol ±90° in het oude scherm). Aanpak: draai herkennen aan rol > 55°, koers/hoogte terugzetten, ijken na rust.
- 2026-11-21 Licentie geregeld: LVNL Geoportaal-datasets (o.a. Airspace) staan onder CC BY 4.0 (metadata). Bronvermelding "LVNL, CC BY 4.0" in de footer.
- 2026-11-21 Vanaf GitHub Actions bereikbaar: Geoportaal-API, eAIP (curl + UA), Overpass, luchtruim3d.nl. Daarmee kan vrijwel alles in de cloud; de thuisbot-route is niet nodig.
- 2026-11-21 Vergrendelde schermstand: sturen in het assenstelsel van hoe de telefoon vastgehouden wordt (zwaartekracht, kleinste rol over 0/90/180/270). Rust meten in dat assenstelsel; rond 90° springen de schermhoeken.
- 2026-11-21 Geoportaal vs huidige ingebakken data (regio Eindhoven): 46 gedeelde idents, 0 verschillen in grenzen/klasse. Geoportaal bevat alleen NL: buitenlandse volumes (EBTRAN21/22/3, EDLV2 Niederrhein CTR, EBBL2 Kleine-Brogel CTR) moeten uit een andere bron (openAIP, alleen ter controle/buurlanden). EHDP heet daar EHDPD; TMZ D = EHAATMZD (oud EHTMZD1) → idents mappen bij de overstap.
- 2026-11-21 AIP-check via eAIP-spiegel (AIRAC 11-2026, ENR 2.1): Nieuw Milligen TMA sector D = E 1500 ft–FL065, B FL065–FL195 → app klopt (open punt Pieter 15 nov gesloten). Sector B = E 1500–FL055, D FL055–065 → klopt. Sectoren A en C1: vrij–zo + feestdagen klasse E t/m FL095 (nog niet in de app; buiten/aan de rand van de regio).
- 2026-11-21 Militaire velden (Deelen, Volkel, Gilze-Rijen) staan niet in AD 2 van de eAIP; CTR/RMZ-gegevens wel in ENR 2.1/2.2.
- 2026-11-21 Klaring van een CTR-verkeersleiding dekt een RMZ die over die CTR ligt (Deelen: CTR HO + RMZ H24, AIP ENR 2.2). Vereenvoudigd: tweezijdig contact met ATC.
- 2026-11-21 Lierterreinen: hoogte uit AIP ENR 5.5 (cirkel 250 m, 500–2000 ft); getekend als cilinder in ware grootte, waarschuwing tot top+500 ft.
- 2026-11-21 Kantelen na ▶: niet ijken op het eerste meetpunt (tik-schok) maar op het gemiddelde na 0,3 s rust t.o.v. het lopende gemiddelde; rol tot 45° = nulstand. Les: test pauze/hervat met schok en scheve houding.
- 2026-11-21 ENR 5.5 is de bron voor alle terreinen met een cirkel (lier, lierstart, model, ULV): hoogte + straal uit de AIP, één bouwscript. Malden: eerst modelvliegen (0,5 NM), dan lierstart.
- 21 nov: WARNED verloopt na 4 s zonder SEEN; ENR 5.5-terreinen kregen nooit SEEN → herhaalde meldingen (Christian). Terreinen binnen 2,6 km/onder top+700 ft nu in SEEN. Les: elke nieuwe meldingsbron moet ook SEEN bijwerken.
