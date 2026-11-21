#!/usr/bin/env bash
# Verkenning in GitHub Actions (Christian 21 nov akkoord): wat is bereikbaar, hoe ziet het Geoportaal eruit?
set -u
mkdir -p probe
for u in "https://geoportaal.lvnl.nl" \
         "https://geoservices.lvnl.nl/arcgis/rest/services/VFRchart/Airspaces/MapServer/24/query?where=1%3D1&outFields=ident,nam&returnGeometry=false&f=json" \
         "https://overpass-api.de/api/status" \
         "https://eaip.lvnl.nl" ; do
  n=$(echo "$u" | sed 's#https://##; s#[^a-zA-Z0-9]#_#g' | cut -c1-60)
  code=$(curl -sSL -m 60 -o "probe/$n.body" -w '%{http_code} %{content_type} %{url_effective}' "$u" || echo "ERR")
  echo "$code  $u" >> probe/summary.txt
done
grep -oE 'href="[^"]+"' probe/geoportaal_lvnl_nl.body 2>/dev/null | sort -u | head -300 > probe/geoportaal_links.txt || true
ls -la probe >> probe/summary.txt
