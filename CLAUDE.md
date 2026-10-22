# CLAUDE.md: Tarihsel Wojak production pipeline

Read this first. Specs and lessons live in `docs/`; this file only points to them and lists the hard rules.
**New to the project? Start with `docs/ADIM_ADIM.md`**: the step-by-step runbook for short reels and long videos.

**Current status (21.10.2026):** new **short reels may be produced now** (owner, 21.10): one topic at a time, never a topic
the channel already did. **Long videos still wait for the ElevenLabs API key.** The long `talidomit-turkiye` is approved.
Queued long-form work: `docs/YAYIN_PLANI.md` §4. YouTube got a violation: read `docs/YAYIN_PLANI.md` §0 before producing.
Signature music (22.10): `music: kanal` now plays OUR OWN waltz (`assets/music/imza_v2_golge.m4a`); the old channel audio is
`music: orijinal` only (YouTube risk). Variants `imza_v2_*.m4a` may rotate per video.
**Fresh cloud session?** The licensed font and the reference reels are not in the repo: run `docs/ADIM_ADIM.md` §1.

## What this repo is

The production pipeline for **@tarihselwojak** (Instagram ~465K followers, plus YouTube): Turkish "olay"
videos told with wojak characters (history, mysteries, legends, carefully handled current events).

- **Short reels:** 14 s, 1080x1920, measured "golden-era" style. Four approved episodes are the reference
  set: `van-depremi-azra-bebek`, `canakkale-kayip-tabur`, `kiz-kulesi-efsanesi`, `talidomit-turkiye`
  (`derinkuyu` and `dyatlov-gecidi` are old-style first attempts; `nusret-mayin-gemisi` was dropped).
- **Long-form YouTube (in progress):** 8-10 min, 1920x1080 30 fps, -14 LUFS, narrator Murat + second voice
  Aylin (Cartesia sonic-3), constant motion. First video: the long version of `talidomit-turkiye`.

## The owner's delivery flow

Claude researches and produces; the owner approves and posts. Nothing is posted automatically.

1. Produce, then deliver with `python -m wojak teslim ...` into `teslim/<id>/` (long-form: `teslim/<id>-uzun/`).
   Send the files in chat; videos never go into the repo.
2. The owner watches and replies "onay" or sends notes. **The owner decides every licence question** about
   copyrighted images (`telif_notu` in the package).
3. The owner posts. Instagram gets the whole story text in the caption; YouTube gets it as a pinned comment.
   Per-episode owner tasks (Hidden Words, seed comment, timing) go in `ek_maddeler`.
4. Never hand-edit files under `teslim/`. Change `episode.yaml` (or `video.yaml`) and regenerate.

## Where the specs are

| File | Use it for |
|---|---|
| `docs/STIL.md` | **The law for short reels:** 30 originals measured frame by frame (structure, lines, text, characters, background, evidence, audio). Renderer defaults and `check` follow it |
| `docs/OGRENILENLER.md` | Lessons from 3/10 to 8/10, failure modes and fixes, **pre-delivery checklist**, the research → produce → two judges → fix workflow, time notes |
| `docs/ADIM_ADIM.md` | **Step-by-step runbook** (setup, short reel, long video, self-check, delivery, budgets, common problems) |
| `docs/YAYIN_PLANI.md` | Publishing schedule (long at noon, short in the evening, every 2-3 days) and the queued work for when ElevenLabs arrives |
| `docs/is_akislari/` | Reusable workflow scripts with the exact producer/judge prompts (`kisa_reel.js`, `uzun_video.js`) |
| `docs/UZUN_FORMAT.md` | Long-form decisions (length, voices, loudness, motion grammar, **face size**, **watermark**, story template, package) |
| `docs/UZUN_MOTOR.md` | Long-form engine guide, if present; otherwise the docstring of `wojak/uzun/cli.py` and `uzun/demo/video.yaml` |
| `docs/GUNDEM.md` | Current events: selection, speed, **§5 pre-publish checklist, §7 legal red lines** |
| `docs/KONSEPT.md`, `docs/URETIM_REHBERI.md`, `docs/GEREKENLER.md`, `docs/INSTAGRAM_ANALIZ.md` | Concept and title/story rules, step-by-step production, delivery and secrets setup, topic/timing data |

README.md's "Ne yapar?" section describes the pre-STIL renderer (Poppins, motion, effects). Where it disagrees,
STIL.md wins.

## Layout

- `episodes/<id>/episode.yaml`: one short reel, with `img/`, `img/telifli/` (git-ignored), `chars/` and
  per-episode helper scripts. Start new ones from `episodes/_sablon/` with `python -m wojak new <id>`.
- `assets/kit/<name>/`: reusable character kits (`uret.py` + `kit.json` + face variants).
  `data/karakter_yon.json` is the gaze registry.
- `uzun/<id>/video.yaml`: one long video (demo: `uzun/demo/`). `wojak/` is the short renderer and
  `wojak/uzun/` the long-form engine. `tools/` holds asset search, music, sfx and research tools.
- `out/` (renders) and `referans/` (original reels) are git-ignored.

## Commands

```bash
# short reel
python -m wojak check  episodes/<id>      # validation + timeline + [stil] warnings: must be clean
python -m wojak frames episodes/<id>      # one frame per scene -> out/<id>/kareler/ (LOOK at them)
python -m wojak render episodes/<id>      # out/<id>/: mp4 + kapak.jpg + paylasim.md + metinler/
python -m wojak teslim episodes/<id>      # -> teslim/<id>/ (--zorla only deliberately)
python -m wojak yon <png> --yon sag|sol|on   # register a character's gaze after looking at it

# long form
python -m wojak uzun kontrol   uzun/<id>
python -m wojak uzun seslendir uzun/<id> --qa   # Cartesia TTS (cached) + name check
python -m wojak uzun onizle    uzun/<id> [--bas 1:10 --bit 2:00]
python -m wojak uzun render    uzun/<id>        # also: kare, kucukresim, paket, teslim

# assets and tests
python tools/wojak_site.py search|sheet|get ...   # wojakland / wojaksparadise
python tools/wojak_lib.py  search|sheet|get ...   # 10,378 transparent wojak PNGs
python tools/kit_varyant.py ...                   # face variants of one base
python -m pytest tests/ -q                        # or: python tests/test_uzun.py
```

## The owner's standing preferences (latest first; details in docs/OGRENILENLER.md, top table)

- Music (22.10): every short uses the same signature `music: kanal`; a variant or a slightly slower/lower version only for a
  topic with a very different mood.
- YouTube (22.10): upload straight to public (`tools/yt_yukle.py`). After upload, post the story text as a comment once the token
  has the `youtube.force-ssl` scope. The API cannot pin comments; the owner pins in Studio.
- No AI-generated images (16.10): backgrounds and evidence are real photos/documents (or our own flat drawings);
  characters are ready-made wojak drawings. `tools/gorsel_uret.py` and the SOL gateway are not used.
- Short reels: produce now (21.10). Long videos: wait for ElevenLabs, then follow `docs/YAYIN_PLANI.md` §4 in order.
- Publishing plan: one topic every 2-3 days, 2-3 per week. The long video goes to YouTube at noon; the same topic's
  Shorts and Reels go out in the evening, and their descriptions point to the long video.
- Long videos: no burned-in watermark from the ElevenLabs re-voice on (`filigran: false`; use the YouTube Studio branding
  watermark instead). Short reels keep it.
- Long videos: keep each character's effective height (`boy` × camera zoom × `yakin`) at or below 0.80 of the frame.
  The owner noticed oversized, cropped faces.
- Short reels should get the long video's character quality (better faces) as a B version; the owner picks.
- Push for the best possible result ("benchmarktasın gibi"); never ship a known flaw silently.
- Long videos: voice will be redone with ElevenLabs when credits arrive (owner disliked the Cartesia voice).
- Characters: prefer ready-made clothed wojaks; do not paint clothes onto wojak heads. Face variants must be clean.
- No end-screen video boxes for now; the subscribe/like/comment call must be engaging, tied to the story.
- Instagram captions: no hashtags. YouTube: 2-3 hashtags allowed. Titles must not read like AI slop.
- Deliver videos via Telegram (`tools/telegram_gonder.py`; creds in secrets.env; files > 50 MB go as one file via
  `tools/telegram/gonder.js`, MTProto over WSS; first run `cd tools/telegram && npm install`). Chat files are limited to 30 MB.

## Quality bar and workflow

A short reel ships only when two independent judges both give it **at least 8/10** and no MUST fix remains.
The visual-fidelity judge compares it side by side with the originals. The Turkish-follower judge checks
script and facts. Judges never edit files. The producer applies the fixes; where the judges conflict, follow
what the originals do. Full method and checklist: `docs/OGRENILENLER.md`.

A long video ships only when four independent judges each give it **at least 8/10** with no blocker.
The four lenses are retention/visual, character/animation, Turkish narration/facts, and technical/package.
Steps: `docs/ADIM_ADIM.md` §4. Prompts: `docs/is_akislari/uzun_video.js`.

## Hard rules

1. **Secrets** (`CARTESIA_API_KEY`, `SOL_API_KEY`, cookies, tokens) live only in environment variables or in
   `~/.config/wojak/secrets.env` (outside the repo, chmod 600), read via `wojak.config.load_secrets()`. Never
   print, log, commit or copy them anywhere else: not into yaml, reports, scratch files or command lines that get echoed.
2. **The repo is public.** Never commit:
   - licensed fonts (`assets/fonts/ozel/`)
   - channel audio (`assets/music/ozel/`)
   - `referans/`
   - copyrighted images (keep them under `*/img/telifli/`)
   - videos (`*.mp4`)
   - `.env` and cookie files

   Check `git status` before every commit. A new folder may not be covered by `.gitignore`.
3. **Network privacy:**
   - Use a generic browser User-Agent.
   - Never put an e-mail address or any personal identifier in HTTP headers or requests.
   - Never bypass the proxy.
   - Pace Wikimedia requests at least 10 s apart (it returns HTTP 429).
4. **Minors and private people:**
   - For a minor, never write the surname, parents' names, school, neighbourhood or a current photo anywhere in
     the repo, including yaml `notes` and `sources`. Git history is public.
   - Hidden Words lists go to the owner in chat only.
   - Do not write the family names of private people into files.
   - No mocking of victims, no graphic content, no invented quotes for real people, no "last words" for the
     recently dead. Follow GUNDEM.md §5 and §7.
5. **Facts:** use at least 2 independent sources. Contested claims are written as "anlatılana göre" (as told),
   and a legend is called a legend. Record every image licence in `sources` and CC attribution in `credits`.
6. **Git:**
   - Commit and push finished work to the session's designated branch (the owner reviews there); no PR unless asked.
   - Never force-push or rewrite history without the owner's explicit approval.
   - During an episode fix loop, do not edit `wojak/` or `tools/`; report bugs instead.

## Commit messages

The convention in `git log`:

- **Subject:** Turkish, one line, says what changed. Scores are often included, e.g. "iki hakemden 8/8".
- **Body:** optional, Turkish bullet lines starting with "- ".
- **Trailers:** end with the attribution lines the session provides, currently:

```
Co-Authored-By: Claude <model> <noreply@anthropic.com>
Claude-Session: <session URL>
```
