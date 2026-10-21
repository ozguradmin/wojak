import sys, os, json, itertools, numpy as np
sys.argv=[sys.argv[0],'auto','tune/state_B2.json','room_wet_db=-9','room_build_ms=2']
exec(open('py/roomfit2.py').read().split("grid={")[0])
res=[]
for pd,hold,rt,tl in itertools.product([4,7,10],[0,8,14,20],[0.03,0.04,0.05,0.07],[-45,-38]):
    Q=dict(P); Q.update(room_pd_ms=pd,room_hold_ms=hold,room_rt60=rt,room_tail_db=tl)
    sc,s,d_ir,d_st=ev(Q); res.append((sc,pd,hold,rt,tl,d_ir,d_st,np.round(s['ir_env_db'],1).tolist()))
res.sort(reverse=True)
for r in res[:8]: print(r)
