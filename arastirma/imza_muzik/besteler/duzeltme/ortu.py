"""python3 ortu.py out.png a.json:a.wav b.json:b.wav ...: preview CQT with the written lead (cyan), counter (green),
chord labels (white, at each change) and bar lines; one panel per piece (adapted from b1/py/ortu.py)."""
import json, os, sys
import numpy as np, librosa, soundfile as sf
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt

out = sys.argv[1]
pairs = [a.split(":") for a in sys.argv[2:]]
fig, axs = plt.subplots(len(pairs), 1, figsize=(16, 3.4 * len(pairs)), dpi=80)
axs = np.atleast_1d(axs)
for ax, (jp, wp) in zip(axs, pairs):
    J = json.load(open(jp))
    bs = 60 / J["tempo_bpm"]
    T = lambda b, bt: (3 * b + bt - 2) * bs
    y, sr = sf.read(wp); y = y.mean(1) if y.ndim > 1 else y
    y = librosa.resample(y, orig_sr=sr, target_sr=22050)
    C = np.abs(librosa.cqt(y, sr=22050, hop_length=256, fmin=librosa.note_to_hz("C4"), n_bins=36 * 3, bins_per_octave=36))
    Z = librosa.amplitude_to_db(C, ref=np.max)
    t = np.arange(Z.shape[1]) * 256 / 22050
    ax.imshow(Z, origin="lower", aspect="auto", cmap="magma", vmin=-60, vmax=0, extent=[0, t[-1], 60, 96])
    for n in J["notes"]:
        t0 = T(n["bar"], n["beat"])
        ax.plot([t0, t0 + n["dur_beats"] * bs], [n["midi"]] * 2, color="#33e0ff", lw=2.2, alpha=0.9)
        ax.plot([t0], [n["midi"]], "|", color="#33e0ff", ms=9)
    for n in J.get("counter", []) or []:
        t0 = T(n["bar"], n["beat"])
        ax.plot([t0, t0 + n["dur_beats"] * bs], [n["midi"]] * 2, color="#7CFC00", lw=1.6, alpha=0.8)
    prev = None
    for c in J["chords"]:
        lab = c.get("symbol") or c.get("roman") or c.get("chord")
        lab = lab.split(" ")[0]
        if lab != prev:
            ax.text(T(c["bar"], c["beat"]) + 0.02, 61, lab, color="w", fontsize=7)
        prev = lab
    for b in range(0, 12):
        ax.axvline((3 * b - 1) * bs, color="w", lw=0.5, alpha=0.4)
        ax.text((3 * b - 1) * bs + 0.03, 91, str(b), color="w", fontsize=7)
    ax.set_xlim(0, 13.8); ax.set_ylim(60, 92)
    ax.set_yticks([60, 63, 67, 72, 75, 79, 84, 87, 91]); ax.set_yticklabels(["C4", "Eb4", "G4", "C5", "Eb5", "G5", "C6", "Eb6", "G6"])
    ax.set_title(f"{J['id']}: preview CQT, written lead (cyan) and counter (green), chord changes (white), bar numbers on top",
                 loc="left", fontsize=10)
fig.tight_layout(); fig.savefig(out)
print(out)
