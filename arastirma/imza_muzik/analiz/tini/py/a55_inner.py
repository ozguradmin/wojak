import numpy as np, soundfile as sf, scipy.signal as ss, pickle
S='/tmp/claude-0/-home-user-wojak/e1bf52df-8e16-5819-ad96-6f6873ef480c/scratchpad'; D=S+'/muzik2/analiz/tini'
tr=pickle.load(open(D+'/tracks.pkl','rb'))
# durations of tracks by register (fundamental-ish ranges)
for lo,hi,lab in [(240,480,'C4-B4 (accomp/inner)'),(480,900,'C5-A5 (melody)')]:
    d=[t['t'][-1]-t['t'][0] for t in tr if lo<=np.median(t['f'])<hi and np.median(t['a'])>-35]
    d=np.array(d); print(f'{lab}: n={len(d)} median dur {np.median(d):.2f}s, p90 {np.percentile(d,90):.2f}s, >0.6 s: {(d>0.6).sum()}')
y,sr=sf.read(S+'/muzik/orijinal.wav'); x=y.mean(1); t=np.arange(len(x))/sr
for fc,a,b in [(388.2,9.3,10.9),(258,0.0,0.7),(298,1.05,2.1),(345,3.7,4.5)]:
    z=x*np.exp(-2j*np.pi*fc*t); sos=ss.butter(4,12,fs=sr,output='sos'); zb=ss.sosfiltfilt(sos,z.real)+1j*ss.sosfiltfilt(sos,z.imag)
    sel=(t>=a)&(t<=b); e=20*np.log10(np.abs(zb[sel])+1e-9)
    seg=e[::441]; print(f'{fc} Hz {a}-{b}s: env (10 ms steps, dB) min {seg.min():.1f} max {seg.max():.1f} p10 {np.percentile(seg,10):.1f} p90 {np.percentile(seg,90):.1f}  frac within 10 dB of max {(seg>seg.max()-10).mean():.2f}')
