import json, sys
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
SP='/tmp/claude-0/-home-user-wojak/e1bf52df-8e16-5819-ad96-6f6873ef480c/scratchpad/muzik2'
NN=['C','Db','D','Eb','E','F','F#','G','Ab','A','Bb','B']
ref=json.load(open(SP+'/analiz/muzik.json'))
pieces=[('ORIGINAL (transcription)',ref['melody'],[{'bar':h['bar'],'beat':h['beat'],'roman':h['roman'].split(' ')[0]} for h in ref['harmony']],[])]
for p in ['b1/b1-1','b1/b1-2','b1/b1-3','b1/b1-4','b2/b2-1','b2/b2-2','b2/b2-3','b2/b2-4']:
    d=json.load(open(f'{SP}/besteler/{p}.json'))
    chs=[]; last=None
    for c in d['chords']:
        r=c.get('roman',c.get('chord','')).split(' ')[0]
        key=(c['bar'],r)
        if key!=last: chs.append({'bar':c['bar'],'beat':c['beat'],'roman':r}); last=key
    pieces.append((d['id']+'  '+d.get('title',''),d['notes'],chs,d.get('counter') or []))
fig,axs=plt.subplots(len(pieces),1,figsize=(16,3.0*len(pieces)))
for ax,(t,notes,chs,ctr) in zip(axs,pieces):
    for n in ctr:
        x=3*n['bar']+n['beat']-1; ax.add_patch(plt.Rectangle((x,n['midi']-0.4),n['dur_beats']*0.95,0.8,color='#9c9',alpha=0.6))
    for n in notes:
        x=3*n['bar']+n['beat']-1
        dur=min(n['dur_beats'],36-x)
        ax.add_patch(plt.Rectangle((x,n['midi']-0.4),dur*0.95,0.8,color='#1565c0'))
        ax.text(x+0.02,n['midi']+0.5,NN[n['midi']%12],fontsize=6)
    for b in range(0,13): ax.axvline(3*b,color='#888',lw=0.6)
    for c in chs:
        ax.text(3*c['bar']+c['beat']-1+0.05,61.2,c['roman'],fontsize=7,color='#b00')
    ax.set_xlim(1,36); ax.set_ylim(60.5,89)
    ax.set_yticks(range(60,90,2)); ax.set_yticklabels([NN[m%12]+str(m//12-1) for m in range(60,90,2)],fontsize=7)
    ax.set_xticks([3*b for b in range(13)]); ax.set_xticklabels([f'bar {b}' for b in range(13)],fontsize=7)
    ax.set_title(t,fontsize=9,loc='left'); ax.grid(axis='y',alpha=0.2)
plt.tight_layout(); plt.savefig(SP+'/besteler/yargi/rulo_hepsi.png',dpi=70)
