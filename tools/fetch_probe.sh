#!/usr/bin/env bash
# Verkenning in GitHub Actions (Christian 21 nov akkoord): eAIP-paginapaden (AD 2 Deelen).
set -u
mkdir -p probe
UA="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0 Safari/537.36"
get(){ curl -sSL -m 60 -A "$UA" -H 'Accept-Language: nl-NL,nl;q=0.9' -o "$2" -w "%{http_code} %{size_download} $1\n" "$1" >> probe/summary.txt; }
E="https://eaip.lvnl.nl/AIRAC%20AMDT%2011-2026_2026_10_29"
get "$E/toc-frameset.html" probe/toc.html
grep -oE '(href|src)="[^"]+"' probe/toc.html | head -40 > probe/toc_links.txt
for f in $(grep -oE 'src="[^"]+"' probe/toc.html | sed -E 's/src="([^"]+)"/\1/' | sed 's/ /%20/g' | tr '\\' '/'); do get "$E/$f" "probe/toc_$(echo $f | tr '/%' '__')"; grep -oE 'href="[^"]*(AD-2|ENR-5)[^"]*"' "probe/toc_$(echo $f | tr '/%' '__')" | head -40 >> probe/toc_links.txt; done
for p in "EH-AD-2.EHDL-en-GB.html" "eAIP/EH-AD-2.EHDL-en-GB.html" "html/eAIP/EH-AD-2.EHDL-en-GB.html" "EH-AD-2.EHDL-nl-NL.html"; do get "$E/$p" "probe/try_$(echo $p | tr '/' '_')"; done
ls -la probe >> probe/summary.txt
