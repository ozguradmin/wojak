# olcum.py calibration

Folder: `/tmp/claude-0/-home-user-wojak/e1bf52df-8e16-5819-ad96-6f6873ef480c/scratchpad/muzik2/olcum/`.
The original was used only for measurement: its features are cached in `cache/`, and nothing from it goes into any
probe. Nobody listened. Every number below was measured, and every PNG mentioned was looked at.

## 1. Usage

```bash
O=/tmp/claude-0/-home-user-wojak/e1bf52df-8e16-5819-ad96-6f6873ef480c/scratchpad/muzik2/olcum
python3 $O/olcum.py aday.wav                                   # full JSON
python3 $O/olcum.py aday.m4a --notalar melodi.json --png aday.png
python3 $O/olcum.py aday.wav --ozet                            # compact summary
```

- **Input**: any audio format ffmpeg can read. It is decoded to 44.1 kHz stereo, and a mono file is duplicated to two
  channels. The analysis window is 0 to 13.77 s. A shorter file is padded; a longer one is measured on its first 13.77 s,
  and its full length is still reported.
- **`--notalar`**: `{"tempo_bpm":..,"notes":[{"bar","beat","dur_beats","midi"}],"chords":[..]}`.
  - `beat` is 1-based, with triplets written as .333/.667.
  - `chords` is optional. It takes either one name per bar from bar 0 (`"Cm"`, `"G7"`, `"Bdim/D"`) or `{"bar","chord"}` objects.
  - A plain list of notes is also accepted.
- **`--tonic`**: the candidate's tonic pitch class (default 0 = C). **`--yenile`** recomputes the reference cache.
  **`--ref`** sets another reference.
- **Output**: one JSON object.
  - `TIMBRE_SCORE`: 0-100.
  - `timbre_subscores`: score, distance, weight, tau and a description for each of the 13 components.
  - `originality_verdict`: PASS or FAIL.
  - `technical`, `timbre`, `musical`, `originality`: every metric is `{value, original, desc, ...}`.
  - `technical_checks`: booleans against the target spec.
- **PNG** (`--png`), with original and candidate side by side:
  - CQT spectrograms of both, each loudness-matched to -29.5 LUFS, on the same 70 dB colour scale.
  - The 1/3-octave LTAS.
  - The modulation spectrum.
  - The 100 ms level envelope.
  - The inter-harmonic floor.
  - The pitch-deviation curve.
- **Runtime**: 8-13 s per file on this machine; the limit is 60 s. The first run builds the reference cache, which takes
  about 12 s more. The cache rebuilds by itself when `olcum.py` changes.
- **Calibration scripts** in `kalib/`:
  - `uret_kalib.py`: the probes.
  - `calistir.py`: runs the whole set into `kalib/sonuc/*.json` and `png/*.png`.
  - `null_chroma.py`: the audio null.
  - `null_sembolik.py`: the symbolic null.
  - `tablo.py`: prints the tables below.

## 2. The harness on the original vs the earlier analyses (cross-check)

| Quantity | olcum.py | Earlier measurement |
|---|---|---|
| LUFS-I / LRA / true peak | -29.5 / 3.6 LU / -16.8 dBTP | tini -29.5 / 3.6 / -16.8; STIL -29.6 |
| Energy shares <250 / 250-1k / 1-4k / >4k | 0.5 / 36.9 / 62.3 / 0.3 % | STIL 0.5 / 36.9 / 62.3 / 0.3 % |
| Centroid (power-weighted / frame median) | 1410 / 1344 Hz | STIL 1346 Hz |
| First / last sound | 0.00 / 13.74 s; tail at -40 dB re LUFS to 13.77 s | STIL 0.00 / 13.75; tini cut at 13.735 |
| L/R correlation, side minus mid | 0.643, -6.6 dB | tini 0.64, -6.6 dB |
| Side-from-mid response at 50 / 75 ms | -16.8 / -26.5 dB | tini -15.7 / -24.6 dB |
| 100 Hz hum | -71.2 dBFS | tini -70.4 dBFS |
| 100 ms level std, crest factor (50 ms windows) | 3.95 dB, 9.9 dB | tini 4.0, 9.9 dB |
| Beat accent ("u a a") | beats 2-3 +4.7 / +4.4 dB louder and +2.9 / +4.6 dB brighter than beat 1 | muzik: beat 1 4.4 dB softer; tilt 4-6 dB |
| Vibrato | 7.1 c RMS in 3.5-9 Hz, no spectral peak | tini: FM std 7.5 c, no periodic vibrato |
| Tuning offset | -11.4 c | muzik raw -13 c; tini about -21 c on the lead notes |
| Tempo | 152.3 BPM (beat-grid fit), 152.0 (comb ACF) | muzik 151.5 (fit to 28 beats); STIL about 152 |
| Key | C minor, r = 0.727 | muzik 0.706 |
| Clicks | 0 | tini 0 |

**Reconciling the "wow".** muzik.md reports a periodic wow of -24..+37 c; tini.md reports a common wow of only 4.4 c.
olcum.py measures the pitch deviation from 12-TET separately in three register bands:

| Signal | Std per band | Mean correlation between bands |
|---|---|---|
| Original | 21-24 c | 0.24 |
| FluidR3 probe with a synthetic common 30 c, 0.5 Hz wow added | 21-24 c | 0.57 |
| FluidR3 probe with no added wow | 7-16 c | 0.27 |

So the original's ±30 c movement is real but mostly **not common** to all registers. It is per-note mistuning, bends
and ensemble detune, not a tape or record wow. Both earlier reports are right about what they measured. The metric is
`pitch_instability_c` and its `coherence_r`.

The tempo differs by 0.8 BPM from muzik's beat fit. Since the same method is applied to every file, comparisons are
consistent.

## 3. Calibration set: main table

`chroma (tools)` is the exact `tools/imza_muzik.py karsilastir` method. `chroma T+tempo` is the best over 12 rotations and
over time scales 0.94-1.06. `audio` and `symbolic` are the originality verdicts (`-` = no `--notalar`).

| file | what | TIMBRE | chroma (tools) | chroma T+tempo | fingerprint | audio | symbolic | LUFS | TP | clicks | tempo | key | onsets/bar |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| orijinal | the original itself | 100.0 | 1.000 | 1.000 | 1.000 | FAIL | FAIL | -29.5 | -16.8 | 0 | 152.3 | C minor | 8.1 |
| kopya_aac128 | re-encode AAC-LC 128k | 98.9 | 0.995 | 0.995 | 0.839 | FAIL | - | -29.5 | -17.0 | 0 | 152.3 | C minor | 8.4 |
| kopya_mp3128 | re-encode MP3 128k | 98.3 | 0.995 | 0.995 | 0.823 | FAIL | - | -29.9 | -17.4 | 0 | 152.3 | C minor | 8.3 |
| kopya_tools | tools copy (orijinal_kopya.m4a) | 98.7 | 0.986 | 0.986 | 0.827 | FAIL | - | -31.5 | -18.7 | 0 | 152.3 | C minor | 8.1 |
| orijinal_p2 | original +2 semitones (rubberband) | 55.7 | 0.252 | 0.926 | 0.161 | FAIL | - | -30.3 | -18.0 | 0 | 152.2 | D minor | 5.0 |
| orijinal_m1 | original -1 semitone | 68.2 | 0.162 | 0.880 | 0.212 | FAIL | - | -30.7 | -17.8 | 0 | 152.3 | B minor | 4.8 |
| orijinal_tempo103 | original tempo +3 % | 79.6 | 0.628 | 0.907 | 0.048 | FAIL | - | -30.3 | -17.7 | 0 | 156.7 | C minor | 5.0 |
| orijinal_10klik | original + 10 clicks (-40..-22 dBFS) | 99.9 | 1.000 | 1.000 | 0.997 | FAIL | - | -29.5 | -16.8 | 10 | 152.3 | C minor | 8.2 |
| orijinal_hiss55 | original + hiss -55 dBFS | 86.8 | 0.988 | 0.988 | 0.716 | FAIL | - | -29.4 | -16.8 | 0 | 152.3 | C minor | 8.5 |
| red_imza | rejected imza_vals.m4a | 23.1 | 0.066 | 0.154 | 0.004 | PASS | PASS | -16.1 | -6.5 | 12 | 154.1 | C minor | 2.5 |
| red_ikinci | rejected imza_vals_ikinci.m4a | 24.8 | 0.104 | 0.133 | 0.004 | PASS | PASS | -16.2 | -7.3 | 7 | 154.1 | C minor | 2.6 |
| red_ucuncu | rejected imza_vals_ucuncu.m4a | 27.1 | 0.155 | 0.199 | 0.004 | PASS | PASS | -16.0 | -7.4 | 8 | 154.1 | C minor | 2.6 |
| ilgisiz_gece_vals | unrelated imza_gece_vals.mp3 | 9.8 | 0.139 | 0.190 | 0.005 | PASS | - | -14.8 | -4.0 | 4 | 132.0 | A minor | 3.1 |
| kapak_orijinal_fluid | COVER: the original's melody and harmony, FluidR3 + measured chain | 24.6 | 0.499 | 0.514 | 0.006 | **FAIL** | **FAIL** | -29.5 | -18.6 | 0 | 151.4 | C minor | 4.6 |
| red_imza_fluid | imza melody, FluidR3 + chain | 33.7 | 0.068 | 0.165 | 0.004 | PASS | PASS | -29.5 | -18.5 | 0 | 154.1 | G minor | 3.2 |
| red_ikinci_fluid | ikinci melody, FluidR3 + chain | 32.8 | 0.101 | 0.145 | 0.004 | PASS | PASS | -29.5 | -18.4 | 0 | 154.0 | C minor | 3.5 |
| red_ucuncu_fluid | ucuncu melody, FluidR3 + chain | 33.2 | 0.117 | 0.180 | 0.004 | PASS | PASS | -29.5 | -18.8 | 0 | 154.1 | G minor | 3.5 |
| rastgele0 | random melody 0, FluidR3 + chain (original's harmony) | 23.9 | 0.281 | 0.290 | 0.003 | PASS | PASS | -29.5 | -17.3 | 0 | 151.9 | C minor | 3.8 |
| rastgele1 | random melody 1, FluidR3 + chain (original's harmony) | 29.9 | 0.201 | 0.219 | 0.003 | PASS | PASS | -29.5 | -17.7 | 0 | 152.0 | G minor | 3.8 |
| rastgele2 | random melody 2, FluidR3 + chain (original's harmony) | 24.4 | 0.231 | 0.235 | 0.003 | PASS | PASS | -29.5 | -16.2 | 0 | 152.1 | G major | 3.6 |
| rastgele3 | random melody 3, FluidR3 + chain (other harmony) | 31.5 | 0.145 | 0.171 | 0.003 | PASS | PASS | -29.5 | -18.4 | 0 | 152.0 | G major | 3.8 |
| rastgele4 | random melody 4, FluidR3 + chain (other harmony) | 30.4 | 0.095 | 0.155 | 0.003 | PASS | PASS | -29.5 | -17.0 | 0 | 152.0 | C minor | 4.1 |
| rastgele5 | random melody 5, FluidR3 + chain (other harmony) | 29.6 | 0.200 | 0.264 | 0.004 | PASS | PASS | -29.5 | -16.5 | 0 | 152.0 | C minor | 3.8 |

The "FluidR3 + chain" probes come from `kalib/uret_kalib.py`:
- Lead: tini R2 (P23 + P22 at +14 c, -2 dB).
- Accompaniment: P23 oom-pah-pah (oom 0.30 s, pah 0.10 s).
- Chain: tini.md §5 (wow 4.5 c, room, two-pass 1/3-octave LTAS match, 5 kHz LPF, hum), then -29.5 LUFS.
- Two simplifications: no 45 ms lead attack fades and no bends.

These are calibration probes, not candidates.

The key estimate is unreliable on some dominant-heavy probes ("G minor/major"). Use `key.c_minor_r` and
`key.profile_corr_with_original` for those.

### 3.1 TIMBRE subscores (0-100)

| file | ltas_db | mel_env_db | mfcc | band_shares | centroid | flatness | noise_floor | modulation | pitch | stereo | reverb | dynamics | accent |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| orijinal | 100 | 100 | 100 | 100 | 100 | 100 | 100 | 100 | 100 | 100 | 100 | 100 | 100 |
| kopya_aac128 | 100 | 100 | 96 | 100 | 100 | 99 | 92 | 100 | 99 | 100 | 100 | 100 | 100 |
| kopya_mp3128 | 100 | 100 | 100 | 100 | 100 | 94 | 82 | 100 | 100 | 100 | 100 | 100 | 100 |
| kopya_tools | 100 | 100 | 96 | 100 | 100 | 99 | 91 | 100 | 98 | 100 | 100 | 100 | 100 |
| orijinal_p2 | 44 | 31 | 31 | 88 | 84 | 99 | 76 | 72 | 78 | 9 | 40 | 60 | 25 |
| orijinal_m1 | 65 | 42 | 55 | 87 | 79 | 93 | 91 | 80 | 87 | 19 | 37 | 65 | 76 |
| orijinal_tempo103 | 98 | 97 | 93 | 83 | 93 | 98 | 97 | 86 | 76 | 19 | 50 | 62 | 61 |
| orijinal_10klik | 100 | 100 | 100 | 100 | 100 | 100 | 100 | 100 | 100 | 100 | 100 | 100 | 100 |
| orijinal_hiss55 | 96 | 71 | 43 | 100 | 100 | 61 | 50 | 100 | 98 | 100 | 99 | 99 | 89 |
| red_imza | 28 | 17 | 11 | 86 | 95 | 8 | 11 | 30 | 4 | 2 | 33 | 10 | 4 |
| red_ikinci | 22 | 19 | 11 | 99 | 98 | 7 | 11 | 44 | 4 | 2 | 31 | 12 | 4 |
| red_ucuncu | 34 | 19 | 12 | 97 | 100 | 8 | 11 | 44 | 5 | 2 | 34 | 10 | 8 |
| ilgisiz_gece_vals | 12 | 9 | 4 | 4 | 6 | 2 | 21 | 18 | 4 | 4 | 18 | 8 | 1 |
| kapak_orijinal_fluid | 30 | 39 | 22 | 60 | 70 | 7 | 9 | 11 | 9 | 26 | 56 | 19 | 5 |
| red_imza_fluid | 54 | 27 | 23 | 96 | 97 | 5 | 7 | 33 | 9 | 18 | 53 | 26 | 18 |
| red_ikinci_fluid | 54 | 35 | 26 | 82 | 94 | 5 | 8 | 26 | 9 | 23 | 55 | 33 | 8 |
| red_ucuncu_fluid | 58 | 29 | 24 | 83 | 94 | 5 | 7 | 31 | 8 | 19 | 55 | 29 | 12 |
| rastgele0 | 28 | 30 | 16 | 52 | 67 | 7 | 10 | 15 | 6 | 40 | 66 | 11 | 5 |
| rastgele1 | 29 | 30 | 18 | 60 | 65 | 6 | 9 | 20 | 6 | 45 | 60 | 70 | 9 |
| rastgele2 | 27 | 24 | 13 | 61 | 89 | 7 | 9 | 15 | 8 | 37 | 57 | 15 | 8 |
| rastgele3 | 54 | 28 | 22 | 98 | 99 | 7 | 8 | 26 | 7 | 18 | 52 | 21 | 6 |
| rastgele4 | 50 | 25 | 17 | 97 | 100 | 5 | 8 | 22 | 8 | 26 | 57 | 12 | 11 |
| rastgele5 | 60 | 36 | 26 | 75 | 91 | 6 | 8 | 14 | 8 | 24 | 56 | 6 | 7 |

## 4. TIMBRE_SCORE

**Definition.** For each component k:
- d_k is a distance to the original, with d = 0 for the original itself.
- The subscore is s_k = 100 / (1 + (d_k / tau_k)^2), a Cauchy curve: 100 at d = 0, 50 at tau, 20 at 2 tau, 10 at 3 tau.
  It is lenient near the original, which absorbs codec noise, and keeps resolution in the tail.
- TIMBRE_SCORE is the weighted mean of the s_k.
- Each tau is set at "a clearly audible difference" for that quantity, for example 3 dB RMS for an LTAS difference. The
  taus were not fitted to the rejected attempts.
- **Loudness is not in the score.** It is a gain fix and is checked in `technical_checks` instead.
- **Composition is not in the score.** The same sound playing different melodies varies by about ±5 points (rastgele
  0-5: 24-32), and the original's composition played with the probe sound does not score higher (24.6).

| component | weight | tau | distance |
|---|---|---|---|
| ltas_db | 14 | 3.0 | 1/3-oct long-term spectrum, 125 Hz-6.3 kHz, dB RMS difference (level-normalised on 250-4000, bands floored at -45 dB) |
| mel_env_db | 7 | 3.0 | mean log-mel envelope (typical frame), dB RMS difference 80 Hz-6 kHz |
| mfcc | 7 | 15.0 | Euclidean distance of mean MFCC c1-c19 (mel clamped at -70 dB re max) |
| band_shares | 5 | 0.10 | total-variation distance of the <250/250-1k/1-4k/>4k energy shares |
| centroid | 4 | 0.25 | abs log2 ratio of the power-weighted spectral centroid (octaves) |
| flatness | 4 | 0.30 | abs log10 ratio of the median spectral flatness inside 250-4000 Hz |
| noise_floor | 8 | 4.0 | inter-harmonic floor (p10 of the bins in each 1/3-oct band re the band mean, 186 ms frames), mean abs dB difference |
| modulation | 14 | 0.20 | modulation spectrum 0.5-20 Hz of 4 band envelopes: (1 - Pearson r) + abs depth difference / 12 dB |
| pitch | 10 | 1.0 | abs d vibrato / 4 c + abs d band pitch-instability / 6 c + abs d partial spread / 6 c + abs log d vibrato peakiness / log 4 |
| stereo | 6 | 1.0 | abs d L/R corr / 0.15 + abs d side-mid / 3 dB |
| reverb | 6 | 6.0 | side-from-mid identified response, dB RMS difference at 10-300 ms (mono or no side: fixed 15 dB) |
| dynamics | 8 | 1.0 | abs d 100 ms level std / 1.5 + abs d fast fluctuation / 1 + abs d crest / 2 + abs d LRA / 2 |
| accent | 7 | 1.0 | "u a a": abs d brightness contrast / 2 dB + abs d bright-pair balance / 2 + abs d level contrast / 2 |

**Weights.**

| Group | Components | Total weight |
|---|---|---|
| Spectral envelope | LTAS, mel, MFCC, shares, centroid, flatness | 41 |
| Texture | noise floor, modulation | 22 |
| Pitch behaviour | pitch | 10 |
| Space | stereo, reverb | 12 |
| Dynamics and the waltz articulation | dynamics, accent | 15 |

**Properties seen in the calibration:**

| Group | TIMBRE_SCORE |
|---|---|
| Original | 100 |
| Re-encodes | 98.3-98.9 |
| Original + 10 clicks | 99.9 (clicks are a technical check, not timbre) |
| Original + hiss at -55 dBFS | 86.8 (the noise floor falls to 50, flatness to 61) |
| Tempo +3 % | 79.6 |
| Pitch -1 / +2 semitones | 68 / 56 (formants move; rubberband decorrelates the channels, so stereo drops to 9-19) |
| FluidR3 + measured-chain probes | 24-34 |
| Rejected attempts | 23.1 / 24.8 / 27.1 |
| Unrelated music-box waltz | 9.8 |

The order of the three rejected attempts matches the owner's remark that "üçüncü" is the least bad. That is three
points and a 4-point spread, so it is weak evidence and not a validation.

**Uncertainties:**
- The weights and taus are a judgement, documented here. No listener data exists.
- TIMBRE_SCORE measures closeness to *this* recording, including its codec. Part of the original's high inter-harmonic
  floor may be Instagram's HE-AAC 70 kb/s quantisation noise. ffmpeg's native AAC at 48-64 kb/s raised a probe's floor by
  only 1-3 dB, and libopus 48k by 5-15 dB in the upper bands. The real Instagram encoder is untested here.

## 5. Originality thresholds

### 5.1 Audio

The rule: **FAIL** if `chroma T+tempo` >= 0.40 or `fingerprint` >= 0.02. **WARN** if `chroma T+tempo` >= 0.32.

**Null.** 40 random C-minor waltzes (`null_chroma.py`):
- In the brief's style: 148-156 BPM, FluidR3 R2 sound and the measured chain.
- Half are over the original's own i/vii° harmony, which is generic and allowed; half are over five other progressions.

| Null group | chroma T+tempo mean | p95 | max | fingerprint max |
|---|---|---|---|---|
| Original's harmony | 0.240 | 0.301 | **0.306** | 0.0049 |
| Other harmony | 0.157 | 0.188 | 0.198 | 0.0048 |

**Positives:**

| Probe | chroma T+tempo | fingerprint | What decides it |
|---|---|---|---|
| Cover (same composition, other sound) | 0.514 | 0.006 | chroma, and symbolically |
| Re-encodes | 0.986-0.995 | 0.82-0.84 | both |
| Pitch shift -1 / +2 | 0.88-0.93 | 0.16-0.21 | both |
| Tempo +3 % | 0.907 | 0.048 | both |

- A plain fingerprint would have missed the tempo-changed copy at a 0.05 threshold. This is why the threshold is 0.02,
  four times the null maximum.
- The tools method alone (`chroma (tools)`) gives 0.16-0.25 on the pitch-shifted copies, which looks original, so the
  verdict uses the rotation- and tempo-invariant version.
- The rejected attempts score 0.13-0.20 and the unrelated piece 0.19.

**Limits.** Chroma only sees pitch-class sequences, and the fingerprint only sees reused audio. Neither is Content ID.
Content ID is not available to test here; these numbers are a proxy.

### 5.2 Symbolic (`--notalar`)

Reference: `analiz/muzik.json` → `melody` (45 notes).

**Checks.** Here n counts intervals: a 3-interval n-gram is a 4-note window.
- `offlimits.py`: N5, S1-S4, R1g-R3g, SK, POV.
- Shared interval n-grams with n = 3 and 4, in two forms:
  - "metric": intervals, inter-onset intervals in triplet slots, and the start slot in the bar;
  - "free": the same without the start slot.
- Per-bar and whole-phrase contour correlation, taking the best bar offset in -2..2.
- Same-bar rhythm cells: all cells, and distinctive (subdivided) cells.
- Melody statistics, and chord-run checks when `chords` are given.

**Null.** 3000 random C-minor waltz melodies (`null_sembolik.py`):
- Quarter-note default, with 8 rhythm cells including one-beat and two-beat triplet groups.
- Interval diet: 45 % steps, 30 % thirds, 12 % repeats, 13 % leaps.
- C4-C6 scale tones, ending on a held C5.

| statistic | null mean | p95 | p99 | max | threshold |
|---|---|---|---|---|---|
| POV | 0.096 | 0.156 | 0.178 | 0.244 | >= 0.25 (offlimits' own) |
| ngram3 metric share | 0.002 | 0.027 | 0.043 | 0.13 | > 0.15 |
| ngram4 free share | 0.001 | 0.000 | 0.031 | 0.091 | > 0.10 |
| contour per bar | 0.249 | 0.537 | 0.658 | 0.805 | > 0.75 |
| contour phrase | 0.166 | 0.427 | 0.527 | 0.686 | > 0.65 |
| distinctive same-bar rhythm cells | 0.52 | 1 | 2 | 3 | > 2 |

The null FAIL rate is 2.2 % from offlimits.py chance hits, plus about 0.3 % from the other rules. Such a FAIL is cheap
for a composer to fix.

My first contour threshold of 0.55 flagged 4 % of the null and two of the rejected melodies (0.61-0.62). I raised it to
0.75 because those values are inside the null range.

**Positive controls** (all must FAIL):

| control | verdict | decided by |
|---|---|---|
| the original | FAIL | violations 73, POV 1.0, every rule |
| transposed +2 / -5 | FAIL | violations 61, n-grams 1.0 (POV 0.09-0.16 is not transposition-invariant) |
| shifted one bar | FAIL | every rule |
| 20 % of notes moved by a scale step | FAIL | violations 28, POV 0.82, ng3 0.45, contour 0.83 / 0.94 |
| 35 % of notes moved by a scale step | FAIL | violations 13, POV 0.62, contour 0.81 / 0.88 |
| triplets flattened to quarters | FAIL | violations 33, POV 0.71 |
| same pitch sequence, plain-quarter rhythm | FAIL | violations 22, POV 0.38 |
| same rhythm, random pitches | FAIL | 5 distinctive same-bar cells (> 2) |
| bars 4-8 pasted into a random melody | FAIL | violations 40, POV 0.69 |
| rejected imza / ikinci / üçüncü | PASS | max contour per bar 0.62, POV 0.07-0.13 |

## 6. Detector checks

**Clicks.** AR(32) residual above 16 robust sigma, isolated under 3 ms.

| Signal | Clicks detected |
|---|---|
| The original, three re-encodes, pitch- and tempo-shifted copies, all FluidR3 renders | 0 (no false positives) |
| Original + 10 injected 3-sample clicks at -40 to -22 dBFS peak (the music peaks at -17) | 10 |
| Rejected attempts (their generator adds about 41 crackles) | 12 / 7 / 8 |

My first threshold of 12 sigma gave 1-8 false hits on the AAC re-encode at codec-noise level (peaks near -60 dBFS), so I
raised it to 16 sigma. Hits within 60 ms count as one click, because a corrupted LPC block can echo a real click as a second hit about 50 ms away.

**Hiss.** Band noise at -55 dBFS (250-6000 Hz) on the original:
- The flatness rises from 0.031 to 0.054.
- The floor in the upper bands rises by up to 10 dB.
- The TIMBRE_SCORE falls to 86.8.

**Start and end.** Thresholds are relative to LUFS-I: sound is above LUFS - 16 dB (-45.5 dBFS for the original, the same
as STIL's -45 dBFS rule), and the tail is above LUFS - 40 dB.

| File | First sound | Last sound | Tail |
|---|---|---|---|
| Original | 0.00 s | 13.74 s | to 13.77 s (its -55 dBFS after-cut residue) |
| Rejected attempts | 0.05 s | 13.18-13.39 s | |

**Fingerprint shift search.** The pitch-shifted copies are found at the right shift: +2.0 and -1.0 semitones.

## 7. Known limits

- **Polyphony.** The pitch metrics come from all spectral peaks in 240-2600 Hz, so they describe the whole texture and not
  the lead alone.
- **Glide share.** `glide_share` (frames moving faster than 600 c/s) is dominated by beating jitter: 0.30 in the original
  against 0.06-0.07 in ours. It is not a portamento detector. Portamento in our attempts is visible in the CQT as slanted
  lines at every note change.
- **Accent metric.** It needs a correct beat grid, and it reports the pattern rotated to start on the darkest beat. It
  cannot tell which beat is the notated downbeat.
- **Reverb.** The reverb estimate needs a side channel. A mono or dual-mono file gets a fixed penalty.
- **Onsets per bar.** librosa onsets react to the original's beating, so "8.1 onsets/bar" is a texture measure and not a
  note count. The same method is applied to every file.
