import numpy as np, soundfile as sf, scipy.signal as ss, matplotlib
matplotlib.use('Agg'); import matplotlib.pyplot as plt
S='/tmp/claude-0/-home-user-wojak/e1bf52df-8e16-5819-ad96-6f6873ef480c/scratchpad'; D=S+'/muzik2/analiz/tini'
y2,sr=sf.read(S+'/muzik/orijinal.wav'); M=y2.mean(1)
bands=[(40,240),(240,480),(480,900),(900,1800),(1800,3600),(3600,7000),(7000,14000)]
fig,ax=plt.subplots(len(bands)+1,1,figsize=(22,16),sharex=True)
t=np.arange(len(M))/sr
ax[0].plot(t,M,lw=0.3); ax[0].set_title('waveform mid')
envs={}
for i,(lo,hi) in enumerate(bands):
    sos=ss.butter(4,[lo,hi],'bandpass',fs=sr,output='sos'); x=ss.sosfiltfilt(sos,M)
    e=np.sqrt(ss.sosfiltfilt(ss.butter(2,30,fs=sr,output='sos'),x**2).clip(0))
    ed=20*np.log10(e+1e-9); envs[(lo,hi)]=ed
    ax[i+1].plot(t,ed,lw=0.6); ax[i+1].set_title(f'{lo}-{hi} Hz env dB (30 Hz LP)'); ax[i+1].set_ylim(np.percentile(ed,1)-3,ed.max()+2)
for a in ax:
    for x in np.arange(0,14,0.387): a.axvline(x,color='r',alpha=0.2)
ax[-1].set_xticks(np.arange(0,14,0.387)); ax[-1].tick_params(axis='x',labelsize=7)
plt.tight_layout(); plt.savefig(D+'/png/06_band_envelopes.png',dpi=55)
# stats: level variability per band
for k,e in envs.items():
    e=e[int(0.3*sr):int(13.4*sr)]; print(k,'mean',round(e.mean(),1),'std',round(e.std(),2),'p5-p95',round(np.percentile(e,95)-np.percentile(e,5),1))
