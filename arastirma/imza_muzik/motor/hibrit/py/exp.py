"""experiment runner: python3 py/exp.py NAME RECIPE [key=value ...] [--png] [--mel path]"""
import sys, os, json, time
H=os.path.abspath(os.path.join(os.path.dirname(__file__),'..'))
sys.path.insert(0,H); sys.path.insert(0,os.path.join(H,'py'))
os.environ.setdefault('HIBRIT_CACHE',os.path.join(H,'cache'))
import render as R
from olc import run, line
MEL=os.path.abspath(os.path.join(H,'..','..','deneme','deneme_melodi.json'))
def exp(name, recipe, sets, png=False, mel=MEL, seed=1, quiet=False):
    out=os.path.join(H,'wav',name+'.wav')
    t0=time.time(); info=R.render(mel,out,seed,recipe,sets,quiet=True); tr=time.time()-t0
    o=run(out, os.path.join(H,'png',name+'.png') if png else None)
    s=line(o)
    rec={'name':name,'recipe':recipe,'sets':sets,'TS':o['TIMBRE_SCORE'],'sub':o.get('sub'),'tp':info['true_peak_dbtp'],'render_s':round(tr,1)}
    with open(os.path.join(H,'results.jsonl'),'a') as f: f.write(json.dumps(rec)+'\n')
    if not quiet: print(f"{name:28s} {s}  tp {info['true_peak_dbtp']:.1f} ({tr:.0f}s)")
    return o
if __name__=='__main__':
    a=[x for x in sys.argv[1:] if not x.startswith('--')]
    mel=MEL; seeds=[1]
    for x in sys.argv[1:]:
        if x.startswith('--mel='): mel=x[6:]
        if x.startswith('--seeds='): seeds=[int(v) for v in x[8:].split(',')]
    import numpy as np
    tot=[]; subs=[]
    for sd in seeds:
        o=exp(a[0]+(f'_s{sd}' if len(seeds)>1 else ''),a[1],a[2:],png='--png' in sys.argv, mel=mel, seed=sd, quiet=len(seeds)>1)
        tot.append(o['TIMBRE_SCORE']); subs.append(o['sub'])
    if len(seeds)>1:
        m={k:np.mean([s[k] for s in subs]) for k in subs[0]}
        print(f"{a[0]:22s} MEAN TS {np.mean(tot):5.1f} (sd {np.std(tot):.1f}; "+','.join(f'{x:.1f}' for x in tot)+") | "+" ".join(f"{k[:5]}={v:.0f}" for k,v in m.items()))
