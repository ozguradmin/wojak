import numpy as np, scipy.signal as ss
TO=np.array([20,25,31.5,40,50,63,80,100,125,160,200,250,315,400,500,630,800,1000,1250,1600,2000,2500,3150,4000,5000,6300,8000,10000,12500,16000,20000])
def stft_pow(x,sr,n=8192,hop=2048):
    w=np.hanning(n); norm=(np.sum(w)**2)/2  # full-scale sine -> peak bin power ~1 ... use energy norm below
    fr=np.fft.rfftfreq(n,1/sr); F=[]
    for j in range(0,len(x)-n,hop):
        X=np.abs(np.fft.rfft(x[j:j+n]*w))**2; F.append(X)
    F=np.array(F)
    # normalise so that sum over bins = mean-square of signal * n ... Parseval with window: sum|X|^2 = n*sum(x^2 w^2)
    F=F*2/(n*np.sum(w**2))   # sum over bins ~ mean square *2 (one-sided)
    return fr,F
def bands(fr,F,agg='sum',pct=None):
    out=[]
    for fc in TO:
        lo,hi=fc/2**(1/6),fc*2**(1/6); m=(fr>=lo)&(fr<hi)
        if m.sum()==0: out.append(np.full(F.shape[0],np.nan)); continue
        if pct is None: out.append(F[:,m].sum(1))
        else: out.append(np.percentile(F[:,m],pct,axis=1)*m.sum())
    return np.array(out).T
def third_oct(x,sr):
    fr,F=stft_pow(x,sr); B=bands(fr,F); return 10*np.log10(np.nanmean(B,0)/0.5+1e-20)   # dB re full-scale sine (ms 0.5)
def noise_floor(x,sr,pct=10):
    fr,F=stft_pow(x,sr,n=4096,hop=1024); B=bands(fr,F,pct=pct); return 10*np.log10(np.nanmedian(B,0)/0.5+1e-20)
