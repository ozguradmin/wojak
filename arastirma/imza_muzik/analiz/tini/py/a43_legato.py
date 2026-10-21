import numpy as np, soundfile as sf, scipy.signal as ss, sys, json, librosa
sys.path.insert(0,'/tmp/claude-0/-home-user-wojak/e1bf52df-8e16-5819-ad96-6f6873ef480c/scratchpad/muzik2/analiz/tini/py')
S='/tmp/claude-0/-home-user-wojak/e1bf52df-8e16-5819-ad96-6f6873ef480c/scratchpad'; D=S+'/muzik2/analiz/tini'
y,sr=sf.read(S+'/muzik/orijinal.wav'); x=y.mean(1)
f0=np.load(D+'/20_f0_dominant_f0.npy')  # t, f, sal
t=f0[:,0]; m=librosa.hz_to_midi(f0[:,1])+0.23; mr=np.round(m)
# melody region only (section B) and in 5th octave
sel=(t>4.8)&(t<11.6)&(mr>=71)&(mr<=82)
# median filter notes
mm=ss.medfilt(np.where(sel,mr,0),9)
ch=[i for i in range(1,len(mm)) if mm[i]!=mm[i-1] and mm[i]>0 and mm[i-1]>0]
trans=[t[i] for i in ch]
print('melody transitions',np.round(trans,2))
def env_db(v,lo=450,hi=3000):
    b=ss.sosfiltfilt(ss.butter(4,[lo,hi],'bandpass',fs=sr,output='sos'),v)
    return 20*np.log10(np.sqrt(ss.sosfiltfilt(ss.butter(2,30,fs=sr,output='sos'),b**2).clip(1e-14)))
e=env_db(x); 
def dips(e,times):
    out=[]
    for tc in times:
        i=int(tc*sr); w=int(0.05*sr); 
        lo=e[i-w:i+w].min(); ref=np.r_[e[i-3*w:i-w],e[i+w:i+3*w]].mean(); out.append(lo-ref)
    return np.array(out)
d=dips(e,trans); print('orig legato dip dB: median',np.median(d).round(1),'IQR',np.percentile(d,25).round(1),np.percentile(d,75).round(1))
# null: random times
rng=np.random.default_rng(0); rt=rng.uniform(5,11.5,200); dn=dips(e,rt); print('random-time dip median',np.median(dn).round(1))
# melody entrance rise at ~4.9 s
seg=e[int(4.80*sr):int(5.10*sr)]; tt=np.arange(len(seg))/sr+4.8
pk=seg.max(); base=np.percentile(e[int(4.5*sr):int(4.85*sr)],50)
i10=np.argmax(seg>base+0.1*(pk-base)); i90=np.argmax(seg>pk-3)
print(f'melody entrance: base {base:.1f} peak {pk:.1f} dB, rise (10%->-3dB) {1000*(i90-i10)/sr:.0f} ms from {tt[i10]:.3f}s')
json.dump(dict(trans=trans,dip_median=float(np.median(d)),dip_null=float(np.median(dn))),open(D+'/legato_orig.json','w'))
