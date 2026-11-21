#!/usr/bin/env bash
# Verkenning in GitHub Actions (Christian 21 nov akkoord): eAIP/LVNL/OSM met browser-headers, en via Playwright.
set -u
mkdir -p probe
UA="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0 Safari/537.36"
for u in "https://eaip.lvnl.nl" \
         "https://geoservices.lvnl.nl/arcgis/rest/services/VFRchart/Airspaces/MapServer/24/query?where=1%3D1&outFields=ident,nam&returnGeometry=false&f=json" \
         "https://overpass-api.de/api/status" \
         "https://luchtruim3d.nl" \
         "https://lvnl.maps.arcgis.com/sharing/rest/search?q=owner%3A*%20AND%20type%3A(%22Feature%20Service%22%20OR%20%22CSV%22%20OR%20%22Shapefile%22%20OR%20%22GeoJson%22%20OR%20%22File%20Geodatabase%22)&num=100&f=json" \
         "https://geoportaal.lvnl.nl/api/search/v1/collections/all/items?limit=100" ; do
  n=$(echo "$u" | sed 's#https://##; s#[^a-zA-Z0-9]#_#g' | cut -c1-60)
  code=$(curl -sSL -m 60 -A "$UA" -H 'Accept: text/html,application/json,*/*' -H 'Accept-Language: nl-NL,nl;q=0.9' -o "probe/$n.body" -w '%{http_code} %{content_type}' "$u" 2>probe/$n.err || echo "ERR $(cat probe/$n.err)")
  echo "$code  $u" >> probe/summary.txt
done
# eAIP via echte browser (Playwright)
pip install -q playwright >/dev/null 2>&1 && python -m playwright install --with-deps chromium >/dev/null 2>&1
python - <<'PY' >> probe/summary.txt 2>&1
import asyncio
from playwright.async_api import async_playwright
async def m():
    async with async_playwright() as p:
        b = await p.chromium.launch(); pg = await b.new_page(locale='nl-NL')
        for u in ['https://eaip.lvnl.nl', 'https://luchtruim3d.nl']:
            try:
                r = await pg.goto(u, timeout=60000); await pg.wait_for_timeout(3000)
                t = (await pg.inner_text('body'))[:300].replace('\n', ' ')
                print('PW', r.status if r else None, u, '|', await pg.title(), '|', t)
                open('probe/pw_' + u.split('//')[1].replace('.', '_') + '.html', 'w').write(await pg.content())
            except Exception as e: print('PW ERR', u, e)
        await b.close()
asyncio.run(m())
PY
echo "LIVE-CHECK goalVizTick: $(grep -c goalVizTick probe/luchtruim3d_nl.body) MISSIONS: $(grep -c "const MISSIONS" probe/luchtruim3d_nl.body)" >> probe/summary.txt
ls -la probe >> probe/summary.txt
