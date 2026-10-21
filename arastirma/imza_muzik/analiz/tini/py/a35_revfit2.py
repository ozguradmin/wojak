import numpy as np, soundfile as sf, sys, json, itertools
sys.path.insert(0,'/tmp/claude-0/-home-user-wojak/e1bf52df-8e16-5819-ad96-6f6873ef480c/scratchpad/muzik2/analiz/tini/py')
import zincir as Z; from olc import stereo_stats, sysid_curve
S='/tmp/claude-0/-home-user-wojak/e1bf52df-8e16-5819-ad96-6f6873ef480c/scratchpad'; D=S+'/muzik2/analiz/tini'
T=json.load(open(D+'/revfit.json'))['orig']
x=np.load(D+'/probe_dry.npy')
def score(st):
    return sum((st[k]-T[k])**2 for k in T if k.startswith('sm_'))/4 + sum(((st[k]-T[k])*20)**2 for k in T if k.startswith('coh_'))/4 + sum((st[k]-T[k])**2 for k in T if k.startswith('ir_'))/9
res=[]
for rt,wet,bld,tail,trt,lp in itertools.product([0.08,0.12,0.18],[-9,-6,-4],[3,8],[-28,-22],[1.0,2.0],[2500,4000]):
    yy=Z.chain(x,wow_c=4.5,wet_db=wet,rev=dict(rt60=rt,build_ms=bld,tail_db=tail,tail_rt=trt,lp=lp),noise=False)
    st=stereo_stats(yy); c,_=sysid_curve(yy); st.update(c); res.append((score(st),rt,wet,bld,tail,trt,lp,st))
res.sort(key=lambda r:r[0])
for r in res[:6]: print(round(r[0],1),'rt',r[1],'wet',r[2],'build',r[3],'tail',r[4],'tail_rt',r[5],'lp',r[6],{k:round(v,2) for k,v in r[7].items()})
json.dump([dict(err=r[0],rt60=r[1],wet_db=r[2],build_ms=r[3],tail_db=r[4],tail_rt=r[5],lp=r[6],stats=r[7]) for r in res[:6]],open(D+'/revfit2.json','w'),indent=1)
