"""overlay the melody JSON (lead = white boxes, counter = cyan, chords = green ticks) on the CQT of a render."""
import sys, json, numpy as np, soundfile as sf, librosa, matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
sys.path.insert(0,'/tmp/claude-0/-home-user-wojak/e1bf52df-8e16-5819-ad96-6f6873ef480c/scratchpad/muzik2/motor/hibrit')
import render as R
mel, wav, out = sys.argv[1], sys.argv[2], sys.argv[3]
S=R.load_score(mel); x,sr=sf.read(wav); m=x.mean(1)
C=np.abs(librosa.cqt(m,sr=sr,hop_length=256,fmin=librosa.note_to_hz('C3'),n_bins=36*4,bins_per_octave=36))
D=librosa.amplitude_to_db(C,ref=np.max)
fig,ax=plt.subplots(1,1,figsize=(18,7))
ax.imshow(D,origin='lower',aspect='auto',extent=[0,len(m)/sr,48-1/6,48+48-1/6],cmap='magma',vmin=-70,vmax=0)
tc=-21/100  # engine tuning offset
for lst,col in ((S['notes'],'w'),(S['counter'],'c')):
    for n in lst:
        t0=R.tsec(S,S['ab'](n)); d=float(n.get('dur_beats',1))*S['beat_s']
        ax.add_patch(plt.Rectangle((t0,n['midi']+tc-0.5),d,1.0,fill=False,ec=col,lw=1.2))
for c in S['chords']:
    t0=R.tsec(S,S['ab'](c))
    for p in c['midi']: ax.plot([t0,t0+0.15],[p%12+60+tc]*2,color='lime',lw=2)
ax.set_xlim(0,13.9); ax.set_ylim(48,92); ax.set_yticks(range(48,93,12)); ax.set_yticklabels(['C3','C4','C5','C6'])
for b in np.arange(0,14,S['beat_s']*3): ax.axvline(R.tsec(S,0)+b,color='0.5',lw=0.4)
ax.set_title(f"{S['id']}: CQT of {wav.split('/')[-1]}; white = lead notes, cyan = counter, green = chord pitch classes (in C4 octave)")
plt.tight_layout(); plt.savefig(out,dpi=65)
