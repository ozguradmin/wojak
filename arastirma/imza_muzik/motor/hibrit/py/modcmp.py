"""per-band modulation spectra (olcum method) original vs candidates"""
import sys, numpy as np, matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
sys.path.insert(0,'/tmp/claude-0/-home-user-wojak/e1bf52df-8e16-5819-ad96-6f6873ef480c/scratchpad/muzik2/olcum')
import olcum as O
def mod(path):
    y=O.decode(path)[:int(13.77*O.SR)]; a0,a1,_,_=O.active_region(y,None); mid=y.mean(1)
    te,env,fs=O.band_envelopes(mid,a0/O.SR,a1/O.SR); return O.modulation(te,env,fs)
R=mod(O.REF_WAV); e=np.array(R['edges_hz']); c=np.sqrt(e[1:]*e[:-1])
fig,ax=plt.subplots(1,4,figsize=(20,5))
names=['250-500','500-1k','1-2k','2-4k']
for b in range(4): ax[b].semilogx(c,R['spec_db'][b],'k',lw=2,label='orig'); ax[b].set_title(names[b]); ax[b].grid(alpha=.3,which='both')
for p in sys.argv[2:]:
    C=mod(p); Ms=np.array(R['spec_db']).ravel(); Mc=np.array(C['spec_db']).ravel()
    print(p.split('/')[-1],'r',round(float(np.corrcoef(Ms,Mc)[0,1]),3),'depth',round(float(np.mean(Mc-Ms)),2),'per band depth',[round(float(np.mean(np.array(C['spec_db'][b])-np.array(R['spec_db'][b]))),1) for b in range(4)], C['fluct_rms_db'])
    for b in range(4): ax[b].semilogx(c,C['spec_db'][b],lw=1,label=p.split('/')[-1][:20])
ax[0].legend(fontsize=7); plt.tight_layout(); plt.savefig(sys.argv[1],dpi=65)
print('orig',R['fluct_rms_db'])
