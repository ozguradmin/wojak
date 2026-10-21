import numpy as np, warnings, logging; logging.disable(logging.WARNING); warnings.filterwarnings('ignore')
from basic_pitch.inference import predict, Model
from basic_pitch import ICASSP_2022_MODEL_PATH
import os, librosa, json
S='/tmp/claude-0/-home-user-wojak/e1bf52df-8e16-5819-ad96-6f6873ef480c/scratchpad'; D=S+'/muzik2/analiz/tini'
mp=os.path.join(os.path.dirname(ICASSP_2022_MODEL_PATH),'nmp.onnx')
m=Model(mp)
out,midi,notes=predict(S+'/muzik/orijinal.wav',m,onset_threshold=0.4,frame_threshold=0.25,minimum_note_length=80,minimum_frequency=60,maximum_frequency=2000,multiple_pitch_bends=True,melodia_trick=True)
np.save(D+'/bp_note.npy',out['note']); np.save(D+'/bp_contour.npy',out['contour'])
notes=sorted(notes,key=lambda n:(n[0],-n[2]))
js=[]
for s,e,p,a,b in notes:
    js.append(dict(start=round(float(s),3),end=round(float(e),3),pitch=int(p),name=librosa.midi_to_note(int(p),unicode=False),amp=round(float(a),3)))
json.dump(js,open(D+'/bp_notes.json','w'),indent=0)
for n in js: print(n['start'],n['end'],n['name'],n['amp'])
midi.write(D+'/bp_notes.mid')
