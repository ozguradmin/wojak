"""average spectral envelope of the Hohner samples (our own source), 1/12-oct bins: is there a fixed body colour?"""
import numpy as np, soundfile as sf, glob, re, matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
D='samples/hohner_cc0/'
sfz=open(D+'PRESET Button Accordion HN tuned.sfz').read().split('trigger=release')[0]
regs=re.findall(r"sample=(Button Accordion HN [^ ]+\.wav) pitch_keycenter=(\d+).*?loop_start=(\d+) loop_end=(\d+)",sfz,re.S)
edges=200*2**(np.arange(0,5.5*12+1)/12); cen=np.sqrt(edges[1:]*edges[:-1])
acc=np.zeros(len(cen)); cnt=np.zeros(len(cen)); rows=[]
for name,kc,ls,le in regs:
    x,sr=sf.read(D+name); m=x.mean(1)[int(ls):int(le)]
    n=2**16; X=np.abs(np.fft.rfft(m[:n]*np.hanning(min(n,len(m))) if len(m)>=n else np.pad(m*np.hanning(len(m)),(0,n-len(m)))))**2; f=np.fft.rfftfreq(n,1/sr)
    f0=440*2**((int(kc)-69)/12)
    hk=[];ha=[]
    for k in range(1,60):
        fk=k*f0
        if fk>edges[-1]: break
        sel=(f>fk*0.97)&(f<fk*1.03); hk.append(fk); ha.append(10*np.log10(X[sel].sum()+1e-20))
    hk=np.array(hk); ha=np.array(ha)
    # remove per-sample smooth trend (1-octave) so only fixed colour remains
    tr=np.array([np.mean(ha[(hk>fk/1.41)&(hk<fk*1.41)]) for fk in hk])
    dev=ha-tr
    for fk,d in zip(hk,dev):
        i=np.searchsorted(edges,fk)-1
        if 0<=i<len(cen): acc[i]+=d; cnt[i]+=1
body=np.where(cnt>0,acc/np.maximum(cnt,1),np.nan)
for c,b,k in zip(cen,body,cnt):
    if 300<c<4000: print(f"{c:6.0f} {b:+5.1f} n={int(k)}")
np.save('py/hn_body.npy',np.array([cen,body,cnt]))
plt.figure(figsize=(10,4)); plt.semilogx(cen,body,'o-'); plt.grid(alpha=.3,which='both'); plt.savefig('png/hn_body.png',dpi=70)
