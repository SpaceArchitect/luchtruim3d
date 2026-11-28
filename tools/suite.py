#!/usr/bin/env python3
"""Volledige suite, zo snel als veilig kan (Christian 28 nov):
1) alles behalve de tijdgevoelige tests: 4 schermvormen parallel (1 proces per vorm);
2) de tijdgevoelige tests (kantelen, 30 fps, laadscherm, …): daarna, één proces, niets anders tegelijk.
    python3 tools/suite.py            # schrijft logs naar $SUITE_LOGS of /tmp; exit 1 bij een ✗
"""
import os, subprocess, sys, tempfile
here = os.path.dirname(os.path.abspath(__file__)); e2e = os.path.join(here, 'e2e.py')
logs = os.environ.get('SUITE_LOGS') or tempfile.mkdtemp(prefix='suite-')
os.makedirs(logs, exist_ok=True)
def cmd(*a): return [sys.executable, '-u', e2e, *a]
procs = []
for i, f in enumerate(('desk', 'p7', 'p7l', 'se')):
    env = dict(os.environ, E2E_PORT=str(8820 + i))
    procs.append((f, subprocess.Popen(cmd('--forms', f, '--timing', 'skip'), stdout=open(f'{logs}/par_{f}.log', 'w'), stderr=subprocess.STDOUT, env=env)))
for f, p in procs: p.wait(timeout=7000)
env = dict(os.environ, E2E_PORT='8830')
subprocess.run(cmd('--only', 'det', '--timing', 'only'), stdout=open(f'{logs}/timing.log', 'w'), stderr=subprocess.STDOUT, env=env, timeout=7000)
bad = 0
for n in sorted(os.listdir(logs)):
    for line in open(os.path.join(logs, n), encoding='utf-8', errors='replace'):
        if line.startswith('== ') or '✗' in line:
            print(n, line.rstrip()); bad += '✗' in line
print('logs:', logs); sys.exit(1 if bad else 0)
