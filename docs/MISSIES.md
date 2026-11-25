# Missies — reeks, meting en generator

*25 nov 2026. Bron van de volgorde: `python tools/mission_report.py --fly` (elke missie écht uitgevlogen) en `--gen N` (generator).*

## Spelregels (Christian 23 + 25 nov)
- Per toestel **6 vaste missies**, van makkelijk naar pittig (2 · 2 · 2). Elke missie heeft **één leerdoel** (🎓), na afloop uitgelegd.
- Daarna **oneindig gegenereerde uitdagingen**, oplopend moeilijk.
- **Nooit een onmogelijke missie.** Een gegenereerde uitdaging komt pas bij de speler als de 3D-routeplanner een route
  **zónder klaring** vindt: om een gebied heen, eronder (dalen) of eroverheen (stijgen), met ±150 ft marge en 0,3–0,6 km afstand.
  Vaste missies met het doel ín een CTR (Lichtstad, Terlet, Over de Rijn, Langs de Peel) leren juist klaring vragen; daar is
  opnieuw vragen na een weigering altijd raak, dus ook die zijn 100% haalbaar.
- Sterren: ⭐ doel gehaald · ⭐ zonder overtreding · ⭐ strakke route (≤ 1,35× de rechte lijn; ballon 1,6×). Lokaal opgeslagen.

## Gemeten zwaarte (route uitgevlogen, 25 nov, di 10:00)
Score = keerpunten + meldingen + 1,5 × klaring nodig + 1 × hoogtewissel nodig + afstand/15 km.

| # | Zweef | score | Motor | score | Ballon | score |
|---|---|---|---|---|---|---|
| 1 makkelijk | Verboden terrein (P Vught omvliegen) | 2,6 | Hoog over Volkel (om/over CTR) | 4,1 | Over de Waal | 2,6 |
| 2 makkelijk | Onder de TMA door (dalen < 1500 ft) | 3,6 | Laag naar Reusel (dalen onder TMA) | 4,6 | Oostenwind | 2,6 |
| 3 medium | Naar de Veluwe (Terlet, klaring Deelen) | 4,2 | Kerktoren van Breda (Gilze CTR) | 5,9 | Ballon over Vught | 3,6 |
| 4 medium | Langs de vliegbasis (Volkel) | 4,6 | Rondje Lichtstad (klaring + teruglezen) | 6,8 | Naar de Maas | 3,7 |
| 5 pittig | Thuis in Malden (2 keerpunten, TRA) | 5,7 | Over de Rijn (Deelen CTR) | 7,1 | Langs Gilze-Rijen | 4,0 |
| 6 pittig | Drie torens (3 keerpunten) | 7,5 | Langs de Peel (3 keerpunten, 3 CTR's) | 11,7 | Tussen de oefengebieden (TRA) | 4,2 |

## Generator (`genMission(ac, L)`)
- Doelen: plaatsen, herkenningspunten en velden in het kerngebied (tot 51,98° N), buiten CTR's en verboden gebieden, niet in BE/DE.
- Niveau L: keerpunten 1 (L ≤ 2) → 2 (L ≤ 5) → 3; minstens 1 + ⌊(L−1)/2⌋ gebieden op de rechte lijn (max 4; ballon max 2);
  bij oneven L ≥ 3 liefst een route die stijgen/dalen vraagt. Vanaf L 4 noemt de briefing de gebieden niet meer.
- Zelfde L = zelfde missie (seed). De volgende wordt na 1,5 s alvast berekend.
- Ballon: start bovenwinds; het hoogteplan rekent met 500 ft/min stijgen/dalen terwijl je meedrijft.

## Tests
- `d_missions_flown`: alle 18 vaste missies uitgevlogen via de knoppen (zweef/motor: zonder klaring, eerst geweigerd, melding weggetikt; ballon: hoogteplan).
- `d_generator`: niveau 1–8 per toestel bestaat en loopt op; niveau 1, 4 en 8 echt uitgevlogen zonder klaring.

## Open
- Thermiek/zweven staat op "niet doen"; de zweefkist stijgt nu arcade-achtig (W). Grote klimmen (1000 → 3500 ft) bij Volkel/Gilze zijn voor een zweefvlieger onrealistisch → bij de volgende ronde de planner voor zweef max. ±1000 ft laten stijgen.
- TRA/TSA rekent de planner als altijd actief (geen AUP-bron); zodra Eurocontrol AUP/UUP binnenkomt, het echte schema gebruiken.
