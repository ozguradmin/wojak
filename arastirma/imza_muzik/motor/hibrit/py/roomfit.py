import sys, os, glob, json, numpy as np, scipy.signal as ss
H=os.path.abspath(os.path.join(os.path.dirname(__file__),'..')); sys.path.insert(0,H)
sys.path.insert(0,'/tmp/claude-0/-home-user-wojak/e1bf52df-8e16-5819-ad96-6f6873ef480c/scratchpad/muzik2/olcum')
import render as R, olcum as O
ORIG={'lr':0.643,'sm':-6.622,'ir':np.array([-3.67,-0.755,-2.588,-16.816,-26.515,-31.446,-35.373,-38.394,-30.931])}
dry=np.load(sys.argv[1])[:int(13.75*R.SR)]
def ev(P):
    rng=np.random.default_rng(1001); h=R.room_ir(P,rng); g=R.db2a(P['room_wet_db']); n=len(dry)
    y=np.stack([dry+g*ss.fftconvolve(dry,h[:,0])[:n],dry+g*ss.fftconvolve(dry,h[:,1])[:n]],1)
    y=ss.sosfilt(ss.butter(4,250,'highpass',fs=R.SR,output='sos'),y,axis=0)
    st=O.stereo_room(y,int(0.1*R.SR),n-int(0.1*R.SR))
    ir=np.maximum(np.array(st['ir_env_db']),-40); d_ir=np.sqrt(np.mean((ir-np.maximum(ORIG['ir'],-40))**2))
    d_st=abs(st['lr_corr']-ORIG['lr'])/0.15+abs(max(st['side_mid_db'],-30)-ORIG['sm'])/3
    sc=O.cauchy(d_st,1.0)*6+O.cauchy(d_ir,6.0)*6
    return sc,st,d_ir,d_st
P=R.make_params('B_hohner',[])
grid={'room_wet_db':[-14,-12,-10,-8,-6],'room_pd_ms':[2,5,8,11,14],'room_build_ms':[2,4,7,10],'room_hold_ms':[0,5,10,15],'room_rt60':[0.05,0.07,0.09,0.12,0.16],
      'room_tail_db':[-45,-38,-32,-26],'room_tail_rt':[0.3,0.6,1.0,1.5],'room_lp':[2000,3000,4500],'room_hp':[150,300]}
best=ev(P)[0]; print('start',best)
for it in range(2):
    for k,vals in grid.items():
        res=[]
        for v in vals:
            Q=dict(P); Q[k]=v; res.append((ev(Q)[0],v))
        sc,v=max(res); 
        if sc>=best: best=sc; P[k]=v
        print(it,k,P[k],round(best,1),flush=True)
sc,st,d_ir,d_st=ev(P)
print(json.dumps({k:P[k] for k in grid}), 'score/1200', round(sc,1), 'lr',round(st['lr_corr'],3),'sm',round(st['side_mid_db'],2),'ir',np.round(st['ir_env_db'],1).tolist(),'d_ir',round(d_ir,2),'d_st',round(d_st,2))
