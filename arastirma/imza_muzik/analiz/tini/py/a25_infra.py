import numpy as np, soundfile as sf, scipy.signal as ss, matplotlib
matplotlib.use('Agg'); import matplotlib.pyplot as plt
S='/tmp/claude-0/-home-user-wojak/e1bf52df-8e16-5819-ad96-6f6873ef480c/scratchpad'; D=S+'/muzik2/analiz/tini'
y,sr=sf.read(S+'/muzik/orijinal.wav'); y=y[:int(13.73*sr)]; x=y.mean(1)
lp=ss.sosfiltfilt(ss.butter(4,25,fs=sr,output='sos'),x)
lpL=ss.sosfiltfilt(ss.butter(4,25,fs=sr,output='sos'),y[:,0]); lpR=ss.sosfiltfilt(ss.butter(4,25,fs=sr,output='sos'),y[:,1])
bp=ss.sosfiltfilt(ss.butter(4,[250,4000],'bandpass',fs=sr,output='sos'),x)
env=np.sqrt(ss.sosfiltfilt(ss.butter(2,25,fs=sr,output='sos'),bp**2).clip(0))
d=lambda v: ss.decimate(ss.decimate(v,10),10)
a,b=d(lp),d(env); b=b-b.mean()
print('corr infra vs env',np.corrcoef(a,b)[0,1], ' infra L/R corr',np.corrcoef(lpL,lpR)[0,1])
for lag in [-40,-20,-10,0,10,20,40]:
    print(lag, np.corrcoef(np.roll(a,lag),b)[0,1])
print('DC offset',x.mean(),' L',y[:,0].mean(),' R',y[:,1].mean())
t=np.arange(len(x))/sr
fig,ax=plt.subplots(2,1,figsize=(16,7),sharex=True)
ax[0].plot(t[::100],lp[::100]); ax[0].set_title('infrasonic <25 Hz (mid)'); ax[1].plot(t[::100],env[::100]); ax[1].set_title('music env 250-4k')
plt.savefig(D+'/png/25_infrasonic.png',dpi=55)
# waveform asymmetry
print('peak+ ',x.max(),' peak- ',x.min(),' skew',((x-x.mean())**3).mean()/x.std()**3)
