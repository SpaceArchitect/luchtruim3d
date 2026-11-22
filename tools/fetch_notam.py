#!/usr/bin/env python3
"""NOTAMs voor de Nederlandse FIR (EHAA) en velden, via de openbare FAA NOTAM Search (geen login).
Draait in GitHub Actions (data-notam.yml) → branch data/notam. Ruw bewaren + Q-regel uitpakken (gebied, straal, FL-grenzen).
Bron is een kopie van de officiële NOTAMs: in de app altijd 'educatief, controleer via de officiële briefing'."""
import json, os, re, time, urllib.parse, urllib.request
LOCS = ['EHAA', 'EHEH', 'EHDL', 'EHVK', 'EHGR', 'EHWO', 'EHSE', 'EHBK', 'EHAM', 'EHRD', 'EHLE', 'EHTE', 'EHMZ', 'EHGG', 'EHLW', 'EHKD', 'EHDR', 'EHHO', 'EHST', 'EHTW']
URL = 'https://notams.aim.faa.gov/notamSearch/search'
UA = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) luchtruim3d-data', 'Content-Type': 'application/x-www-form-urlencoded', 'Accept': 'application/json,*/*'}
Q = re.compile(r'Q\)\s*(\w{4})/(\w{5})/(\w+)/(\w+)/(\w+)/(\d{3})/(\d{3})/(\d{4})([NS])(\d{5})([EW])(\d{3})')
def fetch(locs):
    out, off = [], 0
    while True:
        body = urllib.parse.urlencode({'searchType': 0, 'designatorsForLocation': ','.join(locs), 'offset': off, 'notamsOnly': 'false'}).encode()
        for k in range(4):
            try:
                with urllib.request.urlopen(urllib.request.Request(URL, data=body, headers=UA), timeout=90) as r: d = json.load(r); break
            except Exception as e: print('retry', k, e); time.sleep(15 * (k + 1))
        else: raise SystemExit('NOTAM-bron onbereikbaar')
        lst = d.get('notamList', []); out += lst
        if len(lst) < 30 or off > 3000: return out
        off += 30
def parse(n):
    t = n.get('icaoMessage') or n.get('traditionalMessage') or ''
    m = Q.search(t); r = {'id': n.get('notamNumber'), 'loc': n.get('facilityDesignator') or n.get('icaoId'), 'start': n.get('startDate'), 'end': n.get('endDate'), 'text': t}
    if m:
        fir, code, traffic, purpose, scope, lo, hi, la, ns, lo_, ew, rad = m.groups()
        lat = (int(la[:2]) + int(la[2:]) / 60) * (1 if ns == 'N' else -1); lon = (int(lo_[:3]) + int(lo_[3:]) / 60) * (1 if ew == 'E' else -1)
        r.update(q=code, fl=[int(lo), int(hi)], lat=round(lat, 4), lon=round(lon, 4), r_nm=int(rad))
    return r
raw = fetch(LOCS)
os.makedirs('notam', exist_ok=True)
json.dump(raw, open('notam/raw.json', 'w'))
json.dump({'fetched': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()), 'source': URL, 'n': len(raw), 'notams': [parse(n) for n in raw]}, open('notam/notams.json', 'w'), ensure_ascii=False)
print('NOTAMs:', len(raw))
