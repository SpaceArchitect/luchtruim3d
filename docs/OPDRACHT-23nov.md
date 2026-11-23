# Opdracht 23 nov: game-ervaring, feedback release 22 nov, UX-flow, privacy

Input van Christian (23 nov 2026). Vervangt/verfijnt blok 5 (startflow) van `docs/OPDRACHT-21nov.md`.
Werk het af over meerdere sessies; wat niet past, blijft met prioriteit in STATUS.

## A. Feedback release 22 nov — eerst (volgorde A4 → A2 → A3 → A1 → A5)
**Goed, niet aanpassen:**
- **Kantelen (mobiel) werkt goed → feature AFGEROND.** Alleen nog aankomen bij een bug; regressietests blijven.
- **Sneltoetskaart op desktop:** goed, behouden.

**Beter:**
1. **Herkenningspunten kloppen deels niet.** Voorbeeld: de brug bij de A50 staat een kwartslag gedraaid. → Alle modellen nalopen op oriëntatie en positie. Richting uit OSM-weg- of rivier-as halen in plaats van een vaste rotatie, en elk punt vergelijken met de luchtfoto. Test: brug-as ⟂ rivier en ∥ weg.
2. **Lieren (para's, schermvliegers):** nu een grote cirkel met een kleinere cilinder erop; oogt vreemd. → **Eén cilinder** met de straal en hoogte uit de AIP (ENR 5.5). Bron per terrein in LOG.
3. **Malden: modelvliegveld overlapt deels met het zweefvliegveld.** Christian weet hier niets van. → Herkomst uitzoeken (ENR 5.5, OSM of openAIP?). Staat het niet in de AIP of klopt de positie niet: corrigeren of weghalen. Klopt het wel: Christian uitleggen wat er speelt.
4. **Vught penitentiaire inrichting 's avonds onzichtbaar**, terwijl het volgens Christian 24/7 verboden is. → Tijden in AIP ENR 5.1 controleren en het tijd/dagdeel-filter repareren. Test: H24-gebieden altijd zichtbaar, op elk tijdstip.
5. **Missies veel te makkelijk** → zie B.

## B. Doelstelling 1: betere game-ervaring
Christian: "missies uitdagender, verloop van makkelijk naar moeilijk, intuïtievere besturing, schonere interface, mooiere graphics; de rest vul je zelf in."
- **Progressie:** missie 1 easy (opwarmen), missie 2 medium (één kleine instinker), 3+ langer en moeilijker met meerdere keerpunten en uitdagingen. De moeilijkheid stijgt langzaam: beginners niet afschrikken, ervaren spelers vasthouden. Christian haakt nu na een paar weken af.
- **Moeilijkheidsknoppen:** meer keerpunten, smalle gangen tussen gebieden, hoogtebanden (onder TMA, boven CTR), tijdslimiet, wind, gebieden met activiteitstijden, klaring nodig, dagdeel/zicht.
- **Score en voortgang:** sterren per missie (gehaald / geen overtreding / binnen tijd), voortgang in localStorage (try/catch), volgende missie open na de vorige (zacht: overslaan mag). Elke missie heeft één leerdoel, dat na afloop kort wordt uitgelegd.
- **Besturing:** intuïtief en gelijk voor alle toestellen; direct gevoel, vloeiende camera.
- **Interface:** minimaal; meldingen ruimen zichzelf op; doel en volgend keerpunt altijd vindbaar (markering + pijl aan de schermrand).
- **Graphics:** mooier terrein, lucht en licht en herkenbare modellen; volumes strak en leesbaar. De framerate op mobiel gaat voor.
- **Toets:** wordt het leuker om te blijven spelen én snapt een leerling-vlieger het luchtruim er sneller door?

## C. UX-flow (eerst schets/mock aan Christian laten zien)
1. **Rondleiding in kaartmodus**, met "Sla over" altijd zichtbaar.
   - Nieuwe bezoeker: de basisrondleiding van ±1 min.
   - Terugkerende bezoeker, eerste bezoek na een nieuwe AIRAC: rondleiding **"Wat is er veranderd?"** langs de gewijzigde gebieden, één zin per gebied (laatst geziene AIRAC in localStorage). Geen relevante wijzigingen: overslaan.
   - Anders direct naar het keuzescherm. Beide rondleidingen staan ook in het menu.
2. **Keuzescherm:** Kaart verkennen · Missies (→ toestel: zweef/motor/ballon) · Verkenningsvlucht (met of zonder luchtruim → toestel) · Dagelijkse uitdaging.
3. De sneltoetskaart (desktop) blijft; op mobiel een gelijkwaardige korte uitleg.
4. Vanuit elke modus kom je met één knop terug naar het keuzescherm.

## D. Dagelijkse uitdaging (favoriet van Christian)
- Elke dag één missie die voor iedereen hetzelfde is, gemaakt uit de datum (seed), zonder server. De moeilijkheid wisselt per weekdag.
- Score: tijd + strafpunten voor overtredingen + bonus voor een nette route.
- **Fase 1:** score en streak alleen lokaal; deelknop met tekst à la Wordle ("Luchtruim3d #142: 3 ⭐, 0 overtredingen").
- **Geen accounts met inloggen** (besluit Christian). Een openbare highscorelijst met alleen een bijnaam komt pas na Christians akkoord en een privacycheck.

## E. Later / geparkeerd
- **"Waar ben ik?"-quiz** (potentie): stil op een plek, luchtruim verborgen, meerkeuze (welk luchtruim, klaring nodig, max. hoogte), daarna uitzoomen met de volumes en uitleg. Rondes van 10, steeds moeilijker.
- **IGC-import:** niet op de site (overlap met vfr3d.nl). Hooguit een lokale tool voor alleen Christian.
- **MSFS-export:** te niche, niet uitwerken.

## F. Privacy en analytics (besluit Christian)
Analytics **alleen anoniem, zonder cookiemelding en binnen AVG en Telecommunicatiewet**. Bij twijfel de strengste variant.
- **Functionele localStorage** (rondleiding gezien, AIRAC, voortgang, streak, instellingen) blijft op het apparaat; geen ID's.
- **Stap 1:** een cookieloze teller (geen fingerprinting, geen IP-opslag, EU- of eigen hosting, niets naar derden). Zet GoatCounter/Plausible/Simple Analytics/Umami/Cloudflare naast elkaar; Christian kiest. Privacytekst onder Over.
- **Stap 2** (anonieme gebeurtenissen zoals "terugkerend ja/nee" of "uitdaging voltooid", zonder ID) pas na een juridische check (Tw art. 11.7a geldt voor álle opslag op het apparaat). Mag het niet, dan alleen de dagtelling.

## G. UX-review
Na elk zichtbaar blok: een losse reviewer-subagent die de bouw niet heeft gezien. Die loopt de flow door op screenshots (desktop + mobiel staand/liggend) met de testpersona's. Checklist: binnen 2 min gevonden wat ik zoek? Wat is overbodig? Waar twijfel ik? Is de tekst kort genoeg? Bevindingen gaan in LOG; Christian blijft de eindtester.
