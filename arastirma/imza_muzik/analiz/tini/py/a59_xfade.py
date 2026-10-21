import numpy as np, scipy.signal as ss, sys
sys.path.insert(0,'/tmp/claude-0/-home-user-wojak/e1bf52df-8e16-5819-ad96-6f6873ef480c/scratchpad/muzik2/analiz/tini/py')
from aday import REV, render_cand; import zincir as Z
sr=44100; b=0.387
L=[dict(prog=22),dict(prog=22,detune_c=20,gain_db=-3)]
def env_db(v,lo=450,hi=3000):
    bb=ss.sosfiltfilt(ss.butter(4,[lo,hi],'bandpass',fs=sr,output='sos'),v)
    return 20*np.log10(np.sqrt(ss.sosfiltfilt(ss.butter(2,30,fs=sr,output='sos'),bb**2).clip(1e-14)))
def dips(e,times):
    o=[]
    for tc in times:
        i=int(tc*sr); w=int(0.05*sr); o.append(e[i-w:i+w].min()-np.r_[e[i-3*w:i-w],e[i+w:i+3*w]].mean())
    return np.array(o)
notes=[(0.30,2*b,72),(0.30+2*b,b,74),(0.30+3*b,2*b,75)]
# (a) plain FluidR3 retrigger
xa=render_cand(L,[(s,d+0.02,m,100) for s,d,m in notes],2.2)
# (b) per-note render with long sustain, equal-power crossfade 40 ms at boundaries
xf=0.04; n=int(2.2*sr); xb=np.zeros(n)
for i,(s,d,m) in enumerate(notes):
    seg=render_cand(L,[(0.0,d+0.3,m,100)],d+0.5)
    i0=int(s*sr); g=np.ones(len(seg))
    if i>0:  # fade in over xf (start xf/2 before boundary)
        k=int(xf*sr); g[:k]=np.sin(np.linspace(0,np.pi/2,k)); i0-=k//2
    if i<len(notes)-1:
        k=int(xf*sr); e0=int((d)*sr)+k//2; g[e0:e0+k]*=np.cos(np.linspace(0,np.pi/2,k))[:len(g[e0:e0+k])]; g[e0+k:]=0
    else:
        g[int((d+0.25)*sr):]=0
    seg=seg*g; xb[i0:i0+len(seg)]+=seg[:n-i0]
for lab,x in [('retrigger',xa),('xfade40',xb)]:
    y=Z.chain(x,wow_c=4.5,wet_db=-8,rev=REV,noise=False); e=env_db(y.mean(1))
    tr=dips(e,[0.30+2*b,0.30+3*b]); rnd=dips(e,np.r_[np.linspace(0.55,0.95,6),np.linspace(1.62,2.0,5)])
    print(f'{lab}: transition dips {np.round(tr,1)}  random-time baseline median {np.median(rnd):.1f}')
