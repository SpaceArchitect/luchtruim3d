#!/usr/bin/env python3
"""Haalt ruwe OpenStreetMap-data (ODbL) op voor een regio via Overpass. Draait in GitHub Actions; schrijft naar ./osm/<regio>/.
Bewust ruw: de omzetting naar het compacte app-formaat (osm/areadata/rwdata/pwdata) is een aparte stap."""
import json, os, sys, time, urllib.parse, urllib.request
REGIONS = {  # zuid, west, noord, oost
    'eindhoven': (51.2, 4.75, 51.8, 6.15),
    'arnhem-nijmegen': (51.75, 4.75, 52.15, 6.2),  # hele noordrand van de regio (Rivierenland, Arnhem, Nijmegen, Veluwezoom)
    'herkenning': (51.2, 4.75, 52.15, 6.25),  # hele app-regio, alleen herkenningspunten (QH)
}
# Heel NL (reset-push, Christian 25 nov): tegels van 1,0° × 0,6°; alleen tegels met Nederlands land. Ruwe data is te groot voor git
# (bos/water regio Arnhem al ±99 MB): de Action zet elke tegel direct om (build_landscape.py --src/--out) en bewaart alleen het compacte resultaat.
NL_TILES = {}
for _i, _la in enumerate((50.7, 51.3, 51.9, 52.5, 53.1)):
    for _j, _lo in enumerate((3.3, 4.3, 5.3, 6.3)):
        if (_i, _j) in ((3, 0), (4, 0), (0, 3)): continue  # alleen zee of buitenland
        NL_TILES[f'nl-{_i}{_j}'] = (_la, _lo, round(_la + .6, 1), round(_lo + 1.0, 1))
REGIONS.update(NL_TILES)
if len(sys.argv) > 1 and sys.argv[1] == '--list':
    print(json.dumps(sorted(NL_TILES))); sys.exit(0)
# Herkenningspunten (voorstel 21 nov, akkoord Christian 22 nov): bruggen, knooppunten, vliegvelden.
QH = {
    'bridges': 'way["man_made"="bridge"]["name"]; relation["man_made"="bridge"]["name"]; way["bridge:name"]',
    'junctions': 'node["highway"="motorway_junction"]["name"~"^(Knooppunt|Kp)"]; node["highway"="motorway_junction"]["name"~"Hooipolder|Empel|Zaarderheiken|Ewijk|Valburg|Grijsoord|Batadorp|Leenderheide|De Hogt|Ekkersweijer|Vught|Paalgraven|Rijkevoort|Noorderkroon|Neerbosch|Bankhoef|Deil|Velperbroek|Waterberg|Lunetten"]',
    'aerodromes': 'way["aeroway"="aerodrome"]; relation["aeroway"="aerodrome"]; way["aeroway"="runway"]',
}
Q = {
    'motorways': 'way["highway"~"^(motorway|trunk)$"]',
    'rivers': 'way["waterway"~"^(river|canal)$"]',
    'water': 'way["natural"="water"]; relation["natural"="water"]; way["water"]',
    'urban': 'way["landuse"~"^(residential|commercial|retail|industrial)$"]',
    'forest': 'way["landuse"="forest"]; way["natural"="wood"]; relation["landuse"="forest"]; relation["natural"="wood"]',  # landschap procedureel (Christian 22 nov)
    'heath_sand': 'way["natural"~"^(heath|sand)$"]; relation["natural"~"^(heath|sand)$"]',
    'aeroways': 'way["aeroway"~"^(runway|aerodrome)$"]; relation["aeroway"="aerodrome"]',
    'power': 'way["power"="line"]["voltage"~"^(150000|220000|380000)"]',
    'wind': 'node["generator:source"="wind"]',
    'places': 'node["place"~"^(city|town|village)$"]',
    'border': 'way["boundary"="administrative"]["admin_level"="2"]',
    'rail': 'way["railway"="rail"]["usage"="main"]',
    'landmarks': 'way["bridge"]["name"~"Waalbrug|John Frostbrug|De Oversteek|Nelson Mandelabrug|Rijnbrug"]; way["building"~"church|cathedral"]["name"~"Eusebius|Stevenskerk"]; node["man_made"="tower"]["name"]',
    'tall': 'node["man_made"~"^(tower|chimney|mast)$"]["height"]',
}
ERR = []
UA = {'User-Agent': 'luchtruim3d-data (github.com/SpaceArchitect/luchtruim3d)', 'Content-Type': 'application/x-www-form-urlencoded', 'Accept': 'application/json,*/*'}
def overpass(q):
    body = urllib.parse.urlencode({'data': q}).encode()
    for k in range(4):
        try:
            with urllib.request.urlopen(urllib.request.Request('https://overpass-api.de/api/interpreter', data=body, headers=UA), timeout=300) as r:
                return json.load(r)
        except Exception as e:
            msg = getattr(e, 'read', lambda: b'')()[:300]
            print('  retry', k, e, msg); ERR.append(f'{e} {msg!r}'); time.sleep(20 * (k + 1))
    return None
for reg, (s, w, n, e) in REGIONS.items():
    if len(sys.argv) > 1 and reg not in sys.argv[1:]: continue
    out = os.path.join('osm', reg); os.makedirs(out, exist_ok=True)
    for name, sel in (QH if reg == 'herkenning' else Q).items():
        parts = ''.join(f'{p.strip()}({s},{w},{n},{e});' for p in sel.split(';') if p.strip())
        d = overpass(f'[out:json][timeout:240];({parts});out geom;')
        if d is None: print(reg, name, 'MISLUKT'); continue
        json.dump(d, open(os.path.join(out, name + '.json'), 'w'))
        print(reg, name, len(d.get('elements', [])))
        time.sleep(5)
    json.dump({'bbox': [s, w, n, e], 'license': 'ODbL, © OpenStreetMap-bijdragers', 'fetched': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()), 'errors': ERR}, open(os.path.join(out, 'meta.json'), 'w'))
