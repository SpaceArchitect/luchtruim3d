# Status — lees dit eerst

*Bijgewerkt: 21 nov 2026, ±11:30 (cloudsessie).*

## Live
- https://luchtruim3d.nl = `main` = wip/arnhem + gevaren + fixes 21 nov (volledige suite: 28 smoke + 155/156 det + 8 fuzz; de ene misser gefixt en opnieuw getest: kantel 24/24, smoke 14/14).
  Vorige live: `release/2026-11-21` (170a615-inhoud), daarvoor `release/2026-11-15`.
- Regio: Eindhoven + noordrand Arnhem–Nijmegen (tot 52.15 N), AIRAC 11-2026.

## Nieuw live 21 nov
- Arnhem–Nijmegen: Deelen CTR/RMZ, Terlet, R9/R61, PJA Wijk bij Duurstede/Westbroek, missies Terlet en Arnhem, Eusebiuskerk.
- Gevaren: lierterreinen scherm/delta als **cilinder** (250 m, GND–bovengrens uit AIP ENR 5.5), label op de top (Christian, idee vfr3d).
- Doorsnede langs een lijn, rondleiding (7 stappen), linkvoorbeeld (og).
- Fix: klaring Deelen CTR dekt de RMZ Deelen (H24) erover (`d_ctr_covers_rmz`).
- Fix: kantelen na ▶ / nieuwe opdracht: ijken op gemiddelde na 0,3 s rust (max 1,2 s), scheef tot 45° = rechtuit, vergrendelde liggende houding blijft (`d_tilt_pause_edges`, ruis + tik-schok).

## Klaar op `wip/live-21nov`, nog niet live (sessie 21 nov middag)
- "Houd de telefoon even stil"-melding bij onrustige hand na ▶ (getest, kantel groen).
- Alle 74 ENR 5.5-terreinen in de regio als cilinder: scherm/delta, lierstart zweefvliegen (GND–2300 ft AGL), modelvliegen, ULV (`tools/build_enr55.py`, test `d_enr55_sites` groen).
- Kaart liggend: sonde als lade rechts (≤ ⅓), kolom weg zolang de lade open is (`d_landscape_probe` 4/4).
- Fix terreinmeldingen (lier e.d.): kwamen elke 4 s terug zolang je in de buurt bleef (ENR 5.5-terreinen werden nooit als 'gezien' gemarkeerd). Nu één melding per nadering, zoals luchtruim. Test in `d_enr55_sites`.
- 'ballon voorbij doel' was geen flaky: tests zetten alleen luchtruim op 'gewaarschuwd', niet de terreinen → tests aangepast. Quick 14/14.
- **Volgende:** volledige suite → live.

## Nieuwe opdracht Christian (21 nov middag)
Zie `docs/OPDRACHT-21nov.md`: tutorial + startflow, MSFS-besturing, sneltoetskaart, Spatie bij keerpunten, herkenningspunten-audit, ballonrealisme.

## Wacht op Christian
- **Usage-meter (eenmalig, ±2 min op de pc):** `python tools/usage_probe.py --login` (inloggen op claude.ai in het venster, venster sluiten), daarna `python tools/usage_probe.py --install`. Vanaf dan leest elke sessie de weeklimiet zelf met `python tools/usage.py`.
- **Telefoontest kantelen**: pauzeer/▶ een paar keer, ook scheef vastgehouden, en na "Nieuwe opdracht".
- Claude-browserpane op de pc inloggen op claude.ai (weeklimiet aflezen; 21 nov nog uitgelogd).
- www-doorverwijzing + automatische verlenging domein (OVH).
- Mexico 15 dec – 9 jan: vóór vertrek alle data voor heel NL binnen.

## Top 5 (de noordster: conflicten zien)
1. **Draaimoment live** na Christians telefoontest (zie 5).
2. **Data via GitHub Actions** (akkoord Christian 21 nov; `.github/workflows/data-probe.yml` → branch `data/probe`). Bereikbaar vanaf GitHub:
   ✓ **Geoportaal-API** `geoportaal.lvnl.nl/api/search/v1/collections/all/items` → datasets Airspace/Aerodrome/Route/Waypoint/Navaid (Feature Service, WFS, OGC), **licentie CC BY 4.0** ✓.
   ✓ **eAIP** met `curl` + browser-User-Agent (Playwright krijgt Cloudflare-check); edities als `AIRAC AMDT 12-2026_2026_11_26\index.html`.
   ✓ Overpass (OSM) met User-Agent. ✓ luchtruim3d.nl (+ Playwright) → automatische live-test na publicatie mogelijk.
   ✗ geoservices.lvnl.nl: onvolledige certificaatketen (en LVNL raadt het af) → niet meer gebruiken.
2b. ✅ **Datapijplijn draait:** `tools/fetch_lvnl.py` + `.github/workflows/data-lvnl.yml` → branch `data/lvnl` (wekelijks + bij push). Heel NL: 22 luchtruimlagen (o.a. CTR 16, TMA 42, Parajump 21, Danger 19, Restricted 26, TRA/TSA, Glider area, HPZ) + 13 vliegveldlagen (o.a. Glider 13, Microlight 20, Hangglider 63). Licentie CC BY 4.0. Lezen: `git fetch origin data/lvnl`. **Gevarenlagen (para, scherm/lier, ULV) zijn hiermee binnen bereik zonder pc.**
   Tip voor Christian: in claude.ai → Instellingen → Capabilities kun je domeinen toestaan (bv. services-eu1.arcgis.com, eaip.lvnl.nl, overpass-api.de); dan kan de cloudwerkplek er ook direct bij.
3. **Data uit index.html** (Geoportaal gevalideerd: 0 verschillen met de huidige data; buurlanden apart houden, zie LOG 21 nov) naar `data/luchtruim.json` + `data/regio-*.json`, één ophaalscript (LVNL via Chrome op de pc). Fundament voor uitbreiding.
4. **Arnhem–Nijmegen** — voorbereid: ruwe OSM-data staat op branch `data/osm` (`osm/arnhem-nijmegen/*.json`: snelwegen, rivieren, water, bebouwing, heide/zand, banen, hoogspanning, windturbines, plaatsen, hoge bouwwerken; via `tools/fetch_osm.py` + `.github/workflows/data-osm.yml`, Overpass is soms vol → retries). Luchtruim: `python tools/build_airspace.py --bbox 4.75,51.2,6.25,52.15 --check` → +39 volumes (o.a. EHDL Deelen CTR+RMZ, Terlet GLD 002–004, PJA 019/020, R9, R61, Nieuw Milligen sectoren B/E, Schiphol TMA-delen). **Nog te doen:** converter OSM → app-formaat (`osm`/`areadata`/`rwdata`/`pwdata`-blokken), bbox-constanten (gx0…gn1), NL-landvlak, missies Deelen/Terlet/Malden.: Malden, Deelen, Terlet, Nieuw Milligen TMA, SUP 03/2022, 3 regiomissies, link `#arnhem`.
6. **"Heel Nederland-week" met de full reset (±3–6 dec, vóór 10 dec):** luchtruim landelijk in één keer; landschap per regio (Randstad → Noord → Zeeland/Limburg); alle data binnen vóór Mexico.
5. **Draaimoment staand↔liggend:** fix klaar op `wip/draaien` (alle kanteltests groen, ook vergrendelde schermstand via zwaartekracht-assenstelsel). Wacht op Christians telefoontest + "ok" → live.

## Klaar op `wip/gevaren` (bovenop `wip/draaien`, nog niet live)
- **Luchtruimdata nu uit het LVNL Geoportaal (CC BY 4.0)** via `tools/build_airspace.py --bbox … --check|--write` (0 verschillen in grenzen; +EHTRA12/12A hoog; buitenland EB*/ED* blijft uit de oude data). Bronvermelding aangepast.
- Testharnas robuuster: wachten op wandklok i.p.v. frames (panel/looping), `fly()` wacht op het paneel.
- 10 lierterreinen scherm-/deltavliegen in de regio (LVNL Hangglider-laag): paarse ring + label, waarschuwing onder 2000 ft binnen 1,5 km, vermelding in de sonde (`d_winch_sites`). Kabelhoogte staat niet in de data → verwijzing ENR 5.5.

## Klaar op `wip/arnhem` (bovenop `wip/gevaren`, nog niet live) — volledige suite groen 21 nov (28+136+8, seed 2115)
- **Regio uitgebreid tot 52.15 N**: Arnhem, Nijmegen, Rivierenland, Veluwezoom, Utrecht-zuid. Landschap uit OSM (`tools/build_landscape.py --region arnhem-nijmegen --clip 4.75,51.8,6.15,52.15 --write`), 92 luchtruimvolumes (o.a. Deelen CTR, Terlet GLD, Nieuw Milligen B/E, Schiphol-TMA-delen), velden Deelen/Terlet/Soesterberg, NL-vlak uit de OSM-landsgrens.
- AIP-gecontroleerd (eAIP AMDT 11-2026): paradropzones Wijk bij Duurstede/Westbroek (FL060, Skydive Hilversum), R9 Harskamp + R61 Arnhemse Heide (tijden als Reek/Riel), Deelen CTR/RMZ. `tools/aip_check.py`: 16/16 frequenties OK.
- **Doorsnede** (backlog M4): sonde → "📏 Doorsnede vanaf hier" → tik eindpunt → verticaal profiel (wortelschaal, labels per volume, P/R gearceerd), lijn op de kaart (`d_cross_section`).
- **Rondleiding** (⚙ Weergave → 🎬): 7 stappen CTR → TMA → P → militaire CTR/RMZ → zweefvlieggebied/lier → sonde/doorsnede; teksten uit de data, uitgelicht volume (`d_tour`).
- 2 nieuwe missies: *Naar de Veluwe* (Terlet, les Deelen CTR), *Over de Rijn* (Nijmegen → Arnhem).
- Deelen: AIP ENR 2.1/2.2 (AIRAC 11-2026) → Tower 129.930, CTR HO (dus altijd als actief getoond + NOTAM-hint), RMZ H24 Dutch MIL Info 132.350.
- **eAIP-spiegel** draait: `tools/fetch_eaip.py` + workflow → branch `data/eaip` (ENR 1/2/5, GEN 2.1, AD 2 van burgervelden; militaire velden staan niet in AD 2).
- **Open:** Eusebiuskerk toegevoegd; bruggen (Waalbrug, John Frostbrug) niet betrouwbaar in OSM-namen → later;

## AIRAC-wissel 26 nov (AMDT 12-2026)
- Na donderdag: `git fetch origin data/lvnl data/eaip`, dan `python tools/build_airspace.py --bbox 4.75,51.2,6.15,52.15 --check` en `python tools/aip_check.py` (21 nov: 16/16 frequenties OK tegen AMDT 11-2026). AIRAC-datum in de footer bijwerken.

## Daarna
- Gevarenlagen LVNL (Parajump, Miscellaneous, Obstacles), één klik naar de eAIP-plek, minimale vlieghoogtes SERA.5005(f) (pc).
- Kaart liggend: sonde als smalle lade rechts.
- AIP-correctheid: TRA-status zonder NOTAM, Nieuw Milligen TMA D "klasse E", één klik naar de AIP-plek.
- Uitbreiden naar Arnhem–Nijmegen, daarna heel NL.

## Wacht op Christian
- LVNL antwoordde 19 nov (gis@lvnl.nl): gebruik het Geoportaal; licentie staat in de metadata; de VFR-chart-services kunnen veranderen.
- www-doorverwijzing + automatische verlenging domein (OVH).
- Claude-browserpane op de pc één keer inloggen op claude.ai, zodat de weeklimiet zelf af te lezen is.
- Mexico 15 dec – 9 jan: vóór vertrek samen alle LVNL/OSM-data voor heel NL downloaden.

## Ideeënbak (uit de oude backlog, nog niet beoordeeld)
- Koers voor na Eindhoven: korte scenario-missies met een replay en de AIP-regel erbij; data los van de app (`data/airac-*.json` voor heel NL).
- Doorsnede langs een lijn (A→B verticaal profiel). IFR-naderingsgebieden. Grensstrook DE (squawk + luisterfrequentie per TMZ, bv. Niederrhein).
- Spelplezier: reeks opdrachten met sterren, dagelijkse uitdaging, herkenningspunten "vinden".
- Volledige oude backlog: claude.ai-project `claude/06-backlog.md`.
