import numpy as np, soundfile as sf, sys, matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
O="/tmp/claude-0/-home-user-wojak/e1bf52df-8e16-5819-ad96-6f6873ef480c/scratchpad/muzik/orijinal.wav"
x,sr=sf.read(O); m=x.mean(1)
fig,ax=plt.subplots(3,1,figsize=(16,10))
for a,(t0,t1,lo,hi) in zip(ax,[(11.8,12.8,200,1400),(11.8,12.8,1400,4200),(0.45,0.75,200,2000)]):
    seg=m[int(t0*sr):int(t1*sr)]; n=2**17
    X=20*np.log10(np.abs(np.fft.rfft(seg*np.hanning(len(seg)),n))+1e-12); f=np.fft.rfftfreq(n,1/sr); X-=X[(f>200)&(f<4000)].max()
    a.plot(f,X,lw=0.6)
    c5=516.3
    for k in range(1,9): a.axvline(k*c5,color='r',lw=0.8,alpha=0.6)
    # C minor notes at -23c, octaves 3-5 and their harmonics up to h3
    for midi in [48,51,55,60,63,67,50,53,59,62,65]:
        f0=440*2**((midi-69-0.23)/12)
        for k in range(1,6):
            if lo<k*f0<hi: a.axvline(k*f0,color='g',lw=0.4,alpha=0.4,ls='--')
    a.set_xlim(lo,hi); a.set_ylim(-70,0); a.set_title(f'original {t0}-{t1}s  red=C5 harmonics (516.3), green dashed=C-minor/vii chord tones harmonics',fontsize=9); a.grid(alpha=.3)
plt.tight_layout(); plt.savefig('png/orig_zoomspec.png',dpi=72)
