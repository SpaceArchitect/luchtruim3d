# Backlog — de enige centrale lijst

*Opgezet 23 nov 2026. Alles wat nog moet of kan staat hier, op prioriteit. STATUS toont alleen de top 5.*
**Regels:** één regel per punt: `[grootte S/M/L/XL] wat — bron, datum → uitwerking`. Klaar = schrappen + één regel in `docs/LOG.md`.
Nieuwe feedback (chat, app, testers) komt hier binnen; issues met label `feedback` worden hier opgenomen en gesloten.

## P0 — gaat altijd voor
- [S] AIRAC-wissel 26 nov (AMDT 12-2026): data ophalen, `build_airspace.py --check`, `aip_check.py`, footer — CLAUDE.md
- [S–M] Kapotte data-actie of live-bug — CLAUDE.md

## P1 — nu (feedback release 22 nov, in deze volgorde) → OPDRACHT-23nov A
0. [S] Live-bug: ballon geland aan de Maas (5 km ZO van Dreumel, wo 11:03) maar opdracht 'Drijf naar de Maas' niet geslaagd; doelbaken zegt nog 1,4 km. Vermoeden: doel = één OSM-stuk van de rivier (`LASTGOAL.pts=f.pts`, regel ±2059) i.p.v. de hele Maas (OSM knipt rivieren op, net als bij de bruggen), en/of REACH 0,5 km bij een lijn te krap. Test: elke rivier-/wegopdracht halen op een willekeurig punt langs de héle rivier — Christian 25 nov (screenshot in chat)
0. [S] Bug: ▶ Start na een afgeronde missie moet direct de volgende missie starten (Start = doorgaan met de huidige missie, of na geslaagd/mislukt de volgende). Nu vlieg je verder zonder opdracht — Christian 25 nov
0. [S] Bug: vario toont altijd de vaste stijgsnelheid (bv. 400 ft/min); moet de werkelijke stijg-/daalsnelheid van het toestel tonen (afhankelijk van hoe hard het stijgt) — Christian 25 nov
1. [M] Missies: progressie easy → medium → lang/moeilijk, sterren, leerdoel, doel altijd zichtbaar (Boyd) — Christian 23 nov → B
   - Opzet (akkoord 23 nov): vaste reeks van ±6 handgemaakte missies (elk één regel: CTR, TMA, P-gebied, TMZ, lier, tijden), daarna een **oneindige generator** met oplopende moeilijkheid (keerpunten, smalle gangen, hoogtebanden, wind, tijdsgebonden gebieden) tot een plafond. Elke gegenereerde missie eerst valideren (er bestaat een route zonder overtreding); leerdoel achteraf uit de geraakte gebieden. Dezelfde generator + datum-seed = dagelijkse uitdaging.

## P2 — daarna
- [L] UX-flow: rondleiding + "Wat is er veranderd?" na AIRAC → keuzescherm (Kaart / Missies / Verkenningsvlucht / Dagelijkse uitdaging), toestelkeuze, menu herindelen; eerst mock — Christian 21+23 nov → C (vervangt OPDRACHT-21nov blok 5)
- [M] Dagelijkse uitdaging fase 1 (seed per datum, lokale score/streak, deeltekst) — Christian 23 nov → D
- [M] Feedbackkanaal route A (Worker → GitHub-issues, e-mail privé, "Vlieg je zelf?") + stappenplan Cloudflare/token voor Christian — Christian 23 nov → I
- [S–M] Vindbaarheid/categorisering "educatie": favicon (2–3 varianten), metadata zonder spel/game, `over.html`, robots/sitemap/JSON-LD, auteur Christian Niemeijer, mailtje voor IT, leverancierslijst — Christian 23 nov → J (klein blok per sessie)
- [S] Cookieloze teller (opties naast elkaar, Christian kiest) + privacytekst — Christian 23 nov → F
- [S] Fleur: tik op een melding = verder; toestel wisselen vindbaar (lost C deels op) — 14 nov
- [S] Keerpunten met Spatie / tik (als nog niet volledig) — OPDRACHT-21nov blok 3
- [S] UX-review door een losse subagent na elk zichtbaar blok — Christian 23 nov → G

- [M] AIRAC-vangnet als GitHub Action: na `data-eaip`/`data-lvnl` automatisch `build_airspace.py --check` op een kopie + `e2e.py -k "missies echt uitvliegen|missiegenerator"`; bij falen een issue met welke missie/poot — Christian 25 nov (zie docs/MISSIES.md)
- [S] Zweefkist: planner max ±1000 ft stijgen zonder thermiek (nu klimt hij 1000 → 3500 ft over Volkel) — 25 nov
## P3 — koers (top 5, even zwaar) en groter werk
- [L] Procedureel landschap: bos, heide, stuifzand, reliëf Veluwe/stuwwal; proef Veluwezoom + Malden als kruis in het bos — Christian 22 nov
- [XL] Kaart naar heel NL (luchtruim landelijk, landschap per regio), daarna BE/DE; eerst data uit `index.html` naar `data/*.json` — Christian 22 nov
- [M] Missies per toestel: lierstart naar Malden, ballon over de Waal met wind, RMZ/CTR-oproepen — Christian 22 nov
- [L] Live NOTAM uit een primaire bron (LVNL → Eurocontrol NOP → EAD Basic); automatische AIRAC-check — Christian 22 nov
- [M] Ballon realistischer (windprofiel, traagheid, dagdeel, missie langs CTR; eerst AIP checken) — OPDRACHT-21nov blok 6
- [M] "Waar ben ik?"-quiz — Christian 23 nov → E
- [S] Test GitHub Issues als backlog-werkvorm (naast dit bestand) — Christian 23 nov

## P4 — open ideeën (niet gepland)
- Nelson Mandelabrug Arnhem en Maasbrug Venlo als herkenningspunt (ontbreken in data/osm herkenning; query uitbreiden)
- LVNL-obstakellaag (masten, windmolens) · hoog contrast in de 3D-scène · IFR-naderingsgebieden (VAC) · doorsnede A→B · legenda/afkortingen · grensstrook DE (eerst labels, DFS-AIP)
- Highscorelijst met bijnaam (alleen na akkoord Christian + privacycheck) → D
- Anonieme terugkeer-gebeurtenissen (pas na juridische check) → F
- IGC-import als lokale tool voor alleen Christian (niet op de site) → E

## Nog te verifiëren (AIP) — zie CLAUDE.md "Vastgelegde kennis"
- Malden: model- en zweefvliegen nooit tegelijk (Christian, lokale afspraak; ENR 5.5 zegt niets) · Nistelrode: zweef + lier op één terrein, gelijktijdigheid onbekend
- Status/klasse van een CTR buiten de openingstijden · Niederrhein TMZ squawk/frequentie (DFS-AIP) · eerste oproep Arrival of Tower

## Open vragen aan Christian
- Vught 's avonds onzichtbaar: niet te reproduceren (EHP29 is H24 en in de app altijd actief). Zie je het nog, stuur dan een screenshot met tijd en modus.
- Verduidelijkingsmails feedback: per stuk goedkeuren of vaste standaardvraag? → I

## Besloten (23 nov)
- Ballon: W/↑ = branden (omhoog), S/↓ = dalen; uitleg per toestel in de sneltoetskaart.
- Verkenningsvlucht: standaard **met** luchtruim; laatste keuze onthouden (localStorage).
- Na de vaste missies: oneindige generator (zie P1-6).

## Niet doen (besluit Christian)
- Voorbeeldcircuit en circuits per zweefveld · thermiek/zweven · MSFS-export · accounts met inloggen · cookiemelding · "spel"/"game" in metadata · IGC op de openbare site · AR-bril (apart project)
