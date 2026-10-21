import sys, os, json, numpy as np
H=os.path.abspath(os.path.join(os.path.dirname(__file__),'..')); sys.path.insert(0,H)
sys.path.insert(0,'/tmp/claude-0/-home-user-wojak/e1bf52df-8e16-5819-ad96-6f6873ef480c/scratchpad/muzik2/olcum')
import render as R, olcum as O
ORIG=np.array([-3.67,-0.755,-2.588,-16.816,-26.515,-31.446,-35.373,-38.394,-30.931])
st=json.load(open(sys.argv[1])); sets=[f'{k}={json.dumps(v)}' for k,v in st['params'].items()]
P0=R.make_params(st.get('recipe','B_hohner'),sets)
mel=os.path.join(H,'..','..','deneme','deneme_melodi.json'); S=R.load_score(mel)
R.S_GRID.update({'beat_s':S['beat_s'],'bar1_s':R.tsec(S,0.0)})
dry=R.render_parts(R.build_parts(S,P0,np.random.default_rng(1)),P0,1)
for name,mod in [('full',{}),('wow_pre',{'wow_pre':1}),('no wow',{'wow_c':0,'wow_rand_c':0,'flutter_c':0}),('no medium',{'medium_db':-120,'sbr_db':-120}),('no match',{'match':0}),('no lf/hum',{'lf_noise_db':-130,'hum':[],'rumble_db':-130}),('none',{'wow_c':0,'wow_rand_c':0,'flutter_c':0,'medium_db':-120,'sbr_db':-120,'match':0,'lf_noise_db':-130,'hum':[],'rumble_db':-130})]:
    P=dict(P0); P.update(mod); y,_=R.chain(dry,P,1)
    a0,a1,_,_=O.active_region(y,None); s=O.stereo_room(y,a0,a1); ir=np.array(s['ir_env_db'])
    d=np.sqrt(np.mean((np.maximum(ir,-40)-np.maximum(ORIG,-40))**2))
    print(f"{name:10s} lr {s['lr_corr']:.3f} sm {s['side_mid_db']:.2f} d_ir {d:.2f} ir {np.round(ir,1).tolist()}",flush=True)
