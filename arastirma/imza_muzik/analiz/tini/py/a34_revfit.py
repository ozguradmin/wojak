import numpy as np, soundfile as sf, sys, json, itertools
sys.path.insert(0,'/tmp/claude-0/-home-user-wojak/e1bf52df-8e16-5819-ad96-6f6873ef480c/scratchpad/muzik2/analiz/tini/py')
from fsr import render_layers; import zincir as Z; from olc import stereo_stats, sysid_curve
S='/tmp/claude-0/-home-user-wojak/e1bf52df-8e16-5819-ad96-6f6873ef480c/scratchpad'; D=S+'/muzik2/analiz/tini'
y,sr=sf.read(S+'/muzik/orijinal.wav'); y=y[:int(13.73*sr)]
T=stereo_stats(y); Tc,_=sysid_curve(y); T.update(Tc)
print('ORIG',{k:round(v,2) for k,v in T.items()})
# probe: generic C-minor material, beat 0.387
b=0.387; notes=[]
chords=[[60,63,67],[62,65,68],[60,63,67],[59,62,65,67]]*3
for i,ch in enumerate(chords):
    t0=i*3*b
    for m in ch: notes.append((t0+b,0.13,m,80)); notes.append((t0+2*b,0.13,m,80))
    notes.append((t0,0.35,ch[0]-12,85))
mel=[72,74,75,77,79,77,75,74,72,71,72,74,75,74,72,72]
for i,m in enumerate(mel): notes.append((3*b*1+i*1.5*b,1.5*b+0.02,m,100))
x=render_layers([dict(prog=21)],notes,13.8)
np.save(D+'/probe_dry.npy',x)
res=[]
for rt,wet,bld,tail in itertools.product([0.2,0.3,0.45,0.7],[-6,-3,-1,1],[4,10],[-30,-22]):
    yy=Z.chain(x,wow_c=4.5,wet_db=wet,rev=dict(rt60=rt,build_ms=bld,tail_db=tail),noise=False)
    st=stereo_stats(yy); c,_=sysid_curve(yy); st.update(c)
    err=sum((st[k]-T[k])**2 for k in T if k.startswith('sm_'))/4 + sum(((st[k]-T[k])*20)**2 for k in T if k.startswith('coh_'))/4 + sum((st[k]-T[k])**2 for k in T if k.startswith('ir_'))/9
    res.append((err,rt,wet,bld,tail,st))
res.sort(key=lambda r:r[0])
for r in res[:6]: print(round(r[0],1),'rt',r[1],'wet',r[2],'build',r[3],'tail',r[4],{k:round(v,2) for k,v in r[5].items()})
json.dump(dict(orig=T,best=[dict(err=r[0],rt60=r[1],wet_db=r[2],build_ms=r[3],tail_db=r[4],stats=r[5]) for r in res[:6]]),open(D+'/revfit.json','w'),indent=1)
