import numpy as np, soundfile as sf
S='/tmp/claude-0/-home-user-wojak/e1bf52df-8e16-5819-ad96-6f6873ef480c/scratchpad'
y,sr=sf.read(S+'/muzik/orijinal.wav'); x=y.mean(1)
def cen(a,b,lo=200,hi=4500):
    s=x[int(a*sr):int(b*sr)]; X=np.abs(np.fft.rfft(s*np.hanning(len(s)),8192))**2; f=np.fft.rfftfreq(8192,1/sr); m=(f>=lo)&(f<=hi)
    return (f[m]*X[m]).sum()/X[m].sum(), 10*np.log10(X[m].sum())
bursts=[0.36,0.75,1.47,1.86,2.62,3.04,3.78,4.05]; downs=[0.02,1.08,2.23,3.39]
cb=[cen(b-0.05,b+0.05) for b in bursts]; cd=[cen(d+0.05,d+0.20) for d in downs]
print('beat-1 ("u") centroid Hz:',np.round([c for c,_ in cd]),' median',round(np.median([c for c,_ in cd])))
print('beats 2-3 ("a a") centroid Hz:',np.round([c for c,_ in cb]),' median',round(np.median([c for c,_ in cb])))
print('level diff (a minus u) dB:',round(np.median([l for _,l in cb])-np.median([l for _,l in cd]),1))
