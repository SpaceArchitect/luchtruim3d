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
THREE = os.environ.get('THREE_DIR') or os.path.join(ROOT, '.devenv', 'node_modules', 'three')  # tools/setup.py installeert dit
PORT = int(os.environ.get('E2E_PORT', '8766'))
ARGS = ['--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist']

def serve():
    d = tempfile.mkdtemp()
    if not os.path.isdir(THREE): sys.exit(f'three.js niet gevonden in {THREE} — draai eerst: python tools/setup.py')
    html = open(os.environ.get('E2E_INDEX', os.path.join(ROOT, 'index.html')), encoding='utf-8').read()
    html = html.replace('https://cdn.jsdelivr.net/npm/three@0.160.0/', '/three/')
    open(os.path.join(d, 'index.html'), 'w', encoding='utf-8').write(html)
    try: os.symlink(THREE, os.path.join(d, 'three'))
    except OSError: shutil.copytree(THREE, os.path.join(d, 'three'))  # Windows zonder symlinkrecht
    class Q(http.server.SimpleHTTPRequestHandler):
        def log_message(self, *a): pass
    h = functools.partial(Q, directory=d)
    srv = http.server.ThreadingHTTPServer(('127.0.0.1', PORT), h)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    t = os.environ.get('E2E_TIME', 'wkday')  # wkday = di 10:00 (deterministisch); 'now' = echte klok
    return f'http://127.0.0.1:{PORT}/index.html?e2e' + ('' if t == 'now' else f'&t={t}')

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
        await a.ev('()=>{const v=window.__vfr;for(const f of v.LAYERS)v.WARNED.add(f.ident)}')  # alleen de knop testen, geen luchtruimmelding
        await a.hit('#btnPause'); ok(not await a.v('v.PAUSED'), f'{ac}: start-knop hervat niet ({(await a.v("v.NOTICE") or "")[:60]!r})')
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

OVERLAP_JS = '''()=>{const sels=["header .title","#timeBtn","#btnMode","#btnBig","#btnPanel","#compass","#banner","#ctrl","#loc","#btnCam","#tChip"];const R=[];
  for(const q of sels){const e=document.querySelector(q);if(!e)continue;const c=getComputedStyle(e),b=e.getBoundingClientRect();if(c.display==="none"||c.visibility==="hidden"||b.width<2||b.height<2)continue;R.push([q,b.left,b.top,b.right,b.bottom])}
  const o=[];for(let i=0;i<R.length;i++)for(let j=i+1;j<R.length;j++){const a=R[i],b=R[j];if(a[1]<b[3]-1&&b[1]<a[3]-1&&a[2]<b[4]-1&&b[2]<a[4]-1)o.push(a[0]+"×"+b[0])}
  const out=R.filter(x=>x[1]<-1||x[2]<-1||x[3]>innerWidth+1||x[4]>innerHeight+1).map(x=>x[0]);
  const ui=R.reduce((s,x)=>s+(x[3]-x[1])*(x[4]-x[2]),0)/(innerWidth*innerHeight);return {o,out,ui:+ui.toFixed(2)}}'''

async def t_overlap(a):  # Christian 14 nov: liggend 'zie ik niks door alle knoppen en banners'
    await a.hit('#modal [data-ac=glider]'); await a.frames(3)
    e = await a.ev(JS_FREE_EDGE, ['EHEH', 1.8, 1000])
    cases = [('leeg', None), ('met waarschuwingsregel', 'ahead'), ('melding met radio-opties', 'rt')]
    for name, kind in cases:
        if kind is None:
            await a.ev('()=>{const v=window.__vfr;v.NOTICE="";v.PAUSED=true;v.hudTick()}')
        else:
            await a.place(e[0], e[1], 1000, e[2], paused=True)
            await a.ev('()=>{const v=window.__vfr;v.TASK="Vlieg naar de Dommel (8 km)";v.GOAL={x:v.PLANE.x+5,n:v.PLANE.n,name:"de Dommel"};v.hudTick()}')
            if kind == 'rt':
                await a.ev('()=>{const v=window.__vfr;v.PAUSED=false;v.WARNED.clear()}')
                for _ in range(60):
                    await a.frames(2)
                    if await a.v('v.NOTICE'): break
                if await a.visible('#banner [data-rt^=open]'): await a.hit('#banner [data-rt^=open]')
        await a.frames(2)
        r = await a.ev(OVERLAP_JS)
        await a.shot('overlap_' + name.replace(' ', '_'))
        ok(not r['o'], f'{name}: overlap {r["o"]}'); ok(not r['out'], f'{name}: buiten beeld {r["out"]}')
        lim = 0.38 if a.pg.viewport_size['width'] < 360 else 0.33  # klein staand scherm: stuurknoppen ≥ 44 px (WCAG) kosten ruimte; S5 haalt ze weg bij kantelen
        if kind != 'rt': ok(r['ui'] <= lim, f'{name}: knoppen/banners bedekken {r["ui"]*100:.0f}% van het scherm (max {lim*100:.0f}%)')

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
JS_FREE_EDGE = '''([ident,out,alt])=>{const v=window.__vfr,f=v.LAYERS.find(g=>g.ident===ident);for(let h=0;h<360;h+=5){const a=h*Math.PI/180;for(let d=0;d<40;d+=.05){const x=f.lp[0]+Math.sin(a)*d,n=f.lp[1]+Math.cos(a)*d;if(!v.featsAt(x,n).includes(f)){let ok=true;for(let k=.2;k<=out+.5;k+=.2){const fs=v.featsAt(x+Math.sin(a)*k,n+Math.cos(a)*k).filter(g=>g.lo<=alt&&g.hi>alt&&g.active!==false&&["CTR","TMA","CTA","P","R","RMZ","PJA","UAS","TRA","TSA"].includes(g.layer));if(fs.length){ok=false;break}}if(ok)return [x+Math.sin(a)*out,n+Math.cos(a)*out,(h+180)%360];break}}}return null}'''
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

async def d_balloon_reachable(a):  # Christian 14 nov: ballonmissie onmogelijk door windrichting
    r = await a.ev('''()=>{const v=window.__vfr,bad=[];let n=0;for(let k=0;k<300&&n<40;k++){const x=v.PLANE.x+(Math.random()-.5)*50,y=v.PLANE.n+(Math.random()-.5)*50,h=(v.windAt(800).from+180)%360;const t=v.pickTask(x,y,h,"balloon");if(!t)continue;n++;const g=window.__vfr.GOAL;}return n}''')
    ok(r > 5, f'te weinig ballonopdrachten gevonden ({r})')
    bad = await a.ev('''()=>{const v=window.__vfr,bad=[];for(let k=0;k<300;k++){const x=v.PLANE.x+(Math.random()-.5)*50,y=v.PLANE.n+(Math.random()-.5)*50,h=(v.windAt(800).from+180)%360;const t=v.pickTask(x,y,h,"balloon");if(!t)continue;const L=v.LASTGOAL;const b=(Math.atan2(L.x-x,L.n-y)*180/Math.PI+360)%360;if(!v.balloonReach(b))bad.push([t,b])}return bad.slice(0,3)}''')
    ok(not bad, f'onbereikbare ballondoelen: {bad}')

async def d_foreign_ctr(a):  # Christian 14 nov: Kleine-Brogel "klaring nodig" zonder frequentie of uitleg
    await a.hit('#modal [data-ac=glider]')
    e = await a.ev(JS_FREE_EDGE, ['EBBL2', 1.2, 1000]); ok(e, 'vrije rand Kleine-Brogel niet gevonden')
    await a.place(e[0], e[1], 1000, e[2], paused=False)
    n = ''
    for _ in range(150):
        await a.frames(2); n = await a.v('v.NOTICE') or ''
        if n: break
    ok('Kleine-Brogel' in n and '📻' in n, f'melding Kleine-Brogel zonder radio-info: {n[:100]!r}')

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
    e = await a.ev(JS_FREE_EDGE, [ctr, 1.6, 1000]); ok(e, 'vrije rand CTR niet gevonden')
    await a.place(e[0], e[1], 1000, e[2], paused=True)  # 1,6 km buiten de rand in vrij luchtruim, koers erheen
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
    r = await a.ev('''()=>{const v=window.__vfr,f=v.LAYERS.find(g=>g.ident==="EHDP");for(let h=0;h<360;h+=5){const a=h*Math.PI/180;for(let d=0;d<30;d+=.05){const x=f.lp[0]+Math.sin(a)*d,n=f.lp[1]+Math.cos(a)*d;if(!v.featsAt(x,n).includes(f)){const x2=x+Math.sin(a)*.6,n2=n+Math.cos(a)*.6;if(v.featsAt(x2,n2).some(g=>g.ident==="EHEH"))return [x2,n2,(h+180)%360];break}}}return null}''')
    ok(r, 'testopzet: geen grens De Peel–Eindhoven gevonden')
    await a.place(r[0], r[1], 1000, r[2], paused=False)
    await a.ev('()=>{const v=window.__vfr;v.CLR.add("EHEH");v.GOAL={x:v.PLANE.x+3,n:v.PLANE.n,name:"Test"}}')
    for _ in range(60):
        await a.frames(2)
        if await a.ev('()=>{const v=window.__vfr;return v.featsAt(v.PLANE.x,v.PLANE.n).some(f=>f.ident==="EHDP")}'): break
    await a.frames(4)
    f = await a.ev('()=>[...window.__vfr.FAILS.values()]')
    ok(not any('Peel' in x for x in f), f'De Peel telt als zonder klaring terwijl Eindhoven TWR klaring gaf: {f}')

async def d_warn_lead(a):  # Christian 14 nov: minstens ~2 s reactietijd, niet te vroeg (≤ 20 s), bij elk tempo
    await a.hit('#modal [data-ac=motor]')
    for ti, out in ((0, 1.0), (4, 12)):
        e = await a.ev(JS_FREE_EDGE, ['EHEH', out, 1000]); ok(e, 'vrije rand niet gevonden')
        await a.place(e[0], e[1], 1000, e[2], paused=False)
        await a.ev(f'()=>window.__vfr.setTempo({ti})')
        n = ''
        for _ in range(400):
            await a.frames(1); n = await a.v('v.NOTICE') or ''
            if n: break
        ok('klaring' in n, f'tempo {ti}: geen klaringsmelding: {n!r}')
        r = await a.ev('(id)=>{const v=window.__vfr;const h=v.PLANE.hdg*Math.PI/180;let d=0;while(d<40&&!v.featsAt(v.PLANE.x+Math.sin(h)*d,v.PLANE.n+Math.cos(h)*d).some(f=>f.ident===id))d+=.02;return [d,v.AC.motor.kt*1.852/3600*v.TEMPO]}', 'EHEH')
        secs = r[0] / r[1]
        ok(2 <= secs <= 20, f'tempo {ti}: melding {secs:.1f} s voor de grens (moet 2–20 s)')

async def weekend(a):
    if await a.visible('#timeBtn'):
        await a.hit('#timeBtn'); await a.hit('#timePop [data-tm=weekend]')
        if await a.visible('#timePop'): await a.hit('#timeBtn')

async def d_rmz_call(a):  # Christian 14 nov + AIP ENR 2.1/2.2: Volkel CTR dicht → RMZ H24 in het weekend, eerst Dutch MIL Info 132.350
    await a.hit('#modal [data-ac=glider]'); await weekend(a)
    st = await a.ev('()=>{const v=window.__vfr,f=v.LAYERS.find(g=>g.ident==="EHVK"),r=v.LAYERS.find(g=>g.ident==="EHVKRMZ");return [f.active,!!f.viaRmz,r.active,f.edges.length?f.edges[0].material.opacity:null,f.label?f.label.el.innerText:""]}')
    if st[0] is not False:
        ok(not await a.visible('#timeBtn'), f'weekendtijd gekozen maar Volkel niet dicht: {st}')
        return  # toren open op dit tijdstip: niets te testen (weekendknop niet bereikbaar)
    ok(st[1] and st[2], f'Volkel dicht maar RMZ niet actief/gekoppeld: {st}')
    ok(st[3] is None or st[3] > 0.2, f'Volkel CTR vervaagd terwijl de RMZ geldt: {st}')
    ok('132.350' in st[4] and 'RMZ' in st[4] and 'D ·' not in st[4], f'label Volkel (Pieter: weekend niet als actieve CTR D): {st[4]!r}')
    for call in (True, False):
        e = await a.ev(JS_EDGE, ['EHVKRMZ', 270, 1000])
        await a.place(e[0] - 1.2, e[1], 1000, 90, paused=False)
        await a.ev('()=>{const v=window.__vfr;v.GOAL={x:v.PLANE.x+6,n:v.PLANE.n,name:"Test"}}')
        n = ''
        for _ in range(120):
            await a.frames(2); n = await a.v('v.NOTICE') or ''
            if n: break
        ok('eerst oproepen' in n and '132.350' in n, f'geen oproep-melding voor RMZ Volkel: {n[:90]!r}')
        if call:
            await a.hit('#banner [data-rt^=open]')
            good = await a.ev('()=>[...document.querySelectorAll("#banner .rt")].findIndex(b=>b.querySelectorAll("span").length===6&&!/PH-/.test(b.querySelector("span").textContent))')
            await a.hit(f'#banner .rt >> nth={good}')
            ok('Opgeroepen' in (await a.v('v.NOTICE') or ''), 'oproep niet bevestigd')
            await a.hit('#banner [data-rt=close]') if await a.visible('#banner [data-rt=close]') else None
        await a.ev('()=>{window.__vfr.NOTICE="";window.__vfr.PAUSED=false}')
        for _ in range(120):
            await a.frames(2)
            if await a.ev('()=>{const v=window.__vfr;return v.featsAt(v.PLANE.x,v.PLANE.n).some(f=>f.ident==="EHVKRMZ")}'): break
        await a.ev('()=>window.__vfr.hudTick()')
        f = await a.ev('()=>[...window.__vfr.FAILS.values()]')
        bad = any('oproep' in x for x in f)
        ok(bad != call, f'RMZ {"met" if call else "zonder"} oproep: FAILS={f}')
        head = await a.ev('()=>document.querySelector("#banner .head")?.innerText||""')
        ok(('OPGEROEPEN' in head) == call, f'statusregel na {"wel" if call else "geen"} oproep: {head!r}')

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
    await a.ev('()=>{const v=window.__vfr;for(const f of v.LAYERS)v.WARNED.add(f.ident);v.GOAL={x:v.PLANE.x-0.1,n:v.PLANE.n-4.2,name:"Testdoel",min:1.7};v.TASK="Drijf naar Testdoel";v.hudTick()}')
    n = await a.v('v.NOTICE') or ''
    ok('Missie mislukt' in n and 'ballon' in n, f'ballon voorbij doel geen "mislukt": {n[:80]!r}')
    ok(await a.v('v.GOAL') is None, 'doel blijft staan na mislukt')
    await a.fly('glider')
    st = await a.v('v.PLANE')
    await a.place(st['x'], st['n'], 1500, st['hdg'], paused=False)
    await a.ev('()=>{const v=window.__vfr;for(const f of v.LAYERS)v.WARNED.add(f.ident);v.GOAL={x:v.PLANE.x,n:v.PLANE.n-4.2,name:"Testdoel",min:1.7};v.hudTick()}')  # andere meldingen uit: alleen 'doel gemist' testen
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

SEND = '(o)=>window.dispatchEvent(Object.assign(new Event("deviceorientation"),{alpha:0,beta:o.beta,gamma:o.gamma}))'

async def tilt_on(a):
    """Kantelen aan (staat op telefoon standaard aan sinds S1c) en meteen sensordata sturen zodat de terugval naar knoppen niet afgaat."""
    if not await a.ev('()=>document.getElementById("optTilt").checked'):
        await a.hit('#btnPanel'); await a.hit('label[for=optTilt]'); await a.hit('#btnPanel')
    ang = await a.v('v.tiltAng()')
    await a.ev(SEND, orient(0, 0, ang)); await a.frames(1)
    ok(await a.ev('()=>document.getElementById("optTilt").checked'), 'kantelsturing gaat niet aan: ' + await a.ev('()=>document.getElementById("tiltNote").textContent'))

def orient(turn, back, ang, p0=60):
    """beta/gamma zoals een echte telefoon ze geeft voor een stand: rol 'turn' (rechts +), 'back' graden naar je toe gekanteld t.o.v. p0."""
    t, p = math.radians(turn), math.radians(p0 + back)  # 'back' = naar je toe kantelen (Christian 14 nov: = stijgen)
    sx, sy, sz = -math.sin(t), math.cos(t) * math.sin(p), math.cos(t) * math.cos(p)
    if ang == 90: ux, uy = sy, -sx
    elif ang == 270: ux, uy = -sy, sx
    else: ux, uy = sx, sy
    uz = sz if abs(sz) > 1e-6 else 1e-6
    g = math.atan(-ux / uz); b = math.atan2(uy, uz / math.cos(g))
    return {'beta': math.degrees(b), 'gamma': math.degrees(g)}

async def d_tilt(a):  # Christian 14 nov: kantelen deed niks; liggend achterover = ineens een bocht
    if not a.touch: return
    await a.hit('#modal [data-ac=glider]')
    await tilt_on(a)
    st = await a.v('v.PLANE'); await a.place(st['x'], st['n'], 2000, 0, paused=False)
    send = '(o)=>window.dispatchEvent(Object.assign(new Event("deviceorientation"),{alpha:0,beta:o.beta,gamma:o.gamma}))'
    keys = '[v.keys.tl,v.keys.tr,v.keys.tu,v.keys.td]'
    cdp = await a.ctx.new_cdp_session(a.pg); vw = a.pg.viewport_size
    W, H = min(vw['width'], vw['height']), max(vw['width'], vw['height'])
    for typ, angle in (('portraitPrimary', 0), ('landscapePrimary', 90), ('landscapeSecondary', 270), ('portraitPrimary', 0)):
        w, h = (H, W) if angle else (W, H)
        await cdp.send('Emulation.setDeviceMetricsOverride', {'width': w, 'height': h, 'deviceScaleFactor': 1, 'mobile': True, 'screenOrientation': {'type': typ, 'angle': angle}})
        await a.frames(3); ok(await a.v('v.tiltAng()') == angle, f'schermstand {angle} niet gezien')
        for p0 in (45, 80, 100):  # schuin, bijna rechtop, voorbij rechtop (daar sprongen de Euler-hoeken)
            await a.ev('()=>window.__vfr.resetTilt()')  # opnieuw ijken, zoals bij aanzetten
            await a.ev(send, orient(0, 0, angle, p0)); await a.ev(send, orient(0, 0, angle, p0))
            k = await a.v(keys); ok(k == [False] * 4, f'{angle}°/{p0}°: stuurt al zonder kantelen {k}')
            for d in (3, 6, 7.5):
                await a.ev(send, orient(d, 0, angle, p0)); ok(await a.v(keys) == [False] * 4, f'{angle}°/{p0}°: reageert binnen dode zone ({d}°)')
            await a.ev(send, orient(15, 0, angle, p0)); k = await a.v(keys)
            ok(k == [False, True, False, False], f'{angle}°/{p0}°: rechts kantelen → {k}')
            await a.ev(send, orient(-15, 0, angle, p0)); k = await a.v(keys)
            ok(k == [True, False, False, False], f'{angle}°/{p0}°: links kantelen → {k}')
            for back in (5, 11, 13, 20, 30):  # achterover = stijgen, nooit een bocht
                await a.ev(send, orient(0, back, angle, p0)); k = await a.v(keys)
                ok(not k[0] and not k[1], f'{angle}°/{p0}°: {back}° naar je toe geeft een bocht {k}')
                if back > 9: ok(k[2] and not k[3], f'{angle}°/{p0}°: {back}° naar je toe ≠ stijgen {k}')
            await a.ev(send, orient(0, -15, angle, p0)); k = await a.v(keys)
            ok(k == [False, False, False, True], f'{angle}°/{p0}°: naar voren ≠ dalen {k}')
            await a.ev(send, orient(12, 15, angle, p0)); k = await a.v(keys)
            ok(k == [False, True, True, False], f'{angle}°/{p0}°: rechts + achterover {k}')
            for x in (20, -20, 25, -25, 0): await a.ev(send, orient(x, 0, angle, p0)); await a.frames(1)  # schokkerig
            ok(await a.v(keys) == [False] * 4, f'{angle}°/{p0}°: blijft sturen na terug naar neutraal')
        # panel 3 (ernst 8): telefoon iets scheef bij ▶ → dat is rechtuit, geen blijvende bocht
        await a.ev('()=>window.__vfr.resetTilt()'); await a.ev(send, orient(12, 0, angle)); await a.ev(send, orient(12, 0, angle))
        ok(await a.v(keys) == [False] * 4, f'{angle}°: scheef geijkt (12°) geeft toch een bocht')
        await a.ev(send, orient(28, 0, angle)); ok((await a.v(keys))[1], f'{angle}°: na scheef ijken geen bocht rechts bij +16°')
        await a.ev(send, orient(-4, 0, angle)); ok((await a.v(keys))[0], f'{angle}°: na scheef ijken geen bocht links bij -16°')
        await a.ev(send, orient(0, 0, angle))
        await a.sane()
    await a.ev(send, {'beta': float('nan'), 'gamma': 10}); await a.sane()
    await cdp.send('Emulation.clearDeviceMetricsOverride'); await a.frames(2)

async def d_cam_no_jump(a):  # Christian 14 nov: 'hele beeld schokt en springt heen en weer' bij draaien (desktop) + panel Sanne/Daan: sprong bij begin slepen
    for ac in ('glider', 'balloon', 'motor'):
        await a.fly(ac)
        st = await a.v('v.PLANE'); await a.place(st['x'], st['n'], 2000, st['hdg'], paused=False)
        await a.ev('()=>{const v=window.__vfr;v.setTempo(5);for(const f of v.LAYERS)v.WARNED.add(f.ident);window.__R=[];const f=()=>{const c=v.camera.position,p=v.PLANE;window.__R.push([c.x-p.x,c.y,-c.z-p.n]);if(window.__R.length<500)requestAnimationFrame(f)};requestAnimationFrame(f)}')
        await a.wait(800)
        vw = a.pg.viewport_size; cx, cy = vw['width'] * .45, vw['height'] * .55
        if a.touch:
            cdp = await a.ctx.new_cdp_session(a.pg)
            await cdp.send('Input.dispatchTouchEvent', {'type': 'touchStart', 'touchPoints': [{'x': cx, 'y': cy, 'id': 0}]})
            for k in range(20): await cdp.send('Input.dispatchTouchEvent', {'type': 'touchMove', 'touchPoints': [{'x': cx + k * 6, 'y': cy, 'id': 0}]}); await a.wait(25)
            await cdp.send('Input.dispatchTouchEvent', {'type': 'touchEnd', 'touchPoints': []})
        else:
            await a.pg.mouse.move(cx, cy); await a.pg.mouse.down()
            for k in range(20): await a.pg.mouse.move(cx + k * 6, cy); await a.wait(25)
            await a.pg.mouse.up()
        yaw_rel = await a.v('v.dbg.camYaw'); await a.wait(900)
        yaw_later = await a.v('v.dbg.camYaw')
        ok(abs(yaw_later) > 0.6 * abs(yaw_rel) and abs(yaw_rel) > 0.05, f'{ac}: camera veert direct terug na loslaten ({yaw_rel:.2f}→{yaw_later:.2f})')
        await a.wait(600)
        R = await a.ev('()=>window.__R')
        st_ = [math.dist(R[i], R[i - 1]) for i in range(1, len(R))]
        med = sorted(st_)[len(st_) // 2] + 1e-6
        ok(max(st_) < max(0.6, 8 * med), f'{ac}: camera springt t.o.v. het toestel (max {max(st_):.2f}, mediaan {med:.3f})')
        await a.ev('()=>{const v=window.__vfr;v.PAUSED=true;v.setTempo(2)}')

async def d_panel_fixes(a):  # panelronde 14 nov (Fatima, Noor, Daan): elk punt als test
    await a.hit('#modal [data-ac=motor]')
    # opdracht aanwezig bij start (Fatima 3)
    n = 0
    for _ in range(4):
        await a.fly('glider'); n += 1 if await a.v('!!v.TASK') else 0
    ok(n >= 3, f'start zonder opdracht ({4-n}/4 keer)')
    # radiomelding: Sluiten zichtbaar in beeld (Fatima 2, Noor 3, Daan 9)
    e = await a.ev(JS_FREE_EDGE, ['EHEH', 1.5, 1000])
    await a.place(e[0], e[1], 1000, e[2], paused=False)
    for _ in range(150):  # op wandkloktijd wachten: onder belasting (volledige suite) zijn frames traag
        await a.wait(100)
        if await a.v('v.NOTICE'): break
    await a.hit('#banner [data-rt^=open]')
    b = await a.pg.locator('#banner [data-rt=close]').bounding_box(); vw = a.pg.viewport_size
    ok(b and b['y'] >= 0 and b['y'] + b['height'] <= vw['height'] + 1, f'Sluiten niet in beeld: {b}')
    await a.hit('#banner [data-rt=close]')
    # looping wist geen open melding (Daan 2)
    await a.ev('()=>{const v=window.__vfr;v.PLANE.alt=2000;v.NOTICE="🔶 test melding";v.PAUSED=true;v.hudTick()}')
    await a.pg.keyboard.press('l'); await a.frames(2)
    ok('test melding' in (await a.v('v.NOTICE') or '') and not await a.v('!!v.dbg.LOOP'), 'looping wist een open melding')
    # looping-hoogtecheck (stond in commentaar)
    await a.ev('()=>{const v=window.__vfr;v.NOTICE="";v.PAUSED=false;v.PLANE.alt=400}')
    await a.pg.keyboard.press('l'); await a.frames(2)
    ok('Te laag' in (await a.v('v.NOTICE') or ''), 'looping onder 700 ft niet tegengehouden')
    # menu open = banner weg op telefoon (Fatima 1)
    if a.touch:
        await a.ev('()=>{const v=window.__vfr;v.NOTICE="🔶 test";v.hudTick()}')
        await a.hit('#btnPanel'); await a.frames(4); await a.ev('()=>window.__vfr.hudTick()')
        ok(not await a.visible('#banner') or await a.ev('()=>getComputedStyle(document.getElementById("banner")).visibility==="hidden"'), 'menu en melding tegelijk zichtbaar')
        await a.hit('#btnPanel')
    # blur laat geen pointers hangen (Daan 7)
    await a.ev('()=>{window.dispatchEvent(new Event("blur"))}')
    ok(await a.v('v.dbg.ptr===0&&!v.dbg.dragging'), 'pointers blijven hangen na blur')

async def d_probe_task(a):  # panel ronde 2 (Fatima): vanaf de sonde vliegen = ook een opdracht
    await a.hit('#modal [data-ac=map]'); vw = a.pg.viewport_size
    got = 0
    for k, (fx, fy) in enumerate(((.5, .55), (.4, .6), (.6, .5))):
        await a.tap_xy(vw['width'] * fx, vw['height'] * fy); await a.frames(2)
        await a.fly('glider'); got += 1 if await a.v('!!v.TASK') else 0
        ok('🎯' in (await a.v('v.NOTICE') or '') or not await a.v('!!v.TASK'), 'opdracht niet in de startmelding')
        await a.hit('#btnMode')
    ok(got >= 2, f'vanaf de sonde vaak geen opdracht ({got}/3)')

async def d_tilt_rotate(a):  # Christian 14 nov avond: na staand→liggend→staand bleef het toestel een bocht maken (geijkt midden in de draai)
    if not a.touch: return
    await a.hit('#modal [data-ac=glider]'); await tilt_on(a)
    st = await a.v('v.PLANE'); await a.place(st['x'], st['n'], 2000, 0, paused=False)
    await a.ev('()=>{const v=window.__vfr;for(const f of v.LAYERS)v.WARNED.add(f.ident)}')
    keys = '[v.keys.tl,v.keys.tr,v.keys.tu,v.keys.td]'
    cdp = await a.ctx.new_cdp_session(a.pg); vw = a.pg.viewport_size
    W, H = min(vw['width'], vw['height']), max(vw['width'], vw['height'])
    async def stream(turn, back, ang, ms, p0=60):
        t_end = ms / 1000
        import time as _t
        t0 = _t.time()
        while _t.time() - t0 < t_end:
            await a.ev(SEND, orient(turn, back, ang, p0)); await a.wait(40)
    prev = 0
    await stream(0, 0, 0, 300)
    for typ, angle in (('landscapePrimary', 90), ('portraitPrimary', 0), ('landscapeSecondary', 270), ('portraitPrimary', 0)):
        w, h = (H, W) if angle else (W, H)
        # tijdens het draaien: rare tussenstanden (nog in de oude stand gemeten, scheef)
        await stream(22, 12, prev, 150)
        await cdp.send('Emulation.setDeviceMetricsOverride', {'width': w, 'height': h, 'deviceScaleFactor': 1, 'mobile': True, 'screenOrientation': {'type': typ, 'angle': angle}})
        await stream(-20, -15, angle, 120)  # nog bewegend
        await stream(0, 0, angle, 700)      # telefoon ligt weer stil in de nieuwe stand
        k = await a.v(keys); ok(k == [False] * 4, f'na draaien naar {angle}°: blijft sturen {k}')
        await stream(15, 0, angle, 120); ok((await a.v(keys))[1], f'na draaien naar {angle}°: rechts kantelen werkt niet')
        await stream(0, 0, angle, 120); ok(await a.v(keys) == [False] * 4, f'na draaien naar {angle}°: niet terug naar rechtuit')
        prev = angle
    await cdp.send('Emulation.clearDeviceMetricsOverride'); await a.sane()

async def d_tilt_default(a):  # S1c (Christian): op telefoon standaard kantelen + knoppen weg; geen sensor = knoppen terug; uitzetten onthouden
    await a.hit('#modal [data-ac=glider]'); await a.frames(2)
    on = await a.ev('()=>document.getElementById("optTilt").checked')
    if not a.touch:
        ok(not on, 'desktop: kantelen staat aan'); ok(await a.visible('#ctrl [data-k=arrowup]'), 'desktop: stuurknoppen weg'); return
    ok(on, 'telefoon: kantelen niet standaard aan')
    ok(await a.visible('#ctrl [data-k=arrowup]'), 'stuurknoppen al weg vóór er sensordata is')
    await a.ev(SEND, orient(0, 0, await a.v('v.tiltAng()'))); await a.frames(2)
    ok(not await a.visible('#ctrl [data-k=arrowup]') and not await a.visible('#btnLoop'), 'stuurknoppen niet verborgen in kantelmodus')
    for sel in ('#btnPause', '#tSlow', '#tFast'): ok(await a.visible(sel), f'{sel} weg in kantelmodus')
    r = await a.ev(OVERLAP_JS); ok(not r['o'], f'overlap in kantelmodus {r["o"]}')
    await a.shot('kantelmodus')
    # uitzetten in Weergave → knoppen terug, en onthouden na herladen
    await a.hit('#btnPanel'); await a.hit('label[for=optTilt]'); await a.hit('#btnPanel')
    ok(await a.visible('#ctrl [data-k=arrowup]'), 'knoppen niet terug na uitzetten')
    await a.pg.reload(); await a.wait(1800); await a.hit('#modal [data-ac=glider]'); await a.frames(2)
    ok(not await a.ev('()=>document.getElementById("optTilt").checked'), 'uitzetten niet onthouden')

async def d_tilt_fallback(a):  # geen sensor (desktop-browser op touchscherm, oude telefoon) → na 2,5 s knoppen
    if not a.touch: return
    await a.hit('#modal [data-ac=motor]'); await a.wait(3200); await a.frames(2)
    ok(not await a.ev('()=>document.getElementById("optTilt").checked'), 'kantelen blijft aan zonder sensordata')
    ok(await a.visible('#ctrl [data-k=arrowup]'), 'geen knoppen zonder sensordata')
    ok('knoppen' in await a.ev('()=>document.getElementById("tiltNote").textContent'), 'geen uitleg bij terugval naar knoppen')

async def d_tilt_loop_balloon(a):  # Christian: looping door te kantelen; ballon zelfde logica
    if not a.touch: return
    await a.hit('#modal [data-ac=glider]'); await tilt_on(a)
    st = await a.ev('()=>{const v=window.__vfr;for(let k=0;k<3000;k++){const x=v.PLANE.x+(Math.random()-.5)*60,n=v.PLANE.n+(Math.random()-.5)*60;if(v.inNL(x,n)&&!v.featsAt(x,n).some(f=>f.lo<4000)&&!v.featsAt(x+Math.sin(0)*6,n+6).some(f=>f.lo<4000))return {x,n}}return null}')
    ok(st, 'geen vrije plek gevonden')
    await a.place(st['x'], st['n'], 2000, 0, paused=False)
    await a.ev('()=>{const v=window.__vfr;for(const f of v.LAYERS)v.WARNED.add(f.ident);v.resetTilt()}')
    ang = await a.v('v.tiltAng()')
    await a.ev(SEND, orient(0, 0, ang)); await a.ev(SEND, orient(0, 25, ang))
    ok(not await a.v('!!v.LOOP'), 'looping al bij 25° (moet ver kantelen)')
    await a.ev(SEND, orient(0, 45, ang)); await a.frames(2)
    ok(await a.v('!!v.LOOP'), 'geen looping bij ver naar je toe kantelen ' + json.dumps(await a.v('[v.PAUSED,v.NOTICE,v.PLANE.alt,v.TILT,v.MODE,v.ACTYPE]')))
    for _ in range(300):  # wandklok (max 30 s): onder belasting zijn frames traag
        await a.wait(100)
        if not await a.v('!!v.LOOP'): break
    ok(not await a.v('!!v.LOOP'), 'looping eindigt niet')
    await a.ev(SEND, orient(0, 45, ang)); await a.frames(2)
    ok(not await a.v('!!v.LOOP'), 'tweede looping zonder eerst terug naar neutraal')
    # ballon: naar je toe = stijgen, naar voren = dalen, nooit een looping
    await a.fly('balloon')
    st = await a.ev('()=>{const v=window.__vfr;for(let k=0;k<3000;k++){const x=v.PLANE.x+(Math.random()-.5)*60,n=v.PLANE.n+(Math.random()-.5)*60;if(v.inNL(x,n)&&!v.featsAt(x,n).some(f=>f.lo<4000))return {x,n}}return null}')
    ok(st, 'geen vrije plek voor de ballon gevonden')
    await a.place(st['x'], st['n'], 1000, 0, paused=False)
    await a.ev('()=>{const v=window.__vfr;for(const f of v.LAYERS)v.WARNED.add(f.ident);v.resetTilt()}')
    await a.ev(SEND, orient(0, 0, ang)); await a.ev(SEND, orient(0, 20, ang))
    alt0 = await a.v('v.PLANE.alt')
    for _ in range(100):
        await a.frames(2)
        if await a.v('v.PLANE.alt') > alt0 + 5: break
    ok(await a.v('v.PLANE.alt') > alt0, 'ballon stijgt niet bij naar je toe kantelen ' + json.dumps(await a.v('[v.PAUSED,v.NOTICE,v.PLANE.alt,v.keys.tu,v.TILT]')))
    await a.ev(SEND, orient(0, 50, ang)); await a.frames(2); ok(not await a.v('!!v.LOOP'), 'ballon maakt een looping')
    await a.ev(SEND, orient(0, -20, ang)); alt1 = await a.v('v.PLANE.alt')
    for _ in range(100):
        await a.frames(2)
        if await a.v('v.PLANE.alt') < alt1 - 5: break
    ok(await a.v('v.PLANE.alt') < alt1, 'ballon daalt niet bij naar voren kantelen')

async def d_rmz_inside_call(a):  # Christian 14 nov: in RMZ Gilze-Rijen stond 'oproepen' maar je kon niet oproepen
    await a.hit('#modal [data-ac=glider]'); await weekend(a)
    act = await a.ev('()=>window.__vfr.LAYERS.find(f=>f.ident==="EHGRRMZ").active')
    if act is False:
        ok(not await a.visible('#timeBtn'), 'weekendtijd gekozen maar RMZ Gilze-Rijen niet actief'); return
    lp = await a.ev('()=>window.__vfr.LAYERS.find(f=>f.ident==="EHGRRMZ").lp')
    await a.place(lp[0], lp[1], 1000, 0, paused=False); await a.frames(3)
    ok(await a.visible('#banner [data-rt="open:EHGRRMZ"]'), 'geen knop Oproepen in de RMZ: ' + await a.ev('()=>document.getElementById("banner").innerText'))
    await a.hit('#banner [data-rt="open:EHGRRMZ"]')
    good = await a.ev('()=>[...document.querySelectorAll("#banner .rt")].findIndex(b=>b.querySelectorAll("span").length===6&&!/PH-/.test(b.querySelector("span").textContent))')
    await a.hit(f'#banner .rt >> nth={good}')
    ok('Opgeroepen' in (await a.v('v.NOTICE') or '') and '132.350' in (await a.v('v.NOTICE') or ''), 'oproep Dutch MIL Info 132.350 niet bevestigd')
    await a.ev('()=>{const v=window.__vfr;v.NOTICE="";v.PAUSED=false;v.hudTick()}'); await a.frames(2)
    ok('OPGEROEPEN' in await a.ev('()=>document.querySelector("#banner .head").innerText'), 'statusregel toont geen OPGEROEPEN')

async def d_zoom_desktop(a):  # Christian 14 nov: geen manier om in/uit te zoomen op desktop (Shift+scrollen = horizontaal in Chrome)
    if a.touch: return
    await a.hit('#modal [data-ac=glider]'); await a.frames(2)
    await a.pg.mouse.move(640, 420)
    for dx, dy in ((0, 300), (300, 0)):
        d0 = await a.v('v.dbg.CAM.dist')
        await a.pg.keyboard.down('Shift'); await a.pg.mouse.wheel(dx, dy); await a.wait(200); await a.pg.keyboard.up('Shift')
        ok(abs(await a.v('v.dbg.CAM.dist') - d0) > 0.05, f'Shift+scrollen ({dx},{dy}) zoomt niet')

async def d_defaults_labels(a):  # Christian 15 nov: alle groepen standaard aan; labels óf zichtbaar óf weg, gevaren reiken verder
    await a.hit('#modal [data-ac=map]'); await a.frames(4)
    off = await a.ev('()=>Object.entries(window.__vfr.vis).filter(([k,v])=>!v).map(([k])=>k)')
    ok(not off, f'groepen standaard uit: {off}')
    r = await a.ev('''()=>{const v=window.__vfr,cam=v.camera.position;const out=[];
      for(const L of v.labels){if(!L.isAir||L.el.style.display==='none')continue;const cs=getComputedStyle(L.el);
        out.push([L.ref.layer,+cs.opacity,L.pos3().distanceTo(cam)]);}return out}''')
    ok(r, 'geen luchtruimlabels zichtbaar in kaartmodus')
    ok(all(o >= 0.99 for _, o, _ in r), f'vervaagd label: {[x for x in r if x[1] < .99][:3]}')
    haz = {'CTR','TMA','CTA','ATZ','P','R','D','TRA','TSA','PJA','UAS','LFA'}
    ok(any(l == 'CTR' for l, _, _ in r), 'geen CTR-label zichtbaar')
    far_haz = max([d for l, _, d in r if l in haz] or [0]); far_oth = max([d for l, _, d in r if l not in haz] or [0])
    ok(far_oth <= far_haz + 1e-6 or far_haz == 0, f'overig label verder zichtbaar ({far_oth:.0f}) dan gevaar ({far_haz:.0f})')
    await a.shot('defaults_labels')

async def d_goal_marker(a):  # Boyd 14 nov: kon de A67 niet vinden → doel als baken in de wereld, op het scherm als je erheen kijkt
    await a.hit('#modal [data-ac=glider]'); await a.frames(4)
    if not await a.v('v.GOAL'):
        await a.ev('()=>window.__vfr.newTask()'); await a.frames(3)
    g = await a.v('v.GOAL'); ok(g, 'geen opdracht met doel')
    ok(await a.v('v.goalViz.visible'), 'doelbaken niet zichtbaar tijdens een opdracht')
    pos = await a.v('v.GVPOS'); ok(pos, 'geen baakpositie')
    if not g.get('pts'):
        ok(abs(pos[0]-g['x']) < .01 and abs(pos[1]-g['n']) < .01, f'baken niet op het doel: {pos} vs {g["x"]},{g["n"]}')
    st = await a.v('v.PLANE')
    hdg = (math.degrees(math.atan2(pos[0]-st['x'], pos[1]-st['n'])) + 360) % 360
    await a.place(st['x'], st['n'], st['alt'] or 1500, hdg, paused=True)
    await a.ev('(g)=>{window.__vfr.GOAL=g}', g); await a.wait(400); await a.frames(4)
    on = await a.ev('''()=>{const v=window.__vfr,p=v.goalViz.children.find(c=>c.geometry.type==='OctahedronGeometry').position.clone().project(v.camera);return [p.x,p.y,p.z]}''')
    ok(abs(on[0]) < 1 and abs(on[1]) < 1 and on[2] < 1, f'baken niet in beeld bij koers naar het doel: {on}')
    await a.shot('goal_marker')
    await a.ev('()=>window.__vfr.setMode("map")'); await a.frames(2)
    ok(not await a.v('v.goalViz.visible'), 'doelbaken zichtbaar in kaartmodus')

async def d_tap_notice(a):  # Fleur 14 nov: tik op een melding = verder (nu "lege melding onderin")
    await a.hit('#modal [data-ac=glider]'); await a.frames(3)
    st = await a.v('v.PLANE')
    for html, want in (('🔶 Over 1,0 km: <b>CTR X</b> · klaring nodig<br><small>▶ = verder</small>', True),
                       ('✅ <b>Missie geslaagd!</b><br><small>▶ = verder vliegen</small> <button class="nt">🎯 Nieuwe opdracht</button>', True),
                       ('📻 <b>RMZ X</b> · eerst oproepen<br><small>▶ = verder</small> <button data-rt="open:X">📻 Oproepen</button>', False)):
        await a.place(st['x'], st['n'], 1500, st['hdg'], paused=True)
        await a.ev('(h)=>{const v=window.__vfr;v.NOTICE=h;v.PAUSED=true;v.hudTick()}', html); await a.frames(3)
        b = await a.pg.locator('#banner .notice').first.bounding_box(); ok(b, 'melding niet zichtbaar')
        x, y = b['x'] + 12, b['y'] + 10  # op de tekst, niet op een knop
        if a.touch: await a.pg.touchscreen.tap(x, y)
        else: await a.pg.mouse.click(x, y, delay=90)
        await a.wait(400); await a.frames(3)
        p, n = await a.v('v.PAUSED'), await a.v('v.NOTICE')
        if want: ok(not p and not n, f'tik op melding gaf geen ▶ (gepauzeerd={p}): {html[:30]}')
        else: ok(p and n, f'melding met radioknoppen verdween bij tik op de tekst: {html[:30]}')
        ok(not await a.visible('#info'), 'tik op melding opende het info-paneel (lege melding onderin)')

async def d_ac_switch(a):  # Fleur 14 nov: 'not sure hoe je van vliegtuig wisselt' → tik op het toesteltje onderin
    await a.hit('#modal [data-ac=glider]'); await a.frames(3)
    await a.hit('#loc .acsw'); await a.frames(2)
    ok(await a.visible('#modal'), 'toestelkeuze opent niet na tik op het toesteltje')
    await a.hit('#modal [data-ac=balloon]'); await a.frames(3)
    ok(await a.v('v.ACTYPE') == 'balloon', f'toestel niet gewisseld: {await a.v("v.ACTYPE")}')
    m = await a.menus_open(); ok(len(m) <= 1, f'meerdere menu\'s open: {m}')

async def d_land_city(a):  # Christian 15 nov: 'Buitenlanding … (in een weiland)' boven 's-Hertogenbosch
    await a.hit('#modal [data-ac=glider]'); await a.frames(3)
    r = await a.ev('''()=>{const v=window.__vfr,out=[];for(const [lo,la] of [[5.3037,51.6978],[5.4697,51.4416],[5.25,51.47],[5.70,51.36]]){const [x,n]=v.proj(lo,la);
      Object.assign(v.PLANE,{x,n,alt:0});out.push([v.builtUp(x,n),String(v.landText())]);}return out}''')
    ok(r[0][0] and r[1][0], f"centrum Den Bosch/Eindhoven niet als bebouwd herkend: {[x[0] for x in r]}")
    for bu, t in r:
        if bu: ok('weiland' not in t and 'bebouwde kom' in t, f'tekst boven de stad: {t[:90]}')
    ok(any(not bu for bu, _ in r), 'geen buitengebied gevonden voor de controle')

async def d_tilt_analog(a):  # Christian 21 nov: geleidelijke bocht/klim i.p.v. aan/uit, met dode zone; realistische ruis
    if not a.touch: return
    await a.hit('#modal [data-ac=glider]')
    await tilt_on(a)
    st = await a.v('v.PLANE'); await a.place(st['x'], st['n'], 2000, 0, paused=False)
    send = '(o)=>window.dispatchEvent(Object.assign(new Event("deviceorientation"),{alpha:0,beta:o.beta,gamma:o.gamma}))'
    ang = await a.v('v.tiltAng()'); p0 = 45
    await a.ev('()=>window.__vfr.resetTilt()'); await a.ev(send, orient(0, 0, ang, p0)); await a.ev(send, orient(0, 0, ang, p0))
    rng = random.Random(7)
    for _ in range(30):  # trillende hand ±5° rond neutraal: niets
        await a.ev(send, orient(rng.uniform(-5, 5), rng.uniform(-5, 5), ang, p0))
        t = await a.v('[v.TAX.r,v.TAX.p]'); ok(t == [0, 0], f'ruis ±5° stuurt: {t}')
    prev = 0
    for d in (12, 20, 28, 35, 50):
        await a.ev(send, orient(d, 0, ang, p0)); r = await a.v('v.TAX.r')
        ok(r > prev, f'bocht niet geleidelijk: {d}° → {r:.2f} (vorige {prev:.2f})' if d < 35 else f'{d}°: {r}'); prev = r if d < 35 else prev
        if d >= 35: ok(abs(r - 1) < 1e-6, f'{d}° geeft geen volle bocht: {r}')
    await a.ev(send, orient(-20, 0, ang, p0)); ok(await a.v('v.TAX.r') < 0, 'links kantelen geeft geen negatieve rol')
    prev = 0
    for d in (12, 20, 30):
        await a.ev(send, orient(0, d, ang, p0)); q = await a.v('v.TAX.p'); ok(q > prev, f'klimmen niet geleidelijk: {d}° → {q:.2f}'); prev = q
    # hoe ver kantelen = hoe snel draaien (echte sim)
    rates = []
    for d in (14, 34):
        await a.place(st['x'], st['n'], 2000, 0, paused=False); await a.ev(send, orient(d, 0, ang, p0))
        h0 = await a.v('v.PLANE.hdg'); await a.wait(1200); h1 = await a.v('v.PLANE.hdg')
        rates.append(((h1 - h0 + 540) % 360) - 180)
    ok(0 < rates[0] < rates[1] * 0.7, f'draaisnelheid niet evenredig: 14°→{rates[0]:.1f}°, 34°→{rates[1]:.1f}°')

async def d_missions(a):  # Christian 21 nov: interessantere missies; elk rond een echt conflict, oplosbaar, met les achteraf
    await a.hit('#modal [data-ac=glider]'); await a.frames(3)
    ms = await a.ev('()=>window.__vfr.MISSIONS.map(m=>({id:m.id,ac:m.ac,legs:m.legs.length,st:window.__vfr.misStart(m)}))')
    ok(len(ms) >= 6, f'te weinig missies: {len(ms)}')
    for m in ms: ok(m['st'], f'missie {m["id"]}: geen geldige start gevonden')
    ok((await a.v('v.MISSION||{}')).get('id') == 'vught', 'eerste zweefmissie start niet bij het welkom')
    # elke missie doorspelen: naar elk keerpunt teleporteren, zonder overtredingen → geslaagd met les + ster
    for m in ms:
        if m['ac'] == 'balloon': continue
        await a.ev('(id)=>{const v=window.__vfr;localStorage.setItem("l3d_missies",JSON.stringify(v.MISSIONS.filter(x=>x.ac===v.ACTYPE&&x.id!==id).map(x=>x.id)))}', m['id'])
        if (await a.v('v.ACTYPE')) != m['ac']:
            await a.ev('(ac)=>window.__vfr.setMode("fly",ac)', m['ac']); await a.frames(2)
            await a.ev('(id)=>{const v=window.__vfr;localStorage.setItem("l3d_missies",JSON.stringify(v.MISSIONS.filter(x=>x.ac===v.ACTYPE&&x.id!==id).map(x=>x.id)))}', m['id'])
        await a.ev('()=>window.__vfr.newTask()'); await a.frames(2)
        ok((await a.v('v.MISSION||{}')).get('id') == m['id'], f'missie {m["id"]} niet gekozen')
        for i in range(m['legs']):
            await a.ev('()=>{const v=window.__vfr,g=v.GOAL;Object.assign(v.PLANE,{x:g.x+.5,n:g.n,alt:1000});v.FAILS.clear();v.CLR.clear();for(const f of v.LAYERS)v.CLR.add(f.ident);v.NOTICE="";v.PAUSED=false;v.hudTick()}')
            n = await a.v('v.NOTICE') or ''
            if i < m['legs'] - 1: ok('Keerpunt' in n, f'{m["id"]}: keerpunt {i+1} niet gemeld: {n[:80]}')
            else: ok('geslaagd' in n and '📘' in n and '⭐' in n, f'{m["id"]}: geen geslaagd + les + ster: {n[:120]}')
        ok(m['id'] in await a.v('v.misDone()'), f'{m["id"]}: niet als gehaald opgeslagen')
    # ballon: misStart eist al een oplosbaar hoogteplan; hier nog eens expliciet
    for m in ms:
        if m['ac'] != 'balloon': continue
        plan = await a.ev('''(id)=>{const v=window.__vfr,m=v.MISSIONS.find(x=>x.id===id),st=v.misStart(m),L={};for(const f of v.TASKF)if(f.t==="L")L[f.name]=f.pts[0];
          const g=L[m.legs[0]];const W=v.windAt;return v.balloonPlan(st.x,st.n,g,Math.hypot(g[0]-st.x,g[1]-st.n))}''', m['id'])
        ok(plan or m['id'] == 'boost', f'ballonmissie {m["id"]}: geen hoogteplan haalt het doel')
    await a.shot('missions')

async def d_tilt_rotate_real(a):  # Christian 21 nov: het draaimoment staand↔liggend; echte draai, vertraagde schermstand, trillende hand
    if not a.touch or a.form == 'p7l': return
    await a.hit('#modal [data-ac=glider]'); await tilt_on(a)
    st = await a.v('v.PLANE'); await a.place(st['x'], st['n'], 2000, 0, paused=False)
    await a.ev('()=>{const v=window.__vfr;for(const f of v.LAYERS)v.WARNED.add(f.ident)}')
    cdp = await a.ctx.new_cdp_session(a.pg); vw = a.pg.viewport_size
    W, H = min(vw['width'], vw['height']), max(vw['width'], vw['height'])
    rng = random.Random(21)
    import time as _t
    async def hold(turn, back, ang, ms, jit=4):
        t0 = _t.time()
        while _t.time() - t0 < ms / 1000:
            await a.ev(SEND, orient(turn + rng.uniform(-jit, jit), back + rng.uniform(-jit, jit), ang, 60)); await a.wait(35)
    async def screen(angle):
        typ = {0: 'portraitPrimary', 90: 'landscapePrimary', 270: 'landscapeSecondary'}[angle]
        w, h = (H, W) if angle else (W, H)
        await cdp.send('Emulation.setDeviceMetricsOverride', {'width': w, 'height': h, 'deviceScaleFactor': 1, 'mobile': True, 'screenOrientation': {'type': typ, 'angle': angle}})
    await a.ev('()=>window.__vfr.resetTilt()'); await hold(0, 0, 0, 500)
    cur = 0
    for nxt, sign in ((90, 1), (0, -1), (270, -1), (0, 1)):
        h0 = await a.v('v.PLANE.hdg')
        for k in range(1, 16):  # fysieke draai van 90° in ±0,5 s, gemeten in het oude scherm
            await a.ev(SEND, orient(sign * 90 * k / 15 + rng.uniform(-4, 4), rng.uniform(-4, 4), cur, 60)); await a.wait(33)
        await hold(sign * 90, 0, cur, 800)  # schermstand nog niet gewisseld (Android-vertraging)
        await screen(nxt); await hold(0, 0, nxt, 1300)
        dh = abs(((await a.v('v.PLANE.hdg')) - h0 + 540) % 360 - 180)
        ok(dh < 6, f'draai {cur}°→{nxt}°: toestel maakte een bocht van {dh:.0f}°')
        await hold(22, 0, nxt, 300, jit=2); r = await a.v('v.TAX.r')
        ok(r > .2, f'na draai naar {nxt}°: rechts kantelen werkt niet (rol {r})')
        await hold(0, 0, nxt, 300); ok(await a.v('v.TAX.r') == 0, f'na draai naar {nxt}°: niet terug naar rechtuit')
        cur = nxt
    # schermstand vergrendeld: telefoon draait, scherm niet → na ≤ 3 s weer bestuurbaar vanuit de nieuwe houding
    for k in range(1, 16):
        await a.ev(SEND, orient(90 * k / 15, 0, 0, 60)); await a.wait(33)
    h0 = await a.v('v.PLANE.hdg')
    await hold(0, 0, 90, 3200)  # fysiek liggend vastgehouden (sensor), scherm blijft staand
    dh = abs(((await a.v('v.PLANE.hdg')) - h0 + 540) % 360 - 180); ok(dh < 6, f'vergrendeld: bocht van {dh:.0f}° tijdens de draai')
    ok(await a.v('v.TAX.r') == 0, 'vergrendeld: stuurt nog na het ijken in de nieuwe houding')
    await hold(22, 0, 90, 300, jit=2); ok(await a.v('v.TAX.r') > .2, 'vergrendeld: niet meer bestuurbaar na draaien')
    await hold(0, 18, 90, 300, jit=2); ok(await a.v('v.TAX.p') > .2 and await a.v('v.TAX.r') == 0, 'vergrendeld: klimmen werkt niet of geeft een bocht')
    await cdp.send('Emulation.clearDeviceMetricsOverride'); await a.sane()

async def d_winch_sites(a):  # backlog 15 nov: schermvlieg-/lierterreinen ontbraken; bron LVNL Geoportaal (Hangglider)
    await a.hit('#modal [data-ac=glider]'); await a.frames(2)
    hg = await a.v('v.HG'); ok(len(hg) >= 8, f'te weinig lierterreinen: {len(hg)}')
    h = next(x for x in hg if x['nm'] == 'Sterksel')
    await a.place(h['x'] - 3, h['n'], 1200, 90, paused=False)
    for _ in range(150):
        await a.wait(100)
        n = await a.v('v.NOTICE') or ''
        if n: break
    ok('Lierterrein Sterksel' in n, f'geen waarschuwing bij lierterrein: {n[:80]}')
    await a.place(h['x'] - 3, h['n'], 3000, 90, paused=False)
    await a.ev('(h)=>{const v=window.__vfr;v.WARNED.delete("HG"+h.nm);Object.assign(v.PLANE,{x:h.x,n:h.n});v.hudTick()}', h)
    ok('Lierterrein' not in (await a.v('v.NOTICE') or ''), 'waarschuwing ook hoog boven het lierterrein (3000 ft)')
    await a.ev('()=>window.__vfr.setMode("map")'); await a.frames(2)
    await a.ev('(h)=>{const v=window.__vfr;v.PROBE.x=h.x;v.PROBE.n=h.n;v.showProbe()}', h); await a.frames(2)
    ok('Lierterrein Sterksel' in await a.pg.inner_text('#info'), 'sonde noemt het lierterrein niet')

async def d_ahead_full(a):  # Noor 1: frequentie in de waarschuwingsregel nooit afgekapt
    await a.hit('#modal [data-ac=motor]')
    e = await a.ev(JS_FREE_EDGE, ['EHEH', 1.8, 1000])
    await a.place(e[0], e[1], 1000, e[2], paused=True)
    await a.ev('()=>{const v=window.__vfr;for(const f of v.LAYERS)v.WARNED.add(f.ident);v.hudTick()}'); await a.frames(2)
    r = await a.ev('()=>{const t=document.querySelector("#banner .ahead");return t?[t.innerText,t.scrollWidth,t.clientWidth]:null}')
    ok(r and '131.005' in r[0] and r[1] <= r[2] + 1, f'waarschuwingsregel afgekapt: {r}')

async def d_tilt_takeoff(a):  # Daan 3: met kantelen opstijgen na de opstijgmelding
    if not a.touch: return
    await a.hit('#modal [data-ac=motor]')
    await tilt_on(a)
    lp = await a.ev('()=>window.__vfr.LAYERS.find(f=>f.ident==="EHEH").lp')
    await a.place(lp[0], lp[1], 0, 0, paused=False)
    send = '(o)=>window.dispatchEvent(Object.assign(new Event("deviceorientation"),{alpha:0,beta:o.beta,gamma:o.gamma}))'
    ang = await a.v('v.tiltAng()')
    await a.ev(send, orient(0, 0, ang)); await a.ev(send, orient(0, 20, ang))
    for _ in range(30):
        await a.frames(2)
        if await a.v('v.NOTICE'): break
    ok('Opstijgen' in (await a.v('v.NOTICE') or ''), 'geen opstijgmelding in de CTR')
    await a.ev(send, orient(0, 0, ang)); await a.frames(3); await a.ev(send, orient(0, 20, ang))
    for _ in range(150):
        await a.frames(2)
        if await a.v('v.PLANE.alt') > 0: break
    ok(await a.v('v.PLANE.alt') > 0, 'met kantelen kom je niet van de grond na de opstijgmelding')

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
    ap.add_argument('-k', default='', help='alleen tests waarvan de naam deze tekst bevat')
    ap.add_argument('--quick', action='store_true', help='smoke op desk+p7 (snelle check per commit)')
    o = ap.parse_args()
    if o.quick: o.only, o.forms = 'smoke', 'desk,p7'
    forms = o.forms.split(',')
    seed = o.seed if o.seed is not None else random.randrange(10**6)
    url = serve()
    smoke = [('laden', t_load), ('kaart+sonde', t_map_probe), ('3 toestellen', t_aircraft), ('modusknop 1 regel', t_modebtn), ('één menu', t_one_menu), ('overlap', t_overlap), ('draaien', t_rotate)]
    det = [('opdracht "vlieg naar"', d_task_text), ('ballondoel bereikbaar met de wind', d_balloon_reachable), ('buitenlandse CTR: radio-info', d_foreign_ctr), ('banner RMZ 1 regel', d_banner_rmz), ('geweigerde klaring op tijd', d_refused), ('klaring aangrenzend gebied', d_adjacent_clearance), ('waarschuwing 2–20 s vooraf', d_warn_lead), ('RMZ Volkel: eerst oproepen', d_rmz_call), ('doel als lijn', d_goal_line), ('ballon voorbij doel', d_balloon_past), ('geslaagd met klaring', d_clearance_success), ('geen klasse G buiten NL', d_outside_nl), ('camera slepen/knijpen zonder schokken', d_touch_smooth), ('kantelen', d_tilt), ('camera: geen sprong, niet direct terugveren', d_cam_no_jump), ('panelpunten 14 nov', d_panel_fixes), ('waarschuwing niet afgekapt', d_ahead_full), ('opdracht vanaf de sonde', d_probe_task), ('kantelen na draaien staand↔liggend', d_tilt_rotate), ('kantelen standaard + knoppen weg', d_tilt_default), ('kantelen: terugval naar knoppen', d_tilt_fallback), ('kantel-looping + ballon', d_tilt_loop_balloon), ('RMZ: oproepen vanuit de RMZ', d_rmz_inside_call), ('zoomen desktop', d_zoom_desktop), ('opstijgen met kantelen', d_tilt_takeoff), ('alles aan + labels aan/uit', d_defaults_labels), ('doelbaken', d_goal_marker), ('tik op melding = verder', d_tap_notice), ('toestel wisselen via toesteltje', d_ac_switch), ('landen in de stad', d_land_city), ('kantelen geleidelijk', d_tilt_analog), ('missies', d_missions), ('draaien staand↔liggend (echt)', d_tilt_rotate_real), ('lierterreinen', d_winch_sites)]
    async with async_playwright() as p:
        b = await p.chromium.launch(args=ARGS)
        for form in forms:
            for layer, tests in (('smoke', smoke), ('det', det)):
                if o.only and o.only != layer: continue
                for name, fn in tests:
                    if o.k and o.k.lower() not in name.lower() and o.k not in fn.__name__: continue
                    a = await new_app(p, b, form, url); await run(layer, name, form, fn, a); await a.ctx.close()
            if (not o.only or o.only == 'fuzz') and not o.k:
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
