#!/usr/bin/env python3
"""Calibration probes for olcum.py (measurement only; none of these is a candidate).

  - copies of the original: AAC-LC 128k, MP3 128k (re-encodes), +2 / -1 semitone pitch shifts and +3 % tempo (rubberband)
  - the original + injected clicks, the original + hiss (detector sensitivity tests)
  - melody JSONs of the three rejected attempts (tools/imza_muzik.py MELODILER)
  - FluidR3 renders through the measured chain (tini.md §5): the ORIGINAL's transcription ("cover" = same composition,
    other sound, must FAIL originality), the rejected melodies with the recommended sound, and random C-minor waltzes
    (null distribution for the audio originality thresholds).
"""
import json, os, subprocess, sys
import numpy as np, soundfile as sf, scipy.signal as ss

K = os.path.dirname(os.path.abspath(__file__))
SCR = os.path.abspath(os.path.join(K, "..", "..", ".."))
TINI = os.path.join(SCR, "muzik2", "analiz", "tini", "py")
sys.path.insert(0, TINI)
import zincir as Z                     # noqa: E402  (measured chain model)
from fsr import render_layers          # noqa: E402  (FluidR3 helper)
from eslestir import match_fir, apply  # noqa: E402

SR = 44100
ORIG = os.path.join(SCR, "muzik", "orijinal.wav")
REPO = "/home/user/wojak"
REV = dict(rt60=0.09, pd_ms=6, build_ms=4, tail_db=-30, tail_rt=1.5, lp=4000)
TARGET = json.load(open(os.path.join(SCR, "muzik2", "analiz", "tini.json")))["eq_curve"]


def ff(*a):
    subprocess.run(["ffmpeg", "-y", "-v", "error", *a], check=True)


def copies():
    o = os.path.join(K, "audio")
    os.makedirs(o, exist_ok=True)
    ff("-i", ORIG, "-c:a", "aac", "-b:a", "128k", os.path.join(o, "kopya_aac128.m4a"))
    ff("-i", ORIG, "-c:a", "libmp3lame", "-b:a", "128k", os.path.join(o, "kopya_mp3128.mp3"))
    ff("-i", ORIG, "-af", f"rubberband=pitch={2 ** (2 / 12):.6f}", os.path.join(o, "orijinal_p2.wav"))
    ff("-i", ORIG, "-af", f"rubberband=pitch={2 ** (-1 / 12):.6f}", os.path.join(o, "orijinal_m1.wav"))
    ff("-i", ORIG, "-af", "rubberband=tempo=1.03", os.path.join(o, "orijinal_tempo103.wav"))
    y, sr = sf.read(ORIG)
    rng = np.random.default_rng(5)
    z = y.copy()
    pos = np.linspace(1.0, 12.5, 10)
    amps = 10 ** (np.linspace(-40, -22, 10) / 20)        # click peaks -40 .. -22 dBFS (music peaks at -17)
    for p, a in zip(pos, amps):
        i = int(p * sr)
        z[i:i + 3] += a * np.array([1.0, -0.6, 0.2])[:, None]
    sf.write(os.path.join(o, "orijinal_10klik.wav"), z, sr, subtype="FLOAT")
    h = ss.sosfiltfilt(ss.butter(2, [250, 6000], "bandpass", fs=sr, output="sos"), rng.standard_normal(y.shape), axis=0)
    h = h / np.sqrt(np.mean(h ** 2)) * 10 ** (-55 / 20)
    sf.write(os.path.join(o, "orijinal_hiss55.wav"), y + h, sr, subtype="FLOAT")


# ------------------------------------------------------------------------------------------- melodies
NOTA = {"C": 0, "C#": 1, "Db": 1, "D": 2, "D#": 3, "Eb": 3, "E": 4, "F": 5, "F#": 6, "Gb": 6, "G": 7, "G#": 8,
        "Ab": 8, "A": 9, "A#": 10, "Bb": 10, "B": 11}


def midi(n):
    return 12 * (int(n[-1]) + 1) + NOTA[n[:-1]]


def rejected_jsons():
    sys.path.insert(0, os.path.join(REPO, "tools"))
    import imza_muzik as IM
    out = {}
    for name, v in IM.MELODILER.items():
        notes = []
        for bar, olc in enumerate(v["melodi"]):
            beat = 1.0
            for nota, vur in olc:
                if nota is not None:
                    notes.append({"bar": bar, "beat": beat, "dur_beats": vur, "midi": midi(nota)})
                beat += vur
        j = {"tempo_bpm": 154, "notes": notes, "chords": [c.replace(":M", "").replace(":m", "m") for c in v["akor"]],
             "source": "tools/imza_muzik.py MELODILER['%s'] (bar 0 starts at t=0)" % name}
        p = os.path.join(K, f"notalar_{name}.json")
        json.dump(j, open(p, "w"), indent=1)
        out[name] = j
    return out


def ref_json():
    mj = json.load(open(os.path.join(SCR, "muzik2", "analiz", "muzik.json")))
    notes = [{"bar": n["bar"], "beat": n["beat"], "dur_beats": n["dur_beats"], "midi": n["midi"]} for n in mj["melody"]]
    j = {"tempo_bpm": 151.5, "notes": notes, "chords": [h["chord"] for h in mj["harmony"]]}
    json.dump(j, open(os.path.join(K, "notalar_orijinal.json"), "w"), indent=1)
    return j


# ------------------------------------------------------------------------------------------- arrangement
TRI = {"m": (0, 3, 7), "M": (0, 4, 7), "d": (0, 3, 6), "d7": (0, 3, 6, 9), "7": (0, 4, 7, 10)}


def chord_notes(root_pc, kind, bass_pc=None):
    """close position inside C4..C5 (top <= 72) plus bass in octave 3"""
    pcs = [(root_pc + i) % 12 for i in TRI[kind]]
    notes = sorted(60 + ((p - 0) % 12) for p in pcs)
    notes = [n if n <= 70 else n - 12 for n in notes]
    notes = sorted(notes)
    b = bass_pc if bass_pc is not None else root_pc
    return 48 + b % 12 if 48 + b % 12 <= 55 else 36 + b % 12, notes


def arrange(melody, bars, bpm, t_bar0, total=13.75, lead=None, acc_prog=23, seed=1, acc_db=-6):
    """melody: [{bar,beat,dur_beats,midi}], bars: {bar: [(beat, root_pc, kind, bass_pc)]}"""
    bs = 60 / bpm
    T = lambda bar, beat: t_bar0 + (3 * bar + beat - 1) * bs
    lead = lead or [dict(prog=23), dict(prog=22, detune_c=14, gain_db=-2)]
    ln = []
    for n in melody:
        t0 = T(n["bar"], n["beat"])
        du = n["dur_beats"] * bs + 0.05
        if t0 + du <= 0:
            continue
        if t0 < 0:
            du += t0; t0 = 0.0
        if t0 >= total:
            continue
        du = min(du, total + 0.3 - t0)
        ln.append((t0, du, n["midi"], 100))
    acc = []
    for bar, evs in bars.items():
        for k, (beat, r, kind, bpc) in enumerate(evs):
            bass, ch = chord_notes(r, kind, bpc)
            nxt = evs[k + 1][0] if k + 1 < len(evs) else 4.0
            for bt in [b for b in (1, 2, 3) if beat <= b < nxt]:
                t0 = T(bar, bt)
                if t0 < -0.05 or t0 >= total:
                    continue
                t0 = max(t0, 0.0)
                if bt == 1:
                    acc.append((t0, 0.30, bass, 85)); acc.append((t0, 0.30, bass + 12, 70))
                else:
                    for m in ch:
                        acc.append((t0, 0.10, m, 85))
    xl = render_layers(lead, ln, total + 0.5)
    xa = render_layers([dict(prog=acc_prog)], acc, total + 0.5)
    n = min(len(xl), len(xa))
    xl, xa = xl[:n], xa[:n]
    rl, ra = np.sqrt(np.mean(xl ** 2)) + 1e-12, np.sqrt(np.mean(xa ** 2)) + 1e-12
    x = xl + xa * (rl / ra) * 10 ** (acc_db / 20)
    # 45 ms raised-cosine lead attacks are not applied here (probe only)
    y = Z.chain(x, wow_c=4.5, wet_db=-8, rev=REV)
    for _ in range(2):
        fir, _g = match_fir(y, [v for _, v in TARGET])
        y = apply(y, fir)
    y = ss.sosfilt(ss.butter(8, 5000, "lowpass", fs=SR, output="sos"), y, axis=0)
    y = y[: int(total * SR)]
    t = np.arange(len(y)) / SR
    y *= np.clip((13.75 - t) / 0.30, 0, 1)[:, None]
    return y


def to_lufs(y, path, target=-29.5):
    tmp = path + ".tmp.wav"
    sf.write(tmp, y, SR, subtype="FLOAT")
    for _ in range(2):
        p = subprocess.run(["ffmpeg", "-nostats", "-hide_banner", "-i", tmp, "-af", "ebur128", "-f", "null", "-"],
                           capture_output=True, text=True).stderr
        I = float(p[p.rfind("I:"):].split()[1])
        y = y * 10 ** ((target - I) / 20)
        sf.write(tmp, y, SR, subtype="FLOAT")
    os.replace(tmp, path)


def harmony_from_names(names):
    """['Cm','G','Ab',...] one per bar -> bars dict"""
    out = {}
    for b, nm in enumerate(names):
        r = NOTA[nm[0] + (nm[1] if len(nm) > 1 and nm[1] in "b#" else "")]
        kind = "m" if nm.endswith("m") else "M"
        out[b] = [(1, r, kind, None)]
    return out


REF_BARS = {0: [(1, 0, "m", 0)], 1: [(1, 11, "d", 2)], 2: [(1, 0, "m", 0)], 3: [(1, 11, "d", 2)], 4: [(1, 0, "m", 0)],
            5: [(1, 11, "d", 2)], 6: [(1, 0, "m", 0)], 7: [(1, 11, "d7", 2)], 8: [(1, 0, "m", 0)],
            9: [(1, 2, "d", 2), (2, 2, "7", 2), (3, 7, "7", 7)], 10: [(1, 0, "m", 0)], 11: [(1, 11, "d", 2)]}


def random_melody(rng, n_bars=12):
    """random C-minor waltz top line in the brief's style (null population)"""
    scale = [60, 62, 63, 65, 67, 68, 70, 71, 72, 74, 75, 77, 79, 80, 82, 83, 84]
    cells = [([1, 2, 3], [1, 1, 1], .40), ([1, 3], [2, 1], .18), ([1], [3], .05), ([1, 2], [1, 2], .08),
             ([1, 2, 2 + 1 / 3, 2 + 2 / 3, 3], [1, 1 / 3, 1 / 3, 1 / 3, 1], .08),
             ([1, 1 + 1 / 3, 1 + 2 / 3, 2, 3], [1 / 3, 1 / 3, 1 / 3, 1, 1], .06),
             ([1, 2, 3, 3 + 1 / 3, 3 + 2 / 3], [1, 1, 1 / 3, 1 / 3, 1 / 3], .06),
             ([1, 2, 2 + 1 / 3, 2 + 2 / 3, 3, 3 + 1 / 3, 3 + 2 / 3], [1] + [1 / 3] * 6, .04),
             ([1, 2.5, 3], [1.5, .5, 1], .05)]
    pw = np.array([c[2] for c in cells]); pw /= pw.sum()
    idx = rng.integers(7, 11)
    notes = [{"bar": 0, "beat": 2.0, "dur_beats": 1, "midi": scale[idx]}, {"bar": 0, "beat": 3.0, "dur_beats": 1, "midi": scale[idx]}]
    for bar in range(1, n_bars - 2):
        c = cells[rng.choice(len(cells), p=pw)]
        for bt, du in zip(c[0], c[1]):
            r = rng.random()
            step = rng.choice([-1, 1]) if r < .45 else (rng.choice([-2, 2]) if r < .75 else (0 if r < .87 else rng.choice([-4, -3, 3, 4])))
            idx = int(np.clip(idx + step, 5, 15))
            notes.append({"bar": bar, "beat": float(bt), "dur_beats": float(du), "midi": scale[idx]})
    notes.append({"bar": n_bars - 2, "beat": 1.0, "dur_beats": 6.0, "midi": 72})
    return notes


def renders():
    o = os.path.join(K, "audio")
    os.makedirs(o, exist_ok=True)
    rj = ref_json()
    y = arrange(rj["notes"], REF_BARS, 151.5, -0.152)
    to_lufs(y, os.path.join(o, "kapak_orijinal_besteyle_fluid.wav"))
    rej = rejected_jsons()
    for name, j in rej.items():
        y = arrange(j["notes"], harmony_from_names(j["chords"]), 154, 0.0)
        to_lufs(y, os.path.join(o, f"red_{name}_fluid.wav"))
    rng = np.random.default_rng(2026)
    progs = [["Cm", "Cm", "Fm", "G", "Cm", "Ab", "Fm", "G", "Cm", "G", "Cm", "Cm"],
             ["Cm", "Cm", "Bb", "Ab", "G", "Cm", "Fm", "Dm", "G", "G", "Cm", "Cm"],
             ["Cm", "Cm", "Fm", "Bb", "Eb", "Ab", "Dm", "G", "Cm", "Fm", "Cm", "Cm"]]
    for i in range(6):
        mel = random_melody(rng)
        json.dump({"tempo_bpm": 152, "notes": mel}, open(os.path.join(K, f"notalar_rastgele{i}.json"), "w"))
        bars = REF_BARS if i < 3 else harmony_from_names(progs[i - 3])
        y = arrange(mel, bars, 152, -0.395, seed=i)
        to_lufs(y, os.path.join(o, f"rastgele{i}_{'origarmoni' if i < 3 else 'baskaarmoni'}.wav"))


if __name__ == "__main__":
    what = sys.argv[1:] or ["copies", "renders"]
    if "copies" in what:
        copies()
    if "renders" in what:
        renders()
    print("ok")
