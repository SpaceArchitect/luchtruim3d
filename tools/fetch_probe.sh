#!/usr/bin/env bash
# Verkenning in GitHub Actions (Christian 21 nov akkoord): eAIP-structuur van de huidige AIRAC-editie.
set -u
mkdir -p probe
UA="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0 Safari/537.36"
get(){ curl -sSL -m 60 -A "$UA" -H 'Accept-Language: nl-NL,nl;q=0.9' -o "$2" -w "%{http_code} $1\n" "$1" >> probe/summary.txt; }
E="https://eaip.lvnl.nl/AIRAC%20AMDT%2011-2026_2026_10_29"
get "$E/index.html" probe/ed_index.html
grep -oE '(href|src)="[^"]+"' probe/ed_index.html | head -50 > probe/ed_links.txt
for f in $(grep -oE '(href|src)="[^"#]+\.html?"' probe/ed_index.html | sed -E 's/.*="([^"]+)"/\1/' | tr '\\' '/' | head -5); do
  get "$E/$f" "probe/sub_$(basename "$f")"
  grep -oE 'href="[^"]+"' "probe/sub_$(basename "$f")" | head -80 >> probe/ed_links.txt
done
ls -la probe >> probe/summary.txt
