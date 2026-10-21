"""LTAS match EQ (1/3-octave smoothed) toward the original's measured LTAS (tini.json eq_curve). Analysis/test helper."""
import numpy as np, scipy.signal as ss, json, sys
sys.path.insert(0,'/tmp/claude-0/-home-user-wojak/e1bf52df-8e16-5819-ad96-6f6873ef480c/scratchpad/muzik2/analiz/tini/py')
from chain import third_oct, TO
SR=44100
def match_fir(y,target_rel,bands=TO,fmin=200,fmax=8000,max_boost=12,n=8193):
    m=y.mean(1) if y.ndim>1 else y
    L=third_oct(m,SR); Lr=L-np.nanmax(L)
    g=np.array(target_rel)-Lr
    sel=(bands>=fmin)&(bands<=fmax)
    g=np.where(sel,g,np.nan)
    # outside range: hold edge values below fmin, steep fall above fmax handled by target itself
    gi=np.interp(np.log2(bands),np.log2(bands[sel]),g[sel])
    gi=np.clip(gi-np.median(gi[sel]),-40,max_boost)
    # 3-point smoothing (>= 1/3 octave)
    gs=np.convolve(np.r_[gi[0],gi,gi[-1]],[0.25,0.5,0.25],'valid')
    ff=np.linspace(0,SR/2,4097); gg=np.interp(np.log2(np.clip(ff,15,None)),np.log2(bands),gs)
    return ss.firwin2(n,ff/(SR/2),10**(gg/20)),list(zip(bands.tolist(),gs.round(2).tolist()))
def apply(y,fir):
    z=ss.fftconvolve(y,fir[:,None] if y.ndim>1 else fir,mode='full',axes=0)[len(fir)//2:len(fir)//2+len(y)]
    return z
