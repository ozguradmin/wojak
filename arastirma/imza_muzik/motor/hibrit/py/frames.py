import numpy as np, soundfile as sf, scipy.signal as ss, sys, matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
O="/tmp/claude-0/-home-user-wojak/e1bf52df-8e16-5819-ad96-6f6873ef480c/scratchpad/muzik/orijinal.wav"
files=[O]+sys.argv[2:]
out=sys.argv[1]
times=[1.0,3.0,6.0,8.5,12.2]
fig,ax=plt.subplots(len(times),1,figsize=(15,3*len(times)))
for fpath,col in zip(files,['C0','C1','C2','C3']):
    x,sr=sf.read(fpath); m=x.mean(1)
    f,t,Z=ss.stft(m,sr,nperseg=8192,noverlap=6144,boundary=None,padded=False); P=10*np.log10(np.abs(Z)**2+1e-20)
    for a,tt in zip(ax,times):
        j=np.argmin(abs(t-tt)); band=(f>=250)&(f<4000); ref=10*np.log10(np.mean(np.abs(Z[band,j])**2))
        a.plot(f,P[:,j]-ref,lw=0.6,color=col,label=fpath.split('/')[-1])
        a.set_xlim(200,6000); a.set_ylim(-70,25); a.set_xscale('log'); a.set_title(f't={tt}',fontsize=8); a.grid(alpha=.3)
ax[0].legend(fontsize=7)
plt.tight_layout(); plt.savefig(out,dpi=70)
