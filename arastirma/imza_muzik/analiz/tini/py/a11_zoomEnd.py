import numpy as np, soundfile as sf, scipy.signal as ss, librosa, librosa.display, matplotlib, sys
matplotlib.use('Agg'); import matplotlib.pyplot as plt
S='/tmp/claude-0/-home-user-wojak/e1bf52df-8e16-5819-ad96-6f6873ef480c/scratchpad'; D=S+'/muzik2/analiz/tini'
y2,sr=sf.read(S+'/muzik/orijinal.wav'); M=y2.mean(1)
a,b,name=float(sys.argv[1]),float(sys.argv[2]),sys.argv[3]
seg=M[int(a*sr):int(b*sr)]; t=a+np.arange(len(seg))/sr
fig,ax=plt.subplots(3,1,figsize=(22,16),gridspec_kw=dict(height_ratios=[1,2.5,2]))
ax[0].plot(t,seg,lw=0.3); ax[0].set_xlim(a,b); ax[0].set_xticks(np.arange(np.ceil(a*10)/10,b,0.1))
X2=librosa.stft(seg,n_fft=8192,hop_length=128); Xd2=librosa.amplitude_to_db(np.abs(X2),ref=np.max(np.abs(X2)))
ext=[a,b,0,sr/2]
ax[1].imshow(Xd2,origin='lower',aspect='auto',extent=ext,vmin=-75,vmax=0,cmap='magma'); ax[1].set_ylim(200,4500); ax[1].set_xticks(np.arange(np.ceil(a*10)/10,b,0.1))
ax[1].set_yticks(np.arange(250,4500,250)); ax[1].grid(alpha=0.2)
X3=librosa.stft(seg,n_fft=1024,hop_length=32); Xd3=librosa.amplitude_to_db(np.abs(X3),ref=np.max(np.abs(X3)))
ax[2].imshow(Xd3,origin='lower',aspect='auto',extent=ext,vmin=-80,vmax=0,cmap='magma'); ax[2].set_ylim(0,16000); ax[2].set_xticks(np.arange(np.ceil(a*10)/10,b,0.1))
plt.tight_layout(); plt.savefig(D+f'/png/{name}.png',dpi=55)
