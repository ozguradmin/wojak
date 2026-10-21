import numpy as np, scipy.signal as ss, sys, json
sys.path.insert(0,'/tmp/claude-0/-home-user-wojak/e1bf52df-8e16-5819-ad96-6f6873ef480c/scratchpad/muzik2/analiz/tini/py')
from aday import render_cand, REV; import zincir as Z
sr=44100
def env_db(v,lo=900,hi=4000):
    b=ss.sosfiltfilt(ss.butter(4,[lo,hi],'bandpass',fs=sr,output='sos'),v)
    return 20*np.log10(np.sqrt(ss.sosfiltfilt(ss.butter(2,80,fs=sr,output='sos'),b**2).clip(1e-14)))
res={}
for nm,L,dur in [('P21 accordion',[dict(prog=21)],0.12),('P23 tango',[dict(prog=23)],0.12),('P23 tango 0.08',[dict(prog=23)],0.08),('P22 harmonica',[dict(prog=22)],0.12),('P20 reed organ',[dict(prog=20)],0.12),('P71 clarinet',[dict(prog=71)],0.12),('P48 strings',[dict(prog=48)],0.12),('P52 choir',[dict(prog=52)],0.12),('P0 piano',[dict(prog=0)],0.12),('P24 nylon gtr',[dict(prog=24)],0.12),('P45 pizz',[dict(prog=45)],0.12),('P46 harp',[dict(prog=46)],0.12),('P6 harpsichord',[dict(prog=6)],0.12),('P61 brass',[dict(prog=61)],0.12)]:
    notes=[(0.2,dur,m,90) for m in (67,72,75)]
    x=render_cand(L,notes,1.0); y=Z.chain(x,wow_c=4.5,wet_db=-8,rev=REV,noise=False); m=y.mean(1)
    e=env_db(m); j=np.argmax(e); pk=e[j]
    pre=e[:j]; post=e[j:]
    a10=j-np.where(pre<pk-10)[0][-1]; d10=np.argmax(post<pk-10); d20=np.argmax(post<pk-20)
    res[nm]=(1000*a10/sr,1000*d10/sr,1000*d20/sr)
    print(f'{nm:16} attack(-10dB->peak) {1000*a10/sr:5.0f} ms  decay(peak->-10dB) {1000*d10/sr:5.0f} ms  (->-20dB) {1000*d20/sr:5.0f} ms')
print('ORIGINAL intro bursts: attack median 48 (16-72) ms, decay median 55 (19-76) ms')
