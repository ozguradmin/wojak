import numpy as np, soundfile as sf, librosa, matplotlib
matplotlib.use('Agg'); import matplotlib.pyplot as plt
S='/tmp/claude-0/-home-user-wojak/e1bf52df-8e16-5819-ad96-6f6873ef480c/scratchpad'; D=S+'/muzik2/analiz/tini'
y2,sr=sf.read(S+'/muzik/orijinal.wav'); M=y2.mean(1)
hop=128
# broadband onset in different bands
St=np.abs(librosa.stft(M,n_fft=2048,hop_length=hop))
f=librosa.fft_frequencies(sr=sr,n_fft=2048)
t=librosa.frames_to_time(np.arange(St.shape[1]),sr=sr,hop_length=hop)
def flux(lo,hi):
    b=(f>=lo)&(f<hi); X=np.log1p(1000*St[b]); d=np.maximum(0,np.diff(X,axis=1)).sum(0); return np.r_[0,d]
bands=[(100,300),(300,1000),(1000,3000),(3000,6000),(6000,12000)]
fig,ax=plt.subplots(len(bands)+1,1,figsize=(18,14),sharex=True)
oe=librosa.onset.onset_strength(y=M,sr=sr,hop_length=hop)
ax[0].plot(t[:len(oe)],oe); ax[0].set_title('onset strength')
for i,(lo,hi) in enumerate(bands):
    fx=flux(lo,hi); ax[i+1].plot(t,fx); ax[i+1].set_title(f'flux {lo}-{hi}')
# tempo / beat
tempo,beats=librosa.beat.beat_track(onset_envelope=oe,sr=sr,hop_length=hop,start_bpm=152)
bt=librosa.frames_to_time(beats,sr=sr,hop_length=hop)
print('tempo',tempo,'beats',np.round(bt,3)); print('ibi',np.round(np.diff(bt),3))
for a in ax:
    for b in bt: a.axvline(b,color='r',alpha=0.3)
ax[-1].set_xticks(np.arange(0,14,0.5)); plt.tight_layout(); plt.savefig(D+'/png/03_onsets.png',dpi=65)
# autocorrelation of onset env for period
ac=librosa.autocorrelate(oe-oe.mean()); lags=np.arange(len(ac))*hop/sr
sel=(lags>0.2)&(lags<3)
pk=[ (lags[i],ac[i]/ac[0]) for i in range(1,len(ac)-1) if sel[i] and ac[i]>ac[i-1] and ac[i]>ac[i+1]]
pk=sorted(pk,key=lambda x:-x[1])[:10]; print('ac peaks',[(round(a,3),round(b,3)) for a,b in pk])
np.save(D+'/beats.npy',bt)
