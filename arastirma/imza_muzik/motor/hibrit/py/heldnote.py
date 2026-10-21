"""held-tonic timbre (tini method): harmonic profile, odd-even index, AM std, centroid of the final held C5,
original window 11.75-12.70 s vs candidate window given (default 12.0-12.95)."""
import sys, numpy as np, soundfile as sf
sys.path.insert(0,'/tmp/claude-0/-home-user-wojak/e1bf52df-8e16-5819-ad96-6f6873ef480c/scratchpad/muzik2/analiz/tini/py')
import ozellik as O
OR="/tmp/claude-0/-home-user-wojak/e1bf52df-8e16-5819-ad96-6f6873ef480c/scratchpad/muzik/orijinal.wav"
def feat(path,a,b,f0g=516.3):
    x,sr=sf.read(path); m=x.mean(1)
    f0,p=O.profile(m,a,b,f0g); am,fm=O.am_fm(m,a,b,f0); c=O.centroid(m,a,b)
    return f0,p,O.oe_index(p),am,fm,c
for name,path,a,b in [('orig',OR,11.75,12.70)]+[(p.split('/')[-1],p,float(sys.argv[2]) if len(sys.argv)>2 else 12.0,float(sys.argv[3]) if len(sys.argv)>3 else 12.95) for p in sys.argv[1:2]]:
    f0,p,oe,am,fm,c=feat(path,a,b)
    print(f"{name:22s} f0 {f0:6.1f}  h1-8 {' '.join(f'{p[k]:5.1f}' for k in sorted(p)[:8])}  odd-even {oe:5.1f}  AM {am:4.2f} dB  FM {fm:4.1f} c  centroid {c:5.0f}")
