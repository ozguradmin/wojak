import sys, numpy as np, scipy.signal as ss
sys.path.insert(0,'/tmp/claude-0/-home-user-wojak/e1bf52df-8e16-5819-ad96-6f6873ef480c/scratchpad/muzik2/olcum')
import olcum as o
SR=44100
for name,path in [('orig',o.REF_WAV),('orig_hiss55','kalib/audio/orijinal_hiss55.wav'),('red_ucuncu','/home/user/wojak/assets/music/imza_vals_ucuncu.m4a'),('cover_fluid','kalib/audio/kapak_orijinal_besteyle_fluid.wav')]:
    y=o.decode(path)[:int(13.7*SR)]; mid=y.mean(1)
    for nper in (8192,2048):
        f,t,Z=ss.stft(mid,SR,nperseg=nper,noverlap=nper*3//4,boundary=None,padded=False); P=np.abs(Z)**2
        res=[]
        for fc in (315,630,1250,2500):
            m=(f>=fc*2**(-1/6))&(f<fc*2**(1/6)); sub=P[m]
            lm=10*np.log10(sub.mean(0)+1e-20); lp=10*np.log10(np.percentile(sub,10,axis=0)+1e-20)
            ok=lm>np.median(lm)-15
            sl=np.polyfit(lm[ok],lp[ok],1)[0]
            res.append(f"{fc}: rel {np.median(lp[ok]-lm[ok]):5.1f} dB slope {sl:4.2f} abs p10 {np.median(lp[ok]):6.1f}")
        print(name, nper, ' | '.join(res))
