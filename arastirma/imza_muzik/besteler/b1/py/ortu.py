"""overlay the written score on the preview's CQT: python3 ortu.py b1-1 b1-2 ... -> ../ortu_<id>.png"""
import sys, json, os
import numpy as np, librosa, soundfile as sf
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
OUT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ids = sys.argv[1:]
fig, axs = plt.subplots(len(ids), 1, figsize=(16, 3.6 * len(ids)), dpi=80)
axs = np.atleast_1d(axs)
for ax, pid in zip(axs, ids):
    J = json.load(open(os.path.join(OUT, pid + '.json')))
    y, sr = sf.read(os.path.join(OUT, pid + '.wav')); y = y.mean(1)
    y = librosa.resample(y, orig_sr=sr, target_sr=22050)
    fmin = librosa.note_to_hz('C4')
    C = np.abs(librosa.cqt(y, sr=22050, hop_length=256, fmin=fmin, n_bins=36 * 3, bins_per_octave=36))
    Z = librosa.amplitude_to_db(C, ref=np.max)
    t = np.arange(Z.shape[1]) * 256 / 22050
    ax.imshow(Z, origin='lower', aspect='auto', cmap='magma', vmin=-60, vmax=0, extent=[0, t[-1], 60, 96])
    bs = 60 / J["tempo_bpm"]; prev = None
    for n in J['notes']:
        ax.plot([n['t_s'], n['t_s'] + n['dur_beats'] * bs], [n['midi']] * 2, color='#33e0ff', lw=2.2, alpha=0.9)
    for n in J.get('counter', []):
        ax.plot([n['t_s'], n['t_s'] + n['dur_beats'] * bs], [n['midi']] * 2, color='#7CFC00', lw=1.6, alpha=0.8)
    for c in J['chords']:
        ax.text(c['t_s'] + 0.02, 61, c['symbol'] if c['beat'] in (1.0,) or c['symbol'] != prev else '', color='w', fontsize=7)
        prev = c['symbol']
    for b in range(0, 12):
        tb = (3 * b - 1) * bs
        ax.axvline(tb, color='w', lw=0.5, alpha=0.4)
    ax.set_xlim(0, 13.8); ax.set_ylim(60, 92)
    ax.set_yticks([60, 63, 67, 72, 75, 79, 84, 87, 91]); ax.set_yticklabels(['C4', 'Eb4', 'G4', 'C5', 'Eb5', 'G5', 'C6', 'Eb6', 'G6'])
    ax.set_title(f"{pid}: preview CQT (36 bins/oct) with the written lead (cyan) and counter (green); white lines = bar lines", loc='left', fontsize=10)
    prev = None
fig.tight_layout(); fig.savefig(os.path.join(OUT, 'ortu_' + '_'.join(ids) + '.png'))
print(os.path.join(OUT, 'ortu_' + '_'.join(ids) + '.png'))
