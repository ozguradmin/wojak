export const meta = {
  name: 'imza-tasarim-tur',
  description: 'Signature waltz: one sound engine renders the chosen melodies (with further tuning), then sound and music critics score each candidate',
  phases: [
    { title: 'Design', detail: 'engine renders the top melodies, keeps tuning' },
    { title: 'Critique', detail: 'sound/technical + music/originality critics' },
  ],
}

const SP = '/tmp/claude-0/-home-user-wojak/e1bf52df-8e16-5819-ad96-6f6873ef480c/scratchpad/muzik2'
const A = args || {}
const WHO = A.who
const MELS = (A.melodies || []).map(m => `${m.id}: ${m.json}`).join('; ')
const PRE = `Read ${SP}/BAGLAM.md first (shared context, melody JSON format, HARD RULES). Also read ${SP}/olcum/kalibrasyon.md
(harness usage: python3 ${SP}/olcum/olcum.py <wav> [--notalar <json>] [--png <png>]) and ${SP}/olcum/teshis.md (why our rejected
attempts sounded worse). Note: composers write the 2-beat pickup as bar 0 (bar 0 beat 2 = 0.00 s; t = (3*bar + beat - 2) * 60 / tempo).`

const DESIGN = `${PRE}

TASK: SOUND DESIGN round for engine "${WHO}". The engine was built and tuned on a test melody: ${A.engine_py}
(its folder has log.md; its builder's report: ${A.engine_report}). The melody judge chose these melodies (see ${SP}/besteler/YARGI.md
for why): ${MELS}.
Copy the engine to ${SP}/tasarim/${WHO}/render.py (keep the original in motor/ untouched) and make it render these melodies as a
real, expressive performance: support everything in their JSON (bar-0 pickup convention, per-beat harmony with bass, explicit
accompaniment events, counter-line, expression hints, velocities), the "u a a" waltz accent (beat 1 darker/softer, beats 2-3
brighter: the original's beat contrast is about +4.5 dB, see teshis.md), legato phrasing, balance lead vs accompaniment, the
measured chain and match EQ. Render all melodies to ${SP}/tasarim/${WHO}/<melody id>.wav (44.1 kHz stereo, 13.75 s) and run the
harness on each (--notalar and --png). LOOK at every PNG next to the original's. Keep tuning while TIMBRE_SCORE and the
beat-contrast/true-peak/technical checks improve; log each iteration in ${SP}/tasarim/${WHO}/log.md. Never use original audio
(rule 1). Return per candidate: aday_id ("${WHO}-<melody id>"), melodi_json, wav, png, timbre_score, ozet; plus render_py,
lisanslar, yaklasim.`

const CRIT_SOUND = `${PRE}

TASK: CRITIC, lens = SOUND/TIMBRE/TECHNICAL, for the candidates of engine "${WHO}" in ${SP}/tasarim/${WHO}/ (render.py, log.md,
*.wav, harness outputs). Work in ${SP}/kritik/${WHO}/ses/. Re-run the harness on each candidate; render your own close-up
comparisons (held notes, a 2-bar zoom, the ending, the first second) against the original and LOOK. Compare also against the
rejected attempts (assets/music/imza_vals*.m4a) — a candidate not clearly better than those is a fail.
Judge: does it sound like the same KIND of recording (instrument realism, warmth, texture density, noise, room, movement, the
"u a a" beat accent), or like a synthetic imitation? Technical: clicks, clipping, aliasing, harshness peaks, true peak, length,
start/end, stereo/mono compatibility. Score each candidate 1-10 (10 = in sound quality and feel indistinguishable from the original's
kind of recording; 8 = a long-time follower would accept it as the channel's music with no sense of downgrade; 6 = clearly a
cheaper imitation; 4 = amateur). Give concrete, parameter-level fixes (MUST/SHOULD). Return per candidate: aday_id, puan, guclu,
zayif, duzeltmeler.`

const CRIT_MUSIC = `${PRE}

TASK: CRITIC, lens = MUSIC PERFORMANCE + ORIGINALITY, for the candidates of engine "${WHO}" in ${SP}/tasarim/${WHO}/.
Work in ${SP}/kritik/${WHO}/muzik/. For each candidate: transcribe the RENDERED audio (pitch tracking + CQT) and compare with its
melody JSON (wrong notes, timing drift, inaudible lead, accompaniment masking the melody, chord/melody clashes, mechanical
quantised feel vs. expressive phrasing, balance, legato, the waltz lilt, the final hold and fade). Re-check originality against
${SP}/analiz/muzik.json with the harness (--notalar) and with your own judgement (would a follower hear the same tune?).
Score each candidate 1-10 (10 = as musical and catchy as the original; 8 = a follower would happily accept it as the channel's
waltz; 6 = correct but lifeless; 4 = wrong/awkward). Concrete fixes (MUST/SHOULD). Return per candidate: aday_id, puan, guclu,
zayif, duzeltmeler.`

const SCORE_LIST = {
  type: 'object',
  properties: {
    adaylar: {
      type: 'array',
      items: {
        type: 'object',
        properties: {
          aday_id: { type: 'string' }, puan: { type: 'number' }, guclu: { type: 'string' },
          zayif: { type: 'string' }, duzeltmeler: { type: 'string' },
        },
        required: ['aday_id', 'puan', 'zayif', 'duzeltmeler'],
      },
    },
    genel: { type: 'string' },
  },
  required: ['adaylar'],
}
const DESIGN_OUT = {
  type: 'object',
  properties: {
    adaylar: {
      type: 'array',
      items: {
        type: 'object',
        properties: {
          aday_id: { type: 'string' }, melodi_json: { type: 'string' }, wav: { type: 'string' }, png: { type: 'string' },
          timbre_score: { type: 'number' }, ozet: { type: 'string' },
        },
        required: ['aday_id', 'melodi_json', 'wav'],
      },
    },
    render_py: { type: 'string' }, lisanslar: { type: 'string' }, yaklasim: { type: 'string' },
  },
  required: ['adaylar', 'render_py'],
}

phase('Design')
const d = await agent(DESIGN, { label: `tasarim-${WHO}`, phase: 'Design', schema: DESIGN_OUT })
if (!d) return { who: WHO, error: 'design failed' }
phase('Critique')
const [s, m] = await parallel([
  () => agent(CRIT_SOUND, { label: `kritik-ses-${WHO}`, phase: 'Critique', schema: SCORE_LIST }),
  () => agent(CRIT_MUSIC, { label: `kritik-muzik-${WHO}`, phase: 'Critique', schema: SCORE_LIST }),
])
return { who: WHO, design: d, ses: s, muzik: m }
