import numpy as np, soundfile as sf, librosa, librosa.display, matplotlib
matplotlib.use('Agg'); import matplotlib.pyplot as plt, json, sys
S='/tmp/claude-0/-home-user-wojak/e1bf52df-8e16-5819-ad96-6f6873ef480c/scratchpad'
D=S+'/muzik2/analiz/tini'
y2,sr=sf.read(S+'/muzik/orijinal.wav'); L,R=y2[:,0],y2[:,1]; M=(L+R)/2; Sd=(L-R)/2
print('sr',sr,'dur',len(M)/sr)
# stereo
def db(x): return 20*np.log10(np.sqrt(np.mean(x**2))+1e-20)
print('rms L R M S', db(L),db(R),db(M),db(Sd), 'corr', np.corrcoef(L,R)[0,1])
# windowed correlation
w=int(0.5*sr)
cs=[np.corrcoef(L[i:i+w],R[i:i+w])[0,1] for i in range(0,len(L)-w,w)]
print('win corr', np.round(cs,4))
# side spectrum vs mid
f,Pm=__import__('scipy.signal',fromlist=['welch']).welch(M,sr,nperseg=8192)
f,Ps=__import__('scipy.signal',fromlist=['welch']).welch(Sd,sr,nperseg=8192)
for b in [100,250,500,1000,2000,4000,8000,12000,16000]:
    i=np.argmin(abs(f-b)); print('S-M dB at',b, 10*np.log10(Ps[i]/Pm[i]))
# lag between L and R
c=np.correlate(L[sr*2:sr*4],R[sr*2-200:sr*4+200],'valid'); print('lag',np.argmax(c)-200)
# Spectrograms
fig,ax=plt.subplots(3,1,figsize=(18,14))
Sx=librosa.amplitude_to_db(np.abs(librosa.stft(M,n_fft=4096,hop_length=256)),ref=np.max)
librosa.display.specshow(Sx,sr=sr,hop_length=256,x_axis='time',y_axis='linear',ax=ax[0],vmin=-90); ax[0].set_ylim(0,8000); ax[0].set_title('STFT linear 0-8k (mid)')
librosa.display.specshow(Sx,sr=sr,hop_length=256,x_axis='time',y_axis='log',ax=ax[1],vmin=-90); ax[1].set_title('STFT log (mid)')
C=librosa.amplitude_to_db(np.abs(librosa.cqt(M,sr=sr,hop_length=256,fmin=librosa.note_to_hz('C2'),n_bins=7*36,bins_per_octave=36)),ref=np.max)
librosa.display.specshow(C,sr=sr,hop_length=256,x_axis='time',y_axis='cqt_note',fmin=librosa.note_to_hz('C2'),bins_per_octave=36,ax=ax[2],vmin=-70)
ax[2].set_title('CQT C2-C9 36bpo')
for a in ax: a.set_xticks(np.arange(0,14,0.387*3))
plt.tight_layout(); plt.savefig(D+'/png/01_overview.png',dpi=70)
# full band to 22k
fig,ax=plt.subplots(1,1,figsize=(18,6))
librosa.display.specshow(Sx,sr=sr,hop_length=256,x_axis='time',y_axis='linear',ax=ax,vmin=-110)
plt.colorbar(ax.collections[0]); ax.set_title('STFT full band, vmin -110'); plt.tight_layout(); plt.savefig(D+'/png/02_fullband.png',dpi=70)
