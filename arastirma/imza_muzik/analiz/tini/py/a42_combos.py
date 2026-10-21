import numpy as np, sys, json
sys.path.insert(0,'/tmp/claude-0/-home-user-wojak/e1bf52df-8e16-5819-ad96-6f6873ef480c/scratchpad/muzik2/analiz/tini/py')
from aday import evaluate
D='/tmp/claude-0/-home-user-wojak/e1bf52df-8e16-5819-ad96-6f6873ef480c/scratchpad/muzik2/analiz/tini'
orig=json.load(open(D+'/orig_feat.json'))
C={
 'tremolo_harmonica_18c':[dict(prog=22),dict(prog=22,detune_c=18)],
 'tremolo_harmonica_22c':[dict(prog=22),dict(prog=22,detune_c=22,gain_db=-2)],
 'harmonica+tango':[dict(prog=22),dict(prog=23,gain_db=-3)],
 'tango+clarinet':[dict(prog=23),dict(prog=71,gain_db=-4)],
 'tango+clarinet+20c':[dict(prog=23),dict(prog=71,detune_c=20,gain_db=-4)],
 'accordion+clarinet':[dict(prog=21),dict(prog=71,gain_db=-4)],
 'clarinet_musette_20c':[dict(prog=71),dict(prog=71,detune_c=20,gain_db=-1)],
 'reedorgan_musette_18c':[dict(prog=20),dict(prog=20,detune_c=18,gain_db=-1)],
 'reedorgan+voiceoohs':[dict(prog=20),dict(prog=53,gain_db=-6)],
 'accordion+choir':[dict(prog=21),dict(prog=52,gain_db=-10)],
 'tango+choir':[dict(prog=23),dict(prog=52,gain_db=-10)],
 'tango+voiceoohs':[dict(prog=23),dict(prog=53,gain_db=-8)],
 'tango+accordion':[dict(prog=23),dict(prog=21,gain_db=-6)],
 'tango+harmonica18':[dict(prog=23),dict(prog=22,detune_c=18,gain_db=-4)],
 'harmonica+clarinet_20c':[dict(prog=22),dict(prog=71,detune_c=20,gain_db=-3)],
 'oboe+clarinet':[dict(prog=68),dict(prog=71,gain_db=-2)],
}
rows=[]
for k,L in C.items():
    r=evaluate(L,orig); rows.append(dict(id=k,layers=L,**{kk:v for kk,v in r.items() if kk not in('prof',)}))
    print(f"{k:24} score {r['score']:5.2f} env {r['env_rms']:5.2f} oe {r['oe']:5.1f} am {r['am']:4.2f} fm {r['fm']:5.1f} cen {r['centroid']:5.0f}",flush=True)
json.dump(rows,open(D+'/combos.json','w'),indent=1)
