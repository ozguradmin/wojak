import numpy as np, soundfile as sf, scipy.signal as ss, matplotlib, sys
matplotlib.use('Agg'); import matplotlib.pyplot as plt
S='/tmp/claude-0/-home-user-wojak/e1bf52df-8e16-5819-ad96-6f6873ef480c/scratchpad'; D=S+'/muzik2/analiz/tini'
def load(p):
    y,sr=sf.read(p); 
    if y.ndim>1: y=y.mean(1)
    return y,sr
def het(x,sr,a,b,f0,K,bwmax=60):
    t=np.arange(len(x))/sr
    res=[]
    for k in range(1,K+1):
        fc=k*f0; bw=min(0.3*f0,bwmax)
        z=x*np.exp(-2j*np.pi*fc*t); sos=ss.butter(4,bw,fs=sr,output='sos')
        zb=ss.sosfiltfilt(sos,z.real)+1j*ss.sosfiltfilt(sos,z.imag)
        sel=(t>=a)&(t<=b)
        env=np.abs(zb[sel]); ph=np.unwrap(np.angle(zb[sel])); fi=fc+np.gradient(ph)*sr/(2*np.pi)
        fi=ss.sosfiltfilt(ss.butter(2,20,fs=sr,output='sos'),fi)
        res.append((k,fc,env,fi))
    return res
def modspec(env,sr,fmax=40):
    # decimate env to 1 kHz
    e=ss.resample_poly(env,1,44)
    e=20*np.log10(e+1e-9); e=e-np.polyval(np.polyfit(np.arange(len(e)),e,2),np.arange(len(e)))
    n=8192; E=np.abs(np.fft.rfft(e*np.hanning(len(e)),n)); f=np.fft.rfftfreq(n,1/1000.)
    m=(f>=0.5)&(f<=fmax); return f[m],E[m],np.std(e)
if __name__=='__main__':
    p,a,b,f0,K,name=sys.argv[1],float(sys.argv[2]),float(sys.argv[3]),float(sys.argv[4]),int(sys.argv[5]),sys.argv[6]
    x,sr=load(p)
    res=het(x,sr,a,b,f0,K)
    fig,ax=plt.subplots(K,1,figsize=(14,2.0*K),sharex=True)
    for (k,fc,env,fi),axk in zip(res,ax):
        f,E,sd=modspec(env,sr)
        axk.plot(f,E); pk=f[np.argmax(E)]; 
        top=f[ss.find_peaks(E,distance=20)[0]]; Es=E[ss.find_peaks(E,distance=20)[0]]; o=np.argsort(-Es)[:3]
        axk.set_title(f'h{k} {fc:.0f} Hz  AM std {sd:.1f} dB  peaks {np.round(top[o],1)} Hz',fontsize=9)
        c=1200*np.log2(fi/fc); 
        print(f'h{k} {fc:.0f}Hz AMstd {sd:.2f}dB AMpeaks {np.round(top[o],1)}  FMstd {np.std(c):.1f}c  mean {np.mean(20*np.log10(env+1e-9)):.1f}dB')
    ax[-1].set_xlabel('modulation Hz'); ax[-1].set_xticks(np.arange(0,41,2))
    plt.tight_layout(); plt.savefig(D+f'/png/{name}.png',dpi=55)
