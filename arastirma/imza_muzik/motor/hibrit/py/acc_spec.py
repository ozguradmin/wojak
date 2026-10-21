import numpy as np, soundfile as sf, matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
D="/tmp/claude-0/-home-user-wojak/e1bf52df-8e16-5819-ad96-6f6873ef480c/scratchpad/muzik2/motor/hibrit/ext/accordion_hn/Button Accordion HN SFZ+WAV-20240329/"
H="/tmp/claude-0/-home-user-wojak/e1bf52df-8e16-5819-ad96-6f6873ef480c/scratchpad/muzik2/motor/hibrit/"
names=[('B3',47),('D4',50),('G4',55),('B4',59),('C5',60),('D5',62),('E5',64),('G5',67),('A5',69),('C6',72)]
fig,ax=plt.subplots(len(names),1,figsize=(14,2.0*len(names)))
for a,(nm,kc) in zip(ax,names):
    x,sr=sf.read(D+f"Button Accordion HN {nm}.wav"); m=x.mean(1); seg=m[int(0.5*sr):int(1.3*sr)]
    n=2**17; X=20*np.log10(np.abs(np.fft.rfft(seg*np.hanning(len(seg)),n))+1e-9); f=np.fft.rfftfreq(n,1/sr); X-=X.max()
    a.plot(f,X,lw=0.5); f0=440*2**((kc-69)/12)
    for k in range(1,40): a.axvline(k*f0,color='r',lw=0.3,alpha=0.5)
    a.set_xlim(50,6000); a.set_ylim(-90,0); a.set_xscale('log'); a.set_title(f"{nm} kc={kc} nominal f0={f0:.1f}",fontsize=8)
plt.tight_layout(); plt.savefig(H+"png/acc_samples_spec.png",dpi=80)
