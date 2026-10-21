import sys, numpy as np, scipy.signal as ss, matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
sys.path.insert(0,'/tmp/claude-0/-home-user-wojak/e1bf52df-8e16-5819-ad96-6f6873ef480c/scratchpad/muzik2/olcum')
import olcum as O
def mel(path):
    y=O.decode(path)[:int(13.77*O.SR)]; a0,a1,_,_=O.active_region(y,None); mid=y.mean(1)
    y22=ss.resample_poly(mid,1,2); return O.mel_mfcc(y22,(a0/O.SR,a1/O.SR))
R=mel(O.REF_WAV); 
fig,ax=plt.subplots(2,1,figsize=(12,8))
ax[0].semilogx(R['mel_f'],R['mel_env'],'k',lw=2,label='orig')
for p in sys.argv[2:]:
    C=mel(p); d=np.array(C['mel_env'])-np.array(R['mel_env']); f=np.array(R['mel_f']); m=(f>=80)&(f<=6000)
    print(p.split('/')[-1], 'mel_env rms(80-6k)', round(float(np.sqrt(np.mean(d[m]**2))),2), 'mfcc dist', round(float(np.linalg.norm(np.array(C['mfcc_mean'])-np.array(R['mfcc_mean']))),1))
    print('  mfcc diff', np.round(np.array(C['mfcc_mean'])-np.array(R['mfcc_mean']),1).tolist())
    ax[0].semilogx(f,C['mel_env'],lw=1,label=p.split('/')[-1]); ax[1].semilogx(f,d,lw=1,label=p.split('/')[-1])
ax[1].axhline(0,color='k'); ax[1].axvspan(80,6000,alpha=0.05)
for a in ax: a.grid(alpha=.3,which='both'); a.legend(fontsize=7)
plt.savefig(sys.argv[1],dpi=70)
