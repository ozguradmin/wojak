#!/usr/bin/env python3
"""note-level fit of the LEAD reed model to the original's per-note measurements (analiz/tini/orig_feat.json:
harmonic profiles of C5/D5/Eb5/Ab5, AM/FM/centroid on the held C5, odd-even index), with the method of tini/py/aday.py:
single notes rendered through the chain (warp off: the original's windows avoid the warp bumps; match EQ frozen to the
curve the full test render gets), then
  score = env_resid (after the best smooth EQ + per-note gains) + 0.5|d odd-even| + |d AM| + 0.5|d FM|/3 + 0.5|d centroid| (semitones)
usage: nota_fit.py [--set k=v ...]          -> prints metrics
       nota_fit.py --fit spec.json           -> coordinate descent, writes params_nota.json"""
import sys, os, json, copy, argparse, tempfile
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, ".."))
SP = os.path.abspath(os.path.join(ROOT, "..", ".."))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(SP, "analiz", "tini", "py"))
import render as R
import ozellik as O
ORIG = json.load(open(os.path.join(SP, "analiz", "tini", "orig_feat.json")))
TP = {k: (v[0], {int(kk): vv for kk, vv in v[1].items()}) for k, v in ORIG["prof"].items()}
WIN = {"C5": (0.60, 1.55), "D5": (0.40, 0.66), "Eb5": (0.40, 0.62), "Ab5": (0.40, 0.82)}
DUR = {"C5": 2.0, "D5": 0.9, "Eb5": 0.9, "Ab5": 0.9}
MIDI = {"C5": 72, "D5": 74, "Eb5": 75, "Ab5": 80}
TMP = tempfile.mkdtemp(prefix="notafit_", dir=os.path.join(ROOT, "out"))


def frozen_eq(P):
    """the match-EQ curve the full test render receives with these parameters"""
    R.render(os.path.join(SP, "deneme", "deneme_melodi.json"), 1, copy.deepcopy(P), quiet=True)
    return [R.LAST_EQ["fc"], R.LAST_EQ["db"]]


def note_audio(P, nm, eq):
    Q = copy.deepcopy(P)
    Q["chain"]["warp"] = None
    Q["chain"]["fixed_eq"] = eq
    Q["global"]["timing_jitter_ms"] = 0.0
    Q["global"]["arch_db"] = 0.0
    js = {"id": nm, "tempo_bpm": 60, "pickup_beats": 0.05, "notes": [{"bar": 1, "beat": 1, "dur_beats": DUR[nm], "midi": MIDI[nm], "vel": 90}],
          "chords": [], "accomp": {"pattern": ""}}
    p = os.path.join(TMP, nm + ".json")
    json.dump(js, open(p, "w"))
    Q["global"]["max_len_s"] = DUR[nm] + 0.5
    Q["global"]["end_by_s"] = DUR[nm] + 0.49
    y = R.render(p, 1, Q, quiet=True)
    return y.mean(0)


SONDA = os.path.join(ROOT, "sonda", "sonda_orijinal_transkripsiyon.json")
OWIN = {"C5": (11.75, 12.70), "D5": (9.98, 10.24), "Eb5": (7.34, 7.56), "Ab5": (8.02, 8.44)}   # tini's windows on the original
MODE = {"sonda": False}


def measure_sonda(P):
    """same windows as on the original, on the probe (the original's notes + arrangement + beat grid, full chain;
    warp off because the original's windows avoid its warp bumps)"""
    Q = copy.deepcopy(P)
    Q["chain"]["warp"] = None
    Q["global"]["timing_jitter_ms"] = 0.0
    x = R.render(SONDA, 1, Q, quiet=True).mean(0)
    prof, res = {}, {}
    for nm, (a, b) in OWIN.items():
        f0g = TP[nm][0] * 2 ** ((P["global"]["tuning_cents"] + 23) / 1200)
        f0c, p = O.profile(x, a, b, f0g)
        prof[nm] = (f0c, p)
        if nm == "C5":
            res["am"], res["fm"] = O.am_fm(x, a, b, f0c)
            res["centroid"] = O.centroid(x, a, b)
    return prof, res


def measure(P, eq=None):
    if MODE["sonda"]:
        prof, res = measure_sonda(P)
        return finish(prof, res)
    eq = eq or frozen_eq(P)
    prof, res = {}, {}
    for nm in WIN:
        x = note_audio(P, nm, eq)
        a, b = WIN[nm]
        f0g = R.midi_hz(MIDI[nm], P["global"]["tuning_cents"])
        f0c, p = O.profile(x, a, b, f0g)
        prof[nm] = (f0c, p)
        if nm == "C5":
            res["am"], res["fm"] = O.am_fm(x, a, b, f0c)
            res["centroid"] = O.centroid(x, a, b)
    return finish(prof, res)


def finish(prof, res):
    res["env"], _ = O.env_fit(TP, prof)
    res["oe"] = float(np.mean([O.oe_index(v[1]) for v in prof.values()]))
    res["prof"] = {k: {kk: round(float(vv), 1) for kk, vv in v[1].items()} for k, v in prof.items()}
    d_oe = abs(res["oe"] - ORIG["oe"]); d_am = abs(res["am"] - ORIG["am"]); d_fm = abs(res["fm"] - ORIG["fm"]) / 3
    d_cen = abs(np.log2(res["centroid"] / ORIG["centroid"])) * 12
    res["score"] = res["env"] + 0.5 * d_oe + d_am + 0.5 * d_fm + 0.5 * d_cen
    return res


def show(r):
    return (f"score {r['score']:.2f} | env {r['env']:.2f} oe {r['oe']:.1f} (8.4) am {r['am']:.2f} (4.25) fm {r['fm']:.1f} (13.5) "
            f"cen {r['centroid']:.0f} (1919)")


def get(P, key):
    d = P
    for p in key.split("."):
        d = d[int(p)] if isinstance(d, list) else d[p]
    return d


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--set", action="append", default=[])
    ap.add_argument("--fit")
    ap.add_argument("--params", default=os.path.join(ROOT, "params.json"))
    ap.add_argument("--sweeps", type=int, default=2)
    ap.add_argument("--sonda", action="store_true", help="measure on the probe at the original's windows (with accompaniment)")
    ap.add_argument("--out", default=os.path.join(ROOT, "params_nota.json"))
    a = ap.parse_args()
    MODE["sonda"] = a.sonda
    P = json.load(open(a.params))
    for s in a.set:
        R.set_param(P, s)
    eq = None if a.sonda else frozen_eq(P)
    r = measure(P, eq)
    print(show(r))
    print("orig", {k: {kk: round(vv, 1) for kk, vv in v[1].items()} for k, v in TP.items()})
    print("cand", r["prof"])
    if a.fit:
        spec = json.load(open(a.fit))
        best = r
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
                        o = measure(Q, eq)
                        ok = o["score"] < best["score"] - 0.02
                        print(f"sw{sw} {key} {v0}->{v}: {show(o)} {'ACCEPT' if ok else ''}", flush=True)
                        if ok:
                            P, best, improved = Q, o, True
                        else:
                            break
                    if improved:
                        break
                if not improved:
                    steps[key] = st / 2
            print(f"== sweep {sw}: {show(best)}", flush=True)
        print("cand", best["prof"])
        json.dump(P, open(a.out, "w"), indent=1)
