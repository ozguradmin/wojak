"""python3 vurgu.py <wav> [...]: the 'u a a' on the WRITTEN beat grid (152 BPM, bar 0 beat 2 = 0 s), bars 1-9.
Per beat position: mean peak level 0-120 ms after the beat (250-4000 Hz) and brightness tilt L(1-4k) - L(250-500),
both relative to beat 1 (same band and window definitions as olcum.accent_pattern, but no fitted grid and no rotation).
Also per bar: beat-2 level minus beat-1 level, to show which bars carry an 'a' on 2."""
import os, sys
import numpy as np
import scipy.signal as ss
import librosa

SP = "/tmp/claude-0/-home-user-wojak/e1bf52df-8e16-5819-ad96-6f6873ef480c/scratchpad/muzik2"
sys.path.insert(0, os.path.join(SP, "olcum"))
import olcum as O

BS = 60 / 152


def db(x):
    return 10 * np.log10(x + 1e-20)


for p in sys.argv[1:]:
    y = O.decode(p)[: int(O.WIN_S * O.SR)]
    y22 = ss.resample_poly((y[:, 0] + y[:, 1]) / 2, 1, 2)
    S = np.abs(librosa.stft(y22, n_fft=1024, hop_length=128)) ** 2
    fr = librosa.fft_frequencies(sr=22050, n_fft=1024)
    lo = db(S[(fr >= 250) & (fr < 500)].sum(0)); hi = db(S[(fr >= 1000) & (fr < 4000)].sum(0))
    al = db(S[(fr >= 250) & (fr < 4000)].sum(0))
    fps = 22050 / 128
    lev = np.zeros((9, 3)); til = np.zeros((9, 3))
    for bi, bar in enumerate(range(1, 10)):
        for k in range(3):
            t0 = (3 * bar + (k + 1) - 2) * BS
            i0, i1 = int(t0 * fps), int((t0 + 0.12) * fps) + 1
            lev[bi, k] = al[i0:i1].max(); til[bi, k] = hi[i0:i1].max() - lo[i0:i1].max()
    L = lev.mean(0) - lev.mean(0)[0]; T = til.mean(0) - til.mean(0)[0]
    d2 = lev[:, 1] - lev[:, 0]
    print(f"{os.path.basename(p):24s} level re beat1 [1,2,3] = {np.round(L, 1).tolist()}  tilt re beat1 = {np.round(T, 1).tolist()}"
          f"  | beat2-beat1 per bar 1-9: {np.round(d2, 1).tolist()}")
