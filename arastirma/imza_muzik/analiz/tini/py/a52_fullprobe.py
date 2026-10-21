import numpy as np, sys, json, soundfile as sf, scipy.signal as ss
sys.path.insert(0,'/tmp/claude-0/-home-user-wojak/e1bf52df-8e16-5819-ad96-6f6873ef480c/scratchpad/muzik2/analiz/tini/py')
from aday import render_cand, REV; import zincir as Z
D='/tmp/claude-0/-home-user-wojak/e1bf52df-8e16-5819-ad96-6f6873ef480c/scratchpad/muzik2/analiz/tini'; sr=44100
exec(open(D+'/py/a50_hnr.py').read().split("y,_=sf.read")[0])
b=0.387; T=2.4
acc=[]
for bar,(oom,pah) in enumerate([(48,[63,67]),(50,[65,68]),(48,[63,67])]):
    t0=0.1+bar*3*b
    acc.append((t0,0.30,oom,90)); acc.append((t0,0.30,oom+12,80))
    for bt in (1,2):
        for m in pah: acc.append((t0+bt*b,0.10,m,85))
lead=[(0.1,3*b*3-0.05,72,100)]
for accdb in [-6,-10,-14]:
    for nm,L in [('R1',[dict(prog=22),dict(prog=22,detune_c=20,gain_db=-3)]),('R2',[dict(prog=23),dict(prog=22,detune_c=14,gain_db=-2)])]:
        xl=render_cand(L,lead,3.8); xa=render_cand([dict(prog=23)],acc,3.8)
        rl=np.sqrt(np.mean(xl[int(0.5*sr):int(3*sr)]**2)); ra=np.sqrt(np.mean(xa[int(0.5*sr):int(3*sr)]**2))
        x=xl+xa*(rl/ra)*10**(accdb/20)
        y=Z.chain(x,wow_c=4.5,wet_db=-8,rev=REV); m=y.mean(1)
        print(f'acc {accdb:3d} dB {nm}: HNR held C5 (0.6-1.55 s) {hnr(m[int(0.6*sr):int(1.55*sr)],516.3):5.1f} dB')
        if accdb==-10: sf.write(D+f'/wav/fullprobe_{nm}.wav',(y/np.abs(y).max()*0.14).astype(np.float32),sr)
