"""render all probes + test melody with the given state, run olcum, overlay CQT with notes."""
import sys, os, json, subprocess, glob
H=os.path.abspath(os.path.join(os.path.dirname(__file__),'..')); sys.path.insert(0,H); sys.path.insert(0,os.path.join(H,'py'))
import render as R
from olc import run, line
st=json.load(open(sys.argv[1])) if len(sys.argv)>1 and sys.argv[1].endswith('.json') else {'params':{}}
sets=[f'{k}={json.dumps(v)}' for k,v in st.get('params',{}).items()]
recipe=st.get('recipe',R.DEFAULT_RECIPE); tag=sys.argv[2] if len(sys.argv)>2 else 'p'
mels=[os.path.join(H,'..','..','deneme','deneme_melodi.json')]+sorted(glob.glob(os.path.join(H,'probes','*.json')))
for m in mels:
    nm=os.path.basename(m)[:-5]; out=os.path.join(H,'wav',f'{tag}_{nm}.wav')
    info=R.render(m,out,1,recipe,sets,quiet=True)
    o=run(out, os.path.join(H,'png',f'{tag}_{nm}_olcum.png'), full=True)
    T=o['technical']
    print(f"{nm:16s} {line({'TIMBRE_SCORE':o['TIMBRE_SCORE'],'sub':{k:v['score'] for k,v in o['timbre_subscores'].items()}})}")
    print(f"{'':16s} LUFS {T['lufs_integrated']['value']} TP {T['true_peak_dbtp']['value']} first {T['first_sound_s']['value']} last {T['last_sound_s']['value']} tail {T['tail_end_s']['value']} clicks {T['clicks']['value']} clip {T['clip_samples']['value']} tempo {o['musical']['tempo_bpm']['value']} key {o['musical']['key']['value']} cminor_r {o['musical']['key']['c_minor_r']}")
    subprocess.run(['python3',os.path.join(H,'py','rollcheck.py'),m,out,os.path.join(H,'png',f'{tag}_{nm}_roll.png')])
