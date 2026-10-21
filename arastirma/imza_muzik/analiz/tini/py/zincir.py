"""Measured lo-fi chain model of the original (analysis/test use)."""
import numpy as np, scipy.signal as ss
SR=44100
def wow(x,rms_c=4.5,band=(0.5,5.0),seed=1,sr=SR):
    """random common pitch modulation via variable delay: cents RMS in band"""
    if rms_c<=0: return x
    rng=np.random.default_rng(seed); n=len(x)
    w=rng.standard_normal(n//100+10); fs2=sr/100
    sos=ss.butter(2,[band[0],band[1]],'bandpass',fs=fs2,output='sos'); w=ss.sosfiltfilt(sos,w); w=w/np.std(w)*rms_c
    w=np.interp(np.arange(n)/100,np.arange(len(w)),w)
    ratio=2**(w/1200)   # instantaneous speed
    pos=np.cumsum(ratio); pos=pos-pos[0]
    pos=pos*(n-1)/pos[-1] if pos[-1]>0 else pos
    return np.interp(pos,np.arange(n),x)
def ir(rt60=0.30,pd_ms=2.0,build_ms=8.0,dur=1.5,tail_db=-26.0,tail_rt=1.2,hp=150,lp=6000,seed=7,sr=SR):
    rng=np.random.default_rng(seed); n=int(dur*sr); t=np.arange(n)/sr
    out=[]
    for ch in range(2):
        nz=rng.standard_normal(n); nz2=rng.standard_normal(n)
        tt=np.clip(t-pd_ms/1000,0,None)
        env=(t>pd_ms/1000)*(1-np.exp(-tt/(build_ms/1000+1e-9)))*np.exp(-6.91*tt/rt60)
        env2=(t>pd_ms/1000)*(1-np.exp(-tt/0.02))*np.exp(-6.91*tt/tail_rt)*10**(tail_db/20)
        h=nz*env+nz2*env2
        sos=ss.butter(2,[hp,lp],'bandpass',fs=sr,output='sos'); h=ss.sosfilt(sos,h)
        out.append(h)
    h=np.array(out).T
    h/=np.sqrt(np.sum(h**2)/2)   # unit energy per channel
    return h
def reverb(x,wet_db=-2.5,**kw):
    h=ir(**kw); n=len(x)
    L=ss.fftconvolve(x,h[:,0])[:n]; R=ss.fftconvolve(x,h[:,1])[:n]
    g=10**(wet_db/20)
    return np.stack([x+g*L,x+g*R],1)
def bandeq(y,hp=250,hp_order=4,lp=4500,lp_order=8,sr=SR):
    sos=ss.butter(hp_order,hp,'highpass',fs=sr,output='sos'); y=ss.sosfilt(sos,y,axis=0)
    sos=ss.butter(lp_order,lp,'lowpass',fs=sr,output='sos'); return ss.sosfilt(sos,y,axis=0)
def noises(n,hum=((100,-70.4),(150,-78.3),(50,-87.3),(200,-83.5)),rumble_db=-55.7,hiss_db=-80.0,seed=3,sr=SR):
    """dBFS (peak for hum lines; sine-referenced RMS for rumble/hiss); mono"""
    rng=np.random.default_rng(seed); t=np.arange(n)/sr; out=np.zeros(n)
    for f,db in hum: out+=10**(db/20)*np.sin(2*np.pi*f*t+rng.uniform(0,6.28))
    r=ss.sosfiltfilt(ss.butter(2,[4,20],'bandpass',fs=sr,output='sos'),rng.standard_normal(n)); r=r/np.sqrt(np.mean(r**2))*np.sqrt(0.5)*10**(rumble_db/20); out+=r
    h=ss.sosfiltfilt(ss.butter(2,[250,4500],'bandpass',fs=sr,output='sos'),rng.standard_normal(n)); h=h/np.sqrt(np.mean(h**2))*np.sqrt(0.5)*10**(hiss_db/20); out+=h
    return out
def chain(x,wow_c=4.5,wet_db=-2.5,rev=None,eq=True,noise=True,level_rms=-31.6,sr=SR):
    y=wow(x,wow_c) if wow_c else x
    y=reverb(y,wet_db,**(rev or {})) if wet_db is not None else np.stack([y,y],1)
    if eq: y=bandeq(y)
    # set level: sine-referenced RMS of mid in active part
    m=y.mean(1); act=np.abs(m)>1e-6
    cur=10*np.log10(np.mean(m[act]**2)/0.5+1e-20); y=y*10**((level_rms-cur)/20)
    if noise: y=y+noises(len(y))[:,None]
    return y
