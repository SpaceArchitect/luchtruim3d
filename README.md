# Luchtruim in 3D

Educatieve webtool die het Nederlandse VFR-luchtruim (regio Eindhoven) in 3D laat zien, met een kaartmodus en een vliegmodus.

**⚠ Alleen voor educatie, niet voor vluchtvoorbereiding. De AIP van LVNL is leidend.**

- Luchtruim: LVNL VFR chart (geoservices.lvnl.nl), AIRAC 29 okt 2026, bijgeknipt en vereenvoudigd.
- Kaart: © OpenStreetMap-bijdragers (ODbL).
- Techniek: één statische pagina (`index.html`) met three.js 0.160 via jsDelivr.

## Ontwikkelen
- `index.html` is de hele site.
- `tools/shot.py`: headless test (Playwright + lokale three.js op poort 8765).
- `docs/`: sprintverslagen.
