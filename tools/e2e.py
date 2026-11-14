#!/usr/bin/env python3
"""Regressiesuite Luchtruim in 3D (02-instructies D0).

Gebruik:  python3 tools/e2e.py [--seed N] [--forms desk,p7,p7l,se] [--only smoke|det|fuzz]
Vereist:  playwright (python) en three@0.160.0 in $THREE_DIR (default /home/claude/h/node_modules/three).
Alle bediening gaat via echte klikken/tikken (Playwright mouse/touchscreen/keyboard of CDP-touch),
nooit element.click(). Alleen de opzet van een scenario (positie, doel) gebeurt via window.__vfr.
"""
import asyncio, json, math, os, random, shutil, sys, tempfile, threading, http.server, functools, argparse
from playwright.async_api import async_playwright

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
THREE = os.environ.get('THREE_DIR', '/home/claude/h/node_modules/three')
PORT = 8766
ARGS = ['--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist']

def serve():
    d = tempfile.mkdtemp()
    html = open(os.environ.get('E2E_INDEX', os.path.join(ROOT, 'index.html')), encoding='utf-8').read()
    html = html.replace('https://cdn.jsdelivr.net/npm/three@0.160.0/', '/three/')
    open(os.path.join(d, 'index.html'), 'w', encoding='utf-8').write(html)
    os.symlink(THREE, os.path.join(d, 'three'))
    class Q(http.server.SimpleHTTPRequestHandler):
        def log_message(self, *a): pass
    h = functools.partial(Q, directory=d)
    srv = http.server.ThreadingHTTPServer(('127.0.0.1', PORT), h)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    return f'http://127.0.0.1:{PORT}/index.html?e2e'

FORMS = {'desk': dict(viewport={'width': 1280, 'height': 800}),
         'p7': 'Pixel 7', 'p7l': 'Pixel 7 landscape', 'se': 'iPhone SE'}
RES = {'smoke': [], 'det': [], 'fuzz': []}
SHOTS = os.environ.get('E2E_SHOTS', '/tmp/e2e-shots')

class Fail(Exception): pass
def ok(c, msg):
    if not c: raise Fail(msg)

class App:
    def __init__(s, pg, form, ctx):
        s.pg, s.form, s.ctx, s.errs = pg, form, ctx, []
        s.touch = form != 'desk'
        pg.on('pageerror', lambda e: s.errs.append('PAGEERR ' + str(e)[:200]))
        pg.on('console', lambda m: s.errs.append('CONSOLE ' + m.text[:200]) if m.type == 'error' else None)
    async def ev(s, js, arg=None): return await s.pg.evaluate(js, arg)
    async def v(s, expr): return await s.pg.evaluate('()=>{const v=window.__vfr;return ' + expr + '}')
    async def wait(s, ms): await s.pg.wait_for_timeout(ms)
    async def frames(s, n=3):  # wacht n echte animatieframes
        await s.pg.evaluate('n=>new Promise(r=>{let k=0;const f=()=>++k>=n?r():requestAnimationFrame(f);requestAnimationFrame(f)})', n)
    async def hit(s, sel):  # echte klik of tik in het midden van het element
        el = s.pg.locator(sel).first
        await el.wait_for(state='visible', timeout=8000)
        try: await el.scroll_into_view_if_needed(timeout=3000)
        except Exception: pass
        b = await el.bounding_box(); ok(b, f'{sel} heeft geen box')
        x, y = b['x'] + b['width'] / 2, b['y'] + b['height'] / 2
        if s.touch: await s.pg.touchscreen.tap(x, y)
        else: await s.pg.mouse.click(x, y, delay=90)
        await s.wait(350)
    async def hold(s, sel, ms):
        b = await s.pg.locator(sel).first.bounding_box()
        await s.pg.mouse.move(b['x'] + b['width'] / 2, b['y'] + b['height'] / 2)
        await s.pg.mouse.down(); await s.wait(ms); await s.pg.mouse.up(); await s.wait(150)
    async def tap_xy(s, x, y):
        if s.touch: await s.pg.touchscreen.tap(x, y)
        else: await s.pg.mouse.click(x, y, delay=60)
        await s.wait(250)
    async def visible(s, sel):
        return await s.pg.evaluate('s=>{const e=document.querySelector(s);if(!e)return false;const r=e.getBoundingClientRect(),c=getComputedStyle(e);return r.width>0&&r.height>0&&c.display!=="none"&&c.visibility!=="hidden"&&!e.classList.contains("hidden")}', sel)
    async def menus_open(s):
        return await s.pg.evaluate('''()=>{const vis=id=>{const e=document.getElementById(id);if(!e)return 0;const c=getComputedStyle(e);return c.display!=="none"&&!e.classList.contains("hidden")&&e.getBoundingClientRect().height>0?1:0};
          const m=(document.body.classList.contains("welcome")?0:vis("modal"));return ["panel","a11y","timePop"].filter(vis).concat(m?["modal"]:[])}''')
    async def sane(s):
        r = await s.v('{p:[v.PLANE.x,v.PLANE.n,v.PLANE.alt,v.PLANE.hdg],c:v.camera.position.toArray(),m:v.MODE}')
        ok(all(math.isfinite(a) for a in r['p'] + r['c']), f'NaN/inf in positie/camera: {r}')
        ok(r['m'] in ('map', 'fly'), f'onmogelijke MODE {r["m"]}')
    async def no_errs(s, where):
        e = [x for x in s.errs if 'favicon' not in x]
        ok(not e, f'JS-fouten ({where}): {e[:3]}')
    async def shot(s, name):
        os.makedirs(SHOTS, exist_ok=True); await s.pg.screenshot(path=f'{SHOTS}/{s.form}_{name}.png')
    async def fly(s, ac):  # via de echte knoppen naar vliegen met toestel ac
        if not await s.visible('#modal [data-ac=%s]' % ac):
            if await s.v('v.MODE') != 'fly': await s.hit('#btnMode')
            if not await s.visible('#modal [data-ac=%s]' % ac):
                if not await s.visible('#btnAc'): await s.hit('#btnPanel')
                await s.hit('#btnAc')
        await s.hit('#modal [data-ac=%s]' % ac)
        await s.frames(3)
        ok(await s.v('v.MODE') == 'fly' and await s.v('v.ACTYPE') == ac, f'niet in vliegmodus met {ac}')
    async def place(s, x, n, alt, hdg, paused=False):
        await s.ev('([x,n,a,h,p])=>{const v=window.__vfr;Object.assign(v.PLANE,{x,n,alt:a,hdg:h,bank:0,pitch:0});v.NOTICE="";v.PAUSED=p;v.WARNED.clear();v.FAILS.clear();v.CLR.clear();v.REFUSED.clear();v.GOAL=null;v.TASK="";v.hudTick()}', [x, n, alt, hdg, paused])

async def new_app(p, b, form, url):
    spec = FORMS[form]
    kw = dict(p.devices[spec]) if isinstance(spec, str) else dict(spec)
    kw['device_scale_factor'] = 1
    ctx = await b.new_context(**kw)
    pg = await ctx.new_page(); a = App(pg, form, ctx)
    await pg.goto(url); await a.wait(1800); await a.frames(2)
    return a

async def run(layer, name, form, fn, a):
    try:
        await fn(a); await a.no_errs(name); await a.sane()
        RES[layer].append((form, name, 'OK', ''))
    except Exception as e:
        RES[layer].append((form, name, 'FAIL', str(e)[:300]))
        try: await a.shot('FAIL_' + name)
        except Exception: pass
        a.errs.clear()

# ---------------- smoke ----------------
async def t_load(a):
    ok(await a.ev('()=>!!window.__vfr'), 'app niet gestart (JS-fout bij laden)')
    ok(await a.visible('#modal'), 'welkomstvenster niet zichtbaar')
    ok('Alleen voor educatie' in await a.ev('()=>document.body.innerText'), 'disclaimer ontbreekt')

async def t_map_probe(a):
    await a.hit('#modal [data-ac=map]'); await a.frames(3)
    ok(await a.v('v.MODE') == 'map', 'niet in kaartmodus')
    vw = a.pg.viewport_size
    await a.tap_xy(vw['width'] * .5, vw['height'] * .55); await a.frames(3)
    ok(await a.visible('#info'), 'sonde-paneel niet zichtbaar na tik op de grond')
    await a.shot('map_probe')

async def t_aircraft(a):
    for ac in ('glider', 'motor', 'balloon'):
        await a.fly(ac)
        st = await a.v('v.PLANE')
        await a.place(st['x'], st['n'], 1500, st['hdg'], paused=True)
        await a.hit('#btnPause'); ok(not await a.v('v.PAUSED'), f'{ac}: start-knop hervat niet')
        alt0 = await a.v('v.PLANE.alt')
        if a.touch: await a.hold('#ctrl [data-k=arrowup]', 900)
        else: await a.pg.keyboard.down('ArrowUp'); await a.wait(900); await a.pg.keyboard.up('ArrowUp')
        alt1 = await a.v('v.PLANE.alt')
        ok(alt1 > alt0 or await a.v('v.PAUSED'), f'{ac}: stijgen werkt niet ({alt0}->{alt1})')
        if ac != 'balloon':
            await a.ev('()=>{window.__vfr.NOTICE="";window.__vfr.PAUSED=false}')
            h0 = await a.v('v.PLANE.hdg')
            if a.touch: await a.hold('#ctrl [data-k=arrowright]', 900)
            else: await a.pg.keyboard.down('ArrowRight'); await a.wait(900); await a.pg.keyboard.up('ArrowRight')
            h1 = await a.v('v.PLANE.hdg')
            ok(abs(((h1 - h0 + 540) % 360) - 180) > 2 or await a.v('v.PAUSED'), f'{ac}: draaien werkt niet')
        await a.ev('()=>{window.__vfr.NOTICE="";window.__vfr.PAUSED=false;window.__vfr.hudTick()}')
        await a.hit('#btnPause'); ok(await a.v('v.PAUSED'), f'{ac}: pauze werkt niet')
        await a.shot('fly_' + ac)
    await a.hit('#btnMode'); ok(await a.v('v.MODE') == 'map', 'terug naar kaart werkt niet')

async def t_modebtn(a):
    await a.hit('#modal [data-ac=glider]'); await a.frames(2)
    for _ in range(2):
        b = await a.pg.locator('#btnMode').bounding_box()
        ok(b['height'] < 52, f'modusknop over twee regels (h={b["height"]:.0f})')
        txt = (await a.pg.locator('#btnMode').inner_text()).strip()
        ok(txt in ('→ Kaart', '→ Vliegen'), f'modusknop tekst {txt!r}')
        await a.hit('#btnMode')

async def t_one_menu(a):
    await a.hit('#modal [data-ac=glider]'); await a.frames(2)
    await a.hit('#btnPanel'); ok(await a.menus_open() == ['panel'], 'Weergave opent niet')
    await a.hit('#btnBig'); ok(await a.menus_open() == ['a11y'], f'twee menu\'s open: {await a.menus_open()}')
    if await a.visible('#timeBtn'):
        await a.hit('#timeBtn'); ok(await a.menus_open() == ['timePop'], f'twee menu\'s open: {await a.menus_open()}')
        await a.hit('#timeBtn')
    await a.hit('#btnPanel'); await a.hit('#btnAc')
    ok(await a.menus_open() == ['modal'], f'weergavemenu blijft over toestelkeuze: {await a.menus_open()}')
    await a.hit('#modal [data-ac=motor]'); ok(await a.menus_open() == [], 'menu blijft open na toestelkeuze')

async def t_overlap(a):
    await a.hit('#modal [data-ac=glider]'); await a.frames(3)
    await a.ev('()=>{window.__vfr.NOTICE="";window.__vfr.hudTick()}'); await a.frames(2)
    r = await a.ev('''()=>{const ids=["btnMode","btnBig","btnPanel","timeBtn","banner","ctrl","loc","btnCam","tChip"];const R=[];
      for(const id of ids){const e=document.getElementById(id);if(!e)continue;const c=getComputedStyle(e),b=e.getBoundingClientRect();if(c.display==="none"||c.visibility==="hidden"||b.width<2||b.height<2)continue;R.push([id,b.left,b.top,b.right,b.bottom])}
      const o=[];for(let i=0;i<R.length;i++)for(let j=i+1;j<R.length;j++){const a=R[i],b=R[j];if(a[1]<b[3]-1&&b[1]<a[3]-1&&a[2]<b[4]-1&&b[2]<a[4]-1)o.push(a[0]+"×"+b[0])}
      const out=R.filter(x=>x[1]<-1||x[2]<-1||x[3]>innerWidth+1||x[4]>innerHeight+1).map(x=>x[0]);return {o,out}}''')
    await a.shot('overlap')
    ok(not r['o'], f'overlap: {r["o"]}'); ok(not r['out'], f'buiten beeld: {r["out"]}')

async def t_rotate(a):
    if a.form == 'desk': return
    await a.hit('#modal [data-ac=glider]'); await a.hit('#btnPause')
    vw = a.pg.viewport_size
    for _ in range(2):
        await a.pg.set_viewport_size({'width': vw['height'], 'height': vw['width']}); await a.frames(4)
        vw = a.pg.viewport_size; await a.sane()
        b = await a.pg.locator('#banner').bounding_box()
        ok(b and b['x'] >= -1 and b['x'] + b['width'] <= vw['width'] + 1, 'banner buiten beeld na draaien')
    await a.hit('#btnPanel'); await a.pg.set_viewport_size({'width': vw['height'], 'height': vw['width']}); await a.frames(3)
    ok(len(await a.menus_open()) <= 1, 'meer menu\'s open na draaien in menu')

# ---------------- deterministisch (D2) ----------------
JS_FIND = '''(ident)=>{const v=window.__vfr;const f=v.LAYERS.find(g=>g.ident===ident);return f?{lp:f.lp,lo:f.lo,hi:f.hi,layer:f.layer}:null}'''
JS_EDGE = '''([ident,hdg,alt])=>{const v=window.__vfr,f=v.LAYERS.find(g=>g.ident===ident),h=hdg*Math.PI/180;let x=f.lp[0],n=f.lp[1];
  for(let d=0;d<40;d+=.05){const ax=f.lp[0]+Math.sin(h)*d,an=f.lp[1]+Math.cos(h)*d;if(!v.featsAt(ax,an).includes(f))return [ax,an]}return null}'''

async def d_task_text(a):
    r = await a.ev('''()=>{const v=window.__vfr,o=[];for(let k=0;k<60;k++){const x=v.PLANE.x+(Math.random()-.5)*40,n=v.PLANE.n+(Math.random()-.5)*40;for(const ac of ["glider","balloon"]){const t=v.pickTask(x,n,Math.random()*360,ac);if(t)o.push(t)}}return o}''')
    ok(r, 'geen opdrachten gevonden')
    bad = [t for t in r if not (t.startswith('Vlieg naar') or t.startswith('Drijf naar'))]
    ok(not bad, f'opdracht niet "vlieg naar": {bad[:2]}')
    await a.hit('#modal [data-ac=glider]'); await a.hit('#btnPause'); await a.frames(3)
    if await a.v('!!v.TASK'):
        h = await a.ev('()=>{const t=document.querySelector("#banner .task");return t?[t.scrollHeight,parseFloat(getComputedStyle(t).lineHeight)||16,t.innerText]:null}')
        ok(h and h[0] <= h[1] * 1.6 + 2, f'opdrachtregel niet één regel: {h}')

async def d_banner_rmz(a):
    await a.hit('#modal [data-ac=glider]')
    if await a.visible('#timeBtn'):
        await a.hit('#timeBtn'); await a.hit('#timePop [data-tm=weekend]')
        if await a.visible('#timePop'): await a.hit('#timeBtn')
    else:
        await a.ev('()=>{}')  # tijdknop verborgen op smalle schermen: dan geldt "nu"
    rmz = await a.ev('()=>{const v=window.__vfr;return v.LAYERS.filter(f=>f.layer==="RMZ"&&v.AIPINFO[f.ident]&&/MIL Info/.test(v.AIPINFO[f.ident].unit)).map(f=>[f.ident,f.lp,f.lo])}')
    ok(rmz, 'geen RMZ met MIL Info in data')
    hit = None
    for ident, lp, lo in rmz:
        await a.place(lp[0], lp[1], max(300, lo + 200), 0, paused=True); await a.frames(2)
        txt = await a.ev('()=>document.querySelector("#banner .head")?.innerText||""')
        if 'RMZ' in txt: hit = txt; break
    ok(hit is not None, 'RMZ niet actief op gekozen tijd (geen test mogelijk)')
    ok('📻 Dutch MIL Info 132.350' in hit, f'RMZ-frequentie niet zichtbaar: {hit!r}')
    ok('MHz' not in hit and '▾' not in hit, f'MHz of ▾ in banner: {hit!r}')
    h = await a.ev('()=>{const t=document.querySelector("#banner .head");return [t.scrollHeight,parseFloat(getComputedStyle(t).lineHeight)||18]}')
    ok(h[0] <= h[1] * 1.6 + 2, f'statusregel niet één regel: {h}')
    await a.shot('banner_rmz')

async def d_refused(a):
    await a.hit('#modal [data-ac=motor]')
    ctr = await a.ev('()=>{const v=window.__vfr;const f=v.LAYERS.find(g=>g.layer==="CTR"&&g.ident==="EHEH");return f&&f.ident}')
    ok(ctr, 'geen CTR')
    e = await a.ev(JS_EDGE, [ctr, 90, 1000]); ok(e, 'rand CTR niet gevonden')
    await a.place(e[0] + 1.6, e[1], 1000, 270, paused=True)  # 1,6 km buiten de rand, koers erheen
    await a.ev('(id)=>window.__vfr.RTOUT.set(id,{t:performance.now(),o:"traffic"})', ctr)  # ATC weigert
    await a.hit('#btnPause')
    n = ''
    for _ in range(120):
        await a.frames(2); n = await a.v('v.NOTICE') or ''
        if n: break
    ok('Klaring aanvragen' in n, f'eerste klaringsmelding ontbreekt: {n[:80]!r}')
    await a.hit('#banner [data-rt^=open]')
    good = await a.ev('()=>[...document.querySelectorAll("#banner .rt")].findIndex(b=>b.querySelectorAll("span").length===6&&!/PH-/.test(b.querySelector("span").textContent))')
    await a.hit(f'#banner .rt >> nth={good}')
    ok('Geweigerd' in (await a.v('v.NOTICE') or ''), 'weigering niet getoond')
    await a.hit('#banner [data-rt=close]')
    if await a.v('v.PAUSED'): await a.hit('#btnPause')
    for _ in range(200):
        await a.frames(2); n = await a.v('v.NOTICE') or ''
        inside = await a.ev('(id)=>{const v=window.__vfr;return v.featsAt(v.PLANE.x,v.PLANE.n).some(f=>f.ident===id)}', ctr)
        if n or inside: break
    ok('Geen klaring' in n, f'geen waarschuwing na weigering: {n[:80]!r}')
    ok(not inside, 'waarschuwing pas binnen de CTR (te laat)')

async def d_adjacent_clearance(a):  # Christian 14 nov: klaring Eindhoven, De Peel in → "mislukt zonder klaring" zonder melding
    await a.hit('#modal [data-ac=glider]')
    e = await a.ev(JS_EDGE, ['EHDP', 270, 1000]); ok(e, 'rand De Peel niet gevonden')
    inEH = await a.ev('(p)=>window.__vfr.featsAt(p[0]-0.3,p[1]).some(f=>f.ident==="EHEH")', e)
    ok(inEH, 'testopzet: west van De Peel ligt niet in Eindhoven CTR')
    await a.place(e[0] - 0.6, e[1], 1000, 90, paused=False)
    await a.ev('()=>{const v=window.__vfr;v.CLR.add("EHEH");v.GOAL={x:v.PLANE.x+3,n:v.PLANE.n,name:"Test"}}')
    for _ in range(60):
        await a.frames(2)
        if await a.ev('()=>{const v=window.__vfr;return v.featsAt(v.PLANE.x,v.PLANE.n).some(f=>f.ident==="EHDP")}'): break
    await a.frames(4)
    f = await a.ev('()=>[...window.__vfr.FAILS.values()]')
    ok(not any('Peel' in x for x in f), f'De Peel telt als zonder klaring terwijl Eindhoven TWR klaring gaf: {f}')

async def d_warn_lead(a):  # Christian 14 nov: minstens ~2 s reactietijd, niet te vroeg
    await a.hit('#modal [data-ac=motor]')
    e = await a.ev(JS_EDGE, ['EHEH', 90, 1000])
    await a.place(e[0] + 25, e[1], 1000, 270, paused=False)
    await a.ev('()=>window.__vfr.setTempo(6)')
    t0 = None
    for _ in range(400):
        await a.frames(1)
        n = await a.v('v.NOTICE')
        if n: break
    ok(n and 'klaring' in n, f'geen klaringsmelding: {n!r}')
    r = await a.ev('(id)=>{const v=window.__vfr;const h=v.PLANE.hdg*Math.PI/180;let d=0;while(d<40&&!v.featsAt(v.PLANE.x+Math.sin(h)*d,v.PLANE.n+Math.cos(h)*d).some(f=>f.ident===id))d+=.05;return [d,v.AC.motor.kt*1.852/3600*v.TEMPO]}', 'EHEH')
    secs = r[0] / r[1]
    ok(secs >= 2, f'melding te laat: {secs:.1f} s voor de grens')
    ok(secs <= 20, f'melding te vroeg: {secs:.1f} s voor de grens')

async def d_goal_line(a):
    await a.hit('#modal [data-ac=glider]')
    r = await a.ev('''()=>{const v=window.__vfr;const f=v.TASKF.find(f=>f.t==="R"&&f.pts.length>8);const i=Math.floor(f.pts.length/2),[x,n]=f.pts[i],[x2,n2]=f.pts[i+1];const L=Math.hypot(x2-x,n2-n)||1;return {pts:f.pts,name:f.name,x,n,px:-(n2-n)/L,pn:(x2-x)/L,g:f.pts[0]}}''')
    for off, want in ((0.3, True), (1.0, False)):
        await a.place(r['x'] + r['px'] * off, r['n'] + r['pn'] * off, 3000, 0, paused=False)
        await a.ev('(r)=>{const v=window.__vfr;v.GOAL={x:r.g[0],n:r.g[1],name:"de "+r.name,pts:r.pts};v.TASK="Vlieg naar de "+r.name}', r)
        await a.ev('()=>window.__vfr.hudTick()')
        n = await a.v('v.NOTICE') or ''
        got = 'Missie' in n
        ok(got == want, f'doel als lijn: {off} km van de weg → missie={got}, verwacht {want} ({n[:60]!r})')

async def d_balloon_past(a):
    await a.hit('#modal [data-ac=balloon]')
    st = await a.v('v.PLANE')
    await a.place(st['x'], st['n'], 800, st['hdg'], paused=False)
    await a.ev('()=>{const v=window.__vfr;v.GOAL={x:v.PLANE.x-0.1,n:v.PLANE.n-4.2,name:"Testdoel",min:1.7};v.TASK="Drijf naar Testdoel";v.hudTick()}')
    n = await a.v('v.NOTICE') or ''
    ok('Missie mislukt' in n and 'ballon' in n, f'ballon voorbij doel geen "mislukt": {n[:80]!r}')
    ok(await a.v('v.GOAL') is None, 'doel blijft staan na mislukt')
    await a.fly('glider')
    st = await a.v('v.PLANE')
    await a.place(st['x'], st['n'], 1500, st['hdg'], paused=False)
    await a.ev('()=>{const v=window.__vfr;v.GOAL={x:v.PLANE.x,n:v.PLANE.n-4.2,name:"Testdoel",min:1.7};v.hudTick()}')
    n = await a.v('v.NOTICE') or ''
    ok('Doel gemist' in n, f'zweefvliegtuig voorbij doel: {n[:60]!r}')

async def d_clearance_success(a):
    await a.hit('#modal [data-ac=motor]')
    ctr = await a.ev('()=>{const v=window.__vfr;const f=v.LAYERS.find(g=>g.layer==="CTR"&&g.lo===0&&v.AIPINFO[g.ident]);return f&&[f.ident,f.lp]}')
    await a.place(ctr[1][0], ctr[1][1], 800, 0, paused=False)
    await a.ev('(id)=>{const v=window.__vfr;v.CLR.add(id);v.GOAL={x:v.PLANE.x,n:v.PLANE.n,name:"Test"};v.hudTick()}', ctr[0])
    n = await a.v('v.NOTICE') or ''
    ok('met klaring' in n, f'"geslaagd met klaring" ontbreekt: {n[:90]!r}')

async def d_outside_nl(a):
    await a.hit('#modal [data-ac=glider]')
    p = await a.ev('()=>{const v=window.__vfr;for(let k=0;k<4000;k++){const x=v.PLANE.x+(Math.random()-.5)*120,n=v.PLANE.n+(Math.random()-.5)*120;if(!v.inNL(x,n)&&!v.featsAt(x,n).length)return [x,n]}return null}')
    ok(p, 'geen punt buiten NL gevonden')
    await a.place(p[0], p[1], 1500, 0, paused=True); await a.frames(2)
    t = await a.ev('()=>document.getElementById("banner").innerText')
    ok('Klasse G' not in t and 'klasse G' not in t, f'"Klasse G" buiten NL: {t[:80]!r}')

async def d_touch_smooth(a):  # Christian 14 nov: glitch bij slepen met de muis (ballon, desktop) → alle toestellen, alle vormen
    for ac in ('balloon', 'glider', 'motor'):
        await cam_smooth(a, ac)

async def cam_smooth(a, ac):
    await a.fly(ac)
    await a.ev('()=>{window.__vfr.PAUSED=true;window.__L=[];const f=()=>{const c=window.__vfr.camera.position;window.__L.push([c.x,c.y,c.z,window.__vfr.dbg.CAM.dist]);if(window.__L.length<400)requestAnimationFrame(f)};requestAnimationFrame(f)}')
    vw = a.pg.viewport_size; cx, cy = vw['width'] / 2, vw['height'] / 2
    if not a.touch:
        await a.pg.mouse.move(cx, cy); await a.pg.mouse.down()
        for k in range(25): await a.pg.mouse.move(cx + k * 14, cy + k * 2); await a.wait(25)
        for k in range(25): await a.pg.mouse.move(cx + 350 - k * 20, cy + 50 - k * 4); await a.wait(25)
        await a.pg.mouse.up(); await a.wait(900)
    cdp = await a.ctx.new_cdp_session(a.pg)
    async def touch(kind, pts):
        await cdp.send('Input.dispatchTouchEvent', {'type': kind, 'touchPoints': [{'x': x, 'y': y, 'id': i} for i, (x, y) in enumerate(pts)]})
    if a.touch:
        await touch('touchStart', [(cx, cy)])  # één vinger slepen
        for k in range(15): await touch('touchMove', [(cx + k * 8, cy + k * 3)]); await a.wait(30)
        await touch('touchEnd', [])
        await touch('touchStart', [(cx - 40, cy), (cx + 40, cy)])  # knijpen + schuiven tegelijk
        for k in range(15): await touch('touchMove', [(cx - 40 - k * 5, cy + k * 4), (cx + 40 + k * 5, cy + k * 4)]); await a.wait(30)
        await touch('touchEnd', [])
    await a.wait(800)
    L = await a.ev('()=>window.__L')
    ok(len(L) > 10, 'te weinig frames')
    V = [[L[i][k] - L[i - 1][k] for k in range(3)] for i in range(1, len(L))]
    st = [math.hypot(*v) for v in V]
    med = sorted(st)[len(st) // 2] + 1e-6
    jerk = max(abs(st[i] - st[i - 1]) for i in range(1, len(st)))
    rev = sum(1 for i in range(1, len(V)) if st[i] > 0.02 and st[i - 1] > 0.02 and sum(V[i][k] * V[i - 1][k] for k in range(3)) < -0.3 * st[i] * st[i - 1])
    ok(rev <= 4, f'{ac}: camera schokt heen en weer: {rev} omkeringen')
    ok(jerk < max(1.5, 12 * med), f'{ac}: camera springt: max sprong {jerk:.2f} (mediaan stap {med:.3f})')
    if a.touch: ok(max(x[3] for x in L) - min(x[3] for x in L) > 0.05, f'{ac}: knijpen verandert de zoom niet ({L[0][3]:.2f}→{L[-1][3]:.2f})')

async def d_tilt(a):
    if not a.touch: return
    await a.hit('#modal [data-ac=glider]')
    await a.hit('#btnPanel'); await a.hit('label[for=optTilt]')
    ok(await a.ev('()=>document.getElementById("optTilt").checked'), 'kantelsturing gaat niet aan: ' + await a.ev('()=>document.getElementById("tiltNote").textContent')); await a.hit('#btnPanel')
    st = await a.v('v.PLANE'); await a.place(st['x'], st['n'], 2000, 0, paused=False)
    await a.ev('()=>window.__vfr.setTempo(0)')
    ang = await a.v('v.tiltAng()')
    def ev(turn, pitch):
        ang = A[0]  # gewenste stuur/kantel in schermtermen → beta/gamma voor de huidige stand
        if ang == 90: return {'beta': turn, 'gamma': -pitch}
        if ang == 270: return {'beta': -turn, 'gamma': pitch}
        return {'gamma': turn, 'beta': 40 + pitch}
    A = [ang]
    send = '(o)=>window.dispatchEvent(Object.assign(new Event("deviceorientation"),{alpha:0,beta:o.beta,gamma:o.gamma}))'
    await a.ev(send, ev(0, 0))  # ijkpunt
    for g in (3, 6, 7.9): await a.ev(send, ev(g, 0)); ok(not await a.v('v.keys.tr'), f'draait al binnen dode zone ({g})')
    for g in (9, 15, 25): await a.ev(send, ev(g, 0))
    ok(await a.v('v.keys.tr') and not await a.v('v.keys.tl'), 'rechts kantelen draait niet rechts')
    for g in (20, -20, 25, -25, 0): await a.ev(send, ev(g, 0)); await a.frames(1)  # schokkerig
    ok(not await a.v('v.keys.tr||v.keys.tl'), 'blijft draaien na terug naar rechtuit')
    await a.ev(send, ev(0, 15)); ok(await a.v('v.keys.tu'), 'achterover kantelen ≠ stijgen')
    await a.ev(send, ev(0, -15)); ok(await a.v('v.keys.td'), 'voorover kantelen ≠ dalen')
    await a.ev(send, ev(0, 0))
    for _ in range(5):
        await a.ev(send, {'beta': float('nan'), 'gamma': 10}); await a.frames(1)
    # midden in de vlucht draaien naar liggend en terug (Christian 14 nov): assen wisselen + opnieuw ijken
    cdp = await a.ctx.new_cdp_session(a.pg); vw = a.pg.viewport_size
    for typ, angle in (('landscapePrimary', 90), ('landscapeSecondary', 270), ('portraitPrimary', 0)):
        w, h = (vw['height'], vw['width']) if angle else (vw['width'], vw['height'])
        await cdp.send('Emulation.setDeviceMetricsOverride', {'width': w, 'height': h, 'deviceScaleFactor': 1, 'mobile': True, 'screenOrientation': {'type': typ, 'angle': angle}})
        await a.frames(3); ang = A[0] = await a.v('v.tiltAng()'); ok(ang == angle, f'schermstand {angle} niet gezien ({ang})')
        await a.ev(send, ev(0, 0)); ok(not await a.v('v.keys.tr||v.keys.tl||v.keys.tu||v.keys.td'), f'stuurt al na draaien naar {angle}°')
        await a.ev(send, ev(20, 0)); ok(await a.v('v.keys.tr'), f'{angle}°: rechts kantelen draait niet rechts')
        await a.ev(send, ev(0, 15)); ok(await a.v('v.keys.tu') and not await a.v('v.keys.tr'), f'{angle}°: achterover ≠ stijgen')
        await a.ev(send, ev(0, 0)); await a.sane()
    await cdp.send('Emulation.clearDeviceMetricsOverride'); await a.frames(2)

# ---------------- stochastisch ----------------
async def fuzz(a, seed, steps):
    rnd = random.Random(seed)
    await a.hit('#modal [data-ac=%s]' % rnd.choice(['map', 'glider', 'motor', 'balloon']))
    sels = ['#btnMode', '#btnPanel', '#btnBig', '#timeBtn', '#btnPause', '#ctrl [data-k=arrowup]', '#ctrl [data-k=arrowleft]', '#ctrl [data-k=arrowright]', '#ctrl [data-k=arrowdown]', '#tSlow', '#tFast', '#btnAc', '#modal [data-ac=glider]', '#modal [data-ac=motor]', '#modal [data-ac=balloon]', '#modal [data-ac=map]', '#banner .nt', '#banner .rt', '#btnLoop']
    log = []
    for i in range(steps):
        k = rnd.random(); vw = a.pg.viewport_size
        if k < .45:
            s = rnd.choice(sels)
            if await a.visible(s):
                log.append('tap ' + s)
                try: await a.hit(s)
                except Exception as e: log.append('  (niet klikbaar)')
        elif k < .6:
            x, y = rnd.random() * vw['width'], rnd.random() * vw['height']; log.append(f'tap {x:.0f},{y:.0f}'); await a.tap_xy(x, y)
        elif k < .72:
            key = rnd.choice(['ArrowUp', 'ArrowDown', 'ArrowLeft', 'ArrowRight', ' ', 'l', 'c', '+', '-']); log.append('key ' + key)
            await a.pg.keyboard.down(key); await a.wait(rnd.randint(30, 400)); await a.pg.keyboard.up(key)
        elif k < .85:
            o = {'beta': rnd.uniform(-60, 90), 'gamma': rnd.uniform(-60, 60)}; log.append(f'tilt {o}')
            await a.ev('(o)=>window.dispatchEvent(Object.assign(new Event("deviceorientation"),{alpha:0,beta:o.beta,gamma:o.gamma}))', o)
        elif k < .9 and a.form != 'desk':
            log.append('draai'); await a.pg.set_viewport_size({'width': vw['height'], 'height': vw['width']})
        else:
            log.append('wacht'); await a.wait(rnd.randint(100, 900))
        await a.frames(1)
        try:
            await a.sane(); await a.no_errs('fuzz')
            m = await a.menus_open(); ok(len(m) <= 1, f'meerdere menu\'s open: {m}')
        except Fail as e:
            raise Fail(f'seed {seed} stap {i} na [{" | ".join(log[-4:])}]: {e}')

async def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--seed', type=int, default=None); ap.add_argument('--forms', default='desk,p7,p7l,se')
    ap.add_argument('--only', default=''); ap.add_argument('--steps', type=int, default=40)
    o = ap.parse_args(); forms = o.forms.split(',')
    seed = o.seed if o.seed is not None else random.randrange(10**6)
    url = serve()
    smoke = [('laden', t_load), ('kaart+sonde', t_map_probe), ('3 toestellen', t_aircraft), ('modusknop 1 regel', t_modebtn), ('één menu', t_one_menu), ('overlap', t_overlap), ('draaien', t_rotate)]
    det = [('opdracht "vlieg naar"', d_task_text), ('banner RMZ 1 regel', d_banner_rmz), ('geweigerde klaring op tijd', d_refused), ('klaring aangrenzend gebied', d_adjacent_clearance), ('waarschuwing 2–20 s vooraf', d_warn_lead), ('doel als lijn', d_goal_line), ('ballon voorbij doel', d_balloon_past), ('geslaagd met klaring', d_clearance_success), ('geen klasse G buiten NL', d_outside_nl), ('camera slepen/knijpen zonder schokken', d_touch_smooth), ('kantelen', d_tilt)]
    async with async_playwright() as p:
        b = await p.chromium.launch(args=ARGS)
        for form in forms:
            for layer, tests in (('smoke', smoke), ('det', det)):
                if o.only and o.only != layer: continue
                for name, fn in tests:
                    a = await new_app(p, b, form, url); await run(layer, name, form, fn, a); await a.ctx.close()
            if not o.only or o.only == 'fuzz':
                for k in range(2):
                    s = seed + k; a = await new_app(p, b, form, url)
                    await run('fuzz', f'monkey seed {s}', form, lambda a, s=s: fuzz(a, s, o.steps), a); await a.ctx.close()
        await b.close()
    nfail = 0
    for layer in RES:
        print(f'\n== {layer}: {sum(r[2]=="OK" for r in RES[layer])}/{len(RES[layer])} OK')
        for f, n, st, msg in RES[layer]:
            if st != 'OK': nfail += 1; print(f'  ✗ [{f}] {n}: {msg}')
    print(f'\nseed={seed}  screenshots in {SHOTS}')
    sys.exit(1 if nfail else 0)

if __name__ == '__main__':
    asyncio.run(main())
