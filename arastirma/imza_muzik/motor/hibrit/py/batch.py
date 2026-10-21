"""python3 py/batch.py STATE.json NAME 'k=v k=v' NAME2 '...'  -> paired 2-seed evals on top of STATE params (2 workers)"""
import sys, os, json
sys.path.insert(0,os.path.dirname(__file__))
from tune import evaluate, tosets, MEL
from concurrent.futures import ProcessPoolExecutor
st=json.load(open(sys.argv[1])); base=tosets(st['params']); recipe=st.get('recipe','B_hohner')
args=sys.argv[2:]; seeds=[1,2]
if args and args[0].startswith('--seeds='): seeds=[int(x) for x in args[0][8:].split(',')]; args=args[1:]
with ProcessPoolExecutor(max_workers=2) as pool:
    for name,extra in zip(args[0::2],args[1::2]):
        ex=extra.split() if extra.strip() else []
        rec=recipe
        for e in list(ex):
            if e.startswith('recipe='): rec=e[7:]; ex.remove(e)
        ts,sub=evaluate(pool,base+ex,seeds,rec,name,MEL)
        print(f"{name:18s} {ts:6.2f} | "+" ".join(f"{k[:5]}={v:.0f}" for k,v in sub.items()),flush=True)
        open(os.path.join(os.path.dirname(__file__),'..','batch_log.jsonl'),'a').write(json.dumps({'name':name,'extra':ex,'recipe':rec,'ts':ts,'sub':sub,'base':st['params']})+'\n')
