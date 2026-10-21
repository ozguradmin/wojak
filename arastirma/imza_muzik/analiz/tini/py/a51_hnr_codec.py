import numpy as np, soundfile as sf, sys
sys.path.insert(0,'/tmp/claude-0/-home-user-wojak/e1bf52df-8e16-5819-ad96-6f6873ef480c/scratchpad/muzik2/analiz/tini/py')
D='/tmp/claude-0/-home-user-wojak/e1bf52df-8e16-5819-ad96-6f6873ef480c/scratchpad/muzik2/analiz/tini'; sr=44100
exec(open(D+'/py/a50_hnr.py').read().split("y,_=sf.read")[0])
import glob
for p in sorted(glob.glob(D+'/codec/*.wav')):
    z,_=sf.read(p); z=z.mean(1); 
    # codec delay: find onset
    i0=np.argmax(np.abs(z)>0.01*np.abs(z).max()); a=i0+int(0.55*sr); 
    print(p.split('/')[-1],'%.1f dB'%hnr(z[a:a+int(0.95*sr)],516.3))
