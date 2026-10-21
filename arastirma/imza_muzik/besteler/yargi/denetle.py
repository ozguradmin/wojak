import json, sys
NN=['C','Db','D','Eb','E','F','F#','G','Ab','A','Bb','B']
def nm(m): return f"{NN[m%12]}{m//12-1}"
def T(bar,beat): return 3*bar+beat-1
def run(p):
    d=json.load(open(p))
    notes=sorted(d['notes'],key=lambda n:T(n['bar'],n['beat']))
    chords=sorted(d['chords'],key=lambda c:T(c['bar'],c['beat']))
    ctr=sorted(d.get('counter') or [],key=lambda n:T(n['bar'],n['beat']))
    def chord_at(t):
        cur=None
        for c in chords:
            if T(c['bar'],c['beat'])<=t+1e-6: cur=c
        return cur
    def ctr_at(t):
        for n in ctr:
            s=T(n['bar'],n['beat'])
            if s<=t+1e-6< s+n['dur_beats']: return n['midi']
        return None
    print('='*90); print(d['id'])
    # melody vs chord
    for i,n in enumerate(notes):
        t=T(n['bar'],n['beat']); c=chord_at(t)
        pcs={m%12 for m in c['midi']}|({c['bass']%12} if c.get('bass') is not None else set())
        if n['midi']%12 not in pcs:
            prev=notes[i-1]['midi'] if i>0 else None; nxt=notes[i+1]['midi'] if i+1<len(notes) else None
            a=None if prev is None else n['midi']-prev; b=None if nxt is None else nxt-n['midi']
            kind='?'
            if a is not None and b is not None:
                if abs(a) in (1,2) and abs(b) in (1,2): kind='passing' if a*b>0 else 'neighbour'
                elif a==0: kind='suspension/repeat-dissonance'
                elif abs(b) in (1,2): kind='appoggiatura(leap in, step out)' if abs(a)>2 else kind
                elif b==0: kind='anticipation-like (repeated next)'
                else: kind='FREE (leap in & out)'
            strong = (n['beat']%1==0)
            semis=[ (n['midi']-m)%12 for m in c['midi']]
            m9 = any(s==1 for s in semis)
            print(f"  NCT bar {n['bar']} beat {n['beat']:.3g} {nm(n['midi'])} over {c.get('roman',c.get('chord'))} {[nm(m) for m in c['midi']]} in:{a} out:{b} -> {kind}{' STRONG' if strong else ''}{' (b9 vs a chord tone)' if m9 else ''} dur {n['dur_beats']:.3g}")
    # outer voice parallels: sample at each beat & triplet onset
    evs=sorted(set([T(n['bar'],n['beat']) for n in notes]+[T(c['bar'],c['beat']) for c in chords]))
    def mel_at(t):
        cur=None
        for n in notes:
            s=T(n['bar'],n['beat'])
            if s<=t+1e-6< s+n['dur_beats']+1e-6: cur=n['midi']
        return cur
    prev=None
    for t in evs:
        m=mel_at(t); c=chord_at(t)
        if m is None or c is None or c.get('bass') is None: prev=None; continue
        b=c['bass']; cur=(m,b,t)
        if prev and (prev[0]!=m or prev[1]!=b):
            i1=(prev[0]-prev[1])%12; i2=(m-b)%12
            dm=m-prev[0]; db=b-prev[1]
            if i1==i2 and i1 in (0,7) and dm!=0 and db!=0 and (dm>0)==(db>0):
                print(f"  PARALLEL {'8ve' if i1==0 else '5th'} melody/bass at beat {prev[2]:.3g}->{t:.3g}: {nm(prev[0])}/{nm(prev[1])} -> {nm(m)}/{nm(b)}")
            elif i2 in (0,7) and dm!=0 and db!=0 and (dm>0)==(db>0) and abs(dm)>2:
                print(f"  hidden {'8ve' if i2==0 else '5th'} (melody leaps) at {prev[2]:.3g}->{t:.3g}: {nm(prev[0])}/{nm(prev[1])} -> {nm(m)}/{nm(b)}")
        prev=cur
    # melody vs counter: parallels and semitone/unison clashes
    if ctr:
        prev=None
        for t in sorted(set(evs+[T(n['bar'],n['beat']) for n in ctr])):
            m=mel_at(t); k=ctr_at(t)
            if m is None or k is None: prev=None; continue
            iv=(m-k)
            if iv<0: print(f"  CROSSING melody {nm(m)} below counter {nm(k)} at {t:.3g}")
            if iv%12 in (1,11) or iv%12==2 and False: print(f"  clash m{nm(m)}/ctr{nm(k)} ({iv} st) at beat {t:.3g}")
            if prev and (prev[0]!=m or prev[1]!=k):
                i1=(prev[0]-prev[1])%12; i2=iv%12; dm=m-prev[0]; dk=k-prev[1]
                if i1==i2 and i1 in (0,7) and dm!=0 and dk!=0 and (dm>0)==(dk>0):
                    print(f"  PARALLEL {'8ve/unison' if i1==0 else '5th'} melody/counter {prev[2]:.3g}->{t:.3g}: {nm(prev[0])}/{nm(prev[1])} -> {nm(m)}/{nm(k)}")
            prev=(m,k,t)
    # counter vs chord clash
    for n in ctr:
        t=T(n['bar'],n['beat']); c=chord_at(t)
        pcs={x%12 for x in c['midi']}|({c['bass']%12} if c.get('bass') is not None else set())
        if n['midi']%12 not in pcs: print(f"  counter NCT bar {n['bar']} b{n['beat']} {nm(n['midi'])} over {c.get('roman')} {[nm(x) for x in c['midi']]}")
    # last note timing
    last=notes[-1]; print(f"  final note {nm(last['midi'])} start bar {last['bar']} beat {last['beat']:.3g} t={ (3*last['bar']+last['beat']-2)*60/d['tempo_bpm']:.3f}s dur {last['dur_beats']:.3g} ends {(3*last['bar']+last['beat']-2+last['dur_beats'])*60/d['tempo_bpm']:.3f}s")
for p in sys.argv[1:]: run(p)
