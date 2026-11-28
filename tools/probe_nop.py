#!/usr/bin/env python3
"""Spike 1a (BACKLOG P1, 28 nov): welke dataverzoeken doet de publieke NOP (Eurocontrol Public Portal) voor de EAUP/EUUP?
Eenmalig, in GitHub Actions; legt alleen URL's, status en een kort stukje antwoord vast (geen gebruik in de app tot het NOP Office antwoordt)."""
import asyncio, json, re
from playwright.async_api import async_playwright

URL = 'https://www.public.nm.eurocontrol.int/PUBPORTAL/gateway/spec/index.html'

async def main():
    out = []
    async with async_playwright() as p:
        b = await p.chromium.launch(); pg = await b.new_page()
        async def on_resp(r):
            if r.request.resource_type in ('xhr', 'fetch', 'document'):
                body = ''
                try: body = (await r.text())[:400]
                except Exception: pass
                out.append({'url': r.url, 'status': r.status, 'type': r.request.resource_type, 'method': r.request.method, 'body': body})
        pg.on('response', lambda r: asyncio.ensure_future(on_resp(r)))
        await pg.goto(URL, wait_until='networkidle', timeout=90000); await pg.wait_for_timeout(5000)
        txt = await pg.inner_text('body'); open('probe/nop_text.txt', 'w').write(txt[:20000])
        await pg.screenshot(path='probe/nop_home.png', full_page=True)
        for label in ('AUP', 'EAUP', 'European AUP/UUP', 'AUP/UUP'):
            try:
                el = pg.get_by_text(re.compile(label, re.I)).first
                if await el.count():
                    await el.click(timeout=5000); await pg.wait_for_timeout(8000)
                    await pg.screenshot(path='probe/nop_aup.png', full_page=True)
                    open('probe/nop_aup_text.txt', 'w').write((await pg.inner_text('body'))[:30000]); break
            except Exception as ex:
                out.append({'click': label, 'error': str(ex)[:200]})
        await b.close()
    json.dump(out, open('probe/nop_requests.json', 'w'), indent=1)
    print(len(out), 'verzoeken')

asyncio.run(main())
