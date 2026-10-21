import numpy as np, soundfile as sf, sys, librosa
sys.path.insert(0,'/tmp/claude-0/-home-user-wojak/e1bf52df-8e16-5819-ad96-6f6873ef480c/scratchpad/muzik2/analiz/tini/py')
from harm import harmonics
S='/tmp/claude-0/-home-user-wojak/e1bf52df-8e16-5819-ad96-6f6873ef480c/scratchpad'
y,sr=sf.read(S+'/muzik/orijinal.wav'); x=y.mean(1)
notes=[('Eb5a',4.98,5.38,617),('Eb5b',7.34,7.56,617),('D5a',7.58,7.95,582),('Ab5a',8.02,8.44,816),('Ab5b',8.66,9.0,850),('D5b',9.98,10.24,582),('Eb5c',10.25,10.38,617),('C5a',11.75,12.70,516),('C5b',12.9,13.65,516),('G4acc',11.65,12.6,389),('C4acc',0.0,0.25,258)]
print('name   f0     '+' '.join(f'h{k:<4}' for k in range(1,13)))
for nm,a,b,f0g in notes:
    f0,am=harmonics(x,sr,a,b,f0g)
    m=librosa.hz_to_midi(f0)
    print(f'{nm:6} {f0:6.1f} {librosa.midi_to_note(round(m),unicode=False)}{100*(m-round(m)):+3.0f}c '+' '.join(f'{v:5.0f}' for v in am))
