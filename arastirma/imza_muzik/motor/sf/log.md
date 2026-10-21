# Sound engine "sf": iteration log

Folder: `/tmp/claude-0/-home-user-wojak/e1bf52df-8e16-5819-ad96-6f6873ef480c/scratchpad/muzik2/motor/sf/`

- Engine: `render.py`. `render_dev.py` is the development copy; it is identical to `render.py` at the end.
- Usage: `python3 render.py <melody.json> <out.wav> [--seed N] [--set k=v ...] [--stems DIR]`.
- Nobody listened. Every claim below comes from `olcum.py` (TIMBRE_SCORE, 0-100, original = 100), from my own tools
  in `tools/`, or from spectrogram PNGs I rendered and looked at.
- The original was used only for measurement: by `olcum.py`, by `tools/*.py`, and through the 1/3-octave LTAS table
  in `render.py` (rule 1).

## Scale for the score

| Reference | TIMBRE_SCORE |
|---|---|
| Original | 100 |
| Original re-encoded (AAC/MP3 128k) | 98-99 |
| Original +3 % tempo | 79.6 |
| Original's composition with the earlier FluidR3 recipe (kalib "kapak") | 24.6 |
| Earlier FluidR3 + measured-chain probes | 24-34 |
| The three rejected attempts | 23.1 / 24.8 / 27.1 |
| **sf, final: test melody, 5 seeds** | **70.4 mean (70.6, 73.7, 67.7, 70.6, 69.4)** |
| sf, final: a different test melody (`probe/genel_test.json`: pickup, triplets, counter line, staccato pahs) | 66.2 |

There is a seed spread of ±3 points, because the random parts (intonation, wow timing, room IR, noise) change with
the seed. From m11 on, decisions use the mean of 2-5 seeds.

## Sound sources and licences

| Source | Licence | Use |
|---|---|---|
| FluidR3_GM.sf2 (Frank Wen), `/usr/share/sounds/sf2/FluidR3_GM.sf2` | MIT | All instrument samples. Lead: P23 tango accordion and P22 harmonica. Accompaniment: P23. Counter line: P21 accordion |
| Noise, room impulse response, wow, hum, rumble, noise fill, SBR band | generated in `render.py` | |

No other sample library is used, and nothing from the original audio.

## Iterations (test melody `deneme/deneme_melodi.json`, seed 1 unless noted)

Scores in brackets are per seed. Rows marked "explore" were exploratory runs that the logger did not write
automatically; their numbers are copied from the run output.

| # | tag | TIMBRE_SCORE | change, and what the measurement showed |
|---|---|---|---|
| 1 | v01 | 37.7 | First build. Lead: R1 (2 x P22, with musette detune scaled to 6.7 Hz at C5). Accompaniment: P23 oom-pah-pah plus a held pad. Chain: room, wow bumps of 55 c, adaptive LTAS match, hum. The floor and flatness are 15-20 dB too clean, the accent is wrong, the stereo is too wide |
| 2 | v02 | 37.0 | Each sample starts past FluidR3's attack bloom (measured +4.6 dB at 0.1-0.2 s, which made broadband stripes at every note). Pah brightness swell. Per-key tuning. Match from 125 Hz (the 100 Hz band is hum) |
| 3 | v03 | 41.1 | Thin pahs (low shelf -8 dB). Accent subscore 3 → 40: the pahs had been loudest at 250-500 Hz, which made the tilt negative |
| 4 | v04 | 47.4 | **Wow moved before the room.** The side-from-mid estimate of a post-room wow had a floor at about -20 dB at 75-300 ms. Pre-room wow matches the original (`tools/irtest.py`). Room refit with olcum's own estimator (`tools/roomfit.py`): cluster 16 ms, RT60 0.06 s, wet -11.5 dB. Stereo 12 → 98, reverb 56 → 76 |
| 5 | v05 | 47.4 | Following kalibrasyon.md (the movement is "not common"), the common wow was removed and per-note intonation of 9 c added. The pitch instability fell to 11 c, so this was wrong |
| 6 | explore v05a-d | 46.3 / 48.5 / 47.6 / 47.2 | Accompaniment offset +15 / -15 c; lead intonation 16 c; musette layer at -1 dB. The pitch instability stayed at 11-13 c |
| 7 | explore (pitchdiag) | | `tools/pitchdiag.py` plots olcum's per-band pitch curves (`png/pitchdiag_v05.png`). The original's three band curves **wrap at ±50 c together, every ~2 s**, at the wow peak times in muzik.json. So the original's wow is large and common. Its low coherence (0.24) is a wrap artefact of the circular measure |
| 8 | explore v06a-c | 48.4 / 48.7 / **50.7** | The wow came back as flat-topped excursions of 55-65 c, 0.7-0.9 s wide. Pitch instability 21-23 c (target 23) |
| 9 | explore v07a-f | 48.1 / 51.4 / 54.6 / 58.3 / 60.1 | New stage: a signal-following noise fill ("grain"). The original's inter-harmonic floor (-13..-25 dB re band) and flatness (0.031) need about -10 dB noise-to-signal per 1/3 octave. Frame spectra (`png/frames.png`) show the original's jagged floor and codec-like spectral holes above 3 kHz |
| 10 | v08 | 60.9 | Grain calibrated (the `db` parameter is now the real noise-to-signal ratio: +9.4 dB window loss measured) and band-limited to 220-3300 Hz. Flatness 99, floor 59 |
| 11 | explore v09a-c | 62.6 / 63.0 / 61.3 | Phrase arch 3-4 dB, contour 0.3-0.4 dB per semitone, the accompaniment following the lead's dynamics. The first try made renders take minutes: a direct 22k-tap convolution, fixed to a 100 Hz control grid. LRA overshot (5-7 LU against 3.6) |
| 12 | v10 | 64.3 | Arch 2.5, contour 0.25, follow 0.5, musette layer -4 dB, per-beat pah brightness, rare-peak control. Note: this peak control later turned out to make clicks (see #29) |
| 13 | explore v10a-b | 62.5 / 61.1 | Lower pah brightness. Single-seed changes of ±3 points are noise, so decisions switch to multi-seed |
| 14 | m11 | 60.6 [65.2, 61.1, 55.5] | Multi-seed baseline. The stereo varied with the room seed: L/R corr 0.63-0.74 |
| 15 | m12 | 63.5 [64.9, 64.5, 61.0] | Side/mid normalised to -6.6 dB. Flutter widened to 1-12 Hz, 6 c (a flat vibrato spectrum; the 3 Hz peakiness had come from narrow flutter) |
| 16 | m13a-c (2 seeds) | 62.5 / 65.6 / 57.5 | Musette layer -7 dB; accompaniment level -1 dB with a deeper floor; accompaniment patch P21. A +8..+10 dB excess at 5.6 Hz in the 250-1000 Hz envelopes persists for every patch (`tools/moddiag.py`) |
| 17 | m14 | 62.9 [64.4, 61.2, 63.2] | **Two-band accompaniment envelopes.** Below 1 kHz a smooth bed; above 1 kHz a pah swell (-10 dB in 55 ms to -16 dB). The pulse-like 5 Hz excess in the low bands halved; modulation 44 → 54 |
| 18 | m15 | 64.6 [65.1, 65.6, 63.1] | Side/mid normalisation moved after the match EQ (the EQ had shifted it by 1 dB) |
| 19 | m16 | 64.3 | Codec-like band edge: 12th-order LP at 4.8 kHz plus an SBR-style band above (shifted 2.4-4.8 kHz, 60 % envelope noise). Neutral on the score but visually like the original's noise-like top. Kept |
| 20 | m17 | 67.9 [68.8, 69.2, 65.8] | Match-EQ kernel [0.1, 0.8, 0.1] instead of [0.25, 0.5, 0.25] (still 1/3-octave bands). LTAS 77 → 94. It needed a +10 dB 630 Hz band |
| 21 | m18 / m19 | 65.3 / 65.6 | A local-prominence limit of 7 dB (no melody-specific resonances) cost band shares 99 → 82: the original's 630 Hz band carries much of its energy |
| 22 | m20 | 67.5 [67.5, 69.2, 65.8] | Local limit 10 dB: keeps the original's 630 Hz formant and still guards extreme melodies |
| 23 | explore q0-q6 | modulation sub 40 → 65 | Per-beat pah fullness (beat 2 full, beat 3 thin) restores the bar-rate modulation at 250-500 Hz. A weaker musette layer reduces 4-8 Hz beating. A slower low-band attack does not help |
| 24 | explore (hold probe) | | A held-chord accompaniment still shows a 4.5-5.6 Hz peak: re-triggered P23 notes with their own musette beating. It is inherent in the sample |
| 25 | m21a-c (2 seeds) | 66.2 / 63.7 / 63.7 | Pah low [0, -8] with musette -8 helps modulation (67) but beat 2 becomes too full, so the accent collapses. P20 reed organ or a P23+P20 blend: worse pitch and accent |
| 26 | m22 | 66.5 [69.4, 66.4, 63.8] | Per-beat pah calibrated on the original's known beat grid (`tools/beats.py`): low [-3, -7], bright [7, 6.5]. Accompaniment -2 dB. Musette -8 dB |
| 27 | m23 | 67.4 [68.1, 68.4, 65.6] | Flutter 9 c, arch 2.0, follow 0.35, musette -6. Pitch 54, dynamics 68 |
| 28 | explore (probe_kapak) | 59.1 | **Measurement probe only (deleted):** the original's composition through sf. mel 42 and MFCC 25 are no better than with the test melody. So the mel/MFCC gap is in the sound, not the notes |
| 29 | m24 | 69.9 [70.8, 72.0, 66.8] | Consolidated: 4-voice pahs, pah bright [6, 6], grain over 1/2 octave at -10.5 dB up to 3 kHz. **olcum found 5-9 clicks per render since v10:** the old peak control made gain steps at the limited peaks |
| 30 | ck | 70.9 (seed 1), clicks 0 | Peak control rewritten: min-filter plus moving average, so there are no gain steps |
| 31 | m25-m27 | 68.3 / 69.2 / 69.6 | Pah brightness limited to 1-2.8 kHz (a visual impression from the held-C5 probe); grain time smoothing; final calm. olcum's 2-4 kHz beat modulation prefers broadband pah brightness, so the split is off by default |
| 32 | m28 | 69.3 [70.3, 71.8, 65.9] | Broadband pah brightness again; final calm 0.6 (measured: under the original's held C5 the pahs rise only about 3 dB, against 8-12 dB elsewhere) |
| 33 | m29-m31 | 68.6 / 68.6 / 68.5 | Pah bright [4, 5]; 2-bar heavy/light phrasing; per-bar bellows swell. All within the seed noise. The phrasing options exist but are off |
| 34 | m32 | 70.9 [73.1, 72.1, 67.6] | **Lead R2:** P23 tango accordion plus P22 +14 c at -3 dB. Modulation 48 → 69 |
| 35 | m33 / m34 | 69.5 / 69.9 | Room cluster 19 ms, width 8 (reverb 86-87); pah bright [2.5, 4] |
| 36 | m35 | 71.0 [72.0, 74.4, 66.7], seeds 4-5: 71.2, 69.1 | R2 lead, room 19/8, pah bright [4, 5] |
| 37 | m36 = FINAL | **70.4 [70.6, 73.7, 67.7, 70.6, 69.4]** | m35 plus a 4 dB cap on the lead's note-to-note dynamic range (for melodies with a wide span; the generality probe's LRA went 6.6 → 5.4). Peak threshold -17.8 dBFS. All olcum technical checks pass |

**Plateau.** The last 8 multi-seed configurations score 68.5-71.0, inside the ±3 seed noise. Further parameter
moves trade one subscore against another: accent against modulation, musette depth against pitch, and so on. So I
stopped here.

## Final metrics (test melody, seed 1; `out/final_deneme_s1.wav`, `out/final_deneme_s1.olcum.json`)

TIMBRE_SCORE is 70.5 on this render. Its subscores:

| Subscore | Score |
|---|---|
| LTAS | 97 |
| mel envelope | 48 |
| MFCC | 32 |
| band shares | 100 |
| centroid | 99 |
| flatness | 100 |
| noise floor | 61 |
| modulation | 65 |
| pitch | 64 |
| stereo | 100 |
| reverb | 90 |
| dynamics | 48 |
| accent | 38 |

All technical checks pass. Originality: audio PASS (chroma 0.17, fingerprint 0.003).

| Quantity | sf | Original |
|---|---|---|
| LUFS / LRA / true peak | -29.5 / 3.0 / -17.7 | -29.5 / 3.6 / -16.8 |
| First / last sound | 0.00 / 13.7 s | 0.00 / 13.7 s |
| 100 Hz hum | -70.4 dBFS | -71.2 |
| Clicks | 0 | 0 |
| Centroid | 1390 Hz | 1410 |
| Flatness (250-4000 Hz) | 0.031 | 0.031 |
| LTAS distance | 0.5 dB | 0 |
| Vibrato (3.5-9 Hz) | 7.1 c | 7.1 |
| Pitch instability / partial spread | 21.0 / 14.4 c | 23.0 / 15.7 |
| Glide share | 0.21 | 0.30 |
| Tuning offset | -10.8 c | -11.4 |
| Spectral peaks per frame | 19 | 18 |
| L/R correlation / side-mid | 0.643 / -6.63 dB | 0.643 / -6.62 |
| 100 ms level std / fast fluctuation / crest | 3.2 / 2.6 / 9.7 dB | 4.0 / 2.5 / 9.9 |
| Envelope fluctuation 0.5-2 / 2-8 / 8-20 Hz | 2.3 / 2.9 / 1.7 dB | 3.2 / 2.8 / 1.4 |
| Accent tilt, beats 2/3 (olcum, rotated) | +4.8 / +5.4 dB | +2.9 / +4.6 |
| Accent level, beats 2/3 (olcum) | +4.6 / +4.1 dB | +4.7 / +4.4 |
| Accent on the known grid (`tools/beats.py`), tilt / level | +2.4 / +3.4 and +3.6 / +3.2 | +1.7 / +3.7 and +4.3 / +4.1 |
| Legato gaps | 0 | 0 |

## Remaining weaknesses (measured)

1. **Typical-frame spectrum (mel 48, MFCC 32).** Against the original, the log-mel mean is:
   - 6-11 dB too high at 650-800 Hz;
   - 5-8 dB too low at 1.0-1.25 kHz.

   The power LTAS matches within 1 dB, so the difference is in how steadily the energy is present. The original keeps
   the 1 kHz region filled all the time. The gap is the same with the original's own composition (probe #28), so it
   is the instrument and voicing, not the melody. A log-domain match would fix it, but that is a different statistic
   from the allowed LTAS match, so I did not do it.
2. **Slow modulation.** The 0.5-2 Hz envelope fluctuation is 2.3 dB against 3.2. The 100 ms level std is 3.2 dB
   against 4.0. The original has deeper bar and phrase level swings, partly from its composition (dense triplet bars).
   The optional phrasing controls (`ensemble.hyper_db`, `ensemble.bar_swell_db`) did not raise the score.
3. **Pitch.** Glide share is 0.21 against 0.30, and pitch instability 21 c against 23 c.
4. **Accent subscore is unstable** (30-65 across seeds and small changes). olcum fits its own beat phase; its 154.6 BPM
   estimate against the real 154 drifts about 50 ms over the clip. On the true grid our per-beat levels and tilts are
   within about 1 dB of the original.
5. **Band edges.** The 4 kHz inter-harmonic floor is -31 dB against -47 (the original's codec band edge is cleaner).
   The bass fundamentals at 130-250 Hz are tonal blobs in the CQT; the original's sub-250 Hz energy is diffuse.
6. **The codec-like stages are an emulation of the original's degraded transfer:** noise fill at -10.5 dB per
   1/3 octave, plus the SBR band. If part of the original's floor is Instagram's own encode, our upload will get that
   encode on top and end up denser than the original. `--set chain.grain.db=-14` is the lighter option. I could not
   test a real HE-AAC encode here.
7. **FluidR3 has one sample per key and patch.** All per-note variation comes from our processing (intonation, wander,
   envelopes, noise). P23's built-in musette beating at 4.5-5.6 Hz remains visible in the 250-1000 Hz envelopes.
8. **Seed spread is ±3 points.** Pick the seed per video by measuring 3-5 seeds.

## Files

| Path | Contents |
|---|---|
| `render.py` | The engine (the CFG dict at the top holds every parameter, with its source) |
| `tools/ev.py` | olcum run and compact table |
| `tools/batch.sh`, `tools/multi.sh` | Render + measure, single seed and multi-seed |
| `tools/beats.py` | Per-beat accent on a known grid |
| `tools/moddiag.py`, `tools/meldiag.py`, `tools/pitchdiag.py` | Diagnostics in olcum's own feature code |
| `tools/roomfit.py`, `tools/irtest.py` | Room fit |
| `tools/spek.py`, `tools/frame.py` | Side-by-side spectrograms and frame spectra |
| `out/final_deneme_s1.wav` | Final test-melody render, seed 1 |
| `out/final_genel_test_s1.wav` | Generality probe |
| `out/final_probe_held_c5.wav`, `out/final_probe_phrase3.wav` | Short probes |
| `out/v01.wav` | The first build, for comparison |
| `png/final_deneme_s1_olcum.png` | olcum comparison PNG |
| `png/final_zoom_5_8.png` | 5-8 s zoom against the original |
| `png/final_probes.png` | Held C5 and the 3-note phrase against the original's held C5 |
| `png/genel_zoom.png` | Generality probe, first 4 s against the original's first 4 s |
| `png/pitchdiag_v05.png` | The wrap evidence for the common wow |
| `png/frames.png` | Frame spectra |
| `probe/*.json` | Probe melodies |

The original-composition probe (#28) was measurement-only and its audio is deleted.
