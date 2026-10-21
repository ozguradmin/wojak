import numpy as np, scipy.signal as ss, sys, fluidsynth
sys.path.insert(0,'/tmp/claude-0/-home-user-wojak/e1bf52df-8e16-5819-ad96-6f6873ef480c/scratchpad/muzik2/analiz/tini/py')
from aday import REV; import zincir as Z
from fsr import SF
sr=44100
def env_db(v,lo=450,hi=3000):
    b=ss.sosfiltfilt(ss.butter(4,[lo,hi],'bandpass',fs=sr,output='sos'),v)
    return 20*np.log10(np.sqrt(ss.sosfiltfilt(ss.butter(2,30,fs=sr,output='sos'),b**2).clip(1e-14)))
def rend(prog,notes,total,legato_cc=False,attack_ms=0,det=0):
    fs=fluidsynth.Synth(gain=0.5,samplerate=float(sr),**{'synth.reverb.active':0,'synth.chorus.active':0})
    sf_=fs.sfload(SF); fs.program_select(0,sf_,0,prog); fs.pitch_bend(0,int((-23+det)/200*8192))
    if legato_cc: fs.cc(0,68,127)
    ev=[]
    for st,du,m,v in notes: ev+=[(st,1,m,v),(st+du,0,m,v)]
    ev.sort(key=lambda e:(e[0],-e[1]))
    out=[];t=0.0
    def adv(dt):
        nonlocal t
        n=int(round(dt*sr))
        if n>0: out.append(np.array(fs.get_samples(n),dtype=float)); t+=n/sr
    for et,on,m,v in ev:
        if on and attack_ms>0:
            adv(et-t); fs.cc(0,11,0); fs.noteon(0,m,v)
            steps=8
            for s in range(1,steps+1): adv(attack_ms/1000/steps); fs.cc(0,11,int(127*s/steps))
        else:
            adv(et-t)
            if on: fs.noteon(0,m,v)
            else: fs.noteoff(0,m)
    adv(total-t); fs.delete()
    return np.concatenate(out).reshape(-1,2).mean(1)/32768
b=0.387
for ov in [0.0,0.06,0.12]:
    for leg in [False,True]:
        phr=[(0.30,2*b+ov,72,100),(0.30+2*b,b+ov,74,100),(0.30+3*b,2*b,75,100)]
        x=rend(22,phr,2.2,leg)+10**(-3/20)*rend(22,phr,2.2,leg,det=20)
        y=Z.chain(x,wow_c=4.5,wet_db=-8,rev=REV,noise=False); e=env_db(y.mean(1))
        d=[]
        for tc in [0.30+2*b,0.30+3*b]:
            i=int(tc*sr); w=int(0.05*sr); d.append(e[i-w:i+w].min()-np.r_[e[i-3*w:i-w],e[i+w:i+3*w]].mean())
        print(f'R1 overlap {ov:.2f}s legatoCC68 {leg}: dips {np.round(d,1)}')
x=rend(22,[(0.3,1.0,72,100)],1.6,attack_ms=40); y=Z.chain(x,wow_c=4.5,wet_db=-8,rev=REV,noise=False); e=env_db(y.mean(1))
seg=e[int(0.28*sr):int(0.7*sr)]; pk=seg.max(); lin=10**(seg/20); i10=np.argmax(lin>0.1*10**(pk/20)); i90=np.argmax(seg>pk-3)
print('P22 with 40 ms CC11 ramp: attack(10%->-3dB)',round(1000*(i90-i10)/sr),'ms (orig 45 ms)')
