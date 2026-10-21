#!/usr/bin/env python3
"""Symbolic originality calibration: null = random C-minor waltz melodies in the brief's style; positives = the
original's transcription and disguised copies of it. Output: kalib/null_sembolik.json + printed table."""
import json, os, sys
import numpy as np

K = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, K)
sys.path.insert(0, os.path.dirname(K))
import uret_kalib as U   # noqa: E402
import olcum as O        # noqa: E402

REF, _ = O.load_ref_melody()
REF = O.norm_notes(REF)
SC = [60, 62, 63, 65, 67, 68, 70, 71, 72, 74, 75, 77, 79, 80, 82, 83, 84]


def stats(notes, tonic=0):
    r = O.symbolic(O.norm_notes(notes), REF, tonic)
    return {"viol": r["offlimits"]["violations"], "POV": r["offlimits"]["POV"],
            "ng3m": r["ngram3_metric"]["share"], "ng4f": r["ngram4_free"]["share"], "ng3f": r["ngram3_free"]["share"],
            "ng4m": r["ngram4_metric"]["share"],
            "cbar": r["contour_bar_corr"]["value"] if r["contour_bar_corr"]["value"] is not None else -1,
            "cphr": r["contour_phrase_corr"]["value"] if r["contour_phrase_corr"]["value"] is not None else -1,
            "rdist": r["rhythm_distinctive_same_bar"], "rshare": r["rhythm_same_bar_share"],
            "verdict": r["verdict"], "reasons": r["reasons"]}


def step(m, k):
    i = min(range(len(SC)), key=lambda j: abs(SC[j] - m))
    return SC[int(np.clip(i + k, 0, len(SC) - 1))]


def positives():
    rng = np.random.default_rng(7)
    P = {}
    P["original"] = REF
    P["transposed_+2"] = [(b, bt, d, m + 2) for b, bt, d, m in REF]
    P["transposed_-5"] = [(b, bt, d, m - 5) for b, bt, d, m in REF]
    P["shifted_+1_bar"] = [(b + 1, bt, d, m) for b, bt, d, m in REF]
    for frac in (0.2, 0.35):
        P[f"disguised_{int(frac*100)}pct_notes_stepped"] = [(b, bt, d, step(m, rng.choice([-1, 1])) if rng.random() < frac else m)
                                                         for b, bt, d, m in REF]
    # triplets flattened into quarters (keep first note of each group)
    q = []
    for b, bt, d, m in REF:
        if abs(d - 1 / 3) < 0.01 and abs(bt - round(bt)) > 0.01:
            continue
        q.append((b, float(round(bt)) if abs(d - 1 / 3) < 0.01 else bt, 1.0 if abs(d - 1 / 3) < 0.01 else d, m))
    P["triplets_flattened"] = q
    # same pitches, rhythm re-written as plain quarters (one note per beat, in order)
    pit = [m for _, _, _, m in REF]
    P["same_pitches_new_rhythm"] = [(i // 3, 1.0 + i % 3, 1.0, m) for i, m in enumerate(pit[:36])]
    # same rhythm, new random pitches
    P["same_rhythm_new_pitches"] = [(b, bt, d, SC[int(rng.integers(7, 14))]) for b, bt, d, m in REF]
    # only bars 4-8 copied into an otherwise random melody
    base = [(n["bar"], n["beat"], n["dur_beats"], n["midi"]) for n in U.random_melody(np.random.default_rng(99))]
    P["bars4-8_copied_into_random"] = sorted([x for x in base if not (4 <= x[0] <= 8)] + [x for x in REF if 4 <= x[0] <= 8])
    return P


if __name__ == "__main__":
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 3000
    keys = ["POV", "ng3m", "ng3f", "ng4m", "ng4f", "cbar", "cphr", "rdist", "rshare"]
    null = []
    for i in range(n):
        mel = U.random_melody(np.random.default_rng(50000 + i))
        null.append(stats(mel))
    A = {k: np.array([x[k] for x in null], float) for k in keys}
    summ = {k: {"mean": round(float(A[k].mean()), 3), "p95": round(float(np.percentile(A[k], 95)), 3),
                "p99": round(float(np.percentile(A[k], 99)), 3), "max": round(float(A[k].max()), 3)} for k in keys}
    summ["offlimits_violation_rate"] = round(float(np.mean([x["viol"] > 0 for x in null])), 4)
    summ["verdict_fail_rate"] = round(float(np.mean([x["verdict"] == "FAIL" for x in null])), 4)
    from collections import Counter
    cnt = Counter(r.split(" ")[0] for x in null for r in x["reasons"])
    summ["fail_reasons"] = dict(cnt)
    print(json.dumps(summ, indent=1))
    pos = {}
    for name, mel in positives().items():
        mm = [{"bar": b, "beat": bt, "dur_beats": d, "midi": m} for b, bt, d, m in mel]
        st = stats(mm)
        pos[name] = st
        print(f"{name:34s} {st['verdict']}  viol={st['viol']} POV={st['POV']:.2f} ng3m={st['ng3m']:.2f} ng4f={st['ng4f']:.2f} "
              f"cbar={st['cbar']:.2f} cphr={st['cphr']:.2f} rdist={st['rdist']}  {st['reasons'][:3]}")
    rej = {}
    for name in ("imza", "ikinci", "ucuncu"):
        j = json.load(open(os.path.join(K, f"notalar_{name}.json")))
        st = stats(j["notes"])
        rej[name] = st
        print(f"rejected {name:25s} {st['verdict']}  viol={st['viol']} POV={st['POV']:.2f} ng3m={st['ng3m']:.2f} ng4f={st['ng4f']:.2f} "
              f"cbar={st['cbar']:.2f} cphr={st['cphr']:.2f} rdist={st['rdist']}  {st['reasons'][:3]}")
    json.dump({"null_summary": summ, "positives": pos, "rejected": rej}, open(os.path.join(K, "null_sembolik.json"), "w"), indent=1)
