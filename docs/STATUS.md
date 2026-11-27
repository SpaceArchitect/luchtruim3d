# Status — lees dit eerst

*Bijgewerkt: 26 nov 2026, ±17:00 (sessie AIRAC + bugs + heel NL). Backlog: **`docs/BACKLOG.md`** (enige lijst). Volgorde: **AIRAC → bugs → rest** (Christian 25 nov).*

## Live
- https://luchtruim3d.nl = `main` (25 nov). AIRAC 12-2026 (26 nov) gecontroleerd: **geen wijziging in de regio** (LOG). Terugdraaien: `release/2026-11-25-3`, `-25-2`, `-25`, `-22`, `-21`, `-15`.

## Klaar maar nog niet live (branches)
- **`wip/sessie-26nov`** (gepusht): AIRAC-footer 12-2026 + 7 P1-bugs (Start = volgende missie, ballon/Maas, alles aanklikbaar, grondring, vario, labels over toestel, camera liggend), elk met test. Volledige suite 26 nov: **278/278 groen**. Gaat live via wip/tilt-26nov (bevat dit).
- **`wip/tilt-26nov`** (gepusht; **Christian heeft getest en akkoord gegeven op 26 nov: live na de volledige suite**). Bevat ook wip/sessie-26nov. kantelen ijkt alleen bij start/nieuwe opdracht en na draaien. Preview: https://raw.githack.com/SpaceArchitect/luchtruim3d/wip/tilt-26nov/index.html — test: in een bocht een melding laten komen, ▶, bocht moet doorgaan.
- **`wip/spike-mil-26nov`** (gepusht): TRA/TSA-uitleg volgens ENR 5.2 + probe-Action. Meenemen bij de volgende live-gang.
- **`wip/osm-nl-26nov`** (gepusht): Action `data-osm-nl` (17 tegels, compact → branch `data/osm-nl`). Liep 26 nov nog.
- **`wip/heelnl`** (gepusht, nog niet getest): heel NL begin — 259 volumes, FIR-grens, 40 velden, 214 ENR 5.5-terreinen, AIPINFO 90 volumes uit eAIP (aip_check 0 afwijkingen), TMZ-tijden landelijk, klasse A lichter, labeldichtheid, verre volumes niet tekenen, CLAUDE.md-FMC-correctie. De push start ook data-eaip met de bredere paginaset (AD 2 alle velden).
- **`wip/opnieuw`** (gepusht, op basis van wip/tilt-26nov; akkoord Christian 26 nov): fout in missie → meteen stoppen met reden, ↻ Opnieuw of toch door. Bevat ook (26 nov avond, na tests van Christian): bruggen/herkenningspunten niet te groot, spoor knippert niet (z-fighting), labelbudget + meetbug labels. Mee live morgen na de volledige suite (dan deze branch i.p.v. wip/tilt-26nov).
- **`wip/dagelijks`** (gepusht, nog niet getest): dagelijkse uitdaging + test d_daily, zweefkist-klimlimiet (+1000 ft).

## Eerstvolgende sessie (vr 27 nov 22:47) — AIRAC → bugs → rest
1. **Eerst:** regressie 2834 ms bij ▶ op wip/opnieuw (A55) bisecten (LOG 26 nov 22:49); tot dan alleen `wip/tilt-26nov` live (278/278 + p7l 71/71, akkoord Christian). **Daarna live:** volledige suite op `wip/opnieuw` (bevat wip/tilt-26nov) (bevat de 7 bugfixes + kantelfix, akkoord Christian 26 nov) + `wip/spike-mil-26nov` erbij mergen → groen → `release/<datum>` → `main`.
2. Heel NL verder: 5 regio-gebonden tests op `wip/heelnl` (LOG 26 nov) eerst; dan wip/opnieuw erin mergen; data/osm-nl samenvoegen (plaatsen, wegen, rivieren landelijk); eAIP-ophaal verbreden (AD 2 alle velden: torenfrequenties Schiphol/Rotterdam/Eelde/Beek/De Kooy ontbreken nog); `mission_report --fly` na de zweefkist-klimlimiet.
3. Stotter ½ s na missiestart (A55, Christian 26 nov): Christian meet met `?fps=1` (wip/opnieuw); daarna oorzaak gericht fixen.
4. NOTAM/AUP: **weekend 28–29 nov samen met Christian** uitwerken (spike in LOG 26 nov; opties NM B2B, EAD, FAA alleen ter vergelijking).

## Reset-push (Christian 25 nov)
- Eén volledige reset van de weeklimiet, geldig t/m 10 dec. 27 nov–4 dec "heel NL" voorbereiden; vr 4–zo 6 dec sessies; ma 7 dec reset; 7–10 dec heel NL bouwen. Christian test 11–14 dec, vóór Mexico (15 dec).

## Budget
- 1 SP = 1% weeklimiet; herijking 26 nov: **1% ≈ 5,5 M tokens** (ccusage; 25 nov was 7,3 M). Sessie 26 nov: 102,9 M tokens ≈ 19 SP. 26 nov: weeklimiet 91% (Christian), laatste dag vóór de reset → doorwerken tot op.

## Werkwijze-notities
- Volledige suite in twee helften parallel (`--forms desk,p7` en `--forms p7l,se`, eigen `E2E_PORT`).
- Overpass/eAIP/Eurocontrol alleen via GitHub Actions (cloud kan er niet bij). AIRAC-dag: controleer of data/eaip en data/lvnl echt ververst zijn.
- NOTAM: geen NOTAMs in de app tot er een geverifieerde primaire bron is.
- Eindcontrole elke sessie: BACKLOG, STATUS en LOG nalopen.
