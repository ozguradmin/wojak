import numpy as np, soundfile as sf, sys, json
sys.path.insert(0,'/tmp/claude-0/-home-user-wojak/e1bf52df-8e16-5819-ad96-6f6873ef480c/scratchpad/muzik2/analiz/tini/py')
import ozellik as O
S='/tmp/claude-0/-home-user-wojak/e1bf52df-8e16-5819-ad96-6f6873ef480c/scratchpad'; D=S+'/muzik2/analiz/tini'
y,sr=sf.read(S+'/muzik/orijinal.wav'); x=y.mean(1)
prof={}
for nm,(a,b) in O.ORIG_WIN.items():
    f0,p=O.profile(x,a,b,O.NOTES[nm][0]); prof[nm]=(f0,p); print(nm,round(f0,1),{k:round(v,1) for k,v in p.items()},'OE',round(O.oe_index(p),1))
am,fm=O.am_fm(x,11.75,12.70,prof['C5'][0]); cen=O.centroid(x,11.75,12.70)
print('C5 AM std',round(am,2),'FM std',round(fm,1),'centroid',round(cen))
json.dump(dict(prof={k:[v[0],{str(kk):vv for kk,vv in v[1].items()}] for k,v in prof.items()},am=am,fm=fm,centroid=cen,oe=float(np.mean([O.oe_index(v[1]) for v in prof.values()]))),open(D+'/orig_feat.json','w'),indent=1)
