"""Missierapport: vliegt (plant) elke missie en meet hoe moeilijk hij echt is.
Gebruik: python tools/mission_report.py [--json pad]
Per poot: rechte lijn, route met klaring, route zonder klaring (omvliegen/stijgen/dalen), hoogtes, conflictgebieden op de rechte lijn."""
import asyncio, json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('E2E_PORT', '8797')
import e2e
from playwright.async_api import async_playwright

MEASURE = '''(id)=>{const v=window.__vfr,m=v.MISSIONS.find(x=>x.id===id),st=v.misStart(m);if(!st)return {id,err:'geen start'};const L=v.MPT();
  let p=[st.x,st.n],legs=[];for(const nm of m.legs){const q=L[nm],d=Math.hypot(q[0]-p[0],q[1]-p[1]);const t0=performance.now();
    const a=v.planRoute(p,q,m.alt,{ac:m.ac}),b=v.planRoute(p,q,m.alt,{ac:m.ac,noClr:true});
    const on=new Set();for(let s=0;s<=d;s+=.25){const x=p[0]+(q[0]-p[0])*s/d,n=p[1]+(q[1]-p[1])*s/d;for(const f of v.applies(v.featsAt(x,n),m.alt))if(['P','R','UAS','PJA','TRA','TSA','CTR','TMA','RMZ'].includes(f.layer))on.add(f.ident);for(const h of v.HG)if(Math.hypot(h.x-x,h.n-n)<h.r+.3&&m.alt<=h.top+700)on.add('HG '+h.nm);}
    legs.push({to:nm,d:+d.toFixed(1),clr:a&&{len:+a.len.toFixed(1),alts:a.alts},noclr:b&&{len:+b.len.toFixed(1),alts:b.alts},on:[...on],ms:Math.round(performance.now()-t0)});p=q;}
  return {id,ac:m.ac,lvl:m.lvl,title:m.title,alt:m.alt,legs};}'''

async def main():
    url = e2e.serve()
    async with async_playwright() as p:
        try: b = await p.chromium.launch(args=e2e.ARGS)
        except Exception: b = await p.chromium.launch(args=e2e.ARGS, executable_path='/opt/pw-browsers/chromium')
        a = await e2e.new_app(p, b, 'desk', url)
        await a.hit('#modal [data-ac=glider]'); await a.frames(2)
        out = []
        for mid in await a.ev('()=>window.__vfr.MISSIONS.map(m=>m.id)'):
            r = await a.ev(MEASURE, mid); out.append(r)
            print(f"{r['id']:10} {r.get('ac',''):7} lvl{r.get('lvl')} ", r.get('err', ''))
            for l in r.get('legs', []):
                c, n = l['clr'], l['noclr']
                print(f"   → {l['to']:22} recht {l['d']:5} km · met klaring {c and c['len']} {c and c['alts']} · zonder {n and n['len']} {n and n['alts']} · {l['ms']} ms · op de lijn: {', '.join(l['on'])}")
        if '--fly' in sys.argv:  # elke vaste missie echt uitvliegen (route zonder klaring waar die bestaat) en meten
            for ac in ('glider', 'motor', 'balloon'):
                await a.ev('(ac)=>window.__vfr.setMode("fly",ac)', ac); await a.frames(2)
                for mid in await a.ev('(ac)=>window.__vfr.MISSIONS.filter(m=>m.ac===ac).map(m=>m.id)', ac):
                    st = {}
                    try:
                        await a.ev('()=>window.__vfr.RTOUT.clear()'); await e2e.fly_mission(a, mid, 'around', st)
                    except Exception as ex: st['fout'] = str(ex)[:120]
                    print(f"VLUCHT {mid:10} {json.dumps(st, ensure_ascii=False)}")
        if '--gen' in sys.argv:
            for ac in ('glider', 'motor', 'balloon'):
                for L in range(1, int(sys.argv[sys.argv.index('--gen') + 1]) + 1):
                    r = await a.ev('''([ac,L])=>{const v=window.__vfr,t=performance.now(),m=v.genMission(ac,L);return m&&{id:m.id,lvl:m.lvl,legs:m.legs,alt:m.alt,brief:m.brief,goal:m.goal,ms:Math.round(performance.now()-t)}||{id:ac+L,none:1,ms:Math.round(performance.now()-t)}}''', [ac, L])
                    print(f"{r['id']:16} {r['ms']:5} ms", 'GEEN' if r.get('none') else f"lvl{r['lvl']} {r['alt']} ft · {r['brief'][:110]} · {r['goal'][:40]}")
        if '--json' in sys.argv: json.dump(out, open(sys.argv[sys.argv.index('--json') + 1], 'w'), ensure_ascii=False, indent=1)
        await b.close()
asyncio.run(main())
