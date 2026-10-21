import numpy as np, soundfile as sf, librosa, matplotlib, sys
matplotlib.use('Agg'); import matplotlib.pyplot as plt
S='/tmp/claude-0/-home-user-wojak/e1bf52df-8e16-5819-ad96-6f6873ef480c/scratchpad'; D=S+'/muzik2/analiz/tini'
p=sys.argv[1]; name=sys.argv[2]
y,sr=sf.read(p); x=y.mean(1) if y.ndim>1 else y
nwin=4096; nfft=32768; hop=441
w=np.hanning(nwin); f=np.fft.rfftfreq(nfft,1/sr)
cands=440*2**((np.arange(60*10,86*10)/10-69)/12)  # 10 cents grid MIDI 60..86
res=[]
for j in range(0,len(x)-nwin,hop):
    X=np.abs(np.fft.rfft(x[j:j+nwin]*w,nfft)); L=np.log(X+1e-9*X.max()+1e-12)
    sal=np.zeros(len(cands))
    for k,wt in zip(range(1,6),[1,0.8,0.7,0.5,0.4]):
        idx=np.round(cands*k*nfft/sr).astype(int); sal+=wt*L[idx]
    i=np.argmax(sal); 
    res.append((j/sr+nwin/2/sr,cands[i],sal[i]))
res=np.array(res); np.save(D+f'/{name}_f0.npy',res)
fig,ax=plt.subplots(1,1,figsize=(24,8))
m=librosa.hz_to_midi(res[:,1])
ax.scatter(res[:,0],m,s=3,c=res[:,2],cmap='viridis')
for n in range(60,87): ax.axhline(n-0.25,color='gray',lw=0.4)
ax.set_yticks(np.arange(60,87)-0.25); ax.set_yticklabels([librosa.midi_to_note(n,unicode=False) for n in range(60,87)],fontsize=7)
ax.set_xticks(np.arange(0,14,0.387)); ax.tick_params(axis='x',labelsize=7); ax.grid(axis='x',alpha=.3)
ax.set_ylim(66,82); ax.set_title('dominant f0 (harmonic sum), grid = notes at -25 cents')
plt.tight_layout(); plt.savefig(D+f'/png/{name}.png',dpi=55)
