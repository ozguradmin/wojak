import numpy as np, sys, json, itertools
sys.path.insert(0,'/tmp/claude-0/-home-user-wojak/e1bf52df-8e16-5819-ad96-6f6873ef480c/scratchpad/muzik2/analiz/tini/py')
import zincir as Z; from olc import stereo_stats, sysid_curve
D='/tmp/claude-0/-home-user-wojak/e1bf52df-8e16-5819-ad96-6f6873ef480c/scratchpad/muzik2/analiz/tini'
T=json.load(open(D+'/revfit.json'))['orig']; x=np.load(D+'/probe_dry.npy')
def score(st):
    a=sum((st[k]-T[k])**2 for k in T if k.startswith('sm_'))/4; b=sum(((st[k]-T[k])*20)**2 for k in T if k.startswith('coh_'))/4; c=sum((st[k]-T[k])**2 for k in T if k.startswith('ir_'))/9
    return a+b+c,a,b,c
res=[]
for pd,rt,wet,lp,tail in itertools.product([2,6,10],[0.09,0.12],[-8,-6.5],[3000,4000],[-30,-26]):
    yy=Z.chain(x,wow_c=4.5,wet_db=wet,rev=dict(rt60=rt,pd_ms=pd,build_ms=4,tail_db=tail,tail_rt=1.5,lp=lp),noise=False)
    st=stereo_stats(yy); c,_=sysid_curve(yy); st.update(c); res.append((score(st),pd,rt,wet,lp,tail,st))
res.sort(key=lambda r:r[0][0])
for r in res[:5]: print([round(v,1) for v in r[0]],'pd',r[1],'rt',r[2],'wet',r[3],'lp',r[4],'tail',r[5],{k:round(v,2) for k,v in r[6].items()})
json.dump([dict(err=r[0],pd_ms=r[1],rt60=r[2],wet_db=r[3],lp=r[4],tail_db=r[5],tail_rt=1.5,build_ms=4,stats=r[6]) for r in res[:5]],open(D+'/revfit3.json','w'),indent=1)
