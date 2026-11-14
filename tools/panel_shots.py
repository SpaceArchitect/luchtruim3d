#!/usr/bin/env python3
"""Maakt het materiaal voor de panelronde (02-instructies D1): screenshots per schermvorm + camerasporen bij gebaren.
Gebruik: python3 tools/panel_shots.py [uitmap]   (standaard /tmp/panel)"""
import asyncio, json, os, sys, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import e2e
from playwright.async_api import async_playwright

OUT = sys.argv[1] if len(sys.argv) > 1 else '/tmp/panel'
LOG = []

async def shot(a, name, note):
    p = f'{OUT}/{a.form}_{name}.png'; await a.pg.screenshot(path=p); LOG.append(f'{os.path.basename(p)} — {note}')

async def cam_trace(a, label, gesture):
    await a.ev('()=>{window.__T=[];const v=window.__vfr,f=()=>{const c=v.camera.position,p=v.PLANE;window.__T.push([performance.now(),+(Math.atan2(c.x-p.x,-c.z-p.n)*180/Math.PI).toFixed(1),+v.dbg.CAM.dist.toFixed(2),+c.y.toFixed(2)]);if(window.__T.length<600)requestAnimationFrame(f)};requestAnimationFrame(f)}')
    await gesture(); await a.wait(2500)
    T = await a.ev('()=>window.__T')
    t0 = T[0][0]
    rows = [f'{(t-t0)/1000:5.2f}s yaw={y:7.1f}° zoom={d:4.2f} hoogte={h:5.2f}' for t, y, d, h in T[::3]]
    open(f'{OUT}/{a.form}_cam_{label}.txt', 'w').write('\n'.join(rows))
    LOG.append(f'{a.form}_cam_{label}.txt — cameraspoor (tijd, kijkhoek rond toestel, zoom, camerahoogte) bij: {label}')

async def gestures(a):
    cdp = await a.ctx.new_cdp_session(a.pg)
    vw = a.pg.viewport_size; cx, cy = vw['width'] * .45, vw['height'] * .5
    async def t(kind, pts):
        await cdp.send('Input.dispatchTouchEvent', {'type': kind, 'touchPoints': [{'x': x, 'y': y, 'id': i} for i, (x, y) in enumerate(pts)]})
    async def drag1():
        await t('touchStart', [(cx, cy)])
        for k in range(20): await t('touchMove', [(cx + k * 9, cy + k * 2)]); await a.wait(30)
        await shot(a, 'cam_1vinger_tijdens', '1 vinger slepen naar rechts, vinger nog op het scherm')
        await t('touchEnd', []); await a.wait(400); await shot(a, 'cam_1vinger_na0.4s', '0,4 s na loslaten (veert terug?)')
    async def pinch():
        await t('touchStart', [(cx - 30, cy), (cx + 30, cy)])
        for k in range(20): await t('touchMove', [(cx - 30 - k * 6, cy), (cx + 30 + k * 6, cy)]); await a.wait(30)
        await shot(a, 'cam_knijpen_uit', '2 vingers uit elkaar (inzoomen?)'); await t('touchEnd', [])
    async def pinchpan():
        await t('touchStart', [(cx - 40, cy), (cx + 40, cy)])
        for k in range(20): await t('touchMove', [(cx - 40 + k * 2, cy + k * 5), (cx + 40 - k * 2, cy + k * 5)]); await a.wait(30)
        await shot(a, 'cam_2vingers_schuiven', '2 vingers samen omlaag schuiven + iets knijpen'); await t('touchEnd', [])
    async def hold_and_drag():
        b = await a.pg.locator('#ctrl [data-k=arrowup]').bounding_box()
        bx, by = b['x'] + b['width'] / 2, b['y'] + b['height'] / 2
        await t('touchStart', [(bx, by)])
        await t('touchStart', [(bx, by), (cx, cy)])
        for k in range(15): await t('touchMove', [(bx, by), (cx - k * 8, cy)]); await a.wait(30)
        await shot(a, 'cam_stijgen_en_slepen', 'duim op ▲ (stijgen) en tegelijk met andere vinger rondkijken')
        await t('touchEnd', [])
    for label, g in (('1vinger_slepen', drag1), ('knijpen', pinch), ('2vingers_knijpen_schuiven', pinchpan), ('stijgen_plus_slepen', hold_and_drag)):
        await cam_trace(a, label, g)

async def main():
    os.makedirs(OUT, exist_ok=True)
    url = e2e.serve()
    async with async_playwright() as p:
        b = await p.chromium.launch(args=e2e.ARGS)
        for form in ('p7l', 'p7', 'se', 'desk'):
            a = await e2e.new_app(p, b, form, url)
            await shot(a, '01_welkom', 'welkomstscherm')
            await a.hit('#modal [data-ac=map]'); vw = a.pg.viewport_size
            await a.tap_xy(vw['width'] * .5, vw['height'] * .55); await a.frames(3)
            await shot(a, '02_kaart_sonde', 'kaartmodus, getikt op de grond (sonde)')
            for ac in ('glider', 'motor', 'balloon'):
                await a.fly(ac); await a.frames(3)
                await shot(a, f'03_vliegen_{ac}', f'vliegen met {ac}, startmelding/opdracht')
            await a.fly('glider')
            e = await a.ev(e2e.JS_FREE_EDGE, ['EHEH', 2.5, 1000])
            await a.place(e[0], e[1], 1000, e[2], paused=False)
            await a.ev('()=>{const v=window.__vfr;v.TASK="Vlieg naar de Dommel (8 km)";v.GOAL={x:v.PLANE.x+6,n:v.PLANE.n,name:"de Dommel"}}')
            for _ in range(80):
                await a.frames(2)
                if await a.v('v.NOTICE'): break
            await shot(a, '04_waarschuwing_ctr', 'waarschuwing vóór Eindhoven CTR met knop Klaring aanvragen')
            if await a.visible('#banner [data-rt^=open]'):
                await a.hit('#banner [data-rt^=open]'); await shot(a, '05_radio_oproep', 'kies je eerste oproep (3 opties)')
            await e2e.weekend(a)
            e = await a.ev(e2e.JS_FREE_EDGE, ['EHVKRMZ', 1.5, 1000])
            if e:
                await a.place(e[0], e[1], 1000, e[2], paused=False)
                for _ in range(80):
                    await a.frames(2)
                    if await a.v('v.NOTICE'): break
                await shot(a, '06_rmz_volkel', 'weekend: Volkel CTR dicht → RMZ, eerst oproepen Dutch MIL Info')
            await a.ev('()=>{const v=window.__vfr;v.NOTICE="";v.PAUSED=false;v.WARNED.clear();v.hudTick()}')
            await a.hit('#btnPanel'); await shot(a, '07_weergave', 'menu Weergave open'); await a.hit('#btnPanel')
            if a.touch:
                ang = await a.v('v.tiltAng()')
                await a.ev(e2e.SEND, e2e.orient(0, 0, ang)); await a.frames(2)
                await a.ev('()=>{const v=window.__vfr;v.NOTICE="";v.PAUSED=false;v.hudTick()}'); await a.frames(3)
                await shot(a, '08_kantelmodus', 'kantelmodus (standaard op telefoon): stuurknoppen weg, alleen ⏪ ❚❚ ⏩')
                await a.ev(e2e.SEND, e2e.orient(18, 15, ang)); await a.wait(1200)
                await shot(a, '09_kantelen_bocht_klim', 'telefoon rechts gekanteld + naar je toe: bocht rechts en klimmen')
                await a.ev(e2e.SEND, e2e.orient(0, 0, ang))
                await a.hit('#btnPanel'); await a.hit('label[for=optTilt]'); await a.hit('#btnPanel')
                st = await a.v('v.PLANE'); await a.place(st['x'], st['n'], 1500, st['hdg'], paused=True)
                await gestures(a)
            await a.ctx.close()
        await b.close()
    open(f'{OUT}/INDEX.txt', 'w').write('\n'.join(LOG))
    print(len(LOG), 'items in', OUT)

asyncio.run(main())
