import numpy as np, soundfile as sf, librosa, scipy.signal as ss
S='/tmp/claude-0/-home-user-wojak/e1bf52df-8e16-5819-ad96-6f6873ef480c/scratchpad'; D=S+'/muzik2/analiz/tini'
y2,sr=sf.read(S+'/muzik/orijinal.wav'); M=y2.mean(1)
# long-term high-res spectrum: welch with 1 s segments -> steady lines stand out; compare with median over time of STFT magnitudes
n=65536
St=np.abs(librosa.stft(M,n_fft=n,hop_length=n//8,window='hann'))
f=librosa.fft_frequencies(sr=sr,n_fft=n)
med=np.median(St,axis=1); mean=St.mean(1)
md=20*np.log10(med+1e-12); 
pk,_=ss.find_peaks(md,prominence=10,distance=8)
pk=[p for p in pk if 60<f[p]<5000]
pk=sorted(pk,key=lambda p:-md[p])[:40]
print('steady (median-over-time) peaks:')
for p in sorted(pk):
    m=librosa.hz_to_midi(f[p]); print(f'{f[p]:8.2f} Hz {librosa.midi_to_note(round(m)):>4} {100*(m-round(m)):+5.0f}c {md[p]-md.max():6.1f} dB  ratio/130.81={f[p]/130.81:6.3f}')
