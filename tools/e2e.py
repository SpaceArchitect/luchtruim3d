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
    if os.path.isdir(os.path.join(ROOT, 'data')): os.symlink(os.path.join(ROOT, 'data'), os.path.join(d, 'data'))  # heel NL: tegels data/osm-nl
    try: os.symlink(THREE, os.path.join(d, 'three'))
    except OSError: shutil.copytree(THREE, os.path.join(d, 'three'))  # Windows zonder symlinkrecht
    class Q(http.server.SimpleHTTPRequestHandler):
        def log_message(self, *a): pass
        def do_GET(self):
            if self.path.startswith('/favicon'):  # browser vraagt dit zelf; 404 zou als JS-fout tellen
                self.send_response(204); self.end_headers(); return
            super().do_GET()
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
            for _ in range(2):  # paneel schuift in; op klein scherm viel de tik soms midden in de animatie
                if await s.visible('#modal [data-ac=%s]' % ac): break
                if not await s.visible('#btnAc'): await s.hit('#btnPanel'); await s.wait(400)
                await s.hit('#btnAc'); await s.wait(300)
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
    await ctx.add_init_script("try{localStorage.setItem('l3d_keys_seen','1')}catch(e){}")  # sneltoetskaart alleen in d_keycard
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
        await a.ev('()=>{const v=window.__vfr;for(const f of v.LAYERS)v.WARNED.add(f.ident);for(const g of v.HG)v.WARNED.add("HG"+g.ident)}')  # alleen de knop testen, geen luchtruimmelding
        await a.hit('#btnPause'); ok(not await a.v('v.PAUSED'), f'{ac}: start-knop hervat niet ({(await a.v("v.NOTICE") or "")[:60]!r})')
        alt0 = await a.v('v.PLANE.alt')
        if a.touch: await a.hold('#ctrl [data-k=arrowup]', 900)
        else: await a.pg.keyboard.down('ArrowDown'); await a.wait(900); await a.pg.keyboard.up('ArrowDown')  # MSFS: ↓ = neus omhoog
        alt1 = await a.v('v.PLANE.alt')
        ok(alt1 > alt0 or await a.v('v.PAUSED'), f'{ac}: stijgen werkt niet ({alt0}->{alt1})')
        if ac != 'balloon':
            await a.ev('()=>{window.__vfr.NOTICE="";window.__vfr.PAUSED=false}')
            h0 = await a.v('v.PLANE.hdg')
            if a.touch: await a.hold('#ctrl [data-k=arrowright]', 900)
            else: await a.pg.keyboard.down('ArrowRight'); await a.wait(900); await a.pg.keyboard.up('ArrowRight')
            h1 = await a.v('v.PLANE.hdg')
            ok(abs(((h1 - h0 + 540) % 360) - 180) > 2 or await a.v('v.PAUSED'), f'{ac}: draaien werkt niet')
        # geen melding mag tussendoor zelf pauzeren (lierterrein, doel, luchtruim): anders zet de tik hem juist weer aan
        await a.ev('''()=>{const v=window.__vfr;for(let k=0;k<3000;k++){const x=v.PLANE.x+(Math.random()-.5)*60,n=v.PLANE.n+(Math.random()-.5)*60;
          if(v.inNL(x,n)&&!v.featsAt(x,n).some(f=>f.lo<4000)&&![1,2,3,4,5,6].some(d=>v.featsAt(x+Math.sin(v.PLANE.hdg*Math.PI/180)*d,n+Math.cos(v.PLANE.hdg*Math.PI/180)*d).some(f=>f.lo<4000))&&!v.hgNear(x,n,4).length){v.PLANE.x=x;v.PLANE.n=n;break}}
          for(const f of v.LAYERS)v.WARNED.add(f.ident);for(const g of v.HG)v.WARNED.add("HG"+g.ident);v.GOAL=null;v.TASK="";v.NOTICE="";v.PAUSED=false;v.hudTick()}''')
        await a.hit('#btnPause'); ok(await a.v('v.PAUSED'), f'{ac}: pauze werkt niet ({(await a.v("v.NOTICE") or "")[:60]!r})')
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
    rmz = await a.ev('()=>{const v=window.__vfr;return v.LAYERS.filter(f=>f.layer==="RMZ"&&v.AIPINFO[f.ident]&&/MIL Info/.test(v.AIPINFO[f.ident].unit)&&!v.featsAt(f.lp[0],f.lp[1]).some(g=>g.layer==="CTR")).map(f=>[f.ident,f.lp,f.lo])}')  # 27 nov (heel NL): RMZ Niederrhein (EHAARMZ2) ligt onder CTR Niederrhein → die gaat voor in de banner; test een RMZ zonder CTR erboven
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
    await a.ev('()=>{const v=window.__vfr;for(const f of v.LAYERS)v.WARNED.add(f.ident);for(const g of v.HG)v.WARNED.add("HG"+g.ident);v.GOAL={x:v.PLANE.x-0.1,n:v.PLANE.n-4.2,name:"Testdoel",min:1.7};v.TASK="Drijf naar Testdoel";v.hudTick()}')
    n = await a.v('v.NOTICE') or ''
    ok('Missie mislukt' in n and 'ballon' in n, f'ballon voorbij doel geen "mislukt": {n[:80]!r}')
    ok(await a.v('v.GOAL') is None, 'doel blijft staan na mislukt')
    await a.fly('glider')
    st = await a.v('v.PLANE')
    await a.place(st['x'], st['n'], 1500, st['hdg'], paused=False)
    await a.ev('()=>{const v=window.__vfr;for(const f of v.LAYERS)v.WARNED.add(f.ident);for(const g of v.HG)v.WARNED.add("HG"+g.ident);v.NOTICE="";v.PAUSED=false;v.GOAL={x:v.PLANE.x,n:v.PLANE.n-4.2,name:"Testdoel",min:1.7};v.hudTick()}')  # andere meldingen uit: alleen 'doel gemist' testen
    n = await a.v('v.NOTICE') or ''
    ok('Doel gemist' in n, f'zweefvliegtuig voorbij doel: {n[:60]!r}')

async def d_clearance_success(a):
    await a.hit('#modal [data-ac=motor]')
    ctr = await a.ev('()=>{const v=window.__vfr;const f=v.LAYERS.find(g=>g.ident==="EHEH"&&g.layer==="CTR")||v.LAYERS.find(g=>g.layer==="CTR"&&g.lo===0&&v.AIPINFO[g.ident]);return f&&[f.ident,f.lp]}')  # 27 nov (heel NL): Eindhoven, want de eerste CTR (Beek) ligt naast RMZ Maastricht en die naderingsmelding gaat terecht voor
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
        await a.ev('()=>{const v=window.__vfr;v.setTempo(5);for(const f of v.LAYERS)v.WARNED.add(f.ident);for(const g of v.HG)v.WARNED.add("HG"+g.ident);window.__R=[];const f=()=>{const c=v.camera.position,p=v.PLANE;window.__R.push([c.x-p.x,c.y,-c.z-p.n]);if(window.__R.length<500)requestAnimationFrame(f)};requestAnimationFrame(f)}')
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
    await a.ev('()=>{const v=window.__vfr;for(const f of v.LAYERS)v.WARNED.add(f.ident);for(const g of v.HG)v.WARNED.add("HG"+g.ident)}')
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

async def d_msfs_keys(a):  # Christian 21 nov: W/↑ = neus omlaag, S/↓ = neus omhoog, A/D draaien, Shift+S = looping
    if a.touch: return
    await a.hit('#modal [data-ac=motor]'); await a.frames(2)
    st = await a.v('v.PLANE')
    for key, sign in (('w', -1), ('ArrowUp', -1), ('s', 1), ('ArrowDown', 1)):
        await a.place(st['x'], st['n'], 3000, st['hdg'], paused=False)
        await a.ev('()=>{const v=window.__vfr;for(const f of v.LAYERS)v.WARNED.add(f.ident);for(const g of v.HG)v.WARNED.add("HG"+g.ident);v.NOTICE="";v.PAUSED=false}')
        a0 = await a.v('v.PLANE.alt')
        await a.pg.keyboard.down(key); await a.wait(700); await a.pg.keyboard.up(key)
        a1 = await a.v('v.PLANE.alt')
        ok((a1 - a0) * sign > 0, f'{key}: hoogte {a0:.0f}→{a1:.0f}, verwacht {"omhoog" if sign > 0 else "omlaag"}')
    ok(not any((await a.ev('()=>Object.entries(window.__vfr.keys).filter(([k,v])=>v).map(([k])=>k)'))), 'toets blijft hangen na loslaten')
    for key, sign in (('d', 1), ('a', -1)):
        await a.ev('()=>{window.__vfr.NOTICE="";window.__vfr.PAUSED=false}')
        h0 = await a.v('v.PLANE.hdg'); await a.pg.keyboard.down(key); await a.wait(600); await a.pg.keyboard.up(key); h1 = await a.v('v.PLANE.hdg')
        ok(((h1 - h0 + 540) % 360 - 180) * sign > 1, f'{key}: koers {h0:.0f}→{h1:.0f}')
    await a.place(st['x'], st['n'], 3000, st['hdg'], paused=False)
    await a.ev('()=>{const v=window.__vfr;v.NOTICE="";v.PAUSED=false}')
    await a.pg.keyboard.press('Shift+S'); await a.frames(2)
    ok(await a.v('!!v.LOOP'), 'Shift+S start geen looping')
    for _ in range(50):
        await a.wait(100)
        if not await a.v('!!v.LOOP'): break
    ok(not await a.v('!!v.LOOP'), 'looping eindigt niet')
    ok(not await a.visible('#ctrl [data-k=arrowup]') and await a.visible('#btnPause'), 'desktop: stuurknoppen zichtbaar of pauzeknop weg')
    t = await a.ev('()=>document.querySelector(".note.kb")?.textContent||""')
    ok('W of ↑' in t and 'Shift+S' in t, f'uitleg toetsen niet bijgewerkt: {t[:80]}')

async def d_keycard(a):  # Christian 21 nov: kleine uitleg sneltoetsen vóór de vlucht, makkelijk over te slaan
    if a.touch:
        await a.ev('()=>{localStorage.removeItem("l3d_keys_seen");sessionStorage.clear()}')
        await a.hit('#modal [data-ac=glider]'); await a.frames(2)
        ok(not await a.visible('#keycard'), 'telefoon: sneltoetskaart verschijnt (hoort alleen op desktop)'); return
    await a.ev('()=>{localStorage.removeItem("l3d_keys_seen");sessionStorage.clear()}')
    await a.hit('#modal [data-ac=glider]'); await a.frames(2)
    ok(await a.visible('#keycard'), 'geen sneltoetskaart bij start vlucht')
    t = await a.ev('()=>document.getElementById("keycard").innerText')
    ok('Shift' in t and 'neus omhoog' in t and 'Spatie' in t, f'kaart mist toetsen: {t[:100]}')
    await a.shot('keycard')
    p0 = await a.v('v.PAUSED')
    await a.pg.keyboard.press('Space'); await a.frames(2)
    ok(not await a.visible('#keycard'), 'kaart gaat niet weg met een toets')
    ok(await a.v('v.PAUSED') == p0, 'de toets die de kaart sluit, deed ook iets anders')
    await a.ev('()=>window.__vfr.setMode("map")'); await a.ev('()=>window.__vfr.setMode("fly","motor")'); await a.frames(2)
    ok(not await a.visible('#keycard'), 'kaart komt in hetzelfde bezoek terug')
    await a.pg.keyboard.press('?'); await a.frames(1)
    ok(await a.visible('#keycard'), '? opent de kaart niet')
    await a.ev('()=>document.getElementById("kcNo").click()'); await a.pg.mouse.click(5, 5); await a.frames(1)
    ok(not await a.visible('#keycard'), 'klik sluit de kaart niet')
    ok(await a.ev('()=>localStorage.getItem("l3d_keys_seen")') == '1', '"niet meer tonen" niet onthouden')
    await a.ev('()=>window.__vfr.setMode("fly","balloon")'); await a.pg.keyboard.press('h'); await a.frames(1)
    t = await a.ev('()=>document.getElementById("keycard")?.innerText||""')
    ok('stijgen' in t and 'Shift' not in t, f'ballonkaart klopt niet: {t[:100]}')
    await a.pg.keyboard.press('Escape')

async def d_space_waypoints(a):  # Christian 21 nov: keerpunt → Spatie = volgende; laatste → Spatie = volgende missie
    if a.touch: return
    await a.hit('#modal [data-ac=glider]'); await a.frames(2)
    await a.ev('()=>{const v=window.__vfr;localStorage.setItem("l3d_missies",JSON.stringify(v.MISSIONS.filter(x=>x.ac==="glider"&&x.id!=="torens").map(x=>x.id)));v.newTask()}'); await a.frames(2)
    ok((await a.v('v.MISSION||{}')).get('id') == 'torens', 'missie torens niet gekozen')
    reach = '()=>{const v=window.__vfr,g=v.GOAL;Object.assign(v.PLANE,{x:g.x+.5,n:g.n,alt:1000});v.FAILS.clear();v.CLR.clear();for(const f of v.LAYERS)v.CLR.add(f.ident);for(const f of v.LAYERS)v.WARNED.add(f.ident);for(const h of v.HG)v.WARNED.add("HG"+h.ident);v.NOTICE="";v.PAUSED=false;v.hudTick()}'
    for i in range(2):
        await a.ev(reach); await a.frames(2)
        txt = await a.ev('()=>document.querySelector("#banner .notice")?.innerText||""')
        ok('Keerpunt' in txt and 'Spatie' in txt, f'keerpunt {i+1}: geen "Spatie" in melding: {txt[:90]}')
        await a.pg.keyboard.press('Space'); await a.frames(2)
        ok(not await a.v('v.PAUSED') and (await a.v('v.GOAL'))['li'] == i + 1, f'Spatie gaat niet door naar keerpunt {i+2}')
    await a.ev(reach); await a.frames(2)
    txt = await a.ev('()=>document.querySelector("#banner .notice")?.innerText||""')
    ok('geslaagd' in txt and 'spatie' in txt.lower(), f'laatste keerpunt: geen spatie-hint: {txt[:120]}')
    await a.ev('()=>localStorage.setItem("l3d_missies",JSON.stringify(window.__vfr.MISSIONS.filter(x=>x.ac==="glider"&&x.id!=="vught").map(x=>x.id)))')
    await a.pg.keyboard.press('Space'); await a.frames(2)
    m = (await a.v('v.MISSION||{}')).get('id')
    ok(m == 'vught', f'Spatie start niet de volgende missie (vught), maar {m}')

async def d_tilt_default(a):  # S1c (Christian): op telefoon standaard kantelen + knoppen weg; geen sensor = knoppen terug; uitzetten onthouden
    await a.hit('#modal [data-ac=glider]'); await a.frames(2)
    on = await a.ev('()=>document.getElementById("optTilt").checked')
    if not a.touch:
        ok(not on, 'desktop: kantelen staat aan'); ok(not await a.visible('#ctrl [data-k=arrowup]'), 'desktop: stuurknoppen nog zichtbaar (Christian 21 nov: weg)'); return
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
    st = await a.ev('()=>{const v=window.__vfr;for(let k=0;k<20000;k++){const r=k<3000?60:300,x=v.PLANE.x+(Math.random()-.5)*r,n=v.PLANE.n+(Math.random()-.5)*r;if(v.inNL(x,n)&&!v.featsAt(x,n).some(f=>f.lo<4000)&&!v.featsAt(x+Math.sin(0)*6,n+6).some(f=>f.lo<4000))return {x,n}}return null}')
    ok(st, 'geen vrije plek gevonden')
    await a.place(st['x'], st['n'], 2000, 0, paused=True)  # eerst alle meldingen 'gezien', dan pas vliegen (race)
    await a.ev('()=>{const v=window.__vfr;for(const f of v.LAYERS)v.WARNED.add(f.ident);for(const g of v.HG)v.WARNED.add("HG"+g.ident);for(const h of v.HG)v.WARNED.add("HG"+h.ident);v.NOTICE="";v.PAUSED=false;v.resetTilt()}')
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
    st = await a.ev('()=>{const v=window.__vfr;for(let k=0;k<20000;k++){const r=k<3000?60:300,x=v.PLANE.x+(Math.random()-.5)*r,n=v.PLANE.n+(Math.random()-.5)*r;if(v.inNL(x,n)&&!v.featsAt(x,n).some(f=>f.lo<4000))return {x,n}}return null}')
    ok(st, 'geen vrije plek voor de ballon gevonden')
    await a.place(st['x'], st['n'], 1000, 0, paused=False)
    await a.ev('()=>{const v=window.__vfr;for(const f of v.LAYERS)v.WARNED.add(f.ident);for(const g of v.HG)v.WARNED.add("HG"+g.ident);v.resetTilt()}')
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
    for _ in range(6):  # ENR 5.5-terreinen bij Gilze-Rijen geven elk één melding; die eerst wegklikken
        await a.ev('()=>{const v=window.__vfr;v.NOTICE="";v.PAUSED=false;v.hudTick()}'); await a.frames(2)
        if not await a.v('v.NOTICE'): break
    ok('OPGEROEPEN' in await a.ev('()=>(document.querySelector("#banner .head")||{innerText:""}).innerText'), 'statusregel toont geen OPGEROEPEN: ' + str(await a.v('v.NOTICE'))[:100])

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

async def d_start_next(a):  # Christian 25 nov: ▶ Start na geslaagd/mislukt = volgende missie (vloog verder zonder opdracht)
    await a.hit('#modal [data-ac=glider]'); await a.frames(2)
    reach = '()=>{const v=window.__vfr,g=v.GOAL;Object.assign(v.PLANE,{x:g.x+.5,n:g.n,alt:1000});v.FAILS.clear();v.CLR.clear();for(const f of v.LAYERS)v.CLR.add(f.ident);for(const f of v.LAYERS)v.WARNED.add(f.ident);for(const h of v.HG)v.WARNED.add("HG"+h.ident);v.NOTICE="";v.PAUSED=false;v.hudTick()}'
    for fail in (False, True):
        await a.ev('()=>{const v=window.__vfr;localStorage.setItem("l3d_missies",JSON.stringify(v.MISSIONS.filter(x=>x.ac==="glider"&&x.id!=="torens").map(x=>x.id)));v.newTask()}'); await a.frames(2)
        ok((await a.v('v.MISSION||{}')).get('id') == 'torens', 'missie torens niet gekozen')
        for i in range(5):  # alle keerpunten (+ de directe foutmelding bij 'mislukt', 26 nov)
            if not await a.v('v.GOAL'): break
            await a.ev(reach.replace('v.FAILS.clear();', 'v.FAILS.clear();v.FAILS.set("X","verboden gebied X");') if fail else reach); await a.frames(2)
            if await a.v('v.GOAL') and ('Keerpunt' in await a.v('v.NOTICE') or '↻ Opnieuw' in await a.v('v.NOTICE')): await a.ev('()=>{const v=window.__vfr;v.NOTICE="";v.PAUSED=false}')
        n = await a.v('v.NOTICE'); ok(('mislukt' if fail else 'geslaagd') in n, f'geen einde-melding: {n[:80]}')
        ok('volgende opdracht' in n or '▶ = opnieuw' in n, f'einde-melding zegt niet wat ▶ doet: {n[:120]}')
        await a.ev('()=>localStorage.setItem("l3d_missies",JSON.stringify(window.__vfr.MISSIONS.filter(x=>x.ac==="glider"&&x.id!=="vught").map(x=>x.id)))')
        await a.hit('#btnPause'); await a.frames(2)
        m = (await a.v('v.MISSION||{}')).get('id')
        ok(m == 'vught' and await a.v('v.TASK') and await a.v('v.GOAL'), f'▶ Start na {"mislukt" if fail else "geslaagd"} startte niet de volgende missie (vught), maar {m}')
        await a.hit('#btnPause'); await a.frames(2)
        ok(not await a.v('v.PAUSED') and await a.v('v.TASK'), 'tweede ▶ start de nieuwe missie niet')

async def d_hg_ring_ground(a):  # Christian 25 nov: grondring van lier-/zweef-/modelterreinen zweefde boven de grond (ring y=50 m, cilinder y=0)
    await a.hit('#modal [data-ac=glider]'); await a.frames(2)
    r = await a.ev('''()=>{const v=window.__vfr,T=v.THREE,bad=[];v.hgGroup.updateMatrixWorld(true);
      const rings=v.hgGroup.children.filter(o=>o.userData.hgR),cyl=v.hgCyl.children.filter(o=>o.userData.hg);
      for(const rg of rings){const p=rg.getWorldPosition(new T.Vector3());let best=null,bd=1e9;
        for(const c of cyl){const q=c.getWorldPosition(new T.Vector3()),d=Math.hypot(q.x-p.x,q.z-p.z);if(d<bd){bd=d;best=c;}}
        const bb=new T.Box3().setFromObject(best),foot=bb.min.y;
        if(Math.abs(foot-p.y)>.003||p.y<.004||p.y>.02)bad.push([best.userData.hg,+p.y.toFixed(3),+foot.toFixed(3)]);}
      return {n:rings.length,bad:bad.slice(0,5)};}''')
    ok(r['n'] > 10, f'te weinig grondringen: {r["n"]}')
    ok(not r['bad'], f'ring niet op de cilindervoet/grond (naam, ring-y, voet-y in km): {r["bad"]}')

async def d_vario_real(a):  # Christian 25 nov: vario toonde altijd de vaste stijgsnelheid (400 ft/min), niet hoe hard je echt stijgt
    await a.hit('#modal [data-ac=glider]'); await a.frames(2)
    st = await a.v('v.PLANE')
    async def vario(p, n=40):
        await a.place(st['x'], st['n'], 3000, st['hdg'])
        await a.ev('()=>{const v=window.__vfr;for(const f of v.LAYERS){v.WARNED.add(f.ident);v.CLR.add(f.ident)}for(const h of v.HG)v.WARNED.add("HG"+h.ident);v.resetTilt()}')
        for _ in range(n):
            await a.ev('(p)=>{const v=window.__vfr;v.keys.tu=p>0;v.keys.td=p<0;v.TAX.p=p;v.NOTICE="";v.PAUSED=false}', p); await a.frames(1)
        await a.ev('()=>window.__vfr.hudTick()')
        t = await a.ev('()=>document.querySelector("#loc .vario")?.innerText||""')
        await a.ev('()=>{const v=window.__vfr;v.keys.tu=v.keys.td=false;v.TAX.p=0}')
        return t
    full, half, down = await vario(1), await vario(.5), await vario(-.4)
    num = lambda t: int(''.join(c for c in t if c.isdigit()) or 0)
    ok('↑' in full and 370 <= num(full) <= 430, f'vol stijgen: verwacht ±400 ft/min, kreeg "{full}"')
    ok('↑' in half and 170 <= num(half) <= 230, f'half stijgen (kantelen): verwacht ±200 ft/min, kreeg "{half}"')
    ok('↓' in down and 130 <= num(down) <= 190, f'licht dalen: verwacht ±160 ft/min, kreeg "{down}"')
    await a.place(st['x'], st['n'], 0, st['hdg'])
    for _ in range(30):
        await a.ev('()=>{const v=window.__vfr;v.keys.td=true;v.TAX.p=-1;v.NOTICE="";v.PAUSED=false}'); await a.frames(1)
    await a.ev('()=>{const v=window.__vfr;v.keys.td=false;v.TAX.p=0;v.hudTick()}')
    t = await a.ev('()=>document.querySelector("#loc .vario")?.innerText||""')
    ok(not t, f'op de grond met "dalen" toont de vario nog "{t}"')

async def d_line_goal_whole(a):  # Christian 25 nov: ballon geland aan de Maas, opdracht 'Drijf naar de Maas' niet geslaagd (doel = één OSM-stuk)
    # klasse: elke rivier-/wegopdracht moet op élk OSM-stuk met die naam te halen zijn (grondwaarheid = de ruwe OSM-regels)
    await a.hit('#modal [data-ac=balloon]'); await a.frames(2)
    r = await a.ev('''()=>{const v=window.__vfr,raw={};
      for(const l of document.getElementById('osm').textContent.trim().split('\\n').map(l=>l.split('|')))if(l[0]==='R'||l[0]==='W'){const k=l[0]+l[1].replace('A ','A');(raw[k]=raw[k]||[]).push(v.decode(l[2]).map(([lo,la])=>v.proj(lo,la)));}
      const bad=[],seen=new Set();let rnd=1;const R=()=>(rnd=(rnd*16807)%2147483647)/2147483647;
      for(let k=0;k<6000;k++){const [x0,n0,x1,n1]=v.BOUNDS,x=x0+R()*(x1-x0),n=n0+R()*(n1-n0),h=R()*360;
        if(!v.pickTask(x,n,h,'motor'))continue;const g={...v.LASTGOAL};if(!g.pts)continue;const key=g.name.replace(/^de /,'');
        const t=(raw['W'+key]?'W':'R')+key;if(seen.has(t)||!raw[t])continue;seen.add(t);
        for(const pc of raw[t]){const m=pc[Math.floor(pc.length/2)],d=v.goalDist(g,m[0],m[1]);if(d>.3)bad.push(key+' '+d.toFixed(1)+' km');}}
      return {seen:[...seen],multi:[...seen].filter(t=>raw[t].length>1).length,bad:bad.slice(0,6)};}''')
    ok(r['multi'] >= 5, f'te weinig lijndoelen met meerdere OSM-stukken getest: {r["seen"]}')
    ok(not r['bad'], f'lijndoel mist OSM-stukken met dezelfde naam (afstand tot het doel op dat stuk): {r["bad"]}')
    # echt: ballon boven een ánder stuk van de Maas dan het gekozen doelpunt → geslaagd
    g = await a.ev('''()=>{const v=window.__vfr,[x0,n0,x1,n1]=v.BOUNDS;let rnd=7;const R=()=>(rnd=(rnd*16807)%2147483647)/2147483647;
      for(let k=0;k<20000;k++){const x=x0+R()*(x1-x0),n=n0+R()*(n1-n0),h=R()*360;if(v.pickTask(x,n,h,'balloon')&&v.LASTGOAL.name==='de Maas')break;}
      if(v.LASTGOAL.name!=='de Maas')return null;const g={...v.LASTGOAL};let far=null;
      for(const pc of document.getElementById('osm').textContent.trim().split('\\n').map(l=>l.split('|')).filter(l=>l[0]==='W'&&l[1]==='Maas').map(l=>v.decode(l[2]).map(([lo,la])=>v.proj(lo,la))))
        for(const p of pc)if(Math.hypot(p[0]-g.x,p[1]-g.n)>6&&v.inNL(p[0],p[1])){far=p;break;}
      return far&&{g,far};}''')
    ok(g, 'geen ballonopdracht naar de Maas te maken')
    await a.place(g['far'][0] + .3, g['far'][1], 300, 0)
    await a.ev('''(g)=>{const v=window.__vfr;v.GOAL=g;v.TASK="Drijf naar de Maas";for(const f of v.LAYERS){v.WARNED.add(f.ident);v.CLR.add(f.ident)}for(const h of v.HG)v.WARNED.add("HG"+h.ident);v.PAUSED=false;v.hudTick()}''', g['g'])
    await a.frames(3)
    n = await a.v('v.NOTICE'); ok('geslaagd' in n, f'ballon 300 m naast een ander stuk van de Maas: niet geslaagd: {n[:100]}')

async def d_click_all(a):  # Christian 25 nov: elk luchtruim aanklikbaar, ook ENR 5.5-terreinen (lier, zweef, model, ULV); klik raakte alleen airGroup
    await a.hit('#modal [data-ac=map]'); await a.frames(3); await a.wait(1500)  # openingsanimatie van de camera eerst af
    aim = '''(i)=>{const v=window.__vfr,T=v.THREE,hs=v.HG.filter(h=>h.typ!=="gld"),h=hs[i%hs.length];v.controls.target.set(h.x,0,-h.n);
      v.camera.position.set(h.x+1.5,3.2,-h.n+5.5);v.controls.update();v.camera.updateMatrixWorld();const H=h.top*0.0003048*v.EXAG,
      p=new T.Vector3(h.x,H*.6,-h.n).project(v.camera);return {nm:h.nm,x:h.x,n:h.n,typ:h.typ,sx:(p.x+1)/2*innerWidth,sy:(1-p.y)/2*innerHeight,cnt:hs.length};}'''
    cnt = (await a.ev(aim, 0))['cnt']; tested = 0
    for i in range(0, cnt, max(1, cnt // 4)):
        t = await a.ev(aim, i); await a.frames(3); t = await a.ev(aim, i)
        el = await a.ev('([x,y])=>document.elementFromPoint(x,y)?.tagName', [t['sx'], t['sy']])
        if el != 'CANVAS': continue
        await a.tap_xy(t['sx'], t['sy']); await a.frames(3)
        pr = await a.v('v.PROBE'); txt = await a.ev('()=>document.getElementById("info").innerText')
        ok(abs(pr['x'] - t['x']) < .2 and abs(pr['n'] - t['n']) < .2, f"kaart: tik op terrein {t['nm']} ({t['x']:.1f},{t['n']:.1f} scherm {t['sx']:.0f},{t['sy']:.0f}) zette de sonde niet op het terrein (sonde {pr['x']:.1f},{pr['n']:.1f}) i={i}")
        ok(t['nm'] in txt, f'kaart: info noemt terrein {t["nm"]} niet: {txt[:120]}')
        tested += 1
    ok(tested >= 2, f'te weinig terreinen aangetikt ({tested})')
    # vliegmodus: klik op een terrein → info met naam en bovengrens
    await a.fly('glider'); st = await a.v('v.PLANE'); await a.place(st['x'], st['n'], 1500, st['hdg'], paused=True)
    r = await a.ev('''()=>{const v=window.__vfr,T=v.THREE,h=v.HG.find(h=>h.typ==="hg");v.camera.position.set(h.x+1.5,2.5,-h.n+5);v.camera.lookAt(h.x,0.3,-h.n);v.camera.updateMatrixWorld();
      const p=new T.Vector3(h.x,h.top*0.0003048*v.EXAG*.5,-h.n).project(v.camera);v.ray.setFromCamera(new T.Vector2(p.x,p.y),v.camera);const hs=v.pickHits().map(q=>q.object.userData.h&&q.object.userData.h.nm).filter(Boolean);return {nm:h.nm,hs};}''')
    ok(r['nm'] in r['hs'], f'vliegmodus: straal door terrein {r["nm"]} raakt het niet: {r["hs"][:3]}')

async def d_chase_landscape(a):  # Christian 25 nov (Pixel liggend): chase-camera te ver weg, toestel nauwelijks zichtbaar
    if not a.touch: return
    vw = a.pg.viewport_size; W, H = min(vw['width'], vw['height']), max(vw['width'], vw['height'])
    await a.fly('glider'); st = await a.v('v.PLANE')
    meas = '''()=>{const v=window.__vfr,T=v.THREE,o=v.model();o.updateMatrixWorld(true);const b=new T.Box3().setFromObject(o);let x0=1e9,x1=-1e9,y0=1e9,y1=-1e9;
      for(const x of [b.min.x,b.max.x])for(const y of [b.min.y,b.max.y])for(const z of [b.min.z,b.max.z]){const p=new T.Vector3(x,y,z).project(v.camera);const sx=(p.x+1)/2*innerWidth,sy=(1-p.y)/2*innerHeight;x0=Math.min(x0,sx);x1=Math.max(x1,sx);y0=Math.min(y0,sy);y1=Math.max(y1,sy);}
      return Math.max(x1-x0,y1-y0);}'''
    out = []
    for w, h in ((W, H), (H, W)):
        await a.pg.set_viewport_size({'width': w, 'height': h}); await a.wait(600)
        await a.place(st['x'], st['n'], 1500, st['hdg'], paused=True); await a.ev('()=>window.__vfr.chase(0,true)'); await a.frames(4)
        out.append(await a.ev(meas))
    await a.pg.set_viewport_size({'width': W, 'height': H}); await a.wait(400)
    ok(out[1] >= .75 * out[0], f'toestel liggend {out[1]:.0f} px vs staand {out[0]:.0f} px (moet ≥ 75%)')

async def d_labels_off_aircraft(a):  # Christian 25 nov (Pixel liggend): labels bedekken het eigen toestel. Over meerdere frames, vanuit willekeurige voorgeschiedenis
    await a.fly('glider'); bad = []; shown = 0
    for ident in ('EHEH', 'EHDL', 'EHVK', 'EHGR'):
        await a.ev('''(id)=>{const v=window.__vfr,f=v.LAYERS.find(g=>g.ident===id);const [x,n]=f.lp;Object.assign(v.PLANE,{x:x-3,n:n-3,alt:1500,hdg:45});
          for(const g of v.LAYERS)v.WARNED.add(g.ident);v.NOTICE="";v.PAUSED=true;v.chase(0,true);v.hudTick()}''', ident)
        r = await a.ev('''n=>new Promise(res=>{const v=window.__vfr,L=v.labels;for(const l of L){l.prev=Math.random()<.5;}let k=0,bad=[],sh=0;
          const f=()=>{const A=v.acRect();if(A)for(const l of L){if(l.el.style.display!=='block')continue;sh++;const b=l.el.getBoundingClientRect();
            if(b.left<A[2]&&b.right>A[0]&&b.top<A[3]&&b.bottom>A[1])bad.push(l.el.textContent.slice(0,30));}
            if(++k>=n)res({bad:[...new Set(bad)],sh});else requestAnimationFrame(f);};requestAnimationFrame(f);})''', 20)
        bad += [f'{ident}: {b}' for b in r['bad']]; shown += r['sh']
    ok(shown > 0, 'geen enkel label zichtbaar in vliegmodus (test bewijst niets)')
    ok(not bad, f'label over het eigen toestel: {bad[:4]}')

async def d_unique_idents(a):  # 26 nov: LVNL gebruikt één ident voor CTR én TMA (EHLE1/2, EHGG, EHBK2); AIPINFO per ident gaf Lelystad CTR de Arrival-frequentie
    r = await a.ev("()=>{const v=window.__vfr,c={};for(const f of v.LAYERS)(c[f.ident]=c[f.ident]||[]).push(f.layer);return Object.entries(c).filter(([k,l])=>new Set(l).size>1).map(([k,l])=>k+':'+l.join('/'))}")
    ok(not r, f'ident hoort bij meerdere soorten luchtruim (AIPINFO raakt de verkeerde): {r[:5]}')
    u = await a.ev("()=>{const v=window.__vfr;return v.LAYERS.filter(f=>f.layer==='CTR'&&v.AIPINFO[f.ident]&&/Arrival|Approach|Radar/.test(v.AIPINFO[f.ident].unit)).map(f=>f.ident)}")
    ok(not u, f'CTR met een naderings-eenheid als radio (hoort Tower/Info): {u[:5]}')

async def d_fail_restart(a):  # Christian 26 nov: fout vóór keerpunt 1 (verboden gebied, geen klaring) → meteen stoppen met de reden, ↻ opnieuw of toch door
    await a.hit('#modal [data-ac=glider]'); await a.frames(2)
    start = '()=>{const v=window.__vfr;localStorage.setItem("l3d_missies",JSON.stringify(v.MISSIONS.filter(x=>x.ac==="glider"&&x.id!=="vught").map(x=>x.id)));v.newTask();v.PAUSED=false;v.NOTICE="";v.hudTick()}'
    bad = '()=>{const v=window.__vfr,f=v.LAYERS.find(g=>g.layer==="P"),[x,n]=f.lp;Object.assign(v.PLANE,{x,n,alt:Math.min(1000,f.hi-200)});for(const g of v.LAYERS)v.WARNED.add(g.ident);v.NOTICE="";v.PAUSED=false;v.hudTick()}'
    await a.ev(start); await a.frames(2)
    m0 = (await a.v('v.MISSION||{}')).get('id'); st0 = await a.v('[v.PLANE.x,v.PLANE.n]')
    await a.ev(bad); await a.frames(3)
    n = await a.v('v.NOTICE'); ok(await a.v('v.PAUSED') and 'mislukt' in n and 'verboden' in n, f'geen directe melding met reden na verboden gebied: {n[:120]}')
    ok('Opnieuw' in n, f'melding mist ↻ Opnieuw: {n[:200]}')
    await a.hit('#btnPause'); await a.frames(2)
    m1 = (await a.v('v.MISSION||{}')).get('id'); p1 = await a.v('[v.PLANE.x,v.PLANE.n]')
    ok(m1 == m0 and abs(p1[0] - st0[0]) < .5 and abs(p1[1] - st0[1]) < .5, f'▶ herstart de missie niet vanaf de start: {m0}→{m1}, {st0}→{p1}')
    ok(not await a.v('v.FAILS.size'), 'na opnieuw staan de fouten er nog')
    # Christian 26 nov: geen 'Toch doorvliegen'; tik op de melding = ook opnieuw
    await a.ev(start); await a.frames(2); await a.ev(bad); await a.frames(3)
    n = await a.v('v.NOTICE'); ok('Toch doorvliegen' not in n, 'knop "Toch doorvliegen" staat er weer')
    b = await a.pg.locator('#banner .notice').first.bounding_box()
    if a.touch: await a.pg.touchscreen.tap(b['x'] + 12, b['y'] + 10)
    else: await a.pg.mouse.click(b['x'] + 12, b['y'] + 10, delay=90)
    await a.wait(300); await a.frames(2)
    p2 = await a.v('[v.PLANE.x,v.PLANE.n]'); ok(abs(p2[0] - st0[0]) < .5 and abs(p2[1] - st0[1]) < .5 and not await a.v('v.FAILS.size'), f'tik op de foutmelding herstart niet: {p2}')

async def d_bridge_size(a):  # Christian 26 nov (screenshot Pixel liggend): bruggen veel te groot. Oorzaak: lmMinSize schaalde onbegrensd met de afstand (×30 op 80 km)
    await a.hit('#modal [data-ac=glider]'); await a.frames(2); bad = []
    for lo, la, h in ((5.43, 51.89, 124), (5.86, 51.84, 270), (5.2, 51.75, 45)):
        await a.ev('([lo,la,h])=>{const v=window.__vfr,[x,n]=v.proj(lo,la);Object.assign(v.PLANE,{x,n,alt:1500,hdg:h});for(const f of v.LAYERS)v.WARNED.add(f.ident);v.NOTICE="";v.PAUSED=true;v.chase(0,true);v.hudTick()}', [lo, la, h])
        await a.frames(4)
        r = await a.ev('()=>{const v=window.__vfr,T=v.THREE;return v.lmGroup.children.filter(g=>g.userData.bridge&&g.visible).map(g=>{const b=new T.Box3().setFromObject(g),s=b.getSize(new T.Vector3());return [g.userData.bridge,+Math.max(s.x,s.z).toFixed(1)]}).filter(([n,L])=>L>2.5)}')
        bad += [f'{n} {L} km' for n, L in r]
    ok(not bad, f'brugmodel langer dan 2,5 km in beeld (moet ±0,7–2 km zijn): {bad[:5]}')

async def d_no_zfight(a):  # Christian 26 nov: treinspoor knippert (z-fighting). Klasse: twee lijnen/vlakken op ≈ dezelfde hoogte die allebei diepte schrijven
    await a.hit('#modal [data-ac=map]'); await a.frames(2)
    r = await a.ev("""()=>{const v=window.__vfr,T=v.THREE,out=[],items=[];v.scene.traverse(o=>{if(!(o.isLine||o.isMesh)||!o.visible||!o.material||o.material.depthWrite===false||o.material.depthTest===false)return;
      o.updateMatrixWorld();const b=new T.Box3().setFromObject(o);if(b.isEmpty()||b.max.y-b.min.y>.002||b.max.y>.05)return;items.push([o,b]);});
      for(let i=0;i<items.length;i++)for(let j=i+1;j<items.length;j++){const [p,a]=items[i],[q,c]=items[j];if(Math.abs(a.min.y-c.min.y)<.0025&&Math.abs(a.min.y-c.min.y)>0&&a.min.x<=c.max.x&&a.max.x>=c.min.x&&a.min.z<=c.max.z&&a.max.z>=c.min.z/* alleen grondvlak: platte kaders op verschillende hoogte snijden nooit */&&p.isLine&&q.isLine)out.push((p.userData.nm||p.type)+'/'+(q.userData.nm||q.type)+' y='+a.min.y.toFixed(4)+'/'+c.min.y.toFixed(4));}
      return [items.length,out.slice(0,5)];}""")
    ok(not r[1], f'lijnen op bijna dezelfde hoogte die allebei diepte schrijven (knipperen op telefoons): {r[1]}')

async def d_lm_size(a):  # Christian 26 nov: niet alleen bruggen; geen enkel 3D-herkenningspunt mag ineens het halve beeld vullen (overdreven schaal mag)
    big = []
    js = '''()=>{const v=window.__vfr,T=v.THREE,W=innerWidth,H=innerHeight,out=[],b=new T.Box3(),p=new T.Vector3();
      for(const G of [v.lmGroup,...v.extraGroups()])for(const g of G.children){if(!g.visible||!G.visible)continue;let m=false;g.traverse(o=>{if(o.isMesh)m=true});if(!m)continue;b.setFromObject(g);if(b.isEmpty())continue;
        let x0=1e9,x1=-1e9,y0=1e9,y1=-1e9,beh=false;for(let i=0;i<8;i++){p.set(i&1?b.max.x:b.min.x,i&2?b.max.y:b.min.y,i&4?b.max.z:b.min.z).project(v.camera);if(p.z>1){beh=true;break;}const sx=(p.x+1)/2*W,sy=(1-p.y)/2*H;x0=Math.min(x0,sx);x1=Math.max(x1,sx);y0=Math.min(y0,sy);y1=Math.max(y1,sy);}
        if(beh||x1<0||x0>W||y1<0||y0>H)continue;const cw=Math.min(x1,W)-Math.max(x0,0),ch=Math.min(y1,H)-Math.max(y0,0);
        if(cw*ch>.04*W*H||cw>.35*W||ch>.35*H)out.push((g.userData.bridge||g.userData.nm||g.type)+' '+Math.round(cw)+'x'+Math.round(ch));}return out.slice(0,4);}'''
    await a.hit('#modal [data-ac=glider]'); await a.frames(2)
    for lo, la, h, alt in ((5.43, 51.89, 124, 1500), (5.47, 51.44, 0, 1000), (5.86, 51.84, 270, 2500), (5.2, 51.65, 90, 800)):
        await a.ev('([lo,la,h,alt])=>{const v=window.__vfr,[x,n]=v.proj(lo,la);Object.assign(v.PLANE,{x,n,alt,hdg:h});for(const f of v.LAYERS)v.WARNED.add(f.ident);v.NOTICE="";v.PAUSED=true;v.chase(0,true);v.hudTick()}', [lo, la, h, alt]); await a.frames(5)
        big += [f'vlieg {lo},{la}: {x}' for x in await a.ev(js)]
    await a.ev('()=>window.__vfr.setMode("map")'); await a.frames(3)
    for c in ([0, 40, 30], [0, 12, 10], [5, 4, 6], [-20, 3, 4]):
        await a.ev('(c)=>{const v=window.__vfr;v.controls.target.set(0,0,-30);v.camera.position.set(c[0],c[1],-30+c[2]);v.controls.update()}', c); await a.frames(5)
        big += [f'kaart {c}: {x}' for x in await a.ev(js)]
    ok(not big, f'3D-object te groot op het scherm (> 4% vlak of > 35% breed/hoog): {big[:5]}')

async def d_label_budget(a):  # Christian 26 nov: niet te druk. (1) overige labels ≤ 15% (kaart) / 10% (vlieg) van het scherm; (2) nooit twee labels over elkaar (labels werden verborgen gemeten → 80×16)
    js = '''(fly)=>{const v=window.__vfr,W=innerWidth,H=innerHeight,R=[];let ne=0;for(const L of v.labels){if(L.el.style.display!=='block')continue;const r=L.el.getBoundingClientRect();if(r.right<0||r.left>W||r.bottom<0||r.top>H)continue;R.push([r,L.el.textContent.slice(0,16)]);if(!(L.isAir||L.isGoal||L.isPin))ne+=r.width*r.height;}
      const ov=[];for(let i=0;i<R.length;i++)for(let j=i+1;j<R.length;j++){const [a,x]=R[i],[b,y]=R[j],w=Math.min(a.right,b.right)-Math.max(a.left,b.left),h=Math.min(a.bottom,b.bottom)-Math.max(a.top,b.top);if(w>4&&h>4)ov.push(x+' / '+y);}
      return {ne:ne/W/H,ov:ov.slice(0,3)};}'''
    bad = []
    await a.hit('#modal [data-ac=map]'); await a.frames(2); await a.wait(1500)
    for c in ([0, 40, 30], [0, 12, 10], [5, 4, 6]):
        await a.ev('(c)=>{const v=window.__vfr;v.controls.target.set(0,0,-30);v.camera.position.set(c[0],c[1],-30+c[2]);v.controls.update()}', c); await a.frames(6)
        r = await a.ev(js, False)
        if r['ne'] > .165: bad.append(f'kaart {c}: overige labels {r["ne"]:.0%} van het scherm')
        bad += [f'kaart {c}: overlap {o}' for o in r['ov']]
    await a.ev('()=>window.__vfr.setMode("fly","glider")'); await a.frames(3)
    for lo, la, h in ((5.43, 51.89, 124), (5.47, 51.44, 0), (5.2, 51.65, 90)):
        await a.ev('([lo,la,h])=>{const v=window.__vfr,[x,n]=v.proj(lo,la);Object.assign(v.PLANE,{x,n,alt:1500,hdg:h});for(const f of v.LAYERS)v.WARNED.add(f.ident);v.NOTICE="";v.PAUSED=true;v.chase(0,true);v.hudTick()}', [lo, la, h]); await a.frames(6)
        r = await a.ev(js, True)
        if r['ne'] > .11: bad.append(f'vlieg {lo},{la}: overige labels {r["ne"]:.0%}')
        bad += [f'vlieg {lo},{la}: overlap {o}' for o in r['ov']]
    ok(not bad, f'te druk of labels over elkaar: {bad[:5]}')

async def d_tap_notice(a):  # Fleur 14 nov: tik op een melding = verder (nu "lege melding onderin")
    await a.hit('#modal [data-ac=glider]'); await a.frames(3)
    st = await a.v('v.PLANE')
    for html, want in (('🔶 Over 1,0 km: <b>CTR X</b> · klaring nodig<br><small>▶ = verder</small>', True),
                       ('✅ <b>Missie geslaagd!</b><br><small>▶ = volgende opdracht</small> <button class="nt">🎯 Nieuwe opdracht</button>', 'next'),
                       ('📻 <b>RMZ X</b> · eerst oproepen<br><small>▶ = verder</small> <button data-rt="open:X">📻 Oproepen</button>', False)):
        await a.place(st['x'], st['n'], 1500, st['hdg'], paused=True)
        await a.ev('(h)=>{const v=window.__vfr;v.NOTICE=h;v.PAUSED=true;v.hudTick()}', html); await a.frames(3)
        b = await a.pg.locator('#banner .notice').first.bounding_box(); ok(b, 'melding niet zichtbaar')
        x, y = b['x'] + 12, b['y'] + 10  # op de tekst, niet op een knop
        if a.touch: await a.pg.touchscreen.tap(x, y)
        else: await a.pg.mouse.click(x, y, delay=90)
        await a.wait(400); await a.frames(3)
        p, n = await a.v('v.PAUSED'), await a.v('v.NOTICE')
        if want == 'next': ok('▶ = start' in n and await a.v('v.TASK'), f'tik op melding na een missie startte geen volgende opdracht: {n[:60]}')
        elif want: ok(not p and not n, f'tik op melding gaf geen ▶ (gepauzeerd={p}): {html[:30]}')
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
            await a.ev('()=>{const v=window.__vfr,g=v.GOAL;Object.assign(v.PLANE,{x:g.x+.5,n:g.n,alt:1000});v.FAILS.clear();v.CLR.clear();for(const f of v.LAYERS){v.CLR.add(f.ident);v.WARNED.add(f.ident);}for(const h of v.HG)v.WARNED.add("HG"+h.ident);v.NOTICE="";v.PAUSED=false;v.hudTick()}')
            n = await a.v('v.NOTICE') or ''
            if i < m['legs'] - 1: ok('Keerpunt' in n, f'{m["id"]}: keerpunt {i+1} niet gemeld: {n[:80]}')
            else: ok('geslaagd' in n and '📘' in n and '⭐' in n, f'{m["id"]}: geen geslaagd + les + ster: {n[:120]}')
        ok(m['id'] in await a.v('v.misDone()'), f'{m["id"]}: niet als gehaald opgeslagen')
    # ballon: misStart eist al een oplosbaar hoogteplan; hier nog eens expliciet
    for m in ms:
        if m['ac'] != 'balloon': continue
        plan = await a.ev('''(id)=>{const v=window.__vfr,m=v.MISSIONS.find(x=>x.id===id),st=v.misStart(m),L={};for(const f of v.TASKF)if(f.t==="L")L[f.name]=f.pts[0];
          const g=v.MPT()[m.legs[0]];const W=v.windAt;return v.balloonPlan(st.x,st.n,g,Math.hypot(g[0]-st.x,g[1]-st.n))}''', m['id'])
        ok(plan or m['id'] == 'boost', f'ballonmissie {m["id"]}: geen hoogteplan haalt het doel')
    await a.shot('missions')

async def d_tilt_rotate_real(a):  # Christian 21 nov: het draaimoment staand↔liggend; echte draai, vertraagde schermstand, trillende hand
    if not a.touch or a.form == 'p7l': return
    await a.hit('#modal [data-ac=glider]'); await tilt_on(a)
    st = await a.v('v.PLANE'); await a.place(st['x'], st['n'], 2000, 0, paused=False)
    await a.ev('()=>{const v=window.__vfr;for(const f of v.LAYERS)v.WARNED.add(f.ident);for(const g of v.HG)v.WARNED.add("HG"+g.ident)}')
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
    ok('1500 ft AMSL' in n, f'waarschuwing noemt de bovengrens uit ENR 5.5 niet: {n[:120]}')
    cyl = await a.ev('()=>{const v=window.__vfr;const c=v.hgCyl.children.find(m=>m.userData.hg==="Sterksel");if(!c)return null;const b=new v.THREE.Box3().setFromObject(c);return [b.max.y,b.max.x-b.min.x]}')
    ok(cyl, 'geen cilinder bij lierterrein Sterksel')
    exp = 1500 * 0.0003048 * await a.v('v.EXAG')
    rings = await a.ev('()=>{const v=window.__vfr;return v.hgGroup.children.filter(m=>m.userData.hgR).map(m=>{const b=new v.THREE.Box3().setFromObject(m);return [m.userData.hgR,(b.max.x-b.min.x)/2]}).filter(([r,w])=>Math.abs(r-w)>.01)}')
    ok(await a.v('v.hgGroup.children.filter(m=>m.userData.hgR).length') >= 50, 'te weinig ENR 5.5-ringen gevonden')
    ok(not rings, f'ring groter of kleiner dan de cilinder (Christian 23 nov: één cilinder met AIP-maten): {rings[:3]}')
    ok(abs(cyl[0] - exp) < 0.05 and abs(cyl[1] - 0.5) < 0.05, f'cilinder Sterksel: top {cyl[0]:.2f} (verwacht {exp:.2f}), breedte {cyl[1]:.2f} km (verwacht 0,5)')
    await a.place(h['x'] - 1.6, h['n'] - .3, 900, 80, paused=True)
    await a.ev('(h)=>{const v=window.__vfr;v.WARNED.add("HG"+h.ident);for(const f of v.LAYERS)v.WARNED.add(f.ident);for(const g of v.HG)v.WARNED.add("HG"+g.ident);v.NOTICE="";v.hudTick()}', h); await a.frames(6)
    await a.shot('winch_cylinder')
    await a.place(h['x'] - 3, h['n'], 3000, 90, paused=False)
    await a.ev('(h)=>{const v=window.__vfr;v.WARNED.delete("HG"+h.ident);Object.assign(v.PLANE,{x:h.x,n:h.n});v.hudTick()}', h)
    ok('Lierterrein' not in (await a.v('v.NOTICE') or ''), 'waarschuwing ook hoog boven het lierterrein (3000 ft)')
    await a.ev('()=>window.__vfr.setMode("map")'); await a.frames(2)
    await a.ev('(h)=>{const v=window.__vfr;v.PROBE.x=h.x;v.PROBE.n=h.n;v.showProbe()}', h); await a.frames(2)
    ok('Lierterrein Sterksel' in await a.pg.inner_text('#info'), 'sonde noemt het lierterrein niet')

FLY_STEP = '''(noClr)=>{const v=window.__vfr,g=v.GOAL;if(!g)return {end:v.NOTICE||''};
  if(v.ACTYPE==='balloon'){const gk=g.name+g.li;if(window.__wpk!==gk){window.__wpk=gk;const d=Math.hypot(g.x-v.PLANE.x,g.n-v.PLANE.n);window.__bp={pl:v.balloonPlan(v.PLANE.x,v.PLANE.n,[g.x,g.n],d,v.PLANE.alt),d,s:0};window.__alts=new Set();}
    const B=window.__bp;if(!B.pl)return {n:'GEEN HOOGTEPLAN',p:false,fails:['geen hoogteplan'],alt:v.PLANE.alt};
    if(!v.PAUSED){const [a1,a2,fr]=B.pl,t=B.s<B.d*fr?a1:a2,w=v.windAt(v.PLANE.alt),rate=v.AC.balloon.fpm/Math.max(1,w.kt*1.852/60);v.PLANE.alt+=Math.sign(t-v.PLANE.alt)*Math.min(Math.abs(t-v.PLANE.alt),rate*.2);
      [v.PLANE.x,v.PLANE.n]=v.driftStep(v.PLANE.x,v.PLANE.n,v.PLANE.alt,.2);B.s+=.2;window.__alts.add(t);}
    v.hudTick();return {n:v.NOTICE||'',p:v.PAUSED,open:null,fails:[...v.FAILS.values()],alt:v.PLANE.alt};}
  const gk=g.name+g.li;if(window.__wpk!==gk){window.__wpk=gk;const from=[v.PLANE.x,v.PLANE.n],to=[g.x,g.n],o={ac:v.ACTYPE};
    let r=noClr?v.planRoute(from,to,v.PLANE.alt,{...o,noClr:true}):null;window.__needClr=window.__needClr||(noClr&&!r);if(!r)r=v.planRoute(from,to,v.PLANE.alt,o);
    window.__wp=r?r.slice(1):[{x:g.x,n:g.n,alt:v.PLANE.alt}];window.__alts=new Set([...(window.__alts||[]),...(r?r.alts:[])]);}
  const wp=window.__wp;while(wp.length>1&&Math.hypot(wp[0].x-v.PLANE.x,wp[0].n-v.PLANE.n)<.12&&Math.abs(wp[0].alt-v.PLANE.alt)<1)wp.shift();const t=wp[0]||{x:g.x,n:g.n,alt:v.PLANE.alt};
  if(!v.PAUSED){if(Math.abs(t.alt-v.PLANE.alt)>=1&&Math.hypot(t.x-v.PLANE.x,t.n-v.PLANE.n)<.12){v.PLANE.alt+=Math.sign(t.alt-v.PLANE.alt)*Math.min(50,Math.abs(t.alt-v.PLANE.alt));}// cirkelend stijgen/dalen
    else{const d=Math.hypot(t.x-v.PLANE.x,t.n-v.PLANE.n)||1e-9,s=Math.min(.1,d);v.PLANE.hdg=(Math.atan2(t.x-v.PLANE.x,t.n-v.PLANE.n)*180/Math.PI+360)%360;v.PLANE.x+=(t.x-v.PLANE.x)/d*s;v.PLANE.n+=(t.n-v.PLANE.n)/d*s;}}
  v.hudTick();const b=document.getElementById("banner"),o=b.querySelector("[data-rt^=open]");
  return {n:v.NOTICE||'',p:v.PAUSED,open:o&&o.dataset.rt,fails:[...v.FAILS.values()],alt:v.PLANE.alt}}'''

async def fly_mission(a, mid, mode, stats=None, done=None):  # één missie écht uitvliegen met de 3D-routeplanner, alleen knoppen die de app laat zien
    # mode 'around': route zónder klaring (omvliegen/stijgen/dalen) waar die bestaat; 'refuse'/'dismiss': met klaring, eerst geweigerd / eerste melding weggetikt
    await a.ev('([id,done])=>{const v=window.__vfr;localStorage.setItem("l3d_missies",JSON.stringify(done||v.MISSIONS.filter(x=>x.ac===v.ACTYPE&&x.id!==id).map(x=>x.id)));v.newTask();window.__wpk=null;window.__needClr=false;window.__alts=null}', [mid, done])
    await a.frames(2)
    ok((await a.v('v.MISSION||{}')).get('id') == mid, f'{mid}: missie niet gekozen')
    refused, log, warns, opens = 0, [], [], set()
    for step in range(3000):
        r = await a.ev(FLY_STEP, mode == 'around')
        if 'end' not in r and ('Missie geslaagd' in r['n'] or 'Missie mislukt' in r['n']): r['end'] = r['n']
        if 'end' in r:
            ok('geslaagd' in r['end'], f'{mid} ({mode}): {r["end"][:160]} · {log[-4:]}')
            ok('⭐⭐⭐' in r['end'] and '🎓' in r['end'], f'{mid} ({mode}): goed gevlogen maar geen 3 sterren + leerdoel: {r["end"][:220]}')
            if stats is not None: stats.update(warns=len(warns), opens=sorted(opens), flown=round(await a.v('v.MDIST'), 1), ref=round(await a.v('v.MREF'), 1), needclr=await a.ev('()=>window.__needClr'), alts=sorted(await a.ev('()=>[...(window.__alts||[])]')))
            return True
        if r['fails']: ok(False, f'{mid} ({mode}): overtreding {r["fails"]} · {log[-4:]}')
        if r['p'] and r['n'] and 'Keerpunt' not in r['n'] and r['n'][:40] not in [w[:40] for w in warns[-1:]]: warns.append(r['n'])
        if r['open'] and mode == 'around' and not await a.ev('()=>window.__needClr'): r['open'] = None  # route zonder klaring: knop negeren
        if r['open'] and not (mode == 'dismiss' and refused == 0 and r['p']):
            log.append(r['open']); opens.add(r['open'].split(':')[1])
            if mode == 'refuse' and refused == 0:  # eerste aanvraag: de verkeersleiding weigert
                await a.ev('(id)=>window.__vfr.RTOUT.set(id,{t:performance.now(),o:"traffic"})', r['open'].split(':')[1])
            else:  # verder vast: klaring (geen toeval in de test)
                await a.ev('(id)=>{const R=window.__vfr.RTOUT;if(!R.has(id))R.set(id,{t:performance.now(),o:"yes"})}', r['open'].split(':')[1])
            if not await a.ev('k=>{const e=document.querySelector(`#banner [data-rt="${k}"]`);if(e)e.click();return !!e}', r['open']): continue  # balk net herbouwd: volgende stap opnieuw
            for _ in range(4):
                ks = await a.ev('()=>[...document.querySelectorAll("#banner [data-rt^=pick],#banner [data-rt^=rb]")].map(e=>e.dataset.rt)')
                if not ks: break
                for k in ks:
                    await a.ev('k=>{const e=document.querySelector(`#banner [data-rt="${k}"]`);if(e)e.click()}', k)
                    if '❌' not in (await a.v('v.NOTICE') or ''): break
            n = await a.v('v.NOTICE') or ''
            if 'Geweigerd' in n:
                refused += 1; log.append('geweigerd')
                ok(refused < 3, f'{mid}: blijft geweigerd')
                await a.ev('()=>{const v=window.__vfr;for(const c of v.RTOUT.values())c.t-=60000}')  # een minuut later
            await a.ev('()=>{const v=window.__vfr;v.NOTICE="";v.PAUSED=false}')
        elif r['p']:
            if mode == 'dismiss' and r['open']: refused = 1; log.append('▶ zonder aanvraag')
            await a.ev('()=>{const v=window.__vfr;v.NOTICE="";v.PAUSED=false}')
    ok(False, f'{mid} ({mode}): doel niet bereikt · {log[-4:]}')

async def d_missions_flown(a):  # Christian 24 nov: Evoluon-missie onmogelijk (geen klaring Eindhoven CTR). Elke missie echt uitvliegen,
    # ook na een geweigerde klaring en na een weggetikte eerste melding; d_missions gaf zichzelf klaring voor alles en miste dit.
    await a.hit('#modal [data-ac=motor]'); await a.frames(3)
    flown = []
    for ac in ('motor', 'glider', 'balloon'):
        if (await a.v('v.ACTYPE')) != ac: await a.ev('(ac)=>window.__vfr.setMode("fly",ac)', ac); await a.frames(2)
        for mid in await a.ev('(ac)=>window.__vfr.MISSIONS.filter(m=>m.ac===ac).map(m=>m.id)', ac):
            for mode in (('around',) if ac == 'balloon' else ('around', 'refuse', 'dismiss')):
                await a.ev('()=>window.__vfr.RTOUT.clear()')
                if await fly_mission(a, mid, mode): flown.append(mid)
    allm = await a.ev('()=>window.__vfr.MISSIONS.map(m=>m.id)')
    ok(set(allm) <= set(flown), f'niet elke missie uitgevlogen: {sorted(set(allm) - set(flown))}')
    # opdracht B: elke missie een niveau en één leerdoel; per toestel loopt de reeks op en begint makkelijk
    for ac in ('glider', 'motor', 'balloon'):
        ser = await a.ev('(ac)=>window.__vfr.misSeries(ac).map(m=>[m.id,m.lvl,m.goal||""])', ac)
        ok(all(l in (1, 2, 3) and len(g) > 10 for _, l, g in ser), f'{ac}: missie zonder niveau of leerdoel: {ser}')
        ok(ser[0][1] == 1 and [l for _, l, _ in ser] == sorted(l for _, l, _ in ser), f'{ac}: reeks loopt niet op van makkelijk naar pittig: {ser}')
    ok(len(await a.v('Object.keys(v.misStars())')) >= 3, 'sterren niet opgeslagen')

async def d_labels_steady(a):  # Christian 24 nov: label Deelen CTR knippert in kaartmodus (mobiel). Klasse: geen enkel label mag
    # aan/uit springen terwijl de camera stilstaat. Langzaam uitzoomen (zoals knijpen) en na elke stap stilhouden.
    if await a.visible('#modal [data-ac=glider]'): await a.ev('()=>window.__vfr.setMode("map")'); await a.frames(3)
    await a.ev('()=>{const v=window.__vfr;v.oneMenu&&v.oneMenu(null);document.body.classList.remove("welcome")}')
    bad = []
    for ident in ('EHDL', 'EHEH', 'EHVK'):
        await a.ev('(id)=>{const v=window.__vfr,f=v.LAYERS.find(g=>g.ident===id);const [x,n]=f.lp;v.controls.target.set(x,0,-n);v.camera.position.set(x,6,-n+6);v.controls.update()}', ident)
        await a.frames(3)
        for step in range(40):  # stapjes van 4 %: zo landt een label vroeg of laat in de hysterese-band
            await a.ev('()=>{const v=window.__vfr,t=v.controls.target,p=v.camera.position;p.sub(t).multiplyScalar(1.04).add(t);v.controls.update()}')
            seq = await a.ev('''n=>new Promise(r=>{const v=window.__vfr,L=v.labels,h=L.map(()=>"");let k=0;for(const l of L){l.prev=Math.random()<.5;l.show=Math.random()<.5;}/* elke voorgeschiedenis */const f=()=>{L.forEach((l,i)=>h[i]+=l.show?1:0);if(++k>=n)r(L.map((l,i)=>[l.el.textContent.slice(0,30),h[i].slice(3)]).filter(([_,s])=>/01|10/.test(s)));else requestAnimationFrame(f)};requestAnimationFrame(f)})''', 14)
            for nm, s in seq: bad.append(f'{ident} stap {step}: {nm} {s}')
            if len(bad) > 3: break
    ok(not bad, f'labels knipperen bij stilstaande camera: {bad[:3]}')

async def d_h24_always(a):  # Christian 23 nov: "Vught 's avonds onzichtbaar". ENR 5.1 (AIRAC 11-2026): EHP29 GND–1500 ft AMSL, H24.
    # Klasse: elk P-gebied (allemaal H24 in ENR 5.1) is op elk tijdstip, werkdag en weekend, actief en zichtbaar.
    bad = await a.ev('''()=>new Promise(async res=>{const v=window.__vfr,out=[],d=document.getElementById("tDay"),sl=document.getElementById("tSlide");
      const fr=()=>new Promise(r=>requestAnimationFrame(()=>requestAnimationFrame(r)));
      for(const dow of [2,6])for(let h=0;h<24;h+=.5){d.value=dow;d.dispatchEvent(new Event("change"));sl.value=h*4;sl.dispatchEvent(new Event("input"));sl.dispatchEvent(new Event("change"));await fr();
        for(const f of v.LAYERS.filter(g=>g.layer==="P"))if(f.active===false||!v.vis[f.group.id]||!f.meshes.some(m=>m.visible&&m.material.opacity>.05))out.push(f.ident+" "+dow+" "+h+"u");}
      res(out)})''')
    ok(await a.v('v.LAYERS.some(f=>f.ident==="EHP29")'), 'EHP29 Vught ontbreekt')
    ok(not bad, f'P-gebied niet zichtbaar: {bad[:4]}')

async def d_no_circuit(a):  # Christian 23 nov: voorbeeldcircuit en missie "Land op Eindhoven" definitief geschrapt (BACKLOG "niet doen")
    r = await a.ev('()=>({opt:!!document.getElementById("optCirc"),txt:/voorbeeldcircuit|Land op Eindhoven/i.test(document.documentElement.innerHTML),fn:typeof window.missionEHEH})')
    ok(not r['opt'] and not r['txt'] and r['fn'] == 'undefined', f'voorbeeldcircuit nog in de app: {r}')

async def d_shared_sites(a):  # Christian 23 nov (A3): Malden zweef + model overlappen; nooit tegelijk → één melding, niet als twee volle volumes
    await a.hit('#modal [data-ac=glider]'); await a.frames(2)
    sh = await a.ev('()=>window.__vfr.HG.filter(h=>h.shared.length).map(h=>h.ident)')
    ok('EHAAGLD020' in sh and 'EHAAUAV047' in sh, f'Malden niet als gedeeld terrein herkend: {sh}')
    op = await a.ev('()=>Object.fromEntries(window.__vfr.hgCyl.children.filter(c=>c.userData.hg==="Malden").map(c=>[c.userData.typ,c.material.opacity]))')
    ok(op.get('uas', 1) < op.get('gld', 0) / 2, f'modelvliegvolume Malden nog als vol volume: {op}')
    g = await a.ev('()=>{const h=window.__vfr.HG.find(h=>h.ident==="EHAAGLD020");return [h.x,h.n]}')
    await a.place(g[0] - 3, g[1], 900, 90)
    notes = []
    for _ in range(80):
        n = await a.ev('()=>{const v=window.__vfr;if(!v.PAUSED)v.PLANE.x+=.1;v.hudTick();const n=v.NOTICE||"";if(v.PAUSED){v.NOTICE="";v.PAUSED=false}return n}')
        if n and 'Malden' in n: notes.append(n)
    ok(len(notes) == 1, f'{len(notes)} meldingen bij Malden, verwacht 1: {[x[:60] for x in notes]}')
    ok('Modelvlieg' in notes[0] and 'Zweefvlieg' in notes[0] and 'nooit tegelijk' in notes[0] and 'nog te verifiëren' in notes[0], f'melding Malden onvolledig: {notes[0][:200]}')

async def d_generator(a):  # besluit 23 nov + Christian 25 nov: na 6 vaste missies per toestel oneindig nieuwe, oplopend moeilijk, en altijd 100% haalbaar
    await a.hit('#modal [data-ac=glider]'); await a.frames(2)
    for ac in ('glider', 'motor', 'balloon'):
        ok(await a.ev('(ac)=>window.__vfr.misSeries(ac).length', ac) == 6, f'{ac}: geen 6 vaste missies')
        g = await a.ev('(ac)=>[1,2,3,4,5,6,7,8].map(L=>{const m=window.__vfr.genMission(ac,L);return m&&{id:m.id,legs:m.legs.length,lvl:m.lvl}})', ac)
        ok(all(g), f'{ac}: generator gaf geen missie voor niveau {[i + 1 for i, x in enumerate(g) if not x]}')
        ok(g[0]['legs'] <= g[-1]['legs'] and g[0]['lvl'] <= g[-1]['lvl'], f'{ac}: niet oplopend: {g}')
        fixed = await a.ev('(ac)=>window.__vfr.misSeries(ac).map(m=>m.id)', ac)
        bad = await a.ev('(ac)=>window.__vfr.misSeries(ac).filter(m=>!window.__vfr.misVerify(m,window.__vfr.misStart(m))).map(m=>m.id)', ac)
        ok(not bad, f'{ac}: vaste missie haalt de eigen vlucht-check niet: {bad}')
        if (await a.v('v.ACTYPE')) != ac: await a.ev('(ac)=>window.__vfr.setMode("fly",ac)', ac); await a.frames(2)
        for L in (1, 4, 8):  # steekproef echt uitvliegen, zonder klaring
            st = {}
            await fly_mission(a, f'gen-{ac}-{L}', 'around', st, done=fixed + [f'gen-{ac}-{k}' for k in range(1, L)])
            ok(not st.get('needclr') and not st.get('opens'), f'gen-{ac}-{L}: had klaring nodig: {st}')
    # AIRAC-vangnet: wordt een doel onbereikbaar (hier: doel ín P-gebied Vught), dan biedt de app de missie niet aan maar slaat hem over
    r = await a.ev('''()=>{const v=window.__vfr;v.setMode("fly","glider");const p=v.LAYERS.find(f=>f.ident==="EHP29"),hi0=p.hi;p.hi=1e6;/* 'nieuwe AIRAC': P-gebied zonder bovengrens */v.MPT_EXTRA["Testdoel P"]=p.lp;v.MIS_OK.delete("airac-test");const m={id:'airac-test',ac:'glider',lvl:1,goal:'test',title:'Test',legs:['Testdoel P'],les:null,alt:1000,brief:'x'};
      v.MISSIONS.unshift(m);localStorage.setItem("l3d_missies","[]");v.newTask();const got=v.MISSION&&v.MISSION.id;const ver=v.misVerify(m,v.misStart(m)||{x:0,n:0,alt:1000});v.MISSIONS.shift();p.hi=hi0;v.MIS_OK.clear();return [got,ver]}''')
    ok(r[0] != 'airac-test' and r[1] is False, f'onhaalbare missie toch aangeboden: {r}')

async def d_no_freeze(a):  # 25 nov: generator/vlucht-check blokkeerden de pagina seconden lang → knijpen en tijdknoppen faalden. Klasse: geen lange blokkade
    await a.hit('#modal [data-ac=glider]'); await a.frames(3)
    ms = await a.ev('()=>{const v=window.__vfr;v.MIS_OK.clear();localStorage.setItem("l3d_missies","[]");const t=performance.now();v.newTask();return performance.now()-t}')
    ok(ms < 600, f'missiestart (vaste missie) duurt {ms:.0f} ms')
    r = await a.ev('''()=>new Promise(res=>{const v=window.__vfr;v.GEN.clear();localStorage.setItem("l3d_missies",JSON.stringify(v.misSeries("glider").map(m=>m.id)));
      const t0=performance.now();v.newTask();const wait=v.NOTICE;let last=performance.now(),gap=0;
      const f=()=>{const n=performance.now();gap=Math.max(gap,n-last);last=n;const m=v.MISSION;if(m&&m.gen||n-t0>90000)return res({gap,wait,id:m&&m.id,ms:n-t0});requestAnimationFrame(f)};requestAnimationFrame(f)})''')
    ok('wordt gemaakt' in r['wait'], f'geen wachtmelding tijdens het maken: {r["wait"][:80]}')
    ok(r['id'] == 'gen-glider-1', f'uitdaging start niet vanzelf: {r}')
    ok(r['gap'] < 700, f'pagina zat {r["gap"]:.0f} ms vast tijdens het maken van een uitdaging (max 700)')

async def d_start_smooth(a):  # 27 nov: stotter bij ▶ (A55: 2834 ms stil). Headless ziet geen GPU-pipelines, wél de klasse 'main thread seconden vast na ▶' (synchrone missieberekening, layout-storm)
    await a.ev("()=>{window.__LT=[];new PerformanceObserver(l=>{for(const e of l.getEntries())window.__LT.push(Math.round(e.duration))}).observe({type:'longtask'})}")
    for ac in ('glider', 'motor', 'balloon'):
        await a.fly(ac); await a.wait(1200)
        ok(await a.v('v.PAUSED'), f'{ac}: geen startmelding')
        ok('▶ = start' in (await a.v('v.NOTICE') or ''), f'{ac}: startmelding zonder ▶ = start')
        await a.ev('()=>{window.__LT.length=0}'); await a.hit('#btnPause'); await a.wait(3000)
        mx = await a.ev('()=>Math.max(0,...window.__LT)')
        n = await a.v('v.NOTICE') or ''
        ok('▶ = start' not in n, f'{ac}: ▶ startte de vlucht niet: {n[:90]}')  # daarna mag een naderingsmelding (motor bij Volkel) weer pauzeren
        ok(mx < 500, f'{ac}: na ▶ zat de pagina {mx} ms vast (max 500)')

async def d_tiles(a):  # 28 nov heel NL: landschap per tegel. Laadt in de buurt, verbergt ver weg, bouwt zonder lange blokkade, geen dubbel landschap in de regio
    await a.hit('#modal [data-ac=map]'); await a.frames(2)
    go = """async([lo,la])=>{const v=window.__vfr,[x,n]=v.proj(lo,la);v.controls.target.set(x,0,-n);v.camera.position.set(x,30,-n+25);v.controls.update();
      for(let i=0;i<120;i++){await new Promise(r=>setTimeout(r,100));const s=Object.values(v.TILE_ST);if(s.length&&s.every(t=>t.state!=='loading'))break;}
      return Object.fromEntries(Object.entries(v.TILE_ST).map(([k,t])=>[k,{state:t.state,on:t.on,max:t.max||0,vis:!!(t.group&&t.group.visible)}]))}"""
    r = await a.ev(go, [6.56, 53.22])  # Groningen
    ok('nl-43' in r and r['nl-43']['state'] == 'ready' and r['nl-43']['vis'], f'tegel Groningen (nl-43) niet geladen/zichtbaar: {r.get("nl-43")}')
    ok(all(t['max'] < 120 for t in r.values()), f'tegel bouwen blokkeerde te lang (max per plakje 120 ms headless): {[(k, t["max"]) for k, t in r.items() if t["max"] >= 120]}')
    lab = await a.v("v.labels.filter(L=>L.tile==='nl-43').length")
    ok(lab > 0, 'tegel Groningen zonder labels (plaatsen/wegen)')
    r = await a.ev(go, [4.9, 51.3])  # zuidwesten: Groningen ver weg
    ok(not r['nl-43']['on'] and not r['nl-43']['vis'], f'tegel Groningen niet verborgen op 250 km: {r["nl-43"]}')
    shown = await a.v("v.labels.filter(L=>L.tile==='nl-43'&&L.show).length")
    ok(shown == 0, f'{shown} labels van een verborgen tegel nog getoond')
    dup = await a.ev("""()=>{const v=window.__vfr,R={x0:4.75,y0:51.2,x1:6.15,y1:52.15},[a0,b0]=v.proj(R.x0,R.y0),[a1,b1]=v.proj(R.x1,R.y1);
      return v.labels.filter(L=>L.tile&&L.el.textContent.startsWith('●')).map(L=>{const p=L.pos3();return [L.el.textContent,p.x,-p.z]}).filter(([t,x,n])=>x>a0+1&&x<a1-1&&n>b0+1&&n<b1-1).map(q=>q[0]).slice(0,5)}""")
    ok(not dup, f'tegel tekent steden binnen de ingebakken regio (dubbel): {dup}')

async def d_menu_on_top(a):  # 25 nov: missiemelding lag óver het tijdmenu (weekend niet aan te tikken). Klasse: open menu = bovenop, overal
    await a.hit('#modal [data-ac=glider]'); await a.frames(2)
    for btn, pop in (('#timeBtn', '#timePop'), ('#btnPanel', '#panel')):
        if not await a.visible(btn): continue
        await a.hit(btn); await a.frames(2)
        hid = await a.ev("""(pop)=>{const P=document.querySelector(pop);if(!P||P.classList.contains('hidden'))return 'dicht';const bad=[];
          for(const e of P.querySelectorAll('button,input,select,label')){const r=e.getBoundingClientRect();const R=P.getBoundingClientRect(),cy=r.y+r.height/2,cx=r.x+r.width/2;if(r.width<4||r.height<4||r.bottom<0||r.top>innerHeight||cy<R.top||cy>R.bottom||cx<R.left||cx>R.right)continue;/* buiten het zichtbare (scroll)deel van het menu */
            const t=document.elementFromPoint(Math.min(innerWidth-1,r.x+r.width/2),Math.min(innerHeight-1,r.y+r.height/2));if(t&&!P.contains(t))bad.push((e.textContent||e.id||e.tagName).trim().slice(0,20)+' onder '+(t.id||t.className||t.tagName))}return bad}""", pop)
        ok(hid == 'dicht' or not hid, f'{pop}: bedekt door iets anders: {hid[:3] if hid != "dicht" else hid}')
        await a.hit(btn); await a.frames(2)

async def d_ctr_covers_rmz(a):  # Christian 21 nov: "missie mislukt, RMZ Deelen zonder oproep" terwijl hij klaring had voor Deelen CTR
    await a.hit('#modal [data-ac=motor]'); await a.frames(2)
    xy = await a.ev('()=>{const v=window.__vfr;return v.proj(5.8719,52.0597)}')
    await a.place(xy[0], xy[1], 1000, 0, paused=False)
    ids = await a.ev('()=>{const v=window.__vfr;return v.INSIDE.map(f=>f.ident+":"+(f.active!==false))}')
    ok('EHDL:true' in ids and 'EHDLRMZ:true' in ids, f'testpunt niet in actieve Deelen CTR + RMZ: {ids}')
    await a.ev('()=>{const v=window.__vfr;v.CLR.add("EHDL");v.GOAL={x:v.PLANE.x+30,n:v.PLANE.n,name:"Test"};v.hudTick();v.hudTick()}')
    f = await a.ev('()=>[...window.__vfr.FAILS.keys()]')
    ok('EHDLRMZ' not in f, f'RMZ telt als fout ondanks klaring Deelen Tower: {f}')
    t = await a.ev('()=>document.getElementById("banner").innerText')
    ok('Oproepen' not in t and 'OPROEPEN' not in t, f'banner vraagt nog om oproepen: {t[:100]!r}')
    await a.ev('()=>{const v=window.__vfr;v.CLR.clear();v.hudTick()}')
    f = await a.ev('()=>[...window.__vfr.FAILS.keys()]')
    ok('EHDLRMZ' in f, f'zonder klaring of oproep hoort RMZ Deelen een fout te zijn: {f}')

async def d_tilt_notice_bend(a):  # Christian 25 nov: melding midden in een bocht → ▶ → kantelen opnieuw geijkt, bocht niet voort te zetten.
    # Regel (Christian): ijken alleen bij de start en na draaien staand↔liggend; nooit door een melding, resize of pauze. Realistische ruis ±5°.
    if not a.touch: return
    await a.hit('#modal [data-ac=glider]'); await tilt_on(a)
    st = await a.v('v.PLANE'); await a.place(st['x'], st['n'], 2500, 0, paused=True)
    await a.ev('()=>{const v=window.__vfr;for(const f of v.LAYERS)v.WARNED.add(f.ident);for(const h of v.HG)v.WARNED.add("HG"+h.ident)}')
    rng = random.Random(2511); ang0 = await a.v('v.tiltAng()')
    import time as _t
    async def hold(turn, back, ms, jit=5):
        t0 = _t.time()
        while _t.time() - t0 < ms / 1000:
            await a.ev(SEND, orient(turn + rng.uniform(-jit, jit), back + rng.uniform(-jit, jit), ang0, 60)); await a.wait(35)
    await a.ev('()=>window.__vfr.resetTilt()'); await hold(0, 0, 500); await a.hit('#btnPause'); await hold(0, 0, 1500, jit=2)
    ok(not await a.v('v.PAUSED'), 'start: ▶ hervat niet')
    for cause in ('melding', 'resize', 'pauze'):
        await hold(25, 0, 900); ok(await a.v('v.TAX.r') > .2, f'{cause}: bocht naar rechts komt niet op gang')
        if cause == 'melding':
            await a.ev('()=>{const v=window.__vfr;v.NOTICE="🔶 Over 1,0 km: <b>CTR X</b> · klaring nodig<br><small>▶ = verder</small>";v.PAUSED=true;v.hudTick()}')
            await hold(25, 0, 500); await a.hit('#btnPause')
        elif cause == 'resize':
            vw = a.pg.viewport_size; await a.pg.set_viewport_size({'width': vw['width'], 'height': vw['height'] - 56}); await hold(25, 0, 400)
            await a.pg.set_viewport_size(vw)
        else:
            await a.hit('#btnPause'); await hold(25, 0, 500); await a.hit('#btnPause')
        ok(not await a.v('v.PAUSED'), f'{cause}: ▶ hervat niet')
        h0 = await a.v('v.PLANE.hdg'); await hold(25, 0, 1500)
        dh = (((await a.v('v.PLANE.hdg')) - h0 + 540) % 360 - 180)
        ok(dh > 8 and await a.v('v.TAX.r') > .2, f'{cause}: na ▶ midden in de bocht gaat de bocht niet verder (Δkoers {dh:.0f}°, TAX.r {await a.v("v.TAX.r")})')
        await hold(0, 0, 900); ok(abs(await a.v('v.TAX.r')) < .01, f'{cause}: rechtop houden = niet meer rechtuit (nulstand verschoven)')
    # Christian 26 nov: hetzelfde voor stijgen en dalen (telefoon naar je toe/van je af) midden in een klim of daling
    for back, what in ((22, 'klim'), (-22, 'daling')):
        for cause in ('melding', 'pauze'):
            await hold(0, back, 900); p0 = await a.v('v.TAX.p'); ok(abs(p0) > .2, f'{what}/{cause}: {what} komt niet op gang (TAX.p {p0})')
            if cause == 'melding':
                await a.ev('()=>{const v=window.__vfr;v.NOTICE="🔶 Over 1,0 km: <b>CTR X</b> · klaring nodig<br><small>▶ = verder</small>";v.PAUSED=true;v.hudTick()}')
            else: await a.hit('#btnPause')
            await hold(0, back, 500); await a.hit('#btnPause'); await hold(0, back, 1200)
            p1 = await a.v('v.TAX.p'); ok(abs(p1) > .2 and (p1 > 0) == (p0 > 0), f'{what}/{cause}: na ▶ midden in de {what} gaat die niet door (TAX.p {p0} → {p1})')
            await hold(0, 0, 900); ok(abs(await a.v('v.TAX.p')) < .01, f'{what}/{cause}: telefoon terug in de starthouding = niet meer horizontaal (nulstand verschoven)')
    await a.sane()

async def d_tilt_pause_edges(a):  # Christian 21 nov: "na een missie of pauzeren/onpauzeren gaat het kantelen nu en dan de mist in"
    if not a.touch: return
    await a.hit('#modal [data-ac=glider]'); await tilt_on(a)
    st = await a.v('v.PLANE'); await a.place(st['x'], st['n'], 2500, 0, paused=False)
    await a.ev('()=>{const v=window.__vfr;for(const f of v.LAYERS)v.WARNED.add(f.ident);for(const g of v.HG)v.WARNED.add("HG"+g.ident);for(const h of v.HG)v.WARNED.add("HG"+h.ident)}')
    rng = random.Random(int(os.environ.get('TILT_SEED', '2111')))
    import time as _t
    ang0 = await a.v('v.tiltAng()')
    async def hold(turn, back, ms, ang=None, jit=4, p0=60):
        t0 = _t.time()
        while _t.time() - t0 < ms / 1000:
            await a.ev(SEND, orient(turn + rng.uniform(-jit, jit), back + rng.uniform(-jit, jit), ang0 if ang is None else ang, p0)); await a.wait(35)
    async def jolt(turn, back, ang=None, p0=60):  # de tik op ▶ schudt de telefoon
        for _ in range(4):
            await a.ev(SEND, orient(turn + rng.uniform(-14, 14), back + rng.uniform(-14, 14), ang0 if ang is None else ang, p0)); await a.wait(20)
    async def resume_check(label, turn, back, ang=None, p0=60, start=True):
        # start=True: nieuwe opdracht → ▶ ijkt op de houding van nu. start=False (Christian 25 nov): pauze midden in de vlucht
        # ijkt níet opnieuw; de oude nulstand (turn, back) blijft gelden, ook als je tijdens de pauze anders vasthoudt
        if start:
            await a.ev('()=>{const v=window.__vfr;v.newTask();for(const f of v.LAYERS)v.WARNED.add(f.ident);for(const h of v.HG)v.WARNED.add("HG"+h.ident);v.PLANE.alt=Math.max(v.PLANE.alt,2500)}')
            ok(await a.v('v.PAUSED') and '▶ = start' in await a.v('v.NOTICE'), f'{label}: nieuwe opdracht start niet in pauze')
        else:
            await a.hit('#btnPause'); ok(await a.v('v.PAUSED'), f'{label}: pauze gaat niet aan')
        await hold(rng.uniform(-30, 30), -35, 600, ang, jit=8, p0=p0)
        await hold(turn, back, 400, ang, p0=p0)
        await a.hit('#btnPause'); await jolt(turn, back, ang, p0)
        ok(not await a.v('v.PAUSED'), f'{label}: ▶ hervat niet')
        h0 = await a.v('v.PLANE.hdg'); al0 = await a.v('v.PLANE.alt')
        await hold(turn, back, 2200, ang, p0=p0)
        dh = abs(((await a.v('v.PLANE.hdg')) - h0 + 540) % 360 - 180)
        ok(dh < 6, f'{label}: na ▶ een bocht van {dh:.0f}° terwijl je de telefoon stil houdt')
        ok(await a.v('v.TAX.r') == 0 and await a.v('v.TAX.p') == 0, f'{label}: stuurt nog na ▶ in rust: {await a.v("[v.TAX.r,v.TAX.p]")}')
        await hold(turn + 22, back, 300, ang, jit=2, p0=p0); ok(await a.v('v.TAX.r') > .2, f'{label}: rechts kantelen werkt niet na ▶')
        await hold(turn, back, 300, ang, jit=2, p0=p0)
    await a.ev('()=>window.__vfr.resetTilt()'); await hold(0, 0, 500)
    await resume_check('scheef (20°) vastgehouden', 20, 10)
    await resume_check('erg scheef (32°)', -32, -5)
    await resume_check('rechtop', 0, 0)
    await resume_check('pauze midden in de vlucht', 0, 0, start=False)  # nulstand blijft (0,0)
    await resume_check('na nieuwe opdracht', 12, 5)
    await resume_check('pauze na scheef ijken', 12, 5, start=False)
    # hele onrustige hand (±15°) bij de start: melding "houd even stil", geen bocht; stil houden → melding weg en bestuurbaar
    await a.ev('()=>{const v=window.__vfr;v.newTask();for(const f of v.LAYERS)v.WARNED.add(f.ident);for(const h of v.HG)v.WARNED.add("HG"+h.ident);v.PLANE.alt=Math.max(v.PLANE.alt,2500)}')
    await hold(0, 0, 400); await a.hit('#btnPause')
    h0 = await a.v('v.PLANE.hdg'); await hold(0, 0, 1700, jit=15)
    ok(await a.visible('#stillHint'), 'onrustige hand: geen melding "houd de telefoon even stil"')
    await a.shot('still_hint')
    ok(await a.v('v.TAX.r') == 0, 'onrustige hand: stuurt al vóór het ijken')
    dh = abs(((await a.v('v.PLANE.hdg')) - h0 + 540) % 360 - 180); ok(dh < 6, f'onrustige hand: bocht van {dh:.0f}°')
    await hold(0, 0, 700, jit=3)
    ok(not await a.visible('#stillHint'), 'melding "houd stil" blijft staan na stil houden')
    await hold(22, 0, 300, jit=2); ok(await a.v('v.TAX.r') > .2, 'na onrustige hand niet bestuurbaar')
    await hold(0, 0, 300, jit=2)
    # schermstand vergrendeld, telefoon liggend vastgehouden
    if a.form != 'p7l':
        for k in range(1, 16):
            await a.ev(SEND, orient(90 * k / 15, 0, 0, 60)); await a.wait(33)
        await hold(0, 0, 3200, ang=90)
        ok(await a.v('v.TAX.r') == 0, 'vergrendeld: stuurt na ijken')
        await resume_check('vergrendeld liggend', 8, 5, ang=90)
        await resume_check('vergrendeld liggend, pauze', 8, 5, ang=90, start=False)
    await a.sane()

async def d_enr55_sites(a):  # 21 nov: alle ENR 5.5-terreinen (lier, lierstart zweefvliegen, modelvliegen, ULV) als cilinder met AIP-bovengrens
    await a.hit('#modal [data-ac=motor]'); await a.frames(2)
    hg = await a.v('v.HG'); typs = {h['typ'] for h in hg}
    ok(typs == {'hg', 'gld', 'uas', 'ulm'}, f'niet alle soorten terreinen: {typs}')
    noname = [h['ident'] for h in hg if not h['nm']]
    ok(not noname, f'terrein zonder naam (accent in de AIP-naam, bv. WÂNSWERT?): {noname}')  # 27 nov: naam-regex kende alleen A–Z
    ok(await a.v('v.hgCyl.children.filter(c=>c.userData.h).length') == len(hg), 'niet elk terrein heeft een cilinder')
    for nm, typ, word, lim in (('Boxtel', 'uas', 'Modelvliegterrein Boxtel', '1020 ft AMSL'), ('Malden', 'gld', 'Zweefvliegveld Malden', '2300 ft AGL')):
        h = next(x for x in hg if x['nm'] == nm and x['typ'] == typ)
        await a.place(h['x'] - h['r'] - 0.9, h['n'], 800, 90, paused=True)
        await a.ev('()=>{const v=window.__vfr;for(const f of v.LAYERS)v.WARNED.add(f.ident);for(const g of v.HG)v.WARNED.add("HG"+g.ident);v.PAUSED=false}')
        await a.ev('(h)=>{const v=window.__vfr;v.WARNED.delete("HG"+h.ident);v.hudTick()}', h)
        n = ''
        for _ in range(150):
            await a.wait(100); n = await a.v('v.NOTICE') or ''
            if n: break
        ok(word in n and lim in n, f'{nm}: verwacht "{word}" en "{lim}": {n[:140]}')
        if typ == 'gld': ok('123.355' in n, f'Malden: frequentie ontbreekt: {n[:160]}')
        # Christian 21 nov: bij een lierterrein kwam elke 4 s opnieuw een melding. Eén keer per nadering, zoals bij luchtruim.
        await a.ev('()=>{const v=window.__vfr;v.NOTICE="";v.PAUSED=false}')
        rep = ''
        for _ in range(60):
            await a.wait(100)
            await a.ev('(h)=>{const v=window.__vfr;v.PLANE.x=h.x-h.r-0.9;v.PLANE.n=h.n;v.PLANE.alt=800;v.PAUSED=false;v.hudTick()}', h)
            rep = await a.v('v.NOTICE') or ''
            if word in rep: break
        ok(word not in rep, f'{nm}: melding herhaalt zich terwijl je er nog bent: {rep[:80]}')
    b = next(x for x in hg if x['nm'] == 'Boxtel')
    w = await a.ev('(nm)=>{const v=window.__vfr;const c=v.hgCyl.children.find(m=>m.userData.hg===nm&&m.userData.typ==="uas");const b=new v.THREE.Box3().setFromObject(c);return b.max.x-b.min.x}', 'Boxtel')
    ok(abs(w - 2 * 0.926) < 0.05, f'Boxtel: straal 0,5 NM verwacht, breedte {w:.2f} km')
    h = next(x for x in hg if x['nm'] == 'Malden' and x['typ'] == 'gld')
    await a.place(h['x'] - 4, h['n'] - 3, 1500, 55, paused=True); await a.ev('()=>{const v=window.__vfr;v.NOTICE="";v.hudTick()}'); await a.frames(6); await a.shot('enr55_malden')

async def d_landscape_probe(a):  # Christian 21 nov: "kaart horizontaal op mobiel is nog steeds moeilijk leesbaar" → sonde als smalle lade rechts
    if a.form != 'p7l': return
    await a.hit('#modal [data-ac=map]'); await a.frames(3)
    vw = a.pg.viewport_size
    await a.tap_xy(vw['width'] * .4, vw['height'] * .55); await a.frames(3)
    if not await a.visible('#info .lim'): await a.hit('#info .free')  # ingeklapt → uitklappen
    await a.frames(2)
    r = await a.ev('()=>{const b=document.getElementById("info").getBoundingClientRect();return [b.left,b.top,b.right,b.bottom]}')
    ok(vw['width'] - r[2] < 14 and r[2] - r[0] <= .36 * vw['width'], f'sonde liggend is geen smalle lade rechts: {r} (scherm {vw})')
    ok(r[3] - r[1] > .6 * vw['height'], f'lade gebruikt de hoogte niet: {r}')
    tape = await a.ev('()=>{const e=document.getElementById("tape");if(!e||getComputedStyle(e).display==="none"||e.offsetParent===null)return null;const b=e.getBoundingClientRect();return b.width?[b.left,b.top,b.right,b.bottom]:null}')
    ok(not tape or tape[2] <= r[0] + 2, f'kolom "boven de sonde" overlapt of staat naast de lade (samen > ⅓): {tape}')
    px = await a.ev('()=>{const v=window.__vfr;return v.scr(v.PROBE.x,v.PROBE.n)}')
    ok(px[0] < r[0] - 10, f'sondepunt valt onder de lade: x={px[0]:.0f}, lade vanaf {r[0]:.0f}')
    m = await a.menus_open(); ok(len(m) <= 1, f'meerdere menu\'s open: {m}')
    await a.shot('landscape_probe')

async def d_para_text(a):  # AIP ENR 5.5: elke paradropzone zijn eigen bovengrens en operator (was overal 'FL100 · ENPC')
    await a.hit('#modal [data-ac=glider]'); await a.frames(2)
    r = await a.ev('()=>{const v=window.__vfr;return v.LAYERS.filter(f=>f.layer==="PJA").map(f=>[f.ident,f.hiTxt,v.warnText(f)])}')
    ok(r, 'geen paradropzones in de regio')
    for ident, hi, t in r:
        ok(hi in t or hi.replace('FL0', 'FL') in t, f'{ident}: waarschuwing noemt de bovengrens {hi} niet: {t[:120]}')
        # 27 nov (heel NL): ENPC is wél de operator van cluster Noord-Brabant (ENR 5.5, AIRAC 12-2026); elders nooit
        ENPC = {'EHAAPJA013', 'EHAAPJA014', 'EHAAPJA010', 'EHSEPJA001', 'EHAAPJA003'}
        ok(('ENPC' in t) == (ident in ENPC), f'{ident}: verkeerde operator: {t[:160]}')
    ops = {t.split('Operator:')[-1].split(',')[0].strip() for _, _, t in r if 'Operator:' in t}
    ok(len(r) < 2 or len(ops) > 1 or all(i in ENPC for i, _, _ in r), f'alle paradropzones dezelfde operator: {ops}')

async def d_landmarks(a):  # voorstel herkenningspunten 21 nov, akkoord Christian 22 nov: Eindhoven-centrum 7 → 2, Sluis Heumen weg
    await a.hit('#modal [data-ac=map]'); await a.frames(2)
    txt = await a.v("v.labels.filter(L=>L.isLm&&L.el).map(L=>L.el.textContent).join('|')")
    for nm in ('Sluis Heumen', 'Catharinakerk', 'Strijp-S', 'Bunkertoren', 'Vestedatoren', 'De Regent'):
        ok(nm not in txt, f'{nm} hoort weg (voorstel herkenningspunten)')
    for nm in ('Evoluon', 'Philips Stadion', 'Amercentrale', 'Eusebiuskerk', 'Westpoint'):
        ok(nm in txt, f'{nm} ontbreekt')

async def d_bridges(a):  # Christian 21 nov: "bij Maas en Waal mis ik bruggen" → snelweg × grote rivier
    await a.hit('#modal [data-ac=map]'); await a.frames(2)
    br = await a.v('v.BRIDGES.map(b=>({ref:b.ref,river:b.river,lo:b.lo,la:b.la,x:b.x,n:b.n}))')
    ok(8 <= len(br) <= 25, f'onverwacht aantal bruggen: {len(br)}')
    for ref, river, lo, la in (('A2', 'Waal', 5.258, 51.818), ('A50', 'Waal', 5.738, 51.885), ('A2', 'Maas', 5.306, 51.740), ('A73', 'Maas', 5.840, 51.759)):
        ok(any(b['ref'] == ref and b['river'] == river and abs(b['lo'] - lo) < .01 and abs(b['la'] - la) < .01 for b in br), f'brug {ref} over de {river} ontbreekt')
    ok(len({(round(b['lo'], 2), round(b['la'], 2)) for b in br}) == len(br), 'dubbele bruggen (twee rijbanen?)')
    for nm in ('Waalbrug', 'De Oversteek', 'John Frostbrug'): ok(any(b['ref'] == nm for b in br), f'stadsbrug {nm} ontbreekt (A1 herkenningspunten)')
    n = await a.v("v.labels.filter(L=>L.isLm&&L.el&&L.el.textContent.includes(\"🌉\")).length")
    ok(n >= len(br) or n == 0, f'niet elke brug heeft een label ({n}/{len(br)})')
    # Christian 22 nov: A50-brug stond een kwartslag gedraaid. Klasse: de lange as van elk brugmodel ligt in de wegrichting (±10°)
    bad = await a.ev('''()=>{const v=window.__vfr,T=v.THREE,out=[];for(const g of v.lmGroup.children){const b=g.userData.bridgeObj;if(!b)continue;
      const z=new T.Vector3(0,0,1).applyQuaternion(g.quaternion),e=z.x,n=-z.z,re=Math.sin(b.dir),rn=Math.cos(b.dir);
      const ang=Math.acos(Math.min(1,Math.abs(e*re+n*rn)))*180/Math.PI;if(ang>10)out.push(b.ref+" "+b.river+" "+Math.round(ang)+"°")}return out}''')
    ok(await a.v('v.lmGroup.children.filter(g=>g.userData.bridgeObj).length') == len(br), 'niet elke brug heeft een model')
    ok(not bad, f'brug dwars op de weg: {bad[:4]}')
    b = next(x for x in br if x['ref'] == 'A2' and x['river'] == 'Waal')
    await a.ev('()=>window.__vfr.setMode("fly","motor")'); await a.place(b['x'] - 2.5, b['n'] - 2.0, 1500, 50, paused=True); await a.frames(6); await a.shot('brug_a2_waal')

async def d_cross_section(a):  # backlog M4: doorsnede langs een lijn (verticaal profiel)
    await a.hit('#modal [data-ac=map]'); await a.frames(3)
    await a.ev('()=>{const v=window.__vfr;const [x,n]=v.proj(5.30,51.45);v.PROBE.x=x;v.PROBE.n=n;v.PROBE.user=true;v.showProbe()}'); await a.frames(2)
    if not await a.visible('#xsStart'): await a.hit('#info .free')  # mobiel: sonde ingeklapt → uitklappen
    await a.hit('#xsStart'); await a.frames(2)
    ok(await a.visible('#xsHint'), 'geen hint om het eindpunt te kiezen')
    xy = await a.ev('()=>{const v=window.__vfr;const [x,n]=v.proj(5.62,51.45);return v.scr(x,n)}')
    vw = a.pg.viewport_size; ok(0 < xy[0] < vw['width'] and 0 < xy[1] < vw['height'], f'eindpunt buiten beeld {xy}')
    await a.tap_xy(xy[0], xy[1]); await a.frames(3)
    ok(await a.visible('#xs'), 'doorsnede-paneel opent niet')
    runs = await a.v('v.XS.drawn&&v.XS.drawn.runs')
    ok(runs and 'EHEH' in runs, f'Eindhoven CTR niet in de doorsnede: {runs}')
    m = await a.menus_open(); ok(len(m) <= 1, f'meerdere menu\'s open: {m}')
    await a.shot('cross_section')
    await a.hit('#xsClose'); ok(not await a.visible('#xs'), 'doorsnede sluit niet')

async def d_tour(a):  # backlog M4: rondleiding; elke stap toont tekst uit de data en beweegt de camera
    await a.hit('#modal [data-ac=map]'); await a.frames(2)
    await a.hit('#btnPanel'); await a.wait(400); await a.hit('#btnTour'); await a.frames(2)
    ok(await a.visible('#tour'), 'rondleiding opent niet')
    n = len(await a.v('v.TOUR')); seen = []
    for i in range(n):
        t = await a.pg.inner_text('#tourTxt'); seen.append(t[:40])
        ok(f'{i+1}/{n}' in t, f'stap {i+1}: teller ontbreekt ({t[:60]!r})')
        ok('undefined' not in t and 'null' not in t, f'stap {i+1}: lege waarde in tekst: {t[:120]!r}')
        m = await a.menus_open(); ok(len(m) <= 1, f'stap {i+1}: meerdere menu\'s open: {m}')
        if i == 1: await a.wait(1600); await a.shot('tour_ctr')
        await a.hit('#tourNext')
    ok(not await a.visible('#tour'), 'rondleiding sluit niet na de laatste stap')
    ok(len(set(seen)) == n, f'dubbele stappen: {seen}')

async def d_ahead_full(a):  # Noor 1: frequentie in de waarschuwingsregel nooit afgekapt
    await a.hit('#modal [data-ac=motor]')
    e = await a.ev(JS_FREE_EDGE, ['EHEH', 1.8, 1000])
    await a.place(e[0], e[1], 1000, e[2], paused=True)
    await a.ev('()=>{const v=window.__vfr;for(const f of v.LAYERS)v.WARNED.add(f.ident);for(const g of v.HG)v.WARNED.add("HG"+g.ident);v.hudTick()}'); await a.frames(2)
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
            key = rnd.choice(['ArrowUp', 'ArrowDown', 'ArrowLeft', 'ArrowRight', 'w', 's', 'a', 'd', 'Shift+S', ' ', 'l', 'c', '+', '-']); log.append('key ' + key)
            ks = key.split('+') if len(key) > 1 else [key]  # 'Shift+S' → Shift, S (keyboard.down kent geen combinaties)
            for k_ in ks: await a.pg.keyboard.down(k_)
            await a.wait(rnd.randint(30, 400))
            for k_ in reversed(ks): await a.pg.keyboard.up(k_)
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
    det = [('opdracht "vlieg naar"', d_task_text), ('ballondoel bereikbaar met de wind', d_balloon_reachable), ('buitenlandse CTR: radio-info', d_foreign_ctr), ('banner RMZ 1 regel', d_banner_rmz), ('geweigerde klaring op tijd', d_refused), ('klaring aangrenzend gebied', d_adjacent_clearance), ('waarschuwing 2–20 s vooraf', d_warn_lead), ('RMZ Volkel: eerst oproepen', d_rmz_call), ('doel als lijn', d_goal_line), ('ballon voorbij doel', d_balloon_past), ('geslaagd met klaring', d_clearance_success), ('geen klasse G buiten NL', d_outside_nl), ('camera slepen/knijpen zonder schokken', d_touch_smooth), ('kantelen', d_tilt), ('camera: geen sprong, niet direct terugveren', d_cam_no_jump), ('panelpunten 14 nov', d_panel_fixes), ('waarschuwing niet afgekapt', d_ahead_full), ('opdracht vanaf de sonde', d_probe_task), ('kantelen na draaien staand↔liggend', d_tilt_rotate), ('kantelen standaard + knoppen weg', d_tilt_default), ('toetsen zoals MSFS', d_msfs_keys), ('sneltoetskaart', d_keycard), ('spatie bij keerpunten', d_space_waypoints), ('kantelen: terugval naar knoppen', d_tilt_fallback), ('kantel-looping + ballon', d_tilt_loop_balloon), ('RMZ: oproepen vanuit de RMZ', d_rmz_inside_call), ('zoomen desktop', d_zoom_desktop), ('opstijgen met kantelen', d_tilt_takeoff), ('alles aan + labels aan/uit', d_defaults_labels), ('doelbaken', d_goal_marker), ('tik op melding = verder', d_tap_notice), ('geen z-fighting grondlijnen', d_no_zfight), ('bruggen niet te groot', d_bridge_size), ('3D-herkenningspunten niet te groot', d_lm_size), ('labels: budget en geen overlap', d_label_budget), ('fout in missie: opnieuw of door', d_fail_restart), ('Start na missie = volgende', d_start_next), ('grondring op de grond', d_hg_ring_ground), ('vario = echte stijgsnelheid', d_vario_real), ('rivier-/wegdoel = hele rivier', d_line_goal_whole), ('alles aanklikbaar (ook ENR 5.5)', d_click_all), ('camera liggend dichtbij', d_chase_landscape), ('labels niet over het toestel', d_labels_off_aircraft), ('toestel wisselen via toesteltje', d_ac_switch), ('landen in de stad', d_land_city), ('kantelen geleidelijk', d_tilt_analog), ('missies', d_missions), ('open menu ligt bovenop', d_menu_on_top), ('niet haperen bij missies', d_no_freeze), ('▶ start zonder vastlopen', d_start_smooth), ('heel NL: landschap per tegel', d_tiles), ('missiegenerator', d_generator), ('gedeelde ENR 5.5-terreinen (Malden)', d_shared_sites), ('geen voorbeeldcircuit', d_no_circuit), ('P-gebieden H24 zichtbaar', d_h24_always), ('labels knipperen niet', d_labels_steady), ('missies echt uitvliegen', d_missions_flown), ('draaien staand↔liggend (echt)', d_tilt_rotate_real), ('lierterreinen', d_winch_sites), ('ENR 5.5-terreinen', d_enr55_sites), ('sonde liggend als lade', d_landscape_probe), ('paradropzones: eigen grens en operator', d_para_text), ('klaring CTR dekt RMZ (Deelen)', d_ctr_covers_rmz), ('kantelen na pauze/missie', d_tilt_pause_edges), ('kantelen: melding in de bocht', d_tilt_notice_bend), ('bruggen Maas/Waal', d_bridges), ('doorsnede', d_cross_section), ('rondleiding', d_tour), ('herkenningspunten', d_landmarks), ('idents uniek per luchtruimsoort', d_unique_idents)]
    async with async_playwright() as p:
        try:
            b = await p.chromium.launch(args=ARGS)
        except Exception:
            # cloud: Playwright-versie past niet bij de voorgeïnstalleerde browser
            exe = os.environ.get('PW_CHROMIUM', '/opt/pw-browsers/chromium')
            if not os.path.exists(exe): raise
            b = await p.chromium.launch(args=ARGS, executable_path=exe)
        for form in forms:
            for layer, tests in (('smoke', smoke), ('det', det)):
                if o.only and o.only != layer: continue
                for name, fn in tests:
                    if o.k and o.k.lower() not in name.lower() and o.k not in fn.__name__: continue
                    if fn in LOGIC_ONLY and form != 'desk' and 'desk' in forms: continue  # pure logica (missies uitvliegen): één schermvorm is genoeg
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

LOGIC_ONLY = {d_missions_flown, d_generator}  # vormonafhankelijk en zwaar (±15 min per vorm)

if __name__ == '__main__':
    asyncio.run(main())
