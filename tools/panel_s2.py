#!/usr/bin/env python3
"""Panelmateriaal S2: gevaren standaard aan + vervagende labels, per schermvorm.
Gebruik: E2E_PORT=8773 python3 tools/panel_s2.py [uitmap]"""
import asyncio, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import e2e
from playwright.async_api import async_playwright
OUT = sys.argv[1] if len(sys.argv) > 1 else '/tmp/panel_s2'
async def main():
    os.makedirs(OUT, exist_ok=True); url = e2e.serve(); log = []
    async with async_playwright() as p:
        b = await p.chromium.launch(args=e2e.ARGS)
        for form in ('desk', 'p7', 'p7l', 'se'):
            a = await e2e.new_app(p, b, form, url)
            await a.hit('#modal [data-ac=map]'); await a.frames(4)
            await a.pg.screenshot(path=f'{OUT}/{form}_1_kaart.png')
            L = await a.ev(e2e.JS_AIRLBL); log.append(f'{form} kaart: ' + ', '.join(f'{i}({l}) {o:.2f}' for i, l, o in L))
            if not a.touch:
                await a.pg.mouse.move(640, 500)
                for _ in range(4): await a.pg.mouse.wheel(0, 250); await a.wait(120)
                await a.wait(700); await a.frames(4); await a.pg.screenshot(path=f'{OUT}/{form}_2_uitgezoomd.png')
                L = await a.ev(e2e.JS_AIRLBL); log.append(f'{form} uitgezoomd: ' + ', '.join(f'{i} {o:.2f}' for i, l, o in L))
            await a.hit('#btnBig'); await a.hit('#a11yHC'); await a.frames(4)
            await a.pg.screenshot(path=f'{OUT}/{form}_3_hoogcontrast.png'); await a.ctx.close()
            a = await e2e.new_app(p, b, form, url); await a.hit('#modal [data-ac=glider]'); await a.wait(1500)
            await a.pg.screenshot(path=f'{OUT}/{form}_4_vliegen.png'); await a.ctx.close()
        await b.close()
    open(f'{OUT}/log.txt', 'w').write('\n'.join(log)); print('\n'.join(log))
asyncio.run(main())
