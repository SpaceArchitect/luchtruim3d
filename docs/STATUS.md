# Status — lees dit eerst

*Bijgewerkt: 23 nov 2026, ochtend (chat met Christian: nieuwe input, alleen docs gewijzigd). Opdracht: **`docs/OPDRACHT-23nov.md`**.*

## Live
- https://luchtruim3d.nl = `main` = `wip/live-21nov` + fixes 22 nov (live 22 nov ±20:13, volledige suite groen, Pages OK).
  Terugdraaien: `release/2026-11-22` (= live van 21 nov), daarvoor `release/2026-11-21`, `release/2026-11-15`.
- Regio: Eindhoven + Arnhem–Nijmegen tot 52.15 N, AIRAC 11-2026.
- **Afgerond (Christian 23 nov):** kantelen op mobiel werkt goed → niet meer aanpassen, alleen bij een bug. De sneltoetskaart op desktop blijft.

## Eerstvolgende sessie (di 24 nov 22:47) — in deze volgorde
0. **AIRAC-wissel 26 nov (AMDT 12-2026)** gaat voor als de data er is (zie top 5 punt 5).
1. **Vught penitentiaire inrichting** 's avonds onzichtbaar. Christian denkt 24/7, niet gecheckt → zelf uitzoeken in ENR 5.1, tijdfilter repareren of uitleg tonen waarom het er niet staat.
2. **Lieren para/scherm:** één cilinder met de AIP-maten (nu cirkel + kleinere cilinder).
3. **Malden:** overlappende cilinders zweef (groen) en model (oranje) suggereren gelijktijdig gebruik; dat gebeurt nooit (Christian) → één volume of uitleg "gedeeld, niet gelijktijdig"; één melding (opdracht A3).
4. **Herkenningspunten:** de A50-brug staat een kwartslag gedraaid → alle modellen op oriëntatie (as uit OSM) nalopen. Samen met `wip/herkenning-22nov` (zie Half af).
5. **Missies te makkelijk** → progressie easy → medium → lang/moeilijk met meerdere keerpunten, sterren, leerdoel (opdracht B).

## Koers (Christian 22–23 nov) — top 5
1. **Betere game-ervaring** (opdracht B–D): missieprogressie; UX-flow = rondleiding (+ "Wat is er veranderd?" na een AIRAC) → keuzescherm Kaart / Missies / Verkenningsvlucht / **Dagelijkse uitdaging** (favoriet Christian; fase 1 lokaal, geen accounts). Eerst een mock laten zien. Na elk zichtbaar blok een UX-review door een subagent.
2. **Mooi, herkenbaar landschap, procedureel en licht:** bos, heide, stuifzand, reliëf Veluwe/stuwwal. Eerste proef: Veluwezoom + **Malden als kruis in het bos**. Bos zit in `fetch_osm.py` op `wip/herkenning-22nov`.
3. **Kaart uitbreiden** naar heel NL (luchtruim landelijk via `build_airspace.py`; landschap per regio), later BE/DE. Eerst data uit `index.html` naar `data/*.json`.
4. **Missies** voor motor, zweef en ballon (ideeën: lierstart + thermiek naar Malden, ballon over de Waal, RMZ/CTR-oproepen), volgens de progressie van opdracht B.
5. **Live eAIP/AIRAC/NOTAM:** primaire NOTAM-bron (LVNL → Eurocontrol NOP → EAD Basic); FAA alleen ter vergelijking. **AIRAC 26 nov:** `git fetch origin data/lvnl data/eaip` → `python tools/build_airspace.py --bbox 4.75,51.2,6.25,52.15 --check` + `python tools/aip_check.py`, footer bijwerken.
- Daarnaast: **anonieme analytics zonder cookiemelding** (opdracht F): cookieloze teller, opties naast elkaar zetten, Christian kiest.

## Half af
- `wip/herkenning-22nov`: 6 herkenningspunten weg (akkoord Christian), test `d_landmarks` 4/4. Nog doen: Waalbrug, De Oversteek, John Frostbrug, Nelson Mandelabrug, knooppunten, Maasbrug Venlo, De Peel uit `osm/herkenning/` op `data/osm`. **Neem de oriëntatiefix (A50-brug) hierin mee.** Bevat ook bos in `fetch_osm.py` en de FAA-NOTAM-proef (niet in de app).
- **Feedbackkanaal (besloten, route A, opdracht I):** "Klopt dit niet?" / 👍👎 na een missie / menu → Cloudflare Worker → GitHub-issue; e-mail optioneel en nooit in het openbare issue. Prioriteit omhoog (nog weinig feedback van vliegers). Stappenplan voor Christians eenmalige setup voorbereiden.

## Wacht op Christian
- Niets. Geplande sessies di+vr 22:47 (±25% per sessie). Soms een extra handmatige sessie op vrijdagochtend als er tokens over zijn.

## Werkwijze-notities
- Cloud: `tools/e2e.py` valt terug op `/opt/pw-browsers/chromium`; testserver geeft 204 op `/favicon.ico`.
- `--quick` mist interacties tussen features. Vóór live altijd de volledige suite.
- Overpass/eAIP/Geoportaal alleen via GitHub Actions bereikbaar, niet direct vanuit de cloud.
