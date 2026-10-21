"""python3 anahtar.py <wav> [...]: key ranking with olcum.py's own method (Krumhansl-Kessler on the mean chroma_cqt of
the mid channel at 22.05 kHz), for the whole clip and for the bar 6-9 window (6.71-11.45 s at 152 BPM)."""
import os, sys
import numpy as np
import scipy.signal as ss

SP = "/tmp/claude-0/-home-user-wojak/e1bf52df-8e16-5819-ad96-6f6873ef480c/scratchpad/muzik2"
sys.path.insert(0, os.path.join(SP, "olcum"))
import olcum as O
import librosa

BS = 60 / 152


def rank(prof):
    ks = []
    for k in range(12):
        ks.append((float(np.corrcoef(prof, np.roll(O.KK_MAJ, k))[0, 1]), O.PCN[k] + " maj"))
        ks.append((float(np.corrcoef(prof, np.roll(O.KK_MIN, k))[0, 1]), O.PCN[k] + " min"))
    ks.sort(reverse=True)
    d = dict((n, r) for r, n in ks)
    return ks, d


def main():
  for p in sys.argv[1:]:
    y = O.decode(p)[: int(O.WIN_S * O.SR)]
    mid = (y[:, 0] + y[:, 1]) / 2
    y22 = ss.resample_poly(mid, 1, 2)
    ch = librosa.feature.chroma_cqt(y=y22, sr=22050)
    t = np.arange(ch.shape[1]) * 512 / 22050
    out = []
    for name, (a, b) in (("all", (0, 13.77)), ("bars6-9", (17 * BS, 29 * BS)), ("bars1-5", (2 * BS, 17 * BS))):
        sel = (t >= a) & (t < b)
        ks, d = rank(ch[:, sel].mean(1))
        out.append(f"{name}: " + ", ".join(f"{n} {r:.2f}" for r, n in ks[:3]) +
                   f" | Cmin {d['C min']:.2f} Gmaj {d['G maj']:.2f} Gmin {d['G min']:.2f}")
    print(os.path.basename(p))
    for s in out:
        print("   ", s)


if __name__ == "__main__":
    main()
