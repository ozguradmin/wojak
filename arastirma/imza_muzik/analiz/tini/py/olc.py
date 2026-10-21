"""measurement helpers shared by original and candidates"""
import numpy as np, scipy.signal as ss
SR=44100
def stereo_stats(y,sr=SR):
    L,R=y[:,0],y[:,1]; out={}
    for lo,hi in [(250,500),(500,1000),(1000,2000),(2000,4000)]:
        sos=ss.butter(4,[lo,hi],'bandpass',fs=sr,output='sos'); a=ss.sosfiltfilt(sos,L); b=ss.sosfiltfilt(sos,R)
        out[f'sm_{lo}']=10*np.log10(np.mean((a-b)**2)/np.mean((a+b)**2))
    f,C=ss.coherence(L,R,sr,nperseg=4096)
    for lo,hi in [(250,500),(500,1000),(1000,2000),(2000,4000)]:
        m=(f>=lo)&(f<hi); out[f'coh_{lo}']=C[m].mean()
    return out
def sysid_curve(y,sr=SR,n=32768,times_ms=(10,20,35,50,75,100,150,200,300)):
    L,R=y[:,0],y[:,1]; M=(L+R)/2; Sd=(L-R)/2
    bp=ss.butter(4,[300,4000],'bandpass',fs=sr,output='sos'); M=ss.sosfiltfilt(bp,M); Sd=ss.sosfiltfilt(bp,Sd)
    f,Pxy=ss.csd(M,Sd,sr,nperseg=n,noverlap=n*3//4); f,Pxx=ss.welch(M,sr,nperseg=n,noverlap=n*3//4)
    m=(f>300)&(f<4000); H=np.zeros_like(Pxy); H[m]=Pxy[m]/(Pxx[m]+1e-3*Pxx[m].max())
    h=np.fft.irfft(H,n); e=h**2; k=int(0.005*sr); es=np.convolve(e,np.ones(k)/k,'same')
    env=10*np.log10(es/es[:int(0.3*sr)].max()+1e-12)
    return {f'ir_{t}':float(env[int(t/1000*sr)]) for t in times_ms}, env
