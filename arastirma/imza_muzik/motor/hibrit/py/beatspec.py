"""average spectrum (dB) in 0-120 ms after each beat class, original vs candidate (known grids)"""
import sys, numpy as np, soundfile as sf, matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
O="/tmp/claude-0/-home-user-wojak/e1bf52df-8e16-5819-ad96-6f6873ef480c/scratchpad/muzik/orijinal.wav"
def cls(path,d0,beat,t_end=11.4):
    x,sr=sf.read(path); m=x.mean(1); out={0:[],1:[],2:[]}
    k=-30
    while True:
        t=d0+k*beat; k+=1
        if t>t_end: break
        if t<0.05: continue
        seg=m[int(t*sr):int((t+0.12)*sr)]; X=np.abs(np.fft.rfft(seg*np.hanning(len(seg)),8192))**2
        out[(k-1)%3].append(X)
    f=np.fft.rfftfreq(8192,1/sr)
    return f,{c:10*np.log10(np.mean(v,0)+1e-20) for c,v in out.items()}
fig,ax=plt.subplots(1,2,figsize=(16,5))
for a,(p,d0,b,nm) in zip(ax,[(O,1.036,0.39597,'original'),(sys.argv[2],0.0,60/float(sys.argv[3]),'candidate')]):
    f,S=cls(p,d0,b); ref=np.max(S[1][(f>250)&(f<4000)])
    def band(s,lo,hi): sel=(f>=lo)&(f<hi); return 10*np.log10(np.mean(10**(s[sel]/10)))
    for c,col in zip((0,1,2),('k','C0','C3')):
        sm=np.convolve(S[c],np.ones(9)/9,'same')
        a.semilogx(f,sm-ref,color=col,lw=1,label=f'beat {c+1}: 250-500 {band(S[c],250,500)-ref:.1f}  1-4k {band(S[c],1000,4000)-ref:.1f} tilt {band(S[c],1000,4000)-band(S[c],250,500):.1f}')
    a.set_xlim(100,8000); a.set_ylim(-60,5); a.grid(alpha=.3,which='both'); a.legend(fontsize=8); a.set_title(nm)
plt.tight_layout(); plt.savefig(sys.argv[1],dpi=70)
