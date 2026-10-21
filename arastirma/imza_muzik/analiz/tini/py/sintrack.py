import numpy as np, scipy.signal as ss
def track(x,sr,nwin=4096,nfft=16384,hop=256,fmin=200,fmax=5000,thr_db=-60,prom=6,maxjump=0.012,minlen=0.15):
    w=np.hanning(nwin); nfr=1+(len(x)-nwin)//hop
    f_bin=sr/nfft
    frames=[]
    ref=None
    specs=[]
    for j in range(nfr):
        seg=x[j*hop:j*hop+nwin]*w
        X=np.abs(np.fft.rfft(seg,nfft)); specs.append(X)
    specs=np.array(specs); ref=specs.max()
    L=20*np.log10(specs/ref+1e-12)
    lo=int(fmin/f_bin); hi=int(fmax/f_bin)
    for j in range(nfr):
        col=L[j]
        pk,_=ss.find_peaks(col[lo:hi],prominence=prom,distance=int(20/f_bin)); pk=pk+lo
        pk=[p for p in pk if col[p]>thr_db]
        fr=[]
        for p in pk:
            a,b,c=col[p-1],col[p],col[p+1]; d=0.5*(a-c)/(a-2*b+c); fr.append(((p+d)*f_bin,b-0.25*(a-c)*d))
        frames.append(fr)
    # link
    tracks=[]; active=[]
    for j,fr in enumerate(frames):
        used=set(); new_active=[]
        for tr in active:
            lf=tr['f'][-1]; best=None; bd=1e9
            for i,(f,a) in enumerate(fr):
                if i in used: continue
                d=abs(f-lf)/lf
                if d<maxjump and d<bd: bd=d; best=i
            if best is not None:
                used.add(best); tr['f'].append(fr[best][0]); tr['a'].append(fr[best][1]); tr['t1']=j; new_active.append(tr)
            else:
                tracks.append(tr)
        for i,(f,a) in enumerate(fr):
            if i not in used: new_active.append(dict(t0=j,t1=j,f=[f],a=[a]))
        active=new_active
    tracks+=active
    out=[]
    for tr in tracks:
        if (tr['t1']-tr['t0']+1)*hop/sr>=minlen:
            tt=(np.arange(tr['t0'],tr['t1']+1)*hop+nwin/2)/sr
            out.append(dict(t=tt,f=np.array(tr['f']),a=np.array(tr['a'])))
    return out,L
