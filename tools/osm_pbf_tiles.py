#!/usr/bin/env python3
"""Heel NL zonder Overpass (28 nov): Geofabrik-extract (OpenStreetMap, ODbL) → per tegel dezelfde ruwe lagen als fetch_osm.py,
in het Overpass-JSON-formaat dat build_landscape.py leest ({'elements': [{type, tags, geometry|members|lat/lon}]}).

    python3 tools/osm_pbf_tiles.py netherlands-latest.osm.pbf nl-00 nl-01 …    # schrijft osm/<tegel>/<laag>.json + meta.json

Vereist: osmium-tool (apt). Waarom: Overpass deed 30–70 min per tegel met veel 502's (LOG 27–28 nov).
"""
import json, os, re, subprocess, sys, tempfile, time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
# tegels en lagen: dezelfde definitie als de Overpass-route (één bron van waarheid voor de tegelindeling)
NL_TILES = {}
for _i, _la in enumerate((50.7, 51.3, 51.9, 52.5, 53.1)):
    for _j, _lo in enumerate((3.3, 4.3, 5.3, 6.3)):
        if (_i, _j) in ((3, 0), (4, 0), (0, 3)): continue
        NL_TILES[f'nl-{_i}{_j}'] = (_la, _lo, round(_la + .6, 1), round(_lo + 1.0, 1))

# osmium tags-filter-expressies per laag (zelfde selectie als Q in fetch_osm.py); extra filters op tagwaarden in KEEP
LAYERS = {
    'motorways': ['w/highway=motorway,trunk'],
    'rivers': ['w/waterway=river,canal'],
    'water': ['wr/natural=water', 'wr/water'],
    'urban': ['wr/landuse=residential,commercial,retail,industrial'],
    'heath_sand': ['wr/natural=heath,sand'],
    'aeroways': ['w/aeroway=runway,aerodrome', 'r/aeroway=aerodrome'],
    'power': ['w/power=line'],
    'places': ['n/place=city,town,village'],
    'border': ['r/boundary=administrative'],
    'rail': ['w/railway=rail'],
}
KEEP = {
    'power': lambda t: re.match(r'^(150000|220000|380000)', t.get('voltage', '')) is not None,
    'border': lambda t: t.get('admin_level') == '2',
    'rail': lambda t: t.get('usage') == 'main',
}
AREA = {'water', 'urban', 'heath_sand', 'border'}  # polygonen; de rest lijnen/punten


def run(*a):
    subprocess.run(a, check=True, stdout=subprocess.DEVNULL)


def pts(coords):
    return [{'lat': round(la, 7), 'lon': round(lo, 7)} for lo, la in coords]


def to_elements(path, layer):
    els = []
    keep = KEEP.get(layer, lambda t: True)
    with open(path, encoding='utf-8') as f:
        for line in f:
            line = line.strip().lstrip('\x1e')
            if not line: continue
            ft = json.loads(line); g = ft.get('geometry') or {}; t = {k: str(v) for k, v in (ft.get('properties') or {}).items() if not k.startswith('@')}
            if not keep(t): continue
            ty = g.get('type')
            if ty == 'Point':
                lo, la = g['coordinates']; els.append({'type': 'node', 'lat': la, 'lon': lo, 'tags': t})
            elif ty == 'LineString':
                els.append({'type': 'way', 'tags': t, 'geometry': pts(g['coordinates'])})
            elif ty == 'MultiLineString':
                for c in g['coordinates']: els.append({'type': 'way', 'tags': t, 'geometry': pts(c)})
            elif ty == 'Polygon':
                if layer == 'border':  # build_landscape gebruikt de grens als lijn
                    els.append({'type': 'way', 'tags': t, 'geometry': pts(g['coordinates'][0])})
                else:
                    els.append({'type': 'way', 'tags': t, 'geometry': pts(g['coordinates'][0])})
            elif ty == 'MultiPolygon':
                if layer == 'border':
                    for poly in g['coordinates']: els.append({'type': 'way', 'tags': t, 'geometry': pts(poly[0])})
                else:
                    els.append({'type': 'relation', 'tags': t, 'members': [{'type': 'way', 'role': 'outer', 'geometry': pts(poly[0])} for poly in g['coordinates']]})
    return els


def main():
    pbf, tiles = sys.argv[1], sys.argv[2:] or sorted(NL_TILES)
    for tile in tiles:
        s, w, n, e = NL_TILES[tile]; out = os.path.join('osm', tile); os.makedirs(out, exist_ok=True); missing, t0 = [], time.time()
        with tempfile.TemporaryDirectory() as d:
            tp = os.path.join(d, 't.pbf')
            run('osmium', 'extract', '-b', f'{w},{s},{e},{n}', '-s', 'smart', '-o', tp, '--overwrite', pbf)
            for layer, expr in LAYERS.items():
                try:
                    lp, gj = os.path.join(d, layer + '.pbf'), os.path.join(d, layer + '.geojsonseq')
                    run('osmium', 'tags-filter', '-o', lp, '--overwrite', tp, *expr)
                    gt = ['--geometry-types=polygon'] if layer in AREA and layer != 'border' else []
                    run('osmium', 'export', '-f', 'geojsonseq', '-o', gj, '--overwrite', *gt, lp)
                    els = to_elements(gj, layer)
                    json.dump({'elements': els}, open(os.path.join(out, layer + '.json'), 'w'))
                    print(tile, layer, len(els))
                except Exception as ex:
                    print(tile, layer, 'MISLUKT', ex); missing.append(layer)
        json.dump({'bbox': [s, w, n, e], 'license': 'ODbL, © OpenStreetMap-bijdragers', 'source': 'Geofabrik netherlands-latest.osm.pbf',
                   'fetched': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()), 'errors': [], 'missing': missing}, open(os.path.join(out, 'meta.json'), 'w'))
        print(tile, 'klaar in', round(time.time() - t0), 's')


if __name__ == '__main__':
    main()
