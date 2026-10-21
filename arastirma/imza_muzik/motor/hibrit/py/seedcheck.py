import sys, os, json
H=os.path.abspath(os.path.join(os.path.dirname(__file__),'..')); sys.path.insert(0,H); sys.path.insert(0,os.path.join(H,'py'))
import render as R
from olc import run
st=json.load(open(sys.argv[1])); sets=[f'{k}={json.dumps(v)}' for k,v in st['params'].items()]+sys.argv[3:]
mel=os.path.join(H,'..','..','deneme','deneme_melodi.json')
for sd in [int(x) for x in sys.argv[2].split(',')]:
    out=os.path.join(H,'wav','tune',f'seed_s{sd}.wav'); R.render(mel,out,sd,st.get('recipe','B_hohner'),sets,quiet=True)
    o=run(out,full=True); a=o['timbre']['accent_uaa']; m=o['musical']['tempo_bpm']
    s={k:v['score'] for k,v in o['timbre_subscores'].items()}
    print(sd, round(o['TIMBRE_SCORE'],1), 'acc',s['accent'],'tilt',a['value'],'lev',[round(x,1) for x in a['level_from_dark_db']],'tempo',m['value'],'| pitch',s['pitch'],'mod',s['modulation'],'st',s['stereo'],'rev',s['reverb'],'dyn',s['dynamics'],flush=True)
