import numpy as np, soundfile as sf, scipy.signal as ss, librosa, librosa.display, matplotlib
matplotlib.use('Agg'); import matplotlib.pyplot as plt
S='/tmp/claude-0/-home-user-wojak/e1bf52df-8e16-5819-ad96-6f6873ef480c/scratchpad'; D=S+'/muzik2/analiz/tini'
y2,sr=sf.read(S+'/muzik/orijinal.wav'); M=y2.mean(1)
a,b=0.0,2.5
seg=M[int(a*sr):int(b*sr)]; t=a+np.arange(len(seg))/sr
fig,ax=plt.subplots(3,1,figsize=(22,15),gridspec_kw=dict(height_ratios=[1,2,2]))
ax[0].plot(t,seg,lw=0.3); ax[0].set_xlim(a,b)
X=librosa.stft(seg,n_fft=2048,hop_length=64); Xd=librosa.amplitude_to_db(np.abs(X),ref=np.max(np.abs(librosa.stft(M,n_fft=2048))))
librosa.display.specshow(Xd,sr=sr,hop_length=64,x_axis='time',y_axis='log',ax=ax[1],vmin=-85,vmax=0,cmap='magma'); ax[1].set_ylim(100,16000)
X2=librosa.stft(seg,n_fft=8192,hop_length=128); Xd2=librosa.amplitude_to_db(np.abs(X2),ref=np.max(np.abs(X2)))
librosa.display.specshow(Xd2,sr=sr,hop_length=128,x_axis='time',y_axis='linear',ax=ax[2],vmin=-70,cmap='magma'); ax[2].set_ylim(200,2500)
for k in (1,2):
    xt=ax[k].get_xticks()
for k in range(3): 
    ax[k].set_xticks(np.arange(0,b-a,0.1)+ (a if k==0 else 0))
plt.tight_layout(); plt.savefig(D+'/png/07_zoom_0_2p5.png',dpi=55)
