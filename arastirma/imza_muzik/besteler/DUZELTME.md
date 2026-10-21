# Fix pass on the melody judge's notes: b1-4 → b1-4d, b2-2 → b2-2d

What I fixed is in YARGI.md §4-5. b1-1 is untouched. Nobody listened to the results. Everything below comes from the scores,
`olcum/olcum.py`, the judge's own checker (`yargi/denetle.py`) and images I drew and looked at.

Files (SP = `/tmp/claude-0/-home-user-wojak/e1bf52df-8e16-5819-ad96-6f6873ef480c/scratchpad/muzik2`):
- `SP/besteler/b1/b1-4d.json`, plus `.wav` (b1's own FluidR3 preview, `b1lib.render_preview`), `.png` and `_olcum.json`
- `SP/besteler/b2/b2-2d.json`, plus `.wav` (b2's preview, `b2lib.render`, which includes its fix for FluidSynth's same-pitch
  note-off, needed by the new repeated notes), `.png` and `.olcum.json`
- `SP/besteler/duzeltme/`: build scripts (`b1_4d.py`, `b2_2d.py`; both import the composers' own toolkits and edit none of
  their files), score-over-CQT overlays (`ortu_b1-4_b1-4d.png`, `ortu_b2-2_b2-2d.png`, `zoom_b2-2_b2-2d.png`), a key-read
  tool (`anahtar.py`, using olcum's method), an accent check on the written beat grid (`vurgu.py`), and the variant
  exploration (`dene.py`, `var/*.json`)

## b1-4d "Gölge"

The melody changes in only one note. Every other change is in the harmony, bass or counter.

| Where | b1-4 | b1-4d | Why |
|---|---|---|---|
| bars 2 and 4, beat 3 | VI6 (Ab/C) | **i** | (b) The hook's G5 had sat against Ab4 on the bright beat. Now the chord sighs Ab→G with the melody |
| bar 6, beat 1 | VI (bass Ab2) | **VI6 (bass C)** | (a) Removes the outer-voice octaves on the downbeats, F5/F2 → Ab5/Ab2 |
| bar 6, beat 2 | VI | **i** | The same G5-against-Ab4 rub as (b) |
| bar 6 beat 3 to bar 7 | D7/F# (V7/V) | **F#°7/C** (vii°7/V on the C pedal) | (c) There is no F# in the bass, so the melody no longer doubles it into G. The D-major triad that tonicised G is replaced by C and Eb. The cry is unchanged: Bb5 → A5 at 7.89 s, now a b9 sigh onto the 3rd of the diminished chord |
| bar 8 | V7 | **i6/4 (beats 1-2) → V7** | This lowers the key lean. vii°7/V → cadential 6/4 → V7 is the textbook path. The melody's beat 2 changes from D5 to **Eb5**, and Eb F \| Ab G recalls the hook's Eb \| Ab G |
| counter | bars 6-7 D5; bar 8 B4; bar 10 G4 | bars 6-7 **Eb5** (a chord tone); C5 held over the bar line and resolved **4-3 to B4** when V7 arrives; bar 10 **Eb4** under the held C5 | Supports the voice leading and the C-minor read |

The judge's checker now finds **no melody/bass and no melody/counter parallels**. Before, it found two: the 8ves at 5→6 and
the F#→G at 7→8. The hook's beat-3 G5 and bar 6's beat-2 G5 are now chord tones.

| b1 preview (harness) | b1-4 | b1-4d |
|---|---|---|
| verdict / off-limits violations / POV | PASS / 0 / 0.089 | **PASS / 0 / 0.111** |
| chroma_T / fingerprint / contour bar, phrase / rhythm | 0.198 / 0.003 / 0.469, 0.238 / 1 | 0.199 / 0.003 / 0.466, 0.233 / 1 |
| key (r) | C minor 0.708 (G min 0.64, G maj 0.64) | **C minor 0.738** (G min 0.67, G maj 0.60) |
| key, bars 6-9 window only | **G major 0.49**, C minor 0.11 | **C minor 0.62**, G major 0.44 |
| rocking lag2 / lag1 | 0.18 / 0.106 | 0.166 / 0.061 |
| beat contrast (dB) / TIMBRE (engine) | 5.9 / 35.4 | 5.5 / 35.4 |
| technical checks | all ok | all ok |

Across seeds, the key reads are as follows (means; best key per seed):
- **b1 preview, seeds 1-3:** C minor 0.77 against G major 0.56, C minor 3/3 (b1-4: 0.70 against 0.65).
- **hibrit engine** (current `motor/hibrit/render.py`, seeds 1-4): **C minor 0.72 against G major 0.53, C minor 4/4**. b1-4 in
  the same engine read **G major in 3 of 4 seeds** (C minor 0.60 against G major 0.64), which matches the judge's report.

The fixes (a)-(c) on their own (variant A, `dene.py`) did *not* settle the key: hibrit still read G major in 3 of 4 seeds.
The cadential 6/4 in bar 8 is what made the reading robust.

Caveats:
- `i_V_alternation_bars` rises from 3 to 4, which sets the `warn` flag (≥ 4). The harness reads the first chord of each
  bar, and it reads bar 8's i6/4 as "Cm". The run comes from the cadence (bars 8-11: i6/4–V7 | iiø6/5–V7 | i | V7b9), not
  from a pendulum. b1-1 has 5.
- In b1's preview engine, the bars 1-5 window alone reads G minor 0.74 against C minor 0.68, because G is now in the chord
  on the hook's beat 3. b1-1 reads the same way (G minor 0.78). hibrit reads that window as C minor in 4 of 4 seeds.
- The cry now sits over a diminished seventh in bar 7, as the original's does. But it is a different chord (F#°7 on C,
  against the original's B°7 on D) and a different cry note (Bb, not Ab). The harness finds no chord match: the same-chord
  run is still 1.

## b2-2d "Musette des ombres"

| Where | b2-2 | b2-2d | Why |
|---|---|---|---|
| bar 7, beat 3 | iv under B5 | **vii°7** (B-D-F-Ab, F bass kept, no new bass note) | The judge's fix. Fm → B°7 keeps F and Ab and moves C to B. B°7 → G7 keeps B, D and F, so the C6 cry still arrives with V7 |
| bars 5-6, melody | Ab. G F \| Bb. A G | **Ab \| Ab-G \| F, Bb \| Bb-A \| G** | Fix 2: the long note is struck again on beat 2. The second reed's parallel thirds do the same (F \| F-Eb \| C, G \| G-F# \| Eb) |

Kept unchanged, as the judge praised them: the hook statement in bars 1-3 (the limp), the strict i↔iv pendulum (bar for bar),
the triplet run, the C6 4-3 cry, the cadence and the hold. The melody now attacks beat 2 in bars 4-7. Before, it did so in
bars 4 and 7 only. It still sustains across beat 2 in 5 of 9 bars (1-3, 8, 9), deliberately, so the hook's limp stays.

| b2 preview (harness) | b2-2 | b2-2d |
|---|---|---|
| verdict / violations / POV | PASS / 0 / 0.089 | **PASS / 0 / 0.111** |
| chroma_T (warn 0.32) / fingerprint / contour bar, phrase | 0.267 / 0.003 / 0.274, 0.275 | 0.273 / 0.003 / 0.274, 0.275 |
| key (r) | C minor 0.79 | **C minor 0.782** |
| rocking lag2 / lag1 | 0.399 / -0.302 | 0.40 / -0.29 |
| harness accent level, dark → [a, a] (dB) | [0, 1.3, -1.9] | [0, 2.5, 3.1] (tilt contrast unchanged at 0.7) |
| written-grid beat-2 level minus beat-1 level, bars 5 / 6 (`vurgu.py`) | 1.5 / 0.0 | **4.0 / 2.5** |

- **Audio check:** the Ab5 and Bb5 re-attacks are visible in the zoom, and the Ab5 rises 8 dB after beat 2. In bar 7's
  last beat, C4 falls from -25 to -39 dB and D4 rises from -48 to -19 dB, so the B°7 is in the audio.
- **hibrit, seeds 1-4:** C minor 0.73 against G major 0.42, C minor 4/4. b2-2 measured 0.66 against 0.48.
- **Caveats.**
  - In bar 6 the re-struck Bb5 is the 7th of Cm (Cm7 colour, with the second reed's G5 a third below). The original b2-2
    already had that Bb sounding over the same beat-2 chord; now it is re-attacked.
  - The true-peak check (≤ -17 dBTP) fails in b2's preview engine for every b2 piece, b2-2 included, so it is not a melody
    issue.

## Rebuild

```
python3 SP/besteler/duzeltme/b1_4d.py          # json + preview + olcum
python3 SP/besteler/duzeltme/b2_2d.py harness  # json + preview + olcum
python3 SP/besteler/duzeltme/hibrit_anahtar.py SP/besteler/b1/b1-4d.json SP/besteler/b2/b2-2d.json   # key over hibrit seeds
```
