// KISA REEL İŞ AKIŞI ŞABLONU (14 sn, 1080x1920). Kullanım ve parametreler: docs/is_akislari/README.md
// Dört onaylı kısa (van-depremi, çanakkale, kız kulesi, talidomit) bu akışla 8/8'e çıktı. İstemler bilerek
// İngilizce: alt ajanlar İngilizce talimatı daha tutarlı uyguluyor; üretilen Türkçe metinler (replik, başlık,
// hikâye) Türkçe yazılır. Konuya özel her şey args.konu'dadır; burada konu bilgisi yok.
//
// args: {
//   id:     'bolum-id'                      (episodes/<id>, python -m wojak new <id> ile açılır)
//   konu:   'TOPIC: ...'                    (iddia, kişiler, yıl, yer, neden şimdi; viral kaynak varsa ekran görüntüsü yolu)
//   refs:   'C2kkZ8BsngB, C4V3eMFM6lF, ...' (referans/ içindeki en yakın orijinaller; 3-5 tane)
//   sp:     '<scratchpad>/uretim/<id>'      (araştırma, hakem çıktıları; repoya girmez)
//   max_tur: 4                              (hakem turu üst sınırı)
//   ozel:   ''                              (isteğe bağlı: sahibin bu bölüm için notları, tasarım önerisi)
// }

export const meta = {
  name: 'kisa-reel',
  description: 'Short reel: fact-check + asset hunt, produce, two-lens judging (visual + Turkish follower), fix until both >= 8',
  phases: [
    { title: 'Research', detail: 'fact-check the story; hunt evidence images, background and characters' },
    { title: 'Produce', detail: 'one producer builds the episode' },
    { title: 'Judge', detail: 'visual-fidelity judge + Turkish-follower/script/facts judge' },
    { title: 'Fix', detail: 'apply fixes, re-render, teslim' },
  ],
}

const A = args || {}
if (!A.id || !A.konu || !A.sp) throw new Error('args.id, args.konu ve args.sp gerekli (docs/is_akislari/README.md)')
const ID = A.id
const D = A.sp
const REFS = A.refs || 'C2kkZ8BsngB, C4V3eMFM6lF, C2FriLUM2DR, C12OZjesdVM, C3DeLN1sU7O'
const MAX = A.max_tur || 4

const CONTEXT = `Context: we produce 14 s reels for the Instagram account @tarihselwojak (~465K followers; YouTube Shorts copy).
The owner rated our first attempts 3/10; after we measured the golden-era originals frame by frame (docs/STIL.md is THE spec) and
remade them, the owner approved four house examples: teslim/van-depremi-azra-bebek, teslim/canakkale-kayip-tabur,
teslim/kiz-kulesi-efsanesi, teslim/talidomit-turkiye (episodes/<id>/episode.yaml shows how each is built). Every new reel must be at
least that good. Repo: /home/user/wojak. Read CLAUDE.md, docs/STIL.md fully, docs/OGRENILENLER.md (owner table, §3 failure modes,
§4 checklist), docs/KONSEPT.md §2-5, docs/INSTAGRAM_ANALIZ.md §5-6, docs/GUNDEM.md §5 and §7, docs/URETIM_REHBERI.md.
Originals (720x1280 mp4): /home/user/wojak/referans/<code>.mp4; topics in data/instagram_reels.csv.
Renderer facts: video/audio start at 0.000 and cuts sit on the 0.5 s grid; text is placed 55 px above the speaker's head (visible ink).
episode.yaml extra fields: cover_scene (1-based scene for kapak.jpg) + cover_at (0-1); telif_notu (owner-facing licence note for
img/telifli/ images); ek_maddeler (extra owner checklist lines); uzun_video (YouTube link of the long version, when it exists).
Copyrighted evidence (news agency/newspaper/TV/YouTube/artwork) goes in episodes/<id>/img/telifli/ (git-ignored; the owner decides the
licence); prefer free images when equally strong.
Owner's standing rules: ready-made clothed wojaks only (never paint clothes onto heads); clean face variants; Instagram caption has
no hashtags (pack.py handles it); titles must not read like AI slop (no hype adjectives, no emoji, no "ŞOK"; curiosity gap + one
concrete detail).
Privacy/network: never put any e-mail address or personal identifier in HTTP headers or requests (generic browser User-Agent);
never bypass the network proxy; Wikimedia/Commons rate-limits (HTTP 429): pace requests >= 10 s apart. Minors: never write a minor's
surname, parents' names, school or neighbourhood anywhere in the repo. Do not git commit/push.`

const TOPIC = A.konu + (A.ozel ? `\n\nOWNER NOTES FOR THIS EPISODE (they outrank the judges):\n${A.ozel}` : '')

const FACTS = `${CONTEXT}

${TOPIC}

You are a meticulous Turkish/English fact-checker. Work in ${D}/arastirma/olgular/. Do NOT edit project files.
Verify, with at least 2 independent sources per fact (prefer academic papers, books, official records, reputable Turkish and
international press; note which sources merely repeat the same original), and record exact URLs:
1. Every person: who (dates, title, institution), what exactly they did, when, where; any photo and its licence.
2. Every number, date and place the story will use (ranges where sources disagree).
3. The viral claim sentence by sentence (if the topic comes from a viral post): what is documented, what is exaggerated, what is
   unsupported. Search for debunks (teyit.org, doğrulukpayı, malumatfurus, academic critiques).
4. Safe phrasing for every contested point ("anlatılana göre", "iddia edilir"; a legend is called a legend).
5. Dramatization limits: who may plausibly say what, in which setting and year, without inventing facts or putting invented quotes
   into real people's mouths; respect toward victims (no mockery, no gore, no identifying photos of private children).
Write ${D}/arastirma/olgular.md and return the same content: short verdict, fact table (fact, confidence, sources), source genealogy,
contested points + safe phrasing, dramatization limits, and a 150-250-word Turkish story-text draft following KONSEPT §5
(encyclopedic first sentence, chronological, ends with a question).`

const ASSETS = `${CONTEXT}

${TOPIC}

You are the asset hunter for this episode. Work in ${D}/arastirma/gorseller/ (downloads, contact sheets). Do NOT edit project files.
LOOK at every candidate image you consider (open it; build contact sheets).
Find and download candidates (record source page URL, author, licence for each):
A. EVIDENCE (2-3 images used at the very END, full width): the real photo/document/clipping/headline of the event. Golden-era endings
   are bold headlines/thumbnails or clippings: find one strong FINAL image that pays off the twist. Copyrighted is acceptable as the
   channel's practice (keep the source URL; it goes to img/telifli/ and the owner decides).
B. BACKGROUND: ONE real colour photo of the real place (or a close equivalent) for all dialogue scenes (CC/PD preferred, >= 1080 px
   short side, natural colours). Give 3 ranked options (tools/bg_ara.py helps).
C. CHARACTERS (clean flat MS-Paint wojak family only, READY-MADE clothed drawings): python tools/wojak_site.py search/sheet/get and
   python tools/wojak_lib.py search/sheet/get (search by role + costume + era, never by nationality: "Turkey"-tagged library images are
   mostly political caricatures). Check assets/kit/* (klasik and others have face variants). For each of the two speakers propose a
   concrete asset id plus a face-variant route for the twist (existing kit variant or tools/kit_varyant.py; same line weight, clean
   eyes/mouth, readable at phone size). Download with --out-dir ${D}/arastirma/gorseller/ and build contact sheets.
Write ${D}/arastirma/gorseller.md with ranked candidates (path, source URL, author, licence, why), contact-sheet paths, and return it.`

const PRODUCE = `${CONTEXT}

${TOPIC}

EPISODE ID: ${ID}. Create it: python -m wojak new ${ID} (skip if it exists). You are the producer.
Read the research first: ${D}/arastirma/olgular.md (the story text and every on-screen claim must follow it; contested points keep
its safe phrasing) and ${D}/arastirma/gorseller.md (assets). Watch the originals (extract frames and LOOK): ${REFS}, and the approved
house examples in teslim/.
Design (decide yourself, justify in the report): the channel's hit pattern is dramatic irony + a "wait, what?!" twist with a face
variant; 17 of the 19 10M+ reels are Turkey-set. Victims are real people: no mockery, no gore; the twist must never ridicule
disability or grief. Roles may be dramatized; real people get no invented specific claims beyond the sources.
HARD RULES (docs/STIL.md; renderer defaults already match it, do not override them):
- 13.5-14.0 s, all durations multiples of 0.5 s; dialogue 2.0-3.0 s (first 2.5-3.0); optional single forward-time card 1.5 s; 2-3
  evidence images at the very END (1.5 s each, last may be 2.0); nothing after evidence.
- Two speakers in the same place and time; A always left, B always right; one character per dialogue scene; present tense, first
  person, colloquial Turkish; 1-11 words (median 5); no '.' or '…'; twist = same character, same box, face variant.
- Clean flat MS-Paint wojak only, ready-made clothed; LOOK at every PNG and register its gaze (python -m wojak yon <png> --yon
  sag|sol|on).
- One real colour background photo for the dialogue (max 2, second only after the card); no zoom/shake/flash/pop/sfx/label/banner;
  music: kanal; no sfx.
- Title per KONSEPT §4 (not AI slop); story text (pinned_comment) 150-250 words, <= ~1,950 characters, encyclopedic first sentence,
  chronological, ends with a question; hashtags: 2-3 topic tags (YouTube only); sources: every fact URL + every image's
  source/licence; credits: CC BY/BY-SA attributions of images actually used; telif_notu for any img/telifli/ image; ek_maddeler (seed
  comment, Hidden Words reminder, related long video); cover_scene = the strongest frame.
- Do not edit code under wojak/ or tools/ (report bugs instead). Do not touch other episodes. Do not commit.
Work loop: python -m wojak check episodes/${ID} (no [stil] warnings) -> python -m wojak frames episodes/${ID} -> LOOK -> python -m wojak
render episodes/${ID} -> python -m wojak teslim episodes/${ID}. Then build ${D}/yanyana.jpg (our frames at 0.5, 3.0, 6.0, 9.0, 11.5,
13.0 s next to 2 originals at the same scale) and look at it honestly, plus 1:1 crops of every face. Write your full report to
${D}/son_uretici_raporu.md and return it: scene list (time, background, character+face, line), title, story text, sources, image
licences, characters used (source ids), what you could not do, side-by-side sheet path.`

const JUDGE_VISUAL = `${CONTEXT}

You are an independent, harsh VISUAL-FIDELITY judge for episode ${ID} (teslim/${ID}/${ID}.mp4, kapak.jpg). Do NOT edit any project
files; work only in ${D}/hakem/<ROUND>/gorsel/. Producer report: ${D}/son_uretici_raporu.md.
Method (mandatory): extract frames every 0.5 s from our reel and from at least 3 of these originals: ${REFS} (always include
C2kkZ8BsngB and C4V3eMFM6lF); also compare with the approved teslim/van-depremi-azra-bebek reel. Build same-scale side-by-side sheets
(the 1080 square at identical scale) plus zoomed crops of every character face next to the originals' characters, and LOOK carefully.
Measure what you claim (text block centre and gap above the head, character height and centre x, background luminance/saturation/
softness, evidence size and placement, cut times via frame difference, in-scene motion). Run python -m wojak check episodes/${ID}.
Score 1-10: 10 = indistinguishable from a golden-era original; 8 = a long-time follower would notice nothing off at normal phone
viewing; 6 = a decent imitation; 4 = obviously not the channel. Sub-scores: format/timing/text, characters (flat MS-Paint wojak
family, ready-made costume fit, size, inward gaze, visible face-variant change at phone size), background, evidence, cover. The
overall is capped by the weakest visible element. Then list concrete fixes ordered by impact, MUST or SHOULD, with exact
values/assets/paths, achievable with the repo's tools (no code edits under wojak/). Return overall, scores, fixes, blockers (empty if
none).`

const JUDGE_FOLLOWER = `${CONTEXT}

${TOPIC}

You are an independent, harsh judge with a different lens: a long-time TURKISH follower of @tarihselwojak plus a fact-checker.
Episode ${ID}. Do NOT edit any project files; work only in ${D}/hakem/<ROUND>/takipci/. Producer report: ${D}/son_uretici_raporu.md;
research: ${D}/arastirma/olgular.md.
Method (mandatory): watch our reel as a sequence (a frame per scene at mid-scene, lines in order at real durations) and do the same
for at least 3 of: ${REFS}; read docs/STIL.md §3 and §14. Judge in Turkish-native terms: hook within 1 s; every line sounds like real
spoken Turkish (register, word order, no translationese, no narration, no '.' or '…'); A/B exchange; does the last dialogue line land
as a "wait, what?!" with a face variant; topic pull and comment bait (title per KONSEPT §4, not AI slop; caption). FACTS: open the
URLs in 'sources' and verify at least 5 key facts used on screen, in the title and in the story text (names, years, positions,
numbers); flag contradictions between lines, evidence, title and story text; check that contested claims are phrased safely; respect
toward victims. Story text: 150-250 words, encyclopedic first sentence, chronological, ends with a question; Turkish spelling/grammar
(also teslim/${ID}/metinler/*.txt after censoring). Score 1-10 with the same anchors (10 = as gripping as a golden-era original;
8 = a follower would notice nothing off). List concrete fixes ordered by impact, MUST/SHOULD, with exact new Turkish
lines/titles/texts. Return overall, scores, fixes, blockers (empty if none).`

const FIX = `${CONTEXT}

${TOPIC}

You are the producer of episode ${ID}, fix round <ROUND>. Read your previous report first: ${D}/son_uretici_raporu.md, and the
research: ${D}/arastirma/olgular.md. Two independent judges scored the current reel:
VISUAL judge <VS>/10. Scores:
<VSCORES>
Blockers: <VBLOCK>
Fixes:
<VFIX>

TURKISH-FOLLOWER/SCRIPT/FACTS judge <FS>/10. Scores:
<FSCORES>
Blockers: <FBLOCK>
Fixes:
<FFIX>

Apply every blocker and MUST fix, then the SHOULD fixes unless one breaks a HARD RULE or the facts (then explain). Where the judges
conflict, follow what the golden-era originals do (look). Keep everything the judges praised; never undo an earlier round's fix.
HARD RULES: 13.5-14.0 s, durations multiples of 0.5 s; dialogue 2.0-3.0 s; optional single forward-time card 1.5 s; 2-3 evidence
images at the very END; A always left, B always right, one character per dialogue scene, present tense, colloquial, 1-11 words, no
'.' or '…'; twist = same character, same box, face variant; clean flat ready-made MS-Paint wojak only, gaze registered; one real
colour background (max 2); no zoom/shake/flash/pop/sfx/label/banner; music: kanal; facts never contradicted; story text 150-250 words
ending with a question; licences in sources/credits; copyrighted evidence in img/telifli/ with telif_notu. No code edits under
wojak/ or tools/; no other episodes; no commit.
Work loop: check (no [stil] warnings) -> frames -> LOOK -> render -> teslim; rebuild ${D}/yanyana.jpg and look at it. Overwrite
${D}/son_uretici_raporu.md with your full report and return it.`

const SCORE = {
  type: 'object',
  properties: { overall: { type: 'number' }, scores: { type: 'string' }, fixes: { type: 'string' }, blockers: { type: 'string' } },
  required: ['overall', 'scores', 'fixes', 'blockers'],
}

phase('Research')
const [facts, assets] = await parallel([
  () => agent(FACTS, { label: 'olgular', phase: 'Research' }),
  () => agent(ASSETS, { label: 'gorseller', phase: 'Research' }),
])
if (!facts) log('fact-check agent failed; producer must verify facts itself')
if (!assets) log('asset agent failed; producer must hunt assets itself')

phase('Produce')
let report = await agent(PRODUCE, { label: `uret:${ID}`, phase: 'Produce' })

const judge = (round) => parallel([
  () => agent(JUDGE_VISUAL.replaceAll('<ROUND>', String(round)), { label: `gorsel${round}`, phase: 'Judge', schema: SCORE }),
  () => agent(JUDGE_FOLLOWER.replaceAll('<ROUND>', String(round)), { label: `takipci${round}`, phase: 'Judge', schema: SCORE }),
]).then(([v, f]) => ({ v, f }))

const noBlock = (b) => !b || !b.trim() || /^(yok|none|no\b|no blocker|-|—|engel yok)/i.test(b.trim())
const ok = (j) => j && j.v && j.f && j.v.overall >= 8 && j.f.overall >= 8 && noBlock(j.v.blockers) && noBlock(j.f.blockers)
const history = []
let cur = await judge(1)
history.push({ round: 1, visual: cur.v && cur.v.overall, follower: cur.f && cur.f.overall })
log(`round 1: visual ${cur.v && cur.v.overall}, follower ${cur.f && cur.f.overall}`)
for (let round = 2; round <= MAX && !ok(cur); round++) {
  if (!cur.v && !cur.f) { log('both judges failed; stopping'); break }
  const v = cur.v || { overall: '?', scores: '(judge failed)', fixes: '', blockers: '' }
  const f = cur.f || { overall: '?', scores: '(judge failed)', fixes: '', blockers: '' }
  const p = FIX.replaceAll('<ROUND>', String(round))
    .replace('<VS>', String(v.overall)).replace('<VSCORES>', v.scores).replace('<VBLOCK>', v.blockers || '-').replace('<VFIX>', v.fixes)
    .replace('<FS>', String(f.overall)).replace('<FSCORES>', f.scores).replace('<FBLOCK>', f.blockers || '-').replace('<FFIX>', f.fixes)
  report = await agent(p, { label: `duzelt${round}`, phase: 'Fix' })
  cur = await judge(round)
  history.push({ round, visual: cur.v && cur.v.overall, follower: cur.f && cur.f.overall })
  log(`round ${round}: visual ${cur.v && cur.v.overall}, follower ${cur.f && cur.f.overall}`)
}
if (!ok(cur)) log('did not reach 8/8 with no blockers; residual fixes returned')
return { id: ID, history, final: cur, report, facts, assets }
