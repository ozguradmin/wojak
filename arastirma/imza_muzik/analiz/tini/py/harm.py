import numpy as np, scipy.signal as ss
def harmonics(x,sr,a,b,f0g,K=12,tol=0.012,n=2**18,search=0.03):
    seg=x[int(a*sr):int(b*sr)]; w=np.hanning(len(seg))
    X=np.abs(np.fft.rfft(seg*w,n)); f=np.fft.rfftfreq(n,1/sr)
    P=X**2
    # refine f0 by harmonic sum over k=1..6
    best=None;bs=-1
    for f0 in np.linspace(f0g*(1-search),f0g*(1+search),601):
        s=0
        for k in range(1,7):
            m=(f>k*f0*(1-0.004))&(f<k*f0*(1+0.004)); s+=np.log(np.nan_to_num(P[m].max())+1e-20)
        if s>bs: bs=s;best=f0
    f0=best if best is not None else f0g; amps=[]
    for k in range(1,K+1):
        m=(f>k*f0*(1-tol))&(f<k*f0*(1+tol))
        # band energy (sum) to be robust to smearing
        e=P[m].sum(); amps.append(10*np.log10(e+1e-20))
    amps=np.array(amps); return f0,amps-amps.max()
