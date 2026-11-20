#!/usr/bin/env python3
"""Eén commando om overal te kunnen werken: cloud (Linux) of Christians pc (Windows).

    python tools/setup.py          # installeert wat ontbreekt, idempotent
    python tools/setup.py --check  # alleen melden wat er is

Zet neer:
  - .devenv/node_modules/three   (three@0.160.0, zelfde versie als de CDN in index.html)
  - Python-pakket playwright + Chromium
Niets hiervan gaat de repo in (.gitignore).
"""
import os, shutil, subprocess, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEV = os.path.join(ROOT, '.devenv')
THREE = os.path.join(DEV, 'node_modules', 'three')
CHECK = '--check' in sys.argv


def run(cmd, **kw):
    print('  $', ' '.join(cmd))
    return subprocess.run(cmd, **kw).returncode == 0


def have_playwright():
    try:
        import playwright  # noqa: F401
        return True
    except ImportError:
        return False


status = {}

# 1. three.js
status['three.js 0.160'] = os.path.isfile(os.path.join(THREE, 'build', 'three.module.js'))
if not status['three.js 0.160'] and not CHECK:
    npm = shutil.which('npm') or shutil.which('npm.cmd')
    if npm:
        os.makedirs(DEV, exist_ok=True)
        pj = os.path.join(DEV, 'package.json')
        if not os.path.exists(pj):
            open(pj, 'w').write('{"name":"devenv","private":true}\n')
        status['three.js 0.160'] = run([npm, 'i', 'three@0.160.0', '--silent'], cwd=DEV)
    else:
        print('  ! npm ontbreekt — installeer Node.js, of zet THREE_DIR naar een map met three@0.160.0')

# 2. Playwright (Python) + Chromium
status['playwright'] = have_playwright()
if not status['playwright'] and not CHECK:
    extra = ['--break-system-packages'] if sys.platform.startswith('linux') else []
    status['playwright'] = run([sys.executable, '-m', 'pip', 'install', '-q', 'playwright', *extra])
if status['playwright'] and not CHECK:
    run([sys.executable, '-m', 'playwright', 'install', 'chromium'],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

# 3. git / gh (alleen melden; inloggen doet Christian of de sessie)
status['git'] = bool(shutil.which('git'))
status['gh (optioneel)'] = bool(shutil.which('gh'))

print('\nOmgeving:')
for k, v in status.items():
    print(f'  {"✓" if v else "✗"} {k}')
print('\nSnelle check:  python tools/e2e.py --quick')
sys.exit(0 if status['three.js 0.160'] and status['playwright'] else 1)
