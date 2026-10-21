"""coordinate-descent tuner over render.py parameters; objective = mean TIMBRE_SCORE over seeds.
python3 py/tune.py STATE.json GRID.json [--seeds=1,2] [--workers=2] [--rounds=1]"""
import sys, os, json, time, itertools
from concurrent.futures import ProcessPoolExecutor
H=os.path.abspath(os.path.join(os.path.dirname(__file__),'..')); sys.path.insert(0,H); sys.path.insert(0,os.path.join(H,'py'))
os.environ.setdefault('HIBRIT_CACHE',os.path.join(H,'cache'))
MEL=os.path.abspath(os.path.join(H,'..','..','deneme','deneme_melodi.json'))
def one(args):
    import render as R
    from olc import run
    sets,seed,recipe,tag,mel=args
    out=os.path.join(H,'wav','tune',(f'{tag}' if tag in ('base','keep') else f'w{os.getpid()}')+f'_s{seed}.wav'); os.makedirs(os.path.dirname(out),exist_ok=True)
    info=R.render(mel,out,seed,recipe,sets,quiet=True)
    o=run(out)
    return o['TIMBRE_SCORE'], o['sub']
def evaluate(pool,sets,seeds,recipe,tag,mel):
    res=list(pool.map(one,[(sets,s,recipe,f'{tag}',mel) for s in seeds]))
    ts=sum(r[0] for r in res)/len(res)
    sub={k:round(sum(r[1][k] for r in res)/len(res),1) for k in res[0][1]}
    return ts,sub
def tosets(d): return [f'{k}={json.dumps(v)}' for k,v in d.items()]
if __name__=='__main__':
    st_path, grid_path = sys.argv[1], sys.argv[2]
    seeds=[1,2]; workers=2; rounds=1; mel=MEL
    for a in sys.argv[3:]:
        if a.startswith('--seeds='): seeds=[int(x) for x in a[8:].split(',')]
        if a.startswith('--workers='): workers=int(a[10:])
        if a.startswith('--rounds='): rounds=int(a[9:])
        if a.startswith('--mel='): mel=a[6:]
    st=json.load(open(st_path)); grid=json.load(open(grid_path))
    recipe=st.get('recipe','B_hohner'); cur=st['params']
    logp=os.path.join(H,'tune_log.jsonl')
    with ProcessPoolExecutor(max_workers=workers) as pool:
        if 'best_ts' not in st:
            st['best_ts'],st['best_sub']=evaluate(pool,tosets(cur),seeds,recipe,'base',mel); json.dump(st,open(st_path,'w'),indent=1)
        print('start',round(st['best_ts'],2),st['best_sub'],flush=True)
        for r in range(rounds):
            for k,vals in grid.items():
                for v in vals:
                    if json.dumps(cur.get(k))==json.dumps(v): continue
                    trial=dict(cur); trial[k]=v
                    t0=time.time(); ts,sub=evaluate(pool,tosets(trial),seeds,recipe,f'{k}',mel)
                    rec={'param':k,'value':v,'ts':round(ts,2),'sub':sub,'base':round(st['best_ts'],2),'dt':round(time.time()-t0,1)}
                    open(logp,'a').write(json.dumps(rec)+'\n')
                    flag=''
                    if ts>st['best_ts']+0.3:
                        cur=trial; st['params']=cur; st['best_ts']=ts; st['best_sub']=sub; flag='  <== keep'
                        json.dump(st,open(st_path,'w'),indent=1)
                    print(f"{k}={json.dumps(v)}: {ts:.2f} (best {st['best_ts']:.2f}){flag}",flush=True)
    print('final',json.dumps(cur),round(st['best_ts'],2),st['best_sub'])
