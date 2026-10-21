import numpy as np, soundfile as sf, scipy.signal as ss, matplotlib
matplotlib.use('Agg'); import matplotlib.pyplot as plt
S='/tmp/claude-0/-home-user-wojak/e1bf52df-8e16-5819-ad96-6f6873ef480c/scratchpad'; D=S+'/muzik2/analiz/tini'
y,sr=sf.read(S+'/muzik/orijinal.wav'); y=y[:int(13.73*sr)]; x=y.mean(1)
for lo,hi in [(4500,11000),(6000,15000)]:
    v=ss.sosfiltfilt(ss.butter(6,[lo,hi],'bandpass',fs=sr,output='sos'),x)
    e=np.abs(ss.hilbert(v)); med=ss.medfilt(e[::8],101); 
    r=e[::8]/(med+1e-12)
    pk,_=ss.find_peaks(r,height=6,distance=int(0.01*sr/8))
    print(f'band {lo}-{hi}: kurtosis {((v-v.mean())**4).mean()/v.var()**2:.1f}, rms {20*np.log10(v.std()*np.sqrt(2)):.1f} dBFS, spikes>6x median: {len(pk)} -> per s {len(pk)/13.73:.1f}')
    if lo==4500: times=np.array(pk)*8/sr; print('spike times',np.round(times[:40],3))
# sample-domain click detector on mid: residual of LPC prediction
import numpy.linalg as la
seg=x
p=24
from scipy.linalg import solve_toeplitz
r=np.correlate(seg[:sr*4],seg[:sr*4],'full')[sr*4-1:sr*4-1+p+1]
a=solve_toeplitz(r[:p],r[1:p+1])
pred=np.convolve(seg,np.r_[0,a],'full')[:len(seg)]
res=seg-pred; rs=np.abs(res); mad=np.median(rs)
z=rs/(mad*1.4826)
pk,_=ss.find_peaks(z,height=10,distance=int(0.005*sr))
print('LPC residual spikes z>10:',len(pk),'per s',len(pk)/13.73, 'max z',z.max())
print('times',np.round(np.array(pk)/sr,3)[:40])
