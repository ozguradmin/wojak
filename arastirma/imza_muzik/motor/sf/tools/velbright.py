import sys, numpy as np
sys.path.insert(0, '/tmp/claude-0/-home-user-wojak/e1bf52df-8e16-5819-ad96-6f6873ef480c/scratchpad/muzik2/motor/sf')
import render_dev as R
F = R.Fluid(); SR = R.SR
def cen(x):
    X = np.abs(np.fft.rfft(x * np.hanning(len(x)))) ** 2; f = np.fft.rfftfreq(len(x), 1 / SR)
    return (f * X).sum() / X.sum(), 10*np.log10(np.mean(x**2))
for prog in (22, 23, 21):
    for midi in (48, 63, 72):
        row = []
        for vel in (40, 60, 80, 100, 127):
            x = F.note(prog, 0, midi, vel, 2.0, -21.0, tail_s=0.05)
            c, l = cen(x[int(0.6 * SR):int(1.6 * SR)])
            row.append(f"v{vel}: {c:5.0f}Hz {l:5.1f}dB")
        # long-term level stability 0.3-2.0 s in 100 ms steps
        x = F.note(prog, 0, midi, 90, 2.0, -21.0, tail_s=0.05)
        k = int(0.1 * SR); e = [10*np.log10(np.mean(x[i:i+k]**2)) for i in range(0, int(2.0*SR)-k, k)]
        print(prog, midi, ' | '.join(row)); print('    lvl/100ms', ' '.join(f"{v-e[-1]:4.1f}" for v in e))
