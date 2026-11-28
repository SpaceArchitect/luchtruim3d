"""Lost de terugkerende merge-conflicten in index.html/tools/e2e.py op (28 nov).
Render-regel: HEAD; window.__vfr: vereniging; det-lijst: vereniging; twee nieuwe testfuncties: allebei.
Gebruik: python tools/merge_resolve.py <label na >>>>>>>, bv. origin/wip/x> index.html tools/e2e.py
Onbekend conflict → stopt; los dat zelf op."""
import re,sys
THEIRS=sys.argv[1]  # label after >>>>>>>
pat=re.compile(r'<<<<<<< HEAD\n(.*?)=======\n(.*?)>>>>>>> '+re.escape(THEIRS)+r'\n',re.S)
def split_top(body):
    out=[];d=0;cur='';q=None
    for ch in body:
        if q:
            cur+=ch
            if ch==q: q=None
            continue
        if ch in '"\'`': q=ch
        elif ch in '([{': d+=1
        elif ch in ')]}': d-=1
        if ch==',' and d==0: out.append(cur);cur=''
        else: cur+=ch
    if cur.strip(): out.append(cur)
    return out
def key(e):
    e=e.strip();m=re.match(r'(?:get |set )?([A-Za-z_$][\w$]*)',e);return (e[:4] if e[:4] in('get ','set ') else '')+m.group(1) if m else e
def vfr_union(h,t):
    i=h.index('{');j=h.rindex('}');bh=h[i+1:j];bt=t[t.index('{')+1:t.rindex('}')]
    eh=split_top(bh);kh={key(e) for e in eh};add=[e for e in split_top(bt) if key(e) not in kh]
    return h[:i+1]+','.join(eh+add)+h[j:]
def items(line):
    inner=line[line.index('[')+1:line.rindex(']')];return re.findall(r"\('(?:[^'\\]|\\.)*', \w+\)",inner)
for p in sys.argv[2:]:
    s=open(p,encoding='utf-8').read()
    def rep(m):
        h,t=m.group(1),m.group(2)
        if '    det = [' in h:
            ih,it=items(h),items(t);fn=lambda x:x.rsplit(', ',1)[1];have={fn(x) for x in ih}
            return h[:h.index('[')+1]+', '.join(ih+[x for x in it if fn(x) not in have])+']\n'
        if 'window.__vfr={' in h:
            hl=h.split('\n');tl=t.split('\n');out=[]
            for a in hl:
                if a.startswith('window.__vfr={'):
                    b=next(x for x in tl if x.startswith('window.__vfr={'));out.append(vfr_union(a,b))
                else: out.append(a)
            return '\n'.join(out)
        if h.startswith('async def ') and t.startswith('async def '): return h+'\n'+t
        raise SystemExit('onbekend conflict in '+p+': '+h[:80])
    s2=pat.sub(rep,s);open(p,'w',encoding='utf-8').write(s2);print(p,'opgelost', s.count('<<<<<<<'))
