"""room fit with the medium stage included: python3 py/roomfit2.py DRY.npy STATE.json"""
import sys, os, json, numpy as np, scipy.signal as ss
H=os.path.abspath(os.path.join(os.path.dirname(__file__),'..')); sys.path.insert(0,H)
sys.path.insert(0,'/tmp/claude-0/-home-user-wojak/e1bf52df-8e16-5819-ad96-6f6873ef480c/scratchpad/muzik2/olcum')
import render as R, olcum as O
ORIG={'lr':0.643,'sm':-6.622,'ir':np.array([-3.67,-0.755,-2.588,-16.816,-26.515,-31.446,-35.373,-38.394,-30.931])}
st=json.load(open(sys.argv[2])); sets=[f'{k}={json.dumps(v)}' for k,v in st['params'].items()]+sys.argv[3:]
P=R.make_params(st.get('recipe','B_hohner'),sets)
MEL=os.path.abspath(os.path.join(H,'..','..','deneme','deneme_melodi.json'))
if sys.argv[1]=='auto':
    S=R.load_score(MEL); rng=np.random.default_rng(1); R.S_GRID.update({'beat_s':S['beat_s'],'bar1_s':R.tsec(S,0.0)})
    dry=R.render_parts(R.build_parts(S,P,rng),P,1)
else: dry=np.load(sys.argv[1])
dry=dry[:int(13.75*R.SR)]
def ev(P):
    rng=np.random.default_rng(int(P['room_seed'])); h=R.room_ir(P,rng); g=R.db2a(P['room_wet_db']); n=len(dry)
    y=np.stack([dry+g*ss.fftconvolve(dry,h[:,0])[:n],dry+g*ss.fftconvolve(dry,h[:,1])[:n]],1)
    y=ss.sosfilt(ss.butter(4,250,'highpass',fs=R.SR,output='sos'),y,axis=0)
    y=ss.sosfilt(ss.butter(10,4800,'lowpass',fs=R.SR,output='sos'),y,axis=0)
    y=R.medium(y,P,np.random.default_rng(5))
    s=O.stereo_room(y,int(0.1*R.SR),n-int(0.1*R.SR))
    ir=np.maximum(np.array(s['ir_env_db']),-40); d_ir=np.sqrt(np.mean((ir-np.maximum(ORIG['ir'],-40))**2))
    d_st=abs(s['lr_corr']-ORIG['lr'])/0.15+abs(max(s['side_mid_db'],-30)-ORIG['sm'])/3
    return O.cauchy(d_st,1.0)*6+O.cauchy(d_ir,6.0)*6,s,d_ir,d_st
grid={'room_wet_db':[-16,-14,-13,-12,-11,-10,-9],'room_pd_ms':[5,8,11,14],'room_build_ms':[1,2,4,7],'room_hold_ms':[0,5,10,15,20,25],
      'room_rt60':[0.03,0.04,0.05,0.065,0.08],'room_tail_db':[-50,-45,-40,-35],'room_tail_rt':[0.2,0.4,0.8,1.5],'room_lp':[2500,3000,4000]}
best,s,d_ir,d_st=ev(P); print('start',round(best,1),round(s['lr_corr'],3),round(s['side_mid_db'],2),np.round(s['ir_env_db'],1).tolist(),flush=True)
for it in range(2):
    for k,vals in grid.items():
        res=[]
        for v in vals:
            Q=dict(P); Q[k]=v; res.append((ev(Q)[0],v))
        sc,v=max(res)
        if sc>best+0.5: best=sc; P[k]=v
        print(it,k,P[k],round(best,1),flush=True)
sc,s,d_ir,d_st=ev(P)
print(json.dumps({k:P[k] for k in grid}),'score/1200',round(sc,1),'lr',round(s['lr_corr'],3),'sm',round(s['side_mid_db'],2),'ir',np.round(s['ir_env_db'],1).tolist(),'d_ir',round(d_ir,2),'d_st',round(d_st,2))
