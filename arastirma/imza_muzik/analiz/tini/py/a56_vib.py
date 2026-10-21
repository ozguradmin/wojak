import numpy as np, soundfile as sf, scipy.signal as ss
S='/tmp/claude-0/-home-user-wojak/e1bf52df-8e16-5819-ad96-6f6873ef480c/scratchpad'
y,sr=sf.read(S+'/muzik/orijinal.wav'); x=y.mean(1); t=np.arange(len(x))/sr
def fm(fc,a,b,bw=25):
    z=x*np.exp(-2j*np.pi*fc*t); sos=ss.butter(4,bw,fs=sr,output='sos'); zb=ss.sosfiltfilt(sos,z.real)+1j*ss.sosfiltfilt(sos,z.imag)
    sel=(t>=a)&(t<=b); ph=np.unwrap(np.angle(zb[sel])); fi=fc+np.gradient(ph)*sr/(2*np.pi)
    c=1200*np.log2(fi/fc); c=ss.decimate(ss.decimate(c,9),49)  # -> 100 Hz
    n=np.arange(len(c)); c=c-np.polyval(np.polyfit(n,c,2),n); return c
for lab,a,b,f0,ks in [('C5 held',11.75,12.70,516.3,(5,7)),('C5 held late',12.9,13.65,529.5,(3,5)),('Ab5',8.66,9.05,846,(1,3)),('Eb5',7.34,7.56,618.2,(1,3))]:
    cs=[fm(k*f0,a,b) for k in ks]; c=np.mean(cs,0)
    F=np.abs(np.fft.rfft(c*np.hanning(len(c)),1024)); f=np.fft.rfftfreq(1024,0.01)
    m=(f>=3)&(f<=9); pk=f[m][np.argmax(F[m])]; ratio=F[m].max()/np.median(F[(f>1)&(f<20)])
    r=np.corrcoef(cs[0],cs[1])[0,1]
    print(f'{lab}: FM std {np.std(c):.1f} c (avg of h{ks}), inter-harmonic r {r:.2f}, peak 3-9 Hz at {pk:.1f} Hz, peak/median {ratio:.1f}')
