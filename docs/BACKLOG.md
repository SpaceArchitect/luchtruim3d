# Backlog — de enige centrale lijst

*Opgezet 23 nov 2026. Alles wat nog moet of kan staat hier, op prioriteit. STATUS toont alleen de top 5.*
**Volgorde (Christian 25 nov):** AIRAC-wissel → bugfixes → de rest. Refinement door Claude, steeds getoetst aan de noordster.
**Regels:** één regel per punt: `[grootte S/M/L/XL] wat — bron, datum → uitwerking`. Klaar = schrappen + één regel in `docs/LOG.md` (behalve terugkerende punten: datum doorschuiven).
Nieuwe feedback (chat, app, testers) komt hier binnen; issues met label `feedback` worden hier opgenomen en gesloten.

## P0 — gaat altijd voor
- [S] **Terugkerend — nooit schrappen:** AIRAC-wissel elke 28 dagen (do). Eerstvolgende: **24 dec 2026** (AMDT 13-2026), daarna 21 jan 2027, 18 feb 2027, 18 mrt 2027. Check eerst of data/eaip en data/lvnl die dag echt zijn ververst (26 nov sloeg de cron over). Stappen: data ophalen, `build_airspace.py --check`, `aip_check.py`, footer, `mission_report.py --fly --gen 8` + missietests. Na afloop alleen de datum doorschuiven en een LOG-regel — CLAUDE.md, Christian 25 nov
- [S–M] Kapotte data-actie of live-bug — CLAUDE.md

## P1 — nu
*26 nov gefixt (zie LOG): Start = volgende missie, ballon/rivierdoel, alles aanklikbaar, zwevende ringen, vario, labels over het toestel, camera liggend.*
0. [M] **Story — vloeiend starten (prio 1, Christian 27 nov):** stand 28 nov: bisect (0/a/b/c/d = 50/2931/75/84/64 ms) → variant d (geen renderer.compile; bij laden 1×1 px echt tekenen); Christian zag toch seconden stotter → **laadscherm** (openen, naar vliegen, ▶ start; weg na vloeiende frames) op `wip/live-28nov`, test d_loading + d_start_smooth. Rest: Christian bevestigt op de A55 na live.
1. [S] Kantelen kalibreert opnieuw na een melding in een bocht — **fix staat op `wip/tilt-26nov`** (ijken alleen bij start en na draaien; test d_tilt_notice_bend). Christian testte 26 nov: akkoord, live na de volledige suite (ook klim/daling gedekt) — Christian 25 nov
2. [M] Militaire gebieden (TRA/TSA/EHR): spike 26 nov klaar (LOG). Geen open primaire bron voor live status; NM B2B (EAUP/EUUP, AIXM) vraagt een certificaat + overeenkomst → **samen uitwerken in het weekend van 28–29 nov (Christian 26 nov)** Tot dan: uitleg volgens ENR 5.2 en "of het nu actief is weet deze app niet" (`wip/spike-mil-26nov`, mee met de volgende live-gang); nooit "inactief" — Christian 25 nov

## P2 — daarna
- [XL] **Heel NL (reset-push, zie STATUS):** **26 nov begonnen (lokaal /home/user/l3d-nl, zie LOG): luchtruim, grens, velden, ENR 5.5, AIPINFO, TMZ-tijden, weergave.** Stand 28 nov: `wip/heelnl` (wip/opnieuw erin, tests regio-vrij), **`wip/tiles`** = heel NL + landschap per tegel (data/osm-nl in repo, laden binnen 60 km, bouwen in plakjes van 6 ms, laadscherm wacht op tegels, test d_tiles) + live-28nov. AD 2-torens gedaan (26 nov). Nog: volledige OSM-tegels (Action loopt, MISSING.json), missiepool landelijk, generator landelijk, volledige suite op wip/tiles, telefoonmeting (fps). 27 nov–4 dec voorbereiden: gemeten 26 nov: luchtruim landelijk 91 kB (26 kB gzip) → inbakken; splitsen naar `data/*.json` alleen als de pagina > 1,5 MB wordt. OSM landelijk via Action `data-osm-nl` (17 tegels, compact op branch data/osm-nl; `wip/osm-nl-26nov`) → samenvoegen + naden + grootte meten; `build_airspace.py` landelijk (bbox 3.3,50.7,7.3,53.6) + `aip_check.py` (nieuwe frequenties AIPINFO), AIP SUP 03/2022 (Lelystad/Nieuw Milligen), labels/prestaties met landelijke dichtheid, missiepool landelijk. 7–10 dec bouwen, 11–14 dec test Christian. Daarna BE/DE — Christian 22 + 25 nov
- [M] Herkenningspunten heel NL (Christian 26 nov): bruggen, knooppunten, vliegvelden, hoge bouwwerken, steden en dorpen landelijk. Route: QH-queries (fetch_osm 'herkenning') per tegel in data-osm-nl → compact; dezelfde regels als nu (bruggen langs de weg, d_bridges/d_landmarks), dichtheid per zoomniveau; P4-bruggen (Nelson Mandelabrug, Maasbrug Venlo) gaan hierin op — 26 nov
- [L] Procedureel landschap: glooiend terrein + bos, heide, stuifzand — Christian 22 + 25 nov. Uitwerking:
  - **Reliëf:** open hoogtedata (AHN via PDOK, CC0; of Copernicus GLO-30) via een GitHub Action naar een grof raster (±200 m, 8-bit, < 150 kB voor de regio), als vervormd grondvlak met lichte overdrijving (zelfde EXAG als het luchtruim). Eerst de plekken die je herkent: stuwwal Nijmegen/Berg en Dal, Veluwezoom/Posbank, Loonse en Drunense Duinen, Strabrechtse Heide, Kempen.
  - **Bodemsoorten:** OSM `forest.json`/`heath_sand.json` (staat al op `data/osm`) → bos donkergroen met instanced boompjes (LOD: alleen dichtbij), heide paars-bruin, stuifzand licht beige met duinribbels; gedempt, zodat de luchtruimkleuren blijven winnen.
  - **Luchtvaartkant:** met reliëf worden AGL-grenzen (bv. Malden 2300 ft AGL) en de grondafstand echt; landen/grond raken op terreinhoogte.
  - **Licht genoeg:** pagina < 2 MB, ≥ 30 fps op een middenklasse-Android; meten vóór/na met een fps-test in e2e. Eerst een proef Nijmegen–Berg en Dal–Malden, screenshot aan Christian, dan uitrollen.
- [L] UX-flow: rondleiding + "Wat is er veranderd?" na AIRAC → keuzescherm (Kaart / Missies / Verkenningsvlucht / Dagelijkse uitdaging), toestelkeuze, menu herindelen; eerst mock — Christian 21+23 nov → C (vervangt OPDRACHT-21nov blok 5)
- [S] Dagelijkse uitdaging fase 1: op `wip/dagelijks`, mee in `wip/live-28nov` (d_daily groen). Rest: live.
- [M] Feedbackkanaal route A (Worker → GitHub-issues, e-mail privé, "Vlieg je zelf?") + stappenplan Cloudflare/token voor Christian — Christian 23 nov → I
- [S–M] Vindbaarheid 'educatie' (J): blok 1 klaar op `wip/vindbaar-28nov` (head-metadata zonder spel/game, JSON-LD, over.html, robots, sitemap). **Christian keurt over.html (privacytekst 'verwerkingsverantwoordelijke') goed**, dan mee live. Rest: favicon, manifest, mailtje IT.
- [S] Cookieloze teller (opties naast elkaar, Christian kiest) + privacytekst — Christian 23 nov → F
- [S] UX-review door een losse subagent na elk zichtbaar blok — Christian 23 nov → G
- [M] AIRAC-vangnet als Action: **gebouwd 28 nov** op `wip/airac-vangnet` (airac-check.yml: Geoportaal per volume, aip_check, missies uitvliegen + generator, issue 'airac'); testrun groen. Rest: naar main bij de live-gang (workflow_run werkt alleen vanaf main).
- [S] Zweefkist: planner max ±1000 ft stijgen zonder thermiek — op `wip/dagelijks`; 27 nov `mission_report --fly`: alle 18 vaste missies gehaald, zweefmissies ≤ +1000 ft (gilze = motor). Rest: mee live — 25 nov
- [S] Vangnet: elke ident in het airspace-blok uniek (LVNL hergebruikt CTR-idents voor TMA's; fix suffix 'T' in build_airspace) — 26 nov

- [M] Heel NL missies (28 nov onderzocht): (1) **landdoel** ontbreekt: een veld ín een CTR (Eelde, klasse C) haal je nu ook door er bovenover te vliegen → missietype 'landen' (doel pas gehaald onder ±1000 ft AGL, autopilot daalt) en dan 'eelde'; (2) De Kooy CTR ligt > 18 km van Texel → misStart met langere aanloop of tussenpunt; (3) Teuge: veld in een paradropzone → planner vindt geen route; doel net buiten de PJA kiezen. (4) **CTR-openingstijden per veld landelijk** (Eelde weekend 0630–2100 UTC, De Kooy weekend 0600–1100/1400–1900 UTC, Lelystad 0600–2100 UTC; AD 2.17) controleren in AIPINFO/hrs op wip/heelnl; nu alleen eh/mil gemodelleerd.

- [S] OSM heel NL: **opgelost 28 nov** via Geofabrik + osmium (data-osm-pbf). Open: grensstrook BE/DE zonder landschap (extract = alleen NL); bij uitbreiden naar BE/DE het Geofabrik-extract van die landen toevoegen.

## P3 — koers (top 5, even zwaar) en groter werk
- [M] Generator v2: smalle gangen tussen gebieden, wind voor zweef/motor, tijdsgebonden gebieden (CTR open/dicht), RMZ-oproep als opdracht, plafond aan de moeilijkheid; leerdoel uit de werkelijk geraakte gebieden — Christian 22–25 nov (v1 staat, zie docs/MISSIES.md)
- [L] Live NOTAM/AUP uit een primaire bron. Spike 26 nov: EAD Basic ongeschikt (niet operationeel, login), LVNL NOTAM Portal = aanvragen, NM B2B = certificaat + overeenkomst (beslissing Christian, P1-2). Automatische AIRAC-check: data-acties draaien op do, maar de cron kan overslaan → vangnet-Action die op AIRAC-dag de datum van data/eaip controleert — Christian 22 + 25 nov
- [M] Ballon realistischer: traagheid, dagdeel/thermiek-uren (eerst AIP checken). Gedaan 25 nov: stijgen/dalen 500 ft/min in het hoogteplan, missie langs een CTR — OPDRACHT-21nov blok 6
- [M] "Waar ben ik?"-quiz — Christian 23 nov → E
- [S] Test GitHub Issues als backlog-werkvorm (naast dit bestand) — Christian 23 nov
- [M] RT per blok: in het infopaneel (en bij naderen in vliegmodus) wat je op de radio/transponder doet — CTR: klaring van Tower, ±2 min vooraf oproepen met route + hoogte; FMC: listening squawk, alleen uitluisteren (geverifieerd ENR 1.2, zie CLAUDE.md); RMZ/TMZ; Dutch Mil klasse D boven FL045/055 voor zweef. Later: VFR-routes in/uit CTR's als laag, BE (LFA(G)) en DE (TMZ mit Hörbereitschaft). Achtergrond: KNVvL-syllabus VFR RT v5.2 (projectbestand, © KNVvL: niet in de repo, niet citeren); waarden altijd uit de AIP — Christian 26 nov

## P4 — open ideeën (niet gepland)
- LVNL-obstakellaag (masten, windmolens) · hoog contrast in de 3D-scène · IFR-naderingsgebieden (VAC) · doorsnede A→B · legenda/afkortingen · grensstrook DE (eerst labels, DFS-AIP)
- Highscorelijst met bijnaam (alleen na akkoord Christian + privacycheck) → D
- Anonieme terugkeer-gebeurtenissen (pas na juridische check) → F
- IGC-import als lokale tool voor alleen Christian (niet op de site) → E

## Nog te verifiëren (AIP) — zie CLAUDE.md "Vastgelegde kennis"
- TRA/TSA-activering: planner en missies rekenen ze als altijd actief; echte status via Eurocontrol AUP/UUP (zie NOTAM-punt P3)
- Malden: model- en zweefvliegen nooit tegelijk (Christian, lokale afspraak; ENR 5.5 zegt niets) · Nistelrode: zweef + lier op één terrein, gelijktijdigheid onbekend
- Niederrhein TMZ squawk/frequentie (DFS-AIP). *(CTR buiten openingstijden en eerste oproep Tower: geverifieerd 28 nov, zie CLAUDE.md)*

## Open vragen aan Christian
- Vught 's avonds onzichtbaar: niet te reproduceren (EHP29 is H24 en in de app altijd actief). Zie je het nog, stuur dan een screenshot met tijd en modus.
- Verduidelijkingsmails feedback: per stuk goedkeuren of vaste standaardvraag? → I

## Besloten (23 nov)
- Ballon: W/↑ = branden (omhoog), S/↓ = dalen; uitleg per toestel in de sneltoetskaart.
- Verkenningsvlucht: standaard **met** luchtruim; laatste keuze onthouden (localStorage).
- Na de vaste missies: oneindige generator (staat sinds 25 nov; docs/MISSIES.md).

## Niet doen (besluit Christian)
- Voorbeeldcircuit en circuits per zweefveld · thermiek/zweven · MSFS-export · accounts met inloggen · cookiemelding · "spel"/"game" in metadata · IGC op de openbare site · AR-bril (apart project)
