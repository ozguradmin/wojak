import numpy as np, soundfile as sf, scipy.signal as ss, matplotlib
matplotlib.use('Agg'); import matplotlib.pyplot as plt
S='/tmp/claude-0/-home-user-wojak/e1bf52df-8e16-5819-ad96-6f6873ef480c/scratchpad'; D=S+'/muzik2/analiz/tini'
y,sr=sf.read(S+'/muzik/orijinal.wav'); x=y.mean(1)
sos=ss.butter(4,[900,4000],'bandpass',fs=sr,output='sos'); xb=ss.sosfiltfilt(sos,x)
e=np.sqrt(ss.sosfiltfilt(ss.butter(2,80,fs=sr,output='sos'),xb**2).clip(1e-12)); ed=20*np.log10(e)
t=np.arange(len(x))/sr
# find bursts in 0-4.7 s
seg=(t<4.7)
pk,_=ss.find_peaks(ed*seg,prominence=8,distance=int(0.2*sr))
pk=[p for p in pk if t[p]<4.7]
fig,ax=plt.subplots(1,1,figsize=(12,6))
rows=[]
for p in pk:
    w0=p-int(0.2*sr); w1=p+int(0.25*sr); 
    loc=ed[w0:w1]; base=np.percentile(loc,10); peak=ed[p]
    # attack: from base+3dB to peak-1dB
    pre=ed[w0:p]; post=ed[p:w1]
    i3=np.where(pre<peak-20)[0]; ia=w0+(i3[-1] if len(i3) else 0)
    a10=np.where(pre<peak-10)[0]; a10=w0+(a10[-1] if len(a10) else 0)
    d10=np.where(post<peak-10)[0]; d10=p+(d10[0] if len(d10) else 0)
    d20=np.where(post<peak-20)[0]; d20=p+(d20[0] if len(d20) else len(post))
    # decay slope dB/s between -3 and -15
    rows.append((t[p],peak-base,(p-a10)/sr*1000,(d10-p)/sr*1000,(d20-p)/sr*1000))
    ax.plot((np.arange(w0,w1)-p)/sr*1000,ed[w0:w1]-peak,lw=1,label=f'{t[p]:.2f}s')
ax.legend(); ax.grid(alpha=.3); ax.set_xlabel('ms re peak'); ax.set_ylabel('dB'); ax.set_title('900-4000 Hz envelope of intro bursts')
plt.savefig(D+'/png/21_burst_shapes.png',dpi=60)
print('t_peak  rise_over_base_dB  attack(-10dB->peak ms)  decay(peak->-10dB ms) decay(-20)')
for r in rows: print(' '.join(f'{v:8.2f}' for v in r))
