import numpy as np, soundfile as sf, scipy.signal as ss, sys
sys.path.insert(0,'/tmp/claude-0/-home-user-wojak/e1bf52df-8e16-5819-ad96-6f6873ef480c/scratchpad/muzik2/analiz/tini/py')
from chain import third_oct, TO
S='/tmp/claude-0/-home-user-wojak/e1bf52df-8e16-5819-ad96-6f6873ef480c/scratchpad'
y,sr=sf.read(S+'/muzik/orijinal.wav'); y=y[:int(13.73*sr)]; L,R=y[:,0],y[:,1]; M=(L+R)/2; Sd=(L-R)/2
sos=ss.butter(4,[400,3000],'bandpass',fs=sr,output='sos')
def env(v,lp=40): return 20*np.log10(np.sqrt(ss.sosfiltfilt(ss.butter(2,lp,fs=sr,output='sos'),ss.sosfiltfilt(sos,v)**2).clip(1e-14)))
em,es=env(M),env(Sd); t=np.arange(len(M))/sr
peaks=[0.36,0.75,1.47,1.86,2.62,3.04,3.78,4.05,4.39]
print('burst  mid_peak  mid slope(dB/s, 30-90ms)  side_peak_lag_ms  side slope(dB/s, peak..+150ms) side drop in 150ms')
sl=[]
for p in peaks:
    i=int(p*sr); w=int(0.08*sr); j=i-w+np.argmax(em[i-w:i+w]); 
    # mid decay after its peak
    a,b=j+int(0.03*sr),j+int(0.09*sr); ms=np.polyfit(t[a:b],em[a:b],1)[0]
    k=j+np.argmax(es[j:j+int(0.1*sr)]); 
    a2,b2=k,k+int(0.15*sr); ss_=np.polyfit(t[a2:b2],es[a2:b2],1)[0]; sl.append(ss_)
    print(f'{t[j]:.3f} {em[j]:6.1f} {ms:8.0f} {1000*(t[k]-t[j]):6.0f} {ss_:8.0f}  {es[k]-es[b2]:5.1f}')
print('median side decay slope dB/s',np.median(sl),' -> RT60 ~',60/abs(np.median(sl)),'s')
Lm=third_oct(M,sr); Ls=third_oct(Sd,sr)
print('1/3-oct side-minus-mid (dB):'); print(' '.join(f'{int(fc)}:{a-b:.1f}' for fc,a,b in zip(TO,Ls,Lm) if 100<=fc<=12500))
