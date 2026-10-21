#!/usr/bin/env python3
"""Null distribution of the audio originality measures: random C-minor waltz melodies (brief style), rendered with
FluidR3 through the measured chain, half over the ORIGINAL's i/vii° harmony (allowed, generic) and half over other
progressions. Output: kalib/null_chroma.json"""
import json, os, sys
import numpy as np
import scipy.signal as ss
from multiprocessing import Pool

K = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, K)
sys.path.insert(0, os.path.dirname(K))
import uret_kalib as U   # noqa: E402
import olcum as O        # noqa: E402

PROGS = [["Cm", "Cm", "Fm", "G", "Cm", "Ab", "Fm", "G", "Cm", "G", "Cm", "Cm"],
         ["Cm", "Cm", "Bb", "Ab", "G", "Cm", "Fm", "Dm", "G", "G", "Cm", "Cm"],
         ["Cm", "Cm", "Fm", "Bb", "Eb", "Ab", "Dm", "G", "Cm", "Fm", "Cm", "Cm"],
         ["Cm", "Cm", "Ab", "Eb", "Fm", "Cm", "G", "Cm", "Ab", "G", "Cm", "Cm"],
         ["Cm", "Cm", "Cm", "Fm", "Fm", "Cm", "Ab", "G", "Cm", "G", "Cm", "Cm"]]


def one(i):
    rng = np.random.default_rng(1000 + i)
    mel = U.random_melody(rng)
    bpm = float(rng.uniform(148, 156))
    bars = U.REF_BARS if i % 2 == 0 else U.harmony_from_names(PROGS[i % len(PROGS)])
    prog = 23 if i % 3 else 21
    y = U.arrange(mel, bars, bpm, -2 * 60 / bpm + 0.0, acc_prog=prog)
    mid = y.mean(1)
    y22 = ss.resample_poly(mid, 1, 2)
    ch = O.chroma_seq(y22)
    fp = O.fingerprint(y22)
    return i, mel, ch, fp, bpm, (i % 2 == 0)


if __name__ == "__main__":
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 40
    R = O.ref_features(O.REF_WAV)
    with Pool(4) as p:
        res = p.map(one, range(n))
    out = []
    for i, mel, ch, fp, bpm, origharm in res:
        c0 = O.chroma_sim(ch, R["chroma"])[0]
        ct = O.chroma_sim(ch, R["chroma"], True, O.SCALES)[0]
        fm = O.fp_match(fp, R["fp"])[0]
        out.append({"i": i, "orig_harmony": origharm, "bpm": round(bpm, 1), "chroma": round(c0, 3), "chroma_T": round(ct, 3),
                    "fp": round(fm, 4), "notes": mel})
        print(i, origharm, round(c0, 3), round(ct, 3), round(fm, 4))
    json.dump(out, open(os.path.join(K, "null_chroma.json"), "w"))
    for flag in (True, False):
        v = np.array([o["chroma_T"] for o in out if o["orig_harmony"] == flag])
        f = np.array([o["fp"] for o in out if o["orig_harmony"] == flag])
        print("orig_harmony" if flag else "other_harmony", "chroma_T mean %.3f p95 %.3f max %.3f | fp max %.4f" %
              (v.mean(), np.percentile(v, 95), v.max(), f.max()))
