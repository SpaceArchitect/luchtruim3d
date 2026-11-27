# Status — lees dit eerst

*Bijgewerkt: 28 nov 2026, 00:00 (sessie 27 nov). Backlog: **`docs/BACKLOG.md`** (enige lijst). Volgorde: **AIRAC → bugs → rest** (Christian 25 nov).*

## Live
- https://luchtruim3d.nl = `main` (25 nov). AIRAC 12-2026 gecontroleerd (geen wijziging in de regio). Terugdraaien: `release/2026-11-25-3`, `-25-2`, `-25`, `-22`, `-21`, `-15`.

## Christian test za 28 nov (Galaxy A55, Chrome): stotter bij ▶
Per link: pagina openen → Zweefvliegtuig → 'Vlieg naar Meteren (1/3)' → ▶ → 3 s vliegen. Doe dat 3×, en maak een screenshot van het groene kader linksonder (of noteer de regels 'na ▶ #1' en 'js …'). Onderaan staat de versie.
- **0** `wip/opnieuw` (huidige stand, 2834 ms op 26 nov): https://raw.githack.com/SpaceArchitect/luchtruim3d/wip/opnieuw/index.html?fps=1
- **a** zónder labels-in-batch: https://raw.githack.com/SpaceArchitect/luchtruim3d/wip/stotter-a/index.html?fps=1
- **b** zónder compile-opwarmen: https://raw.githack.com/SpaceArchitect/luchtruim3d/wip/stotter-b/index.html?fps=1
- **c** zonder beide (= stand 26 nov 17:13, toen 112 ms): https://raw.githack.com/SpaceArchitect/luchtruim3d/wip/stotter-c/index.html?fps=1
- **d** zonder beide + bij het laden 1×1 px écht tekenen: https://raw.githack.com/SpaceArchitect/luchtruim3d/wip/stotter-d/index.html?fps=1
- Lezen: `js sim/render/labels/hud` = JS-tijd van dat frame, `knop` = duur van ▶. Grote gap + kleine JS = GPU/pipeline-stall; grote render = shader-link; grote knop = synchrone berekening.
- Beslisregel daarna: de snelste variant die < 100 ms haalt wordt de basis; is c ≈ 112 ms en d beter → d. Niets haalt < 100 ms → laadscherm (akkoord Christian).

## Klaar maar nog niet live (branches)
- **`wip/opnieuw`**: 7 P1-bugfixes 26 nov + kantelfix (Christian akkoord) + opnieuw bij fout + bruggen/spoor/labelbudget + meetlat + d_start_smooth. **Niet live tot de stotter beslist is.** Daarna: regressie eruit (variant uit de test), `wip/spike-mil-26nov` + `wip/dagelijks` erin, volledige suite → `release/<datum>` → `main`.
- **`wip/dagelijks`**: dagelijkse uitdaging + zweefkist-klimlimiet; 27 nov: uitvliegen/generator/d_daily groen, alle 18 vaste missies gehaald (`mission_report --fly`).
- **`wip/spike-mil-26nov`**: TRA/TSA-uitleg (ENR 5.2).
- **`wip/heelnl`** (heel NL, 259 volumes): 27 nov `wip/opnieuw` erin gemerged, 6 regio-gebonden tests opgelost + bug WÂNSWERT (naam met accent viel weg). vóór de laatste 2 testfixes: desk 68/69, p7 66/69; de rode tests daarna los groen (volledige run nog te doen); `d_tilt_pause_edges` 1× van 6 rood alleen op heelnl (tragere frames) → in de gaten houden.
- **`wip/osm-nl-26nov`**: Action `data-osm-nl` gerepareerd (Overpass-502 gaf gaten). Nieuwe run gestart 27 nov 23:30 (17 tegels, één tegelijk, uren).

## Eerstvolgende sessie (di 1 dec 22:47)
1. Uitslag stottertest verwerken (zie beslisregel) → live-gang zoals hierboven (volledige suite; kantelfix is al door Christian getest).
2. `data/osm-nl`: `osm-nl/MISSING.json` lezen; tegels met ontbrekende lagen opnieuw (workflow_dispatch met `tiles`). Daarna landschap heel NL samenvoegen (± 1 MB compact → pagina ±1,5 MB: dan data/*.json-splitsing, BACKLOG).
3. Heel NL: volledige suite op `wip/heelnl` (alle 4 vormen); `d_tilt_pause_edges` herhalen.
4. NOTAM/AUP: weekend 28–29 nov samen met Christian (spike LOG 26 nov).

## Reset-push (Christian 25 nov)
- Eén volledige reset van de weeklimiet, geldig t/m 10 dec. 27 nov–4 dec heel NL voorbereiden; vr 4–zo 6 dec sessies; ma 7 dec reset; 7–10 dec heel NL bouwen. Christian test 11–14 dec, vóór Mexico (15 dec).

## Budget
- 1 SP = 1% weeklimiet; herijking 26 nov: **1% ≈ 5,5 M tokens** (ccusage). Sessie 27 nov: ±17 M tokens ≈ 3 SP (weinig: vooral wachten op tests).

## Werkwijze
- Volledige suite in twee helften parallel (`--forms desk,p7` en `--forms p7l,se`, eigen `E2E_PORT`). Andere worktree testen: `THREE_DIR=<repo>/.devenv/node_modules/three`.
- Overpass/eAIP/Eurocontrol alleen via GitHub Actions. Een push die `tools/fetch_osm.py` wijzigt start óók `data-osm` (wist data/osm): annuleren als dat niet de bedoeling is.
- NOTAM: geen NOTAMs in de app tot er een geverifieerde primaire bron is.
- Eindcontrole elke sessie: BACKLOG, STATUS en LOG nalopen.
