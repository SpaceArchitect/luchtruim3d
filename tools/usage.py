"""Lees de laatste usage-meting (van tools/usage_probe.py op Christians pc) vanuit de cloud.
    python tools/usage.py          → bv. "week 42% · sessie 17% · 12 min oud"
Exitcode 0 = gelezen, 1 = geen of te oude meting (> 3 uur): dan voorzichtig schatten (CLAUDE.md › Budget)."""
import json, subprocess, sys, datetime
r = subprocess.run(['git', 'fetch', '-q', '--depth=1', 'origin', 'meta/usage'], capture_output=True, text=True)
if r.returncode:
    print('Geen usage-meting (branch meta/usage bestaat nog niet; probe op de pc nog niet ingesteld).'); sys.exit(1)
d = json.loads(subprocess.run(['git', 'show', 'FETCH_HEAD:usage.json'], capture_output=True, text=True, check=True).stdout)
age = (datetime.datetime.now(datetime.timezone.utc) - datetime.datetime.fromisoformat(d['ts'])).total_seconds() / 60
if not d.get('ok'):
    print(f"Laatste meting mislukt ({age:.0f} min geleden): {d.get('reason')}"); sys.exit(1)
print(f"week {d.get('week_pct')}% · sessie {d.get('session_pct')}% · {age:.0f} min oud")
for m in d.get('meters', []): print('  ', m.get('v'), '·', m.get('label', '')[:100])
sys.exit(0 if age < 180 else 1)
