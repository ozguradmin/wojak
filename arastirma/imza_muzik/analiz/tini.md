# Timbre and production forensics of the original signature waltz

Source: `assets/music/ozel/kanal_orijinal_ses.m4a`, HE-AAC v1 (SBR) 70 kb/s stereo, 44.1 kHz, 13.77 s.
The original was used only for measurement. Nobody listened. Every statement below comes from a number or from a spectrogram I rendered and looked at.
Folder: `/tmp/claude-0/-home-user-wojak/e1bf52df-8e16-5819-ad96-6f6873ef480c/scratchpad/muzik2/analiz/tini/` (scripts `py/`, images `png/`, probe audio `wav/`). Machine-readable data: `../tini.json`.

## 0. What the sound is, in one paragraph

It is a **free-reed waltz in a small room, recorded or processed lo-fi**. The texture has two parts:
- A legato **lead** with two slightly detuned voices (musette or tremolo-reed beating, detune about 17-22 cents). Its odd harmonics are 5-11 dB stronger than its even ones.
- A **reed oom-pah-pah accompaniment**: a dark, soft beat 1 (about 0.3 s) and bright staccato chords on beats 2-3, each a 120-150 ms swell.

There is no bass below 250 Hz and no drums. The room is short (RT60 about 0.1 s, with a faint long tail). On top of the music sit:
- a 100 Hz hum at -70 dBFS
- infrasonic rumble at -56 dBFS
- about 4.4 cents of random wow

There is no crackle and no measurable hiss. Tuning is about A4 = 434-435 Hz, roughly 21 cents flat.

The followers' "u a a" is the accompaniment's brightness pattern, not a vowel:
- beat 1 has a centroid of about 1.07 kHz
- beats 2-3 have a centroid of about 1.61 kHz and are 8.3 dB louder

## 1. Layers (png 01, 04, 05, 06, 07, 13, 21, 22, 34)

| Layer | When | Register | Rhythm and envelope | Evidence |
|---|---|---|---|---|
| Accompaniment "oom", beat 1 | whole clip | partials 240-450 Hz (C4-A4); any lower fundamental is removed by the band EQ | about 0.3 s, dark (centroid about 1070 Hz) | the 240-330 Hz band is 5-7 dB higher at downbeats than at the accents |
| Accompaniment "pah pah", beats 2-3 | whole clip; alone in bars 1-4 | chord tones C4-F5; the top voice is C5/Eb5 (bar 1) and D5/F5 (bar 2) | staccato swells 120-150 ms wide, attack (-10 dB to peak) median 48 ms (16-72), decay to -10 dB median 55 ms (19-76), 15-18 dB over background | `21_burst_shapes.png`; the 3rd harmonics (1.5-1.9 kHz) jump 15+ dB |
| Inner sustained tones | sometimes | D4, F4, G4 | held 0.5-1.5 s (D4 1.05-2.1 s, G4 9.3-10.9 s) | partial tracks; 15 tracks in C4-B4 are longer than 0.6 s |
| Lead melody | **starts at 4.94 s** (bar 5) to the end | C5-Ab5 (fundamentals 516-850 Hz) | legato, 45 ms entrance rise, no dips at note changes (-2.8 dB vs -2.9 dB at random times), final C5 held about 2 s | `20_f0_dominant.png`, `13_tracks.png` |
| Absent | | | bass below 250 Hz, drums or percussion, pads or strings, voice, SFX | LTAS below 250 Hz is -31 dB; no onsets; no clicks |

Observations about levels and the opening bars:
- **Bars 1-4 are an accompaniment vamp.** The "C5-Eb5-D5-F5" line from the earlier pitch tracking (STIL 10.2) is the top voice of the pah chords, not a separate melody instrument.
- Section levels (RMS): intro -36.7 dBFS, melody section -33.3 dBFS, final hold -35.1 dBFS.
- The accompaniment sits about **1-6 dB below the lead**. This is consistent with the harmonic-to-valley ratio at the held C5: 19-20 dB in the original, 21-24 dB for our lead with accompaniment at -6 dB, and 40-56 dB for the lead alone.

## 2. Lead instrument identity

**Harmonics.** Harmonic levels in dB relative to the strongest, measured after the original chain (`a37`):

| note (window) | h1 | h2 | h3 | h4 | h5 | h6 | h7 | h8 | odd-even |
|---|---|---|---|---|---|---|---|---|---|
| C5 516.3 Hz (11.75-12.70) | -7 | -13 | -5 | -10 | 0 | -22 | -12 | -23 | 11.2 |
| D5 583.3 (9.98-10.24) | -2 | -15 | 0 | -13 | -11 | -28 | -19 | | 10.8 |
| Eb5 618.2 (7.34-7.56) | -1 | -12 | 0 | -20 | -19 | -26 | -32 | | 6.3 |
| Ab5 817.6 (8.02-8.44) | 0 | -6 | -3 | -16 | -16 | | | | 5.1 |

- **Odd harmonics dominate** by 5-11 dB, and h3 is often the strongest. The upper limit is real harmonics up to about 4.7 kHz, then the codec cliff. Above about 5 kHz the content is SBR noise with no harmonic peaks (`27_hf_harmonics.png`).
- **Source vs filter.** I fitted a fixed-frequency envelope E(f) and a harmonic-number term H(k) on 30 melody notes. Each explains the data about equally (residual 4.9 dB and 4.8 dB); together they reach 3.9 dB. So there is both a fixed EQ or body shape and an odd-harmonic source.
  - Fixed peaks: 630 Hz and 1.6-2.5 kHz. Fixed dip: 0.8-1.25 kHz.
  - Even harmonics stay about 7-8 dB under their odd neighbours after the EQ is removed.
- **Beating.** The amplitude modulation of the harmonics scales with harmonic number:
  - C5: h1 7.0, h3 20, h4 26.7, h5 33.4 Hz, which is k x 6.7 Hz, a detune of about 22 cents.
  - Ab5: h1 9.0, h3 24.7, h4 31.9 Hz, which is k x 8.3 Hz, about 17 cents.

  This is the musette or tremolo-reed signature. The FluidR3 tango accordion (P23) sample shows the same pattern at about 15 cents (k x 4.5-4.8 Hz). Confidence is moderate: the pattern is clean on 2 of 5 notes, and polyphony masks the others.
- **Tremolo.** Lead harmonic AM is 4.2 dB std. Our chain alone (wow plus room) gives only about 1 dB on a steady sample, so the modulation comes from beating in the source, not from an LFO tremolo.
- **Vibrato: none.** FM std is 7.5 c on the held C5, with only a weak 4.5 Hz component (peak/median 3). Other notes show 10-12 c with no peak. That figure includes about 4.4 c of common wow and leakage from the accompaniment.
- **Expressive pitch.** The lead bends on long notes. Free-bass accordion reeds cannot do this; a harmonica, melodica or voice can.
  - At 4.95-5.20 s a scoop falls about 77 c (640 to 612 Hz).
  - At 8.45-8.65 s a glide rises about 69 c (815 to 848 Hz), visible in h1 and h3, and holds there (`33_glide_check.png`).
  - At about 12.8 s the held C5 drifts about 44 c sharp (516 to 529 Hz).
- **Inharmonicity.** None (within 0.4 %).
- **Breath or bellows noise.** Not separable from the accompaniment, and no evidence of it.
- **Attack.** The lead entrance rises in about 45 ms (10 % to -3 dB). FluidR3 harmonica and accordion take 17-28 ms, so a 40-50 ms fade-in is needed.

**Conclusion:** the lead is a free reed with two detuned voices, odd-heavy, brightness centroid about 1.9 kHz, no vibrato, and occasional 45-75 c bends. A **tremolo harmonica or melodica** fits best. An accordion musette fits the timbre and the accompaniment, but not the bends. The exact instrument is unknown.

## 3. Recording chain

- **EQ target, the 1/3-octave LTAS of mid** (dB relative to the 1.6 kHz band):

  | Hz | 125 | 160 | 200 | 250 | 315 | 400 | 500 | 630 | 800 | 1k | 1.25k | 1.6k | 2k | 2.5k | 3.15k | 4k | 5k | 6.3k | 8k | 10k | 12.5k | 16k |
  |---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
  | dB | -32.0 | -31.2 | -32.2 | -19.7 | -11.6 | -9.3 | -6.6 | -1.3 | -6.8 | -10.2 | -7.9 | 0.0 | -1.6 | -4.7 | -12.5 | -15.2 | -25.7 | -34.7 | -37.0 | -39.5 | -45.4 | -55.9 |

  - This is a target for a match EQ (1/3-octave smoothing or wider) on the **full arrangement**. It is not a filter: part of its shape is the note distribution.
  - Above 8 kHz the curve is codec SBR.
- **Noise.**
  - Hum: 100.0 Hz at -70.4 dBFS peak, 150 Hz -78.3, 200 Hz -83.5, 250 Hz -83.5, 50 Hz -87.3. It is stable within 0.5 Hz, so it was added after any speed effect.
  - Infrasonic rumble: 1-25 Hz at -55.7 dBFS RMS, peak 7.6 Hz. It is mono (L/R r=0.994) and uncorrelated with the music (r=0.01).
  - No crackle: 0 clicks, kurtosis 3.4-4.3.
  - Hiss is **not detectable**. Valley power is at most about -64 dBFS per 1/3-octave band in 250-3150 Hz, and that is an upper bound filled by music. Above 4 kHz valleys are at or below -108 dBFS (codec).
- **Reverb** (system identification of side from mid, `29_sysid_orig.png`, fitted by grid search):
  - The side response peaks at 20 ms, is at -15.7 dB by 50 ms and -24.6 dB by 75 ms, then has a plateau at -27 to -28 dB out to 200 ms and -35 dB at 300 ms.
  - Model: decorrelated stereo noise IR with **early RT60 0.09 s (0.08-0.15), predelay 6 ms, build-up 4 ms, late tail -30 dB at RT60 1.5 s, wet band 150-4000 Hz, wet -8 dB**.
  - Fit vs original: side/mid -6.7/-5.4/-2.8/-6.1 dB against -8.1/-5.3/-6.1/-9.6; coherence 0.69/0.65/0.64/0.71 against 0.66/0.58/0.57/0.73. The model is a little too wet around 1 kHz, which suggests the wet should be darker (LPF about 3 kHz).
- **Stereo.**
  - L/R correlation 0.64; side is 6.6 dB under mid.
  - Mono below about 130 Hz (side is zero there).
  - Side lags mid by about 25 ms. Side is -13 dB under mid at the accents and -4 dB between them.
  - Balance is within ±1.6 dB.
  - Reading: a mono dry source in a decorrelated room.
- **Wow and flutter.** A common pitch modulation of about **4.4 c RMS**, broadband 0.8-5 Hz and not periodic. Slow deviations of simultaneous, unrelated partials correlate at r=0.33 mean (n=255) against 0.00 for the null (n=6466).
- **Saturation.** No clipping. Sample peaks are -18.0/-16.9 dBFS, crest factor 16.3 dB (50 ms windows: 9.9 dB). Harmonic distortion cannot be separated from instrument harmonics, so I recommend none.
- **Dynamics.** -29.5 LUFS, LRA 3.6 LU, 100 ms level std 4.0 dB. Per-bar RMS in dBFS: -37.0, -36.2, -38.0, -36.1, -32.2, -36.8, -32.8, -33.6, -33.1, -33.7, -34.4, -36.9.
- **Edges.** Sound is present from 0.000 s (the clip was excerpted mid-sound). It ends with a hard cut at 13.735 s (-42 to -58 dB within 10 ms).
- **Time-varying filter.** None, apart from the accent brightness changes.

## 4. Candidate match (FluidR3, through the measured chain)

**Method.** I rendered every candidate at -23 c on the same four notes as the original: C5 2 s, and D5, Eb5 and Ab5 at 0.9 s each. Each render went through wow 4.5 c, the fitted room, the band EQ and the noise layer. I then measured the same windows as on the original.

Distances (all in dB-like units):
- **env:** residual after the best smooth fixed EQ fitted across all four notes, so EQ cannot fake a match.
- **odd-even** difference.
- **AM** difference.
- **FM** difference.
- **score** = env + 0.5·|Δodd-even| + |ΔAM| + 0.5·|ΔFM|/3. An extra centroid penalty is shown in `tini.json`.

The env floor is about 4 dB for every candidate, because the original's notes carry accompaniment leakage.

Original targets: odd-even 8.4 dB, AM 4.25 dB, FM 13.5 c, centroid 1919 Hz.

**Singles** (all requested programs and 30 more):

| Program | score | env | odd-even | AM | centroid |
|---|---|---|---|---|---|
| **P23 tango accordion** | **7.13** | 4.25 | 4.8 | 4.12 | 2048 |
| P21 accordion | 8.98 | 6.20 | 5.9 | 5.09 | 1706 |
| P42 cello | 10.03 | 4.96 | | | 1860 |
| P81 saw lead | 10.66 | | | | |
| P22 harmonica | 11.29 | 5.16 | 10.8 | **1.20** (no beating) | 2077 |
| P68 oboe | 11.03 | | | | |
| P71 clarinet | 12.96 | 7.30 | 9.5 | 1.02 | |
| P53 voice oohs | 11.43 | | | | 687 (too dark) |
| P40 violin | 12.25 | | | | |
| P52 choir aahs | 14.35 | | | | |
| P20 reed organ | 15.49 | | 0.7 | 1.11 | |
| P54 synth voice | 16.25 | | | | |
| P19 church organ | 22.74 | | | | |
| P16 drawbar organ | 30.99 | | | | |
| P78 whistle | 14.07 | | | | 516 |
| P79 ocarina | 24.91 | | | | |
| P73 flute | 8.89 | | | | **730** |

Notes on the singles:
- P73 flute scores well, but its centroid (730 Hz) is 16 semitones too dark. P72 piccolo is rejected for the same octave artefact.
- A pure square wave is far off (odd-even 57 dB, env 21-22), so "odd-heavy" does **not** mean square.

**Layered combinations:**

| Combination | score |
|---|---|
| **P22 + P22 at +20 c, -3 dB** | **5.92** (env 4.66, odd-even 9.9, AM 4.19, FM 10.9, centroid 1943) |
| P22 + P22 at +18 c | 5.98 |
| P23 + P22 at +14 c, -2 dB | 6.76 |
| P23 + P22 at +18 c, -4 dB | 7.12 |
| P23 + P53 at -8 dB | 7.28 |
| P71 + P71 at +20 c | 7.29 to 7.98 |
| P21 + P52 at -10 dB | 9.92 |
| P20 + P53 at -6 dB | 14.86 |

**Accompaniment "pah" check.** I rendered staccato chords through the chain:
- P23 at 0.08 s gives attack/decay 34/39 ms; P21 at 0.12 s gives 74/72 ms. Both are in range of the original's 48/55 ms.
- Piano (9 ms), nylon guitar (8 ms) and harp (18 ms) attacks are too sharp, which rules out plucked or struck accompaniment.

### The 3 best timbre recipes (exact parameters)

All three share these settings:
- FluidR3 with reverb and chorus off. Tune the whole render by pitch bend to **-23 cents** (bend range 2 semitones, value -942).
- Per-note fade-in of 40-50 ms (raised cosine), because the FluidR3 attack is 13-28 ms against the original's 45 ms. A CC11 ramp did not slow it.
- Start each next note 30-60 ms before the previous one releases. Solo FluidR3 renders still dip 3-5 dB at note changes, so keep the accompaniment sustained under them.
- Then the chain in §5.

**R1 - tremolo harmonica (best measured match).**
- Layer A: P22 at 0 dB.
- Layer B: P22 detuned +20 c at -3 dB. This gives a 6.0 Hz beat at C5, matching the original's 6.7 Hz (22 c) and 8.3 Hz at Ab5. Use 20-22 c.
- Patch EQ before the LTAS match: +8.9 @400, +7.6 @504, +6.4 @635, +4.8 @800, +3.1 @1008, +1.1 @1270, -0.8 @1600, -1.8 @2016, -3.0 @2540, -5.3 @3200, -8.6 @4032, -12.3 @5080. This is roughly a -4.5 dB/oct tilt around 1.3 kHz.
- Optional bends with pitch bend on 1-3 long notes: a 150-250 ms glide of 45-75 c into or within the note, as measured.

**R2 - tango accordion + tremolo harmonica (best for an accordion character, and the best choice for the accompaniment).**
- Lead: P23 at 0 dB (built-in 15 c musette) plus P22 detuned +14 c at -2 dB.
- Patch EQ: +7.2 @400, +5.9 @504, +4.6 @635, +3.2 @800, +1.9 @1008, +0.7 @1270, -0.3 @1600, -0.8 @2016, -1.8 @2540, -3.9 @3200, -6.8 @4032, -9.9 @5080.
- Accompaniment with P23 (alternative P21):
  - oom on beat 1: 0.30 s, velocity about 85
  - pah chords on beats 2-3: 0.08-0.12 s, velocity about 85
  - level -1 to -6 dB under the lead (the HNR check favours about -6 dB)

**R3 - clarinet musette (an odd-heavy alternative with a darker, woodier colour).**
- P71 plus P71 detuned +20 c, both at 0 dB.
- Measured: odd-even 8.0, AM 4.66, centroid 1633.
- Patch EQ: +4.2 @400, +3.9 @504, +3.6 @635, +2.9 @800, +1.7 @1008, -0.4 @1270, -2.7 @1600, -4.1 @2016, -4.7 @2540, -4.0 @3200, -1.5 @4032, +1.1 @5080.
- Its env residual is worse (6.7 dB vs 4.3-4.7), so use it only for variation.

## 5. Chain to apply after the patch (code in `py/zincir.py`, `py/eslestir.py`)

1. Render dry and mono.
2. **Wow:** band-limited random signal 0.5-5 Hz, 4.5 c RMS, applied as a variable delay.
3. **Room:** stereo decorrelated IR with RT60 0.09 s, predelay 6 ms, build-up 4 ms, tail -30 dB at 1.5 s, wet band 150-4000 Hz (3000 Hz is probably closer), wet -8 dB re dry.
4. **Patch EQ** (above). Then a **1/3-octave LTAS match** to `eq_curve` on the whole 13.75 s arrangement: boost cap +12 dB, 2-3 passes, normalise on the 250-4000 Hz energy. A test on a single-chord probe did not converge, because it has too few notes.
5. Steep LPF at about 5 kHz (48 dB/oct or steeper), to mimic the codec cliff.
6. Hum at 100 Hz -70 dBFS peak, with 150 Hz -78 and 200 Hz -83.5. Rumble at 4-20 Hz -56 dBFS RMS is optional: it is inaudible and was measured only.
7. No hiss (or at most -80 dBFS), no crackle, no saturation, no limiter.
8. Set the level to -29.5 LUFS with true peak -17 dBTP or lower. Use a short fade so that all sound ends by 13.75 s.

## 6. Honest limits

- The instrument name is inferred. "Free reed, two detuned voices, bends" is measured; "harmonica" vs "accordion" is not settled.
- The lead profiles are contaminated by accompaniment, so every candidate's residual is about 4 dB. Rankings 1-4 are close (5.9-7.1).
- The reverb tail below -28 dB is near the identification floor. The hiss figure is an upper bound only.
- The probe audio files are FluidR3 renders of a scale fragment (C5-D5-Eb5) and a generic chord. They contain nothing from the original.

## Files

- Data: `.../muzik2/analiz/tini.json`
- Images (all looked at): `.../tini/png/01_overview.png`, `04_cqt_zoom{1,2,3}.png`, `05_narrowband.png`, `06_band_envelopes.png`, `07_zoom_0_2p5.png`, `13_tracks.png`, `15_am_C5.png`, `21_burst_shapes.png`, `23_ltas.png`, `24_lowfreq.png`, `26_stereo.png`, `27_hf_harmonics.png`, `29_sysid_orig.png`, `33_glide_check.png`, `34_oom_check.png`, `35_recipes_vs_original.png`, `36_fullprobe_vs_original.png`
- Probe audio: `.../tini/wav/R{1,2,3}_*_{heldC5,phrase}.wav`, `fullprobe_R1.wav`, `fullprobe_R2.wav`
