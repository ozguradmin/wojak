import numpy as np, soundfile as sf, scipy.signal as ss, matplotlib
matplotlib.use('Agg'); import matplotlib.pyplot as plt
S='/tmp/claude-0/-home-user-wojak/e1bf52df-8e16-5819-ad96-6f6873ef480c/scratchpad'; D=S+'/muzik2/analiz/tini'
y,sr=sf.read(S+'/muzik/orijinal.wav'); x=y.mean(1)
def env(lo,hi,lp=25):
    b=ss.sosfiltfilt(ss.butter(4,[lo,hi],'bandpass',fs=sr,output='sos'),x); return 20*np.log10(np.sqrt(ss.sosfiltfilt(ss.butter(2,lp,fs=sr,output='sos'),b**2).clip(1e-14)))
t=np.arange(len(x))/sr
E=[(240,330),(330,450),(450,900),(900,4000)]
bursts=[0.36,0.75,1.47,1.86,2.62,3.04,3.78,4.05,4.39]
downs=[1.08,2.23,3.39]
fig,ax=plt.subplots(len(E),1,figsize=(18,10),sharex=True)
for i,(lo,hi) in enumerate(E):
    e=env(lo,hi); ax[i].plot(t[::50],e[::50]); ax[i].set_title(f'{lo}-{hi}')
    for bb in bursts: ax[i].axvline(bb,color='r',alpha=.4)
    for d in downs: ax[i].axvline(d,color='g',alpha=.6)
    print(f'{lo}-{hi}: level at downbeats(+0.05..0.25) {np.mean([e[int((d+0.05)*sr):int((d+0.25)*sr)].mean() for d in downs]):.1f} dB, at bursts {np.mean([e[int((b-0.03)*sr):int((b+0.05)*sr)].mean() for b in bursts]):.1f}, overall median {np.median(e[:int(4.6*sr)]):.1f}')
ax[-1].set_xlim(0,4.7); ax[-1].set_xticks(np.arange(0,4.7,0.1)); ax[-1].tick_params(axis='x',labelsize=7)
plt.tight_layout(); plt.savefig(D+'/png/34_oom_check.png',dpi=55)
