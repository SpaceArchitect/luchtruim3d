# Status — lees dit eerst

*Bijgewerkt: 28 nov 2026 21u (sessie 27–28 nov). Backlog: **`docs/BACKLOG.md`** (enige lijst). Volgorde: **AIRAC → bugs → rest**. **Elke sessie door tot ±25 SP, ook als je op Christian wacht** (CLAUDE.md).*

## Live
- https://luchtruim3d.nl = `main` **28 nov 09:58 UTC** (5bf56cf): laadscherm, RT per blok, TRA/TSA-uitleg, dagelijkse uitdaging, AIRAC-vangnet. Terugdraaien: `release/2026-11-28-2`, `release/2026-11-28`, ouder.

## Klaar op `develop` (nog niet live)
- Stotterfix (één laadscherm per missie, geen generator tijdens vliegen; meting Christian: desktop 23 ms, A55 staand 32 ms), infovak na kaart → vliegen, waarschuwing vóór CTR op tijd (draaicirkel), knop zonder code, ballon W/↑ = branden, TRA/TSA: hoe weet je of het actief is (Dutch MIL Info 132.350).
- Volledige suite 28 nov 20u: 336/338; rood = 2 kanteltests p7l → **echte bug** (zie hieronder). Niet live tot groen + telefoontest.

## Half af (werkbranches)
- **`wip/kantel-laad`**: kantelen ging uit na het laadscherm op een trage telefoon (terugval-wekker 2,5 s liep door tijdens zwaar werk). Fix: alleen 'stille' tijd telt. Test d_tilt_long_task (faalde eerst). **Raakt kantelen → Christian test op de A55 vóór live.** Daarna: merge in develop → volledige suite (`tools/suite.py` of twee helften) → live.
- **`wip/ios-strook`**: grijze strook rechts op iPhone (Raquel); canvas herstelt zichzelf. Test d_view_fills; nog niet gedraaid.
- **`wip/test-split`**: `tools/suite.py` = 64 tests parallel op 4 cores, 14 tijdgevoelige los (idee Christian). Eén keer naast de oude manier draaien, dan standaard.
- `wip/tiles` (heel NL), `wip/vindbaar-28nov` (Christian: privacytekst over.html), `wip/nop-spike` (1a deel 1 klaar, wacht op NOP Office).

## Eerstvolgende stappen
1. A55-test kantelen (wip/kantel-laad) → develop → suite → **live** (met release/<datum>).
2. Bugs 0e (iPhone-strook), 0f (Vught ×60: **hele klasse**: elk gevaar, elk tempo, elke start), 0g (vorm se → WebKit), 0d (liggend: camera + UI ≤ ⅓, varianten als screenshot), 0c (ballon laag boven bebouwing).
3. Dan BACKLOG-volgorde (U5 tempo per toestel bij de UX-story).

## Werkwijze
- Suite **nooit 4 processen tegelijk** (kantelen/fps worden rood); twee helften (`--forms desk,p7` / `--forms p7l,se`, eigen `E2E_PORT`, `python3 -u`) of `tools/suite.py`. `THREE_DIR=/home/user/luchtruim3d/.devenv/node_modules/three` in worktrees.
- Docs gaan via de claude/…-branch en mee bij publicatie (direct naar main pushen wordt geweigerd).
- 1 SP ≈ 11 M tokens (Christian: 21% bij 240 M).
- NOTAM: geen NOTAMs in de app tot er een geverifieerde primaire bron is (EAD Basic: voorwaarden lezen; LOG 28 nov).
