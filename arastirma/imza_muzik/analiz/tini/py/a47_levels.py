import numpy as np, soundfile as sf, scipy.signal as ss
S='/tmp/claude-0/-home-user-wojak/e1bf52df-8e16-5819-ad96-6f6873ef480c/scratchpad'
y,sr=sf.read(S+'/muzik/orijinal.wav'); x=y.mean(1)
def rms(a,b): s=x[int(a*sr):int(b*sr)]; return 10*np.log10(np.mean(s**2))
print('RMS dBFS: intro 0-4.6',round(rms(0,4.6),1),' melody 4.9-11.5',round(rms(4.9,11.5),1),' held C5 11.65-13.7',round(rms(11.65,13.7),1))
for a in np.arange(0,13.7,1.161): print(f'bar@{a:5.2f}: {rms(a,a+1.161):6.1f}',end=' | ')
print()
pk=np.abs(y).max(0); print('sample peaks L,R dBFS',20*np.log10(pk))
print('crest factor dB (peak/RMS, mid)',20*np.log10(np.abs(x).max()/np.sqrt(np.mean(x**2))))
# 50 ms windows crest
w=int(0.05*sr); cf=[20*np.log10(np.abs(x[i:i+w]).max()/np.sqrt(np.mean(x[i:i+w]**2))) for i in range(0,len(x)-w,w)]
print('50ms crest median',np.median(cf).round(1),'p5',np.percentile(cf,5).round(1))
# count samples near max (flat tops)
m=np.abs(y).max(); print('samples within 0.1 dB of max:',int((np.abs(y)>m*10**(-0.1/20)).sum()))
# micro-dynamics: short-term (100 ms) level std in melody section
w=int(0.1*sr); lv=[10*np.log10(np.mean(x[i:i+w]**2)) for i in range(int(4.9*sr),int(11.5*sr)-w,w//2)]
print('100ms level std in melody section',np.std(lv).round(2),'dB; p10-p90',np.round(np.percentile(lv,90)-np.percentile(lv,10),1))
