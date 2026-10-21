import numpy as np, soundfile as sf, scipy.signal as ss, matplotlib
matplotlib.use('Agg'); import matplotlib.pyplot as plt
S='/tmp/claude-0/-home-user-wojak/e1bf52df-8e16-5819-ad96-6f6873ef480c/scratchpad'; D=S+'/muzik2/analiz/tini'
y,sr=sf.read(S+'/muzik/orijinal.wav'); y=y[:int(13.73*sr)]; L,R=y[:,0],y[:,1]; M=(L+R)/2; Sd=(L-R)/2
f,C=ss.coherence(L,R,sr,nperseg=4096)
fig,ax=plt.subplots(3,1,figsize=(16,12))
ax[0].semilogx(f,C); ax[0].set_xlim(50,16000); ax[0].set_title('L/R magnitude-squared coherence'); ax[0].grid(which='both',alpha=.3)
for lo,hi in [(250,500),(500,1000),(1000,2000),(2000,4000)]:
    m=(f>=lo)&(f<hi); print(f'coherence {lo}-{hi}: {C[m].mean():.2f}')
# envelopes of mid and side in 500-2500 band
sos=ss.butter(4,[400,3000],'bandpass',fs=sr,output='sos')
em=np.sqrt(ss.sosfiltfilt(ss.butter(2,20,fs=sr,output='sos'),ss.sosfiltfilt(sos,M)**2).clip(1e-12))
es=np.sqrt(ss.sosfiltfilt(ss.butter(2,20,fs=sr,output='sos'),ss.sosfiltfilt(sos,Sd)**2).clip(1e-12))
t=np.arange(len(M))/sr
ax[1].plot(t[::50],20*np.log10(em[::50]),label='mid'); ax[1].plot(t[::50],20*np.log10(es[::50]),label='side'); ax[1].legend(); ax[1].set_xlim(0,5); ax[1].grid(alpha=.3)
dm=np.diff(20*np.log10(em[::100])); ds=np.diff(20*np.log10(es[::100]))
xc=np.correlate(ds-ds.mean(),dm-dm.mean(),'full'); lags=(np.arange(len(xc))-(len(dm)-1))*100/sr*1000
k=np.argmax(xc); print('side-vs-mid envelope-derivative xcorr peak lag ms',lags[k])
m=(abs(lags)<200); ax[2].plot(lags[m],xc[m]); ax[2].set_title('xcorr d(env side) vs d(env mid), lag ms (positive=side later)'); ax[2].grid(alpha=.3)
plt.tight_layout(); plt.savefig(D+'/png/26_stereo.png',dpi=60)
# level of side relative to mid during bursts vs between
d=20*np.log10(es/em)
burst=(20*np.log10(em)>np.percentile(20*np.log10(em[:int(4.6*sr)]),90)); 
sel=np.arange(len(M))<int(4.6*sr)
print('intro: side-mid dB at bursts',np.median(d[burst&sel]),' between',np.median(d[(~burst)&sel]))
# ratio of side/mid around burst decay: compute side/mid in 0-100ms after burst peaks vs at peak
