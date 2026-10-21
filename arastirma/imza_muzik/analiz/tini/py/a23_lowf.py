import numpy as np, soundfile as sf, scipy.signal as ss, matplotlib, librosa
matplotlib.use('Agg'); import matplotlib.pyplot as plt
S='/tmp/claude-0/-home-user-wojak/e1bf52df-8e16-5819-ad96-6f6873ef480c/scratchpad'; D=S+'/muzik2/analiz/tini'
y,sr=sf.read(S+'/muzik/orijinal.wav'); x=y[:int(13.73*sr)].mean(1); s=(y[:int(13.73*sr),0]-y[:int(13.73*sr),1])/2
n=2**19
X=np.abs(np.fft.rfft(x*np.hanning(len(x)),n)); f=np.fft.rfftfreq(n,1/sr); Xd=20*np.log10(X/X.max()+1e-12)
Sx=np.abs(np.fft.rfft(s*np.hanning(len(s)),n)); Sd=20*np.log10(Sx/X.max()+1e-12)
m=f<400
pk,_=ss.find_peaks(Xd[m],prominence=10,distance=40)
print('LF peaks (Hz, dB rel global max):',[(round(f[p],2),round(Xd[p],1)) for p in pk if Xd[p]>-75])
fig,ax=plt.subplots(2,1,figsize=(16,9))
ax[0].plot(f[m],Xd[m],lw=0.6,label='mid'); ax[0].plot(f[m],Sd[m],lw=0.6,alpha=.7,label='side'); ax[0].legend(); ax[0].grid(alpha=.3); ax[0].set_xticks(np.arange(0,401,25))
# time stability of 100 & 150 Hz lines
St=np.abs(librosa.stft(x,n_fft=32768,hop_length=4096)); fs=librosa.fft_frequencies(sr=sr,n_fft=32768); tt=np.arange(St.shape[1])*4096/sr
for hz in [50,93.5,100.26,125.2,150.06,200,258]:
    i=np.argmin(abs(fs-hz)); ax[1].plot(tt,20*np.log10(St[i]/St.max()+1e-12),label=f'{hz}')
ax[1].legend(); ax[1].grid(alpha=.3)
plt.tight_layout(); plt.savefig(D+'/png/24_lowfreq.png',dpi=60)
# stereo: L-R correlation per band
for lo,hi in [(20,250),(250,500),(500,1000),(1000,2000),(2000,4000),(4000,8000),(8000,16000)]:
    sos=ss.butter(4,[lo,hi],'bandpass',fs=sr,output='sos'); a=ss.sosfiltfilt(sos,y[:,0]); b=ss.sosfiltfilt(sos,y[:,1])
    print(f'band {lo}-{hi}: L/R corr {np.corrcoef(a,b)[0,1]:.3f}  side/mid {10*np.log10(np.mean((a-b)**2)/np.mean((a+b)**2)):.1f} dB  L-R level {10*np.log10(np.mean(a**2)/np.mean(b**2)):+.1f} dB')
