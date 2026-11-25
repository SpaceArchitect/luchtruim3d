# Status — lees dit eerst

*Bijgewerkt: 25 nov 2026, middag (sessie met Christian). Backlog: **`docs/BACKLOG.md`** (enige lijst). Volgorde: **AIRAC → bugs → rest** (Christian 25 nov).*

## Live
- https://luchtruim3d.nl = `main`: fixes 24/25 nov (Evoluon-klaring, knipperende labels, lieren als één cilinder) + batch 2 (voorbeeldcircuit weg,
  Malden/Nistelrode gedeelde terreinen, bruggen langs de weg + Waalbrug/De Oversteek/John Frostbrug, 6 herkenningspunten weg).
  Terugdraaien: `release/2026-11-25-2` (vóór batch 2), `release/2026-11-25` (live 22 nov), `release/2026-11-22`, `-21`, `-15`.
- Regio: Eindhoven + Arnhem–Nijmegen tot 52.15 N, AIRAC 11-2026.

## Half af
- **`wip/sessie-25nov` = missies** (nog niet live): 3D-routeplanner, 6 vaste missies per toestel op gemeten zwaarte, generator met
  bewezen route zónder klaring, vlucht-check vóór aanbieden (`misVerify`), sterren, eerlijk ballonplan. Volledige suite liep bij het
  afsluiten (in twee helften). Groen → live zetten (release-branch eerst). Rood → eerst fixen. Uitleg: `docs/MISSIES.md`.
  Preview: https://raw.githack.com/SpaceArchitect/luchtruim3d/wip/sessie-25nov/index.html

## Eerstvolgende sessie (vr 27 nov 22:47) — in deze volgorde
0. **AIRAC-wissel 26 nov (AMDT 12-2026)** (terugkerend P0): `git fetch origin data/lvnl data/eaip` → `build_airspace.py --bbox 4.75,51.2,6.25,52.15 --check`, `aip_check.py`, footer, `mission_report.py --fly --gen 8`.
1. Missies live (als nog niet gedaan), dan de **5 bugs uit P1**: Start = volgende missie · ballon aan de Maas niet geslaagd · alles aanklikbaar (ook lier/model) · zwevende grondringen · vario-snelheid.
2. **Heel NL voorbereiden** (reset-push, P2 bovenaan).

## Reset-push (Christian 25 nov)
- Eén volledige reset van de weeklimiet, geldig t/m 10 dec; gewone weekreset vr 18:00. 27 nov–4 dec "heel NL" voorbereiden; sessies vr 4, za 5,
  zo 6 dec (±75%) → Christian reset ma 7 dec → ma 7–do 10 dec heel NL bouwen (±100%). Christian test 11–14 dec, vóór Mexico (15 dec).

## Budget
- 1 SP = 1% weeklimiet; schatting vooraf in LOG, Christian meldt het werkelijke %. Meter in de cloud: `npx -y ccusage@latest weekly --json`
  (alleen deze container). Deze sessie: zie de SP-regel van 25 nov in LOG; verhouding tokens ↔ % volgt uit Christians terugmelding.

## Werkwijze-notities
- Volledige suite: zware missietests alleen op desktop; draai in twee helften parallel (`--forms desk,p7` en `--forms p7l,se`, eigen `E2E_PORT`).
- Overpass/eAIP/Geoportaal alleen via GitHub Actions; luchtruim3d.nl niet vanuit de cloud (deploy via GitHub controleren).
- NOTAM: geen NOTAMs in de app tot er een geverifieerde primaire bron is; FAA alleen ter vergelijking.
- Eindcontrole elke sessie: BACKLOG, STATUS en LOG nalopen (CLAUDE.md).
