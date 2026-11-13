# PI-planning 14–20 nov 2026 (7 sprints, één per dag) — herzien 14 nov 00:15

> **LEIDEND:** deze planning is herzien na feedback van Christian (14 nov) en een korte panelronde. Wijkt het sprintdoel hieronder af van de tekst in de geplande taak, **volg dan dit document**.

**Doel van de PI:** Luchtruim in 3D van "werkende demo regio Eindhoven" naar een nette, gehoste site waarop je **alle gevaren en mogelijke conflictgebieden in één oogopslag** ziet, die goed werkt op de telefoon, en die vliegers graag gebruiken. Plus de eerste extra regio.

**Leidend principe (Christian, 14 nov):** alles wat op de 2D ICAO/VFR-kaart staat, moet uiteindelijk ook in de app zichtbaar zijn. Gevaren/conflictgebieden standaard aan — **daar horen ook gecontroleerd luchtruim klasse A/B/C/D (klaring nodig of verboden voor VFR) en P/R/D bij**; de rest uit te zetten; labels vervagen geleidelijk op afstand zodat het niet te druk wordt.

**Budget:** op vrijdag 20 nov om 17:59 maximaal **80% van de weeklimiet** (stand 13 nov 23:50: 15%). Let op: andere geplande taken van Christian (CVZ za, RAM-mail zo, LinkedIn ma) tellen ook mee.

| Sprint | Dag | Thema | Weeklimiet na de sprint (max) |
|---|---|---|---|
| S1 | za 14 nov | Telefoon & besturing + domein + LVNL-mail | 24% |
| S2 | zo 15 nov | Alles van de 2D-kaart (1): inventaris en gevaren standaard aan | 33% |
| S3 | ma 16 nov | Alles van de 2D-kaart (2) + toegankelijkheid (WCAG 2.2 AA) | 42% |
| S4 | di 17 nov | Radiogesprek en AIP-correctheid | 51% |
| S5 | wo 18 nov | Spelplezier: langere, moeilijkere missies | 60% |
| S6 | do 19 nov | Regio Nijmegen–Arnhem | 69% |
| S7 | vr 20 nov (klaar vóór 17:00) | Doorsnede A→B + stabiliseren + PI-review | 78% |

Panelinbreng (14 nov, 5 persona's): hoog = kantelsturing, mobiele fixes, WCAG, gevaren in één oogopslag (met tweede kanaal naast kleur); midden = dalen, RT/AIP, spelplezier, doorsnede, domein; laag = nieuwe regio, toestelmodellen. Christian wil elke week een regio → één regio in S6, de rest op de roadmap.

## Werkwijze per sprint
1. Elke sprint start als **nieuwe chat** (geplande taak, 09:13). Christian geeft daar feedback.
2. Begin: lees `02-instructies.md`, `06-backlog.md`, het laatste sprintverslag en dit plan; **lees de weeklimiet af** (Chrome → claude.ai/settings/usage). Ligt het verbruik boven het maximum van de vorige sprint, maak de sprint kleiner.
3. Bouwen in de repo `SpaceArchitect/luchtruim3d` (clone, `index.html`), testen met echte klikken (`tools/shot.py`, Playwright).
4. Kanbanbord bijwerken: https://claude.ai/artifact/6ogPFEojFzEi7WxTrp2H3m (collectie `cards`).
5. **Eén panelronde** per sprint (klein model).
6. **Eindtest** in Chrome op de live site (luchtruim3d.nl of spacearchitect.github.io/luchtruim3d): desktop en mobiel (Playwright Pixel 7), met echte klikken.
7. Publiceren: push naar GitHub, ★1-artifact bijwerken, `index.html` naar `Documenten\luchtruim3d`.
8. Sprintverslag `claude/sprints/<datum>.md`, backlog bijwerken, weeklimiet noteren.
9. Stoppen bij het maximum uit de tabel. Niet alles hoeft af: wat niet past, gaat met prioriteit terug naar de backlog.

## Sprintdoelen

**S1 – za 14 nov: Telefoon & besturing + domein + LVNL-mail**
- Kantelsturing ("Sturen door de telefoon te kantelen" doet niks): oorzaak zoeken op GitHub Pages met Christians telefoon (permissie iOS/Android, https, deviceorientation, ijkpunt); duidelijke melding als het niet kan.
- Mobiel: opdrachttekst mag over twee regels; RT-kaart en profielpaneel "Boven de sonde" compacter/inklapbaar; labels niet onder knoppen/kaartjes; modusknop niet over twee regels.
- Dalen ongeveer half zo sterk in beeld (stijgen is goed).
- Domein luchtruim3d.nl live: DNS-zone bij OVHcloud (4 A-records 185.199.108-111.153, CNAME www → spacearchitect.github.io.), CNAME-bestand in repo, Enforce HTTPS; automatische verlenging aanzetten (Christian).
- LVNL-mail: concept in Gmail nalopen met Christian (URL luchtruim3d.nl), Christian verstuurt.
- Optioneel: Christian laat EasyVFR zien als inspiratie voor S2/S3 (welke lagen, hoe decluttering).

**S2 – zo 15 nov: Alles van de 2D-kaart (1)**
- Inventaris: legenda van de ICAO-kaart 1:500.000 / LVNL VFR chart viewer naast wat de app toont. Welke LVNL-lagen hebben we, welke niet (Airspaces, Miscellaneous, Routes, Aerodrome, Obstacles…)? Lijst in het verslag.
- Standaard aan: paradropzones, dronegebieden (UAS/TSA), schermvlieg-/lier-/ULV-terreinen en andere gevaren die op de 2D-kaart staan (bron: LVNL-laag of AIP), laagvlieggebieden waar relevant. Per type vastleggen waarom aan/uit.
- Ontbrekende lagen ophalen via Chrome (same-origin op geoservices.lvnl.nl).
- Decluttering: labels vervagen geleidelijk op afstand; lagen per groep uit te zetten.

**S3 – ma 16 nov: Alles van de 2D-kaart (2) + toegankelijkheid**
- Restant S2 (obstakels/masten uit LVNL-laag Obstacles, symbolen voor nieuwe lagen).
- **Norm uitzoeken en toetsen** (Christian/Boyd): WCAG 2.2 niveau AA (EN 301 549). Checklist van relevante succescriteria (contrast, toetsenbord, labels, tekstgrootte, beweging, touch-doelen) en de site toetsen; uitkomst vastleggen.
- Gevaren niet alleen op kleur: patroon/randstijl/letter (kleurenblind: ATZ vs P/R/D, klasse B/C/D). Hoog contrast ook in de 3D-scène.

**S4 – di 17 nov: Radiogesprek en AIP-correctheid**
- RT-blok toetsen aan eAIP (GEN 3.4, EHEH AD 2.22) en KNVvL/zweefvliegopleiding-lesstof; korte eerste oproep (tweestaps); positie via VFR-meldpunt.
- AIP-checks uit de backlog: squawk in CTR, eerste oproep Tower/Arrival, Niederrhein TMZ (DFS-AIP).
- Korte legenda/"?"-knop.

**S5 – wo 18 nov: Spelplezier**
- **Idee Christian (14 nov): sturen door te kantelen als hoofdbesturing op telefoon/tablet, liggend vasthouden, minder knoppen (ook looping via kantelen).** Aanpak: S1 laat kantelen eerst überhaupt werken en laat het panel kort reageren. Is dat positief, dan in S5 een **liggende kantelmodus** als prototype: telefoon dwars, kantelen = sturen/stijgen/dalen, looping door de telefoon ver naar je toe te kantelen, knoppen ingeklapt. Knoppen blijven altijd beschikbaar als alternatief (WCAG 2.5.4 'Motion Actuation': bewegingsbesturing moet ook via de interface kunnen en uit te zetten zijn; nodig voor o.a. Kees en mensen met een motorische beperking). Wordt het een grote ombouw, dan naar de volgende PI.
- Missies zijn nu te makkelijk en te kort (Christian): langere routes, tussendoelen, opdrachten waarbij je om luchtruim heen moet plannen (onder TMA door, om CTR heen, paradropzone vermijden).
- Sterren en voortgang (localStorage), dagelijkse uitdaging.

**S6 – do 19 nov: Regio Nijmegen–Arnhem**
- Data via Chrome (LVNL + OSM) voor de nieuwe bbox; ophaal-/bouwscript herbruikbaar in `tools/` (basis voor "elke week een regio").
- Luchtruim + gevaren (zelfde lagen als S2/S3) + belangrijkste herkenningspunten (Waalbrug, De Oversteek, rivieren); controle tegen AIP (SUP 03/2022 Nieuw Milligen).
- Prestaties op mobiel bewaken.

**S7 – vr 20 nov: Doorsnede + stabiliseren + PI-review**
- Doorsnede langs een lijn (twee punten tikken → verticaal profiel).
- Open bugs uit S1–S6; volledige eindtest.
- PI-review `claude/09-pi-review-14-20nov.md` en voorstel volgende PI.

## Backlog (niet in deze PI, tenzij er ruimte is)
- Mooiere toestelmodellen en schaduw in toestelvorm (panel: laag).
- Live NOTAMs (eigen server nodig).
- Contact met Frank (vfr3d.nl): samenwerken, naar elkaar verwijzen, samen naar LVNL.

## Roadmap na deze PI (Christian, 13 nov)
- **Elke week één regio erbij**, tot heel Nederland gedekt is (na Nijmegen–Arnhem bijvoorbeeld Utrecht/Gelderse Vallei, Randstad/Schiphol, Noord, Zeeland/West-Brabant, Zuid-Limburg, Twente/Oost).
