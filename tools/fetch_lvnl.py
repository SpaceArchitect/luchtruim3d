#!/usr/bin/env python3
"""Haalt de LVNL-luchtruimdata (Geoportaal, CC BY 4.0) op: alle lagen van de Airspace- en Aerodrome-FeatureServer als GeoJSON.
Draait in GitHub Actions (open internet); schrijft naar ./lvnl/. Alleen standaardbibliotheek."""
import json, os, sys, urllib.parse, urllib.request
SERVICES = {
    'airspace': 'https://services-eu1.arcgis.com/OtUwzhpKSdeXgRIB/arcgis/rest/services/Airspaces_data/FeatureServer',
    'aerodrome': 'https://services-eu1.arcgis.com/OtUwzhpKSdeXgRIB/arcgis/rest/services/Aerodrome_data/FeatureServer',
}
UA = {'User-Agent': 'luchtruim3d-data (github.com/SpaceArchitect/luchtruim3d)'}
def get(url, **q):
    if q: url += '?' + urllib.parse.urlencode(q)
    with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=120) as r:
        return json.load(r)
out = os.path.join(os.getcwd(), 'lvnl'); os.makedirs(out, exist_ok=True)
meta = {'license': 'CC BY 4.0 (LVNL Geoportaal)', 'services': SERVICES, 'layers': {}}
for name, svc in SERVICES.items():
    info = get(svc, f='json')
    meta[name + '_info'] = {k: info.get(k) for k in ('serviceDescription', 'copyrightText', 'maxRecordCount')}
    for L in info.get('layers', []) + info.get('tables', []):
        feats, off = [], 0
        while True:
            d = get(f"{svc}/{L['id']}/query", where='1=1', outFields='*', f='geojson', resultOffset=off, resultRecordCount=1000, outSR=4326)
            fs = d.get('features', []); feats += fs; off += len(fs)
            if not fs or not d.get('exceededTransferLimit') and len(fs) < 1000: break
        fn = f"{name}_{L['id']}_{L['name']}".replace(' ', '_').replace('/', '_') + '.geojson'
        json.dump({'type': 'FeatureCollection', 'features': feats}, open(os.path.join(out, fn), 'w'))
        meta['layers'][fn] = {'count': len(feats), 'fields': sorted(feats[0]['properties'].keys()) if feats else []}
        print(fn, len(feats))
json.dump(meta, open(os.path.join(out, 'meta.json'), 'w'), indent=1)
