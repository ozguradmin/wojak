import numpy as np, soundfile as sf, glob, os, scipy.signal as ss
D="/tmp/claude-0/-home-user-wojak/e1bf52df-8e16-5819-ad96-6f6873ef480c/scratchpad/muzik2/motor/hibrit/ext/accordion_hn/Button Accordion HN SFZ+WAV-20240329"
import re
sfz=open(D+"/PRESET Button Accordion HN tuned.sfz").read()
regs=re.findall(r"sample=(Button Accordion HN [^ ]+\.wav) pitch_keycenter=(\d+).*?tune=(-?\d+)\s+loop_start=(\d+) loop_end=(\d+)",sfz,re.S)
for name,kc,tune,ls,le in regs:
    x,sr=sf.read(D+"/"+name); m=x.mean(1)
    kc=int(kc); f0n=440*2**((kc-69)/12)
    seg=m[int(0.5*sr):int(1.3*sr)]
    n=2**18; X=np.abs(np.fft.rfft(seg*np.hanning(len(seg)),n)); f=np.fft.rfftfreq(n,1/sr)
    # find f0 near nominal (try octave too)
    best=None
    for mult in (0.5,1,2):
        lo,hi=f0n*mult*0.95,f0n*mult*1.05; mm=(f>lo)&(f<hi); pk=f[mm][np.argmax(X[mm])]; a=X[mm].max()
        if best is None or a>best[1]: best=(pk,a,mult)
    f0=best[0]
    cents=1200*np.log2(f0/(f0n*best[2]))
    # harmonics
    H=[]
    for k in range(1,13):
        mm=(f>k*f0*0.985)&(f<k*f0*1.015); H.append(20*np.log10(X[mm].max()+1e-12))
    H=np.array(H)-max(H)
    # AM of h1 envelope (beat)
    t=np.arange(len(m))/sr; z=m*np.exp(-2j*np.pi*f0*t); sos=ss.butter(4,40,fs=sr,output='sos'); zb=np.abs(ss.sosfiltfilt(sos,z.real)+1j*ss.sosfiltfilt(sos,z.imag))
    e=20*np.log10(zb[int(0.4*sr):int(1.3*sr)]+1e-9); e=e-e.mean()
    E=np.abs(np.fft.rfft(e*np.hanning(len(e)),2**16)); fe=np.fft.rfftfreq(2**16,1/sr); mm=(fe>1)&(fe<25); beat=fe[mm][np.argmax(E[mm])]
    # rms env attack
    r=np.sqrt(np.convolve(m**2,np.ones(441)/441,'same')); pk=r.max(); i10=np.argmax(r>0.1*pk); i90=np.argmax(r>0.7*pk)
    print(f"{name[20:]:10s} kc {kc} f0 {f0:7.2f} (x{best[2]}) dev {cents:+5.1f}c tune {tune}  beat {beat:4.1f}Hz amstd {e.std():.1f}dB  att10-70 {(i90-i10)/sr*1000:4.0f}ms  H {' '.join(f'{h:4.0f}' for h in H[:10])}  dur {len(m)/sr:.2f} peak {20*np.log10(np.abs(x).max()):.1f}")
