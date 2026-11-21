#!/usr/bin/env python3
"""Haalt ruwe OpenStreetMap-data (ODbL) op voor een regio via Overpass. Draait in GitHub Actions; schrijft naar ./osm/<regio>/.
Bewust ruw: de omzetting naar het compacte app-formaat (osm/areadata/rwdata/pwdata) is een aparte stap."""
import json, os, sys, time, urllib.parse, urllib.request
REGIONS = {  # zuid, west, noord, oost
    'eindhoven': (51.2, 4.75, 51.8, 6.15),
    'arnhem-nijmegen': (51.75, 4.75, 52.15, 6.2),  # hele noordrand van de regio (Rivierenland, Arnhem, Nijmegen, Veluwezoom)
}
Q = {
    'motorways': 'way["highway"~"^(motorway|trunk)$"]',
    'rivers': 'way["waterway"~"^(river|canal)$"]',
    'water': 'way["natural"="water"]; relation["natural"="water"]; way["water"]',
    'urban': 'way["landuse"~"^(residential|commercial|retail|industrial)$"]',
    'heath_sand': 'way["natural"~"^(heath|sand)$"]; relation["natural"~"^(heath|sand)$"]',
    'aeroways': 'way["aeroway"~"^(runway|aerodrome)$"]; relation["aeroway"="aerodrome"]',
    'power': 'way["power"="line"]["voltage"~"^(150000|220000|380000)"]',
    'wind': 'node["generator:source"="wind"]',
    'places': 'node["place"~"^(city|town|village)$"]',
    'border': 'way["boundary"="administrative"]["admin_level"="2"]',
    'rail': 'way["railway"="rail"]["usage"="main"]',
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
    for name, sel in Q.items():
        parts = ''.join(f'{p.strip()}({s},{w},{n},{e});' for p in sel.split(';') if p.strip())
        d = overpass(f'[out:json][timeout:240];({parts});out geom;')
        if d is None: print(reg, name, 'MISLUKT'); continue
        json.dump(d, open(os.path.join(out, name + '.json'), 'w'))
        print(reg, name, len(d.get('elements', [])))
        time.sleep(5)
    json.dump({'bbox': [s, w, n, e], 'license': 'ODbL, © OpenStreetMap-bijdragers', 'fetched': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()), 'errors': ERR}, open(os.path.join(out, 'meta.json'), 'w'))
