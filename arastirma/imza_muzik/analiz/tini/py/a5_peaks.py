import numpy as np, soundfile as sf, librosa, scipy.signal as ss
S='/tmp/claude-0/-home-user-wojak/e1bf52df-8e16-5819-ad96-6f6873ef480c/scratchpad'; D=S+'/muzik2/analiz/tini'
y2,sr=sf.read(S+'/muzik/orijinal.wav'); M=y2.mean(1)
print('tuning (frac of bin) librosa:', librosa.estimate_tuning(y=M,sr=sr,n_fft=8192,resolution=0.01))
n=8192; hop=2205  # 50 ms
X=np.abs(librosa.stft(M,n_fft=n,hop_length=hop,window='hann',center=True))
f=librosa.fft_frequencies(sr=sr,n_fft=n); L=20*np.log10(X+1e-12)
out=[]
for j in range(X.shape[1]):
    col=L[:,j]; t=j*hop/sr
    pk,pr=ss.find_peaks(col,prominence=8)
    pk=[p for p in pk if 200<f[p]<1300 and col[p]>col.max()-35]
    s=[]
    for p in pk:
        a,b,c=col[p-1],col[p],col[p+1]; d=0.5*(a-c)/(a-2*b+c); fr=(p+d)*sr/n; amp=b-0.25*(a-c)*d
        m=librosa.hz_to_midi(fr); s.append((fr,m,amp))
    out.append((t,s))
np.save(D+'/peaks.npy',np.array(out,dtype=object),allow_pickle=True)
ref=max(a for t,s in out for _,_,a in s)
for t,s in out[::2]:
    print(f'{t:5.2f} '+' '.join(f'{librosa.midi_to_note(round(m),unicode=False)}{100*(m-round(m)):+.0f}({a-ref:.0f})' for fr,m,a in s))
