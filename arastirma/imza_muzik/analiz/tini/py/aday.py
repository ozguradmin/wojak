"""render + chain + features for one candidate timbre (analysis only)"""
import numpy as np, sys, json
sys.path.insert(0,'/tmp/claude-0/-home-user-wojak/e1bf52df-8e16-5819-ad96-6f6873ef480c/scratchpad/muzik2/analiz/tini/py')
import ozellik as O, zincir as Z
from fsr import render_layers
SR=44100
REV=dict(rt60=0.09,pd_ms=6,build_ms=4,tail_db=-30,tail_rt=1.5,lp=4000)
WIN={'C5':(0.60,1.55),'D5':(0.40,0.66),'Eb5':(0.40,0.62),'Ab5':(0.40,0.82)}
DUR={'C5':2.0,'D5':0.9,'Eb5':0.9,'Ab5':0.9}
def synth_fn(kind):
    """non-FluidR3 references: returns f(notes,total)->mono"""
    def f(notes,total):
        n=int(total*SR); out=np.zeros(n); t=np.arange(n)/SR
        for st,du,m,v in notes:
            f0=440*2**((m-69-0.23)/12); i0=int(st*SR); i1=min(n,int((st+du)*SR))
            tt=np.arange(i1-i0)/SR; env=np.minimum(1,tt/0.03)*np.minimum(1,(du-tt)/0.03).clip(0)
            sig=np.zeros(len(tt))
            for det in ([-10,10] if '2' in kind else [0]):
                ff=f0*2**(det/1200); ph=np.random.default_rng(int(m)+det).uniform(0,6.28)
                for k in range(1,int(9000/ff)):
                    if kind.startswith('sq'): a=(1/k if k%2 else 0)
                    elif kind.startswith('pulse'): a=abs(np.sin(np.pi*k*0.40))/k
                    elif kind.startswith('saw'): a=1/k
                    elif kind.startswith('clar'): a=(1/k if k%2 else 0.25/k)
                    else: a=1/k
                    sig+=a*np.sin(2*np.pi*k*ff*tt+ph*k)
            out[i0:i1]+=0.05*sig*env*(v/100)
        return out
    return f
def render_cand(layers,notes,total):
    if isinstance(layers,str): return synth_fn(layers)(notes,total)
    return render_layers(layers,notes,total)
def evaluate(layers,orig,chain_kw=None,keep=False):
    chain_kw=chain_kw or dict(wow_c=4.5,wet_db=-8,rev=REV)
    prof={};res={}
    for nm,(f0,m) in O.NOTES.items():
        x=render_cand(layers,[(0.05,DUR[nm],m,100)],DUR[nm]+0.3)
        if np.max(np.abs(x))<1e-6: return None
        y=Z.chain(x,**chain_kw); mid=y.mean(1)
        a,b=WIN[nm]; f0c,p=O.profile(mid,a,b,f0); prof[nm]=(f0c,p)
        if nm=='C5':
            res['am'],res['fm']=O.am_fm(mid,a,b,f0c); res['centroid']=O.centroid(mid,a,b)
            if keep: res['c5_audio']=y
    tp={k:(v[0],{int(kk):vv for kk,vv in v[1].items()}) for k,v in orig['prof'].items()}
    res['env_rms'],res['eq_corr']=O.env_fit(tp,prof)
    res['oe']=float(np.mean([O.oe_index(v[1]) for v in prof.values()]))
    res['prof']={k:{kk:round(float(vv),1) for kk,vv in v[1].items()} for k,v in prof.items()}
    # combined distance (dB-ish units)
    res['d_oe']=abs(res['oe']-orig['oe']); res['d_am']=abs(res['am']-orig['am']); res['d_fm']=abs(res['fm']-orig['fm'])/3; res['d_cen']=abs(np.log2(res['centroid']/orig['centroid']))*12
    res['score']=res['env_rms']+0.5*res['d_oe']+1.0*res['d_am']+0.5*res['d_fm']
    return res
