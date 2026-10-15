// UZUN VİDEO İŞ AKIŞI ŞABLONU (YouTube, 8-10 dk, 1920x1080). Kullanım ve parametreler: docs/is_akislari/README.md
// "Talidomit ve Türkiye" uzun videosu (14 tur, sahibin "baya iyi olmuş beğendim" onayı) bu akışın parçalarıyla yapıldı:
// araştırma -> senaryo v1 -> iki eleştirmen -> senaryo v2 -> varlık + karakter -> üretim -> dört hakem -> düzeltme döngüsü.
// İstemler İngilizce (alt ajanlar daha tutarlı uyguluyor); anlatım ve paket metinleri Türkçe yazılır.
//
// args: {
//   id:      'konu-id'                 (uzun/<id>/video.yaml; aynı konunun kısası episodes/<id>)
//   konu:    'TOPIC: ...'              (konu, Türkiye bağlantısı, kısa sürümde doğrulanmış olgular nerede)
//   sp:      '<scratchpad>/uzun/<id>'  (araştırma, senaryo, hakem çıktıları; repoya girmez)
//   kisa:    '<scratchpad>/uretim/<id>' (isteğe bağlı: kısa sürümün araştırma klasörü, olgular.md)
//   basla:   'arastirma'               ('arastirma' | 'uretim' | 'hakem': senaryo hazırsa ya da yalnız hakem/düzeltme turu)
//   max_tur: 6                         (hakem + düzeltme turu üst sınırı; talidomit 14 tur sürdü, motor oturduğu için 4-6 hedef)
//   ozel:    ''                        (sahibin bu video için notları; hakemlerden önce gelir)
// }

export const meta = {
  name: 'uzun-video',
  description: 'Long YouTube video: research, script + two critics, assets/characters, production, four-lens judging, fix loop',
  phases: [
    { title: 'Research', detail: 'deep research with sources, image candidates, narrative beats' },
    { title: 'Script', detail: 'script v1, retention + Turkish/facts critics, script v2' },
    { title: 'Prepare', detail: 'assets, ready-made characters + face variants, engine needs' },
    { title: 'Produce', detail: 'video.yaml, narration, render, thumbnails, package' },
    { title: 'Judge', detail: 'retention, character+animation, Turkish/facts, technical' },
    { title: 'Fix', detail: 'apply fixes, re-render' },
  ],
}

const A = args || {}
if (!A.id || !A.konu || !A.sp) throw new Error('args.id, args.konu ve args.sp gerekli (docs/is_akislari/README.md)')
const ID = A.id
const U = A.sp
const KISA = A.kisa ? `${A.kisa}/arastirma/olgular.md (the short's verified facts; contested points keep their safe phrasing)` : '(no short research)'
const MAX = A.max_tur || 6
const BASLA = A.basla || 'arastirma'

const BASE = `Context: repo /home/user/wojak makes videos for the Turkish account @tarihselwojak (wojak-character history/mystery
stories). The owner approved our short reels and our first LONG YouTube video (uzun/talidomit-turkiye: "baya iyi olmuş beğendim").
Every new long video must reach at least that quality: "benchmarktasın gibi düşün, elinden gelen en iyi videoyu yap" — genuinely
engaging, animated, never voice over a static picture. READ FIRST: CLAUDE.md, docs/ADIM_ADIM.md (the step-by-step runbook),
docs/UZUN_FORMAT.md (decisions, incl. face-size and watermark rules), docs/UZUN_MOTOR.md (the engine: wojak/uzun, spec
uzun/<id>/video.yaml, CLI python -m wojak uzun kontrol|seslendir|onizle|kare|render|kucukresim|paket|teslim), docs/OGRENILENLER.md
(owner table + §7.1: lessons from 14 judging rounds — do not repeat those mistakes), uzun/talidomit-turkiye/video.yaml (the approved
example; its comments explain every fix) and uzun/demo/video.yaml (every scene type).
Research: ${U}/arastirma/arastirma_uzun.md and ${KISA}. The same topic's short: episodes/${ID}, teslim/${ID}/ (if it exists).
Secrets: TTS keys only via wojak.config.load_secrets(); NEVER print/log/commit them. Public repo: never commit assets/fonts/ozel,
assets/music/ozel, referans/, copyrighted images (keep them under uzun/<id>/img/telifli/, git-ignored), or videos. Privacy: no
e-mail or personal identifier in HTTP headers/requests (generic browser User-Agent); never bypass the proxy; Wikimedia rate limits
(HTTP 429): pace requests >= 10 s apart. Never name private individuals' families; minors' surnames/parents/school never appear.
Do not git commit/push.

${A.konu}`

const OWNER = `OWNER'S STANDING RULES (they OUTRANK the judges; see docs/OGRENILENLER.md top table):
1. Quality: push to the limit; never deliver a known flaw silently (list it in the report and the package).
2. CHARACTERS: READY-MADE clothed wojaks only (single drawings from wojakland / wojaksparadise / the 10,378-PNG library:
   tools/wojak_site.py, tools/wojak_lib.py); never paint or paste clothes onto heads. Face variants are clean face-only edits
   (tools/kit_varyant.py or careful PIL on the face; same line weight, classic eyes kept, emotion via lids/brows/mouth, readable at
   phone size). Check every character at 1:1 and at phone size.
3. FACE SIZE: effective on-screen character height = boy x camera zoom x yakin must stay <= 0.80 of frame height (sweet spot
   0.55-0.75); a deliberate dramatic close-up may reach 0.88 at most 1-2 times per video, with the whole head and chin inside the
   frame. The owner noticed oversized, bottom-cropped faces in the first video (0.94-0.96 in four scenes).
4. END: no "next video" boxes; the subscribe/like/comment call is engaging and tied to the story's open question (kapanis scene).
5. Watermark: follow docs/UZUN_FORMAT.md §2 (decision recorded there; from the ElevenLabs re-voice on, no burned-in watermark on long
   videos: filigran: false, YouTube Studio branding watermark instead).
6. Voice: provider and voices per docs/UZUN_FORMAT.md §1 (Cartesia was disliked; ElevenLabs replaces it once its adapter exists).
   Synthesize only new or changed lines; the cache keeps the rest.
7. Packaging: YouTube title must not read like AI slop (no hype adjectives, no emoji, no "ŞOK"; curiosity gap + concrete detail);
   YouTube description 2-3 hashtags; Instagram captions never use hashtags.
${A.ozel ? `\nOWNER NOTES FOR THIS VIDEO:\n${A.ozel}` : ''}`

const RESEARCH = `${BASE}

You are a meticulous researcher for a ~9-minute Turkish YouTube documentary on this topic. Start from the short's verified facts if
they exist and keep their caution. Extend with >= 2 independent sources per fact (academic papers, books, official archives, reputable
press; record exact URLs): full chronology, every person (bio, positions, sources), numbers with ranges, what is contested (and safe
phrasing), the Turkey angle (everything verifiable; what is only "anlatılana göre"), the aftermath / today (the twist), any debunks.
Also list IMAGE candidates with licence (prefer public domain / CC; mark copyrighted ones): portraits, documents, newspaper pages,
period street/office/lab photos, places, objects. Download good candidates into ${U}/arastirma/gorseller/ (not the repo) with a
licence table and a contact sheet; LOOK at them.
Finally propose the narrative beats: a cold-open hook (first 5 s opens a question; a wojak on screen within 15 s), 4-6 chapters with
titles, the open loops between chapters, the climax (the answer to the title's question, built as a character scene), the twist,
the closing question (it becomes the kapanis A/B/C choice and the pinned comment).
Write ${U}/arastirma/arastirma_uzun.md and return it (fact table with confidence and URLs, contested points + safe phrasing, image
table, narrative beats).`

const SCRIPT = `${BASE}

You are the head writer of a top Turkish history/mystery YouTube channel. Write the narration script (target 1,200-1,350 spoken words
~ 9-10 min) using ONLY facts from the research (contested points keep their safe phrasing). Watch/read the short if it exists — the
long video is its big brother (the same wojak characters reappear).
Structure per docs/UZUN_FORMAT.md §3: cold open hook (0:00-0:40, no intro music/logo before the hook), brand sting, chapters with
titles, open loops at chapter ends, the Turkey chapter, the twist, closing question + pointer to the short. Spoken, natural Turkish
(short sentences, rhythm, rhetorical questions, no translationese, no academic tone), respectful to victims. Mark second-voice quotes
([AYLIN] ...). Mark pronunciation risks (foreign names, double consonants like "cüzzam", rare words: prefer a synonym that TTS reads
well and keep the hard word on screen). For EVERY sentence or pair give the visual beat (scene type: wojak scene with which characters/
background/face change, foto, manset+highlight, harita, sayac, metin, zaman_cizelgesi, pano, bolunmus, bolum karti, isim, kelime,
damga, konuk reacting in a corner) so that something new appears at least every 4-6 s and characters are on screen >= 50% of the time.
Write ${U}/senaryo_v1.md (table: chapter, line, voice, visual beat, estimated seconds; total word count and runtime) and return it.`

const CRIT_RETENTION = `${BASE}

You are a ruthless YouTube retention editor (top faceless documentary channels). Read ${U}/senaryo_v1.md and the research. Judge: the
first 30 s (would a Turkish viewer who clicked the thumbnail stay?), open loops, pacing per chapter, dead spots, visual change density
(>= every 4-6 s), character share (>= 50%), repeated visuals (max 2 uses per image), the climax as a character scene, the twist and
ending, the title/thumbnail concept (propose 3 non-slop title options and 3 thumbnail concepts: max 3 elements, 2-4 huge words,
readable at 168x94). Score 1-10, concrete rewrites (exact Turkish lines) ordered by impact, MUST/SHOULD. Write ${U}/elestiri_izlenme.md
and return it.`

const CRIT_LANG = `${BASE}

You are a native Turkish narration editor and a fact-checker. Read ${U}/senaryo_v1.md and the research. Judge every line: natural
spoken Turkish for a narrator voice (rhythm, sentence length, no translationese, correct suffixes/apostrophes for foreign names,
TTS-friendly punctuation, numbers written for speech, pauses where meaning needs them), facts vs sources (open the URLs; flag anything
unsupported or overstated, especially the Turkey part), respect toward victims, legal/ethical lines (docs/GUNDEM.md §7), no invented
quotes for real people. Score 1-10, exact line rewrites ordered by impact, MUST/SHOULD. Write ${U}/elestiri_dil_dogruluk.md and return it.`

const REVISE = `${BASE}

You are the head writer again. Revise ${U}/senaryo_v1.md using ${U}/elestiri_izlenme.md and ${U}/elestiri_dil_dogruluk.md (apply all
MUST, and SHOULD unless it conflicts with facts or respect; conflicts: facts > respect > retention). Keep 1,200-1,350 words. Output
${U}/senaryo_v2.md in the same table format plus: 3 title options, 3 thumbnail concepts, chapter list with target timestamps, YouTube
description draft (with sources), pinned comment (the closing A/B/C question), tags, the kapanis question and choices, and the asset
list (characters with needed face variants, backgrounds, archival images with licence, maps, counters, own drawings). Return it.`

const CHARS = `${BASE}

${OWNER}

You are the CHARACTER and ASSET lead for uzun/${ID}. Read ${U}/senaryo_v2.md (asset list). Build everything in uzun/${ID}/img/ and
uzun/${ID}/chars/ (copyrighted images in uzun/${ID}/img/telifli/), with a licence table uzun/${ID}/VARLIKLAR.md (file, what, source
URL, author, licence, credit line) and contact sheets in ${U}/varlik/.
Characters: reuse the approved ones first (uzun/talidomit-turkiye/chars/*_v2_*, assets/kit/*, episodes/*/chars) when the role fits;
otherwise find READY-MADE clothed wojaks that fit role, era and costume (search widely and LOOK: tools/wojak_site.py, tools/wojak_lib.py;
by role + costume + era). Make only the face variants the script needs (calm, worried/sweating, shocked, sad/teary, determined, serious,
thoughtful, suspicious; smug only for a villain), per the face-variant rules in docs/OGRENILENLER.md §7.1 (rounds 9-13). Register
every new PNG's gaze after LOOKING (python -m wojak yon <png> --yon sag|sol|on). If a source PNG has opaque pixels in row 0, extend the
canvas upward (cut head). Backgrounds: real colour photos (CC/PD, >= 1920 px wide preferred) per location, or our own flat drawings
for generic rooms; each image used in at most 2 shots. Build review sheets (all characters with variants at 1:1 and at 360 px) and
LOOK at them critically against the approved characters. Return the licence table, the asset mapping and your honest assessment.`

const ENGINE = `${BASE}

You are the engine owner of wojak/uzun. Read ${U}/senaryo_v2.md and list every visual the script needs that the engine cannot do yet
(compare with docs/UZUN_MOTOR.md §3 scene types and events). Implement only those that clearly raise quality, cleanly and with tests
(python -m pytest tests -q must pass), keeping uzun/demo and uzun/talidomit-turkiye rendering unchanged (re-render uzun/demo at preview
size and LOOK). Update docs/UZUN_MOTOR.md and uzun/_sablon/video.yaml. Do not edit uzun/${ID}/video.yaml. If nothing is missing, say
so and change nothing. Return what you added and how to use it.`

const PRODUCE = `${BASE}

${OWNER}

You are the producer/editor. Inputs: ${U}/senaryo_v2.md, uzun/${ID}/VARLIKLAR.md (+ img/, chars/), the engine (docs/UZUN_MOTOR.md).
Start from uzun/_sablon (cp -r uzun/_sablon uzun/${ID} if missing) and build uzun/${ID}/video.yaml implementing the script faithfully:
every line, voice, visual beat, events, sfx; telaffuz overrides for every risky name; the cold open without logo/music intro; the
channel sting after the hook; bölüm cards (kart_bindirme); maps, counters, timeline, documents with highlights; isim (lower third) for
every real person on first appearance; konuk characters reacting on info scenes (character share >= 50%); the kapanis CTA with the
script's question. Follow the face-size rule (effective height <= 0.80; check with the camera zoom/yakin, not the yaml boy alone).
Then: python -m wojak uzun kontrol (fix EVERY warning: motion, chapters, subtitles, overlaps, jump cuts, out-of-frame, face cover),
seslendir --qa (fix mispronounced names via telaffuz/synonyms and regenerate only those lines; generate 2-4 takes of a hard line and
pick by two Whisper decodes), onizle, LOOK at frames every 2 s and at every transition (python -m wojak uzun kare, or ffmpeg) and fix
anything ugly; run python tools/uzun_animasyon_denetimi.py on the preview and look at each flagged moment; then render (1080p),
kucukresim (3 variants: max 3 elements, huge 2-4 word text, expressive wojak, readable at 168x94), paket and teslim. Measure: duration
8:30-10:15, -14 LUFS / <= -1 dBTP, A/V sync, click scan at every narration edge, chapter timestamps valid (first 0:00, >= 3, each >= 10 s,
rounded UP), SRT (<= 42 chars per line). Build ${U}/final_sheet.jpg (1 frame / 3 s) and ${U}/karakter_final.jpg (every character as it
appears, 1:1 crops, with its effective height) and LOOK at both like the owner would. Write the full report to ${U}/uretici_raporu.md
and return it (runtime, chapter list, voices/speeds, deviations from the script and why, known weaknesses, listening list).`

const J_RET = `${BASE}

${OWNER}

You are an independent, harsh YouTube RETENTION and VISUAL judge (you edit for top faceless documentary channels). Judge
teslim/${ID}-uzun/ (video, thumbnails, paylasim.md); the producer's report: ${U}/uretici_raporu.md. Work in ${U}/hakem/<ROUND>/izlenme/
(do not edit project files). Method: extract a frame every 1 s for the first 60 s and every 2 s after; build contact sheets and look at
them in order like a viewer; transcribe the narration with faster-whisper (decode audio with ffmpeg to 16 kHz float yourself) to follow
what is said when; detect static stretches (frame difference) and dead air. Judge: the first 30 s (hook; would a viewer who clicked the
thumbnail stay?), pacing per chapter, visual variety and motion (anything static > 4-6 s, repeated visuals, filler), character share,
oversized or cropped faces, animation quality (smooth easing, no jitter, readable text, inward gaze, face variants on the right beats),
thumbnail and title click-appeal (at 168x94 and 360x202; not AI slop), audio balance (music vs voice, sfx not annoying), the climax and
the kapanis CTA. Score 1-10 (10 = top documentary channel quality; 8 = a viewer would happily watch to the end and nothing looks
amateur; 6 = watchable but clearly low-budget). Concrete fixes ordered by impact, MUST/SHOULD, with timestamps and exact changes in
video.yaml terms. Return overall, scores, fixes, blockers.`

const J_ANIM = `${BASE}

${OWNER}

You are an independent, harsh CHARACTER & ANIMATION judge (you have animated for top YouTube animated-documentary channels). Judge
teslim/${ID}-uzun/ (video + thumbnails). Work in ${U}/hakem/<ROUND>/animasyon/ (do not edit project files). Method: decode the video at
30 fps; run python tools/uzun_animasyon_denetimi.py and look at every flagged moment at full resolution; check every character
appearance at 1:1 (crop sheets) and at phone size, and measure its effective on-screen height (flag > 0.80 of frame height or a cropped
chin/head); scrub every transition and every animated element frame by frame around its start/end (pops, jitter, z-order, clipping,
overlaps, ghosting from motion blur, double characters in crossfades, jump cuts of the same character, flashes from dark to bright);
check face variants (clean lines, consistent weight, readable emotion, right beat); check clothing (ready-made only, no pasted
clothes); check the kapanis CTA (engaging, story-tied, no video boxes). Score 1-10 (10 = top animated documentary channel; 8 = the owner
would find no error and nothing looks home-made; 6 = clearly amateur in places). List every defect with timestamp and exact fix
(MUST/SHOULD). Return overall, scores, fixes, blockers.`

const J_LANG = `${BASE}

You are an independent, harsh judge: native Turkish narration editor + fact-checker. Judge teslim/${ID}-uzun/ (video, paylasim.md,
.srt). Work in ${U}/hakem/<ROUND>/dil/ (do not edit project files). Method: transcribe the final audio with faster-whisper medium
(decode with ffmpeg to 16 kHz float yourself), align with uzun/${ID}/video.yaml lines; listen-check by metrics: mispronounced names
(compare transcription), unnatural pauses (gaps > 1.2 s inside a sentence), rushed lines (> 7.0 syllables/s), level jumps between
voices. Judge every line: natural spoken Turkish (no translationese), rhythm, correct suffixes for foreign names, tone (documentary,
respectful, no sensationalism), and FACTS: open the sources and verify at least 10 key claims (dates, numbers, names, positions, the
Turkey part phrased safely as in the research); check the title, description, chapters, pinned comment, tags and SRT text too. Score
1-10 (10 = flawless professional Turkish documentary narration and fully accurate; 8 = a Turkish viewer notices nothing off and no
factual error). Concrete fixes (exact new Turkish lines / telaffuz entries), MUST/SHOULD. Return overall, scores, fixes, blockers.`

const J_TECH = `${BASE}

You are an independent technical/package QA judge for YouTube upload. Judge teslim/${ID}-uzun/ and out/${ID}-uzun/. Work in
${U}/hakem/<ROUND>/teknik/ (do not edit project files). Check: container/codec (H.264 high, yuv420p, 1920x1080, 30 fps, AAC 48 kHz),
A/V start 0 and durations match, -14 LUFS +-1 and <= -1 dBTP, no clipping, no clicks (scan every point where the narration track
drops to or rises from silence: last 20 ms vs the 45 ms before), no digital-zero silences, no silent gaps > 2 s except intended,
chapter timestamps valid for YouTube (0:00 first, >= 3, >= 10 s each, ascending, within 1 s of actual chapter starts, rounded up), SRT
validity (UTF-8, timing, <= 42 chars, Turkish chars), description <= 5000 chars, title <= 100, tags <= 500 chars, credits cover every CC
image actually used (compare uzun/${ID}/VARLIKLAR.md with the rendered scenes), copyrighted images listed for the owner, no secrets or
private data in any file under teslim/ or uzun/, thumbnails 1280x720 < 2 MB, the last 20 s usable for YouTube end-screen elements, the
Short's package (teslim/${ID}/) still valid and pointing to the long video. Score 1-10 and list MUST/SHOULD fixes. Return overall,
scores, fixes, blockers.`

const FIX = `${BASE}

${OWNER}

You are the producer, fix round <ROUND>. Your previous report: ${U}/uretici_raporu.md. Four independent judges scored the current video:
<REPORTS>
Apply all blockers and MUST fixes, then SHOULD fixes unless they conflict with facts/respect (explain). Priority: facts > respect >
owner's rules > retention > polish. Keep what judges praised; never undo an earlier round's fix. Do not apply a judge's suggested number
blindly: check the frame (a suggested size/zoom often causes a new overlap). Engine fixes in wojak/uzun are allowed (keep tests
passing). Synthesize only new/changed lines. Re-run kontrol (clean), render, kucukresim, paket, teslim; verify every fixed item
objectively (30 fps strips of each fixed moment, click scan, loudness) and LOOK; rebuild ${U}/final_sheet.jpg and
${U}/karakter_final.jpg. Append the round's lessons (what failed, how it was found, the rule) to your report under "DERSLER" so the
lead can copy them into docs/OGRENILENLER.md §7.1. Overwrite ${U}/uretici_raporu.md and return the full report.`

const SCORE = { type: 'object', properties: { overall: { type: 'number' }, scores: { type: 'string' }, fixes: { type: 'string' }, blockers: { type: 'string' } }, required: ['overall', 'scores', 'fixes', 'blockers'] }
const fmt = (n, j) => `${n} ${j ? j.overall : '?'}/10:\n` + (j ? `${j.scores}\nBlockers: ${j.blockers || '-'}\nFixes:\n${j.fixes}` : '(judge failed)')
const noBlock = (b) => !b || !b.trim() || /^(yok|none|no\b|no blocker|-|—|engel yok)/i.test(b.trim())

let script = null
if (BASLA === 'arastirma') {
  phase('Research')
  await agent(RESEARCH, { label: 'arastirma', phase: 'Research' })
  phase('Script')
  await agent(SCRIPT, { label: 'senaryo_v1', phase: 'Script' })
  await parallel([
    () => agent(CRIT_RETENTION, { label: 'elestiri_izlenme', phase: 'Script' }),
    () => agent(CRIT_LANG, { label: 'elestiri_dil', phase: 'Script' }),
  ])
  script = await agent(REVISE, { label: 'senaryo_v2', phase: 'Script' })
}

let report = null
if (BASLA === 'arastirma' || BASLA === 'uretim') {
  phase('Prepare')
  await parallel([
    () => agent(CHARS, { label: 'karakter_varlik', phase: 'Prepare' }),
    () => agent(ENGINE, { label: 'motor', phase: 'Prepare' }),
  ])
  phase('Produce')
  report = await agent(PRODUCE, { label: `uret:${ID}`, phase: 'Produce' })
}

const judge = (round) => parallel([
  () => agent(J_RET.replaceAll('<ROUND>', String(round)), { label: `izlenme${round}`, phase: 'Judge', schema: SCORE }),
  () => agent(J_ANIM.replaceAll('<ROUND>', String(round)), { label: `animasyon${round}`, phase: 'Judge', schema: SCORE }),
  () => agent(J_LANG.replaceAll('<ROUND>', String(round)), { label: `dil${round}`, phase: 'Judge', schema: SCORE }),
  () => agent(J_TECH.replaceAll('<ROUND>', String(round)), { label: `teknik${round}`, phase: 'Judge', schema: SCORE }),
]).then(([r, a, l, t]) => ({ r, a, l, t }))
const ok = (j) => ['r', 'a', 'l', 't'].every(k => j[k] && j[k].overall >= 8 && noBlock(j[k].blockers))

const history = []
let cur = await judge(1)
const kayit = (round) => {
  history.push({ round, r: cur.r && cur.r.overall, a: cur.a && cur.a.overall, l: cur.l && cur.l.overall, t: cur.t && cur.t.overall })
  log(`round ${round}: retention ${cur.r && cur.r.overall}, animation ${cur.a && cur.a.overall}, language ${cur.l && cur.l.overall}, tech ${cur.t && cur.t.overall}`)
}
kayit(1)
for (let round = 2; round <= MAX && !ok(cur); round++) {
  const reports = [fmt('RETENTION/VISUAL', cur.r), fmt('CHARACTER/ANIMATION', cur.a), fmt('TURKISH/FACTS', cur.l), fmt('TECHNICAL', cur.t)].join('\n\n')
  report = await agent(FIX.replaceAll('<ROUND>', String(round)).replace('<REPORTS>', reports), { label: `duzelt${round}`, phase: 'Fix' })
  cur = await judge(round)
  kayit(round)
}
if (!ok(cur)) log('not all four judges >= 8 with no blockers; residual fixes returned')
return { id: ID, history, final: cur, report, script }
