# Status — lees dit eerst

*Bijgewerkt: 21 nov 2026, 01:00 (cloudsessie).*

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

## Top 5 (de noordster: conflicten zien)
1. **Publiceren** van het bovenstaande na Christians mobiele check.
2. **Kantelen na draaien staand↔liggend:** eerst Christian laten testen op live (053d823) wat er nog misgaat. Daarna pas een fix, met realistische ruis.
3. **Gevarenlagen LVNL** (Parajump, Miscellaneous, Obstacles) + één klik naar de juiste eAIP-plek. **Pc-sessie nodig.**
4. **Kaartmodus op telefoon liggend + sonde** (Fleur: "onoverzichtelijk").
5. **Minimale vlieghoogtes** (SERA.5005(f)) als waarschuwing; eerst ENR 1.2 lezen (pc).

## Daarna
- AIP-correctheid: TRA-status zonder NOTAM, Nieuw Milligen TMA D "klasse E", één klik naar de AIP-plek.
- Uitbreiden naar Arnhem–Nijmegen, daarna heel NL.

## Wacht op Christian
- LVNL-licentiemail versturen (concept in Gmail).
- www-doorverwijzing + automatische verlenging domein (OVH).
- Claude-browserpane op de pc één keer inloggen op claude.ai, zodat de weeklimiet zelf af te lezen is.
- Mexico 15 dec – 9 jan: vóór vertrek samen alle LVNL/OSM-data voor heel NL downloaden.

## Ideeënbak (uit de oude backlog, nog niet beoordeeld)
- Koers voor na Eindhoven: korte scenario-missies met een replay en de AIP-regel erbij; data los van de app (`data/airac-*.json` voor heel NL).
- Doorsnede langs een lijn (A→B verticaal profiel). IFR-naderingsgebieden. Grensstrook DE (squawk + luisterfrequentie per TMZ, bv. Niederrhein).
- Spelplezier: reeks opdrachten met sterren, dagelijkse uitdaging, herkenningspunten "vinden".
- Volledige oude backlog: claude.ai-project `claude/06-backlog.md`.
