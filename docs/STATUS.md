# Status — lees dit eerst

*Bijgewerkt: 27 nov 2026, 19:00 (stotter naar prio 1, Christian). Docs van wip/sessie-26nov staan nu ook op main. Backlog: **`docs/BACKLOG.md`** (enige lijst). Volgorde: **AIRAC → bugs → rest** (Christian 25 nov).*

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

## Eerstvolgende sessie (vr 27 nov 22:47) — EERST DE STOTTER (Christian 27 nov)
0. **Stotter bij ▶ = prioriteit 1.** Meting Christian 27 nov (Galaxy A55, raw.githack `wip/opnieuw`, `?fps=1`, glider-missie 'Vlieg naar Meteren (1/3)', ×5): **na ▶ max 2834 ms @ 0 ms, tijdens ijken**; beeld staat ~3 s stil, sinds 26 nov (eerst 112 ms). **Regressie** door de twee maatregelen van 26 nov zelf (labels in batch meten, `renderer.compile` met alle verborgen objecten zichtbaar) — LOG 26 nov 22:49. **Eerste stap: bisecten** (commit vóór 'Stotter bij ▶' = 112 ms): previewlinks per stap, één maatregel per meting.
   - Vooronderzoek 27 nov (headless, swiftshader, 4× CPU-rem): **niet te reproduceren**. Geen nieuwe shaderprogramma's, texture-uploads of zware JS na ▶ (ook gen-glider-3 met 2 keerpunten). `misVerify` per vaste missie < 0,5 s; uitschieter `misStart` ballon `bmaas` 2,3 s (synchroon).
   - **Daarna (de oorspronkelijke 112 ms):** Chrome Android (ANGLE/Vulkan) maakt GPU-pipelines pas bij de eerste échte draw; `renderer.compile()` helpt daar niet.
   - **Aanpak:** (1) `?fps=1` uitbreiden: JS-tijd per frame (sim/render/labels) naast de frame-gap → GPU-stall of JS? (2) opwarmen tijdens de startmelding: één frame álles (ook verborgen: doel, schaduw, verre volumes) echt naar het canvas tekenen met scissor 1×1 px vanuit de vliegcamera; (3) synchrone missieberekeningen (`misStart`/`misVerify`/`nextMission` in de meldingstekst) in plakjes of vooraf; (4) niet aantoonbaar opgelost → klein laadscherm 'Luchtruim laden…' (akkoord Christian 26+27 nov).
   - Bug-les (CLAUDE.md): waarom glipte dit door? Headless meet geen GPU-pipelines → vastleggen wat de suite wél kan bewaken (JS-tijd per frame, synchrone berekeningen > 50 ms).
   - Telefoongedrag is headless niet te bewijzen: **niet live**. **Christian test za 28 nov 's ochtends (mobiel, A55)** — niet op hem wachten:
     zet vanavond kant-en-klare previewbranches klaar, elk met `?fps=1` (incl. JS-tijd per frame), en zet de links + wat hij per link doet in STATUS en het eindbericht:
     `wip/stotter-a` = wip/opnieuw zónder labels-in-batch · `wip/stotter-b` = zónder compile-opwarmen · `wip/stotter-c` = zonder beide (+ evt. `-d` met 1×1-scissor-opwarmen).
     Daarna **verder met ander werk** (punt 2 heel NL en de rest van BACKLOG); niets op `wip/opnieuw` live.
1. **Live (pas na de stotter — `wip/opnieuw` niet live met de regressie erin):** volledige suite op `wip/opnieuw` (bevat wip/tilt-26nov: 7 bugfixes + kantelfix, akkoord Christian 26 nov) + `wip/spike-mil-26nov` mergen → groen → `release/<datum>` → `main`. Stotterfix pas mee als Christian op de A55 akkoord geeft.
2. Heel NL verder: 5 regio-gebonden tests op `wip/heelnl` (LOG 26 nov) eerst; dan wip/opnieuw erin mergen; data/osm-nl samenvoegen; eAIP-ophaal verbreden (AD 2-torens); `mission_report --fly` na de zweefkist-klimlimiet.
3. NOTAM/AUP: **weekend 28–29 nov samen met Christian** uitwerken (spike in LOG 26 nov).

## Reset-push (Christian 25 nov)
- Eén volledige reset van de weeklimiet, geldig t/m 10 dec. 27 nov–4 dec "heel NL" voorbereiden; vr 4–zo 6 dec sessies; ma 7 dec reset; 7–10 dec heel NL bouwen. Christian test 11–14 dec, vóór Mexico (15 dec).

## Budget
- 1 SP = 1% weeklimiet; herijking 26 nov: **1% ≈ 5,5 M tokens** (ccusage; 25 nov was 7,3 M). Sessie 26 nov: 102,9 M tokens ≈ 19 SP. 26 nov: weeklimiet 91% (Christian), laatste dag vóór de reset → doorwerken tot op.

## Werkwijze-notities
- Volledige suite in twee helften parallel (`--forms desk,p7` en `--forms p7l,se`, eigen `E2E_PORT`).
- Overpass/eAIP/Eurocontrol alleen via GitHub Actions (cloud kan er niet bij). AIRAC-dag: controleer of data/eaip en data/lvnl echt ververst zijn.
- NOTAM: geen NOTAMs in de app tot er een geverifieerde primaire bron is.
- Eindcontrole elke sessie: BACKLOG, STATUS en LOG nalopen.
