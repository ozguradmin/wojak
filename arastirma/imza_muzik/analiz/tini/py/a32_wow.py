import numpy as np, scipy.signal as ss, pickle
from fractions import Fraction
D='/tmp/claude-0/-home-user-wojak/e1bf52df-8e16-5819-ad96-6f6873ef480c/scratchpad/muzik2/analiz/tini'
tr=pickle.load(open(D+'/tracks.pkl','rb'))
long=[t for t in tr if t['t'][-1]-t['t'][0]>0.5 and np.median(t['a'])>-40]
hop=256/44100; sos=ss.butter(2,6,fs=1/hop,output='sos')
rat=sorted(set(p/q for p in range(1,10) for q in range(1,10) if p>=q))
def prep(c):
    n=len(c); c=c-np.polyval(np.polyfit(np.arange(n),c,1),np.arange(n)); return ss.sosfiltfilt(sos,c)
real=[];null=[];stds=[]
for i in range(len(long)):
    for j in range(len(long)):
        if i==j: continue
        a,b=long[i],long[j]
        r=np.median(a['f'])/np.median(b['f']); 
        if r<1: continue
        if min(abs(r/q-1) for q in rat)<0.012: continue
        t0=max(a['t'][0],b['t'][0]); t1=min(a['t'][-1],b['t'][-1])
        if t1-t0<0.4: continue
        sa=(a['t']>=t0)&(a['t']<=t1); sb=(b['t']>=t0)&(b['t']<=t1); n=min(sa.sum(),sb.sum())
        ca=prep(1200*np.log2(a['f'][sa][:n])); cb=prep(1200*np.log2(b['f'][sb][:n]))
        real.append(np.corrcoef(ca,cb)[0,1]); stds+= [np.std(ca),np.std(cb)]
# null: pair tracks that do not overlap, align by start
for i in range(len(long)):
    for j in range(len(long)):
        a,b=long[i],long[j]
        if i==j or not (a['t'][0]>b['t'][-1]+0.3): continue
        n=min(len(a['f']),len(b['f']))
        if n*hop<0.4: continue
        null.append(np.corrcoef(prep(1200*np.log2(a['f'][:n])),prep(1200*np.log2(b['f'][:n])))[0,1])
real=np.array(real); null=np.array(null)
print('overlapping non-harmonic pairs:',len(real),'mean r',real.mean().round(3),'median',np.median(real).round(3))
print('null (non-overlapping) pairs:',len(null),'mean r',null.mean().round(3),'sd',null.std().round(3))
print('slow pitch deviation std (cents) median',np.median(stds).round(1))
