#!/usr/bin/env python3
"""fit the ACCOMPANIMENT envelope model to the original's intro (bars 0-3, accompaniment alone, 0.05-4.5 s):
mean band envelopes (250-500, 900-4000, 250-4000 Hz; dB, 1024/128 STFT at 22.05 kHz) in a -0.15..+0.37 s window around
each beat, averaged per beat position, normalised by the intro's mean level. The probe (the original's arrangement on the
same beat grid) is rendered with the match EQ frozen to the full-length render's curve.
usage: intro_fit.py [--set k=v]   |   intro_fit.py --fit spec.json [--sweeps 2]  -> params_intro.json"""
import sys, os, json, copy, argparse
import numpy as np, librosa
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, ".."))
SP = os.path.abspath(os.path.join(ROOT, "..", ".."))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(SP, "olcum"))
import render as R
import olcum
B = 60 / 151.5
PH = -0.152
SONDA = os.path.join(ROOT, "sonda", "sonda_orijinal_transkripsiyon.json")
INTRO = os.path.join(ROOT, "out", "_sonda_intro.json")
W0, W1 = -0.15, 0.37


def profile(y):
    """y mono 44.1k -> array (3 pos, 3 bands, n) dB"""
    y22 = librosa.resample(y, orig_sr=44100, target_sr=22050)
    S = np.abs(librosa.stft(y22, n_fft=1024, hop_length=128)) ** 2
    fr = librosa.fft_frequencies(sr=22050, n_fft=1024)
    fps = 22050 / 128
    bands = [(250, 500), (900, 4000), (250, 4000)]
    E = np.array([10 * np.log10(S[(fr >= a) & (fr < b)].sum(0) + 1e-20) for a, b in bands])
    t = np.arange(E.shape[1]) / fps
    m = (t > 0.05) & (t < 4.5)
    ref = 10 * np.log10(np.mean(10 ** (E[2, m] / 10)))
    E = E - ref
    n = int((W1 - W0) * fps)
    acc = [[], [], []]
    for k in range(0, 14):
        tb = PH + k * B
        if tb + W0 < 0.05 or tb + W1 > 4.5:
            continue
        i0 = int((tb + W0) * fps)
        acc[k % 3].append(E[:, i0:i0 + n])
    return np.array([np.mean(a, 0) for a in acc])


ORIG = None


def orig_profile():
    global ORIG
    if ORIG is None:
        ORIG = profile(olcum.decode(olcum.REF_WAV).mean(1))
    return ORIG


def make_intro():
    p = json.load(open(SONDA))
    p["notes"] = [n for n in p["notes"] if n["bar"] < 5]
    p["chords"] = [c for c in p["chords"] if c["bar"] < 5]
    json.dump(p, open(INTRO, "w"))


def frozen(P):
    R.render(SONDA, 1, copy.deepcopy(P), quiet=True)
    return [R.LAST_EQ["fc"], R.LAST_EQ["db"]]


def measure(P, eq):
    Q = copy.deepcopy(P)
    Q["chain"]["fixed_eq"] = eq
    y = R.render(INTRO, 1, Q, quiet=True).mean(0)
    C = profile(y)
    O = orig_profile()
    d = C - O
    out = {"rms": float(np.sqrt(np.mean(d ** 2)))}
    names = ["lo", "hi", "all"]
    for b in range(3):
        out[names[b]] = [float(np.sqrt(np.mean(d[p, b] ** 2))) for p in range(3)]
    return out, C


def show(o):
    return f"rms {o['rms']:.2f} | " + " ".join(f"{k} " + "/".join(f"{x:.1f}" for x in o[k]) for k in ("lo", "hi", "all"))


def plot(C, png):
    import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
    O = orig_profile()
    t = W0 + np.arange(O.shape[2]) * 128 / 22050
    fig, axs = plt.subplots(3, 3, figsize=(15, 9), sharex=True)
    for p in range(3):
        for b, nm in enumerate(["250-500", "900-4000", "250-4000"]):
            ax = axs[b, p]
            ax.plot(t * 1000, O[p, b], color="#2a78d6", label="original")
            ax.plot(t * 1000, C[p, b], color="#eb6834", label="spektral")
            ax.set_title(f"beat {p + 1}, {nm} Hz", fontsize=9, loc="left"); ax.grid(alpha=.3)
            ax.axvline(0, color="k", lw=.5); ax.axvline(B * 1000, color="k", lw=.5, ls=":")
    axs[0, 0].legend(fontsize=8); fig.suptitle("intro (bars 0-3) mean band envelope around each beat, dB re intro mean level")
    fig.tight_layout(); fig.savefig(png, dpi=70)


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
    ap.add_argument("--png")
    ap.add_argument("--params", default=os.path.join(ROOT, "params.json"))
    a = ap.parse_args()
    P = json.load(open(a.params))
    for s in a.set:
        R.set_param(P, s)
    make_intro()
    eq = frozen(P)
    o, C = measure(P, eq)
    print(show(o), flush=True)
    if a.png:
        plot(C, a.png)
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
                        oo, CC = measure(Q, eq)
                        ok = oo["rms"] < best["rms"] - 0.01
                        print(f"sw{sw} {key} {v0}->{v}: {show(oo)} {'ACCEPT' if ok else ''}", flush=True)
                        if ok:
                            P, best, improved, C = Q, oo, True, CC
                        else:
                            break
                    if improved:
                        break
                if not improved:
                    steps[key] = st / 2
            print(f"== sweep {sw}: {show(best)}", flush=True)
            eq = frozen(P)
        json.dump(P, open(os.path.join(ROOT, "params_intro.json"), "w"), indent=1)
        if a.png:
            plot(C, a.png.replace(".png", "_fit.png"))
