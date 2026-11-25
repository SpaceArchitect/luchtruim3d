# Status — lees dit eerst

*Bijgewerkt: 25 nov 2026, middag (einde sessie met Christian). Backlog: **`docs/BACKLOG.md`** (enige lijst). Volgorde: **AIRAC → bugs → rest** (Christian 25 nov).*

## Live
- https://luchtruim3d.nl = `main` (25 nov, 3 live-gangen vandaag): fixes Evoluon-klaring, knipperende labels, lieren als één cilinder ·
  voorbeeldcircuit weg, Malden/Nistelrode gedeelde terreinen, bruggen langs de weg + 3 stadsbruggen · **missies**: 6 vaste per toestel op
  gemeten zwaarte, daarna een generator met oplopende moeilijkheid; elke missie wordt eerst door de app zelf uitgevlogen (route zónder
  klaring: om, over of onder), sterren, leerdoel (`docs/MISSIES.md`).
  Terugdraaien: `release/2026-11-25-3` (vóór missies), `-25-2` (vóór batch 2), `-25` (live 22 nov), `release/2026-11-22`, `-21`, `-15`.
- Regio: Eindhoven + Arnhem–Nijmegen tot 52.15 N, AIRAC 11-2026.

## Half af
- Niets. (`wip/sessie-25nov` is volledig live.)

## Eerstvolgende sessie (vr 27 nov 22:47) — volgorde AIRAC → bugs → rest
0. **AIRAC-wissel 26 nov (AMDT 12-2026)** (terugkerend P0): `git fetch origin data/lvnl data/eaip` → `build_airspace.py --bbox 4.75,51.2,6.25,52.15 --check`, `aip_check.py`, footer, `mission_report.py --fly --gen 8`.
1. **5 bugs uit P1**: Start = volgende missie · ballon aan de Maas niet geslaagd · alles aanklikbaar (ook lier/model) · zwevende grondringen · vario-snelheid.
2. **Heel NL voorbereiden** (reset-push, P2 bovenaan).

## Reset-push (Christian 25 nov)
- Eén volledige reset van de weeklimiet, geldig t/m 10 dec; gewone weekreset vr 18:00. 27 nov–4 dec "heel NL" voorbereiden; sessies vr 4, za 5,
  zo 6 dec (±75%) → Christian reset ma 7 dec → ma 7–do 10 dec heel NL bouwen (±100%). Christian test 11–14 dec, vóór Mexico (15 dec).

## Budget
- 1 SP = 1% weeklimiet; schatting vooraf in LOG, Christian meldt het werkelijke %. Meter in de cloud: `npx -y ccusage@latest weekly --json`
  (alleen deze container). **Kalibratie 25 nov: 1% ≈ 7,3 M tokens** → 25 SP ≈ 180 M tokens. Deze sessie: zie LOG.

## Werkwijze-notities
- Volledige suite: zware missietests alleen op desktop; draai in twee helften parallel (`--forms desk,p7` en `--forms p7l,se`, eigen `E2E_PORT`).
- Overpass/eAIP/Geoportaal alleen via GitHub Actions; luchtruim3d.nl niet vanuit de cloud (deploy via GitHub controleren).
- NOTAM: geen NOTAMs in de app tot er een geverifieerde primaire bron is; FAA alleen ter vergelijking.
- Eindcontrole elke sessie: BACKLOG, STATUS en LOG nalopen (CLAUDE.md).
