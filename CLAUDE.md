# CLAUDE.md: Tarihsel Wojak production pipeline

Read this first. Specs and lessons live in `docs/`; this file only points to them and lists the hard rules.

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
| `docs/UZUN_FORMAT.md` | Long-form decisions (length, voices, loudness, motion grammar, story template, package) |
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

- Push for the best possible result ("benchmarktasın gibi"); never ship a known flaw silently.
- Long videos: voice will be redone with ElevenLabs when credits arrive (owner disliked the Cartesia voice).
- Characters: prefer ready-made clothed wojaks; do not paint clothes onto wojak heads. Face variants must be clean.
- No end-screen video boxes for now; the subscribe/like/comment call must be engaging, tied to the story.
- Instagram captions: no hashtags. YouTube: 2-3 hashtags allowed. Titles must not read like AI slop.
- Deliver videos via Telegram (`tools/telegram_gonder.py`; creds in secrets.env), chat files are limited to 30 MB.

## Quality bar and workflow

A short reel ships only when two independent judges both give it **at least 8/10** and no MUST fix remains.
The visual-fidelity judge compares it side by side with the originals. The Turkish-follower judge checks
script and facts. Judges never edit files. The producer applies the fixes; where the judges conflict, follow
what the originals do. Full method and checklist: `docs/OGRENILENLER.md`.

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
