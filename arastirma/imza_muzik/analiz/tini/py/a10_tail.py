import numpy as np, soundfile as sf, scipy.signal as ss, matplotlib
matplotlib.use('Agg'); import matplotlib.pyplot as plt
S='/tmp/claude-0/-home-user-wojak/e1bf52df-8e16-5819-ad96-6f6873ef480c/scratchpad'; D=S+'/muzik2/analiz/tini'
y2,sr=sf.read(S+'/muzik/orijinal.wav'); M=y2.mean(1)
w=int(0.01*sr)
r=[20*np.log10(np.sqrt(np.mean(M[i:i+w]**2))+1e-12) for i in range(0,len(M)-w,w)]
r=np.array(r); t=np.arange(len(r))*0.01
print('first 30 x10ms:',np.round(r[:30],1)); print('last 40 x10ms:',np.round(r[-40:],1))
fig,ax=plt.subplots(2,1,figsize=(18,8))
tt=np.arange(len(M))/sr
ax[0].plot(tt,M,lw=0.4); ax[0].set_xlim(13.2,13.78)
ax[1].plot(tt,M,lw=0.4); ax[1].set_xlim(0,0.15)
plt.tight_layout(); plt.savefig(D+'/png/08_head_tail.png',dpi=60)
