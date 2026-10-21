#!/usr/bin/env python3
"""grid-fit the room (stereo) parameters on a fixed pre-chain mix: olcum.stereo_room metrics vs the original's.
usage: fit_room.py <stems_dir>"""
import sys, os, json, itertools
import numpy as np, soundfile as sf
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, ".."))
sys.path.insert(0, os.path.join(HERE, "..", "..", "..", "olcum"))
import render as R
import olcum
P = json.load(open(os.path.join(HERE, "..", "params.json")))
st = sys.argv[1]
a, _ = sf.read(os.path.join(st, "lead.wav")); b, _ = sf.read(os.path.join(st, "acc.wav"))
y0 = (a + b).T
C = P["chain"]
yw = R.apply_wow(y0, C, 1)
import scipy.signal as ss
orig = {"lr": 0.643, "sm": -6.622, "ir": [-3.67, -0.755, -2.588, -16.816, -26.515, -31.446, -35.373, -38.394, -30.931]}

def run(room):
    y = R.apply_room(yw, room, 1)
    sos = ss.butter(C["hpf_order"], C["hpf_hz"], "highpass", fs=R.SR, output="sos")
    y = ss.sosfiltfilt(sos, y, axis=1)
    y = R.transfer_noise(y, C, 1)
    y = R.match_eq(y, P["target_ltas"]["fc"], P["target_ltas"]["db"], dict(C, match_passes=1))
    s = olcum.stereo_room(y.T, int(0.1 * R.SR), y.shape[1] - int(0.1 * R.SR))
    ir = s["ir_env_db"]
    d_ir = float(np.sqrt(np.mean((np.maximum(np.array(ir), -40) - np.maximum(np.array(orig["ir"]), -40)) ** 2)))
    d_st = abs(s["lr_corr"] - orig["lr"]) / 0.15 + abs(max(s["side_mid_db"], -30) - orig["sm"]) / 3
    return d_ir, d_st, s

base = dict(C["room"], tail_db=-42, wet_db=-11)
grid = {"predelay_ms":[6.0,10.0,14.0],"rt60":[0.05,0.07],"build_ms":[6.0,12.0],"wet_db":[-12,-10.5]}

grid0 = {
    "wet_db": [-14, -11, -8],
    "rt60": [0.06, 0.09, 0.13],
    "tail_db": [-45, -38, -30],
    "build_ms": [4.0, 10.0],
}
res = []
keys = list(grid)
for vals in itertools.product(*[grid[k] for k in keys]):
    room = dict(base, **dict(zip(keys, vals)))
    d_ir, d_st, s = run(room)
    sc = 100 / (1 + (d_ir / 6) ** 2) * 6 + 100 / (1 + d_st ** 2) * 6
    res.append((sc, d_ir, d_st, dict(zip(keys, vals)), round(s["lr_corr"], 3), round(s["side_mid_db"], 2), [round(x, 1) for x in s["ir_env_db"]]))
    print(round(sc / 12, 1), round(d_ir, 2), round(d_st, 2), dict(zip(keys, vals)), res[-1][4:], flush=True)
res.sort(key=lambda r: -r[0])
print("BEST")
for r in res[:5]:
    print(r)
