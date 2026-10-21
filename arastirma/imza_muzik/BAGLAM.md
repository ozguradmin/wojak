CONTEXT (shared by every agent of the signature-music project)

Repo /home/user/wojak produces videos for the Turkish account @tarihselwojak. For years its short reels used one signature
"original sound": a 13.75 s lo-fi C-minor waltz that followers love (comments imitate it as "u a a u a a"). The YouTube channel just
got a policy/copyright violation, and that audio was extracted from an old reel: its source may be a third-party track (STIL.md §10
says possibly a waltz called "Phantomimes", unverified). The owner wants OUR OWN sound-alike: the same feel and the same quality, but
owned by us, so it can never trigger Content ID or a copyright claim. Later we will vary it per video.
Our first try (tools/imza_muzik.py: additive sawtooth "reeds" + ffmpeg EQ; outputs assets/music/imza_vals.m4a, imza_vals_ikinci.m4a,
imza_vals_ucuncu.m4a) was REJECTED by the owner: "üçüncü daha iyi gibi ama üçü de orijinal kadar iyi değil, beğenmedim.
Benchmarktasın gibi düşün, elinden gelenin en iyisini yap." So the bar is: as good as the original.

FILES
- Original: /home/user/wojak/assets/music/ozel/kanal_orijinal_ses.m4a (13.77 s, 44.1 kHz stereo); WAV copy:
  /tmp/claude-0/-home-user-wojak/e1bf52df-8e16-5819-ad96-6f6873ef480c/scratchpad/muzik/orijinal.wav
- Prior measurements: docs/STIL.md §10.1-10.4.
- Project folder: /tmp/claude-0/-home-user-wojak/e1bf52df-8e16-5819-ad96-6f6873ef480c/scratchpad/muzik2/  (= SP below)
  - SP/analiz/tini.md + tini.json (+ tini/py reusable chain/measurement code, tini/png, tini/wav): DONE timbre/production forensics
  - SP/analiz/muzik.md + muzik.json: DONE music transcription, why it works, off-limits list, composition brief
  - SP/olcum/olcum.py: the shared measurement harness (TIMBRE_SCORE, originality checks). IN PROGRESS until
    SP/olcum/kalibrasyon.md and SP/olcum/teshis.md exist; until then use SP/analiz/tini/py tools, then switch to olcum.py.
  - SP/deneme/deneme_melodi.json: a provisional TEST melody (the owner's least-disliked earlier one) for engine building.
  - Melody JSON format (composers will use the same): {"id", "tempo_bpm", "pickup_beats", "notes":[{"bar":1,"beat":1.0,
    "dur_beats":2,"midi":72,"vel":90}...], "chords":[{"bar":1,"beat":1,"dur_beats":3,"midi":[60,63,67]}...],
    "accomp":{"pattern":"..."}, "counter":[optional, same as notes]}; bars 1-based, beats 1.0-3.x.

TOOLS: python3 with numpy, scipy, librosa, soundfile, pyfluidsynth; fluidsynth CLI; SoundFont /usr/share/sounds/sf2/FluidR3_GM.sf2
(MIT licence, Frank Wen; GM programs 0-based: accordion 21, harmonica 22, tango accordion 23, reed organ 20, church organ 19, drawbar
16, choir aahs 52, voice oohs 53, synth voice 54, music box 10, celesta 8, strings 48-51, violin 40, cello 42, whistle 78, ocarina 79,
recorder 74, flute 73, oboe 68, clarinet 71, bassoon 70 ...), sox, ffmpeg. You may pip install more Python packages (e.g. pedalboard).
Outside sample libraries only with a licence allowing commercial use with no in-video attribution (CC0, public domain, MIT; record
it). Network through a proxy (freepats.zenvoid.org and archive.org reachable). The machine has 4 cores shared by several agents:
keep renders lean (no huge parallel jobs).

HARD RULES
1. NOTHING from the original audio may be used in a candidate: no samples, no segments, no vocoding, no convolution with it. The
   original may be used ONLY for measurement, and for a smoothed long-term-average-spectrum match EQ (>= 1/3-octave smoothing).
2. The melody must be original (see SP/analiz/muzik.json off-limits).
3. Nobody can listen. Every quality claim must rest on measurement or on LOOKING at spectrogram/waveform images you render (Read
   the PNG). Be honest about uncertainty.
4. Work only in your own folder under SP unless told otherwise; do not edit repo files; do not commit; never print secrets.
5. Target spec (from the original): C minor, 3/4 waltz, ~148-156 BPM (bar ~1.16 s), sound starts at 0.00 s, one phrase of ~12 bars,
   a held tonic from ~11.5 s, all sound ends by 13.75 s; legato, continuous, lo-fi gramophone/telephone band (~250-4000 Hz), no
   drums, no sound effects, no words. Deviate only if measurements show the original does otherwise.
