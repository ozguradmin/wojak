import numpy as np
M = 1024
n = np.arange(2 * M); k = np.arange(M)
w = np.sin(np.pi * (n + 0.5) / (2 * M))
Cm = np.cos(np.pi / M * (n[None, :] + 0.5 + M / 2) * (k[:, None] + 0.5))
x = np.random.default_rng(0).standard_normal(20 * M)
xp = np.r_[np.zeros(M), x, np.zeros(2 * M)]
nf = (len(xp) - 2 * M) // M + 1
out = np.zeros(len(xp))
for i in range(nf):
    fr = xp[i * M:i * M + 2 * M] * w
    X = Cm @ fr
    yb = (2.0 / M) * (Cm.T @ X) * w
    out[i * M:i * M + 2 * M] += yb
r = out[M:M + len(x)]
print('recon err', np.max(np.abs(r - x)))
