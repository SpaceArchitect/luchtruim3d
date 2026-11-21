#!/usr/bin/env python3
"""Spiegel van de relevante eAIP-pagina's (LVNL) per AIRAC → ./eaip/. Draait in GitHub Actions (cloud kan er niet bij).
Kiest de nieuwste editie die vandaag geldt. Alleen standaardbibliotheek."""
import datetime as dt, json, os, re, urllib.parse, urllib.request
ROOT = 'https://eaip.lvnl.nl/'
UA = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0 Safari/537.36 luchtruim3d',
      'Accept-Language': 'nl-NL,nl;q=0.9,en;q=0.8'}
WANT = re.compile(r"^EH-(GEN 2\.1|ENR 1\.[1-6]|ENR 2\.[12]|ENR 5\.[1-6]|AD 2 (EHEH|EHTL|EHBD|EHSE|EHMZ|EHDR|EHLE|EHST) \d+)-en-GB\.html$")
def get(u):
    with urllib.request.urlopen(urllib.request.Request(u, headers=UA), timeout=90) as r: return r.read()
root = get(ROOT).decode('utf-8', 'replace')
eds = sorted(set(re.findall(r'AIRAC AMDT (\d\d)-(\d{4})_(\d{4})_(\d\d)_(\d\d)', root)), key=lambda t: (t[2], t[3], t[4]))
today = dt.date.today().isoformat()
valid = [e for e in eds if f'{e[2]}-{e[3]}-{e[4]}' <= today] or eds
nr, yr, y, m, d = valid[-1]
ed = f'AIRAC AMDT {nr}-{yr}_{y}_{m}_{d}'; base = ROOT + urllib.parse.quote(ed) + '/eAIP/'
menu = get(base + 'menu.html').decode('utf-8', 'replace')
pages = sorted({h for h in re.findall(r"href='([^'#]+)", menu) if WANT.match(h)})
os.makedirs('eaip', exist_ok=True); got, bad = [], []
for p in pages:
    try: open(os.path.join('eaip', p.replace(' ', '_')), 'wb').write(get(base + urllib.parse.quote(p))); got.append(p)
    except Exception as e: bad.append(f'{p}: {e}')
json.dump({'edition': ed, 'effective': f'{y}-{m}-{d}', 'pages': got, 'failed': bad, 'source': base}, open('eaip/meta.json', 'w'), indent=1)
print(ed, len(got), 'pagina\'s', len(bad), 'mislukt')
