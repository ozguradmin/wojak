# Talidomit uzun: Gemini turu, 1. hakem turu (23.10.2026)

> Dört bağımsız hakemin kararları (docs/is_akislari/uzun_video.js, basla: hakem). 2. tur düzeltmesi yarıda durduruldu
> (hesap sahibi: kota). Devam: YAYIN_PLANI §4 madde 4'teki not.

## izlenme1: 7.5/10

**Puanlar:** Retention/visual judge, Gemini re-voice round (teslim/talidomit-turkiye-uzun, 10:56).

- First 30 s (hook): 9. A wojak is on screen from 0:00. In order: 46 countries, a 10,000+ counter, Turkey green with a RUHSAT VERİLMEDİ stamp at 0:10, the Ankara door slamming on "kim kapattı?" at 0:14, and BELGE: 0 / BOŞ. The Kore ad voice "Tamamen zehirsiz." lands at 0:31, exactly as the yellow highlight appears. The thumbnail promise is paid off in the first 35 s. A viewer who clicked would stay.
- Pacing per chapter: 8. Chapter lengths are 1:30 / 1:06 / 1:45 / 1:11 / 2:24 / 1:32 / kapanış 0:45. Speech fills 465 of 656 s, at a median 5.9 syllables/s (p90 6.75), which fits the calm, tense style. The 31 pauses of 1.2 s or more are almost all deliberate stamp beats. The re-voice added 23 s but the video is still not draggy. The heaviest stretch is the 38.5 s on one cork board (7:26.8-8:05.3), which the owner already approved.
- Visual variety and motion: 9. Frame-difference scan at 10 fps: no near-static run of 3 s or more except 7:33.6 (3.6 s on the board). No dark run except the two chapter cards. Something new appears on screen every few seconds.
- Character share: 9. A wojak reacts in almost every info scene.
- Face size and cropping: 6. All sizes are 0.80 or less except the single 0.86 shot, which is correct. But that dramatic shot crops the chin for about 8 s (MUST 1). This is the exact scene the owner complained about.
- Animation and readability: 8.5. Unchanged from the approved cut. Faces switch on the right beats, gaze points inward, and stamps hold 1.2 s or more except at 2:24.
- Thumbnail and title: 8.5. K1 ("TAMAMEN ZEHİRSİZ" + HAYIR + the sweating representative) reads at 168x94 and 360x202. K3 is a good test variant; K2 is the weakest. Title 1 has a concrete number and a curiosity gap, and does not read like AI slop.
- Audio balance: 8.5. Voice is above the music+sfx bed by 19 dB at the median and 8.1 dB at the 5th percentile. The only dips under 6 dB are 0.3 s word onsets under stamp sfx. No bed window goes above speech median + 3 dB. Kore lines are about 1 dB above Charon, so there is no level jump between voices. The mix has no digital-zero silence.
- Voice delivery (retention view): 6.5. About 22 lines end with a chopped final syllable (MUST 2). There is also a dead 1.7 s pause at 2:21 (SHOULD 1).
- Climax: 7. The staging is strong: ETKİLİ OLABİLİR, then …AMA ZEHİRLİLİK, then the OLUMSUZ GÖRÜŞ stamp held 1.2 s, then RUHSAT VERİLMEDİ held 1.3 s. But the chin is cropped, and the name reveal "Kaymakçalan" loses its final "n".
- Kapanış CTA: 8.5. The question gets A/B/C cards that react about 0.85 s apart. Abone/zil/beğen come after. The comment is typed, there is no video box, and the pinned comment matches the cards.

Evidence (all under /tmp/claude-0/-home-user/e1bf52df-8e16-5819-ad96-6f6873ef480c/scratchpad/uzun/talidomit-turkiye/hakem/1/izlenme/):
- sayfalar/ (contact sheets: 1 s for the first minute, 2 s after)
- transkript.txt (full-mix faster-whisper medium)
- cene.txt (face-box bottom measured with the engine geometry)
- kuyruk.txt (truncated line tails)
- ses_analiz.txt
- tam/b64_sheet.jpg (6:36.4-6:41, chin cut)
- serit/bosluk.jpg (2:19-2:24.5)
- serit/doruk.jpg (6:44.5-6:53)

**Engel:** 1) Climax B5.3b (6:36.2-6:44.4): Kaymakçalan's chin and mouth are below the frame. The face box ends at 1.12 H at the start of the scene, and frames at 6:36.4-6:41 show it cut. This is the owner's explicit complaint scene and breaks rule 3. kontrol reports it clean only because its face out-of-frame check ignores the bottom edge.
2) Until ear-checked and re-taken: clipped sentence ends from Gemini on about 22 lines. Whisper confirms three, including the name reveal at 6:35.5, where "Şükrü Kaymakçalan" is heard as "Kaymakçala". Do not ship the climax line with its final syllable cut.

**Düzeltmeler:**

MUST 1 (blocker): the climax crops Kaymakçalan's chin and mouth below the frame from 6:36.2 to about 6:44.4. Scene: bölüm 6, sahne 4, "B5.3b · DORUK", video.yaml around line 1405.
- This is the owner's own complaint ("Kaymakçalan + RUHSAT BAŞVURUSU, altta kesik") and a break of rule 3 ("whole head and chin inside the frame").
- The producer shrank `boy` from 0.74 to 0.66 (effective size 0.86). But the camera starts at zoom 1.3 centred at y 0.42, so the world bottom stays far out of frame.
- Engine geometry: the face box (top of head to neck) ends at 1.12 H at the start of the scene, 17% of the face height below the edge, and stays below the edge for 8.2 s. Frames at 6:36.4 / 6:37.5 / 6:39 / 6:41 show the mouth on the bottom edge and the chin cut. At 6:44.6 the chin is only about 15 px above the edge.
- Fix: change `kamera: {zoom: [1.3, 1.2], merkez: [[0.66, 0.42], [0.42, 0.5]]}` to `merkez: [[0.66, 0.56], [0.42, 0.53]]` and keep the zoom, so the drama stays. Computed: neck at about 0.93 H at the start and about 0.94 H at the end; head top at about 0.26 H, so it clears the kelime at y 0.14-0.15.
- Then re-check the OLUMSUZ GÖRÜŞ damga (x 0.42, y 0.6) on the folder, which shifts up about 0.04 H. If it no longer sits on the folder, try y 0.57.
- Verify with `uzun kare --t 6:36.4`, `6:40` and `6:44.5`.
- Also extend the engine check so this cannot recur: in `wojak/uzun/yerlesim._karakter_denetle` the `dis` term counts only the left, right and top edges. Add `max(0, fb[3] - H) / fh` with a small allowance (about 0.03), because the box ends at the neck. Today kontrol cannot see bottom-cropped faces at all, which is why it reported this scene clean.

MUST 2: Gemini truncates sentence ends on about 22 lines. The final syllable is still at -3 to -15 dB of the line's peak 10-40 ms before the clip ends, then only the 25 ms engine fade follows, with no natural decay.
- The raw takes already end this way: 81 of 188 Gemini raw takes have less than 30 ms of trailing silence. So `sessizlik_kirp` is not the cause, and the per-line Whisper QA does not catch it.
- My full-mix Whisper drops the final syllable on three of them:
  - 4:31.0 "ilk haftaları" heard as "haftalı"
  - 6:35.5 "Şükrü Kaymakçalan" heard as "Kaymakçala" (the climax name reveal)
  - 8:13.6 "vakalar görüldü" heard as "görül"
- Worst measured tail: 9:15.8 "…nasıl yapıyordu?" at -3 dB.
- The rest, by end time: 9:20.1 "gösterildi:", 4:58.0 "ne oldu?", 1:40.1 "piyasaya çıkıyor.", 2:49.5 "gönül rahatlığıyla alıyor.", 5:23.0 "talidomit.", 5:25.1 "Kevadon.", 4:40.4 "beklenecekti.", 9:42.0 "yayımlandı.", 7:06.0 "baştan kapalı.", 8:56.2 "iyileşmeye başlıyor.", 3:16.9 "yerdeydi:", 0:53.1 "getirmiş.", 5:12.1 "demişti.", 7:57.7 "Enstitüsü.", 3:55.5 "tekrarlıyor.", 0:13.8 "kapattı?", 4:50.1 "yaşıyor.", 4:44.6 "gelişmemiş.". The list with levels is in kuyruk.txt.
- Fix: add a "kesik son" check to `seslendir --qa`, rejecting a take like a take with extra words when its last 30 ms is above p95 − 20 dB or its raw trailing silence is under 40 ms. Then run `python -m wojak uzun seslendir uzun/talidomit-turkiye --qa --kotu --yenile 3` on these lines.
- If Gemini keeps truncating, test ending the `tts` text with "…" (text only; no change to voice, speed or style).
- Then run kontrol, render and the rest. Ear-check the climax line and 9:12 first.

SHOULD 1: 2:21.0-2:22.6 (bölüm 3, sahne 1, the line "Ama haritada bir boşluk var: Türkiye."). Gemini's 1.7 s pause after "var:" sits on an unchanged world map, so nothing moves in picture or voice. Then the Turkey push and the "BOŞLUK: TÜRKİYE" damga get only about 1.0 s before the cut at 2:24.53 (the rule is 1.2 s or more).
- Fix: move `{tip: ulke, kod: TUR}` and `{tip: it}` from `an: son, ofset: -0.55/-0.6` to about `ofset: -1.5`, so the reveal fills the pause.
- Keep the damga at `an: son, ofset: 0.15` and raise the line's `sonra` from 0.4 to 0.7, giving the stamp about 1.4 s.

SHOULD 2: kapanış question (bölüm 8, sahne 1, around line 2025). Full-mix Whisper heard "Tek bir kahraman mı? / …bir kural mı?" as "kahramandan … kurama". The "mı" question tone may be too weak right where the A/B/C cards are set up.
- Ear-check. If it is weak, add a per-line `tarz` ("soru tonuyla; 'mı'yı net ve ayrı söyle") and re-take.

SHOULD 3: package text is stale in paylasim.md (fix it in the generator or `ek_maddeler`, not by hand).
- The "Değiştirilmiş ya da yapay içerik" item still says "Seslendirme yapay zekâ (Cartesia)"; it should say Google Gemini.
- The "Süre" item says "~30 sn üstünde". It is now 56 s over 10:00 and 41 s over the ADIM_ADIM 10:15 gate.

SHOULD 4: 1:41.3 "Bu arada bir ayrıntı:" is +3.5 dB louder than its neighbours for 1 s, then drops 4.4 dB on "Batı Almanya'da…". Ear-check. If it sounds like a jump, re-take, or split the line and set per-line `db`.

NICE 1: 6:34-6:36 (B5.3a). Kaymakçalan's chin is within about 2% of the bottom edge at the end of the push. Change the end `merkez` from `[0.6, 0.47]` to `[0.6, 0.51]`.

NICE 2: 2:49.1-2:49.5 (B3.4, "HAMİLELERDE TEST EDİLMEDİ" push). The pharmacist's neck reaches the frame bottom at the end of the push. Lower the end zoom slightly or raise merkez y by 0.03.

NICE 3: 7:33.6. A 3.6 s near-static hold on the board. Add a small `it` to the "ANMA YAZILARI, 1994" card as it lands. No redesign.

## animasyon1: 7.5/10

**Puanlar:** Character & animation judge, round 1 (Gemini re-voice). I judged teslim/talidomit-turkiye-uzun/talidomit-turkiye-uzun.mp4 (19,688 frames, 10:56) and the three thumbnails.

Method:
- Decoded at 30 fps with tools/uzun_animasyon_denetimi.py (kareler) and ran the report (rapor).
- The `oge` step crashes on Python 3.13 (see fixes, item 10), so I traced every bindir call with an equivalent wrapper and ran rapor with --oge as well.
- Looked at full resolution at 3 frames per scene for all 72 scenes with characters, and frame strips at every flagged moment and every same-character cut.
- Measured chin and face boxes for every live character every 0.1 s, using the engine's own ekran_kutulari and yuz_kutusu.
- Aligned every stamp, word and face event against Whisper word times.
- Checked thumbnails at 1280x720 and 168x94.
- Test-rendered proposed camera fixes in memory. No project files were edited.

Scores:
- Characters and clothing: 9. All are ready-made clothed v2 drawings, with no pasted clothes and the same line weight.
- Face variants: 8.5. Clean lines, classic eyes, readable on a phone (Kelsey suspicious/determined, Kaymakçalan thoughtful/serious/determined, narrator sweaty/teary/surprised/happy), each on the right beat.
- Face size and framing: 6.5.
  - The effective heights are within the rule (max 0.80, plus one dramatic 0.86).
  - But in that one dramatic close-up (6:36-6:44) Kaymakçalan's chin and jaw are cut off by the frame bottom.
  - Two other camera pushes end with the chin on the bottom edge.
- Motion and transitions: 8.5.
  - The hook door closes over 4-5 frames with a shake.
  - Motion blur sits under the sharp sprite, so no ghosts.
  - Dip and push transitions are clean, with no double characters in crossfades, and the Lenz matched cut at 4:07.7 holds.
  - The 20?? corner indicator only runs forward.
  - Counters behave. No 1-2 frame pops; every flag was a counter, a typing label or a fast entrance.
  - The KESMEDE YARI SAYDAM flags all fall inside crossfade or dip cuts.
- Sync with the new speech: 8. Stamps and face changes land on their words (BOŞLUK: TÜRKİYE, OLUMSUZ GÖRÜŞ, YANLIŞ, PİYASADAN ÇEKİLDİ, the door slam). One word appears 1.3 s early.
- Closing CTA: 9.
  - The A/B/C question is tied to the story, and the cards react about 0.85 s apart.
  - The cursor clicks Subscribe, the bell and Like; the comment is typed and sent; the narrator smiles.
  - No video boxes.
- Thumbnails: 8.5. All three are readable at phone size; K2's character is small.
- Watermark: none is burned in, as required.

With the blocker fixed I would score it about 8.5.

**Engel:** The only deliberate dramatic close-up still breaks owner rule 3. In B5.3b, from 6:36.2 to about 6:44.5, Kaymakçalan's chin and jaw are cut off by the bottom of the frame: the face box goes up to 127 px past the edge at 1080. The rule allows up to 0.88 only with the whole head and chin in frame, and the owner named bottom-cropped faces specifically. The fix is a camera centre change, already verified in memory: merkez [[0.66,0.53],[0.47,0.55]], stamp y 0.5, second word y 0.12 (fixes item 1). Then re-render.

**Düzeltmeler:**

1. MUST, 6:36.2-6:47.7 (B5.3b climax, scene 61, the video's only deliberate close-up at 0.86): Kaymakçalan's chin and jaw are cut by the frame bottom.
- Measured face-box bottom: +127 px below the frame at 6:36.6, still +24 px at 6:43; the chin is back inside only from about 6:44.5.
- Visible in frames 11905, 12100 and 12200.
- Rule 3 allows a dramatic close-up only "with the whole head and chin inside the frame". This is the exact defect the owner noticed, and the producer report says it is fixed.
- Fix in video.yaml (B5.3b):
  - `kamera: {zoom: [1.3, 1.2], merkez: [[0.66, 0.53], [0.47, 0.55]], it: 0}` (was [[0.66,0.42],[0.42,0.5]]).
  - Damga "OLUMSUZ GÖRÜŞ": y 0.6 -> 0.5, so it stays on the folder.
  - Kelime "…AMA ZEHİRLİLİK DENEYLERİ YETERSİZ": y 0.14 -> 0.12, so it clears the hair. Do not use 0.075: that clips the word.
- Verified in memory: the chin stays 26-93 px inside at 1080 for the whole scene, the green collar shows, the stamp sits on the folder and the word clears the hair. The cut in is karart, so there is no jump.
- Then run kontrol and look at frames at 6:37, 6:42 and 6:47.

2. SHOULD, engine/kontrol gap (report it; do not edit wojak/ during the fix loop): the face-out-of-frame check never looks at the bottom edge.
- yerlesim._karakter_denetle measures only left/right/top: `dis = max((max(0,-fb[0])+max(0,fb[2]-W))/fw, max(0,-fb[1])/fh)`.
- cli.etkin_boylar ignores camera merkez.
- So chins cut by the bottom edge always pass. Add a warning when the face-box bottom exceeds H-8 px outside entrances and exits.
- My measurement script: /tmp/claude-0/-home-user/e1bf52df-8e16-5819-ad96-6f6873ef480c/scratchpad/uzun/talidomit-turkiye/hakem/1/animasyon/araclar/cene.py, output in /tmp/claude-0/-home-user/e1bf52df-8e16-5819-ad96-6f6873ef480c/scratchpad/uzun/talidomit-turkiye/hakem/1/animasyon/cene.txt.

3. SHOULD, 3:11.3-3:17.1 (B3.8, scene 29): the zoom 1.0 -> 1.3 push goes to the default centre (0.5, 0.46) while the narrator sits low.
- At 3:16.9 his chin touches the bottom edge (21 px left) and about 45% of the frame is empty wall above his head.
- Fix: `kamera: {zoom: [1.0, 1.3], merkez: [[0.5, 0.5], [0.5, 0.6]], it: 0}`. Verified in memory: head centred, with collar and shirt visible.

4. SHOULD, 5:32.1-5:45.9 (B4.4, scene 51): Kelsey's push ends with her chin about 15 px from the bottom.
- Fix: merkez [[0.44,0.52],[0.76,0.46]] -> [[0.44,0.52],[0.74,0.54]]. Verified: chin and collar inside.
- The folder stack at bottom-left is also cut by the left edge at the end (flagged at 5:39.9). Move it in: x +0.04.

5. SHOULD, 9:54.1 (B6.6, scene 82): the green RUHSAT stamp's landing animation sweeps across temsilci2000's left eye and cheek for 3 frames (17826-17828), then rests about 25 px from his cheek. "Yüze binen damga yasak."
- Fix: damga x 0.47 -> 0.42 (or boy 110 -> 96), then check the 30 fps strip.

6. SHOULD, 0:22.47 (scene 5): "REÇETESİZ" appears 1.33 s before the word, while the narrator is still saying "1957, Batı Almanya." (Gemini's longer period pauses).
- Fix: ofset 1.9 -> 3.2.
- Every other word and stamp is within about 1 s of its word (‘OLUMSUZ ETKİSİ YOK’ shows 0.5 s before Kore's quote, which is fine).

7. NICE, holds stretched by the slower read:
- 2:19.4-2:22.4: Gemini's 1.8 s pause before "Türkiye." leaves 3.0 s of drift only. Start the `it` push about 0.6 s earlier so it still lands on the word.
- 7:34-7:41.7 (board, scene 66): about 7 s of static board after the ANMA card lands. Add a slow camera push to the card, or a face change on the Kaymakçalan guest at "danışmanlık".

8. NICE, same-character size and position jumps at hard cuts into info cards (pre-existing): 3:03.6 Voss (large right -> corner, x 0.88) and 8:56.4 Sheskin (0.63 -> 0.5 in the corner). Use kaydir or karart, or match the position.

9. NICE, 3:58-4:04: the ‘İFTİRA’ stamp covers the envelope's own "TAAHHÜTLÜ" label. Move the stamp up or down by 0.05.

10. Tool bug (report): `tools/uzun_animasyon_denetimi.py oge` crashes on Python 3.13 with `AttributeError: Can't get local object 'cmd_oge.<locals>.sahne_isle'`, because a local function is passed to Pool.imap_unordered.
- Fix: move sahne_isle and its state to module level.
- Working wrapper: /tmp/claude-0/-home-user/e1bf52df-8e16-5819-ad96-6f6873ef480c/scratchpad/uzun/talidomit-turkiye/hakem/1/animasyon/araclar/oge_sarici.py.

Evidence (all under /tmp/claude-0/-home-user/e1bf52df-8e16-5819-ad96-6f6873ef480c/scratchpad/uzun/talidomit-turkiye/hakem/1/animasyon/):
- Full tool report: rapor_tam.txt
- Climax crop frames: seri/k11905.png, seri/k12100.png
- Proposed climax fix: seri/deneme_s61_e.png
- Event-vs-word alignment: olay_kelime.txt
- Contact sheets: sayfalar/

## dil1: 8.2/10

**Puanlar:** Dil ve olgu hakemi (hakem 1), teslim/talidomit-turkiye-uzun (Gemini turu, 10:56, 152 satır).

YÖNTEM: Final mp4'ün sesi ffmpeg ile 16 kHz float'a çözüldü, faster-whisper medium ile döküldü (int8, beam 5, kelime zamanlı, ipucu yok). Motorun kendi zaman çizelgesiyle (toplam 656,267 sn, videoyla birebir) 152 satıra hizalandı. Şüpheli satırlar ayrıca hem ham TTS klibinden hem miks kesitinden yeniden döküldü (small ve medium, beam 5 ve 10). Duraklar, hece hızı ve klip sonu enerjisi her klipte ölçüldü. Satır düzeyleri anlatım ve altlık stemlerinde BS.1770 K-ağırlıklı olarak ölçüldü.

PUANLAR
- Doğal konuşma Türkçesi (çeviri kokusu yok): 8.8. Cümleler kısa ve konuşur gibi. Tarihî şimdiki zaman ile -mişti/-di arka planı doğru dengelenmiş. "Onlar için bu, bir tarih dersi değil." ve "o ‘deneme’ kapısı, burada baştan kapalı" gibi satırlar çok iyi.
- Ritim ve duraklar: 8.2.
  - Hece hızı: hiçbir satır 7,0 hece/sn'yi aşmıyor. Anlatıcının ortalaması 5,94, medyanı 6,17. En hızlı satır L97 (6,99).
  - Cümle içinde 1,2 sn'yi aşan tek durak 2:19'da (1,76 sn).
  - Kısa ama göze batan bir Gemini durağı: 1:26 "Oysa … kandaki" (0,92 sn).
- Telaffuz ve isimler: 7.3.
  - 6:35'te "Kaymakçalan" kesik.
  - 10:15'te "kahraman mı?" sorusundaki "mı" duyulmuyor.
  - 2:24'te "Gürünentel" okunuyor (1:04'te doğru).
  - FDA 5:12'de "Ef De A", 13 sn sonra 5:25'te "Fe De A" okunuyor.
  - "yayımlanmadı/yayımlanmış" iki yerde "yayın-" duyuluyor.
  - Öteki isimler temiz: Lenz/Lents, Kelsey, Kevadon, Distaval, Şeskin, Nejat, Eczacıbaşı, Refik Saydam, Cerrahpaşa, Behçet, SALL4, Süreyya Tahsin Aygün.
  - Hiçbir çekimde tarz tarifi sesli okunmamış (fazla kelime yok).
- Yabancı ad ekleri ve yazım: 9.5. Grünenthal'in (ince l), Lenz'in, Kelsey'yi/Kelsey'nin, ABD'ydi ve Sheskin'in doğru. Tırnaktan sonraki ekler kesmesiz (TDK). Bağlaç "da" ayrı ve doğru: "Doğu Almanya da", "İstanbul'un da".
- Ton: 9.5. Belgesel dili, saygılı, sansasyon yok. Mağdurlar onurlu anlatılıyor.
- Olgular: 9.6. Bu turda 26 iddia kaynağından yeniden açıldı; hata yok. Türkiye bölümü araştırmadaki güvenli kalıplarla birebir.
- Ses düzeyi ve sesler arası geçiş: 9.3.
  - Anlatıcı satırlarının sapması (σ) 0,42 dB.
  - İkinci ses (Kore) anlatıcının +0,2 ile +1,4 dB üstünde.
  - Ardışık satırlar arasında 3 dB'yi aşan sıçrama yok.
  - Ses-altlık farkı medyan 17,3 dB, en düşük 7,8 dB (L152). Kural (6 dB) her yerde sağlanıyor.
- Paket metinleri (başlık, açıklama, bölümler, sabit yorum, etiketler): 8.6.
  - Başlık doğal, 51 karakter. Açıklama 4.918 bayt (sınır 5.000), < > yok.
  - Bölümler zaman çizelgesiyle uyuşuyor: 0:00 başlıyor, 8 bölüm, her biri 10 sn'den uzun.
  - Etiketler ve 3 hashtag kurala uygun. Sabit yorum kapanıştaki A/B/C ile aynı.
  - Kusurlar: bayat "Cartesia" satırı, bayat süre notu, dinleme listesinde 6:27 için yanlış teşhis.
- SRT: 8.4. Metin video.yaml ile birebir, alıntılar italik; üç blok kırımı zayıf.

DOĞRULANAN OLGULAR (kaynak açılarak)
1. Grünenthal'in 1961 Kasımına kadar 300 milyonu aşkın günlük doz satması; "gefahrlos / völlig ungiftig" reklamı; dönemde devlet ruhsat şartı olmaması: Ärzteblatt 2016.
2. Contergan'ın 1.10.1957'de reçetesiz piyasaya çıkması: SRF 2018 ve Planet Wissen.
3. Lenz'in 15.11.1961 telefonu, taahhütlü mektup (Einschreiben), 20 Kasım'daki "Rufmord" suçlaması ve dava tehdidi, 26 Kasım Welt am Sonntag (o gün pazar), ertesi gün toplatma: Planet Wissen.
4. 46 ülke, 10 binden fazla bebek, Distaval reklamının birebir metni, ABD'de ~1.200 doktor ve ~20.000 hasta, gebeliğin 20-37. günleri: Science Museum.
5. Yaklaşık %40'ın doğumda ya da kısa süre sonra ölümü; ABD'de en az 17 vaka: Wikipedia ve UChicago 2020.
6. Kelsey'nin 1960'ta FDA'ya katılması, 60 gün kuralı, 1.267 doktor, 17 vaka (10'u Kevadon'la), Washington Post 15.7.1962, Kennedy ödülü 7.8.1962: UChicago, NLM ve Scientific American.
7. Noel 1956'da Grünenthal çalışanının kulaksız doğan kızı; 1959'daki ilk sinir hasarı bildirimi: Scientific American 2024.
8. Almanya'da bugün ~2.400 kişinin yaşaması: SRF 2018.
9. Doğu Almanya'nın ruhsat vermemesi ve kaçak ilaçla en az 10 vaka: nd 2007.
10. Brezilya'da 1965 sonrası lepra kullanımıyla vakalar: Vianna, PLoS ONE 2011.
11. SALL4'ün 2018'de gösterilmesi: Donovan, eLife 2018.
12. Hamuryudan 1998: Cerrahpaşa, 96 erkek hasta, Ann Intern Med (PubMed özeti).
13. Sheskin 1965, Clin Pharmacol Ther 6:303.
14. 1262 sayılı Kanun: kabul 14/5/1928; md. 3 satıştan ya da ithalattan önce Bakanlık izni şart (mevzuat.gov.tr PDF).
15. TİTCK KÜB: ilk ruhsat 31/05/2004. "Talidomid, gebe kadınlar (…) tarafından kesinlikle kullanılmamalıdır." alıntısı bölüm 4.4'ün dürüst bir kısaltması.
16. TFD Bülteni 114 (2012):
    - Kaymakçalan'ın "etkin olabilir ama toksisite çalışmaları yetersiz" diyerek olumsuz görüş vermesi (Özer ve Dülger tanıklığı).
    - Bakanlığın bu görüşü dikkate alması.
    - Ruhsatsız ilacın tanıtım numunesinin de giremediği.
    - Nejat Eczacıbaşı'nın sözünün bir SÖYLEŞİ olduğu ("Yazı, konuşma ve söyleşilerden", 1998); başarıyı Refik Saydam Enstitüsü'ne bağlaması.
    - Gerçeker'in "kanıtlayacak bir belge sunamadığı".
17. TFD Bülteni 26 (1994), sayfa görüntüleri tek tek okundu: Kayaalp ve Bökesoy'un anma yazıları "ölümünün onuncu yılında". Kayaalp'in yazısında Bakanlığa (başta İlaç ve Eczacılık Genel Müdürlüğü) danışmanlık geçiyor; iki yazıda da talidomit hiç geçmiyor.

ÇALIŞMA DOSYALARI (/tmp/claude-0/-home-user/e1bf52df-8e16-5819-ad96-6f6873ef480c/scratchpad/uzun/talidomit-turkiye/hakem/1/dil/)
- out/: whisper_medium.json, satirlar.json, hizalama.json, kuyruk.json, ritim.json
- kaynak_dl/: tfd114.txt, tfd26 sayfaları, kub.txt, m1262.txt
- scripts/: kullanılan betikler

**Engel:** Olgu ya da dil engeli yok. Videodaki ve pakette kontrol edilen her iddia kaynakla tutuyor; Türkiye bölümü araştırmadaki güvenli ifadelerle birebir. Yayından önce yapılması gereken tek iş MUST 1: 6:35'teki "Şükrü Kaymakçalan." satırı yeniden çekilmeli, çünkü ham Gemini çekimi adın son sesinde kesik (Whisper 4/4 "Kaymakçala"). Bu tek satırlık bir yeniden çekim; yapıldığında 8.2 puan geçerli olur.

**Düzeltmeler:**

MUST 1 — 6:35, B5.2 (satır 96): "…genç bir farmakolog: Şükrü Kaymakçalan." Adın son sesi kesik.
- Sorun Gemini'nin ham çekiminde (out/talidomit-turkiye-uzun/ses/ham/hf39ee9f71c5edf9610b.wav, tek önbellek çekimi): son 30 ms konuşma düzeyinin yalnız 13 dB altında ve sonda sessizlik yok. Yani çekim "n" bitmeden kesiliyor; motorun 25 ms'lik söndürmesi kalan payı da alıyor.
- Whisper medium klipte ve mikste, beam 5 ve 10'da, 4/4 "Kaymakçala" yazıyor. small "kaymak çalan" duyuyor, yani "n" ancak sınırda var.
- Gerçek kişinin adı, üstelik Türkiye bölümündeki tanıtım anı.
- Düzeltme: yalnız bu satırı yeniden çek (seslendir --qa --yenile 3). Seçilecek çekimde iki şart olsun: ham çekimin sonu sessiz (son 30 ms ≤ −30 dB, tepe düzeyine göre) ve ipucusuz Whisper "Kaymakçalan" yazıyor.
- 3 denemede olmazsa adı cümle sonundan al (isim etiketi ekranda zaten var):
  metin: "Meslektaşlarının anlattığına göre, başvuru hakkında görüş verenlerden biri, Şükrü Kaymakçalan adında genç bir farmakolog."
- Sonra paylasim.md dinleme listesindeki 6:27 notunu düzelt. Şu an "okunuş doğru görünüyor" diyor; doğrusu: "ham çekim adın son sesinde kesikti".
- Motor önerisi (rapor; ben düzenlemedim): QA, ham çekim sonu tepe düzeyinin 20 dB'den yakınında olan çekimi seçmesin. Bugün bu durumda 5 satır var: 128 (−10,6 dB), 96 (−13,3), 41 (−13,4), 134 (−14,3), 68 (−14,4).

SHOULD 1 — 10:15, KP.1 (satır 144): "Tek bir kahraman mı?" Soru eki duyulmuyor.
- Önbellekteki iki çekimde de (deneme 0 ve 1), klipte ve mikste, small ve medium ile 6/6 döküm "kahramanla / kahramandan / kahrananla" çıkıyor. Komşu satırlar ("…bir kural mı?", "…şans mı?") temiz.
- Kapanış sorusunun A seçeneği. Ekranda "TEK BİR KAHRAMAN?" yazdığı için MUST değil.
- Düzeltme: aynı metinle yeni çekim, satıra şu tarzı ekle:
  tarz: "Soru sorar gibi söyle; 'kahraman' ile 'mı' arasında çok kısa bir ayrım olsun, 'mı' net ve hafif yükselen tonda."
- Seçim ölçütü: ipucusuz Whisper "kahraman mı" yazmalı.
- Olmazsa metin: "Bir kahramanın cesareti mi?" (n+m birleşmesi yok).

SHOULD 2 — 2:19, B2.1 (satır 36): "Ama haritada bir boşluk var: … Türkiye." Cümle içinde 1,76 sn durak var (eşik 1,2 sn).
- Neden: tts'teki <break 350ms> Gemini'ye "..." olarak gidiyor.
- Düzeltme: tts: "Ama haritada bir boşluk var: Türkiye." (break yok; iki nokta kendi kısa durağını verir), sonra: 0.4 kalsın. 0,5-1,0 sn duraklı bir çekim seç.
- Ya da durak bilinçli kalacaksa paket.dinle'deki "uzun gelirse söyle" notunu bir karara çevir.

SHOULD 3 — paylasim.md'deki bayat paket metinleri (paket alanları; değiştir, `uzun paket` + `teslim` ile yeniden üret):
- (a) Yapay içerik maddesi "Seslendirme yapay zekâ (Cartesia)" diyor, açıklama ise "Google Gemini" diyor. Yeni metin: "Seslendirme yapay zekâ (Google Gemini TTS) ama yalnız anlatıcı ile reklam sloganı ve ürün bilgisi alıntıları; gerçek bir kişinin sesi ya da görüntüsü üretilmedi…"
- (b) Süre maddesi "~30 sn üstünde (11. ve 12. turda yavaşlatılan satırlar)" diyor. Yeni metin: "Süre 10:56: 8-10 dk kararının ~56 sn üstünde (Gemini anlatıcısı Cartesia'dan ~%4 yavaş: +23 sn; 11-12. turda yavaşlatılan satırlar). YouTube için sorun değil; kısaltmak istersen aday: B6.5 Behçet sahnesi."
- (c) Dinleme listesine ekle: "10:15 «Tek bir kahraman mı?» — Whisper soru ekini duymuyor ('kahramanla'): 'mı' duyuluyor mu?"

SHOULD 4 — SRT blok kırımları (yalnız metin; `\n` blok, `¦` blok içi satır ipucu; tts ve önbellek anahtarı değişmez):
- 2:04 (satır 33). Şu anki blok, sesin durduğu yerin ötesine taşıyor:
  metin: "Asıl soruyu ise kimse araştırmamış:\nHamile bir kadın bu ilacı alırsa,¦karnındaki bebeğe ne olur?"
- 8:22 (satır 118). Alıntı iki bloğa bölünüyor; "Bu söz yanlış." alıntının yarısıyla aynı blokta:
  metin: "İnternette sık duyulan bir söz var:\n‘Etkilenmeyen tek iki ülke: Türkiye ve ABD.’\nBu söz yanlış."
- 1:04 (satır 19). "Grünenthal'in | laboratuvarında" tamlaması iki bloğa bölünüyor:
  "1954'te Alman ilaç firması¦Grünenthal'in laboratuvarında\nyeni bir molekül sentezleniyor."
- 9:34 (satır 134). "etkisini | gösteren" bölünüyor:
  "Talidomitin Behçet hastalığındaki¦etkisini gösteren\nönemli bir çalışma Cerrahpaşa'da yapıldı\nve 1998'de yayımlandı."

NICE (her biri yeni TTS ister, getirisi küçük):
- 5:12 / 5:25: FDA iki farklı okunuyor. telaffuz: `FDA: Fe De A` yap; yalnız L76 yeniden çekilir. Kötüyse eskisi kalsın.
- 9:28 (satır 132): "Bu kadarını anlamak bile 60 yıldan uzun sürdü." Videonun kurduğu soru 1961'de, cevap 2018'de: arada 57 yıl var ve 4:37'deki "yarım asırdan fazla" ile çelişiyor. Yeni satır: "Bu kadarını anlamak bile yarım asırdan uzun sürdü."
- 9:12 (satır 128, ham sonu −10,6 dB) ile 2:46 / 9:34 / 4:40 (satır 41 / 134 / 68): ham çekimin sonu sesli kesiliyor. Hepsi doğru dökülüyor; kulakla bak, kesik gelirse yeniden çek.
- 2:24 "Gürünentel" (1:04'te doğru) ile 8:00 / 10:30 "yayınlan-" (tire hilesi tutmuyor): kulakta küçük, ama listede kalsın.
- 1:26 "Oysa … kandaki" (0,92 sn): Gemini'nin dramatik durağı. Kalabilir, ya da tts "Oysa kandaki ilaç düzeyini ölçen yok." için daha sıkı bir çekim seçilir.

## teknik1: 8.5/10

**Puanlar:** Technical/package judge, talidomit-turkiye-uzun (Gemini re-voice, 10:56). The renders and the package files are byte-identical. Measured independently in /tmp/claude-0/-home-user/e1bf52df-8e16-5819-ad96-6f6873ef480c/scratchpad/uzun/talidomit-turkiye/hakem/1/teknik/.

- Container/codec 10/10:
  - MP4 with moov before mdat (faststart).
  - H.264 High L4.0, yuv420p, tagged BT.709 tv range, 1920x1080, SAR 1:1, 30/1 CFR. 19,688 frames = 656.267 s.
  - bframes=0, keyint 60 (max GOP 2 s), CRF 18, about 5.6 Mbps.
  - AAC-LC, 48 kHz stereo, 311 kbps, language tur.
- A/V sync 10/10:
  - Both streams start at 0.000 and the AAC 1024-sample priming is handled by the edit list.
  - Video 656.2667 s, audio 656.266 s (0.7 ms apart).
- Loudness 10/10:
  - ebur128: -14.0 LUFS integrated, true peak -2.5 dBTP, LRA 3.2.
  - Sample peak 0.752. No samples at or above 0.95, no flat tops.
  - DC is about 0. L/R correlation 0.96; the mono sum loses only 0.08 dB.
- Clicks and silence 9.5/10:
  - I scanned all 373 narration silence boundaries (silence ≥ 50 ms, 50 dB under the speech median), comparing the last 20 ms with the 45 ms before, and the first 20 ms with the next 45 ms.
  - No transient was found: no step at a boundary above 0.017 (stem peak 1.92), and the >4 kHz band shows no impulse.
  - The engine's own clip-tail check (`uzun kontrol`) is clean.
  - Only tiny low-frequency breath fragments exist: 8:17.06, about 15 ms at 17 dB under speech, masked by music at -30 dBFS.
  - The mix has no digital-zero run of 5 ms or more and no stretch under -50 dBFS of 1 s or more.
  - At 10:32.65 there is one 1.05 s dip to about -47 dBFS. It is the intended thesis pause (music floor, not zero).
  - Narration pauses over 2 s fall only on chapter cards, at 6:45.8 and 8:03.5 (about 2.0-2.1 s), and in the closing scene.
  - Voice over music/effects: median 17 dB, 10th percentile 7.9 dB. No 1 s speech window is under 3 dB. The bed peaks 2.5 dB over the speech median.
- Picture 10/10:
  - No black segment of 0.3 s or more and no freeze of 2.5 s or more.
  - Frames darker than 45/255 appear only on the three black chapter cards (3:19.6, 6:15.2, 8:40.0). No one-frame flashes.
  - No burned-in watermark (matches `filigran: false`).
- Chapters 9.5/10:
  - 8 chapters, 0:00 first, ascending; the shortest is 43 s.
  - 0:44, 2:14, 3:20, 5:05, 6:16 and 8:40 are rounded up, each lands inside its card 0.3-0.9 s after the card starts, and the narration is silent there.
  - Kapanış 10:11 is rounded down on purpose: speech starts at 10:11.8, and 10:12 would cut "Peki". The cost is 0.6 s of the previous scene's frame.
  - Mid-roll ads at 3:20 and 6:16 sit inside black cards with silent narration.
- SRT 10/10:
  - UTF-8 without BOM, LF line endings, 190 cues in order, no overlaps.
  - At most 2 lines per cue and at most 42 characters per line. Italics are balanced in every cue and Turkish letters are intact.
  - Every speech run of 150 ms or more is covered. Highest reading speed is 19.6 characters/s.
- Metadata limits 9.5/10:
  - Description: 4,739 characters / 4,918 bytes (limit 5,000), no < or >, 3 hashtags.
  - Titles 51, 59 and 68 characters.
  - 21 tags: 304 characters, 308 by YouTube's count.
  - The pinned comment matches the closing question.
  - The Short link resolves: oEmbed shows it public on the Tarihsel Wojak channel with the same title.
- Credits and licences 9.5/10:
  - Every one of the 23 photos/derivatives from outside sources used in video.yaml maps to a row in uzun/talidomit-turkiye/VARLIKLAR.md and to a credit line in the description.
  - No image from img/telifli/ is used. The copyrighted upgrades and the unlicensed character bases are listed for the owner.
- Privacy and secrets 10/10: no keys, tokens, e-mail addresses or home paths in teslim/ or uzun/. The mp4 and telifli/ files are git-ignored.
- Thumbnails 10/10: three 1280x720 JPEGs, 141-193 KB.
- End screen 9/10:
  - The closing scene starts at 10:44.47 and lasts 11.8 s. The top-right is free.
  - The "start at 10:45" instruction is correct; 10:36-10:44 still carries other scenes' top-centre text.
- Package text accuracy 6.5/10: several stale or contradictory owner instructions (see fixes).
- Short package 6.5/10: still valid as a Short package, but it does not point to the long video and is stale against the current pack.py.

**Engel:** None. The video and audio files, the subtitles, the thumbnails, the chapter list and the licence credits are all ready to upload. The only must-fix is a wrong instruction in paylasim.md (the watermark advice in MUST 1). It is fixed by regenerating the package, with no re-render.

**Düzeltmeler:**

MUST

1. The upload checklist contradicts the owner's watermark decision.
   - In teslim/talidomit-turkiye-uzun/paylasim.md the end-screen item says not to use the YouTube Studio channel watermark, because YouTube would put it on top of "the 'tarihselwojak' text in the video".
   - This render has no burned-in watermark: `filigran: false`, and I checked bottom-right crops across the whole video.
   - The owner decided on 15.10 (UZUN_FORMAT §2.8, CLAUDE.md) to use exactly that Studio watermark instead.
   - As written, the owner would publish the video with no branding at all.
   - Fix: in wojak/uzun/paket.py `bitis_maddesi()` (lines ~183-188), make that sentence depend on `z.video.filigran`. When it is false, say: "turn on Customisation > Branding > Video watermark; this video has no burned-in watermark (UZUN_FORMAT §2.8)". Then rerun `python -m wojak uzun paket uzun/talidomit-turkiye` and `uzun teslim`. No re-render is needed.

SHOULD

2. The AI-content item names the wrong voice provider.
   - uzun/talidomit-turkiye/video.yaml `paket.yapay_icerik` (~line 2181) still says "Seslendirme yapay zekâ (Cartesia)".
   - It is Google Gemini now (Charon narrator, Kore for the quotes), as the description already says.
   - The channel has a YouTube violation, so the AI-disclosure note must be accurate. Fix the text and regenerate.

3. Stale `ek_maddeler` in video.yaml:
   - (a) The runtime item says "~30 sn üstünde". The real runtime is 10:56: 56 s over 10:00 and 41 s over the 8:30-10:15 gate in ADIM_ADIM §4.11. It is 23 s longer than the approved 10:33 because of the Gemini re-voice, and the reason given ("11-12. tur" slowdowns) dates from Cartesia. State the real figure and let the owner choose: keep it, or trim B6.5 Behçet.
   - (b) The Short item says "Short'un videosu değişmedi". The Short was re-rendered on 22.10 with the new music and new evidence and is already live (Fb77-MsYmRc).
   - (c) In paket.py, the checklist line "bu açıklamadaki [Short bağlantısı] dolduruldu" should be dropped when `short_url` is set, because the link is already in the description.

4. The Short package teslim/talidomit-turkiye/ (22.10) does not point to the long video.
   - episodes/talidomit-turkiye/episode.yaml has no `uzun_video`, so there is no "▶ Uzun hali:" line and no "İlgili video" checklist item, which UZUN_FORMAT §4 requires.
   - It also predates the 23.10 pack.py change: its YouTube description is still "Olayın tamamı sabit yorumda 👇" instead of the full story text, and its timing note ("en geç 16-17 Ekim") is stale.
   - The Short is already live, so after the long video is published: set `uzun_video: <long URL>`, run `python -m wojak paket episodes/talidomit-turkiye`, then edit the live Short in Studio (description line plus İlgili video). The long package's checklist already lists the Studio steps.

NICE

5. The video bitrate is about 5.6 Mbps (CRF 18), under YouTube's recommended 8 Mbps for 1080p30. Nothing is visible on flat cartoon art; CRF 16 is optional.

6. Optional ear check of short low-level breath fragments at 0:37.3, 1:02.6, 4:55.5 and 8:17.06. They are not clicks by the high-frequency test and are masked by the music.

7. The description is at 4,918/5,000 bytes; leave the 82 bytes of headroom.
