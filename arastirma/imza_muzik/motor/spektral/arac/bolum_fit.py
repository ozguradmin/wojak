#!/usr/bin/env python3
"""time-resolved spectral fit on the probe (the original's notes/arrangement/grid): per-bar 1/3-octave spectra
(250-4000 Hz, each bar normalised to its own 250-4000 energy) of the probe render vs the original; distance = rms dB over
bars x bands. Constrains the pitch-dependent spectral envelopes of lead and accompaniment and their balance.
usage: bolum_fit.py [--set k=v]  |  bolum_fit.py --fit spec.json [--sweeps 2] [--out params_bolum.json]"""
import sys, os, json, copy, argparse
import numpy as np, scipy.signal as ss
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, ".."))
SP = os.path.abspath(os.path.join(ROOT, "..", ".."))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(SP, "olcum"))
import render as R
import olcum
SONDA = os.path.join(ROOT, "sonda", "sonda_orijinal_transkripsiyon.json")
FCS = [250, 315, 400, 500, 630, 800, 1000, 1250, 1600, 2000, 2500, 3150, 4000]
BAR = 3 * 60 / 151.5
EDGES = [0.02] + [1.036 + BAR * k for k in range(11)] + [13.70]


def bar_spectra(y):
    out = []
    for a, b in zip(EDGES[:-1], EDGES[1:]):
        x = y[int(a * 44100):int(b * 44100)]
        f, P = ss.welch(x, 44100, nperseg=4096)
        L = np.array([P[(f >= fc * 2 ** (-1 / 6)) & (f < fc * 2 ** (1 / 6))].sum() for fc in FCS])
        out.append(10 * np.log10(L / L.sum() + 1e-12))
    return np.array(out)


ORIG = None


def orig():
    global ORIG
    if ORIG is None:
        ORIG = bar_spectra(olcum.decode(olcum.REF_WAV).mean(1))
    return ORIG


def measure(P):
    Q = copy.deepcopy(P)
    y = R.render(SONDA, 1, Q, quiet=True).mean(0)
    C = bar_spectra(y)
    d = np.maximum(C, -35) - np.maximum(orig(), -35)
    return {"rms": float(np.sqrt(np.mean(d ** 2))), "intro": float(np.sqrt(np.mean(d[:4] ** 2))),
            "mel": float(np.sqrt(np.mean(d[4:10] ** 2))), "end": float(np.sqrt(np.mean(d[10:] ** 2))),
            "band": np.sqrt(np.mean(d ** 2, 0)).round(1).tolist(), "mean_band": d.mean(0).round(1).tolist()}, C


def show(o):
    return f"rms {o['rms']:.2f} (intro {o['intro']:.2f} mel {o['mel']:.2f} end {o['end']:.2f}) band-bias {o['mean_band']}"


def get(P, key):
    d = P
    for p in key.split("."):
        d = d[int(p)] if isinstance(d, list) else d[p]
    return d


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--set", action="append", default=[])
    ap.add_argument("--fit")
    ap.add_argument("--sweeps", type=int, default=2)
    ap.add_argument("--params", default=os.path.join(ROOT, "params.json"))
    ap.add_argument("--out", default=os.path.join(ROOT, "params_bolum.json"))
    a = ap.parse_args()
    P = json.load(open(a.params))
    for s in a.set:
        R.set_param(P, s)
    o, C = measure(P)
    print(show(o), flush=True)
    if a.fit:
        spec = json.load(open(a.fit))
        best = o
        steps = {k: s for k, s, lo, hi in spec}
        for sw in range(a.sweeps):
            for key, _, lo, hi in spec:
                st = steps[key]
                improved = False
                for direction in (+1, -1):
                    while True:
                        Q = copy.deepcopy(P)
                        v0 = get(Q, key)
                        v = min(hi, max(lo, round(v0 + direction * st, 4)))
                        if v == v0:
                            break
                        R.set_param(Q, f"{key}={json.dumps(v)}")
                        oo, CC = measure(Q)
                        ok = oo["rms"] < best["rms"] - 0.01
                        print(f"sw{sw} {key} {v0}->{v}: {show(oo)} {'ACCEPT' if ok else ''}", flush=True)
                        if ok:
                            P, best, improved = Q, oo, True
                            json.dump(P, open(a.out, "w"), indent=1)
                        else:
                            break
                    if improved:
                        break
                if not improved:
                    steps[key] = st / 2
            print(f"== sweep {sw}: {show(best)}", flush=True)
        json.dump(P, open(a.out, "w"), indent=1)
