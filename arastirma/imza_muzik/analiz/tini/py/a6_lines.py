import numpy as np, soundfile as sf, librosa, scipy.signal as ss, matplotlib
matplotlib.use('Agg'); import matplotlib.pyplot as plt
S='/tmp/claude-0/-home-user-wojak/e1bf52df-8e16-5819-ad96-6f6873ef480c/scratchpad'; D=S+'/muzik2/analiz/tini'
y2,sr=sf.read(S+'/muzik/orijinal.wav'); M=y2.mean(1)
n=16384; hop=256
X=np.abs(librosa.stft(M,n_fft=n,hop_length=hop)); f=librosa.fft_frequencies(sr=sr,n_fft=n)
t=np.arange(X.shape[1])*hop/sr
Ld=20*np.log10(X+1e-9); Ld-=Ld.max()
fig,ax=plt.subplots(2,1,figsize=(22,14))
b=(f>150)&(f<800)
ax[0].pcolormesh(t,f[b],Ld[b],vmin=-70,vmax=0,cmap='magma',shading='auto')
for name in ['C4','D4','Eb4','F4','G4','Ab4','Bb4','C5','D5','Eb5','F5','G5','Ab5']:
    h=librosa.note_to_hz(name)*2**(-25/1200); ax[0].axhline(h,color='c',lw=0.5,alpha=0.5); ax[0].text(13.8,h,name,color='k',fontsize=9)
for k in range(2,7): ax[0].axhline(130.81*2**(-25/1200)*k,color='lime',lw=0.6,ls='--',alpha=0.6)
ax[0].set_xticks(np.arange(0,14,0.387)); ax[0].tick_params(axis='x',labelsize=7); ax[0].set_title('narrowband 16384 (cyan = C-minor notes at -25c, green dashed = C3 harmonics)')
b=(f>700)&(f<2200)
ax[1].pcolormesh(t,f[b],Ld[b],vmin=-70,vmax=0,cmap='magma',shading='auto'); ax[1].set_xticks(np.arange(0,14,0.387)); ax[1].tick_params(axis='x',labelsize=7)
plt.tight_layout(); plt.savefig(D+'/png/05_narrowband.png',dpi=55)
