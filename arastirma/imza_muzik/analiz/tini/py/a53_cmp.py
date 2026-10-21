import numpy as np, soundfile as sf, librosa, matplotlib
matplotlib.use('Agg'); import matplotlib.pyplot as plt
S='/tmp/claude-0/-home-user-wojak/e1bf52df-8e16-5819-ad96-6f6873ef480c/scratchpad'; D=S+'/muzik2/analiz/tini'; sr=44100
y0,_=sf.read(S+'/muzik/orijinal.wav'); o=y0[int(11.3*sr):int(13.7*sr)].mean(1)
fig,ax=plt.subplots(3,1,figsize=(16,15))
def spec(a,x,t):
    X=np.abs(librosa.stft(x,n_fft=4096,hop_length=128)); Xd=20*np.log10(X/X.max()+1e-9)
    a.imshow(Xd,origin='lower',aspect='auto',extent=[0,len(x)/sr,0,sr/2],vmin=-70,vmax=0,cmap='magma'); a.set_ylim(0,6000); a.set_title(t)
spec(ax[0],o,'ORIGINAL 11.3-13.7 s')
for i,k in enumerate(['R1','R2']):
    z,_=sf.read(D+f'/wav/fullprobe_{k}.wav'); spec(ax[i+1],z.mean(1)[:int(2.4*sr)],f'{k} full probe: held C5 + oom-pah-pah (acc -10 dB), chain')
plt.tight_layout(); plt.savefig(D+'/png/36_fullprobe_vs_original.png',dpi=50)
