import numpy as np, soundfile as sf, scipy.signal as ss, matplotlib, sys
matplotlib.use('Agg'); import matplotlib.pyplot as plt
S='/tmp/claude-0/-home-user-wojak/e1bf52df-8e16-5819-ad96-6f6873ef480c/scratchpad'; D=S+'/muzik2/analiz/tini'
y2,sr=sf.read(S+'/muzik/orijinal.wav'); M=y2.mean(1)
a,b,f0,name=float(sys.argv[1]),float(sys.argv[2]),float(sys.argv[3]),sys.argv[4]
K=int(sys.argv[5]) if len(sys.argv)>5 else 8
x=M[int((a-0.2)*sr):int((b+0.2)*sr)]
t=a-0.2+np.arange(len(x))/sr
fig,ax=plt.subplots(2,1,figsize=(20,12),sharex=True)
devs=[];amps=[]
for k in range(1,K+1):
    fc=k*f0; bw=min(0.35*f0,60)
    # complex demod
    z=x*np.exp(-2j*np.pi*fc*t)
    sos=ss.butter(4,bw,fs=sr,output='sos'); zb=ss.sosfiltfilt(sos,z.real)+1j*ss.sosfiltfilt(sos,z.imag)
    ph=np.unwrap(np.angle(zb)); fi=fc+np.gradient(ph)*sr/(2*np.pi)
    fi=ss.sosfiltfilt(ss.butter(2,25,fs=sr,output='sos'),fi)
    am=20*np.log10(np.abs(zb)+1e-9)
    sel=(t>=a)&(t<=b)
    c=1200*np.log2(fi[sel]/fc); devs.append(c); amps.append(am[sel])
    ax[0].plot(t[sel][::50],c[::50],lw=1,label=f'h{k} {fc:.0f}Hz')
    ax[1].plot(t[sel][::50],am[sel][::50],lw=1,label=f'h{k}')
ax[0].set_ylim(-150,150); ax[0].legend(ncol=8); ax[0].grid(alpha=.3); ax[0].set_ylabel('cents re k*f0')
ax[1].legend(ncol=8); ax[1].grid(alpha=.3); ax[1].set_ylabel('dB')
ax[1].set_xticks(np.arange(a,b,0.1))
plt.tight_layout(); plt.savefig(D+f'/png/{name}.png',dpi=55)
devs=np.array(devs); amps=np.array(amps)
print('median cents per harmonic',np.round(np.median(devs,1),1))
print('mean amp dB per harmonic',np.round(amps.mean(1)-amps.mean(1).max(),1))
cc=np.corrcoef(devs[:, ::100]); print('corr matrix of deviations (h1..)'); print(np.round(cc,2))
