import numpy as np, soundfile as sf, sys, json, librosa, matplotlib
sys.path.insert(0,'/tmp/claude-0/-home-user-wojak/e1bf52df-8e16-5819-ad96-6f6873ef480c/scratchpad/muzik2/analiz/tini/py')
from eslestir import match_fir, apply; from chain import third_oct, TO
matplotlib.use('Agg'); import matplotlib.pyplot as plt
S='/tmp/claude-0/-home-user-wojak/e1bf52df-8e16-5819-ad96-6f6873ef480c/scratchpad'; D=S+'/muzik2/analiz/tini'; sr=44100
lt=json.load(open(D+'/ltas.json')); target=np.array(lt['ltas_rel'])
z,_=sf.read(D+'/wav/fullprobe_R1.wav')
fir,curve=match_fir(z,target); zz=apply(z,fir)
L0=third_oct(z.mean(1),sr); L1=third_oct(zz.mean(1),sr)
print('band target before after')
for fc,t,a,b in zip(TO,target,L0-np.nanmax(L0),L1-np.nanmax(L1)):
    if 160<=fc<=12500: print(f'{fc:6.0f} {t:6.1f} {a:6.1f} {b:6.1f}')
sf.write(D+'/wav/fullprobe_R1_matched.wav',(zz/np.abs(zz).max()*0.14).astype(np.float32),sr)
y0,_=sf.read(S+'/muzik/orijinal.wav'); o=y0[int(11.3*sr):int(13.7*sr)].mean(1)
fig,ax=plt.subplots(2,1,figsize=(16,10))
for a,x,t in [(ax[0],o,'ORIGINAL 11.3-13.7'),(ax[1],zz.mean(1)[:int(2.4*sr)],'R1 full probe after 1/3-oct LTAS match EQ')]:
    X=np.abs(librosa.stft(x,n_fft=4096,hop_length=128)); Xd=20*np.log10(X/X.max()+1e-9)
    a.imshow(Xd,origin='lower',aspect='auto',extent=[0,len(x)/sr,0,sr/2],vmin=-70,vmax=0,cmap='magma'); a.set_ylim(0,8000); a.set_title(t)
plt.tight_layout(); plt.savefig(D+'/png/37_matched_probe.png',dpi=50)
