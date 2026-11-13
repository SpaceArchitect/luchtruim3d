import sys,asyncio,json
from playwright.async_api import async_playwright
# usage: shot.py out.png [w h] [js...]
async def main():
    out=sys.argv[1]; w=int(sys.argv[2]) if len(sys.argv)>2 else 1280; h=int(sys.argv[3]) if len(sys.argv)>3 else 800
    js=sys.argv[4:]
    async with async_playwright() as p:
        b=await p.chromium.launch(executable_path='/usr/bin/google-chrome',args=['--use-gl=angle','--use-angle=swiftshader','--enable-unsafe-swiftshader','--ignore-gpu-blocklist'])
        pg=await b.new_page(viewport={'width':w,'height':h})
        errs=[]
        pg.on('console',lambda m: errs.append(m.type+': '+m.text) if m.type in('error','warning') else None)
        pg.on('pageerror',lambda e: errs.append('PAGEERR '+str(e)))
        await pg.goto('http://localhost:8765/t.html'); await pg.wait_for_timeout(2500)
        for s in js:
            if s.startswith('wait:'): await pg.wait_for_timeout(int(s[5:])); continue
            if s.startswith('drag:'):
                a=[int(v) for v in s[5:].split(',')];await pg.mouse.move(a[0],a[1]);await pg.mouse.down(button='right' if len(a)>4 else 'left')
                for i in range(1,11): await pg.mouse.move(a[0]+(a[2]-a[0])*i/10,a[1]+(a[3]-a[1])*i/10);await pg.wait_for_timeout(30)
                await pg.mouse.up(button='right' if len(a)>4 else 'left');continue
            if s.startswith('wheel:'):
                await pg.mouse.move(640,400);await pg.mouse.wheel(0,int(s[6:]));await pg.wait_for_timeout(300);continue
            if s.startswith('click:'):
                await pg.click(s[6:],delay=180);await pg.wait_for_timeout(400);continue
            if s.startswith('key:'): 
                k,d=s[4:].split(',');await pg.keyboard.down(k);await pg.wait_for_timeout(int(d));await pg.keyboard.up(k);continue
            r=await pg.evaluate(s)
            if r is not None: print('JS>',json.dumps(r)[:1500])
        await pg.wait_for_timeout(800)
        await pg.screenshot(path=out)
        for e in errs[:15]: print(e[:300])
        await b.close()
asyncio.run(main())
