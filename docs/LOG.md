# Log — beslissingen en lessen (nieuwste onderaan, één regel per stuk)

Oudere geschiedenis: claude.ai-project `claude/03-beslissingen-log.md` en `claude/sprints/`.

- 2026-11-09 Bron = LVNL-MapServer `geoservices.lvnl.nl/arcgis/rest/services/VFRchart/*` (GeoJSON); alleen bereikbaar via de browser op de pc.
- 2026-11-09 three.js met een lokale platte projectie; data ingebakken in `index.html`.
- 2026-11-10 Landen: het toestel stopt, de simulatie loopt door. Tijdsafhankelijk luchtruim volgens AIP GEN 2.1 §6 (feestdagen).
- 2026-11-14 Live op luchtruim3d.nl via GitHub Pages; publiceren = push naar `main`.
- 2026-11-15 Labels vervagen afgewezen: een label is er óf niet. Alle groepen standaard aan. Gevaren gaan voor.
- 2026-11-15 Teruggedraaid naar 053d823 na de kantel-bug op live. Les: sensortests met realistische ruis; geen fix na de laatste test.
- 2026-11-20 Nieuwe briefing (`CLAUDE.md`): doel boven proces, geen sprints/PI/DFMEA/verplicht panel. Testen evenredig (quick per commit, volledig vóór `main`). Eén omgeving voor cloud + pc via `tools/setup.py`. Repo = geheugen (`docs/STATUS.md`, `docs/LOG.md`).
