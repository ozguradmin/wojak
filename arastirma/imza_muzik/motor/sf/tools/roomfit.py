"""fit room params to the original's stereo/reverb numbers using olcum's own stereo_room(); measurement only"""
import sys, json, itertools, numpy as np, soundfile as sf
sys.path.insert(0, '/tmp/claude-0/-home-user-wojak/e1bf52df-8e16-5819-ad96-6f6873ef480c/scratchpad/muzik2/olcum')
sys.path.insert(0, '/tmp/claude-0/-home-user-wojak/e1bf52df-8e16-5819-ad96-6f6873ef480c/scratchpad/muzik2/motor/sf')
import olcum, render as R
ref = olcum.ref_features(olcum.REF_WAV)
rs = ref['stereo']; print('orig', round(rs['lr_corr'],3), round(rs['side_mid_db'],2), [round(v,1) for v in rs['ir_env_db']])
D = '/tmp/claude-0/-home-user-wojak/e1bf52df-8e16-5819-ad96-6f6873ef480c/scratchpad/muzik2/motor/sf/out/stems_v03/'
x = sum(sf.read(D + f + '.wav')[0] for f in ('lead', 'accomp', 'counter'))
x = x[:int(13.7 * R.SR)]
base = dict(R.CFG['chain']['room'])
xw = R.apply_wow(np.stack([x, x], 1), R.CFG['chain']['wow'], 1)[0][:, 0]
grid = json.loads(sys.argv[1]) if len(sys.argv) > 1 else {}
keys = list(grid)
res = []
for vals in itertools.product(*[grid[k] for k in keys]):
    Rm = dict(base); Rm.update(dict(zip(keys, vals)))
    y = R.apply_room(xw, Rm, 1)
    st = olcum.stereo_room(y, int(0.1 * R.SR), int(13.6 * R.SR))
    ir = np.maximum(np.array(st['ir_env_db']), -40); ro = np.maximum(np.array(rs['ir_env_db']), -40)
    d_ir = float(np.sqrt(np.mean((ir - ro) ** 2)))
    d_st = abs(st['lr_corr'] - rs['lr_corr']) / 0.15 + abs(st['side_mid_db'] - rs['side_mid_db']) / 3
    sc = 6 * 100 / (1 + (d_ir / 6) ** 2) + 6 * 100 / (1 + d_st ** 2)
    res.append((sc, dict(zip(keys, vals)), round(st['lr_corr'], 3), round(st['side_mid_db'], 2), round(d_ir, 2), [round(v, 1) for v in st['ir_env_db']]))
res.sort(key=lambda r: -r[0])
for r in res[:8]: print(round(r[0], 1), r[1:])
