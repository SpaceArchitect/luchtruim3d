# PI-planning 14–20 nov 2026 (7 sprints, één per dag)

**Doel van de PI:** Luchtruim in 3D van "werkende demo regio Eindhoven" naar "nette, gehoste site die vliegers graag gebruiken", met de regio uitgebreid richting Nijmegen–Arnhem.

**Budget:** op vrijdag 20 nov om 17:59 maximaal **80% van de weeklimiet** (stand 13 nov 23:50: 15%). Per sprint ≈ 8–9% van de week.

| Sprint | Dag | Weeklimiet na de sprint (max) |
|---|---|---|
| S1 | za 14 nov | 24% |
| S2 | zo 15 nov | 33% |
| S3 | ma 16 nov | 42% |
| S4 | di 17 nov | 51% |
| S5 | wo 18 nov | 60% |
| S6 | do 19 nov | 69% |
| S7 | vr 20 nov (klaar vóór 17:00) | 78% |

## Werkwijze per sprint
1. Elke sprint start als **nieuwe chat** (geplande taak, 09:13). Christian geeft daar feedback.
2. Begin: lees `02-instructies.md`, `06-backlog.md`, het laatste sprintverslag en dit plan; **lees de weeklimiet af** (Chrome → claude.ai/settings/usage). Ligt het verbruik boven het maximum van de vorige sprint, maak de sprint kleiner.
3. Bouwen in de repo `SpaceArchitect/luchtruim3d` (clone, `index.html`), testen met echte klikken (`tools/shot.py`, Playwright).
4. Kanbanbord bijwerken: https://claude.ai/artifact/6ogPFEojFzEi7WxTrp2H3m (kaartjes `cards/…`).
5. **Eén panelronde** (klein model, screenshots).
6. **Eindtest** in Chrome op https://spacearchitect.github.io/luchtruim3d/ (of luchtruim3d.nl): desktop en mobiel (Playwright Pixel 7), met echte klikken.
7. Publiceren: push naar GitHub, ★1-artifact bijwerken, `index.html` naar `Documenten\luchtruim3d`.
8. Sprintverslag `claude/sprints/<datum>.md`, backlog bijwerken, weeklimiet noteren.
9. Stoppen bij het maximum uit de tabel.

## Sprintdoelen

**S1 – za 14 nov: Afwerking hosting + panel 11**
- **Feedback Christian (14 nov 00:05) — eerst doen:**
  1. Vakje "Sturen door de telefoon te kantelen" doet niks: testen op GitHub Pages op een echte telefoon (Christian), oorzaak zoeken (permissie iOS/Android, https, deviceorientation-events, ijkpunt), duidelijke melding als het niet kan.
  2. Mobiel: opdrachttekst past net niet → mag over twee regels (niet afkappen).
  3. Dalen ziet er te overdreven uit (camera/neus); stijgen is goed. Daal-effect ongeveer halveren.
  4. Standaard zichtbare luchtruimtypen herzien: paradropzones, dronegebieden (UAS/TSA), paraglide-/schermvliegvelden en ander relevant luchtruim moeten standaard aan. Inventariseer alle LVNL-lagen in de data, kies per type met reden (log), en check welke lagen we nog niet hebben (bijv. schermvliegterreinen/lierlocaties: bron uitzoeken, LVNL VFRchart/Miscellaneous of AIP).
- Domein luchtruim3d.nl: DNS controleren, `CNAME` in repo, HTTPS (samen met Christian).
- Panel 11: labels bovenaan/onderaan niet onder knoppen en kaartjes; RT-kaart mobiel compacter of inklapbaar; profielpaneel "Boven de sonde" mobiel inklapbaar; modusknop niet over twee regels.
- Mooiere toestelmodellen (zweef/motor) en schaduw in de vorm van het toestel.

**S2 – zo 15 nov: Toegankelijkheid**
- **Eerst de norm uitzoeken en toetsen** (verzoek Christian/Boyd, 13 nov): waarschijnlijk WCAG 2.2 niveau AA (in Europa via EN 301 549; in NL de standaard voor digitoegankelijkheid). Zoek uit welke norm geldt, maak een checklist van de relevante succescriteria (contrast, toetsenbord, labels, tekstgrootte, beweging, touch-doelen) en toets de site; leg de uitkomst vast in het sprintverslag en het project.
- Kleurenblind: ATZ vs P/R/D, klasse B/C/D (patroon of letter als tweede kanaal).
- Hoog contrast ook in de 3D-scène.
- Grote letters overal, schermlezerlabels nalopen.

**S3 – ma 16 nov: RT en AIP-correctheid**
- RT-fraseologie toetsen aan AIP (GEN 3.4, AD 2.22 EHEH) en KNVvL-lesstof; tweestaps-oproep; meldpunten.
- AIP-checks uit backlog: squawk in CTR, eerste oproep Tower/Arrival, Niederrhein TMZ (DFS-AIP).
- Legenda/afkortingen kort terug als "?"-knop.

**S4 – di 17 nov: Spelplezier**
- Feedback Christian 14 nov: missies zijn te makkelijk en te kort → langere routes, meerdere tussendoelen, uitdagingen waarbij je echt om luchtruim heen moet plannen.
- Reeks opdrachten met sterren en voortgang (localStorage), dagelijkse uitdaging.
- "Nieuwe opdracht" na geslaagd/gefaald verfijnen, score bij foutloos vliegen.

**S5 – wo 18 nov: Regio Nijmegen–Arnhem (data)**
- LVNL-lagen en OSM ophalen via Chrome voor de nieuwe bbox, pijplijnscript in de repo (`tools/`).
- Luchtruim tonen, controleren tegen AIP (SUP 03/2022 Nieuw Milligen).

**S6 – do 19 nov: Regio Nijmegen–Arnhem (landschap)**
- Herkenningspunten (Waalbrug, De Oversteek), steden en water, opdrachten in de nieuwe regio.
- Prestaties op mobiel bewaken.

**S7 – vr 20 nov: Doorsnede + PI-afsluiting**
- Doorsnede langs een lijn (verticaal profiel A→B).
- Stabiliseren, volledige eindtest, PI-review voor Christian, voorstel volgende PI.

## Roadmap na deze PI (Christian, 13 nov)
- **Elke week één regio erbij**, tot heel Nederland gedekt is (na Nijmegen–Arnhem bijvoorbeeld Utrecht/Gelderse Vallei, Randstad/Schiphol, Noord, Zeeland/West-Brabant, Limburg-Zuid, Twente/Oost). Datapijplijn uit S5 herbruikbaar maken, zodat een nieuwe regio vooral data ophalen + controleren tegen de AIP is.

## Buiten de PI (wachten op anderen)
- Antwoord van LVNL op licentiemail (concept staat in Gmail; Christian verstuurt).
- Contact met Frank (vfr3d.nl) over samenwerking.
