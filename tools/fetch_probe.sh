#!/usr/bin/env bash
# Verkenning in GitHub Actions. 26 nov: spike militaire gebieden (BACKLOG P1-9): zijn AUP/UUP en NOTAM publiek en machineleesbaar, en onder welke voorwaarden?
set -u
mkdir -p probe
UA="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0 Safari/537.36"
get(){ curl -sSL -m 60 -A "$UA" -H 'Accept-Language: en;q=0.9' -o "probe/$2" -w "%{http_code} %{size_download} %{url_effective} $1\n" "$1" >> probe/summary.txt 2>>probe/errors.txt || echo "FAIL $1" >> probe/summary.txt; }
get "https://www.public.nm.eurocontrol.int/PUBPORTAL/gateway/spec/index.html" nop_index.html
get "https://www.public.nm.eurocontrol.int/PUBPORTAL/gateway/spec/" nop_spec.html
get "https://www.eurocontrol.int/service/network-manager-business-business-b2b-web-services" b2b.html
get "https://www.eurocontrol.int/publication/eurocontrol-network-manager-terms-and-conditions" nm_terms.html
get "https://www.eurocontrol.int/platform/network-operations-portal" nop_platform.html
get "https://www.ead.eurocontrol.int/cms-eadbasic/opencms/en/ead-solutions/ead-basic" ead_basic.html
get "https://www.ead.eurocontrol.int/cms-eadbasic/opencms/en/login/terms-and-conditions/" ead_terms.html
get "https://www.homebriefing.nl/" homebriefing.html
get "https://www.lvnl.nl/diensten/aeronautical-information-service" lvnl_ais.html
get "https://english.defensie.nl/topics/military-aviation-authority" mil.html
# snelle aanwijzingen: links naar AUP/UUP/download in de opgehaalde pagina's
for f in probe/*.html; do echo "== $f" >> probe/hints.txt; grep -oiE '(href|src)="[^"]*(aup|uup|fua|download|xml|json|csv|terms|b2b|notam)[^"]*"' "$f" | sort -u | head -30 >> probe/hints.txt; done
ls -la probe >> probe/summary.txt
