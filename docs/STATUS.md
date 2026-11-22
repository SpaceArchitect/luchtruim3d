# Status — lees dit eerst

*Bijgewerkt: 22 nov 2026, avond (cloudsessie; gestopt ruim vóór Christians grens van 80% weeklimiet).*

## Live
- https://luchtruim3d.nl = `main` = `wip/live-21nov` + fixes 22 nov (LIVE_RESULT).
  Terugdraaien: `release/2026-11-22` (= live van 21 nov), daarvoor `release/2026-11-21`, `release/2026-11-15`.
- Regio: Eindhoven + Arnhem–Nijmegen tot 52.15 N, AIRAC 11-2026.
- Nieuw 22 nov: alle 74 ENR 5.5-terreinen (lier, lierstart zweef, model, ULV) als cilinder met één melding per nadering; starts nooit naast een terrein; sonde liggend als lade; "Houd de telefoon even stil" na ▶; besturing zoals MSFS + sneltoetskaart (desktop); 13 snelwegbruggen; RMZ-oproepknop blijft zichtbaar tijdens een melding.

## Wacht op Christian
- **Telefoontest** (mobiel, https://luchtruim3d.nl): vlieg, pauzeer/▶ een paar keer (ook scheef vastgehouden) en na "Nieuwe opdracht". Klopt de koers? Zie je "Houd de telefoon even stil"?
- Verder niets: Christian doet geen handmatige acties (afspraak 22 nov). Geplande sessies di+vr 22:47 (±25% per sessie).
- (Geparkeerd: usage-meter tot de home server er is. OVH geregeld.)

## Koers (Christian 22 nov) — top 5
1. **Betere game-ervaring:** startflow/tutorial (blok 5 `docs/OPDRACHT-21nov.md`): eigen vraag vóór de iOS-bewegingsvraag (Raquel), korte uitleg kantelen + staand/liggend; standaardtempo (×10/×20?) uitzoeken; wat na de laatste missie.
2. **Mooi, herkenbaar landschap, procedureel en licht:** bos (instanced boomtoefjes → tapijt van ver), heide (paarsbruin + plukjes), stuifzand/duinen (reliëf zoals Loonse en Drunense Duinen), licht reliëf Veluwe/stuwwal Nijmegen. Eerste proef: Arnhem/Veluwezoom + **Malden als kruis in het bos**. Bos zit nog niet in `fetch_osm.py` (toevoegen: `landuse=forest`, `natural=wood`). Veluwe-heide/zand staat ruw op `data/osm`, nog niet omgezet.
3. **Kaart uitbreiden** naar heel NL (luchtruim landelijk in één keer via `build_airspace.py`; landschap per regio), later stukken BE/DE. Eerst data uit `index.html` naar `data/*.json`.
4. **Missies** voor motor, zweef en ballon (nu o.a. Terlet, Over de Rijn). Ideeën: lierstart + thermiek naar Malden, ballon over de Waal met wind, RMZ/CTR-oproepen.
5. **Live eAIP/AIRAC/NOTAM:** pijplijn `data/lvnl` + `data/eaip` draait wekelijks; volgende stap: NOTAM-bron vinden en automatische AIRAC-check. **AIRAC-wissel 26 nov (AMDT 12-2026):** `git fetch origin data/lvnl data/eaip` → `python tools/build_airspace.py --bbox 4.75,51.2,6.25,52.15 --check` + `python tools/aip_check.py`, footer bijwerken.

## Half af
- `wip/herkenning-22nov`: 6 herkenningspunten weg (akkoord Christian; Eindhoven-centrum 7→2, Sluis Heumen), test `d_landmarks` groen 4/4. OSM-actie haalt bruggen/knooppunten/vliegvelden voor de hele regio op (`osm/herkenning/` op `data/osm`). Nog doen: Waalbrug, De Oversteek, John Frostbrug, Nelson Mandelabrug, knooppunten, Maasbrug Venlo, De Peel toevoegen uit die data; dan `--quick` en mee met de volgende live-gang.

- `wip/herkenning-22nov` bevat ook: bos in `fetch_osm.py` en de **NOTAM-proef** (`tools/fetch_notam.py` → `data/notam`). Controleer de eerste runs (data-osm, data-notam); bridges-query faalde 22 nov door volle Overpass.
- **Feedbackkanaal testers (open):** zonder handwerk van Christian. Idee: ⚙ → "Feedback" in de app die een vooraf ingevulde GitHub-issue opent (testers met account) — zoek een route zonder account én zonder server/secret.

## Werkwijze-notities
- Cloud: `tools/e2e.py` valt terug op `/opt/pw-browsers/chromium`; testserver geeft 204 op `/favicon.ico`.
- `--quick` mist interacties tussen features (22 nov: terreinmelding verdrong RMZ-knop). Vóór live altijd de volledige suite.
- Overpass/eAIP/Geoportaal alleen via GitHub Actions bereikbaar, niet direct vanuit de cloud.
