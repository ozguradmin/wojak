import numpy as np, sys, json
sys.path.insert(0,'/tmp/claude-0/-home-user-wojak/e1bf52df-8e16-5819-ad96-6f6873ef480c/scratchpad/muzik2/analiz/tini/py')
from aday import evaluate
D='/tmp/claude-0/-home-user-wojak/e1bf52df-8e16-5819-ad96-6f6873ef480c/scratchpad/muzik2/analiz/tini'
orig=json.load(open(D+'/orig_feat.json'))
rows=[]
for base,lab in [(22,'harm'),(71,'clar'),(23,'tango')]:
    for det in [14,20,26]:
        for g in [0,-3]:
            L=[dict(prog=base),dict(prog=22 if base==23 else base,detune_c=det,gain_db=g-(2 if base==23 else 0))]
            r=evaluate(L,orig); rows.append((r['score'],lab,det,g,r['env_rms'],r['oe'],r['am'],r['fm'],r['centroid']))
            print(f'{lab:6} det {det:3d} g {g:3d}: score {r["score"]:5.2f} env {r["env_rms"]:4.2f} oe {r["oe"]:5.1f} am {r["am"]:4.2f} fm {r["fm"]:5.1f} cen {r["centroid"]:5.0f}',flush=True)
json.dump(rows,open(D+'/grid.json','w'))
