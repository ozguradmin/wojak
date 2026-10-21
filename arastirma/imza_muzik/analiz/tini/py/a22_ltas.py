import numpy as np, soundfile as sf, scipy.signal as ss, sys, json, matplotlib
sys.path.insert(0,'/tmp/claude-0/-home-user-wojak/e1bf52df-8e16-5819-ad96-6f6873ef480c/scratchpad/muzik2/analiz/tini/py')
from chain import third_oct, noise_floor, TO
matplotlib.use('Agg'); import matplotlib.pyplot as plt
S='/tmp/claude-0/-home-user-wojak/e1bf52df-8e16-5819-ad96-6f6873ef480c/scratchpad'; D=S+'/muzik2/analiz/tini'
y,sr=sf.read(S+'/muzik/orijinal.wav'); x=y[:int(13.73*sr)].mean(1)
print('rms dBFS (sine ref)',10*np.log10(np.mean(x**2)/0.5))
L=third_oct(x,sr); Ln=noise_floor(x,sr,10); Ln5=noise_floor(x,sr,5)
mx=np.nanmax(L)
print('band  LTAS_rel  LTAS_dBFS  floor10_dBFS floor5  diff')
for fc,a,b,c in zip(TO,L,Ln,Ln5): print(f'{fc:7.0f} {a-mx:7.1f} {a:7.1f} {b:7.1f} {c:7.1f} {a-b:6.1f}')
print('total LTAS dBFS',10*np.log10(np.nansum(10**(L/10))),'floor10 total',10*np.log10(np.nansum(10**(Ln/10))))
json.dump(dict(bands=TO.tolist(),ltas_rel=(L-mx).round(2).tolist(),ltas_dbfs=L.round(2).tolist(),floor_p10_dbfs=np.nan_to_num(Ln,nan=-200).round(2).tolist()),open(D+'/ltas.json','w'))
f,P=ss.welch(x,sr,nperseg=16384)
fig,ax=plt.subplots(1,1,figsize=(14,6))
ax.semilogx(f,10*np.log10(P/P.max()),lw=0.6,label='LTAS fine (Welch 16384, rel max)')
ax.semilogx(TO,L-mx,'o-',label='1/3 oct LTAS (rel max)')
ax.semilogx(TO,Ln-mx,'s--',label='valley floor p10 (same ref)')
ax.set_xlim(20,20000); ax.set_ylim(-110,5); ax.grid(which='both',alpha=.3); ax.legend()
plt.savefig(D+'/png/23_ltas.png',dpi=70)
