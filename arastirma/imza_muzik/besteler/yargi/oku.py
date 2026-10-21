import json, sys
from collections import defaultdict
NN=['C','Db','D','Eb','E','F','F#','G','Ab','A','Bb','B']
def nm(m): return f"{NN[m%12]}{m//12-1}"
def fb(b):
    fr=b-int(b)
    s={0:'',0.333:'⅓',0.334:'⅓',0.5:'½',0.667:'⅔',0.666:'⅔',0.25:'¼',0.75:'¾'}
    k=round(fr,3)
    return f"{int(b)}{s.get(k, '.'+str(k)[2:])}"
for p in sys.argv[1:]:
    d=json.load(open(p))
    print('='*100); print(d['id'], d.get('title'), 'tempo', d['tempo_bpm'], 'pickup', d.get('pickup_beats'))
    notes=sorted(d['notes'], key=lambda n:(n['bar'],n['beat']))
    by=defaultdict(list)
    for n in notes: by[n['bar']].append(n)
    ch=defaultdict(list)
    for c in d['chords']: ch[c['bar']].append(c)
    co=defaultdict(list)
    for c in d.get('counter',[]) or []: co[c['bar']].append(c)
    acc=defaultdict(list)
    for e in d.get('accomp',{}).get('events',[]) or []: acc[e['bar']].append(e)
    bars=sorted(set(by)|set(ch))
    for b in bars:
        mel=' '.join(f"{fb(n['beat'])}:{nm(n['midi'])}({n['dur_beats']:.3g})v{n.get('vel','')}" for n in by[b])
        chs=' '.join(f"{fb(c['beat'])}:{c.get('roman',c.get('chord',''))}[{c.get('chord','')}] b={nm(c['bass']) if c.get('bass') is not None else '-'} {'/'.join(nm(x) for x in c['midi'])}" for c in ch[b])
        print(f"bar {b:2d} | MEL {mel}")
        print(f"       | CH  {chs}")
        if co[b]: print(f"       | CTR "+' '.join(f"{fb(n['beat'])}:{nm(n['midi'])}({n['dur_beats']:.3g})" for n in co[b]))
        if acc[b]: print(f"       | ACC "+' '.join(f"{fb(e['beat'])}:{e.get('role','')}:{'/'.join(nm(x) for x in (e['midi'] if isinstance(e['midi'],list) else [e['midi']]))}" for e in acc[b]))
    ms=[n['midi'] for n in notes]
    iv=[b-a for a,b in zip(ms,ms[1:])]
    import collections
    steps=sum(1 for i in iv if abs(i) in (1,2)); th=sum(1 for i in iv if abs(i) in (3,4)); lp=sum(1 for i in iv if abs(i)>=5); rp=sum(1 for i in iv if i==0)
    trip=sum(1 for n in notes if abs(n['dur_beats']-1/3)<0.05 or abs((n['beat']%1)-1/3)<0.05 or abs((n['beat']%1)-2/3)<0.05)
    print(f"range {nm(min(ms))}-{nm(max(ms))} = {max(ms)-min(ms)} st; n={len(ms)}; steps {steps/len(iv):.0%} thirds {th/len(iv):.0%} leaps>=4th {lp/len(iv):.0%} repeats {rp/len(iv):.0%}; triplet-ish {trip/len(ms):.0%}")
    big=[(notes[i]['bar'],notes[i]['beat'],nm(ms[i]),nm(ms[i+1]),iv[i]) for i in range(len(iv)) if abs(iv[i])>=5]
    print('leaps:',big)
    pcs=collections.Counter(NN[m%12] for m in ms); print('pcs', dict(pcs.most_common()))
