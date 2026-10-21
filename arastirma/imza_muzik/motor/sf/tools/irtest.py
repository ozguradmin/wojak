import sys, numpy as np, soundfile as sf
sys.path.insert(0, '/tmp/claude-0/-home-user-wojak/e1bf52df-8e16-5819-ad96-6f6873ef480c/scratchpad/muzik2/olcum')
sys.path.insert(0, '/tmp/claude-0/-home-user-wojak/e1bf52df-8e16-5819-ad96-6f6873ef480c/scratchpad/muzik2/motor/sf')
import olcum, render as R
D = '/tmp/claude-0/-home-user-wojak/e1bf52df-8e16-5819-ad96-6f6873ef480c/scratchpad/muzik2/motor/sf/out/stems_v03/'
x = sum(sf.read(D + f + '.wav')[0] for f in ('lead', 'accomp', 'counter'))[:int(13.7 * R.SR)]
Rm = dict(R.CFG['chain']['room']); Rm.update(pd_ms=8, rt60=0.07, wet_db=-11.5, tail_db=-80)
rng = np.random.default_rng(0)
for nm, sig, wow in (('music+wow', x, 1), ('music', x, 0), ('noise', rng.standard_normal(len(x)) * 0.05, 0)):
    y = R.apply_room(sig, Rm, 1)
    if wow: y, _ = R.apply_wow(y, R.CFG['chain']['wow'], 1)
    st = olcum.stereo_room(y, int(0.1 * R.SR), int(13.6 * R.SR))
    print(nm, round(st['lr_corr'], 3), round(st['side_mid_db'], 2), [round(v, 1) for v in st['ir_env_db']])
print('--- wow before room, cluster room')
Rm.update(pd_ms=2, cluster_ms=16, cluster_w_ms=4, rt60=0.03)
xw, _ = R.apply_wow(np.stack([x, x], 1), R.CFG['chain']['wow'], 1)
for nm, sig in (('wow->room', xw[:, 0]), ('room only', x)):
    y = R.apply_room(sig, Rm, 1)
    st = olcum.stereo_room(y, int(0.1 * R.SR), int(13.6 * R.SR))
    print(nm, round(st['lr_corr'], 3), round(st['side_mid_db'], 2), [round(v, 1) for v in st['ir_env_db']])
