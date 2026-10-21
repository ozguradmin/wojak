import numpy as np, soundfile as sf, sys
S='/tmp/claude-0/-home-user-wojak/e1bf52df-8e16-5819-ad96-6f6873ef480c/scratchpad'; D=S+'/muzik2/analiz/tini'; sr=44100
def hnr(x,f0,lo=500,hi=4400):
    n=2**17; X=np.abs(np.fft.rfft(x*np.hanning(len(x)),n))**2; f=np.fft.rfftfreq(n,1/sr)
    m=(f>=lo)&(f<=hi); kk=f/f0; d=np.abs(kk-np.round(kk))
    harm=m&(d<0.04); val=m&(d>0.25)&(d<0.5)
    return 10*np.log10(X[harm].sum()/X[val].sum()*(val.sum()/harm.sum()))  # per-bin density ratio
y,_=sf.read(S+'/muzik/orijinal.wav'); x=y.mean(1)
print('original held C5 11.75-12.70: harmonic/valley density ratio %.1f dB'%hnr(x[int(11.75*sr):int(12.7*sr)],516.3))
print('original Eb5 7.34-7.56: %.1f dB'%hnr(x[int(7.34*sr):int(7.56*sr)],618.2))
for k in ['R1_tremolo_harmonica','R2_tango_plus_harmonica','R3_clarinet_musette']:
    z,_=sf.read(D+f'/wav/{k}_heldC5.wav'); z=z.mean(1); print(k,'held C5 0.6-1.55: %.1f dB'%hnr(z[int(0.6*sr):int(1.55*sr)],516.3))
