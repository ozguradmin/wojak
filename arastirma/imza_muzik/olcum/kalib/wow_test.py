import sys, numpy as np, scipy.signal as ss, soundfile as sf
sys.path.insert(0,'/tmp/claude-0/-home-user-wojak/e1bf52df-8e16-5819-ad96-6f6873ef480c/scratchpad/muzik2/olcum')
import olcum as o
SR=44100
def common_drift(pt, use_median=True):
    nfr=len(pt['t']); hop=pt['hop_s']
    num=np.zeros(nfr); den=np.zeros(nfr); lists=[[] for _ in range(nfr)]
    t_index={round(x,6):i for i,x in enumerate(pt['t'])}
    for tr in pt['tracks']:
        c=1200*np.log2(tr['f']); w=10**((tr['a']-pt['gmax'])/20)
        fi=np.searchsorted(pt['t'], tr['t'])
        d=np.diff(c)
        for k in range(len(d)):
            lists[fi[k+1]].append((d[k], w[k+1]))
    v=np.zeros(nfr); n=np.zeros(nfr)
    for i,L in enumerate(lists):
        if len(L)>=2:
            a=np.array(L); n[i]=len(L)
            if use_median:
                o_=np.argsort(a[:,0]); cw=np.cumsum(a[o_,1])/a[:,1].sum(); v[i]=a[o_,0][np.searchsorted(cw,0.5)]
            else: v[i]=np.average(a[:,0],weights=a[:,1])
    curve=np.cumsum(v)
    sos=ss.butter(2,0.2,'highpass',fs=1/hop,output='sos'); curve=ss.sosfiltfilt(sos,curve)
    return curve, n
def wowify(x, depth_c, rate):
    n=len(x); t=np.arange(n)/SR
    cents=depth_c*np.sin(2*np.pi*rate*t)
    ratio=2**(cents/1200); pos=np.cumsum(ratio); pos=pos-pos[0]
    return np.stack([np.interp(pos,np.arange(n),x[:,c]) for c in range(x.shape[1])],1)
for name,path,dep in [('orig',o.REF_WAV,0),('cover_fluid','kalib/audio/kapak_orijinal_besteyle_fluid.wav',0),('cover+sine30c@0.5','kalib/audio/kapak_orijinal_besteyle_fluid.wav',30),('red_ucuncu','/home/user/wojak/assets/music/imza_vals_ucuncu.m4a',0)]:
    y=o.decode(path)[:int(13.77*SR)]
    if dep: y=wowify(y,dep,0.5)
    pt=o.peaks_and_tracks(y.mean(1),0,13.7)
    for med in (True,False):
        c,n=common_drift(pt,med)
        X=np.abs(np.fft.rfft(c))**2; fx=np.fft.rfftfreq(len(c),pt['hop_s'])
        m=(fx>0.2)&(fx<3); fpk=fx[m][np.argmax(X[m])]
        print(f"{name:20s} median={med} std {np.std(c):5.1f} c  p5/p95 {np.percentile(c,5):6.1f}/{np.percentile(c,95):6.1f}  peak {fpk:.2f} Hz  mean tracks/frame {n.mean():.1f}")
