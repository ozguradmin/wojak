import numpy as np, sys, json
sys.path.insert(0,'/tmp/claude-0/-home-user-wojak/e1bf52df-8e16-5819-ad96-6f6873ef480c/scratchpad/muzik2/analiz/tini/py')
from aday import evaluate
D='/tmp/claude-0/-home-user-wojak/e1bf52df-8e16-5819-ad96-6f6873ef480c/scratchpad/muzik2/analiz/tini'
orig=json.load(open(D+'/orig_feat.json'))
GM={0:'piano',6:'harpsichord',8:'celesta',10:'music box',11:'vibraphone',16:'drawbar organ',17:'percussive organ',18:'rock organ',19:'church organ',20:'reed organ',21:'accordion',22:'harmonica',23:'tango accordion',40:'violin',41:'viola',42:'cello',48:'strings',49:'slow strings',52:'choir aahs',53:'voice oohs',54:'synth voice',56:'trumpet',57:'trombone',60:'french horn',64:'soprano sax',65:'alto sax',66:'tenor sax',68:'oboe',69:'english horn',70:'bassoon',71:'clarinet',72:'piccolo',73:'flute',74:'recorder',75:'pan flute',78:'whistle',79:'ocarina',80:'square lead',81:'saw lead',82:'calliope',85:'voice lead',109:'bagpipe',110:'fiddle',111:'shanai'}
rows=[]
for p,nm in GM.items():
    r=evaluate([dict(prog=p)],orig)
    if r is None: print('silent',p); continue
    rows.append(dict(id=f'P{p}',name=nm,**{k:v for k,v in r.items() if k not in('prof','eq_corr')}))
    print(f"P{p:3d} {nm:16} score {r['score']:5.2f} env {r['env_rms']:5.2f} oe {r['oe']:5.1f} am {r['am']:4.2f} fm {r['fm']:5.1f} cen {r['centroid']:5.0f}",flush=True)
for kind in ['sq1','sq2','pulse2','saw2','clar2']:
    r=evaluate(kind,orig); rows.append(dict(id=kind,name='synthetic '+kind,**{k:v for k,v in r.items() if k not in('prof','eq_corr')}))
    print(f"{kind:4} {'synthetic':16} score {r['score']:5.2f} env {r['env_rms']:5.2f} oe {r['oe']:5.1f} am {r['am']:4.2f} fm {r['fm']:5.1f} cen {r['centroid']:5.0f}",flush=True)
json.dump(rows,open(D+'/singles.json','w'),indent=1)
print('ORIG oe',round(orig['oe'],1),'am',round(orig['am'],2),'fm',round(orig['fm'],1),'cen',round(orig['centroid']))
