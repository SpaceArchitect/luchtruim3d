# Status — lees dit eerst

*Bijgewerkt: 28 nov 2026 (sessie 27–28 nov). Backlog: **`docs/BACKLOG.md`** (enige lijst). Volgorde: **AIRAC → bugs → rest**. **Elke sessie door tot ±25 SP, ook als je op Christian wacht** (CLAUDE.md).*

## Live
- https://luchtruim3d.nl = `main` **28 nov 09:58 UTC** (5bf56cf). Bevat:
  - laadscherm (openen, vliegen, ▶ start) + stotterfix variant d;
  - 7 bugfixes 26 nov + kantelfix (Christian akkoord) + opnieuw bij fout + labelbudget;
  - TRA/TSA-uitleg (ENR 5.2) + dagelijkse uitdaging + zweefkist-klimlimiet;
  - **RT per blok** ('Wat doe je' per luchtruim);
  - AIRAC-vangnet (Action airac-check, eerste run groen);
  - data-workflows heel NL (data-osm-pbf).
- Suites: live-28nov 277/278, rt-28nov 281/282; de ene fout telkens test-timing in d_loading, gecorrigeerd en op 4 vormen groen.
- Terugdraaien: **`release/2026-11-28-2`** (= live 08:46), **`release/2026-11-28`** (= 25 nov), `-25-3` … `-15`.
- **Stotter nog niet weg** (Christian 28 nov 11u: 3 laadschermen + stotter erna). Preview `wip/stotter2` (1 meting met ?fps=1 → wanneer en waar): https://raw.githack.com/SpaceArchitect/luchtruim3d/wip/stotter2/index.html?fps=1

## Klaar op branches (nog niet live)
- **`wip/tiles`** = heel NL (bevat alles van live). Inhoud:
  - landschap per tegel uit Geofabrik/osmium (compleet, 680 kB in `data/osm-nl`), laden ≤ 60 km, bouwen in plakjes;
  - laadscherm wacht op tegels;
  - opdracht vanaf de sonde + generator overal in NL;
  - CTR/RMZ-openingstijden uit de AIP-tekst;
  - **landdoel** (missie 'lely': landen op Lelystad);
  - tests: d_tiles, d_tiles_probe_cold, d_ctr_hours, d_land_goal.
  - Volledige suite: 28 nov gestopt voor de stotter → opnieuw draaien.
- **`wip/vindbaar-28nov`**: metadata zonder spel/game, JSON-LD, over.html, robots, sitemap. **Christian: privacytekst over.html goedkeuren** ('verwerkingsverantwoordelijke: Christian Niemeijer').

## Eerstvolgende stappen
1. Rode tests van de wip/tiles-suite oplossen → heel NL klaar voor Christians test (11–14 dec): eerst previewlink (raw.githack wip/tiles) + fps-meting op de A55.
2. BACKLOG 'Heel NL missies': De Kooy (langere aanloop), Teuge (doel buiten PJA); PJA's zijn in de app altijd verboden (vereenvoudigd) → velden met een PJA (Eelde) vallen af als landdoel.
3. NOTAM: route "Inloggen met EasyVFR" gekozen (BACKLOG P3, N1–N4). Wacht op EasyVFR (call 1–4 dec) en LVNL GIS; AUP wacht op NOP Office. Christian bevestigt de twee CLAUDE.md-punten (BACKLOG, open vragen).

## Reset-push (Christian 25 nov)
- Reset geldig t/m 10 dec. 27 nov–4 dec heel NL voorbereiden; 7–10 dec bouwen; Christian test 11–14 dec, vóór Mexico (15 dec).

## Budget
- 1 SP ≈ 10 M tokens (ccusage; ijking Christian 28 nov: 13% bij ±128 M).

## Werkwijze
- Volledige suite in twee helften parallel (`--forms desk,p7` / `--forms p7l,se`, eigen `E2E_PORT`, `python3 -u`, time-out 7000 s); **géén andere browsertests tegelijk**.
- Worktrees: `THREE_DIR=<repo>/.devenv/node_modules/three`. Merge-conflicten index.html/e2e.py: `python tools/merge_resolve.py <label> index.html tools/e2e.py`.
- OSM heel NL verversen: Action **data-osm-pbf** (workflow_dispatch op main, 23 min). Niet meer de Overpass-route (data-osm-nl, uren).
- Een push die `tools/fetch_osm.py` wijzigt op een wip-branch start óók `data-osm` (wist data/osm): annuleren als dat niet de bedoeling is.
- NOTAM: nog geen NOTAMs in de app; eerst N1 (CORS/app) en Christians akkoord op de CLAUDE.md-punten. Homebriefing-data nooit gebruiken (voorwaarden).
