"""Usage-meter voor Claude-sessies in de cloud.

Draait op Christians pc (Windows Taakplanner, elke 30 min, onzichtbaar via pythonw).
Leest https://claude.ai/settings/usage in een EIGEN, headless Chromium-profiel
(los van Chrome) en zet het resultaat als usage.json op branch `meta/usage`.
De cloud leest het met `python tools/usage.py`.

Eenmalig (Christian, want inloggen doet hij zelf):
    python tools/usage_probe.py --login      # opent een venster, log in op claude.ai, sluit het venster
    python tools/usage_probe.py --install    # zet de taak in de Taakplanner (elke 30 min)
Testen:
    python tools/usage_probe.py              # één meting + push

Er worden geen wachtwoorden of cookies gekopieerd: het profiel blijft lokaal op de pc.
"""
import json, os, subprocess, sys, time, datetime, pathlib, shutil

HOME = pathlib.Path(os.environ.get('LOCALAPPDATA', pathlib.Path.home())) / 'luchtruim3d'
PROFILE = HOME / 'usage-profile'
REPO_DIR = HOME / 'usage-repo'
REPO_URL = 'https://github.com/SpaceArchitect/luchtruim3d.git'
BRANCH = 'meta/usage'
URL = 'https://claude.ai/settings/usage'


def read_usage(headless=True):
    from playwright.sync_api import sync_playwright
    with sync_playwright() as p:
        ctx = p.chromium.launch_persistent_context(str(PROFILE), headless=headless)
        pg = ctx.pages[0] if ctx.pages else ctx.new_page()
        pg.goto(URL, wait_until='domcontentloaded', timeout=60000)
        try:
            pg.wait_for_selector('[aria-valuenow]', timeout=30000)
        except Exception:
            ctx.close()
            return {'ok': False, 'reason': 'geen meters gevonden (uitgelogd? draai --login)', 'url': pg.url}
        meters = pg.evaluate('''()=>[...document.querySelectorAll('[aria-valuenow]')].map(m=>{
            let t='';let e=m;for(let i=0;i<6&&e;i++){e=e.parentElement;if(e&&e.innerText&&e.innerText.length<300){t=e.innerText;}}
            return {v:+m.getAttribute('aria-valuenow'),max:+(m.getAttribute('aria-valuemax')||100),label:(m.getAttribute('aria-label')||'')+' '+t.replace(/\\s+/g,' ').slice(0,160)}})''')
        ctx.close()
    pct = [round(100 * m['v'] / (m['max'] or 100)) for m in meters]
    # Volgorde volgens CLAUDE.md: 2e waarde = sessie, 3e = week. Labels gaan mee zodat de cloud kan controleren.
    return {'ok': True, 'meters': meters, 'session_pct': pct[1] if len(pct) > 1 else None,
            'week_pct': pct[2] if len(pct) > 2 else None}


def push(data):
    data['ts'] = datetime.datetime.now(datetime.timezone.utc).isoformat(timespec='seconds')
    if not (REPO_DIR / '.git').exists():
        REPO_DIR.mkdir(parents=True, exist_ok=True)
        subprocess.run(['git', 'init', '-q', str(REPO_DIR)], check=True)
        subprocess.run(['git', '-C', str(REPO_DIR), 'remote', 'add', 'origin', REPO_URL], check=True)
    (REPO_DIR / 'usage.json').write_text(json.dumps(data, ensure_ascii=False, indent=1), encoding='utf-8')
    g = lambda *a: subprocess.run(['git', '-C', str(REPO_DIR), *a], check=True, capture_output=True)
    # één commit, steeds vervangen (wees-branch): geen groeiende geschiedenis
    subprocess.run(['git', '-C', str(REPO_DIR), 'checkout', '-q', '--orphan', 'tmp'], capture_output=True)
    g('add', 'usage.json')
    g('-c', 'user.name=usage-probe', '-c', 'user.email=usage-probe@localhost', 'commit', '-q', '-m', 'usage ' + data['ts'])
    g('branch', '-M', BRANCH)
    g('push', '-q', '-f', 'origin', BRANCH)


def install():
    pyw = shutil.which('pythonw') or sys.executable.replace('python.exe', 'pythonw.exe')
    cmd = f'"{pyw}" "{pathlib.Path(__file__).resolve()}"'
    subprocess.run(['schtasks', '/Create', '/F', '/SC', 'MINUTE', '/MO', '30', '/TN', 'luchtruim3d-usage', '/TR', cmd], check=True)
    print('Taak "luchtruim3d-usage" staat in de Taakplanner (elke 30 min, zonder venster).')


if __name__ == '__main__':
    HOME.mkdir(parents=True, exist_ok=True)
    if '--login' in sys.argv:
        from playwright.sync_api import sync_playwright
        with sync_playwright() as p:
            ctx = p.chromium.launch_persistent_context(str(PROFILE), headless=False)
            pg = ctx.pages[0] if ctx.pages else ctx.new_page(); pg.goto(URL)
            print('Log in op claude.ai in het venster en sluit het daarna.')
            pg.wait_for_event('close', timeout=0)
        sys.exit(0)
    if '--install' in sys.argv:
        install(); sys.exit(0)
    try:
        d = read_usage()
    except Exception as e:
        d = {'ok': False, 'reason': f'{type(e).__name__}: {e}'[:300]}
    try:
        push(d)
    except Exception as e:
        (HOME / 'usage-error.txt').write_text(str(e), encoding='utf-8')
    print(json.dumps({k: d.get(k) for k in ('ok', 'session_pct', 'week_pct', 'reason')}, ensure_ascii=False))
