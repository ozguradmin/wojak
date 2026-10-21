"""per-beat level / brightness on the known beat grid, per section (measurement only). usage: beats.py wav [wav...]"""
import sys, numpy as np, librosa
sys.path.insert(0, '/tmp/claude-0/-home-user-wojak/e1bf52df-8e16-5819-ad96-6f6873ef480c/scratchpad/muzik2/olcum')
import olcum
B = 60 / 151.5; ph = -0.152
for p in sys.argv[1:]:
    y = olcum.decode(p).mean(1)
    y22 = librosa.resample(y, orig_sr=44100, target_sr=22050)
    S = np.abs(librosa.stft(y22, n_fft=1024, hop_length=128)) ** 2
    fr = librosa.fft_frequencies(sr=22050, n_fft=1024)
    db = lambda x: 10 * np.log10(x + 1e-20)
    lo = db(S[(fr >= 250) & (fr < 500)].sum(0)); hi = db(S[(fr >= 1000) & (fr < 4000)].sum(0)); al = db(S[(fr >= 250) & (fr < 4000)].sum(0))
    fps = 22050 / 128
    rows = []
    for k in range(0, 40):
        t0 = ph + k * B
        if t0 < 0 or t0 > 11.4: continue
        i0, i1 = int(t0 * fps), int((t0 + 0.12) * fps) + 1
        j0, j1 = int((t0 + 0.2) * fps), int((t0 + B - 0.02) * fps)
        rows.append((k % 3, t0, al[i0:i1].max(), hi[i0:i1].max() - lo[i0:i1].max(), np.median(al[j0:j1])))
    R = np.array(rows)
    print(p.split('/')[-1])
    for name, m in (("intro <4.6s", R[:, 1] < 4.6), ("melody 4.6-11.4", R[:, 1] >= 4.6)):
        out = []
        for c in range(3):
            q = R[m & (R[:, 0] == c)]
            out.append(f"b{c+1}: lvl {q[:,2].mean():6.1f} tilt {q[:,3].mean():5.1f} bed {q[:,4].mean():6.1f}")
        print("  ", name, " | ".join(out))
