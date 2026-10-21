import numpy as np, soundfile as sf, librosa, matplotlib, sys
matplotlib.use('Agg'); import matplotlib.pyplot as plt
S='/tmp/claude-0/-home-user-wojak/e1bf52df-8e16-5819-ad96-6f6873ef480c/scratchpad'; D=S+'/muzik2/analiz/tini'
y2,sr=sf.read(S+'/muzik/orijinal.wav'); M=y2.mean(1)
a,b,flo,fhi,name=float(sys.argv[1]),float(sys.argv[2]),float(sys.argv[3]),float(sys.argv[4]),sys.argv[5]
n=int(sys.argv[6]) if len(sys.argv)>6 else 8192
seg=M[int(a*sr):int(b*sr)]
X=np.abs(librosa.stft(seg,n_fft=n,hop_length=64)); Xd=20*np.log10(X/X.max()+1e-9)
f=librosa.fft_frequencies(sr=sr,n_fft=n); m=(f>=flo)&(f<=fhi)
fig,ax=plt.subplots(1,1,figsize=(22,12))
ax.imshow(Xd[m],origin='lower',aspect='auto',extent=[a,b,f[m][0],f[m][-1]],vmin=-70,vmax=0,cmap='magma')
ax.set_xticks(np.arange(np.ceil(a*10)/10,b,0.1)); 
step=50 if fhi-flo<1200 else 100
ax.set_yticks(np.arange(np.ceil(flo/step)*step,fhi,step)); ax.grid(alpha=0.25)
plt.tight_layout(); plt.savefig(D+f'/png/{name}.png',dpi=55)
