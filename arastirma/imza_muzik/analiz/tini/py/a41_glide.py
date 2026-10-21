import numpy as np, soundfile as sf, librosa, matplotlib
matplotlib.use('Agg'); import matplotlib.pyplot as plt
S='/tmp/claude-0/-home-user-wojak/e1bf52df-8e16-5819-ad96-6f6873ef480c/scratchpad'; D=S+'/muzik2/analiz/tini'
y,sr=sf.read(S+'/muzik/orijinal.wav'); x=y.mean(1)
a,b=7.9,9.4; seg=x[int(a*sr):int(b*sr)]
n=8192; X=np.abs(librosa.stft(seg,n_fft=n,hop_length=128,win_length=4096)); f=librosa.fft_frequencies(sr=sr,n_fft=n); Xd=20*np.log10(X/X.max()+1e-9)
fig,ax=plt.subplots(1,3,figsize=(21,8))
for i,k in enumerate([1,2,3]):
    lo,hi=760*k,900*k; m=(f>=lo)&(f<=hi)
    ax[i].imshow(Xd[m],origin='lower',aspect='auto',extent=[a,b,lo,hi],vmin=-60,vmax=0,cmap='magma')
    for fr in [817.6,846]: ax[i].axhline(fr*k,color='c',lw=0.6,ls='--')
    ax[i].set_title(f'harmonic {k} region ({lo}-{hi} Hz), cyan = k*817.6 and k*846')
plt.tight_layout(); plt.savefig(D+'/png/33_glide_check.png',dpi=55)
