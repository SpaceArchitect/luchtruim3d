# Status — lees dit eerst

*Bijgewerkt: 21 nov 2026, 01:00 (cloudsessie 20→21 nov).*

## Live
- https://luchtruim3d.nl = `main` = inhoud van 14 nov (053d823), teruggedraaid op 15 nov.
  Vorige live-versies: `release/s1-live-1…4`.
- Regio: Eindhoven (bbox 4.75–6.15 E / 51.2–51.8 N), AIRAC 29 okt 2026.

## Half af (bewaard, niet live)
- `wip/s2-15nov`, `wip/s2b-15nov`: kantel-ijken na draaien, labels vervagen (afgewezen),
  TRA/TSA aan. Bruikbaar als bron, niet blind mergen. De kantel-fix brak live (te strenge
  stilte-eis); test `d_tilt_start_shaky` staat in de stash op `wip/s2b-15nov`.

## Klaar op `wip/briefing-20nov` (nog niet live; wacht op "ok, live" van Christian)
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
1. **Publiceren** van het bovenstaande na Christians mobiele check (missies + kantelgevoel). Push naar `main` vraagt zijn expliciete "ok, live".
2. **Data via GitHub Actions** (akkoord Christian 21 nov): `.github/workflows/data-probe.yml` → branch `data/probe`. Geoportaal (ArcGIS Hub, org `lvnl.maps.arcgis.com`) ✓ bereikbaar; Overpass 406 (User-Agent toevoegen); eAIP 403 en geoservices.lvnl.nl onbereikbaar vanaf GitHub. Volgende stap: Hub-API zoeken naar luchtruimdatasets + licentie uit de metadata.
3. **Data uit index.html** naar `data/luchtruim.json` + `data/regio-*.json`, één ophaalscript (LVNL via Chrome op de pc). Fundament voor uitbreiding.
4. **Arnhem–Nijmegen**: Malden, Deelen, Terlet, Nieuw Milligen TMA, SUP 03/2022, 3 regiomissies, link `#arnhem`.
6. **"Heel Nederland-week" met de full reset (±3–6 dec, vóór 10 dec):** luchtruim landelijk in één keer; landschap per regio (Randstad → Noord → Zeeland/Limburg); alle data binnen vóór Mexico.
5. **Draaimoment staand↔liggend** (Christian: "essentieel"): branch `wip/draaien`. Bevriezen + koers terugzetten bij een draai, ijken na 0,4 s rust; test `d_tilt_rotate_real` (oude code: 65° bocht). **Open:** vergrendelde schermstand (rol ~90° in het oude scherm) wordt nog niet goed geijkt. Eerst doen in de nieuwe chat.

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
