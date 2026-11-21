# Status — lees dit eerst

*Bijgewerkt: 21 nov 2026, 01:00 (cloudsessie 20→21 nov).*

## Live
- https://luchtruim3d.nl = `main` = 170a615 (21 nov 01:30, volledige suite groen: 28 smoke + 128 det + 8 fuzz, seed 2111). Live gecontroleerd via GitHub Actions.
  Vorige live-versie: `release/2026-11-15` (053d823-inhoud); daarvoor `release/s1-live-1…4`.
- Regio: Eindhoven (bbox 4.75–6.15 E / 51.2–51.8 N), AIRAC 29 okt 2026.

## Half af (bewaard, niet live)
- `wip/s2-15nov`, `wip/s2b-15nov`: kantel-ijken na draaien, labels vervagen (afgewezen),
  TRA/TSA aan. Bruikbaar als bron, niet blind mergen. De kantel-fix brak live (te strenge
  stilte-eis); test `d_tilt_start_shaky` staat in de stash op `wip/s2b-15nov`.

## Live sinds 21 nov (was `wip/briefing-20nov`)
Preview: https://raw.githack.com/SpaceArchitect/luchtruim3d/wip/briefing-20nov/index.html
- Alle luchtruimgroepen standaard aan; kaartlabels aan/uit op afstand, gevaren 1,6× verder (`d_defaults_labels`).
- Missiedoel als goudkleurig baken + label "🎯 A67 · x km" (Boyd) (`d_goal_marker`).
- Tik op een melding = verder; de tik viel eerst door naar de 3D-scène = "lege melding onderin" (Fleur) (`d_tap_notice`).
- Toestel wisselen: tik op het toesteltje onderin (Fleur) (`d_ac_switch`).
- Landen in de bebouwde kom krijgt een eigen tekst; missietekst zonder dubbel "verboden" (`d_land_city`).
- Tests draaien op een vast tijdstip (di 10:00): de uitslag hing af van de klok (RMZ 's nachts actief).
- Kantelen geleidelijk: dode zone 8°, lineair tot vol bij 35° (bocht) / 30° (klim) (`d_tilt_analog`, ±5° ruis).
- 7 missies rond echte conflicten (`MISSIONS` in index.html): start berekend uit de data, keerpunten, les + ⭐ achteraf; ballon met hoogteplan-solver en eigen wind (`d_missions`).
- Doelbaken: lichtbundel, draaiende ruit, uitdijende ring. Kaart liggend: tijduitleg verborgen.

## Top 5 (de noordster: conflicten zien)
1. **Draaimoment live** na Christians telefoontest (zie 5).
2. **Data via GitHub Actions** (akkoord Christian 21 nov; `.github/workflows/data-probe.yml` → branch `data/probe`). Bereikbaar vanaf GitHub:
   ✓ **Geoportaal-API** `geoportaal.lvnl.nl/api/search/v1/collections/all/items` → datasets Airspace/Aerodrome/Route/Waypoint/Navaid (Feature Service, WFS, OGC), **licentie CC BY 4.0** ✓.
   ✓ **eAIP** met `curl` + browser-User-Agent (Playwright krijgt Cloudflare-check); edities als `AIRAC AMDT 12-2026_2026_11_26\index.html`.
   ✓ Overpass (OSM) met User-Agent. ✓ luchtruim3d.nl (+ Playwright) → automatische live-test na publicatie mogelijk.
   ✗ geoservices.lvnl.nl: onvolledige certificaatketen (en LVNL raadt het af) → niet meer gebruiken.
2b. ✅ **Datapijplijn draait:** `tools/fetch_lvnl.py` + `.github/workflows/data-lvnl.yml` → branch `data/lvnl` (wekelijks + bij push). Heel NL: 22 luchtruimlagen (o.a. CTR 16, TMA 42, Parajump 21, Danger 19, Restricted 26, TRA/TSA, Glider area, HPZ) + 13 vliegveldlagen (o.a. Glider 13, Microlight 20, Hangglider 63). Licentie CC BY 4.0. Lezen: `git fetch origin data/lvnl`. **Gevarenlagen (para, scherm/lier, ULV) zijn hiermee binnen bereik zonder pc.**
   Tip voor Christian: in claude.ai → Instellingen → Capabilities kun je domeinen toestaan (bv. services-eu1.arcgis.com, eaip.lvnl.nl, overpass-api.de); dan kan de cloudwerkplek er ook direct bij.
3. **Data uit index.html** naar `data/luchtruim.json` + `data/regio-*.json`, één ophaalscript (LVNL via Chrome op de pc). Fundament voor uitbreiding.
4. **Arnhem–Nijmegen**: Malden, Deelen, Terlet, Nieuw Milligen TMA, SUP 03/2022, 3 regiomissies, link `#arnhem`.
6. **"Heel Nederland-week" met de full reset (±3–6 dec, vóór 10 dec):** luchtruim landelijk in één keer; landschap per regio (Randstad → Noord → Zeeland/Limburg); alle data binnen vóór Mexico.
5. **Draaimoment staand↔liggend:** fix klaar op `wip/draaien` (alle kanteltests groen, ook vergrendelde schermstand via zwaartekracht-assenstelsel). Wacht op Christians telefoontest + "ok" → live.

## Klaar op `wip/gevaren` (bovenop `wip/draaien`, nog niet live)
- 10 lierterreinen scherm-/deltavliegen in de regio (LVNL Hangglider-laag): paarse ring + label, waarschuwing onder 2000 ft binnen 1,5 km, vermelding in de sonde (`d_winch_sites`). Kabelhoogte staat niet in de data → verwijzing ENR 5.5.

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
