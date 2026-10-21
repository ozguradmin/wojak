import sys, json, numpy as np
sys.path.insert(0, '/tmp/claude-0/-home-user-wojak/e1bf52df-8e16-5819-ad96-6f6873ef480c/scratchpad/muzik2/olcum')
import olcum
R = olcum.ref_features(olcum.REF_WAV)
C = olcum.features(sys.argv[1], with_cqt=False)
mf = np.array(R['melmfcc']['mel_f']); r = np.array(R['melmfcc']['mel_env']); c = np.array(C['melmfcc']['mel_env'])
print('mel f  :', ' '.join(f"{f:5.0f}" for f in mf[::2]))
print('orig   :', ' '.join(f"{v:5.1f}" for v in r[::2]))
print('cand-or:', ' '.join(f"{v:5.1f}" for v in (c - r)[::2]))
print('mfcc orig:', np.round(R['melmfcc']['mfcc_mean'], 1).tolist())
print('mfcc cand:', np.round(C['melmfcc']['mfcc_mean'], 1).tolist())
