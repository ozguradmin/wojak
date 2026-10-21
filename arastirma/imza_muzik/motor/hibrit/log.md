# hibrit engine: iteration log

Nobody listened. Every statement is a number from `olcum.py` (TIMBRE_SCORE and its sub-scores, v1.0 as of 21.10 13:00, still
in progress) or the tini/py style measurements, or something I saw in a PNG I rendered and read.
Test melody: `SP/deneme/deneme_melodi.json` only (provisional, 154 BPM, pickup 0).
Score lines: `TS` = TIMBRE_SCORE (0-100, 100 = original), then the 13 sub-scores (ltas, mel_env, mfcc, band_shares, centroid,
flatness, noise_floor, modulation, pitch, stereo, reverb, dynamics, accent). "mean of seeds 1,2,3" where stated: one seed
has sd about 1.3 TS.
Reference points (olcum kalib): rejected tools/imza_muzik.py renders 23-27; the same melodies through FluidR3 + tini chain
32.8-33.7; an unrelated waltz 9.8; the original re-encoded AAC128 98.9.

## Sources and licences

| Source | Licence | Where | Use |
|---|---|---|---|
| FreePats "Button Accordion HN" (Hohner, recorded by Jeff Stauffer 2023, processed by michael02022), SFZ+WAV 2024-03-29 | **CC0 1.0** (LICENSE.txt in the bank; freepats.zenvoid.org/Organ/accordion.html) | `samples/hohner_cc0/` (17 sustain + 17 release WAVs, sfz, LICENSE, README) | recipe B source layer |
| FluidR3_GM.sf2 (Frank Wen) | MIT (BAGLAM) | /usr/share/sounds/sf2/FluidR3_GM.sf2 | recipe A layers |
| own wavetable reed model, synthetic room IR, own chain | ours | render.py | all recipes |
| the original | measurement only | never read by render.py | only numbers: TARGET_LTAS (1/3-oct, used as a smoothed match-EQ target, rule 1) and the measured chain values from tini.json |

## Iterations

### i0-i1: infrastructure (render.py v0) and first measurement
- render.py v0: score parser (pickup logic, chord voice-leading into B3-D5, default waltz "B C C"), three sources
  (Hohner CC0 sampler with SFZ loops, FluidR3 per-note renderer, own wavetable reed model), per-note envelopes, chain
  (tini.md §5 values: room RT60 0.09/pd 6/build 4/tail -30, wow 14 c, HPF 250/LPF 4.8k, 2/3-oct match EQ, hum, -29.5 LUFS).
  Own BS.1770 loudness agrees with ffmpeg ebur128 (-29.5 / -29.5).
- `v0_B` (Hohner + reed layer): **TS 37.9** (ltas 69, mel 34, mfcc 23, flat 10, noise 7, mod 39, pitch 28, stereo 19, reverb 47,
  dyn 16, accent 13). Already above every earlier attempt (23-34), but the PNG shows the core problem: clean harmonic stripes
  with dark valleys, while the original is fuzzy and dense (`png/v0_B.png`, `png/frames_v0.png`).
- Looked at single STFT frames (`png/frames_v0.png`): the original's valleys between partials are only 10-20 dB deep
  everywhere; ours 40-60 dB. High-resolution view of the original's held C5 (`png/orig_zoomspec.png`): every partial is a
  hump +-30-40 cents wide (strong pitch motion), with codec holes at 3.2-3.3 and 3.7-3.8 kHz.

### i2: lossy-medium noise (signal-dependent, STFT domain)
Hypothesis: the valley filling is the low-bitrate lossy chain (HE-AAC 70k) plus tape-like modulation noise, i.e. noise that
follows the local spectrum. Implemented `medium()`: complex noise at `medium_db` re the 1/3-oct smoothed local spectrum.
| run | medium_db | TS | flat | noise | mel | dyn | accent |
|---|---|---|---|---|---|---|---|
| v1_B_base | off | 37.9 | 10 | 7 | 34 | 16 | 13 |
| v1_B_med | -12 | 45.0 | 29 | 26 | 40 | 31 | 50 |
| v1_B_med6 | -6 | 48.5 | 77 | 52 | 45 | 32 | 52 |
At -6 dB the inter-harmonic floor matches (-18..-22 dB re band mean vs the original's -13..-23).

### i3: room fitted to the original's side-from-mid response (py/roomfit.py, olcum.stereo_room on our own dry mix)
Coordinate search: wet -12 dB, predelay 11 ms, build 2 ms, hold 5 ms, RT60 0.05 s, tail -45 dB. L/R corr 0.647 (orig 0.643),
side-mid -6.6 dB (orig -6.6). `v2_room`: **TS 57.0** (stereo 19 -> 100, ltas 100 with per-band 1/3-oct match).

### i4: pitch behaviour, swells, bellows dynamics; first-beat bug
- Measurement variance: one seed sd ~1.3 TS; decisions use the mean of seeds 1,2,3 from here.
- Envelope plot (`png/env_v4.png`) showed our pah swells were blunted: the Hohner samples have slow natural onsets
  (10-70 % in 33-267 ms). Fix: start each sample where it reaches -4 dB of its sustain and let our envelope shape the
  attack (onset now 2-13 ms before our own 40-50 ms attack). Also found and fixed a bug that dropped the first beat's
  bass when humanize jitter was negative.
- `v5_c` (pah +6 dB re lead, floor -15 dB, oom -1 dB): **58.7** (mean of 3). `v6_a` (lead -1): **60.9**; a 40 ms hold on the
  swell (`v6_b`) overshoots the accent (contrast 9.5 dB vs 3.8): 55.6.

### i5: recipes compared with the same chain/arrangement (mean of seeds 1,2,3)
| recipe | TS | notes |
|---|---|---|
| A_fluid: FluidR3 P23 + P22 +14 c lead, P23 accompaniment | 53.2 | mfcc 28 better, flatness 50, pitch 43, dyn 48, accent 12 |
| B_hohner: Hohner CC0 + own reed layer (-8/-10 dB) | **60.9** | |
| B without the reed layer | 60.7 | the reed layer is neutral at -8 dB |
| C_reed: own wavetable reed model only | 56.3 | modulation 45 (best), pitch 30 |
(the chain/arrangement parameters were tuned on B, so A and C are slightly disadvantaged; see i7 for A re-tuned)

### i6: HF regeneration and LF floor
- mel/MFCC diagnosis (`py/melcmp.py`, `png/melcmp_rB.png`): above 6 kHz our typical frame was 5-10 dB under the original
  (which has HE-AAC SBR noise up to 12 kHz). Added an SBR-like stage (noise with the smoothed envelope of 2.5-5 kHz copied
  above 5 kHz, then the match EQ up to 12.5 kHz): mfcc 20 -> 33.
- The 700-900 Hz excess in our typical frame (+9..12 dB) is the test melody's register (many F5/G5 notes); not an engine
  property, so not "fixed".
- Diffuse mono LF floor 30-260 Hz (-69 dBFS) instead of bare hum lines (the original's C2-C3 region is diffuse noise in the
  CQT), and a medium-noise shape (+4 dB at 250 Hz, -30 dB from 4 kHz, codec cliff): noise 46 -> 59.

### i7: olcum kalibrasyon.md + teshis.md appeared (13:14-13:16); switched to their reading
- Confirms olcum.py TIMBRE_SCORE is the metric to use (I was already calling olcum.py v1.0 through `py/olc.py`).
- Key facts taken from them: the original's pitch motion is mostly NOT a common wow (band coherence 0.24; per band std
  21-24 c). Decomposition from its numbers: common part ~11 c, per-band independent part ~20 c. The 0.5 Hz "wow" is
  per-note mistuning, bends and ensemble detune. Onsets/bar (8.1) react to beating and are a texture measure. Start at
  level, held to a cut at 13.74 s.

### i8: coordinate-descent tuner (py/tune.py, paired seeds 1+2, 2 workers; tune/run_B1.txt, tune_log.jsonl)
Start (recipe B + SBR + LF floor + medium shape): 63.35. Kept: wow_c 16 (66.75), pah_floor_db -18 (67.55),
flutter_per_c 0 (68.4). Rejected (all lower): reed_mistune 6/9, wander 7/10/20, pah_db 4/8, lead_db -3/0, oom_db -3/+1,
pah attack 30/50, hold 15/30, decay 35/70, dyn_arch 5/8, dyn_wander 1/2, dyn_pitch 0.2/0.7, medium -9/-4, flutter
2.5/6, room wet -14/-10. End of round: **68.4** (ltas 98, mel 47, mfcc 36, flat 96, noise 58, mod 37, pitch 63, stereo 75,
reverb 48, dyn 98, accent 68). Note: many single changes are within +-1.5 of each other (noise), so the tuner's choices
are only indicative.

### i9: structural tests on the tuned state (py/batch.py, 2 seeds)
| change | TS | what moved |
|---|---|---|
| base | 68.40 | |
| medium noise in mid/side (joint stereo) | 68.35 | noise 58 -> 65, pitch -7 (noise) |
| two-bar hypermetric bellows accent 2 dB | **69.70** | modulation 37 -> 44 |
| hyper 4 dB | 69.80 | modulation 51, dynamics 98 -> 84 |
| pah high shelf +4 dB | 63.40 | accent 68 -> 20 |
| lead high shelf +4 / -3 dB | 62.35 / 65.40 | accent 14 / 41 |
| low-coherence pitch (wow 6, mistune 15, scoops on every leap, expr 1.5) | 65.10 | pitch 63 -> 31: band std 17.5 (orig 23) |
The low-coherence version is closer to the calibration's reading but loses on the scored pitch distance, because our
partial spread is already too high (18.9-19.3 c vs 15.7) and per-note detune raises it further. Kept the common wow for now.

### i10: room re-fit with the medium stage included, IR now seed-independent (room_seed 7)
The random IR realisation used to change with the render seed (L/R corr 0.67 vs 0.57 between seeds 1 and 2). Fixed it.
Joint grid (py/roomgrid.py): wet -9 dB, predelay 7 ms, build 2 ms, hold 8 ms, RT60 0.04 s, tail -45 dB: L/R corr 0.646,
side-mid -6.4 dB, IR distance 4.3 dB (floor: the identified response at 100-300 ms stays near -25 dB from music
self-correlation; the original reads -31..-38).

### i11: tuner round 2 (tune/run_B2.txt; crashed at the 20th trial when the shared /tmp filled up, state was saved)
Start with the refit room: 65.7 (the fixed room changed the random streams; accent 68 -> 37 by chance). Kept:
wow_c 19 (67.3), wander_acc_c 2 (68.05), medium noise in mid/side (70.2), pah_decay 35 ms (71.65), lead attack 60 ms
(72.1). Not kept: wow 10/13, mistune 8/15, wander 8/20, hyper 2/4.5, medium -4.5/-7.5, pah decay 42, attack 33,
oom -2/0, bass octave -2/-8, dyn_wander 0.8, arch 1.5, lead attack 30.
Disk: deleted my dry cache and old WAVs (the shared disk had 0 MB free); the tuner now overwrites per-worker WAVs and
the dry cache is capped at 12 float32 files.

### i12: variance check and two physical corrections
- 4 seeds of the round-2 state: TS 69.8 / 74.4 / 69.3 / 66.4 (mean 70.0). The accent sub-score alone swings 15-95:
  the beat-2/3 brightness tilt over beat 1 ranges 1.1-3.8 dB between seeds (original 3.76). So differences below ~2 TS
  between configurations are not meaningful at 2 seeds; from here decisions use 4 seeds.
- pah shelf +2 dB / darker oom: 69.95-70.28 vs 69.97 (no change beyond noise; not kept).
- **Where the reverb score goes** (`py/revstage.py`, side-from-mid IR distance with stages switched off): full chain 6.3 dB,
  without wow 4.5, without anything after the room 3.5. A common pitch motion applied after the room (playback wow)
  smears the M->S cross-spectrum. The original's identified response is clean down to -38 dB at 200 ms, which says its
  pitch motion happens before the room (in the source), in agreement with kalibrasyon.md's "not a tape or record wow".
  Moved the slow pitch motion into the source (`wow_pre=1`): IR distance 3.3 dB; 4 seeds: **70.67** (reverb 47 -> 74,
  pitch 63 -> 49 (seed spread 48-65), stereo 89).
- Partial spread (ours 17.3-18.9 c, original 15.7): medium noise adds +1.3 c (spurious peaks), mistune 12 -> 6 only -0.7,
  wander 14 -> 6 only -0.3. Most of it is intrinsic to the Hohner samples (their tremolo beats are 3.4-10 Hz, i.e. up to
  ~26 c at E5, wider than the original's 17-22 c).
