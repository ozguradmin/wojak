import numpy as np, soundfile as sf, scipy.signal as ss
S='/tmp/claude-0/-home-user-wojak/e1bf52df-8e16-5819-ad96-6f6873ef480c/scratchpad'
y,sr=sf.read(S+'/muzik/orijinal.wav'); y=y[:int(13.73*sr)]; x=y.mean(1)
def dbfs_rms(v): return 10*np.log10(np.mean(v**2)/0.5)   # dB re full-scale sine
for lo,hi,lab in [(1,25,'infrasonic 1-25'),(30,90,'LF 30-90'),(90,110,'100Hz band'),(140,160,'150 band'),(160,240,'160-240'),(250,4000,'music band')]:
    sos=ss.butter(4,[lo,hi],'bandpass',fs=sr,output='sos'); v=ss.sosfiltfilt(sos,x); print(f'{lab:15} {dbfs_rms(v):6.1f} dBFS(sine-ref)')
# sinusoid amplitude of hum lines via long FFT with flat-top
n=len(x); w=ss.windows.flattop(n); X=np.fft.rfft(x*w); f=np.fft.rfftfreq(n,1/sr)
A=2*np.abs(X)/np.sum(w)
for hz in [50,100,150,200,250,93.8,125,187.6]:
    m=(f>hz-1.5)&(f<hz+1.5); i=np.argmax(A*m); print(f'line {f[i]:7.2f} Hz amplitude {20*np.log10(A[i]):6.1f} dBFS(peak)')
# stability: 100 Hz line amplitude in 2 s windows
for t0 in np.arange(0,12,2):
    seg=x[int(t0*sr):int((t0+2)*sr)]; w=ss.windows.flattop(len(seg)); X=np.fft.rfft(seg*w); f=np.fft.rfftfreq(len(seg),1/sr); A=2*np.abs(X)/np.sum(w)
    m=(f>98)&(f<102.5); i=np.argmax(A*m); print(f't {t0:4.1f}: {f[i]:.2f} Hz {20*np.log10(A[i]):.1f} dBFS')
