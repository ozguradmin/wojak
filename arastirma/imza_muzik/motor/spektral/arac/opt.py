#!/usr/bin/env python3
"""coordinate-descent fit of engine parameters to the original's measurements (olcum.py TIMBRE_SCORE, mean over the
test melody and the transcription probe). Writes the best parameters to params_opt.json and a log.
usage: opt.py <spec.json> [--sweeps 2] [--out params_opt.json]
spec.json: [["acc.bed_db", 2.0, lo, hi], ...]"""
import sys, os, json, copy, time, argparse
import multiprocessing as mp
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, ".."))
sys.path.insert(0, HERE)
sys.path.insert(0, ROOT)
import deg
import render as R


def get(P, key):
    d = P
    for p in key.split("."):
        d = d[int(p)] if isinstance(d, list) else d[p]
    return d


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("spec")
    ap.add_argument("--sweeps", type=int, default=2)
    ap.add_argument("--out", default=os.path.join(ROOT, "params_opt.json"))
    ap.add_argument("--start", default=os.path.join(ROOT, "params.json"))
    ap.add_argument("--log", default=os.path.join(ROOT, "olcumler", "opt_log.txt"))
    a = ap.parse_args()
    spec = json.load(open(a.spec))
    P = json.load(open(a.start))
    logf = open(a.log, "a")
    def log(s):
        print(s, flush=True)
        logf.write(s + "\n"); logf.flush()
    with mp.Pool(2) as pool:
        best = deg.evaluate(P, pool=pool)
        log(f"start obj {best['obj']:.2f} mean {best['mean']:.2f}  ({best['deneme']['score']:.1f}/{best['sonda']['score']:.1f})")
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
                        t0 = time.time()
                        o = deg.evaluate(Q, pool=pool)
                        ok = o["obj"] > best["obj"] + 0.05
                        log(f"sw{sw} {key} {v0} -> {v}: obj {o['obj']:.2f} mean {o['mean']:.2f} intro {o['intro']:.2f} bolum {o['bolum']:.2f} ({o['deneme']['score']:.1f}/{o['sonda']['score']:.1f}) "
                            f"{'ACCEPT' if ok else ''} [{time.time() - t0:.0f}s]")
                        if ok:
                            P, best, improved = Q, o, True
                            json.dump(P, open(a.out, "w"), indent=1)
                        else:
                            break
                    if improved:
                        break
                if not improved:
                    steps[key] = st / 2
            log(f"== sweep {sw} best obj {best['obj']:.2f} mean {best['mean']:.2f}")
    log(deg.fmt(best))
    json.dump(P, open(a.out, "w"), indent=1)


if __name__ == "__main__":
    main()
