import numpy as np, soundfile as sf, scipy.signal as ss, matplotlib, sys
matplotlib.use('Agg'); import matplotlib.pyplot as plt
S='/tmp/claude-0/-home-user-wojak/e1bf52df-8e16-5819-ad96-6f6873ef480c/scratchpad'; D=S+'/muzik2/analiz/tini'
p,a,b,f0,K,name=sys.argv[1],float(sys.argv[2]),float(sys.argv[3]),float(sys.argv[4]),int(sys.argv[5]),sys.argv[6]
y,sr=sf.read(p); x=y.mean(1) if y.ndim>1 else y
seg=x[int(a*sr):int(b*sr)]; n=2**20
w=ss.windows.blackmanharris(len(seg)) if len(sys.argv)<=7 else np.hanning(len(seg))
X=np.abs(np.fft.rfft(seg*w,n)); f=np.fft.rfftfreq(n,1/sr); Xd=20*np.log10(X/X.max()+1e-12)
fig,ax=plt.subplots(K,1,figsize=(12,2.1*K))
for k in range(1,K+1):
    fc=k*f0; m=(f>fc-0.06*fc-25)&(f<fc+0.06*fc+25)
    ax[k-1].plot(f[m]-fc,Xd[m]); ax[k-1].set_title(f'h{k} around {fc:.0f} Hz',fontsize=9); ax[k-1].grid(alpha=.3)
    pk,_=ss.find_peaks(Xd[m],prominence=4); fr=f[m][pk]; am=Xd[m][pk]; o=np.argsort(-am)[:4]
    print(f'h{k}: peaks (offset Hz, dB):',[(round(fr[i]-fc,1),round(am[i],1)) for i in sorted(o)])
plt.tight_layout(); plt.savefig(D+f'/png/{name}.png',dpi=55)
