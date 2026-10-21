import numpy as np, soundfile as sf, scipy.signal as ss, matplotlib
matplotlib.use('Agg'); import matplotlib.pyplot as plt
S='/tmp/claude-0/-home-user-wojak/e1bf52df-8e16-5819-ad96-6f6873ef480c/scratchpad'; D=S+'/muzik2/analiz/tini'
y,sr=sf.read(S+'/muzik/orijinal.wav'); x=y.mean(1)
def inst(x,sr,fc,a,b,bw=12,lp=10):
    t=np.arange(len(x))/sr; z=x*np.exp(-2j*np.pi*fc*t); sos=ss.butter(4,bw,fs=sr,output='sos')
    zb=ss.sosfiltfilt(sos,z.real)+1j*ss.sosfiltfilt(sos,z.imag); sel=(t>=a)&(t<=b)
    ph=np.unwrap(np.angle(zb[sel])); fi=fc+np.gradient(ph)*sr/(2*np.pi); fi=ss.sosfiltfilt(ss.butter(2,lp,fs=sr,output='sos'),fi)
    return t[sel],1200*np.log2(fi/fc),20*np.log10(np.abs(zb[sel])+1e-9)
a,b=11.75,12.7
cur={}
for lab,fc in [('C5h1',516),('C5h3',1548),('C5h5',2580),('C5h7',3612),('G4h1',389.3),('G4h2',778.6),('G4h4',1557),('C4h1',258.2),('Eb4?',308)]:
    t,c,am=inst(x,sr,fc,a,b); cur[lab]=(c-np.mean(c),np.mean(am))
labs=list(cur)
C=np.corrcoef([cur[l][0][::200] for l in labs])
print('levels',{l:round(cur[l][1],1) for l in labs})
print('      '+' '.join(f'{l:>6}' for l in labs))
for i,l in enumerate(labs): print(f'{l:>6}'+' '.join(f'{v:6.2f}' for v in C[i]))
print('std cents',{l:round(np.std(cur[l][0]),1) for l in labs})
fig,ax=plt.subplots(1,1,figsize=(16,6))
for l in labs: ax.plot(t[::100],cur[l][0][::100],label=l)
ax.legend(); ax.set_ylim(-60,60); ax.grid(alpha=.3); plt.savefig(D+'/png/17_corr_G4_C5.png',dpi=55)
