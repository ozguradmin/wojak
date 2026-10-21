import numpy as np, soundfile as sf, matplotlib, sys, pickle
sys.path.insert(0,'/tmp/claude-0/-home-user-wojak/e1bf52df-8e16-5819-ad96-6f6873ef480c/scratchpad/muzik2/analiz/tini/py')
from sintrack import track
matplotlib.use('Agg'); import matplotlib.pyplot as plt
S='/tmp/claude-0/-home-user-wojak/e1bf52df-8e16-5819-ad96-6f6873ef480c/scratchpad'; D=S+'/muzik2/analiz/tini'
y2,sr=sf.read(S+'/muzik/orijinal.wav'); M=y2.mean(1)
tr,L=track(M,sr)
pickle.dump(tr,open(D+'/tracks.pkl','wb'))
print('n tracks',len(tr))
fig,ax=plt.subplots(2,1,figsize=(24,18))
for k,(lo,hi) in enumerate([(200,1100),(1100,4200)]):
    for t in tr:
        if lo<=np.median(t['f'])<hi:
            c=np.clip((t['a']+60)/60,0,1)
            ax[k].scatter(t['t'],t['f'],c=c,s=1.5,cmap='magma',vmin=0,vmax=1)
    ax[k].set_ylim(lo,hi); ax[k].set_xticks(np.arange(0,14,0.387)); ax[k].tick_params(axis='x',labelsize=7); ax[k].grid(alpha=0.3)
    ax[k].set_facecolor('#222')
plt.tight_layout(); plt.savefig(D+'/png/13_tracks.png',dpi=50)
