import numpy as np, scipy.signal as ss, pickle, matplotlib
matplotlib.use('Agg'); import matplotlib.pyplot as plt
D='/tmp/claude-0/-home-user-wojak/e1bf52df-8e16-5819-ad96-6f6873ef480c/scratchpad/muzik2/analiz/tini'
tr=pickle.load(open(D+'/tracks.pkl','rb'))
hop=256/44100; N=int(13.8/hop)+1
sos=ss.butter(2,8,fs=1/hop,output='sos')
acc=np.zeros(N); wsum=np.zeros(N); cnt=np.zeros(N)
for t in tr:
    if t['t'][-1]-t['t'][0]<0.35 or np.median(t['a'])<-45: continue
    c=1200*np.log2(t['f']); n=len(c); c=c-np.polyval(np.polyfit(np.arange(n),c,1),np.arange(n)); c=ss.sosfiltfilt(sos,c) if n>15 else c
    idx=np.round((t['t']-t['t'][0])/hop).astype(int)+int(round(t['t'][0]/hop))
    idx=np.clip(idx,0,N-1); w=10**(t['a']/20)
    acc[idx]+=w*c; wsum[idx]+=w; cnt[idx]+=1
g=np.where(cnt>=3,acc/np.maximum(wsum,1e-12),np.nan)
tt=np.arange(N)*hop
ok=~np.isnan(g)
print('frames with >=3 tracks:',ok.mean().round(2),' global wow std (cents):',np.nanstd(g).round(2),' p2-p98 range',(np.nanpercentile(g,98)-np.nanpercentile(g,2)).round(1))
# spectrum via Lomb-Scargle
from scipy.signal import lombscargle
fr=np.linspace(0.3,8,300); pw=lombscargle(tt[ok],g[ok]-np.nanmean(g),2*np.pi*fr,normalize=True)
o=np.argsort(-pw)[:5]; print('dominant wow rates Hz:',fr[o].round(2),pw[o].round(3))
fig,ax=plt.subplots(2,1,figsize=(16,8))
ax[0].plot(tt,g); ax[0].set_title('global (common) pitch deviation, cents (track-detrended, LP 8 Hz)'); ax[0].grid(alpha=.3)
ax[1].plot(fr,pw); ax[1].set_title('Lomb-Scargle periodogram'); ax[1].grid(alpha=.3)
plt.tight_layout(); plt.savefig(D+'/png/30_wow.png',dpi=60)
