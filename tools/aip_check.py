#!/usr/bin/env python3
"""Controleert de AIP-gegevens in index.html (AIPINFO: frequenties) tegen de eAIP-spiegel (branch data/eaip).
    git fetch origin data/eaip && python tools/aip_check.py
Per ident: staat de frequentie in het blok van dat luchtruim in ENR 2.1/2.2? Uitvoer: OK / AFWIJKING / NIET GEVONDEN."""
import html, os, re, subprocess, sys, tempfile
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
d = tempfile.mkdtemp(); subprocess.run(f'git -C "{ROOT}" archive origin/data/eaip eaip | tar -x -C "{d}"', shell=True, check=True)
txt = ''
for f in ['EH-ENR_2.1-en-GB.html', 'EH-ENR_2.2-en-GB.html'] + sorted(x for x in os.listdir(os.path.join(d, 'eaip')) if x.startswith('EH-AD_2_EHEH')):
    t = open(os.path.join(d, 'eaip', f), encoding='utf-8', errors='replace').read()
    txt += re.sub(r'\s+', ' ', html.unescape(re.sub(r'<[^>]+>', ' ', t)))
meta = open(os.path.join(d, 'eaip', 'meta.json')).read()
src = open(os.path.join(ROOT, 'index.html'), encoding='utf-8').read()
info = re.findall(r"(EH[A-Z0-9]+):\{unit:'([^']*)',freq:'([^']*)'", src)
bad = 0
for ident, unit, freq in info:
    if not freq: continue  # geen frequentie (TMZ/ATZ, of 'nog te verifiëren'): niets te toetsen
    if ident == 'EHAMTMZ': txt_ok = '124.300' in open(os.path.join(d, 'eaip', 'EH-ENR_1.2-en-GB.html'), encoding='utf-8', errors='replace').read(); print(('OK          ' if txt_ok else 'AFWIJKING   ') + f'{ident:9} {unit} {freq} (ENR 1.2 FMC)'); bad += 0 if txt_ok else 1; continue
    base = re.sub(r'(\d[A-Z]?)$', '', ident) if re.match(r'EHEH\d', ident) else ident  # Eindhoven TMA 1–4 staan samen
    m = re.search(r'\(%s\)' % re.escape(base), txt) or (re.search(r'\(%s\)' % re.escape(ident[:4] + 'TMA'), txt) if ident.startswith('EHMC') else None)
    if ident.startswith('EHMCD'): m = re.search(r'NIEUW MILLIGEN TMA D \(EHMC', txt)
    if ident.startswith('EHEH') and ident[4:].isdigit(): m = re.search(r'EINDHOVEN TMA', txt)
    if not m and ident == 'EHEH': m = re.search(r'Eindhoven CTR|EINDHOVEN CTR|CTR Eindhoven', txt)
    if not m: print(f'NIET GEVONDEN  {ident} ({unit} {freq})'); continue
    blk = txt[m.start():m.start() + 1600]
    nxt = re.search(r'[A-Z][A-Z ]+ \((EH[A-Z0-9]{2,})\)', blk[80:])
    blk = blk[:80 + nxt.start()] if nxt else blk
    ok = freq.replace('.', r'\.') and re.search(re.escape(freq), blk)
    if not ok:  # CTR-frequentie staat soms alleen in AD 2.18 van het veld (bv. Lelystad Tower): zoek in die pagina's
        adf = [x for x in os.listdir(os.path.join(d, 'eaip')) if x.startswith('EH-AD_2_' + ident[:4] + '_')]
        adt = ''.join(open(os.path.join(d, 'eaip', x), encoding='utf-8', errors='replace').read() for x in adf)
        ok = bool(adt) and freq in adt and unit.split()[0] in adt
    print(('OK          ' if ok else 'AFWIJKING   ') + f'{ident:9} {unit} {freq}' + ('' if ok else f'  | AIP: {blk[:220]}'))
    bad += 0 if ok else 1
print(re.search(r'"edition": "([^"]+)"', meta).group(1), '·', len(info), 'gecontroleerd,', bad, 'afwijkingen')
sys.exit(1 if bad else 0)
