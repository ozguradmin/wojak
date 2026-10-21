import numpy as np, scipy.signal as ss, sys, json, soundfile as sf
sys.path.insert(0,'/tmp/claude-0/-home-user-wojak/e1bf52df-8e16-5819-ad96-6f6873ef480c/scratchpad/muzik2/analiz/tini/py')
from aday import render_cand, REV; import zincir as Z
D='/tmp/claude-0/-home-user-wojak/e1bf52df-8e16-5819-ad96-6f6873ef480c/scratchpad/muzik2/analiz/tini'
sr=44100
def env_db(v,lo=450,hi=3000):
    b=ss.sosfiltfilt(ss.butter(4,[lo,hi],'bandpass',fs=sr,output='sos'),v)
    return 20*np.log10(np.sqrt(ss.sosfiltfilt(ss.butter(2,30,fs=sr,output='sos'),b**2).clip(1e-14)))
b=0.387
phr=[(0.30,2*b+0.02,72,100),(0.30+2*b,b+0.02,74,100),(0.30+3*b,2*b,75,100)]
cands={'P23':[dict(prog=23)],'P21':[dict(prog=21)],'P22':[dict(prog=22)],'trem_harm_20c':[dict(prog=22),dict(prog=22,detune_c=20)],'P71':[dict(prog=71)],'P20':[dict(prog=20)],'P53':[dict(prog=53)],'P52':[dict(prog=52)],'P40':[dict(prog=40)],'P68':[dict(prog=68)],'tango+harm18':[dict(prog=23),dict(prog=22,detune_c=18,gain_db=-4)],'clar_mus20':[dict(prog=71),dict(prog=71,detune_c=20,gain_db=-1)]}
out={}
for k,L in cands.items():
    x=render_cand(L,phr,2.2); y=Z.chain(x,wow_c=4.5,wet_db=-8,rev=REV,noise=False); m=y.mean(1)
    sf.write(D+f'/wav/phrase_{k}.wav',y.astype(np.float32),sr)
    e=env_db(m); i0=int(0.28*sr); seg=e[i0:i0+int(0.4*sr)]; pk=seg.max(); base=-120
    lin=10**(seg/20); p=10**(pk/20)
    i10=np.argmax(lin>0.1*p); i90=np.argmax(seg>pk-3)
    dips=[]
    for tc in [0.30+2*b,0.30+3*b]:
        i=int(tc*sr); w=int(0.05*sr); dips.append(e[i-w:i+w].min()-np.r_[e[i-3*w:i-w],e[i+w:i+3*w]].mean())
    out[k]=dict(attack_ms=1000*(i90-i10)/sr,dips=dips)
    print(f'{k:14} attack(10%->-3dB) {1000*(i90-i10)/sr:5.0f} ms  legato dips {np.round(dips,1)}')
json.dump(out,open(D+'/attack.json','w'),indent=1)
