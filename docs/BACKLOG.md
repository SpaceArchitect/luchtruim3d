# Backlog — de enige centrale lijst

*Opgezet 23 nov 2026. Alles wat nog moet of kan staat hier, op prioriteit. STATUS toont alleen de top 5.*
**Volgorde (Christian 25 nov):** AIRAC-wissel → bugfixes → de rest. Refinement door Claude, steeds getoetst aan de noordster.
**Regels:** één regel per punt: `[grootte S/M/L/XL] wat — bron, datum → uitwerking`. Klaar = schrappen + één regel in `docs/LOG.md` (behalve terugkerende punten: datum doorschuiven).
Nieuwe feedback (chat, app, testers) komt hier binnen; issues met label `feedback` worden hier opgenomen en gesloten.

## P0 — gaat altijd voor
- [S] **Terugkerend — nooit schrappen:** AIRAC-wissel elke 28 dagen (do). Eerstvolgende: **24 dec 2026** (AMDT 13-2026), daarna 21 jan 2027, 18 feb 2027, 18 mrt 2027. Check eerst of data/eaip en data/lvnl die dag echt zijn ververst (26 nov sloeg de cron over). Stappen: data ophalen, `build_airspace.py --check`, `aip_check.py`, footer, `mission_report.py --fly --gen 8` + missietests. Na afloop alleen de datum doorschuiven en een LOG-regel — CLAUDE.md, Christian 25 nov
- [S–M] Kapotte data-actie of live-bug — CLAUDE.md

## P1 — nu
*26 nov gefixt (zie LOG): Start = volgende missie, ballon/rivierdoel, alles aanklikbaar, zwevende ringen, vario, labels over het toestel, camera liggend. **Live sinds 28 nov.***
0a. [S–M] **Bug (Christian 28 nov, live, motor 'lichtstad'/Evoluon):** klaring De Peel geweigerd → geen tijd om om te keren → steeds per ongeluk de CTR in. Oorzaak (vermoeden): waarschuwing ±8 s schermtijd vooraf = bij ×1 maar ±0,4 km voor de motor (< draaicirkel); test d_missions_flown 'refuse' zet na een weigering de klok een minuut vooruit i.p.v. te controleren dat je met de knoppen buiten kunt blijven. Fix: waarschuwing minstens een draaicirkel + marge vooraf (alle tempo's); na weigering dichtbij: instructeur draait weg. Vangnet: na een weigering met alleen de stuurknoppen buiten blijven, alle CTR-missies, ×1 en ×10. Na de stotter, vóór elke story (Christian).
0b. [S] **Bug (Christian 28 nov, live):** tik op een luchtruim in de vliegmodus (bv. TSA Wamel, TMA) → infovak leeg (alleen ✕), als je eerst naar de kaart ging en dan weer vliegt; direct vliegen werkt wel. Vangnet: kaart → vliegen → tik op elk soort luchtruim → info niet leeg (4 vormen).
0. [M] **Story — vloeiend starten (prio 1, Christian 27 nov):** stand 28 nov: bisect (0/a/b/c/d = 50/2931/75/84/64 ms) → variant d (geen renderer.compile; bij laden 1×1 px echt tekenen); Christian zag toch seconden stotter → **laadscherm** (openen, naar vliegen, ▶ start; weg na vloeiende frames) op `wip/live-28nov`, test d_loading + d_start_smooth. Rest: Christian bevestigt op de A55 na live.
0c. [S–M] **Minibug (Christian 28 nov, lage prio):** ballonmissie 'Drijf naar Lent': doel alleen haalbaar op ±200 ft boven bebouwing. Onrealistisch: SERA.5005(f) minimaal 1000 ft boven het hoogste obstakel binnen 600 m boven bebouwde kom (nog te verifiëren in de Nederlandse uitwerking/ontheffingen voor ballonlanding). Fix: ballondoel + windcheck rekenen met een minimumhoogte boven bebouwing (doel buiten de bebouwde kom of haalbaar op ≥ 1000 ft); app waarschuwt bij lager boven bebouwing. Vangnet: elke ballonmissie (vast + generator) uitvliegen zonder < 1000 ft AGL boven URBAN.
1. **Story — live status militaire gebieden (TRA/TSA/EHR, evt. PJA)** — refinement Christian + Claude 28 nov (LOG). Christian wil een live status, met disclaimer 'de vlieger blijft zelf verantwoordelijk voor NOTAMs en AUP/UUP'. Nooit "inactief" (Christian 25 nov). NM B2B geparkeerd (certificaat + overeenkomst, bedoeld voor operationele partijen).
   - 1a. [S] Spike 2 — publieke NOP (Eurocontrol Public Portal, portlet European AUP/UUP; ook Flyk/AIS Finland haalt AUP/UUP daar automatisch): bereikbaar vanuit een Action? Staan de EH-TRA's/TSA's/EHR's (en PJA's, i.v.m. Eelde/Teuge) in de EAUP? Formaat + koppeling AUP-naam → onze idents? Wat zeggen de gebruiksvoorwaarden over automatisch ophalen/tonen? → go/no-go in LOG. **Mail aan nop.office@eurocontrol.int** (toestemming + voorkeursroute) door Christian verstuurd op 28 nov ±16:15; antwoord afwachten (zijn Gmail), 1c pas na antwoord/voorwaarden ok. **Stand 28 nov 17:30 (probe in Actions, data/probe):** portal bereikbaar vanuit Actions; de portlet toont de lijst EAUP/EUUP-publicaties (geldig 06–06 UTC), data via GWT-RPC (`gwt/MainPages/eaup`, intern formaat, geen open API → breekbaar). Volgende stap: de publicatie openen en kijken of EH-gebieden met tijden erin staan (extra probe), pas na antwoord NOP Office.
   - 1b. [M] Alleen bij go: Action `data-aup` → `data/aup` (EAUP dagelijks na ±16 UTC, EUUP's daarna, hooguit 1×/uur, alleen EH). Test: elke AUP-naam gekoppeld aan een volume.
   - 1c. [M] Alleen bij go én toestemming/voorwaarden ok: app toont alleen positieve info met bron en tijd ("Gepland actief 09–15 UTC · EAUP 28-11 16:02 UTC") + disclaimer; niet in de AUP of data > 24 u oud → huidige tekst "of het nu actief is weet deze app niet". Planner/missies blijven TRA's als altijd actief rekenen. Vangnetten: nooit-inactief, verouderde data, 4 vormen.
   - 1d. [S] Altijd: les "Hoe weet je of een TRA actief is?" aanvullen: AUP/UUP vooraf, NOTAM, in de lucht Dutch MIL Info 132.350.

## P2 — daarna
- [XL] **Heel NL (reset-push, zie STATUS):** **26 nov begonnen (lokaal /home/user/l3d-nl, zie LOG): luchtruim, grens, velden, ENR 5.5, AIPINFO, TMZ-tijden, weergave.** Stand 28 nov: `wip/heelnl` (wip/opnieuw erin, tests regio-vrij), **`wip/tiles`** = heel NL + landschap per tegel (data/osm-nl in repo, laden binnen 60 km, bouwen in plakjes van 6 ms, laadscherm wacht op tegels, test d_tiles) + live-28nov. AD 2-torens gedaan (26 nov). Nog: volledige OSM-tegels (Action loopt, MISSING.json), missiepool landelijk, generator landelijk, volledige suite op wip/tiles, telefoonmeting (fps). 27 nov–4 dec voorbereiden: gemeten 26 nov: luchtruim landelijk 91 kB (26 kB gzip) → inbakken; splitsen naar `data/*.json` alleen als de pagina > 1,5 MB wordt. OSM landelijk via Action `data-osm-nl` (17 tegels, compact op branch data/osm-nl; `wip/osm-nl-26nov`) → samenvoegen + naden + grootte meten; `build_airspace.py` landelijk (bbox 3.3,50.7,7.3,53.6) + `aip_check.py` (nieuwe frequenties AIPINFO), AIP SUP 03/2022 (Lelystad/Nieuw Milligen), labels/prestaties met landelijke dichtheid, missiepool landelijk. 7–10 dec bouwen, 11–14 dec test Christian. Daarna BE/DE — Christian 22 + 25 nov
- [M] Herkenningspunten heel NL (Christian 26 nov): bruggen, knooppunten, vliegvelden, hoge bouwwerken, steden en dorpen landelijk. Route: QH-queries (fetch_osm 'herkenning') per tegel in data-osm-nl → compact; dezelfde regels als nu (bruggen langs de weg, d_bridges/d_landmarks), dichtheid per zoomniveau; P4-bruggen (Nelson Mandelabrug, Maasbrug Venlo) gaan hierin op — 26 nov
- [L] Procedureel landschap: glooiend terrein + bos, heide, stuifzand — Christian 22 + 25 nov. Uitwerking:
  - **Reliëf:** open hoogtedata (AHN via PDOK, CC0; of Copernicus GLO-30) via een GitHub Action naar een grof raster (±200 m, 8-bit, < 150 kB voor de regio), als vervormd grondvlak met lichte overdrijving (zelfde EXAG als het luchtruim). Eerst de plekken die je herkent: stuwwal Nijmegen/Berg en Dal, Veluwezoom/Posbank, Loonse en Drunense Duinen, Strabrechtse Heide, Kempen.
  - **Bodemsoorten:** OSM `forest.json`/`heath_sand.json` (staat al op `data/osm`) → bos donkergroen met instanced boompjes (LOD: alleen dichtbij), heide paars-bruin, stuifzand licht beige met duinribbels; gedempt, zodat de luchtruimkleuren blijven winnen.
  - **Luchtvaartkant:** met reliëf worden AGL-grenzen (bv. Malden 2300 ft AGL) en de grondafstand echt; landen/grond raken op terreinhoogte.
  - **Licht genoeg:** pagina < 2 MB, ≥ 30 fps op een middenklasse-Android; meten vóór/na met een fps-test in e2e. Eerst een proef Nijmegen–Berg en Dal–Malden, screenshot aan Christian, dan uitrollen.
- **Story — UX-flow** (Christian 21+23 nov, OPDRACHT-23nov §C; refinement Claude 28 nov). Noordster: een nieuwe bezoeker weet binnen 1 min wat hij hier kan en zit binnen 2 tikken in de kaart of de lucht. Nu bestaan er geen keuzescherm, verkenningsvlucht-ingang en "Wat is er veranderd?" (alleen rondleiding).
  - U1. [S] Mock: 3 schermen (startrondleiding, keuzescherm, toestelkeuze) statisch op `wip/ux-mock`, screenshots desk + p7 naar Christian, **gebundeld met andere vragen**. Daarna pas U2–U4.
  - U2. [M] Keuzescherm met 4 tegels: Kaart verkennen · Missies (→ toestel zweef/motor/ballon) · Verkenningsvlucht (met/zonder luchtruim, keuze onthouden → toestel) · Dagelijkse uitdaging. Terugkerende bezoeker komt hier direct; menu: "Terug naar start" + rondleidingen; menu herindelen = alleen wat niet op het keuzescherm staat. Klaar: elke tegel ≤ 2 tikken tot kaart/vliegen; laadscherm 'Missie klaarzetten…' blijft het enige laadmoment. Vangnet: d_chooser (elke tegel → juiste modus + toestel), 4 vormen, d_smooth_flight groen.
  - U3. [S] Startrondleiding ±1 min in kaartmodus, "Sla over" altijd zichtbaar, daarna keuzescherm; gezien = localStorage (`l3d_tour`). Vangnet: nieuw → rondleiding, terugkerend → keuzescherm.
  - U4. [M] "Wat is er veranderd?": `build_airspace.py` schrijft per AIRAC een lijst gewijzigde gebieden (nieuw/weg/grens/hoogte/tijden) t.o.v. de vorige; bij het eerste bezoek na een nieuwe AIRAC vliegt de camera langs elk gebied met één zin; laatst geziene AIRAC in localStorage; geen wijzigingen → overslaan. Wordt een stap in de P0-AIRAC-wissel (lijst nalezen). Vangnet: test met een nep-diff (1 gebied verplaatst) + lege diff.
- [M] Feedbackkanaal route A (Worker → GitHub-issues, e-mail privé, "Vlieg je zelf?") + stappenplan Cloudflare/token voor Christian — Christian 23 nov → I
- [S–M] Vindbaarheid 'educatie' (J): blok 1 klaar (review: eAIP-licentie gecorrigeerd) op `wip/vindbaar-28nov` (head-metadata zonder spel/game, JSON-LD, over.html, robots, sitemap). **Christian keurt over.html (privacytekst 'verwerkingsverantwoordelijke') goed**, dan mee live. Rest: favicon, manifest, mailtje IT.
- [S] Cookieloze teller (opties naast elkaar, Christian kiest) + privacytekst — Christian 23 nov → F
- [S] UX-review door een losse subagent na elk zichtbaar blok — Christian 23 nov → G
- [S] Vangnet: elke ident uniek per luchtruimsoort: **gebouwd** op wip/heelnl/wip/tiles (d_unique_idents, suffix 'T' in build_airspace); live met heel NL — 26 nov

- [M] Heel NL missies (28 nov onderzocht): (1) landdoel **gebouwd** (wip/tiles, missie 'lely'); Eelde valt af zolang PJA's altijd verboden zijn (veld in PJA Winde) → eerst 'PJA actief/niet actief' modelleren (AUP/NOTAM, P3); (2) De Kooy CTR ligt > 18 km van Texel → misStart met langere aanloop of tussenpunt; (3) Teuge: veld in een paradropzone → planner vindt geen route; doel net buiten de PJA kiezen. (4) CTR/RMZ-openingstijden landelijk: **gebouwd op wip/tiles** (uit de AIP-tekst, d_ctr_hours). Rest: steekproef Eelde/De Kooy/Lelystad tegen AD 2.17 bij de heel NL-suite.

- **Story — "Waar ben ik?"-quiz** (Christian 23 nov, OPDRACHT-23nov §E; refinement Claude 28 nov; van P3 naar P2: dit ís de noordster, begrip toetsen zonder vliegvaardigheid).
  - Q1. [M] Ronde van 10: je hangt stil op een plek en hoogte (uit de missiepool, landelijk na heel NL), luchtruim verborgen, alleen terrein + herkenningspunten. Eén meerkeuzevraag (3–4 opties): *in welk luchtruim zit je?* / *klaring nodig?* / *hoe hoog mag je hier zonder klaring?* Na het antwoord faden de volumes in en verschijnt de sonde-uitleg ('Wat doe je'). Antwoorden komen uit dezelfde sonde-functie als de app (geen tweede waarheid). Score lokaal. Ingang: menu, later tegel op het keuzescherm (U2). Vangnet: d_quiz (elk goed antwoord = sonde-uitkomst; 10 vragen zonder dubbele plek), 4 vormen.
  - Q2. [S] Oplopend: ronde 1 CTR/P/R, daarna TMA-trappen en klasse, dan TRA/TSA, RMZ/TMZ, PJA; afleiders uit naburige gebieden.

- [S] OSM heel NL: **opgelost 28 nov** via Geofabrik + osmium (data-osm-pbf). Open: grensstrook BE/DE zonder landschap (extract = alleen NL); bij uitbreiden naar BE/DE het Geofabrik-extract van die landen toevoegen.

- **Story — beloning en hangaar** (ideeën Raquel via Christian 28 nov; **besluit Christian 28 nov: plezier mag**, het houdt mensen oefenen; refinement Claude 28 nov). Grens: beloningen alleen voor goed luchtruimgedrag, nooit voor vliegkunst; geen accounts, alles in localStorage (functioneel, zonder ID's).
  - R1. [S] 5 sterren i.p.v. 3: ⭐ gehaald · ⭐ zonder overtreding · ⭐ strakke route (zoals nu) · ⭐ alle verplichte meldingen/klaringen gedaan (RT per blok) · ⭐ nergens binnen 200 ft van een grens (marge). Oude scores (`l3d_sterren`, max 3) blijven geldig. Vangnet: d_stars (elke ster apart te halen en te missen), mission_report: 5 sterren haalbaar per vaste missie.
  - R2. [M] Hoedjes: elke behaalde missie levert een goofy hoedje op (sombrero, cowboyhoed, pet, kroon, pylon, verjaardagshoedje…), op het toestel gestapeld tot een **hoedentoren** zoals in ARAM (Christian 28 nov). Lowpoly, procedureel in three.js (geen externe assets/licenties), samengevoegd tot één mesh, max ±30 zichtbaar. Alleen in de buitencamera; de vrije zone voor labels groeit mee. Uitzetten in de hangaar. Vangnet: d_smooth_flight met 30 hoedjes, 4 vormen.
  - R3. [M] Hangaar (vanuit toestelkeuze/keuzescherm): toestel + livery kiezen (3–4 kleurstellingen per toestel, geen nieuwe modellen, vlieggedrag identiek), livery's vrijspelen met sterren, hoedjes aan/uit. Na U2.
  - R4. [S] Voortgangscode: missies, sterren, dag, hoedjes, livery als korte tekstcode (+ controlegetal) om te kopiëren; plakken op een ander apparaat = overzetten. QR alleen als het zonder externe bibliotheek kan. Geen server. Vangnet: export → wissen → import = zelfde stand; foute code → nette melding.

- [M] **Bugregister:** script dat elke bug-regel in LOG koppelt aan een test in de suite. Eerst kantelen en knipperende lijnen (Christian: komen terug).
- [M] **Vaste missies heel NL** (Christian 28 nov: nu vooral Zuid-Nederland): per regio missies met één leerdoel; generator werkt op wip/tiles al landelijk.

## P3 — koers (top 5, even zwaar) en groter werk
- [M] **Transition level op basis van het actuele weer** (idee Christian 28 nov). AIP ENR 1.7 (AIRAC 12-2026): transition altitude **3000 ft IFR / 3500 ft VFR** in de hele Amsterdam FIR; transition level op of boven 4000 ft AMSL, elk uur vastgesteld. Nog te verifiëren: de regel/tabel QNH → TL (ENR 1.7) en een primaire, loginvrije bron voor QNH (METAR via een Action). In de app: boven TA hoogte als FL tonen, uitleg 'boven 3500 ft: standaard 1013 hPa', TL in de HUD; bij twijfel 'vereenvoudigd'.
- **Story — generator v2** (Christian 22–25 nov; v1 staat, zie docs/MISSIES.md; opgesplitst door Claude 28 nov). Elke stap: generator blijft alleen missies leveren die de vlucht-check haalt, nooit generatorwerk tijdens het vliegen (d_gen_bg_idle, d_smooth_flight).
  - G1. [S] Leerdoel uit de werkelijk geraakte gebieden (sonde langs de geplande route) i.p.v. het doelgebied + plafond aan de moeilijkheid (max. aantal conflicten per niveau). Eerst, want G2–G5 leunen erop.
  - G2. [M] Smalle gangen: keerpunt of route door een gang < 3 km tussen twee gebieden (bv. tussen CTR en TMA-trap). Vangnet: elke gang-missie heeft een route met ≥ 300 m marge.
  - G3. [S] RMZ/TMZ-oproep als opdracht: missie door een RMZ, ster alleen met de melding (koppelt aan R1).
  - G4. [M] Tijdsgebonden: CTR open/dicht met missietijd (na heel NL live; openingstijden staan op wip/tiles, regel 'buiten openingstijden' in CLAUDE.md). Zelfde route, ander antwoord = het leerdoel.
  - G5. [L] Wind voor zweef/motor: windvector per missie in de sim (drift), planner rekent ermee; ballon later. Pas na G1–G4.
- [L] Live NOTAM uit een primaire bron (AUP: zie P1-1). Spike 26 nov: EAD Basic ongeschikt (niet operationeel, login), LVNL NOTAM Portal = aanvragen, NM B2B = certificaat + overeenkomst (geparkeerd 28 nov). Wacht op de uitkomst van P1-1a (NOP). *(AIRAC-vangnet-Action: live 28 nov.)* — Christian 22 + 25 nov
- Ballon realistischer (OPDRACHT-21nov blok 6; gedaan 25 nov: 500 ft/min in het hoogteplan, missie langs een CTR):
  - B1. [S] Traagheid: branden/dalen werkt met ±10 s vertraging en loopt uit; hoogteplan en planner rekenen ermee. Vangnet: mission_report --fly, alle ballonmissies gehaald.
  - B2. [S] Spike: wat zeggen AIP/regelgeving over ballonvaren en dagdeel (ENR 1.2/1.4, SERA zonsopkomst/-ondergang)? Alleen opnemen wat in de bron staat → go/no-go in LOG.
- [S] Test GitHub Issues als backlog-werkvorm (naast dit bestand) — Christian 23 nov
- [M] RT per blok: sondepaneel **live 28 nov** ('Wat doe je', d_rt_advice). Rest: dezelfde tekst bij naderen in de vliegmodus (melding) — Christian/KNVvL RT-syllabus

## P4 — open ideeën (niet gepland)
- Hapering na draaien staand↔liggend (A55 ±219 ms, Christian 28 nov): **alleen oppakken als het storend wordt** (Christian). Opties: kort laadscherm of lichtere resize.
- LVNL-obstakellaag (masten, windmolens) · hoog contrast in de 3D-scène · IFR-naderingsgebieden (VAC) · doorsnede A→B · legenda/afkortingen · grensstrook DE (eerst labels, DFS-AIP)
- Highscorelijst met bijnaam (alleen na akkoord Christian + privacycheck) → D
- Anonieme terugkeer-gebeurtenissen (pas na juridische check) → F
- IGC-import als lokale tool voor alleen Christian (niet op de site) → E
- Gebruikerstest met zweefvliegers van Christians club (middag tijdens het winteronderhoud), pas als de site 'af' is: scenario's papieren kaart vs. app — Christian 28 nov

## Nog te verifiëren (AIP) — zie CLAUDE.md "Vastgelegde kennis"
- TRA/TSA-activering: planner en missies rekenen ze als altijd actief; echte status via Eurocontrol AUP/UUP (zie NOTAM-punt P3)
- Malden: model- en zweefvliegen nooit tegelijk (Christian, lokale afspraak; ENR 5.5 zegt niets) · Nistelrode: zweef + lier op één terrein, gelijktijdigheid onbekend
- Niederrhein TMZ squawk/frequentie (DFS-AIP). *(CTR buiten openingstijden en eerste oproep Tower: geverifieerd 28 nov, zie CLAUDE.md)*

## Open vragen aan Christian
- Vught 's avonds onzichtbaar: niet te reproduceren (EHP29 is H24 en in de app altijd actief). Zie je het nog, stuur dan een screenshot met tijd en modus.
- Verduidelijkingsmails feedback: per stuk goedkeuren of vaste standaardvraag? → I
- "Test GitHub Issues als backlog-werkvorm" (P3, 23 nov): nog nodig nu BACKLOG.md de enige lijst is? Zo niet: schrappen.

## Besloten (23 nov)
- Ballon: W/↑ = branden (omhoog), S/↓ = dalen; uitleg per toestel in de sneltoetskaart.
- Verkenningsvlucht: standaard **met** luchtruim; laatste keuze onthouden (localStorage).
- Na de vaste missies: oneindige generator (staat sinds 25 nov; docs/MISSIES.md).

## Niet doen (besluit Christian)
- 'Les van de week' uit de AIP voor Christian — Christian 28 nov: flutidee.
- Betaalde device-testdienst (BrowserStack e.d.) — Christian 28 nov: geen abonnement; liever schone code. Vervanging: structurele klasse-tests (d_smooth_flight, bugregister) + meetlat ?fps=1 bij twijfel.
- Voorbeeldcircuit en circuits per zweefveld · thermiek/zweven · MSFS-export · accounts met inloggen · cookiemelding · "spel"/"game" in metadata · IGC op de openbare site · AR-bril (apart project)
