import sys, os, numpy as np
H=os.path.abspath(os.path.join(os.path.dirname(__file__),'..')); sys.path.insert(0,H)
sys.path.insert(0,'/tmp/claude-0/-home-user-wojak/e1bf52df-8e16-5819-ad96-6f6873ef480c/scratchpad/muzik2/olcum')
import render as R, olcum as O
mel=sys.argv[1]
for name,sets in [('final',[]),('no peak',['peak_ceiling_dbtp=null']),('no medium',['medium_db=-120','sbr_db=-120']),('no wander',['wander_c=0','wander_acc_c=0','expr=0']),('no wow',['wow_c=0','wow_rand_c=0','flutter_c=0'])]+[(a,[a]) for a in sys.argv[2:]]:
    out=os.path.join(H,'wav','tune','click.wav'); R.render(mel,out,1,'B_hohner',sets,quiet=True)
    y=O.decode(out); a0,a1,_,_=O.active_region(y,None); c=O.clicks(y.mean(1)[a0:a1])
    print(f"{name:12s} clicks {c['count']} at {[round(t+a0/O.SR,3) for t in c['times_s']]} kurt {c['resid_kurtosis']:.1f}",flush=True)
