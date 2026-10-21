import numpy as np, sys, json
sys.path.insert(0,'/tmp/claude-0/-home-user-wojak/e1bf52df-8e16-5819-ad96-6f6873ef480c/scratchpad/muzik2/analiz/tini/py')
from aday import evaluate
D='/tmp/claude-0/-home-user-wojak/e1bf52df-8e16-5819-ad96-6f6873ef480c/scratchpad/muzik2/analiz/tini'
orig=json.load(open(D+'/orig_feat.json'))
print('ORIG'); [print(' ',k,{int(kk):round(vv,0) for kk,vv in v[1].items()}) for k,v in orig['prof'].items()]
for lab,L in [('P23',[dict(prog=23)]),('P21',[dict(prog=21)]),('P71',[dict(prog=71)]),('clar2','clar2'),('P22',[dict(prog=22)])]:
    r=evaluate(L,orig); print(lab,'env',round(r['env_rms'],2))
    for k,v in r['prof'].items(): print('  ',k,{kk:round(vv,0) for kk,vv in v.items()})
    print('   EQ corr (Hz:dB):',' '.join(f'{f:.0f}:{g:+.1f}' for f,g in r['eq_corr']))
