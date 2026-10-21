"""20 ms level (all band / 250-500 / 1-4k) of original vs candidate, with beat grids"""
import numpy as np, soundfile as sf, scipy.signal as ss, sys, json, matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
O="/tmp/claude-0/-home-user-wojak/e1bf52df-8e16-5819-ad96-6f6873ef480c/scratchpad/muzik/orijinal.wav"
out=sys.argv[1]; cand=sys.argv[2]; bpm=float(sys.argv[3]) if len(sys.argv)>3 else 154; t1=float(sys.argv[4]) if len(sys.argv)>4 else 0.0
def lev(x,sr,lo=None,hi=None):
    m=x.mean(1) if x.ndim>1 else x
    if lo: m=ss.sosfiltfilt(ss.butter(4,[lo,hi],'bandpass',fs=sr,output='sos'),m)
    w=int(0.02*sr); h=int(0.005*sr)
    e=np.sqrt(np.convolve(m**2,np.ones(w)/w,'same'))[::h]
    return np.arange(len(e))*h/sr, 20*np.log10(e+1e-9)
fig,ax=plt.subplots(4,1,figsize=(16,12))
for k,(path,grid0,beat) in enumerate([(O,1.036,0.39597),(cand,t1,60/bpm)]):
    x,sr=sf.read(path)
    for j,(a0,a1) in enumerate([(0,3.6),(6.5,10.1)]):
        a=ax[2*j+k]
        for lo,hi,col,lab in [(None,None,'k','all'),(250,500,'C0','250-500'),(1000,4000,'C3','1-4k')]:
            t,e=lev(x,sr,lo,hi); m=(t>=a0)&(t<=a1); a.plot(t[m],e[m]-np.median(e[(t>1)&(t<13)]),color=col,lw=0.9,label=lab)
        g=grid0-30*beat
        while g<a1:
            if g>=a0: a.axvline(g,color='g' if round((g-grid0)/beat)%3==0 else '0.7',lw=1.2 if round((g-grid0)/beat)%3==0 else 0.6)
            g+=beat
        a.set_ylim(-25,12); a.set_title(('ORIGINAL ' if k==0 else 'CANDIDATE ')+f'{a0}-{a1}s  (green = downbeats)',fontsize=9); a.grid(alpha=.3); a.legend(fontsize=7,loc='lower right')
plt.tight_layout(); plt.savefig(out,dpi=70)
