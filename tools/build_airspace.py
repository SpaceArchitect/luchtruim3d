#!/usr/bin/env python3
"""Bouwt het ingebakken luchtruimblok (<script id="airspace">) uit de LVNL Geoportaal-data (branch data/lvnl).

    git fetch origin data/lvnl
    python tools/build_airspace.py --bbox 4.75,51.2,6.15,51.8 --check     # vergelijk met index.html, verandert niets
    python tools/build_airspace.py --bbox 4.75,51.2,6.15,51.8 --write     # vervang het NL-deel in index.html

Regelformaat (zie index.html, LAYERS):
    layer|ident|naam|typ|klasse|lo|loUnit|loRef|hi|hiUnit|hiRef|ringen
ringen = ';'-gescheiden, coördinaten ×1e4 en delta-gecodeerd. Buitenlandse volumes (EB*, ED*) staan niet in het
Geoportaal en blijven zoals ze in index.html staan.
"""
import argparse, json, os, re, subprocess, sys, tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LAYER = {'CTR': 'CTR', 'TMA': 'TMA', 'CTA': 'CTA', 'ATZ': 'ATZ', 'Prohibited_area': 'P', 'Restricted_area': 'R',
         'Danger_area': 'D', 'TRA': 'TRA', 'TSA': 'TSA', 'Parajump': 'PJA', 'Climb_area': 'CLIMB', 'TMZ_RTMZ': 'TMZ',
         'RMZ': 'RMZ', 'Glider_area': 'GLD', 'Low_Flying_area_': 'LFA'}
IDENT_MAP = {'EHDPD': 'EHDP'}  # oude namen behouden (missies, AIPINFO)


def load_geojson():
    d = tempfile.mkdtemp()
    subprocess.run(f'git -C "{ROOT}" archive origin/data/lvnl lvnl | tar -x -C "{d}"', shell=True, check=True)
    return os.path.join(d, 'lvnl')


def enc(ring):
    out, px, py = [], 0, 0
    for lo, la in ring:
        x, y = round(lo * 1e4), round(la * 1e4)
        out += [x - px, y - py]; px, py = x, y
    return ','.join(map(str, out))


def simplify(ring, tol=0.0008):  # Douglas-Peucker in graden (~70 m), zoals de oorspronkelijke data
    if len(ring) < 4: return ring
    def rdp(pts):
        a, b = pts[0], pts[-1]; dx, dy = b[0] - a[0], b[1] - a[1]; L = (dx * dx + dy * dy) ** .5 or 1e-12
        i, dm = 0, 0
        for k in range(1, len(pts) - 1):
            d = abs(dy * pts[k][0] - dx * pts[k][1] + b[0] * a[1] - b[1] * a[0]) / L
            if d > dm: i, dm = k, d
        return rdp(pts[:i + 1])[:-1] + rdp(pts[i:]) if dm > tol else [a, b]
    # gesloten ring: begin = eind, dus eerst splitsen op het verste punt (anders klapt hij in tot 2 punten)
    a = ring[0]; k = max(range(len(ring)), key=lambda i: (ring[i][0] - a[0]) ** 2 + (ring[i][1] - a[1]) ** 2)
    return rdp(ring[:k + 1])[:-1] + rdp(ring[k:])


def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--bbox', required=True)
    ap.add_argument('--check', action='store_true'); ap.add_argument('--write', action='store_true')
    o = ap.parse_args(); x0, y0, x1, y1 = map(float, o.bbox.split(','))
    src = load_geojson(); lines = []; feats = []
    for fn in sorted(os.listdir(src)):
        m = re.match(r'airspace_\d+_(.+)\.geojson$', fn)
        if not m or m.group(1) not in LAYER: continue
        feats += [(m, f) for f in json.load(open(os.path.join(src, fn)))['features']]
    part_names = {f['properties']['Name'] for _, f in feats if f['properties'].get('Type') == 'PART'}
    all_names = {f['properties']['Name'] for _, f in feats if f['properties']['Name']}
    for m, f in feats:
        if True:
            # 'RAS' = het hele gebied; als er delen (PART, eigen grenzen per deel) zijn, tonen we alleen de delen
            N = f['properties']['Name']
            if N and ((f['properties'].get('Type') == 'RAS' and N in part_names) or any(x.startswith(N + ' ') and len(x) == len(N) + 2 and x[-1] in 'ABCDEFGH' for x in all_names)): continue
            g = f['geometry']
            if not g: continue
            polys = [g['coordinates']] if g['type'] == 'Polygon' else g['coordinates']
            if not any(x0 <= lo <= x1 and y0 <= la <= y1 for p in polys for lo, la in p[0]): continue
            rings = [simplify(p[0]) for p in polys]
            P = f['properties']; ident = IDENT_MAP.get(P['Designator'], P['Designator'])
            lines.append('|'.join(map(str, [LAYER[m.group(1)], ident, P['Name'] or P['Designator'], P.get('Type') or '', P.get('Class') or '',
                         P['LowerLimit'], P['LowerLimitUnit'], P['LowerLimitReference'], P['UpperLimit'], P['UpperLimitUnit'],
                         P['UpperLimitReference'], ';'.join(enc(r) for r in rings)])))
    # LVNL gebruikt soms één ident voor CTR én TMA (EHLE1, EHLE2, EHGG, EHBK2): AIPINFO is per ident → TMA krijgt suffix 'T' (26 nov)
    ctr_ids = {l.split('|')[1] for l in lines if l.startswith('CTR|')}
    lines = [('TMA|' + l.split('|')[1] + 'T|' + l.split('|', 2)[2]) if l.startswith('TMA|') and l.split('|')[1] in ctr_ids else l for l in lines]
    html = open(os.path.join(ROOT, 'index.html'), encoding='utf-8').read()
    m = re.search(r'(<script id="airspace" type="text/plain">)(.*?)(</script>)', html, re.S)
    cur = m.group(2).strip().split('\n')
    foreign = [l for l in cur if re.match(r'^[A-Z]+\|(EB|ED)', l)]
    new_ids = {l.split('|')[1] for l in lines}; cur_ids = {l.split('|')[1] for l in cur}
    print(f'Geoportaal: {len(lines)} volumes in bbox · huidig: {len(cur)} · buitenland behouden: {len(foreign)}')
    print('nieuw:', sorted(new_ids - cur_ids)); print('verdwijnt:', sorted(cur_ids - new_ids - {l.split("|")[1] for l in foreign}))
    if o.write:
        html = html[:m.start(2)] + '\n'.join(lines + foreign) + html[m.end(2):]
        open(os.path.join(ROOT, 'index.html'), 'w', encoding='utf-8').write(html); print('index.html bijgewerkt')


if __name__ == '__main__':
    main()
