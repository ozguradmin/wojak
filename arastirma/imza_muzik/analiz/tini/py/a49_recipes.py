import numpy as np, sys, json, soundfile as sf, scipy.signal as ss, librosa, matplotlib
sys.path.insert(0,'/tmp/claude-0/-home-user-wojak/e1bf52df-8e16-5819-ad96-6f6873ef480c/scratchpad/muzik2/analiz/tini/py')
from aday import evaluate, render_cand, REV; import zincir as Z
matplotlib.use('Agg'); import matplotlib.pyplot as plt
S='/tmp/claude-0/-home-user-wojak/e1bf52df-8e16-5819-ad96-6f6873ef480c/scratchpad'; D=S+'/muzik2/analiz/tini'
orig=json.load(open(D+'/orig_feat.json')); sr=44100
R={'R1_tremolo_harmonica':[dict(prog=22),dict(prog=22,detune_c=20,gain_db=-3)],
   'R2_tango_plus_harmonica':[dict(prog=23),dict(prog=22,detune_c=14,gain_db=-2)],
   'R3_clarinet_musette':[dict(prog=71),dict(prog=71,detune_c=20,gain_db=0)]}
def eq_fir(nodes,n=4097):
    f=np.array([0]+[a for a,b in nodes]+[sr/2]); g=np.array([nodes[0][1]]+[b for a,b in nodes]+[nodes[-1][1]])
    ff=np.linspace(0,sr/2,2049); gg=np.interp(np.log2(np.clip(ff,20,None)),np.log2(np.clip(f,20,None)),g)
    return ss.firwin2(n,ff/(sr/2),10**(gg/20))
b=0.387
phr=[(0.30,2*b+0.05,72,100),(0.30+2*b,b+0.05,74,100),(0.30+3*b,2*b,75,100)]
out={}
y0,_=sf.read(S+'/muzik/orijinal.wav'); seg0=y0[int(11.6*sr):int(13.7*sr)].mean(1)
fig,ax=plt.subplots(4,2,figsize=(20,18))
def spec(a,x,title):
    X=np.abs(librosa.stft(x,n_fft=4096,hop_length=128)); Xd=20*np.log10(X/X.max()+1e-9)
    a.imshow(Xd,origin='lower',aspect='auto',extent=[0,len(x)/sr,0,sr/2],vmin=-70,vmax=0,cmap='magma'); a.set_ylim(0,6000); a.set_title(title)
spec(ax[0,0],seg0,'ORIGINAL held C5 11.6-13.7 s (with accompaniment)')
ax[0,1].axis('off')
for i,(k,L) in enumerate(R.items()):
    r=evaluate(L,orig); fir=eq_fir(r['eq_corr'])
    x=render_cand(L,[(0.05,2.0,72,100)],2.2); y=Z.chain(x,wow_c=4.5,wet_db=-8,rev=REV)
    y=ss.lfilter(fir,1,y,axis=0)[2048:]; y=np.r_[y,np.zeros((2048,2))]
    xp=render_cand(L,phr,2.2); yp=Z.chain(xp,wow_c=4.5,wet_db=-8,rev=REV); yp=ss.lfilter(fir,1,yp,axis=0)[2048:]
    for nm,sig in [('heldC5',y),('phrase',yp)]:
        sig=sig/np.abs(sig).max()*10**(-17/20); sf.write(D+f'/wav/{k}_{nm}.wav',sig.astype(np.float32),sr)
    spec(ax[i+1,0],y.mean(1),f'{k}: held C5 (chain + fitted EQ)'); spec(ax[i+1,1],yp.mean(1),f'{k}: probe phrase C5-D5-Eb5')
    out[k]=dict(layers=L,score=r['score'],env_rms=r['env_rms'],oe=r['oe'],am=r['am'],fm=r['fm'],centroid=r['centroid'],eq_corr=r['eq_corr'],prof=r['prof'])
    print(k,{kk:(round(v,2) if isinstance(v,float) else v) for kk,v in out[k].items() if kk not in('prof','layers')})
plt.tight_layout(); plt.savefig(D+'/png/35_recipes_vs_original.png',dpi=50)
json.dump(out,open(D+'/recipes.json','w'),indent=1)
