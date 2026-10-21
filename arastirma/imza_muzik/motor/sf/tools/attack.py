import sys, numpy as np
sys.path.insert(0, '/tmp/claude-0/-home-user-wojak/e1bf52df-8e16-5819-ad96-6f6873ef480c/scratchpad/muzik2/motor/sf')
import render_dev as R
F = R.Fluid(); SR = R.SR
for prog in (22, 23, 21, 20, 71, 68):
    for midi, vel in ((48, 62), (63, 96), (72, 90)):
        x = F.note(prog, 0, midi, vel, 0.8, -21.0, tail_s=0.05)
        # 5 ms RMS envelope and high-band (4-8k) share early vs steady
        k = int(0.005 * SR)
        e = np.sqrt(np.convolve(x ** 2, np.ones(k) / k, 'same'))
        import scipy.signal as ss
        hb = ss.sosfilt(ss.butter(4, [3500, 9000], 'bandpass', fs=SR, output='sos'), x)
        eh = np.sqrt(np.convolve(hb ** 2, np.ones(k) / k, 'same'))
        st = e[int(0.4 * SR):int(0.6 * SR)].mean(); sth = eh[int(0.4 * SR):int(0.6 * SR)].mean()
        ts = [0.005, 0.01, 0.02, 0.03, 0.05, 0.08, 0.12, 0.2, 0.3]
        print(prog, midi, vel, 'lvl', ' '.join(f"{20*np.log10(e[int(t*SR)]/st+1e-9):5.1f}" for t in ts),
              '| hf', ' '.join(f"{20*np.log10(eh[int(t*SR)]/sth+1e-9):5.1f}" for t in ts))
