import numpy as np, soundfile as sf, scipy.signal as ss, matplotlib
matplotlib.use('Agg'); import matplotlib.pyplot as plt
S='/tmp/claude-0/-home-user-wojak/e1bf52df-8e16-5819-ad96-6f6873ef480c/scratchpad'; D=S+'/muzik2/analiz/tini'
y,sr=sf.read(S+'/muzik/orijinal.wav'); x=y.mean(1)
a,b=11.75,12.70; f0=516.3
seg=x[int(a*sr):int(b*sr)]; n=2**18
X=np.abs(np.fft.rfft(seg*np.hanning(len(seg)),n)); f=np.fft.rfftfreq(n,1/sr); Xd=20*np.log10(X/X.max()+1e-12)
fig,ax=plt.subplots(2,1,figsize=(18,10))
m=(f>200)&(f<12000)
ax[0].plot(f[m],Xd[m],lw=0.5)
for k in range(1,24): ax[0].axvline(k*f0,color='g',alpha=.3,lw=0.8)
for k in range(1,24): 
    fm=8000-k*f0
    if fm>0: ax[0].axvline(fm,color='r',alpha=.2,lw=0.8,ls='--')
ax[0].set_xticks(np.arange(0,12001,500)); ax[0].grid(alpha=.2); ax[0].set_title('held C5 11.75-12.70: green = harmonics k*516.3, red dashed = 8000-k*f0 mirror')
ax[0].set_ylim(-100,2)
# harmonic levels k=1..22
lev=[]
for k in range(1,23):
    mm=(f>k*f0*0.985)&(f<k*f0*1.015); lev.append(10*np.log10((X[mm]**2).sum()))
lev=np.array(lev); lev-=lev.max()
# inter-harmonic valley levels
val=[]
for k in range(1,22):
    mm=(f>(k+0.35)*f0)&(f<(k+0.65)*f0); val.append(10*np.log10((X[mm]**2).mean()*((0.03*k*f0)/(f[1]-f[0]))))
val=np.array(val)-np.max(lev+0)  # rough
ax[1].plot(np.arange(1,23)*f0,lev,'o-',label='harmonic band energy (dB re max)')
ax[1].plot((np.arange(1,22)+0.5)*f0,np.array(val)-(10*np.log10((X**2).sum()) - 10*np.log10((X**2).sum())),'x--',label='valley (same scale, approx)')
ax[1].set_xticks(np.arange(0,12001,500)); ax[1].grid(alpha=.3); ax[1].legend()
plt.tight_layout(); plt.savefig(D+'/png/27_hf_harmonics.png',dpi=55)
print('harmonic levels dB:',' '.join(f'{k+1}:{v:.0f}' for k,v in enumerate(lev)))
