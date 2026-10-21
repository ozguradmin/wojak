import numpy as np, pickle, scipy.signal as ss
D='/tmp/claude-0/-home-user-wojak/e1bf52df-8e16-5819-ad96-6f6873ef480c/scratchpad/muzik2/analiz/tini'
tr=pickle.load(open(D+'/tracks.pkl','rb'))
hop_s=256/44100.
rows=[]
for t in tr:
    dur=t['t'][-1]-t['t'][0]
    if dur<0.45 or np.median(t['a'])<-45: continue
    c=1200*np.log2(t['f']/np.median(t['f']))
    # detrend with 2nd order poly (slow drift) 
    x=np.arange(len(c)); p=np.polyfit(x,c,2); r=c-np.polyval(p,x)
    drift=np.polyval(p,x); drift_range=drift.max()-drift.min()
    # spectrum of r
    n=4096; R=np.abs(np.fft.rfft(r*np.hanning(len(r)),n)); fr=np.fft.rfftfreq(n,hop_s)
    m=(fr>2)&(fr<14); k=np.argmax(R[m]); rate=fr[m][k]
    depth=np.sqrt(2)*np.std(r)   # peak cents for sinusoid
    # amplitude modulation of this partial
    a=t['a']; ar=a-np.polyval(np.polyfit(x,a,2),x)
    A=np.abs(np.fft.rfft(ar*np.hanning(len(ar)),n)); ka=np.argmax(A[m]); arate=fr[m][ka]
    rows.append((t['t'][0],dur,np.median(t['f']),np.median(a),rate,depth,drift_range,arate,np.sqrt(2)*np.std(ar)))
rows=np.array(rows)
print('n long tracks',len(rows))
print(' t0   dur   f_med  amp  vibHz depth_c drift_c  AMHz AMdB')
for r in rows[np.argsort(-rows[:,3])][:45]: print(' '.join(f'{v:6.2f}' for v in r))
w=10**(rows[:,3]/20)
for lo,hi in [(200,480),(480,1000),(1000,2000),(2000,4500)]:
    m=(rows[:,2]>=lo)&(rows[:,2]<hi)
    if m.sum()==0: continue
    print(f'band {lo}-{hi}: n={m.sum()} vib rate median {np.median(rows[m,4]):.2f} Hz (IQR {np.percentile(rows[m,4],25):.2f}-{np.percentile(rows[m,4],75):.2f}), depth median {np.median(rows[m,5]):.1f} c, AM rate {np.median(rows[m,7]):.2f}, AM depth {np.median(rows[m,8]):.2f} dB')
hist,edges=np.histogram(rows[:,4],bins=np.arange(2,14.5,0.5),weights=w); print('vib-rate histogram (amp weighted):'); print(' '.join(f'{e:.1f}:{h/hist.sum()*100:.0f}' for e,h in zip(edges,hist)))
np.save(D+'/vibrows.npy',rows)
