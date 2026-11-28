#!/usr/bin/env python3
"""Zet ruwe OSM-data (branch data/osm, tools/fetch_osm.py) om naar de compacte landschapsblokken in index.html.

    git fetch origin data/osm
    python tools/build_landscape.py --region arnhem-nijmegen --clip 4.75,51.8,6.15,52.15 [--write]

Alleen geometrie binnen --clip komt erbij (de bestaande regio blijft zoals hij is; naad op 51.8 N).
Formaten (zie index.html):
  osm       R|ref|delta   (snelweg)   W|naam|delta (rivier/kanaal)
  areadata  U||delta (bebouwing)  Q|naam|delta (water)  H||delta (heide)  T||delta (spoor)
  rwdata    R||surface|breedte_m|||lon,lat lon,lat …
  pwdata    P3|dx,dy dx,dy … (380/220 kV)   P1|… (150 kV)
  nl        extra ring (Nederland) ';'-gescheiden;  borders: extra lijn ';'-gescheiden
  plaatsen  CITIES/TOWNS-regels voor de JS-lijsten (alleen getekende bebouwing krijgt een naam)
Vereist: shapely (pip install shapely).
"""
import argparse, json, math, os, re, subprocess, tempfile
from shapely.ops import linemerge as _lm
def linemerge(g):
    if g is None or g.is_empty: return g
    if g.geom_type == 'LineString': return g
    if g.geom_type == 'MultiLineString': return _lm(g)
    ls = [x for x in getattr(g, 'geoms', []) if x.geom_type in ('LineString', 'MultiLineString')]
    return _lm(ls) if ls else g
from shapely.geometry import LineString, Polygon, MultiPolygon, box, Point
from shapely.ops import unary_union

RIVERS = {'Waal', 'Nederrijn', 'Lek', 'Boven-Rijn', 'Pannerdensch Kanaal', 'IJssel', 'Maas', 'Maas-Waalkanaal', 'Amsterdam-Rijnkanaal', 'Linge', 'Afgedamde Maas',
          # heel NL (26 nov): grote navigatielijnen elders
          'Noordzeekanaal', 'Nieuwe Waterweg', 'Nieuwe Maas', 'Oude Maas', 'Noord', 'Boven Merwede', 'Beneden Merwede', 'Nieuwe Merwede', 'Hollandsch Diep',
          'Twentekanaal', 'Zuid-Willemsvaart', 'Julianakanaal', 'Wilhelminakanaal', 'Kanaal door Zuid-Beveland', 'Kanaal Gent-Terneuzen', 'Van Starkenborghkanaal',
          'Prinses Margrietkanaal', 'Vecht', 'Zwarte Water', 'Overijsselse Vecht', 'Eemskanaal', 'Hollandse IJssel', 'Gouwe'}  # wat je vanuit de lucht als navigatielijn gebruikt
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LON0, LAT0 = 5.45, 51.5; KX = 111.32 * math.cos(math.radians(LAT0)); KY = 111.25
km = lambda lo, la: ((lo - LON0) * KX, (la - LAT0) * KY)
ll = lambda x, y: (x / KX + LON0, y / KY + LAT0)


def load(region, src=None):
    if src:  # ruwe tegel direct uit de Action (niet uit git)
        return {f[:-5]: json.load(open(os.path.join(src, f))) for f in os.listdir(src) if f.endswith('.json') and f != 'meta.json'}
    d = tempfile.mkdtemp()
    subprocess.run(f'git -C "{ROOT}" archive origin/data/osm osm/{region} | tar -x -C "{d}"', shell=True, check=True)
    p = os.path.join(d, 'osm', region)
    return {f[:-5]: json.load(open(os.path.join(p, f))) for f in os.listdir(p) if f.endswith('.json') and f != 'meta.json'}


def enc(coords):  # lon/lat → delta ×1e4
    o, px, py = [], 0, 0
    for lo, la in coords:
        x, y = round(lo * 1e4), round(la * 1e4); o += [x - px, y - py]; px, py = x, y
    return ','.join(map(str, o))


def enc_pw(coords):
    o, px, py = [], 0, 0
    for lo, la in coords:
        x, y = round(lo * 1e4), round(la * 1e4); o.append(f'{x - px},{y - py}'); px, py = x, y
    return ' '.join(o)


def way_km(el): return [km(p['lon'], p['lat']) for p in el.get('geometry', []) if p]


def polys(data):
    """ways + multipolygon-relaties → shapely-polygonen in km."""
    out = []
    for el in data.get('elements', []):
        if el['type'] == 'way':
            c = way_km(el)
            if len(c) >= 4 and c[0] == c[-1]: out.append((el.get('tags', {}), Polygon(c).buffer(0)))
        elif el['type'] == 'relation':
            outer = [LineString(way_km(m)) for m in el.get('members', []) if m.get('role') == 'outer' and m.get('geometry')]
            merged = _lm(outer) if outer else None
            for g in (getattr(merged, 'geoms', [merged]) if merged is not None and not merged.is_empty else []):
                if g.is_ring: out.append((el.get('tags', {}), Polygon(g.coords).buffer(0)))
    return out


def to_ll(geom):
    return [ll(x, y) for x, y in geom.coords]


def ring_lines(tag, geom, name='', min_km2=0.0, simp=0.06):
    res = []
    for g in getattr(geom, 'geoms', [geom]):
        if g.is_empty or g.area < min_km2: continue
        g = g.simplify(simp)
        if g.geom_type != 'Polygon' or len(g.exterior.coords) < 4: continue
        res.append(f'{tag}|{name}|{enc(to_ll(g.exterior))}')
    return res


def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--region', required=True); ap.add_argument('--clip', required=True)
    ap.add_argument('--write', action='store_true'); ap.add_argument('--src', help='map met ruwe OSM-json (Action)'); ap.add_argument('--out', help='compact resultaat als json')
    o = ap.parse_args()
    x0, y0, x1, y1 = map(float, o.clip.split(','))
    CL = box(*km(x0, y0), *km(x1, y1)); D = load(o.region, o.src); out = {k: [] for k in ('osm', 'areadata', 'rwdata', 'pwdata', 'nl', 'borders')}
    # snelwegen per wegnummer, rivieren per naam
    roads, rivers = {}, {}
    for k in ('motorways', 'rivers', 'urban', 'water', 'heath_sand', 'aeroways', 'power', 'places'): D.setdefault(k, {'elements': []})
    for el in D['motorways']['elements']:
        t = el.get('tags', {}); ref = (t.get('ref') or '').split(';')[0].replace(' ', '')
        if t.get('highway') == 'motorway' and ref: roads.setdefault(ref, []).append(LineString(way_km(el)))
    for el in D['rivers']['elements']:
        t = el.get('tags', {}); nm = t.get('name')
        if nm in RIVERS: rivers.setdefault(nm, []).append(LineString(way_km(el)))
    for tag, groups, simp in (('R', roads, .25), ('W', rivers, .15)):
        for nm, ls in groups.items():
            g = linemerge(unary_union(ls).intersection(CL)) if ls else None
            for part in (getattr(g, 'geoms', [g]) if g is not None and not g.is_empty else []):
                if part.length < (3.0 if tag == 'R' else 2.0): continue
                p = part.simplify(simp)
                out['osm'].append(f"{tag}|{('A ' + nm[1:]) if tag == 'R' and nm.startswith('A') else nm}|{enc(to_ll(p))}")
    # vlakken
    urban = unary_union([g for _, g in polys(D['urban'])]).buffer(.1).buffer(-.1).intersection(CL)
    out['areadata'] += ring_lines('U', urban, min_km2=1.0)
    for tags, g in polys(D['water']):
        g = g.intersection(CL)
        if g.area >= .4: out['areadata'] += ring_lines('Q', g, tags.get('name', '') if g.area > 2 else '', .4, .05)
    heath = unary_union([g for t, g in polys(D['heath_sand']) if t.get('natural') == 'heath']).intersection(CL)
    out['areadata'] += ring_lines('H', heath, min_km2=.5)
    if 'rail' in D:
        rl = linemerge(unary_union([LineString(way_km(e)) for e in D['rail']['elements'] if len(way_km(e)) > 1]).intersection(CL))
        for part in getattr(rl, 'geoms', [rl]):
            if part.length > 2: out['areadata'].append(f'T||{enc(to_ll(part.simplify(.1)))}')
    # banen
    for el in D['aeroways']['elements']:
        t = el.get('tags', {})
        if el['type'] == 'way' and t.get('aeroway') == 'runway' and LineString(way_km(el)).intersects(CL):
            surf = 'grass' if t.get('surface') in ('grass', 'ground', 'dirt') else 'paved'
            w = re.sub(r'[^0-9.]', '', t.get('width', '')) or ''
            out['rwdata'].append(f"R||{surf}|{w}|||" + ' '.join(f"{p['lon']:.4f},{p['lat']:.4f}" for p in el['geometry']))
    # hoogspanning
    for el in D['power']['elements']:
        v = t = el.get('tags', {}).get('voltage', ''); hi = any(k in v for k in ('380000', '220000'))
        g = LineString(way_km(el)).intersection(CL)
        for part in getattr(g, 'geoms', [g]):
            if not part.is_empty and part.length > .5: out['pwdata'].append(f"{'P3' if hi else 'P1'}|{enc_pw(to_ll(part.simplify(.05)))}")
    # landsgrens en NL-vlak (noordrand)
    if 'border' in D:
        bl = linemerge(unary_union([LineString(way_km(e)) for e in D['border']['elements'] if len(way_km(e)) > 1]).intersection(CL.buffer(3)))
        for part in getattr(bl, 'geoms', [bl]):
            if part.length > 1: out['borders'].append(enc(to_ll(part.simplify(.1))))
    # plaatsen
    cities, towns = [], []
    for el in D['places']['elements']:
        t = el.get('tags', {}); nm = t.get('name'); lo, la = el.get('lon'), el.get('lat')
        if not nm or lo is None or not CL.contains(Point(km(lo, la))): continue
        (cities if t.get('place') == 'city' else towns).append([nm, round(lo, 4), round(la, 4)])
    U = [g for g in getattr(urban, 'geoms', [urban]) if g.area >= 1.0]
    inU = lambda pl: any(g.contains(Point(km(pl[1], pl[2]))) for g in U)
    towns = [t for t in towns if inU(t)]
    out['places'] = {'cities': cities, 'towns': towns}
    for k, v in out.items(): print(k, len(v) if not isinstance(v, dict) else {a: len(b) for a, b in v.items()})
    json.dump(out, open(o.out or os.path.join(tempfile.gettempdir(), f'landscape-{o.region}.json'), 'w'), ensure_ascii=False)
    if o.write: write(out)


def write(out):
    p = os.path.join(ROOT, 'index.html'); h = open(p, encoding='utf-8').read()
    for bid, sep in (('osm', '\n'), ('areadata', '\n'), ('rwdata', '\n'), ('pwdata', '\n'), ('borders', ';')):
        if not out[bid]: continue
        m = re.search(r'(<script id="%s" type="text/plain">)(.*?)(</script>)' % bid, h, re.S)
        cur = m.group(2).rstrip()
        add = [l for l in out[bid] if l not in cur]
        h = h[:m.start(2)] + cur + sep + sep.join(add) + h[m.end(2):]
    open(p, 'w', encoding='utf-8').write(h); print('index.html bijgewerkt (landschap)')


if __name__ == '__main__':
    main()
