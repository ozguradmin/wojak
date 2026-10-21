# Melody judge: the 8 candidate waltzes (b1-1..b1-4, b2-1..b2-4)

Judge: melody/composition lens (a demanding film/TV composer reading the score). Nobody listened. Everything below rests on
the JSON scores, my own harness re-runs, a piano-roll comparison I drew, and a small voice-leading checker I wrote.

Files (all under `/tmp/claude-0/-home-user-wojak/e1bf52df-8e16-5819-ad96-6f6873ef480c/scratchpad/muzik2/besteler/`):
- `yargi/olcum/<id>.json`: my re-runs of `olcum/olcum.py <wav> --notalar <json>` for all 8 previews, and
  `yargi/olcum/mt_<id>_<engine>.json` for b1's 5 engine renders in `b1/motor_testi/`.
- `yargi/rulo_hepsi.png`: piano rolls of the original transcription and all 8 melodies on the same bar grid
  (blue = lead, green = counter, red = chord symbols). I looked at it.
- `yargi/oku.py` (lead-sheet printer), `yargi/denetle.py` (non-chord tones, outer-voice and melody/counter parallels),
  `yargi/rulo.py` (the piano roll).

Bar numbering: both composers write the 2-beat pickup as bar 0 (bar 0 beat 2 = 0.00 s), so bars 1-9 carry the tune and
bars 10-11 the held tonic. The original's transcription uses the same bar numbers (its bar 0 beat 2 is at 0.24 s), so
"bar 7" means the same place in all nine.

## 1. Verdict

| Rank | Piece | Score | One line |
|---|---|---|---|
| **1** | **b1-1 "İç Çekiş" (the sigh)** | **8.5** | Best-crafted and most unified. The hook is a dissonant sigh on the soft "u" that resolves onto a repeated bright "a a". Clean voice leading, a real arch to an octave cry, and a Neapolitan Db→C cadence |
| **2** | **b1-4 "Gölge" (shadow)** | **7.5** | The closest emotional twin: a low "u" under two sighing "a a" beats over a hypnotic i↔VI6 tonic pedal, with a romance-waltz climax. Three fixable voice-leading slips keep it from 8 |
| **3** | **b2-2 "Musette des ombres"** | **7.5** | The one distinctive alternative that is genuinely strong: a limping musette cell with chromatic neighbours, a plagal pendulum and accordion thirds. It is less eerie, and the melody skips beat 2 |
| 4 | b2-1 "Kurmalı Kutu" (wind-up box) | 7.0 | Strong music-box hook, but it is the closest harmonic cousin: bars 0-7 have the original's chords bar for bar. It also sits a 4th higher than the original |
| 5 | b2-3 "Çingene Dansı" (danse macabre) | 6.5 | A characterful Hungarian-minor hook, but a foreign colour at full strength, and the climax is unresolved |
| 6 | b1-3 "Atlıkarınca" (carousel) | 6.0 | A very hummable twirl, but the most literal i↔V7 twin. It has the original's whole arch in spirit and its F#-cadence gesture, and its climax is weak |
| 6 | b2-4 "Kürdi Ninni" (sinking lullaby) | 6.0 | A good descending lullaby cell. The Phrygian planing brings parallel fifths, a tritone leap goes onto a consonant Dorian A climax, and the colour is foreign |
| 8 | b1-2 "Çan Kulesi" (bell tower) | 5.5 | A clean but static G-bell hook over an Andalusian descent. There is no rocking at all, and the tonal centre measures as G |

All 8 PASS the harness's originality gates (audio and symbolic): 0 off-limits violations, POV ≤ 0.156, transposed chroma
≤ 0.267 (warn 0.32), fingerprint ≤ 0.004. None of them is the same tune. The by-ear risk differences are harmonic and
structural, and they are listed per piece.

## 2. How I scored

Weights: hook and memorability 20 %, emotional match to the original (eerie, melancholic, old-world waltz, the "u a a")
20 %, harmony and voice leading 15 %, originality by ear (would a follower hear the same tune or the same skeleton?) 15 %,
phrase arc and climax 10 %, rhythm against the waltz pulse 10 %, ending and loop 5 %, playability 5 %. Following the
brief, the closest emotional match with a strong hook outranks clever-but-foreign colour. I rounded each score down to
the nearest 0.5 when fixes are needed before delivery.

| Piece | Hook | Emotion | Arc/climax | Rhythm | Harmony/VL | Ending/loop | Play | Originality by ear | **Score** |
|---|---|---|---|---|---|---|---|---|---|
| b1-1 | 9 | 8.5 | 9 | 8.5 | 8.5 | 9 | 9 | 8.5 | **8.5** |
| b1-4 | 7.5 | 9 | 8.5 | 8.5 | 6 | 8.5 | 9 | 8 | **7.5** |
| b2-2 | 8 | 6.5 | 8 | 6.5 | 7.5 | 7.5 | 9.5 | 9 | **7.5** |
| b2-1 | 8 | 7.5 | 8 | 8 | 7 | 8 | 8.5 | 5.5 | **7.0** |
| b2-3 | 7.5 | 6 | 6 | 7.5 | 6 | 7.5 | 8.5 | 8.5 | **6.5** |
| b1-3 | 8 | 7 | 5 | 8.5 | 7 | 7 | 9 | 4.5 | **6.0** |
| b2-4 | 7 | 5.5 | 5 | 6 | 5.5 | 7.5 | 9 | 8.5 | **6.0** |
| b1-2 | 5.5 | 6 | 7 | 7.5 | 7 | 7.5 | 9 | 7 | **5.5** |

## 3. Measurements (my re-runs; previews unless marked)

| Piece | Verdict | off-limits viol / POV | chroma_T | fingerprint | contour bar / phrase | same-chord run vs original | i-V alternation bars | rocking lag2 / lag1 | key read (preview; hibrit) | beat contrast dB (preview) | notes/bar | triplets | range (st) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| original | | | 1.0 | 1.0 | | | | 0.45 / -0.35 | C minor 0.73 | 3.8 | 4.5 | 42 % | 8 |
| b1-1 | PASS | 0 / 0.133 | 0.176 | 0.003 | 0.07 / 0.14 | 1 | 5 | 0.11 / -0.09 | C minor 0.69; C minor 0.74 | 5.1 | 3.8 | 32 % | 12 |
| b1-2 | PASS | 0 / 0.133 | 0.117 | 0.003 | 0.24 / -0.04 | 1 | 2 | -0.02 / -0.09 | **G minor** 0.79; **G major** 0.73 | 3.2 | 3.8 | 32 % | 9 |
| b1-3 | PASS | 0 / 0.133 | 0.192 | 0.003 | 0.07 / -0.00 | 2 | 5 | 0.19 / -0.14 | **G minor** 0.75; **G major** 0.62 | 4.7 | 4.8 | 56 % | 9 |
| b1-4 | PASS | 0 / 0.089 | 0.198 | 0.003 | **0.47** / 0.24 | 1 | 3 | 0.18 / 0.11 | C minor 0.71; G major 0.65 | 5.9 | 3.9 | 36 % | 10 |
| b2-1 | PASS | 0 / 0.133 | 0.213 | 0.004 | -0.00 / -0.05 | **8** | **8** | 0.36 / -0.16 | C minor 0.62 | 2.8 | 3.7 | 40 % | 10 |
| b2-2 | PASS | 0 / 0.089 | 0.267 | 0.003 | 0.27 / 0.28 | 1 | 0 | **0.40 / -0.30** | C minor 0.79 | 0.7 | 3.6 | 25 % | 9 |
| b2-3 | PASS | 0 / 0.133 | 0.178 | 0.003 | 0.07 / -0.08 | 1 | 2 | 0.35 / 0.04 | C minor 0.65 | 0.4 | 4.0 | 38 % | 11 |
| b2-4 | PASS | 0 / 0.156 | 0.207 | 0.003 | 0.39 / -0.11 | 1 | 0 | 0.28 / -0.30 | C minor 0.73 | 1.6 | 3.9 | 54 % | 10 |

How to read the measurements:
- **"same-chord run"** is `olcum.chord_check`: the longest run of bars whose chord equals the original's chord in the same
  bar, at the best offset of ±2 bars. b2-1 matches the original **for 8 consecutive bars**, which is the harness's own
  harmonic-cousin warning.
- **TIMBRE_SCORE did not affect the ranking.** It is an engine property. b1's previews score 31.5-35.4 and its hibrit
  renders 55.1-59.6; b2's previews score 32.0-39.2. Any melody can go through the hibrit engine.
- **Beat contrast** is partly engine as well, because b1's and b2's preview engines differ. Within b2 (one engine),
  b2-1 (2.8 dB) keeps the "u a a" best. b2-2 (0.7) and b2-4 (1.6) are weaker, which fits their melodies sustaining
  across beat 2. b2-3 (0.4) contradicts that explanation, so this is weak evidence.
- **Rocking.** The b2 pieces keep a 7-8-bar pendulum and come closest to the original's lag2 0.45. The b1 pieces rock for
  4-5 bars and then take a harmonic journey (lag2 0.11-0.19). teshis.md cause 4 says the lost rocking hurt the rejected
  attempts, so this counts somewhat against b1, b1-2 most of all.
- **Key reading.** b1-2 and b1-3 read as G in both engines. Their melodies dwell on G over a dominant-heavy harmony.
  b1-4 reads G only in hibrit. The long C-minor hold will settle the ear, but the tonal centre is measurably weaker.

## 4. Piece by piece

### b1-1 "İç Çekiş": 8.5 (rank 1)

`(F G) | Ab G G | Eb D F | Ab G G | [Eb F Eb] D D | Eb [G F G] Ab | F G [F Ab B] | C6 B G | [Ab G Ab] G Eb | Ab F Db-(C | C~~`
over `i | i | V6/5 | i | V6/5 | i(VI6) | iv6(vii°4/2) | Vsus4-V7 | i | N6 | i | V7`.

- **Hook (9).** The 2-bar cell is a semitone appoggiatura on the soft, dark "u", resolving onto a repeated bright "a a":
  Ab–G–G, then Eb–D–F. It is stated twice exactly (bars 1 and 3), and bar 4 echoes it with a turn and D–D.
  - It returns in bar 8 ([Ab G Ab] G).
  - The same semitone-sigh idea makes the climax (C6→B5) and the cadence (Db→C), so the piece grows from one motif.
  - The repeated note on beats 2-3 keeps the rhythm of the followers' "u a a" without the original's rising-third cell.
    The direction is inverted (high, then lower), so it cannot be mistaken for the original's line.
- **Voice leading (8.5).** This is the craft point: each dissonance sits on the soft beat 1 over the quiet chord bed, and
  its resolution note is a chord tone of the bright pa chords. No outer-voice parallels were found.
  - The only real rub is G5 against Ab4 on beat 2 of bar 6 (iv6). It is a neighbour note and reads as Fm(add9).
- **Arc (9).** The line climbs Eb → Ab → the diminished arpeggio F–Ab–B, which brings in the augmented second the brief
  asks for. It reaches C6 at 7.89 s (57 %), which falls to B5 as a 4-3 suspension over V. It then descends to a
  Phrygian/Neapolitan cadence, and the tonic arrives a triplet early (11.32 s).
- **Ending and loop (9).** V7 sits under the held C in bar 11. The loop restarts on F–G over i, so the dominant resolves
  into bar 0.
- **Against it.**
  - The range is an octave (C5–C6), beyond the brief's minor 7th, and only for the cry.
  - The second half travels through 7 chords, so lag2 is only 0.11. The hypnotic pendulum lasts 5 bars, not 8. A shorter
    "journey" (keeping i–V6/5 through bar 5 and replacing iv6 with a second i bar) would add rocking if wanted.
  - The i↔V6/5 pendulum is the same function as the original's i↔vii°6. But it is phase-shifted by a bar (the tonic is
    on bars 0-1 and 3) and sits over a C–B bass, so only 1 bar has the same chord as the original's bar.
- **Owner.** This is the most "composed" of the eight and still reads as the same species: a dark minor waltz rocking on
  the dominant, with triplet spins in the middle and one cry. In the hibrit engine it is the only b1 piece that still
  reads C minor, and its beat accent is +5.1/+5.1 dB against the original's +4.7/+4.4.

### b1-4 "Gölge": 7.5 (rank 2)

`(G F) | Eb G F | Eb Ab G | Eb G F | [Eb D Eb] Ab G | F [G Ab G] F | Ab G [F# G A] | Bb A F# | [G F G] D F | Ab G [F D] C | C~~`
over `i | i | VI6/C | i | VI6/C | iv | VI–V7/V | V7/V | V7 | iiø6/5–V7 | i | V7(b9)`.

- **Emotion (9).** It is the closest of the eight to the follower's "u a a". A low Eb5 "u" on every downbeat is followed
  by two higher, sighing "a a" beats (G–F, Ab–G).
  - The pendulum is the gentlest one, i↔VI6 over a tonic pedal. Only G↔Ab moves in the chord, which is the same semitone
    the melody sighs on: hypnotic and melancholic.
  - The climax is a "Russian-romance" one. A chromatic lift F#–G–A goes to Bb5, a b13 over V7/V at 7.89 s (57 %), which
    falls a semitone to A5. It is approached by step, as the brief asks.
- **Hook (7.5).** It is memorable but plain. The cell is gentle and a little generic next to b1-1's.
- **Originality (8).** It has the highest contour similarity to the original (0.47 per bar, against a null p99 of 0.66),
  and its beat-2 pitches alternate G/Ab for 4 bars (ALT warning). It evokes the original's shape most, with different
  pitches and harmony, which is exactly a sound-alike. I see no risk of it being heard as the same tune.
- **Harmony and voice leading (6).** These are real, fixable flaws:
  1. **Parallel octaves, outer voices, on downbeats:** bar 5 F5 over F2 → bar 6 Ab5 over Ab2. Fix: VI6 with a C bass in
     bar 6, or the melody on C6/Eb5.
  2. **G5 against Ab4** in the pa chord on beat 3 of bars 2 and 4, the hook bars, on the bright accented beat. The melody
    resolves Ab→G but the chord keeps Ab. Fix: make beat 3 of bars 2 and 4 the i chord (C–Eb–G).
  3. F#5 on beat 3 of bar 7 doubles the F#2 bass (the leading tone of V/V), and both go to G in bar 8. Fix: let the
     melody go F#5→D5, or move the bass.
  4. The hibrit render reads G major (C-minor r 0.54), because bars 6-9 tonicise G.

With fixes 1-3 this is an 8.

### b2-2 "Musette des ombres": 7.5 (rank 3, the distinctive alternative)

`(Eb G) | F. E Ab | G. F# Eb | F. E Ab | G [F# G Ab] Bb | Ab. G F | Bb. A G | Ab [G Ab Bb] B | C6. B [Ab G F] | Ab. G B-(C6 | C6~~`
over a strict **i↔iv pendulum for 8 bars**, then `V7 | iv6–V7 | i | i–iv`, with a second reed in parallel thirds in bars 5-9.

- **Hook (8).** The limping musette lilt (dotted quarter, then an eighth chromatic lower neighbour, then a leap) is a
  genuinely good cell you can hum.
  - It is stated twice, then sequenced up by step (Ab. G F | Bb. A G) into a rising triplet run and the cry: C6 as a
    4-3 over V7 at 9.08 s (66 %, slightly late), with a triplet fall after it.
- **Measurements.** The rocking numbers are the closest of all to the original's (lag2 0.40 / lag1 -0.30), and the
  tonal centre is the strongest C minor (0.79).
- **Craft (7.5).** The voice leading is clean and idiomatic. The only sour spot is B5 over iv for a full beat (bar 7,
  beat 3). Fix: vii°7 or V7 on that beat. The thirds are natural accordion writing (9.5 for playability).
- **Emotion (6.5).** This is why it is not higher.
  - The plagal pendulum has no tritone. It is melancholic, Parisian and "from the next room", but not eerie.
  - The dotted rhythm sustains across beat 2 in 7 of 9 bars, so the melody no longer strikes the bright "a" on 2. The
    pa chords still do. Its measured beat contrast (0.7 dB) is the second lowest in b2's engine.
  - The iv chord under the held tonic gives a soft plagal loop rather than the original's unanswered dominant.
- **Originality by ear (9).** It is the most distinct of the strong pieces: it shares neither the pendulum chord nor the
  cells nor the arch.

It is the right "different but genuinely strong" option to put next to the two b1 pieces.

### b2-1 "Kurmalı Kutu": 7.0 (rank 4, runner-up)

`(C6 Ab) | B [C B Ab] B | C6– G | Ab [B Ab G] F | G [Ab G F] G | Ab B D6 | C6– [B C D] | Eb6 D6– | C6 [Bb Ab G] F | G Ab B-(C6 | C6~~`
over **i↔vii°7 on a C pedal for bars 0-7**, then `iv | i6/4–V7 | i | i–vii°7`.

- **Hook (8).** The music-box turn ("ti, do-ti-le, ti | do – sol") is distinctive and sequenced a third lower in bars 3-4.
- **Arc (8).** A diminished arpeggio goes up to Eb6 at 57 %, a b9 that sighs a semitone to D6 and is approached by step.
  The cadence rises G–Ab–B–C (hicaz).
- **Emotion (7.5).** It is the most hypnotic pendulum of the eight, and every beat is articulated (the best beat accent
  in b2's engine).
- **Against it.**
  - **Harmonic cousin (originality by ear 5.5).** Bars 0-7 have the original's exact chord per bar (i, vii°, i, vii°, …),
    the cry sits over vii°7 in bar 7 as in the original, and a vii° chord sounds under the held tonic as in the original.
    The harness measures an 8-bar same-chord run. Only the bass (C pedal against C–D) and the tune differ. The tune is
    clearly new, but the backing alone would sound like "our song's backing".
  - **Register.** It sits at F5–Eb6, a 4th above the original's humming C5–Ab5, which is more tinkly and less fused with
    the C4–C5 chords.
  - **Pervasive hicaz colour.** The Ab–B augmented second comes back every second bar.
  - **The very first bright pa is a clash:** Ab5 over the Cm chord (against G4) at 0.39 s.
  - The counter doubles the melody in octaves at bar 5→6 (D6/D5 → C6/C5).

If the owner wants the closest feel, this is the alternative. Change the pendulum chord on two of the four vii° bars, or
use a walking bass, to lose the cousin status.

### b2-3 "Çingene Dansı": 6.5

`(Eb F#) | Ab [G F# G] Ab | G Eb C | Eb [F# G F#] Ab | G Eb C | C [Eb F# Ab] F# | G Eb [F# G Ab] | B Ab G | Ab [G F Eb] D | Eb F D-(C | C~~`
over i↔German 6th on a C pedal.

- **For it.** A strong, characterful cell and an elegant pendulum, in which the tonic's G splits into F# and Ab.
- **Against it.**
  - The Hungarian-minor colour is the original's single cadence F# turned into the whole identity. It reads as a gypsy
    dance or klezmer turn (clever but foreign).
  - The cry B5 is unsupported by the chord and leaves by an augmented second, not a semitone.
  - The counter doubles the melody's Ab→G resolution in octaves twice (bars 1→2 and in bar 7): a doubled tendency tone.
  - The anticipated C5 meets a held B4 in the counter (a minor 2nd) in bar 9.
  - The plain "G Eb C" arpeggio bars (2 and 4) are weak filler.

### b1-3 "Atlıkarınca": 6.0

`(Eb F) | [G F# G] Eb G | [F E F] D F | [G F# G] Eb G | [F E F] D B | [C Eb F][G F Eb] D | Eb G [C Db F] | Ab [G F G] F | [G F# G] Eb C | Eb F# D-(C | C~~`
over i↔V7 for bars 1-5.

- **For it.** The "shiver-a-a" twirl is very hummable and very waltz-like (rhythm 8.5).
- **Against it.** By ear it is the closest to the original's skeleton (4.5). It has, in modified form, every element of
  the "overall arch to avoid" in muzik.md §4.3:
  - a 4-bar plateau whose beat-2 pitch alternates Eb/D over a strict i↔V7 rocking (its composer calls it "the most
    literal twin");
  - the b6 Ab5 as the cry in bar 7 at 57 %, falling a semitone to G;
  - a stepwise fall;
  - the original's cadence gesture: F# on beat 2 of bar 9 over V7/V, a falling third, and C a triplet early at beat 3⅔.
- **Weak climax.** Ab5 is one semitone above G5, the piece's most frequent note (12 of 48), and it is consonant (the 5th
  of N6).
- **Key.** It reads as G minor/major in both engines.

### b2-4 "Kürdi Ninni": 6.0

`(Eb F) | G– [Ab G Eb] | F– [G F Db] | Eb– [F Eb C] | Db F Ab | G– [Eb F G] | F [Ab F Db] Eb | A Ab [G F Eb] | D [Eb F Eb] D | Db– B-(C | C~~`
over i↔bII (Db major, root position).

- **For it.** A good falling-sequence lullaby cell, and a textbook Db–B–C Neapolitan cadence.
- **Against it.**
  - The Phrygian pendulum plus the Dorian A make the colour foreign.
  - Root-position i↔bII close triads plane in parallel fifths every bar. There are also outer-voice fifths at bar 4→5
    (Ab5 over Db3 → G5 over C3) and the melody doubles the Db bass on bar 4's downbeat.
  - The cry is reached by a **tritone leap** (Eb5→A5) onto a *consonant* A natural over F7. The IV7→iv slide that follows
    is a pop gesture, not a dissonance resolving by a semitone.
  - The half notes on beats 1-2 (bars 1-3 and 5) remove the melody's "a" on beat 2.

### b1-2 "Çan Kulesi": 5.5

`(G G) | G Eb G | G D G | G C Eb | [B C D] G F | G Eb C | [C D Eb][F Eb F] G | Ab G F | [Eb D Eb] G G | F D B-(C | C~~`
over the Andalusian descent `i | VII | VImaj7 | V7 | i | iv6 | V7b9 | i | iv6(+6)–V7`.

- **For it.** Tidy craft: parallel tenths between the falling inner line and the bass, and hidden 5ths/8ves only with
  the soprano moving by step.
- **Against it.**
  - The hook is static: G sounds on 7 of the first 11 beats, and the "u a a" is turned into high–low–high. It is weak as
    a tune.
  - There is no pendulum at all (lag2 -0.02, the rejected attempts' failure mode).
  - The cry is the original's note, function and bar (Ab5 as b9 over V7 in bar 7, falling to G). The brief allows this,
    but it is a cousin moment.
  - The tonal centre reads as G in both engines.

## 5. Top 3 and what to fix before the next render

1. **b1-1**, `/tmp/claude-0/-home-user-wojak/e1bf52df-8e16-5819-ad96-6f6873ef480c/scratchpad/muzik2/besteler/b1/b1-1.json`,
   **8.5**. Render it as it stands through the hibrit engine. Two changes are optional: soften the G5 neighbour over iv6
   (bar 6, beat 2) to F5 or Ab5, and if more rocking is wanted, keep the i↔V6/5 pendulum one bar longer.
2. **b1-4**, `/tmp/claude-0/-home-user-wojak/e1bf52df-8e16-5819-ad96-6f6873ef480c/scratchpad/muzik2/besteler/b1/b1-4.json`,
   **7.5**. Make three fixes first:
   - the bar 5→6 downbeat octaves with the bass;
   - the beat-3 chord of bars 2 and 4 → i;
   - the F# doubling at bar 7→8.
3. **b2-2**, `/tmp/claude-0/-home-user-wojak/e1bf52df-8e16-5819-ad96-6f6873ef480c/scratchpad/muzik2/besteler/b2/b2-2.json`,
   **7.5**. Change bar 7 beat 3 to vii°7 or V7 under B5. Optionally re-strike the melody on beat 2 in one or two hook bars
   so the "a" on 2 is heard. It has not been through the hibrit engine yet, so render it there before comparing timbre.

The runner-up is b2-1 (7.0). Choose it over b2-2 only if the owner prefers the closest feel to distinctness, and only
after breaking its bar-for-bar i/vii° match with the original.

## 6. Uncertainty

- Nobody listened. Hook strength, "eerie" and "owner appeal" are my judgement from the score and the piano roll. The
  harness checks originality, not quality.
- The b1 and b2 previews use different engines, so beat contrast and TIMBRE_SCORE are not a fair melody comparison. Only
  b1 has hibrit renders.
- The key readings (G for b1-2, b1-3 and b1-4 in hibrit) may partly depend on the engine.
- The parallel checks assume the bass sounds from its beat-1 attack through the bar. I dropped one flag that depended on
  a chord change with no new bass attack (b1-3, bar 6 beat 3). Downbeat-to-downbeat parallels (b1-4, bars 5→6) are certain.
