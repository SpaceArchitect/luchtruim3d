# Status — lees dit eerst

*Bijgewerkt: 28 nov 2026 (sessie 27–28 nov). Backlog: **`docs/BACKLOG.md`** (enige lijst). Volgorde: **AIRAC → bugs → rest**. **Elke sessie door tot ±25 SP, ook als je op Christian wacht** (CLAUDE.md).*

## Live
- https://luchtruim3d.nl = `main` **28 nov 08:46 UTC** (4215d3e): laadscherm (openen, vliegen, ▶ start) + stotterfix variant d + 7 bugfixes 26 nov + kantelfix (Christian akkoord) + opnieuw bij fout + labelbudget + TRA/TSA-uitleg (ENR 5.2) + dagelijkse uitdaging + zweefkist-klimlimiet. Suite 277/278 (1 test-timing in d_loading gecorrigeerd, daarna op 4 vormen groen). Terugdraaien: **`release/2026-11-28`**, `-25-3`, `-25-2`, `-25`, `-22`, `-21`, `-15`.
- **Christian:** graag op de A55 kijken of de stotter weg is (laadscherm 'Starten…' i.p.v. stilstand).

## Klaar op branches (nog niet live)
- **`wip/rt-28nov`** (volgende live-gang, bevat live-28nov + airac-vangnet): RT per blok ('Wat doe je' per luchtruim), test d_rt_advice; 3 kleine review-fixes laadscherm (finally, race bij ▶ + kiezer, melding zonder WebGL); Action airac-check.
- **`wip/airac-vangnet`**: Action airac-check + `build_airspace --check` per volume (exit 1). Moet op `main` staan om na data-eaip/data-lvnl te draaien.
- **`wip/vindbaar-28nov`**: metadata zonder spel/game, JSON-LD, over.html, robots, sitemap. **Christian: privacytekst over.html goedkeuren** ('verwerkingsverantwoordelijke: Christian Niemeijer').
- **`wip/tiles`** (heel NL, bevat wip/heelnl + live-28nov): landschap per tegel (data/osm-nl in repo, laden ≤ 60 km, bouwen in plakjes van 6 ms), laadscherm wacht op tegels, opdracht vanaf de sonde + generator overal in NL, CTR/RMZ-tijden uit de AIP-tekst, missie 'lely'. Tests d_tiles, d_tiles_probe_cold, d_ctr_hours. Volledige suite nog niet gedraaid.
- **`wip/osm-nl-26nov`**: data-osm-nl gerepareerd; run 27–28 nov loopt (1 tegel tegelijk; nl-01 liep in de 4-uurs time-out → opnieuw met workflow_dispatch `tiles: nl-01` zodra de workflow op main staat, of tijdelijk op een wip-push).

## Eerstvolgende stappen
1. Volledige suite op `wip/rt-28nov` → live (dan draait airac-check ook na de data-acties).
2. Heel NL: volledige suite op `wip/tiles` (4 vormen), `uitvliegen` opnieuw (liep 28 nov in een time-out onder belasting), `osm-nl/MISSING.json` lezen en tegels bijwerken in `data/osm-nl/`.
3. BACKLOG P3 'Heel NL missies': landdoel-missietype (Eelde), langere aanloop (De Kooy), PJA op veld (Teuge).
4. NOTAM/AUP: weekend 28–29 nov met Christian (spike LOG 26 nov).

## Reset-push (Christian 25 nov)
- Reset geldig t/m 10 dec. 27 nov–4 dec heel NL voorbereiden; 7–10 dec bouwen; Christian test 11–14 dec, vóór Mexico (15 dec).

## Budget
- 1 SP ≈ 5,5 M tokens (ccusage). Sessie 27–28 nov: zie LOG (SP-regel).

## Werkwijze
- Volledige suite in twee helften parallel (`--forms desk,p7` en `--forms p7l,se`, eigen `E2E_PORT`); geen andere tests tegelijk (tijdmetingen worden onbetrouwbaar, uitvliegen haalt de time-out niet).
- Worktrees: `THREE_DIR=<repo>/.devenv/node_modules/three`. Merge-conflicten index.html/e2e.py (render-regel, `window.__vfr`, det-lijst): `python tools/merge_resolve.py <label> index.html tools/e2e.py`.
- Een push die `tools/fetch_osm.py` wijzigt start óók `data-osm` (wist data/osm): annuleren als dat niet de bedoeling is.
- Docs naar `main` pushen werd 28 nov door de auto-mode geweigerd: docs gaan mee met de live-gang.
- NOTAM: geen NOTAMs in de app tot er een geverifieerde primaire bron is.
