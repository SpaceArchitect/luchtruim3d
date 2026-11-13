
## 13 nov 2026 — sprint 1 (opruimen en correctheid) + stukje sprint 3

**Bouwomgeving.** De map `vfr3d-build/` van eerdere sessies bestaat niet meer in de cloud (elke sessie start leeg). Bron voor deze sprint = de gepubliceerde ★1-pagina zelf (index.html, 183 KB). Testen met een nieuwe headless Chrome-harnas (`/home/claude/h/shot.py`, lokale three.js 0.160). **Les:** bouwbestanden voortaan na elke sprint ook in het project of op Christians pc bewaren.

**Let op:** de gepubliceerde ★1 bevatte de wijziging "squawk 7000 alleen bij TMZ" (10 nov 22:00) nog niet; die is nu opnieuw gebouwd.

**Gebouwd (★1):**
- *Weergave-paneel:* weg zijn de knop "Laag", de hoogteplaat (ook uit vliegmodus: verwarde tijdens vliegen), de missie "Land op Eindhoven", de afkortingenlijst. Voetnoot alleen nog bronnen (LVNL, OSM). "Toon tot 5000 ft" → "FL065 (laag luchtruim)".
- *Tekst overdrijving:* "pannenkoek" vervangen door "3000 ft is maar 0,9 km hoog, terwijl dit gebied 100 km breed is…".
- *Squawk 7000* alleen nog bij TMZ ("📡 Transponder aan · sqk 7000"); bij CTR/TMA alleen de frequentie.
- *Waarschuwingen:* afstand = ~8 s schermtijd vooraf (min 1,5 km, max 20 km), dus verder vooruit bij hoog tempo. Nieuw: waarschuwing bij stijgen/dalen een gebied in ("⛔ Boven je vanaf 1500 ft: TMA 1 Eindhoven (C) · klaring nodig"). Opnieuw waarschuwen als een gebied ~4 s niet meer binnen of vóór je ligt.
- *Opdrachten:* doelen minstens 10 km van de rand; "Volg de A58 richting Gilze" (plaats in de vliegrichting) i.p.v. "(5 km)"; live "nog X km". **Missie geslaagd/gefaald** bij aankomst (≤1,5 km): gefaald met reden bij verboden gebied, para-/dronegebied of CTR/TMA zonder klaring.
- *Hoog contrast:* labels zonder gloed (text-shadow uit), scherp zwart/wit.
- *Geknipper randlijnen:* (1) staande lijnen alleen nog op echte hoeken (>40°, zijden >400 m) i.p.v. op elk punt van bochten/grenzen; (2) gedeelde lijnstukken tussen buurgebieden in dezelfde groep maar één keer getekend (sterkste klasse wint, E verliest). Onderplaat-arcering in kaartmodus lichter (0,5 → 0,3), want zonder hoogteplaat werd alles gearceerd.
- *Bijknippen:* alle luchtruimvlakken (paradrop, Rucphense Heide, TSA) geknipt tot het kaartgebied (Sutherland-Hodgman). Hoogspanning was al punt-voor-punt gefilterd.
- *Namen:* bebouwing (OSM) wordt alleen nog getekend als er een stad of dorp in ligt (15 steden + ~80 dorpen met coördinaten); dorpen krijgen een klein label (binnen ~45 km camera-afstand op de kaart, 14 km tijdens vliegen). "x km NO van …" gebruikt nu ook dorpen. De Peel (EHDP) heeft een veldlabel.
- *Water Amercentrale:* het naamloze watervlak van 154 km² (Amer + Bergsche Maas + Biesbosch samengesmolten door het rasteren) is verwijderd. Amer en Bergsche Maas blijven als rivierlint; benoemde Biesbosch-plassen blijven.
- *Plassen (Leukermeer):* label op het binnenste punt van de plas (niet het midden van de bbox), zichtbaar binnen 12 km tijdens vliegen.
- *GLV VIII:* label toonde "grond – grond" (bovengrens 150 ft AGL werd als "grond" geschreven). Nu "grond – 150 ft AGL". AIP ENR 5.2 (§1 Military low flying areas): GLV VIII (De Peel) GND – 150 ft AGL, helikopter-oefenvluchten, VMC, MON 0700 (0600) – FRI 1600 (1500) UTC. Geen klaring nodig; uitlegtekst aangepast.
- *Mobiel:* hoogteband in kaartmodus schoof onder de knoppen (transform) — opgelost.

**Bronnen gecheckt:** eAIP ENR 5.2 (LVNL, via zoekmachine; editie 2016-pagina nog geldig in AIRAC 2024). eAIP zelf was via WebFetch niet bereikbaar.

**Panelronde 9 (5 persona's, screenshots), direct doorgevoerd:**
- Eén opbouw voor waarschuwingen: "🔶 Over 1,5 km: CTR Eindhoven (D) · klaring nodig" / "⛔ … verboden". ⛔ alleen nog bij verboden; klaring = 🔶 (ook de status-tag "🔶 KLARING" en de opstijgmelding).
- Doelpijl in de opdrachtregel (⬆ ↗ ➡ … t.o.v. je koers) en melding "↩ Doel gemist: draai om" zodra de afstand 2 km boven het minimum oploopt.
- Hoog contrast: grondarcering van zwevend luchtruim bijna uit (0,08).
- Tag "ZWEEF" → "ZWEEFGEBIED" (leek op toesteltype); kleurvakje bij CTR/TMA in Lagen toont nu de klassekleuren (leek op een tweede vinkje).
- Dorpslabels met "•" (één stijl met steden); op de telefoon in kaartmodus geen dorpslabels.

**Panel 9 — nog open (naar backlog):** "Nieuwe opdracht"-knop in de geslaagd/gefaald-melding (S); sonde op mobiel compacter, kolom niet afkappen, kompas niet over de lijst (M); in de sondekolom valt Nieuw Milligen TMA sector D (E) weg achter TMA 1 (S); scheidingsstreep ft/FL in de kolom (S); Weergave-paneel valt over de titel en toont "Vliegen"-sectie in kaartmodus (S); statusblok tijd bedekt labels (S); CTR/TMA C/TMA B allemaal blauw voor kleurenblinden (M, 🧪).

## 13 nov, 19:40–19:55 — tweede deel sprint (Christian: "er is budget over")

**Gebouwd:**
- Knop "🎯 Nieuwe opdracht" in de melding geslaagd/gefaald (nieuwe willekeurige start met hetzelfde toestel).
- Weergave-paneel op desktop onder de titel; sectie "Vliegen" alleen in vliegmodus.
- Mobiel: sonde-lijst max 36% hoog, zonder uitlegregel; noordpijl linksboven. Sondekolom: stippellijn op 3000 ft (overgang ft → FL), tekst alleen als de kolom breed genoeg is.
- Sondekolom "mist" Nieuw Milligen TMA sector D (E) boven Eindhoven: geen bug. Volgens EXCL (AIP: overlappend deel uitgezonderd) geldt die daar niet; de lijst toont hem met "Geldt hier niet overal".
- **RT-blok "Klaring aanvragen"** (sprint 3, suggestie Dinant): knop in de klaringswaarschuwing → kies je eerste oproep uit 3 (goed / station en roepnaam omgedraaid / zonder toestel-positie-hoogte) → bij fout uitleg en opnieuw → ATC: klaring (65%) of weigering met reden (traffic / expect entry in 10 minutes / runway change in progress); zelfde antwoord bij direct opnieuw vragen, na ~45 s opnieuw proberen. Na klaring: **readback** kiezen (goed / "Roger" / zonder hoogte). Pas na een goede readback telt het gebied niet meer als fout in de missie (tag "✓ KLARING GEKREGEN"). Ander luchtruim (bv. TMA erboven) blijft waarschuwen.
  - Positie in de oproep = dichtstbijzijnd VFR-meldpunt (<8 km, bv. "3 km southwest of WHISKEY"), anders dichtstbijzijnde plaats. "VFR glider/Cessna 172", "altitude 1000 ft", "request to enter control zone for crossing". Alles gemarkeerd "vereenvoudigd". Uitleg dat je op een drukke frequentie eerst kort oproept.
  - **Nog te checken (AIP/KNVvL-lesstof):** volledige vs. korte eerste oproep, exacte klaringstekst (in werkelijkheid vaak met route/meldpunt, QNH en squawk), fraseologie voor zweefvliegers.

**Panelronde 10** (RT-blok): eerste versie was monospace, 60% weigering, geen readback, "▶ = laat maar". Doorgevoerd: readback-stap, knop "Sluiten", weigering 35% met reden, proportioneel lettertype met de delen als blokjes, harde spaties in "1000 ft", positie via meldpunt.
**Panel 10 — nog open:** "dicht" (tijdbalk) vs "niet actief" (kaartlabel) gelijktrekken (S); modusknop "Kaart"/"Vliegen" leest als huidige modus → "Naar kaart" (S); sondekolom op mobiel dekt kaartlabels af (S); ATZ-paars vs P/R/D-roze en B/C/D-blauw lastig voor kleurenblinden (M, patroon of letter); kop van de sonde in hoofdletters leest slecht (S).
