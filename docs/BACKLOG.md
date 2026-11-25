# Backlog — de enige centrale lijst

*Opgezet 23 nov 2026. Alles wat nog moet of kan staat hier, op prioriteit. STATUS toont alleen de top 5.*
**Volgorde (Christian 25 nov):** AIRAC-wissel → bugfixes → de rest. Refinement door Claude, steeds getoetst aan de noordster.
**Regels:** één regel per punt: `[grootte S/M/L/XL] wat — bron, datum → uitwerking`. Klaar = schrappen + één regel in `docs/LOG.md` (behalve terugkerende punten: datum doorschuiven).
Nieuwe feedback (chat, app, testers) komt hier binnen; issues met label `feedback` worden hier opgenomen en gesloten.

## P0 — gaat altijd voor
- [S] **Terugkerend — nooit schrappen:** AIRAC-wissel elke 28 dagen (do). Eerstvolgende: **26 nov 2026** (AMDT 12-2026), daarna 24 dec 2026, 21 jan 2027, 18 feb 2027. Stappen: data ophalen, `build_airspace.py --check`, `aip_check.py`, footer, `mission_report.py --fly --gen 8` + missietests. Na afloop alleen de datum doorschuiven en een LOG-regel — CLAUDE.md, Christian 25 nov
- [S–M] Kapotte data-actie of live-bug — CLAUDE.md

## P1 — nu (live-feedback Christian 25 nov, in deze volgorde)
1. [S] Bug: ▶ Start na een afgeronde missie moet direct de volgende missie starten (Start = doorgaan met de huidige missie, of na geslaagd/mislukt de volgende). Nu vlieg je verder zonder opdracht — Christian 25 nov
2. [S] Live-bug: ballon geland aan de Maas (5 km ZO van Dreumel, wo 11:03) maar opdracht 'Drijf naar de Maas' niet geslaagd; doelbaken zegt nog 1,4 km. Vermoeden: doel = één OSM-stuk van de rivier (`LASTGOAL.pts=f.pts`, regel ±2059) i.p.v. de hele Maas (OSM knipt rivieren op, net als bij de bruggen), en/of REACH 0,5 km bij een lijn te krap. Test: elke rivier-/wegopdracht halen op een willekeurig punt langs de héle rivier — Christian 25 nov (screenshot in chat)
3. [M] Elk luchtruim aanklikbaar voor info, ook ENR 5.5-terreinen (lier, zweef, model, ULV), paradropzones e.d. Nu raakt de klik alleen `airGroup` (regel ±1499: `ray.intersectObjects(airGroup…)`), niet `hgCyl`. Mobiel: alleen de highlights (naam · grenzen · wat moet je doen · frequentie), details achter "meer" — Christian 25 nov
4. [S] Bug: grondring van ENR 5.5-terreinen zweeft boven de grond: ring op y = 0,05 (50 m) terwijl de cilinder op 0 begint en de grond nog lager ligt → ring en cilindervoet op dezelfde grondhoogte; test: ringhoogte = cilindervoet — Christian 25 nov (screenshot)
5. [S] Bug: vario toont altijd de vaste stijgsnelheid (bv. 400 ft/min); moet de werkelijke stijg-/daalsnelheid van het toestel tonen (afhankelijk van hoe hard het stijgt) — Christian 25 nov
6. [S–M] Bug (sensor → Christian test vóór live): tilt kalibreert opnieuw als er een melding komt terwijl je in een bocht hangt; de bocht is daarna niet voort te zetten. Kalibreren alleen bij de start en na draaien staand↔liggend, zonder knop of vraag: hooguit een korte melding "Aan het kalibreren… Houd de telefoon stil." (Christian: gebruiker hoeft niets aan te klikken). Nooit herkalibreren door een melding, resize of pauze. Vermoeden: melding → resize/re-init → kalibratie. Test: met ±5° ruis een bocht vliegen, midden in de bocht een melding (en een resize) forceren → nulstand ongewijzigd — Christian 25 nov
7. [S] Bug mobiel: labels bedekken het eigen toestel (vliegmodus). Vrije zone rond de schermpositie van het toestel waarin labels wegvallen/vervagen; test: alle schermvormen, over meerdere frames, geen label-rect overlapt het toestel — Christian 25 nov (screenshot, Pixel liggend)
8. [S] Bug mobiel liggend: chase-camera te ver weg, toestel nauwelijks zichtbaar. Camera-afstand laten afhangen van schermhoogte/beeldverhouding; test: toestelgrootte in px liggend ≈ staand (±25%) — Christian 25 nov
9. [M] Militaire gebieden (TRA/TSA/EHR): gebruiker weet niet wat hij moet doen. Eerst begrip: bij aanraken/naderen uitleggen wat het gebied is, dat het actief kán zijn en hoe je dat checkt (NOTAM, Eurocontrol AUP/UUP) met link. Daarna echte activering tonen via het P3-punt Live NOTAM (primaire bron, met tijdstempel en "alleen educatie") — Christian 25 nov

## P2 — daarna
- [XL] **Heel NL (reset-push, zie STATUS):** 27 nov–4 dec voorbereiden: data uit `index.html` naar `data/*.json` (laden + cache, pagina < 2 MB), `build_airspace.py` landelijk (bbox NL) + `aip_check.py`, AIP SUP 03/2022 (Lelystad/Nieuw Milligen), labels/prestaties met landelijke dichtheid, missiepool landelijk. 7–10 dec bouwen, 11–14 dec test Christian. Daarna BE/DE — Christian 22 + 25 nov
- [L] Procedureel landschap: glooiend terrein + bos, heide, stuifzand — Christian 22 + 25 nov. Uitwerking:
  - **Reliëf:** open hoogtedata (AHN via PDOK, CC0; of Copernicus GLO-30) via een GitHub Action naar een grof raster (±200 m, 8-bit, < 150 kB voor de regio), als vervormd grondvlak met lichte overdrijving (zelfde EXAG als het luchtruim). Eerst de plekken die je herkent: stuwwal Nijmegen/Berg en Dal, Veluwezoom/Posbank, Loonse en Drunense Duinen, Strabrechtse Heide, Kempen.
  - **Bodemsoorten:** OSM `forest.json`/`heath_sand.json` (staat al op `data/osm`) → bos donkergroen met instanced boompjes (LOD: alleen dichtbij), heide paars-bruin, stuifzand licht beige met duinribbels; gedempt, zodat de luchtruimkleuren blijven winnen.
  - **Luchtvaartkant:** met reliëf worden AGL-grenzen (bv. Malden 2300 ft AGL) en de grondafstand echt; landen/grond raken op terreinhoogte.
  - **Licht genoeg:** pagina < 2 MB, ≥ 30 fps op een middenklasse-Android; meten vóór/na met een fps-test in e2e. Eerst een proef Nijmegen–Berg en Dal–Malden, screenshot aan Christian, dan uitrollen.
- [L] UX-flow: rondleiding + "Wat is er veranderd?" na AIRAC → keuzescherm (Kaart / Missies / Verkenningsvlucht / Dagelijkse uitdaging), toestelkeuze, menu herindelen; eerst mock — Christian 21+23 nov → C (vervangt OPDRACHT-21nov blok 5)
- [S–M] Dagelijkse uitdaging fase 1: `genMission` met datum-seed (generator + vlucht-check bestaan al), lokale score/streak, deeltekst — Christian 23 nov → D
- [M] Feedbackkanaal route A (Worker → GitHub-issues, e-mail privé, "Vlieg je zelf?") + stappenplan Cloudflare/token voor Christian — Christian 23 nov → I
- [S–M] Vindbaarheid/categorisering "educatie": favicon (2–3 varianten), metadata zonder spel/game, `over.html`, robots/sitemap/JSON-LD, auteur Christian Niemeijer, mailtje voor IT, leverancierslijst — Christian 23 nov → J (klein blok per sessie)
- [S] Cookieloze teller (opties naast elkaar, Christian kiest) + privacytekst — Christian 23 nov → F
- [S] UX-review door een losse subagent na elk zichtbaar blok — Christian 23 nov → G
- [M] AIRAC-vangnet als GitHub Action: na `data-eaip`/`data-lvnl` automatisch `build_airspace.py --check` op een kopie + `e2e.py -k "missies echt uitvliegen|missiegenerator"`; bij falen een issue met welke missie/poot — Christian 25 nov (zie docs/MISSIES.md)
- [S] Zweefkist: planner max ±1000 ft stijgen zonder thermiek (nu klimt hij 1000 → 3500 ft over Volkel) — 25 nov

## P3 — koers (top 5, even zwaar) en groter werk
- [M] Generator v2: smalle gangen tussen gebieden, wind voor zweef/motor, tijdsgebonden gebieden (CTR open/dicht), RMZ-oproep als opdracht, plafond aan de moeilijkheid; leerdoel uit de werkelijk geraakte gebieden — Christian 22–25 nov (v1 staat, zie docs/MISSIES.md)
- [L] Live NOTAM uit een primaire bron (LVNL → Eurocontrol NOP → EAD Basic); automatische AIRAC-check. Eerste toepassing: TRA/TSA/EHR-activering (AUP/UUP) zichtbaar bij de militaire gebieden (zie P1-9) — Christian 22 + 25 nov
- [M] Ballon realistischer: traagheid, dagdeel/thermiek-uren (eerst AIP checken). Gedaan 25 nov: stijgen/dalen 500 ft/min in het hoogteplan, missie langs een CTR — OPDRACHT-21nov blok 6
- [M] "Waar ben ik?"-quiz — Christian 23 nov → E
- [S] Test GitHub Issues als backlog-werkvorm (naast dit bestand) — Christian 23 nov

## P4 — open ideeën (niet gepland)
- Nelson Mandelabrug Arnhem en Maasbrug Venlo als herkenningspunt (ontbreken in data/osm herkenning; query uitbreiden)
- LVNL-obstakellaag (masten, windmolens) · hoog contrast in de 3D-scène · IFR-naderingsgebieden (VAC) · doorsnede A→B · legenda/afkortingen · grensstrook DE (eerst labels, DFS-AIP)
- Highscorelijst met bijnaam (alleen na akkoord Christian + privacycheck) → D
- Anonieme terugkeer-gebeurtenissen (pas na juridische check) → F
- IGC-import als lokale tool voor alleen Christian (niet op de site) → E

## Nog te verifiëren (AIP) — zie CLAUDE.md "Vastgelegde kennis"
- TRA/TSA-activering: planner en missies rekenen ze als altijd actief; echte status via Eurocontrol AUP/UUP (zie NOTAM-punt P3)
- Malden: model- en zweefvliegen nooit tegelijk (Christian, lokale afspraak; ENR 5.5 zegt niets) · Nistelrode: zweef + lier op één terrein, gelijktijdigheid onbekend
- Status/klasse van een CTR buiten de openingstijden · Niederrhein TMZ squawk/frequentie (DFS-AIP) · eerste oproep Arrival of Tower

## Open vragen aan Christian
- Vught 's avonds onzichtbaar: niet te reproduceren (EHP29 is H24 en in de app altijd actief). Zie je het nog, stuur dan een screenshot met tijd en modus.
- Verduidelijkingsmails feedback: per stuk goedkeuren of vaste standaardvraag? → I

## Besloten (23 nov)
- Ballon: W/↑ = branden (omhoog), S/↓ = dalen; uitleg per toestel in de sneltoetskaart.
- Verkenningsvlucht: standaard **met** luchtruim; laatste keuze onthouden (localStorage).
- Na de vaste missies: oneindige generator (staat sinds 25 nov; docs/MISSIES.md).

## Niet doen (besluit Christian)
- Voorbeeldcircuit en circuits per zweefveld · thermiek/zweven · MSFS-export · accounts met inloggen · cookiemelding · "spel"/"game" in metadata · IGC op de openbare site · AR-bril (apart project)
