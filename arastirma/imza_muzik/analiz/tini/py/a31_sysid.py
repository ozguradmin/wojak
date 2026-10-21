import numpy as np, soundfile as sf, scipy.signal as ss, matplotlib, sys
matplotlib.use('Agg'); import matplotlib.pyplot as plt
S='/tmp/claude-0/-home-user-wojak/e1bf52df-8e16-5819-ad96-6f6873ef480c/scratchpad'; D=S+'/muzik2/analiz/tini'
p=sys.argv[1] if len(sys.argv)>1 else S+'/muzik/orijinal.wav'; name=sys.argv[2] if len(sys.argv)>2 else 'orig'
y,sr=sf.read(p); y=y[:int(13.73*sr)]; L,R=y[:,0],y[:,1]; M=(L+R)/2; Sd=(L-R)/2
bp=ss.butter(4,[300,4000],'bandpass',fs=sr,output='sos'); M=ss.sosfiltfilt(bp,M); Sd=ss.sosfiltfilt(bp,Sd); Lb=ss.sosfiltfilt(bp,L); Rb=ss.sosfiltfilt(bp,R)
def sysid(inp,out,n=32768):
    f,Pxy=ss.csd(inp,out,sr,nperseg=n,noverlap=n*3//4,window='hann')
    f,Pxx=ss.welch(inp,sr,nperseg=n,noverlap=n*3//4,window='hann')
    m=(f>300)&(f<4000); H=np.zeros_like(Pxy); H[m]=Pxy[m]/(Pxx[m]+1e-3*Pxx[m].max())
    h=np.fft.irfft(H,n); return h
res={}
for lab,(i,o) in {'side_from_mid':(M,Sd),'R_from_L':(Lb,Rb)}.items():
    h=sysid(i,o); e=h**2
    # smooth energy envelope, 5 ms
    k=int(0.005*sr); es=np.convolve(e,np.ones(k)/k,'same')
    t=np.arange(len(h))/sr
    res[lab]=(t,10*np.log10(es/es.max()+1e-12),h)
    # Schroeder on first 0.6 s
    seg=e[:int(0.6*sr)]; sch=np.cumsum(seg[::-1])[::-1]; schd=10*np.log10(sch/sch[0])
    # find predelay: first time envelope within 10 dB of max
    env=10*np.log10(es/es.max()+1e-12); pd=t[np.argmax(env>-10)]; tmax=t[np.argmax(env[:int(0.3*sr)])]
    # fit slope of envelope between peak and peak+200ms
    i0=np.argmax(env[:int(0.3*sr)]); i1=i0+int(0.25*sr)
    sl=np.polyfit(t[i0:i1],env[i0:i1],1)[0]
    def tcross(db):
        j=np.argmax(schd<db); return t[j]
    edt=6*tcross(-10); t20=3*(tcross(-25)-tcross(-5))
    print(f'{lab}: env peak at {tmax*1000:.1f} ms, first -10dB {pd*1000:.1f} ms, slope {sl:.0f} dB/s -> RT60 {60/abs(sl):.2f}s; Schroeder EDT {edt:.2f}s T20 {t20:.2f}s; floor(0.4-0.7s) {env[int(0.4*sr):int(0.7*sr)].mean():.1f} dB')
fig,ax=plt.subplots(2,1,figsize=(14,9))
for lab,(t,env,h) in res.items():
    ax[0].plot(t[:int(0.7*sr)]*1000,env[:int(0.7*sr)],label=lab)
    ax[1].plot(t[:int(0.12*sr)]*1000,h[:int(0.12*sr)],label=lab,lw=0.6)
ax[0].legend(); ax[0].grid(alpha=.3); ax[0].set_xlabel('ms'); ax[0].set_ylabel('dB'); ax[0].set_title(f'{name}: identified response energy (5 ms smoothing)')
ax[1].legend(); ax[1].grid(alpha=.3)
plt.tight_layout(); plt.savefig(D+f'/png/29_sysid_{name}.png',dpi=60)
