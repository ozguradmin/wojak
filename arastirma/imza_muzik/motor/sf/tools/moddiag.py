import sys, numpy as np
sys.path.insert(0, '/tmp/claude-0/-home-user-wojak/e1bf52df-8e16-5819-ad96-6f6873ef480c/scratchpad/muzik2/olcum')
import olcum
R = olcum.ref_features(olcum.REF_WAV)
e = np.array(R['mod']['edges_hz']); ce = np.sqrt(e[1:] * e[:-1])
Ms = np.array(R['mod']['spec_db'])
print('Hz      ', ' '.join(f"{c:5.1f}" for c in ce))
for b in range(4): print('orig b%d ' % b, ' '.join(f"{v:5.1f}" for v in Ms[b]))
for p in sys.argv[1:]:
    C = olcum.features(p, with_cqt=False); Mc = np.array(C['mod']['spec_db'])
    r = np.corrcoef(Ms.ravel(), Mc.ravel())[0, 1]
    print(p.split('/')[-1], 'r', round(r, 3), 'depth', round(float(np.mean(Mc - Ms)), 2), 'fluct', {k: round(v, 2) for k, v in C['mod']['fluct_rms_db'].items()})
    for b in range(4): print('  d b%d  ' % b, ' '.join(f"{v:+5.1f}" for v in Mc[b] - Ms[b]))
