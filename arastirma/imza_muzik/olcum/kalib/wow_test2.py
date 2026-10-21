import sys, numpy as np, scipy.signal as ss
sys.path.insert(0,'/tmp/claude-0/-home-user-wojak/e1bf52df-8e16-5819-ad96-6f6873ef480c/scratchpad/muzik2/olcum')
sys.path.insert(0,'/tmp/claude-0/-home-user-wojak/e1bf52df-8e16-5819-ad96-6f6873ef480c/scratchpad/muzik2/olcum/kalib')
import olcum as o
from wow_test import wowify
SR=44100
def band_curves(pt, bands=((240,470),(480,940),(1400,2500))):
    cents=1200*np.log2(pt['pk_f']/440.0); d=(cents+50)%100-50; th=2*np.pi*d/100
    wl=10**((pt['pk_a']-pt['gmax'])/20); nfr=len(pt['t'])
    zall=np.sum(wl*np.exp(1j*th)); off=np.angle(zall)
    hop=pt['hop_s']; k=int(round(0.2/hop))|1; win=np.hanning(k+2)[1:-1]
    out=[]
    for lo,hi in bands:
        m=(pt['pk_f']>=lo)&(pt['pk_f']<hi)
        zr=np.bincount(pt['pk_fr'][m],(wl*np.cos(th-off))[m],nfr); zi=np.bincount(pt['pk_fr'][m],(wl*np.sin(th-off))[m],nfr); W=np.bincount(pt['pk_fr'][m],wl[m],nfr)
        zs=np.convolve(zr,win,'same')+1j*np.convolve(zi,win,'same'); Ws=np.convolve(W,win,'same')
        c=np.angle(zs)*100/(2*np.pi); c[Ws<0.05*np.median(Ws[Ws>0])]=np.nan
        out.append(c)
    return np.array(out), off*100/(2*np.pi)
for name,path,dep in [('orig',o.REF_WAV,0),('cover_fluid','kalib/audio/kapak_orijinal_besteyle_fluid.wav',0),('cover+sine30c@0.5','kalib/audio/kapak_orijinal_besteyle_fluid.wav',30),('red_ucuncu','/home/user/wojak/assets/music/imza_vals_ucuncu.m4a',0),('orig_p2','kalib/audio/orijinal_p2.wav',0)]:
    y=o.decode(path)[:int(13.77*SR)]
    if dep: y=wowify(y,dep,0.5)
    pt=o.peaks_and_tracks(y.mean(1),0,13.7)
    C,off=band_curves(pt)
    ok=~np.isnan(C).any(0)
    r01=np.corrcoef(C[0,ok],C[1,ok])[0,1]; r02=np.corrcoef(C[0,ok],C[2,ok])[0,1]; r12=np.corrcoef(C[1,ok],C[2,ok])[0,1]
    common=np.nanmean(C,0)
    print(f"{name:20s} offset {off:6.1f}  band std {np.nanstd(C,1).round(1)}  r(lo,mid) {r01:.2f} r(lo,hi) {r02:.2f} r(mid,hi) {r12:.2f}  common std {np.nanstd(common):.1f} p5/p95 {np.nanpercentile(common,5):.0f}/{np.nanpercentile(common,95):.0f}  valid {ok.mean():.2f}")
    if name=='orig':
        np.save('kalib/orig_band_curves.npy',C); np.save('kalib/orig_t.npy',pt['t'])
