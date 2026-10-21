import numpy as np, soundfile as sf, sys, json, librosa, matplotlib
sys.path.insert(0,'/tmp/claude-0/-home-user-wojak/e1bf52df-8e16-5819-ad96-6f6873ef480c/scratchpad/muzik2/analiz/tini/py')
from harm import harmonics
matplotlib.use('Agg'); import matplotlib.pyplot as plt
S='/tmp/claude-0/-home-user-wojak/e1bf52df-8e16-5819-ad96-6f6873ef480c/scratchpad'; D=S+'/muzik2/analiz/tini'
y,sr=sf.read(S+'/muzik/orijinal.wav'); x=y.mean(1)
bp=json.load(open(D+'/bp_notes.json'))
segs=[]
for n in bp:
    if n['pitch']>=70 and n['end']-n['start']>=0.18 and n['amp']>=0.3:
        segs.append((n['start']+0.03,n['end']-0.02,librosa.midi_to_hz(n['pitch'])*2**(-23/1200),n['name']))
# add manual ones
segs+= [(11.75,12.7,516.3,'C5'),(12.9,13.65,529,'C5b'),(8.02,8.44,817.6,'Ab5'),(8.66,9.0,846,'Ab5b'),(9.98,10.24,583,'D5'),(7.34,7.56,618,'Eb5')]
rows=[]
for a,b,f0g,nm in segs:
    f0,am=harmonics(x,sr,a,b,f0g,K=9)
    for k,v in enumerate(am,1):
        fr=k*f0
        if fr<4400: rows.append((len(rows) and 0, nm, a, f0, k, fr, v))
# build design: note offsets + E(f) bins (1/6 oct) + H(k)
notes=sorted(set((r[2]) for r in rows)); ni={t:i for i,t in enumerate(notes)}
fb=np.exp(np.linspace(np.log(240),np.log(4400),18)); 
def fbin(fr): return int(np.clip(np.searchsorted(fb,fr)-1,0,len(fb)-2))
Y=np.array([r[6] for r in rows])
def fit(useE,useH):
    cols=len(notes)+(len(fb)-1 if useE else 0)+(9 if useH else 0)
    A=np.zeros((len(rows),cols))
    for i,r in enumerate(rows):
        A[i,ni[r[2]]]=1; c=len(notes)
        if useE: A[i,c+fbin(r[5])]=1; c+=len(fb)-1
        if useH: A[i,c+r[4]-1]=1
    coef,res,rk,sv=np.linalg.lstsq(A,Y,rcond=None); pred=A@coef
    return np.sqrt(np.mean((Y-pred)**2)),coef,A.shape[1]
print('n notes',len(notes),'n points',len(rows))
for useE,useH,lab in [(0,0,'offset only'),(1,0,'E(f) fixed filter'),(0,1,'H(k) harmonic-number'),(1,1,'E(f)+H(k)')]:
    rms,coef,p=fit(useE,useH); print(f'{lab:22} rms resid {rms:5.2f} dB  params {p}')
rms,coef,p=fit(1,1)
E=coef[len(notes):len(notes)+len(fb)-1]; H=coef[len(notes)+len(fb)-1:]
print('E(f) [Hz:dB]:',' '.join(f'{np.sqrt(fb[i]*fb[i+1]):.0f}:{E[i]-E.max():.1f}' for i in range(len(E))))
print('H(k) [k:dB]:',' '.join(f'{k+1}:{H[k]-H.max():.1f}' for k in range(9)))
rmsE,coefE,_=fit(1,0); E1=coefE[len(notes):]
print('E(f) only:',' '.join(f'{np.sqrt(fb[i]*fb[i+1]):.0f}:{E1[i]-E1.max():.1f}' for i in range(len(E1))))
rmsH,coefH,_=fit(0,1); H1=coefH[len(notes):]
print('H(k) only:',' '.join(f'{k+1}:{H1[k]-H1.max():.1f}' for k in range(9)))
json.dump(dict(E_hz=[float(np.sqrt(fb[i]*fb[i+1])) for i in range(len(E))],E_db=(E-E.max()).round(2).tolist(),H_db=(H-H.max()).round(2).tolist()),open(D+'/srcfilt.json','w'))
fig,ax=plt.subplots(1,2,figsize=(16,6))
ax[0].semilogx([np.sqrt(fb[i]*fb[i+1]) for i in range(len(E))],E-E.max(),'o-'); ax[0].set_title('fixed-frequency envelope E(f) (joint fit)'); ax[0].grid(which='both',alpha=.3)
ax[1].bar(range(1,10),H-H.max()); ax[1].set_title('harmonic-number term H(k) (joint fit)'); ax[1].grid(alpha=.3)
plt.savefig(D+'/png/28_source_filter.png',dpi=60)
