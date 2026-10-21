# Why the three rejected waltzes fall short of the original

The files compared:
- The original: `assets/music/ozel/kanal_orijinal_ses.m4a`.
- The three rejected attempts: `assets/music/imza_vals.m4a`, `imza_vals_ikinci.m4a` and `imza_vals_ucuncu.m4a`, all made by
  `tools/imza_muzik.py`.

The method:
- Every number comes from `olcum.py`. The JSON outputs are in `kalib/sonuc/{orijinal,red_imza,red_ikinci,red_ucuncu}.json`.
- The PNGs I looked at are `png/red_imza.png`, `png/red_ucuncu.png` and `png/kapak_orijinal_fluid.png`.
- Where a cause comes from the generator code, I name the line.
- Nobody listened.
- The order of the ten causes is my judgement, weighing three things: the size of each measured gap, how directly it
  touches the hook the followers name ("u a a u a a"), and how audible it is on a phone. It is not a listening test.

## Summary numbers

| | Original | imza | ikinci | üçüncü |
|---|---|---|---|---|
| TIMBRE_SCORE | 100 | 23.1 | 24.8 | **27.1** |
| Points lost: spectral envelope / texture / dynamics + accent / space / pitch | 0 | 26.6 / 16.9 / 14.0 / 9.9 / 9.6 | 26.8 / 15.0 / 13.8 / 10.0 / 9.6 | 24.9 / 14.9 / 13.7 / 9.9 / 9.5 |
| Originality (audio, symbolic) | | PASS, PASS | PASS, PASS | PASS, PASS |

The originality check is not the problem: all three are original.

## The top 10 causes, ranked

### 1. The waltz pulse is gone: no oom-pah-pah, so no "u a a"

| | Original | imza | ikinci | üçüncü |
|---|---|---|---|---|
| Level of the other two beats re the darkest beat | **+4.7 / +4.4 dB** | 0.0 / -0.9 | -1.1 / 0.0 | -1.7 / 0.0 |
| Brightness contrast of the beats (tilt 1-4 kHz minus 250-500 Hz) | **3.8 dB** | 0.4 | 0.2 | 2.9 |
| Onsets per bar | **8.1** | 2.5 | 2.6 | 2.6 |
| Band-envelope fluctuation, 2-8 Hz | 2.83 dB | 2.46 | 2.52 | 2.57 |
| Modulation spectrum vs the original | | r 0.83 | r 0.86 | r 0.86 |
| Fastest level drop | -235 dB/s | -198 | -208 | -170 |
| Accent subscore | | 4 | 4 | 8 |
| Modulation subscore | | 30 | 44 | 44 |

- In the original, the bright, louder "pa pa" on beats 2-3 is the "a a". In all three attempts it is flat: no beat is
  more than 1.7 dB above another.
- The attempts have about 3.2 times fewer onsets.
- In the PNGs, the original's modulation spectrum has a bump at about 2.5 Hz, the beat rate. The attempts dip there.
- The attempts' level drops more slowly, so there are no staccato "pah" releases.
- Cause in the code: `uret()` plays one sustained harmonium chord per bar, `zarf(L, 0.05, 0.08)`, plus a decaying root.
  The "pa pa" is only a Gaussian swell of +18 %: `pa = 1 + 0.18*...exp(-((tt - x*vurus)/0.09)**2)`. There are no new
  attacks on beats 2-3.

### 2. The pitch is too clean, and it moves the wrong way

| | Original | Attempts |
|---|---|---|
| Pitch instability (std of the deviation from 12-TET in 3 register bands) | **23.0 c** | 4.9-5.4 c |
| Coherence between bands | 0.24 | |
| Partial spread inside a frame | 15.7 c | 7.7 c |
| Tuning | 11 c flat | 0 c (exact A440) |
| Vibrato | 7.1 c, **no peak** | 6.2-6.6 c, **peak at 5.2 Hz** (peakiness 2.7-5.4) |

- The original's notes sit 11-28 c flat of 12-TET, each by a different amount, plus bends. tini measured the held lead notes at C5 -23 c,
  D5 -12 c, Eb5 -11 c and Ab5 -28 c, with bends of +69 c and -77 c.
- The low coherence (0.24) means this is per-note mistuning and bends, not a tape wow. A synthetic common 30 c wow
  measures 0.57.
- The attempts are 4.5 times steadier than the original. They add a periodic vibrato the original does not have, and a
  35 ms portamento at every note change, which shows in the CQT as slanted lines between notes.
- Cause in the code: exact frequencies; `vib = 9*...sin(2*pi*5.2*t)` (delayed); `np.geomspace(onceki, hedef, k)` with
  k = 35 ms; `sap = 0.0028*sin(0.55 Hz) + 0.0009*sin(6.7 Hz)`, a smooth wow of about ±5 c.
- Pitch subscore: 4-5 out of 100, which costs 9.5 points.

### 3. The melody is too slow and too wide, with no triplet motion

| | Original | imza | ikinci | üçüncü |
|---|---|---|---|---|
| Notes per bar | **4.5** | 1.8 | 1.7 | 2.1 |
| Share of triplet notes | **42 %** | 0 % | 0 % | 0 % |
| Range | **8 semitones (C5-Ab5)** | 12 (G4-G5) | 13 (G4-Ab5) | 16 (Eb4-G5) |
| Steps / thirds / leaps of a 4th or more | 43 / 30 / 14 % | 57 / 19 / 14 % | 42 / 37 / 16 % | 46 / 25 / 25 % |

- The original is a narrow, humming top line fused with the pah chords. It repeats on beats 2-3 and spins in
  falling-triplet bars.
- The attempts use half and dotted-half notes, which makes a hymn-like line. They go 5-9 semitones below C5, into the
  register of the accompaniment.
- The off-limits rules forbid the original's cells, not a high note density or triplets as such. muzik.md §5, rules 4-6,
  asks for both.

### 4. The harmony wanders instead of rocking

| | Original | Attempts |
|---|---|---|
| Chroma self-similarity at a 2-bar lag | **0.45** | 0.01 / -0.09 / -0.09 |
| Chroma self-similarity at a 1-bar lag | **-0.35** | -0.12 / -0.04 / -0.08 |
| Different chords in 12 bars | 2 (i and vii°), plus a cadence | 6-7 (Cm, Ab, G, Fm, Eb, Bb, Gm, ...) |
| Longest i-V alternation | | 2-3 bars |

- The original is a hypnotic pendulum: i ↔ vii°6 every bar over a C-D bass.
- The attempts change function on almost every bar, so the "stuck in a loop", music-box feel is lost.
- The strict i ↔ vii°6 over C-D-C-D for four or more bars, combined with R1/R2 cells, is off-limits, but a 1-2-chord
  rocking in general is not. muzik.md lists it as "Not off-limits".

### 5. The texture between the harmonics is too thin and clean

| | Original | Attempts |
|---|---|---|
| Inter-harmonic floor, re band mean (250-4000 Hz) | **-13 to -25 dB** | -18 to -38 dB (mean 9.0-9.5 dB lower) |
| Spectral flatness inside 250-4000 Hz | **0.031** | 0.003 (10 times lower) |
| Spectral peaks per 46 ms frame (240-2600 Hz) | **18** | 12-13 |

- The original's spectrogram is dense and grainy between the partial lines. The attempts show clean lines on a dark
  background (`png/red_imza.png`).
- The hiss in the generator (`hisirti`, smoothed white noise at 0.012) does not fill this: the attempts are still
  9 dB cleaner than the original.
- The floor rises with the signal level in the original (slope 0.2-0.5 dB per dB). So it is partly music-dependent:
  ensemble detune, mistuning, polyphony, room and probably codec. It is not stationary hiss.
- Noise-floor and flatness subscores: 7-11, which costs 10.8 points.

### 6. The spectral balance and voicing are off

| | Original | Attempts |
|---|---|---|
| LTAS distance | | 4.2 (üçüncü) / 4.8 (imza) / 5.7 (ikinci) dB RMS |
| Energy above 4 kHz | 0.3 % | 0.9 % (3 times more) |
| 95 % roll-off | 2.6 kHz | 2.9-3.1 kHz |

Per band, the attempts against the original:

| Band | Difference | Cause |
|---|---|---|
| 200 Hz | **+10 to +12.5 dB** | The octave-down root (`kok - 12`, F2-E3) passes the gentle 2x2-pole 240 Hz high-pass. The original has a cliff of -12.5 dB from 250 to 200 Hz |
| 125-160 Hz | -6 to -8 dB | |
| 400 Hz | -3 to -16 dB | The `equalizer=f=380:g=-4` cut, plus chord voicing gaps |
| 3.2-5 kHz | +2 to +7 dB | 17 harmonics at `1/h**0.6` make a sawtooth that is too bright |

- Spectral-envelope subscores (LTAS, mel, MFCC) lose 21-23 points. This is the largest group, but it is also the
  easiest to fix: a 1/3-octave match EQ is allowed.

### 7. The stereo image and the room are artificial

| | Original | Attempts |
|---|---|---|
| L/R correlation | **0.64** | -0.08 to -0.11 |
| Side minus mid | **-6.6 dB** | +0.7 to +1.0 dB (side louder than mid) |
| Mono fold-down: std over 300-3000 Hz | **0.4 dB** | 6.1-6.2 dB |
| Mono fold-down: deepest notch | -2.4 dB | -26 to -28 dB |
| Side-from-mid response at 50 / 75 / 300 ms | -16.8 / -26.5 / -30.9 dB | -13.9 / -16.8 / -17.3 dB |

- Many phones play mono, and the attempts comb-filter there, with notches every 111 Hz.
- Instead of a short diffuse room (RT60 about 0.09 s), the attempts have a 4-tap comb echo whose energy stays high.
- Cause in the code: `sag = np.roll(sinyal, 0.009 s)*0.97`, a Haas copy, and echo taps at 29, 43, 71 and 109 ms.
- Stereo subscore 2, reverb subscore 31-34: together they cost 9.9 points.

### 8. The loudness and dynamics processing flatten the music

| | Original | Attempts |
|---|---|---|
| Loudness / true peak | **-29.5 LUFS / -16.8 dBTP** | -16.0 to -16.2 LUFS / -6.5 to -7.4 dBTP |
| Loudness range | **3.6 LU** | 0.9-1.3 LU |
| Fast level fluctuation | 2.5 dB | 1.5-1.7 dB |
| Crest factor (50 ms windows) | 9.9 dB | 8.9 dB |
| Lift of bars 4-8 over bars 0-3 | **+3.3 dB** | +1.3 / -0.1 / +0.6 dB |

- The attempts are 13.5 dB louder with peaks about 10 dB hotter. They are almost without dynamics.
- The original's middle section (B) lifts clearly; the attempts barely change.
- Cause in the code: `tanh(1.6*x)` saturation, and `loudnorm=I=-16:LRA=7`, which runs in dynamic mode in a single pass.
- Dynamics subscore: 10-12.

### 9. The lo-fi artefacts are the wrong ones

| | Original | imza | ikinci | üçüncü |
|---|---|---|---|---|
| Isolated clicks detected | **0** | 12 | 7 | 8 |
| 100 Hz hum | **-71 dBFS** | -89 | -87 | -89 |

- The attempts add crackle (`citirti`, about 41 impulses), white hiss and saturation, none of which the original has.
- The original's actual lo-fi signatures are missing: the hum, the flat and uneven tuning (cause 2), and the dense
  floor (cause 5).
- So the "old record" sound in the attempts comes from effects the original does not use.

### 10. The start and the end are shaped differently

| | Original | Attempts |
|---|---|---|
| Level of the first 0.5 s re the median | **-1.4 dB** | **-12.1 to -12.5 dB** |
| Last sound | **13.74 s** | 13.18-13.39 s |
| Level of the last 1 s before the end re the median | **-1.25 dB** | -2.4 / -4.4 / -5.5 dB |

- The original starts mid-sound at full level, with the first pah at 0.24 s.
- The attempts open with accompaniment only and a 30 ms fade-in, and the melody enters at about 0.75 s.
- The original holds the tonic at level up to a hard cut, which makes Instagram's auto-loop seamless (muzik.md §3,
  point 8).
- The attempts fade out early. The `sonus` fade lasts 1.6 s, and `afade` runs from 13.45 s.

## Why üçüncü was "the least bad" (consistent with the owner, but weak evidence)

Among the three, üçüncü is closest to the original on:

| Measure | üçüncü | imza / ikinci |
|---|---|---|
| Beat brightness contrast | **2.9 dB** | 0.4 / 0.2 |
| Notes per bar | 2.1 | 1.8 / 1.7 |
| LTAS distance | 4.2 dB | 4.8 / 5.7 |
| TIMBRE_SCORE | 27.1 | 23.1 / 24.8 |

- Its melody moves on every beat (arpeggios G4-C5-Eb5), which gives back a little beat pulse (cause 1).
- It is the furthest on range: 16 semitones.
- With three files and small gaps, this supports causes 1 and 6 but does not prove them.

## What the recommended FluidR3 + measured-chain sound fixes, and what it does not

I rendered the same three melodies with tini's R2 lead, a P23 oom-pah-pah and the tini.md §5 chain at -29.5 LUFS.
These are calibration probes, not candidates.

| Measure | FluidR3 probes | Rejected attempts | Original |
|---|---|---|---|
| TIMBRE_SCORE | 32.8-33.7 | 23-27 | 100 |
| LTAS distance | 2.6-3.0 dB | | |
| L/R correlation | 0.46 | | 0.64 |
| Clicks | 0 | | |
| Points still lost: modulation / pitch / noise floor / accent | 9.7 / 9.2 / 7.4 / 6.2 | | |
| Pitch instability | 11-12 c | | 23 c |
| Inter-harmonic floor re the original | 12-13 dB lower | | |
| Beat level contrast | +2.9 / +0.7 dB | | +4.7 / +4.4 dB |
| Modulation depth vs the original | +1.2 dB (its pahs leave gaps) | | |

- The probes recover about 8 points, mainly on spectrum, stereo and room.
- The original's composition played with the same sound (the cover probe) scores no higher: 24.6. So the timbre gap is
  in the sound and the arrangement articulation, not in the notes.
- Causes 1, 2 and 5 survive the recommended recipe and need explicit work:
  - pah swells of 120-150 ms over sustained chords, with no gaps;
  - per-note detuning of 10-35 c and 2-3 bends;
  - a denser, ensemble-like floor.

## Targets for the next candidate (the original, measured by olcum.py)

| Area | Target |
|---|---|
| Loudness | -29.5 LUFS, true peak -16.8, LRA 3.6 |
| Start and end | first sound 0.00 s, held to about 13.74 s, then a cut |
| Stereo | L/R correlation 0.64, side minus mid -6.6 dB, mono fold-down std below 1 dB |
| Room | side response -17 / -26 / -31 dB at 50 / 75 / 100 ms |
| Spectrum | the LTAS curve in `cache/` (tini.json `eq_curve`) |
| Floor and flatness | inter-harmonic floor -13 to -25 dB re band; flatness 0.03 |
| Pitch | instability about 23 c with low coherence; spread about 16 c; offset about -11 c; vibrato with no peak |
| Beat accent | beats 2-3 +4.5 dB louder and 3-5 dB brighter than beat 1 |
| Onsets | about 8 per bar (olcum count) |
| Modulation | fluctuation 3.2 / 2.8 / 1.4 dB in 0.5-2 / 2-8 / 8-20 Hz |
| Dynamics | 100 ms level std 4.0 dB, fast fluctuation 2.5 dB, crest 9.9 dB, bars 4-8 about 3 dB above bars 0-3 |
| Harmony | chroma self-similarity about 0.45 at 2 bars and -0.35 at 1 bar |
| Melody | about 4-5 notes per bar, about 40 % triplets, range of a minor 6th to a minor 7th in C5-Bb5, avoiding the original's cells |

All of these are reported by `olcum.py`.

## Uncertainty

- **Ranking.** The order of the causes is a judgement.
- **TIMBRE_SCORE.** Its weights are documented, but no listener data exists.
- **Codec.** Part of the original's dense floor may be Instagram's HE-AAC encode. It could not be reproduced with the
  encoders available here.
- **Accent metric.** It cannot tell which beat is the notated downbeat. It reports the pattern starting on the darkest
  beat.
- **The owner's ranking** is three data points.
