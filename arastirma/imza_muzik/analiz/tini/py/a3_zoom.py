import numpy as np, soundfile as sf, librosa, librosa.display, matplotlib
matplotlib.use('Agg'); import matplotlib.pyplot as plt
S='/tmp/claude-0/-home-user-wojak/e1bf52df-8e16-5819-ad96-6f6873ef480c/scratchpad'; D=S+'/muzik2/analiz/tini'
y2,sr=sf.read(S+'/muzik/orijinal.wav'); M=y2.mean(1)
hop=128; bpo=60; fmin=librosa.note_to_hz('A2')
C=np.abs(librosa.cqt(M,sr=sr,hop_length=hop,fmin=fmin,n_bins=int(5.5*bpo),bins_per_octave=bpo,filter_scale=2))
Cd=librosa.amplitude_to_db(C,ref=np.max)
np.save(D+'/cqt60.npy',C)
segs=[(0,4.7),(4.5,9.2),(9.0,13.77)]
for k,(a,b) in enumerate(segs):
    fig,ax=plt.subplots(1,1,figsize=(20,11))
    librosa.display.specshow(Cd,sr=sr,hop_length=hop,x_axis='time',y_axis='cqt_note',fmin=fmin,bins_per_octave=bpo,ax=ax,vmin=-60,cmap='magma')
    ax.set_xlim(a,b)
    # grid at bars (beat 0.387) with phase from first onset 0.0
    for x in np.arange(0,14,0.387): ax.axvline(x,color='c',alpha=0.25,lw=0.8)
    ax.set_xticks(np.arange(np.ceil(a*10)/10,b,0.2))
    ax.grid(axis='y',alpha=0.3,color='w')
    ax.set_yticks(librosa.note_to_hz(['C3','G3','C4','Eb4','G4','C5','Eb5','G5','C6','G6','C7','G7']))
    ax.set_yticklabels(['C3','G3','C4','Eb4','G4','C5','Eb5','G5','C6','G6','C7','G7'])
    plt.tight_layout(); plt.savefig(D+f'/png/04_cqt_zoom{k+1}.png',dpi=60)
