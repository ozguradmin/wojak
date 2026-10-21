#!/usr/bin/env python3
"""evaluate a parameter variant on the test melody and on the transcription probe with olcum.py internals
(no CQT, no PNG): prints TIMBRE per melody, mean, and sub-scores.
usage: deg.py [--set k=v ...] [--only deneme|sonda] [--save tag]   (python API: evaluate(P) -> dict)"""
import sys, os, json, copy, argparse, time
import numpy as np, soundfile as sf
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, ".."))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "..", "..", "olcum"))
import render as R
import olcum
MELS = {"deneme": os.path.join(ROOT, "..", "..", "deneme", "deneme_melodi.json"),
        "sonda": os.path.join(ROOT, "sonda", "sonda_orijinal_transkripsiyon.json")}
_REF = None
BOLUM_W = 4.0          # ... and - BOLUM_W * per-bar 1/3-oct spectral rms on the probe (dB)
INTRO_W = 4.0          # objective = mean TIMBRE - INTRO_W * intro envelope rms (dB): keeps the accompaniment on the measured intro


def ref():
    global _REF
    if _REF is None:
        _REF = olcum.ref_features(olcum.REF_WAV)
    return _REF


def one(args):
    name, P, seed, save = args
    y = R.render(MELS[name], seed, P, quiet=True)
    path = os.path.join(ROOT, "out", f"_eval_{name}_{os.getpid()}.wav" if not save else f"{save}_{name}.wav")
    sf.write(path, y.T.astype(np.float32), R.SR, subtype="FLOAT")
    C = olcum.features(path, with_cqt=False)
    cm = olcum.compare(ref(), C)
    if not save:
        os.remove(path)
    keep = {k: cm[k] for k in olcum.TIMBRE_WEIGHTS}
    intro = None
    if name == "sonda":
        import intro_fit
        intro = float(np.sqrt(np.mean((intro_fit.profile(y.mean(0)) - intro_fit.orig_profile()) ** 2)))
        import bolum_fit
        Cb = bolum_fit.bar_spectra(y.mean(0))
        bolum = float(np.sqrt(np.mean((np.maximum(Cb, -35) - np.maximum(bolum_fit.orig(), -35)) ** 2)))
    else:
        bolum = None
    det = {"flat": C["spec"]["flatness_core_median"], "vib": (C["pitch"] or {}).get("vibrato_rms_c"),
           "peaky": (C["pitch"] or {}).get("vibrato_peakiness"), "instab": (C["pitch"] or {}).get("pitch_dev_band_std_c"),
           "coh": (C["pitch"] or {}).get("pitch_dev_coherence_r"), "spread": (C["pitch"] or {}).get("partial_spread_c"),
           "lr": C["stereo"]["lr_corr"], "crest": C["level"]["crest50_median_db"], "lstd": C["level"]["rms100_std_db"],
           "fast": C["level"]["fast_fluct_std_db"], "LRA": C["loud"].get("LRA"),
           "acc_c": C["accent"]["contrast_db"], "acc_b": C["accent"]["balance_db"], "acc_l": C["accent"]["level_contrast_db"],
           "mod_r": cm["modulation_r"], "mod_d": cm["modulation_depth_db"], "nf": cm["noise_floor_signed_db"], "intro": intro, "bolum": bolum}
    return name, cm["TIMBRE_SCORE"], cm["subscores"], keep, det


def evaluate(P, names=("deneme", "sonda"), seed=1, save=None, pool=None):
    jobs = [(n, P, seed, save) for n in names]
    if pool is not None and len(jobs) > 1:
        res = pool.map(one, jobs)
    else:
        res = [one(j) for j in jobs]
    out = {"mean": float(np.mean([r[1] for r in res]))}
    intro = [r[4]["intro"] for r in res if r[4].get("intro") is not None]
    out["intro"] = intro[0] if intro else None
    bol = [r[4]["bolum"] for r in res if r[4].get("bolum") is not None]
    out["bolum"] = bol[0] if bol else None
    out["obj"] = (out["mean"] - INTRO_W * (out["intro"] if out["intro"] is not None else 0.0)
                  - BOLUM_W * (out["bolum"] if out["bolum"] is not None else 0.0))
    for n, sc, subs, keep, det in res:
        out[n] = {"score": sc, "subs": subs, "dist": keep, "det": det}
    return out


def fmt(o):
    s = f"OBJ {o['obj']:.2f} MEAN {o['mean']:.1f} intro {o['intro'] if o['intro'] is None else round(o['intro'], 2)} bolum {o['bolum'] if o['bolum'] is None else round(o['bolum'], 2)}"
    for n in ("deneme", "sonda"):
        if n in o:
            s += f" | {n} {o[n]['score']:.1f}"
    lines = [s]
    for n in ("deneme", "sonda"):
        if n in o:
            lines.append(f"  {n:6s} " + " ".join(f"{k[:6]}={v:.0f}" for k, v in o[n]["subs"].items()))
            lines.append("         " + " ".join(f"{k}={v:.3g}" if isinstance(v, float) else f"{k}={v}" for k, v in o[n]["det"].items()))
    return "\n".join(lines)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--set", action="append", default=[])
    ap.add_argument("--only")
    ap.add_argument("--save")
    ap.add_argument("--seed", type=int, default=1)
    a = ap.parse_args()
    P = json.load(open(os.path.join(ROOT, "params.json")))
    for s in a.set:
        R.set_param(P, s)
    names = (a.only,) if a.only else ("deneme", "sonda")
    import multiprocessing as mp
    t0 = time.time()
    with mp.Pool(2) as pool:
        o = evaluate(P, names, a.seed, a.save, pool)
    print(fmt(o))
    print(f"({time.time() - t0:.0f} s)")
