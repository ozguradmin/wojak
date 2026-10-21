"""timbre features used to compare candidates with the original"""
import numpy as np, scipy.signal as ss, sys
sys.path.insert(0,'/tmp/claude-0/-home-user-wojak/e1bf52df-8e16-5819-ad96-6f6873ef480c/scratchpad/muzik2/analiz/tini/py')
from harm import harmonics
SR=44100
NOTES={'C5':(516.3,72),'D5':(583.3,74),'Eb5':(618.2,75),'Ab5':(817.6,80)}
ORIG_WIN={'C5':(11.75,12.70),'D5':(9.98,10.24),'Eb5':(7.34,7.56),'Ab5':(8.02,8.44)}
def profile(x,a,b,f0g,K=9,fmax=4400):
    f0,am=harmonics(x,SR,a,b,f0g,K=K,search=0.02)
    ks=[k for k in range(1,K+1) if k*f0<fmax]
    return f0,{k:am[k-1] for k in ks}
def am_fm(x,a,b,f0,ks=(1,3,5)):
    t=np.arange(len(x))/SR; am=[];fm=[]
    for k in ks:
        fc=k*f0; bw=min(0.3*f0,60)
        z=x*np.exp(-2j*np.pi*fc*t); sos=ss.butter(4,bw,fs=SR,output='sos')
        zb=ss.sosfiltfilt(sos,z.real)+1j*ss.sosfiltfilt(sos,z.imag); sel=(t>=a)&(t<=b)
        e=20*np.log10(np.abs(zb[sel])+1e-12); n=np.arange(len(e)); e=e-np.polyval(np.polyfit(n,e,2),n)
        am.append(np.std(e))
        ph=np.unwrap(np.angle(zb[sel])); fi=fc+np.gradient(ph)*SR/(2*np.pi); fi=ss.sosfiltfilt(ss.butter(2,20,fs=SR,output='sos'),fi)
        c=1200*np.log2(np.clip(fi,1,None)/fc); c=c-np.polyval(np.polyfit(n,c,2),n); fm.append(np.std(c))
    return float(np.mean(am)),float(np.median(fm))
def oe_index(p):
    odd=[p[k] for k in (1,3,5,7) if k in p]; ev=[p[k] for k in (2,4,6,8) if k in p]
    return float(np.mean(odd)-np.mean(ev))
def centroid(x,a,b,lo=250,hi=4500):
    seg=x[int(a*SR):int(b*SR)]; X=np.abs(np.fft.rfft(seg*np.hanning(len(seg))))**2; f=np.fft.rfftfreq(len(seg),1/SR)
    m=(f>=lo)&(f<=hi); return float((f[m]*X[m]).sum()/X[m].sum())
def env_fit(tp,cp,lam=3.0):
    """tp,cp: dict note->(f0,{k:dB}); fit smooth EQ G(f) on 1/3-oct log grid + per-note gains; return residual rms, G"""
    nodes=np.log2(np.array([400*2**(i/3) for i in range(0,12)]))  # 400..~4.4k
    rows=[];y=[];notes=list(tp)
    for i,nm in enumerate(notes):
        f0t,pt=tp[nm]; f0c,pc=cp[nm]
        for k in pt:
            if k not in pc: continue
            fr=np.log2(k*f0t); w=np.interp(fr,nodes,np.arange(len(nodes)))
            r=np.zeros(len(notes)+len(nodes)); r[i]=1
            j=int(np.floor(np.clip(w,0,len(nodes)-1.001))); fr_=np.clip(w,0,len(nodes)-1)-j
            r[len(notes)+j]+=1-fr_; r[len(notes)+min(j+1,len(nodes)-1)]+=fr_
            rows.append(r); y.append(pt[k]-pc[k])
    A=np.array(rows); y=np.array(y)
    # smoothness penalty on second differences of G
    nN=len(nodes); P=np.zeros((nN-2,A.shape[1]))
    for i in range(nN-2): P[i,len(notes)+i:len(notes)+i+3]=[1,-2,1]
    AA=np.vstack([A,lam*P]); yy=np.r_[y,np.zeros(nN-2)]
    coef=np.linalg.lstsq(AA,yy,rcond=None)[0]; res=y-A@coef
    G=coef[len(notes):]; G=G-G.mean()
    return float(np.sqrt(np.mean(res**2))),[(float(2**n),float(g)) for n,g in zip(nodes,G)]
