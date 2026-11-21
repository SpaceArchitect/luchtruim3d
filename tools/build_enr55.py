"""ENR 5.5 (eAIP LVNL) → datablok <script id="enr55"> in index.html.

Activiteiten met een cirkel: schermvliegen/deltavliegen (lier), zweefvliegen (lierstart),
modelvliegen (UAS) en ULV. Per terrein: positie, straal, bovengrens (GND–top) en operator.

Gebruik:
  git fetch origin data/eaip
  python tools/build_enr55.py [--bbox 4.75,51.2,6.25,52.15] [--check]

Bron: AIP ENR 5.5 (eAIP-spiegel op branch data/eaip). De AIP is leidend.
"""
import argparse, html, os, re, subprocess, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STOP = {'UDP', 'UAS', 'ULM', 'TWR.', 'HOL', 'SUN', 'SAT', 'FRI', 'PPR.', 'INFO', 'OPR', 'HR'}


def text_of(src):
    s = re.sub(r'<[^>]+>', ' ', src)
    return html.unescape(re.sub(r'\s+', ' ', s))


def dms(v, deg):
    return int(v[:deg]) + int(v[deg:deg + 2]) / 60 + int(v[deg + 2:deg + 4]) / 3600


def parse(t):
    ids = list(re.finditer(r'\((EH[A-Z0-9]+)\)', t))
    out = []
    for i, m in enumerate(ids):
        body = t[m.end():ids[i + 1].start() if i + 1 < len(ids) else len(t)]
        c = re.match(r' Circle, radius ([\d.]+) (M|NM), centre (\d{6})N (\d{7})E\*?\. (\d+) FT (AMSL|AGL) GND (.*)', body)
        if not c:
            continue  # polygonen (bv. TERLET 1, MALDEN AREA) zitten al als luchtruim in de app
        # naam = de hoofdletterwoorden vlak vóór "(EH…)", zonder staartwoorden van de vorige regel
        toks = t[max(0, m.start() - 80):m.start()].split()
        name = []
        for tok in reversed(toks):
            if tok in STOP or not re.fullmatch(r"[A-Z0-9'\-/().]+", tok) or re.fullmatch(r'[\d.:]+', tok) or tok.endswith('.') and tok != 'ST.':
                break
            name.insert(0, tok)
        rest = c.group(7)
        # de rest loopt door tot de naam van het volgende terrein: die eraf halen
        nxt = ' '.join(t[ids[i + 1].start() - 80:ids[i + 1].start()].split()[-len(name) or -1:]) if i + 1 < len(ids) else ''
        typ = ('hg' if re.search(r'Paragliding|Hanggliding', rest) else
               'gld' if re.search(r'\bGliding\b', rest) else
               'uas' if re.search(r'\bUAS\b', rest) else
               'ulm' if re.search(r'\bULM\b', rest) else None)
        if not typ:
            continue
        r = float(c.group(1)) * (1.852 if c.group(2) == 'NM' else 0.001)
        op = re.split(r' \+31| UDP| \d\d (?:JAN|FEB|MAR|APR|MAY|JUN|JUL|AUG|SEP|OCT|NOV|DEC)| MON| WED| FRI| SAT| APR-| 0[0-9]{3}-', rest)[0].strip()
        if op in ('', 'UDP') or re.match(r'^(UDP|ULM|UAS|Paragliding)\b|^\d', op):
            op = ''
        com = re.search(r'COM CH: ([\d.]+)', rest)
        out.append(dict(typ=typ, name=' '.join(name).title().replace("'S-", "'s-"), ident=m.group(1),
                        lon=round(dms(c.group(4), 3), 5), lat=round(dms(c.group(3), 2), 5), r=round(r, 3),
                        top=int(c.group(5)), ref=c.group(6), op=op[:60], com=com.group(1) if com else '',
                        nowinch='No winch' in rest))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--bbox', default='4.75,51.2,6.25,52.15')
    ap.add_argument('--src', default=None, help='pad naar EH-ENR_5.5-en-GB.html (standaard: branch data/eaip)')
    ap.add_argument('--check', action='store_true', help='alleen tonen, index.html niet aanpassen')
    a = ap.parse_args()
    x0, y0, x1, y1 = map(float, a.bbox.split(','))
    src = open(a.src, encoding='utf-8').read() if a.src else subprocess.run(
        ['git', 'show', 'origin/data/eaip:eaip/EH-ENR_5.5-en-GB.html'], cwd=ROOT, capture_output=True, text=True, check=True).stdout
    rows = [e for e in parse(text_of(src)) if x0 <= e['lon'] <= x1 and y0 <= e['lat'] <= y1]
    rows.sort(key=lambda e: (e['typ'], e['name'], e['ident']))
    lines = ['|'.join(str(e[k]) for k in ('typ', 'name', 'ident', 'lon', 'lat', 'r', 'top', 'ref', 'op', 'com')) + ('|nowinch' if e['nowinch'] else '') for e in rows]
    from collections import Counter
    print(Counter(e['typ'] for e in rows), file=sys.stderr)
    if a.check:
        print('\n'.join(lines)); return
    p = os.path.join(ROOT, 'index.html')
    s = open(p, encoding='utf-8').read()
    blk = '<script type="text/plain" id="enr55">\n' + '\n'.join(lines) + '\n</script>'
    if 'id="enr55"' in s:
        s = re.sub(r'<script type="text/plain" id="enr55">.*?</script>', lambda _: blk, s, flags=re.S)
    else:
        s = s.replace('<script type="importmap">', blk + '\n<script type="importmap">', 1)
    open(p, 'w', encoding='utf-8').write(s)
    print(f'{len(rows)} terreinen → index.html', file=sys.stderr)


if __name__ == '__main__':
    main()
