# Status — lees dit eerst

*Bijgewerkt: 26 nov 2026, ±17:00 (sessie AIRAC + bugs + heel NL). Backlog: **`docs/BACKLOG.md`** (enige lijst). Volgorde: **AIRAC → bugs → rest** (Christian 25 nov).*

## Live
- https://luchtruim3d.nl = `main` (25 nov). AIRAC 12-2026 (26 nov) gecontroleerd: **geen wijziging in de regio** (LOG). Terugdraaien: `release/2026-11-25-3`, `-25-2`, `-25`, `-22`, `-21`, `-15`.

## Klaar maar nog niet live (branches)
- **`wip/sessie-26nov`** (gepusht): AIRAC-footer 12-2026 + 7 P1-bugs (Start = volgende missie, ballon/Maas, alles aanklikbaar, grondring, vario, labels over toestel, camera liggend), elk met test. Volledige suite liep 26 nov (zie LOG voor de uitslag). Groen → `release/<datum>` maken en naar `main`.
- **`wip/tilt-26nov`** (gepusht, **sensor → Christian test eerst**): kantelen ijkt alleen bij start/nieuwe opdracht en na draaien. Preview: https://raw.githack.com/SpaceArchitect/luchtruim3d/wip/tilt-26nov/index.html — test: in een bocht een melding laten komen, ▶, bocht moet doorgaan.
- **`wip/spike-mil-26nov`** (gepusht): TRA/TSA-uitleg volgens ENR 5.2 + probe-Action. Meenemen bij de volgende live-gang.
- **`wip/osm-nl-26nov`** (gepusht): Action `data-osm-nl` (17 tegels, compact → branch `data/osm-nl`). Liep 26 nov nog.
- **`wip/heelnl`** (gepusht, nog niet getest): heel NL begin — 259 volumes, FIR-grens, 40 velden, 214 ENR 5.5-terreinen, AIPINFO 90 volumes uit eAIP (aip_check 0 afwijkingen), TMZ-tijden landelijk, klasse A lichter, labeldichtheid, verre volumes niet tekenen, CLAUDE.md-FMC-correctie. De push start ook data-eaip met de bredere paginaset (AD 2 alle velden).
- **`wip/dagelijks`** (gepusht, nog niet getest): dagelijkse uitdaging + test d_daily, zweefkist-klimlimiet (+1000 ft).

## Eerstvolgende sessie (vr 27 nov 22:47) — AIRAC → bugs → rest
1. Uitslag suite `wip/sessie-26nov` → live (release-branch eerst).
2. Heel NL verder: suite draaien op `wip/heelnl`; data/osm-nl samenvoegen (plaatsen, wegen, rivieren landelijk); eAIP-ophaal verbreden (AD 2 alle velden: torenfrequenties Schiphol/Rotterdam/Eelde/Beek/De Kooy ontbreken nog); `mission_report --fly` na de zweefkist-klimlimiet.
3. Militaire gebieden: beslissing Christian over NM B2B (P1-2).

## Reset-push (Christian 25 nov)
- Eén volledige reset van de weeklimiet, geldig t/m 10 dec. 27 nov–4 dec "heel NL" voorbereiden; vr 4–zo 6 dec sessies; ma 7 dec reset; 7–10 dec heel NL bouwen. Christian test 11–14 dec, vóór Mexico (15 dec).

## Budget
- 1 SP = 1% weeklimiet; kalibratie 25 nov: 1% ≈ 7,3 M tokens (ccusage). 26 nov: weeklimiet 91% (Christian), laatste dag vóór de reset → doorwerken tot op.

## Werkwijze-notities
- Volledige suite in twee helften parallel (`--forms desk,p7` en `--forms p7l,se`, eigen `E2E_PORT`).
- Overpass/eAIP/Eurocontrol alleen via GitHub Actions (cloud kan er niet bij). AIRAC-dag: controleer of data/eaip en data/lvnl echt ververst zijn.
- NOTAM: geen NOTAMs in de app tot er een geverifieerde primaire bron is.
- Eindcontrole elke sessie: BACKLOG, STATUS en LOG nalopen.
