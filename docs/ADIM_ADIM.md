# Adım adım üretim: projeyi hiç bilmeyen biri için

> Bu belge tek giriş noktasıdır. Okuyan kişi projeyi hiç bilmese de buradaki sırayı izleyerek onaylı videolar kadar,
> hatta daha iyi bir kısa reel ve uzun YouTube videosu çıkarabilmelidir. Burada **ne, hangi sırayla, hangi komutla**
> yazar. **Neden** ve ölçüler başka belgelerde: kısa reel ölçüleri [`STIL.md`](STIL.md), dersler ve hata türleri
> [`OGRENILENLER.md`](OGRENILENLER.md), uzun format kararları [`UZUN_FORMAT.md`](UZUN_FORMAT.md), motor başvurusu
> [`UZUN_MOTOR.md`](UZUN_MOTOR.md), yayın takvimi ve sıradaki işler [`YAYIN_PLANI.md`](YAYIN_PLANI.md), ajan istemleri
> [`is_akislari/`](is_akislari/README.md).
>
> Kalite çıtası iki örnekle tanımlıdır: dört onaylı kısa reel (`teslim/van-depremi-azra-bebek`,
> `canakkale-kayip-tabur`, `kiz-kulesi-efsanesi`, `talidomit-turkiye`) ve onaylı ilk uzun video
> (`uzun/talidomit-turkiye`, 15.10.2026: "baya iyi olmuş beğendim"). Yeni iş bunların altına düşmez.

---

## 0. İlk gün: okuma sırası (yaklaşık 2 saat)

1. [`../CLAUDE.md`](../CLAUDE.md): sert kurallar (gizli anahtar, herkese açık repo, mahremiyet, git).
   **Görseller:** yapay zekâ ile görsel üretilmez; arka plan ve kanıt gerçek fotoğraf/belge (ya da kendi düz
   çizimimiz), karakterler hazır wojak çizimleri.
2. [`OGRENILENLER.md`](OGRENILENLER.md) en üstteki **hesap sahibinin geri bildirimi** tablosu. Hakemlerden önce gelir.
3. Kısa reel yapacaksan [`STIL.md`](STIL.md) baştan sona (§0 altın kurallar, §14 gerçek senaryo örnekleri, §15 yapma
   listesi). Uzun video yapacaksan [`UZUN_FORMAT.md`](UZUN_FORMAT.md), sonra [`UZUN_MOTOR.md`](UZUN_MOTOR.md) §1-3.
4. Onaylı örnekleri izle: `teslim/<id>/` (kısa) ve `uzun/talidomit-turkiye/video.yaml` (uzun; her satırın yorumu hangi
   turda neden değiştiğini anlatır, en iyi ders kitabı budur).

## 1. Ortam kurulumu

```bash
pip install -r requirements.txt faster-whisper     # Pillow, numpy, PyYAML, requests + konuşma tanıma (Whisper QA)
pip install py7zr multivolumefile                  # yalnız Telegram yedek yolu (7-Zip parçaları) için
ffmpeg -hide_banner -filters | grep -E "rubberband|loudnorm|ebur128"   # üçü de olmalı
cd tools/telegram && npm install && cd -           # 50 MB üstü tek parça Telegram gönderimi (node 18+)
python -m pytest tests -q                          # 71 test geçmeli (15.10.2026)
```

**Gizli anahtarlar** yalnız ortam değişkeninde ya da `~/.config/wojak/secrets.env` (repo dışı, `chmod 600`) içinde durur;
kod `wojak.config.load_secrets()` ile okur. Hiçbir dosyaya, loga, komut satırına yazılmaz. Gerekenler (yalnız adları):

| Anahtar | Ne için |
|---|---|
| `CARTESIA_API_KEY`, `_2`, `_3` … `_9` | Uzun video TTS (HTTP 402 kota dolunca sıradakine geçer). ElevenLabs gelince yenisi eklenir (YAYIN_PLANI §4) |
| `TELEGRAM_BOT_TOKEN`, `TELEGRAM_CHAT_ID` | Teslim (Bot API, ≤ 49 MB) |
| `TELEGRAM_API_ID`, `TELEGRAM_API_HASH` | 50 MB üstü tek parça (MTProto); oturum `~/.config/wojak/telegram_gramjs.session` |
| `SOL_API_KEY` | Yapay zekâ görsel üretimi: **kullanılmıyor** (hesap sahibi 16.10: gerçek görseller ve hazır wojak'lar daha iyi) |
| `IG_*` çerezleri | Yalnız `tools/ig_fetch.py` (orijinal reel indirme/analiz) |

Bulut oturumunda bu dosya konteynerle birlikte silinir: kalıcılık için anahtarlar **cloud environment → environment
variables** bölümüne eklenir (GEREKENLER.md §1).

**Yeni bulut oturumunda ilk iş (özel dosyalar):** lisanslı font ve ölçülen orijinal reel'ler hesap sahibinin Telegram
sohbetinde bot mesajı olarak durur (21.10). Hesap sahibi `TELEGRAM_BOT_TOKEN`, `TELEGRAM_CHAT_ID` (ve büyük dosya için
`TELEGRAM_API_ID`, `TELEGRAM_API_HASH`) değişkenlerini cloud environment ayarlarına ekler; dosya kimliklerini (file_id)
yeni sohbetin isteminde verir. Sonra:

```bash
pip install -q py7zr multivolumefile
python tools/ozel_indir.py '<istemdeki JSON>'      # -> assets/fonts/ozel/*.otf + referans/*.mp4 (75 reel)
```

**Repoda olmayan ama gereken üç yerel varlık** (herkese açık repoya girmez, konteyner sıfırlanınca kaybolur; hesap
sahibinde özel bir yedeği bulunmalı):

| Yol | Ne | Yoksa ne olur / nasıl geri gelir |
|---|---|---|
| `assets/fonts/ozel/AvenirLTStd-BoldItalic-TR.otf` | Kanalın replik yazısı (lisanslı) | Poppins'e düşer, kısa reel "kanal değil" görünür (STIL §5). Lisanslı dosya yedekten konur |
| `assets/music/ozel/kanal_orijinal_ses.m4a` | Kısa reel'lerin imza "orijinal ses"i (Do minör vals, 13,75 sn) | Sentez yedek `imza_gece_vals.mp3` çalar. Bir orijinal reel'in sesinden yeniden çıkarılabilir (STIL §10) |
| `referans/*.mp4` | Ölçülen altın dönem reel'leri (hakemlerin kıyas kaynağı) | `python tools/ig_fetch.py --download 30` (IG çerezi gerekir) |

## 2. Konu seçimi

1. Takvim ve sıra: [`YAYIN_PLANI.md`](YAYIN_PLANI.md). Her konu üç çıktıdır: uzun YouTube videosu + aynı konunun kısası
   (YouTube Shorts + Instagram Reels). Her konu uzun videoyu kaldırmaz; bkz. YAYIN_PLANI §2.
2. Beş soruluk filtre: [`URETIM_REHBERI.md`](URETIM_REHBERI.md) §1 ("Ne?!" dedirtiyor mu, kaynağı var mı, Türkiye
   bağlantısı, gerçek görsel, daha önce yapıldı mı). Havuz: [`KONU_HAVUZU.md`](KONU_HAVUZU.md).
3. Güncel olaysa önce [`GUNDEM.md`](GUNDEM.md) §5 kontrol listesi ve §7 hukuki kırmızı çizgiler; hız önemli (1-6 gün).
4. Uzun video için ek soru: **8-10 dakikayı şişirmeden dolduracak** kronoloji, kişi ve ters köşe var mı? Yoksa yalnız kısa.

## 3. Kısa reel (14 sn): adım adım

Süre: oturmuş akışla **yaklaşık bir iş günü** (araştırma ~2 sa, görsel avı ~2 sa, üretim + 3 hakem turu ~2-3 sa).
Çok ajanlı yürütme: [`is_akislari/kisa_reel.js`](is_akislari/kisa_reel.js). Elle yürütürken aynı sıra:

| # | Adım | Komut / çıktı | Geçiş koşulu |
|---|---|---|---|
| 1 | **Olgu araştırması** (scratchpad'de) | `olgular.md`: olgu tablosu (güven düzeyi + en az 2 bağımsız kaynak), kaynak soy ağacı, tartışmalı noktalar + güvenli ifade, dramatizasyon sınırları, 150-250 kelimelik hikâye taslağı | Her ekran iddiası tabloda; tartışmalı olan "anlatılana göre" |
| 2 | **Görsel avı** | `gorseller.md`: 2-3 kanıt (sonda; en güçlüsü son kare), 1 gerçek renkli arka plan (3 aday), 2 hazır kıyafetli karakter + ters köşe yüz varyantı yolu; lisanslar | Her görsele bakıldı (temas sayfası); karakterler düz MS-Paint wojak |
| 3 | **Bölümü aç** | `python -m wojak new <id>` → `episodes/<id>/episode.yaml` | |
| 4 | **Karakterler** | `tools/wojak_site.py` / `tools/wojak_lib.py` `search → sheet → get --out-dir episodes/<id>/chars`; yüz varyantı `assets/kit/*` ya da `tools/kit_varyant.py`; her PNG'ye bak ve DOSYANIN baktığı yönü kaydet: `python -m wojak yon <png> --yon sag\|sol\|on` (`faces:` yazma); render sonrası `python -m wojak bakis episodes/<id>` | `bakis.jpg`'de A solda sağa, B sağda sola bakıyor; varyant telefonda okunuyor |
| 5 | **Senaryo** (`episode.yaml`) | STIL §2-§5: 13,5-14 sn, 0,5 sn ızgarası, diyalog 2-3 sn, isteğe bağlı tek ara kart 1,5 sn, kanıt sonda 2-3 × 1,5 sn; replik 1-11 kelime, şimdiki zaman, nokta/üç nokta yok; ters köşe = aynı karakter, aynı kutu, yüz varyantı. `title`, `pinned_comment`, `sources`, `credits`, `telif_notu`, `ek_maddeler`, `cover_scene`, `uzun_video` | |
| 6 | **Denetim** | `python -m wojak check episodes/<id>` | Hiç `[stil]` uyarısı yok |
| 7 | **Karelere bak** | `python -m wojak frames episodes/<id>` → `out/<id>/kareler/` | Yazı yüzü kapatmıyor; yüzler temiz; arka plan doğal |
| 8 | **Render + teslim klasörü** | `python -m wojak render episodes/<id>` → `python -m wojak teslim episodes/<id>` | `teslim/<id>/` dolu |
| 9 | **Yan yana** | Bizim kareler (0,5 / 3 / 6 / 9 / 11,5 / 13 sn) + 2 orijinal aynı ölçekte tek sayfada; yüzlerin 1:1 kırpımı | Dürüstçe bakıldı |
| 10 | **İki bağımsız hakem** (paralel, dosyaya dokunmaz) | Görsel sadakat (orijinallerle kare kare) + Türk takipçi/senaryo/olgu (kaynak URL'leri açarak) | |
| 11 | **Düzeltme döngüsü** | Engel + MUST, sonra SHOULD; çelişkide orijinaller; `wojak/`, `tools/` düzenlenmez | **İki hakem ≥ 8 ve MUST yok** (genelde 2-4 tur) |
| 12 | **Kendi son kontrolün** | [`OGRENILENLER.md`](OGRENILENLER.md) §4 listesi tek tek | Bilinen kusur yok ya da açıkça yazıldı |
| 13 | **Teslim** | §6 | Hesap sahibi "onay" der |

## 4. Uzun video (8-10 dk): adım adım

Süre hedefi: motor oturduğu için **1,5-2,5 gün** (ilk video motor yapımıyla birlikte 12-15.10 arası 14 tur sürdü).
Çok ajanlı yürütme: [`is_akislari/uzun_video.js`](is_akislari/uzun_video.js). Sıra:

| # | Adım | Ne yapılır | Geçiş koşulu |
|---|---|---|---|
| 1 | **Derin araştırma** | Kısa sürümün `olgular.md`'sinden başla; kronoloji, kişiler, sayı aralıkları, Türkiye kısmı, bugün/ters köşe; görsel adayları lisanslı; anlatı vuruşları (kanca, 4-6 bölüm, açık döngüler, doruk, ters köşe, kapanış sorusu) | Her olgu ≥ 2 kaynak |
| 2 | **Senaryo v1** | 1.200-1.350 kelime; her cümle çiftine görsel vuruş (sahne tipi); ikinci ses alıntıları `[AYLIN]`; telaffuz riskleri işaretli | En geç 4-6 sn'de bir yeni görüntü; karakter payı ≥ %50 |
| 3 | **İki eleştirmen** (paralel) | İzlenme editörü (ilk 30 sn, tempo, başlık/küçük resim önerisi) + Türkçe anlatım/olgu editörü | |
| 4 | **Senaryo v2** | MUST'lar + SHOULD'lar; 3 başlık, 3 küçük resim, bölüm listesi, açıklama, sabit yorum, etiketler, varlık listesi | Çelişkide olgu > saygı > izlenme |
| 5 | **Karakter ve varlıklar** | Önce onaylı karakterler (`uzun/talidomit-turkiye/chars/*_v2_*`, `assets/kit/`); yoksa **hazır kıyafetli** wojak bul; yalnız gereken yüz varyantları (OGRENILENLER §7.1, 9-13. tur kuralları); bakış kaydı; arka planlar (gerçek foto ya da kendi düz çizimimiz); `VARLIKLAR.md` lisans tablosu | 1:1 ve telefon boyunda temiz; her görsel en çok 2 çekimde |
| 6 | **Motor ihtiyacı** | Senaryonun istediği ama motorda olmayan görsel varsa ekle (test + demo + UZUN_MOTOR.md) | `python -m pytest tests -q` geçer |
| 7 | **`video.yaml`** | `cp -r uzun/_sablon uzun/<id>`; her satır, ses, olay, efekt; `telaffuz`; kanca (logo/müzik yok) → imza → bölüm kartları (`kart_bindirme`) → `kapanis` | |
| 8 | **Denetim** | `python -m wojak uzun kontrol uzun/<id>` | **Her uyarı giderildi** (hareket, bölüm, altyazı, çakışma, zıplama, kadraj dışı, yüz örtme, kayıtsız bakış) |
| 9 | **Seslendirme** | `python -m wojak uzun seslendir uzun/<id> --qa` | Whisper "KONTROL ET" yok ya da dinleme listesinde gerekçeli. Zor satıra 2-4 çekim, iki Whisper çözümüyle seç; okunmayan kelimede eş anlamlı + ekranda doğru yazım |
| 10 | **Ön izleme ve bakış** | `python -m wojak uzun onizle uzun/<id>` (aralık: `--bas 1:10 --bit 2:00`); `uzun kare --t ...`; `python tools/uzun_animasyon_denetimi.py kareler/oge/rapor/seri` | Her işaretli an tam çözünürlükte görüldü; **yüz boyu kuralı** (§5) |
| 11 | **Render ve paket** | `uzun render` → `uzun kucukresim` → `uzun paket` → `uzun teslim` | Süre 8:30-10:15, -14 LUFS / ≤ -1 dBTP, A/V 0, tık taraması temiz, bölüm damgaları geçerli (0:00, ≥ 3, ≥ 10 sn, yukarı yuvarlı), SRT ≤ 42 karakter |
| 12 | **Dört bağımsız hakem** (paralel) | İzlenme/görsel, karakter/animasyon (30 fps), Türkçe/olgu (Whisper + kaynaklar), teknik/paket | |
| 13 | **Düzeltme döngüsü** | Engel + MUST → SHOULD; motor düzeltmesi serbest; yalnız değişen satır yeniden seslendirilir; her düzeltme kare şeridiyle doğrulanır; turun dersleri OGRENILENLER §7.1'e | **Dört hakem ≥ 8, engel yok** |
| 14 | **Kendi son kontrolün** | §5 listesi | |
| 15 | **Teslim** | §6 (473 MB'lık video Telegram'dan tek parça gitti) | Hesap sahibi onayı |

## 5. Teslimden önce kendi gözünle (hakemler 8 verse bile)

Hesap sahibinin kuralı: **bilinen bir kusurla teslim yok; varsa açıkça yazılır.** Kısa reel için
[`OGRENILENLER.md`](OGRENILENLER.md) §4 listesi. Uzun video için ek olarak:

- [ ] **Yüz boyu:** her karakterin ekrandaki etkin boyu = `boy` × kamera `zoom` (en büyük değer) × `yakin` ≤ **0,80**
      (rahat aralık 0,55-0,75). Bilinçli dramatik yakın plan en çok 0,88, videoda en fazla 1-2 kez; baş tepesi ve çene
      kadrajın içinde. Hazır kıyafetli "baş-omuz" çizimlerde baş PNG'nin daha büyük kısmıdır: aynı `boy` daha büyük yüz
      verir (UZUN_FORMAT §2).
- [ ] Karakterler içeri bakıyor; kesmede aynı karakter aynı yer/boyda ya da geçiş bilinçli; çapraz geçişte çift karakter yok.
- [ ] Hiçbir yazı/damga/etiket yüze, başka yazıya ya da fotoğraf atfına binmiyor; kadraj dışına taşmıyor.
- [ ] Damga ve vurgu en az 1,2 sn okunur; doruk bir karakter sahnesi; kanca ilk 15 sn'de bir wojak gösteriyor.
- [ ] Koyu kareler telefonda kapkara değil (ortalama ≥ 45/255, bilinçli düşüşler hariç); koyudan açığa flaş yok.
- [ ] Sayaçlar geri okumuyor, her değer ≥ 0,6 sn oturuyor; zaman göstergesi ileri akıyor.
- [ ] Ses: tık yok (anlatımın sıfıra inip çıktığı her yer), efekt tepesi konuşma medyanının en çok +2-3 dB üstü, dijital sıfır sessizlik yok.
- [ ] Küçük resim 168x94'te okunur, en çok 3 öğe; başlık "AI slop" değil.
- [ ] Paket: açıklamada kaynaklar ve CC atıfları, telifli görseller hesap sahibine listeli, dinleme listesi zaman damgalı, Short'a "İlgili video" talimatı.

## 6. Teslim ve hesap sahibine gönderim

```bash
python -m wojak teslim episodes/<id>               # kısa → teslim/<id>/ (video, kapak, paylasim.md, metinler/)
python -m wojak uzun teslim uzun/<id>              # uzun → teslim/<id>-uzun/ (video, .srt, küçük resimler, paylasim.md)
python tools/telegram_gonder.py --mesaj "<kısa özet>"
python tools/telegram_gonder.py teslim/<id>-uzun/<id>-uzun.mp4 teslim/<id>-uzun/kucukresim_*.jpg \
       teslim/<id>-uzun/paylasim.md teslim/<id>-uzun/<id>-uzun.srt --aciklama "..."
```

- 49 MB altı Bot API ile gider; üstü `TELEGRAM_API_ID/HASH` varsa **tek parça** (MTProto, WSS üzerinden; ≤ 2 GB), yoksa
  7-Zip parçaları. Sohbete doğrudan dosya gönderme sınırı 30 MB (ön izleme gerekiyorsa 720p iki geçişli ~27 MB).
- Sohbet mesajında: başlık seçenekleri, **lisans kararı bekleyen telifli görseller** (karar hesap sahibinin), dinleme
  listesi, Hidden Words listesi (yalnız sohbette, dosyaya yazılmaz), bilinen kusurlar.
- `teslim/` altındaki dosyalar elle düzenlenmez; değişiklik `episode.yaml` / `video.yaml`'da yapılıp yeniden üretilir.
- **Commit:** `git status` ile videonun (`*.mp4`), `img/telifli/`, `assets/*/ozel/`, `referans/` girmediğini doğrula; Türkçe
  tek satır konu ("... iki hakemden 8/8"), oturumun atıf satırları; oturumun dalına push. PR yalnız istenirse.

## 7. Hesap sahibinin notu gelince

1. Notu [`OGRENILENLER.md`](OGRENILENLER.md) en üstteki tabloya **tarihli** satır olarak yaz (ne dedi → bundan sonra kural).
2. Kalıcı tercihse [`../CLAUDE.md`](../CLAUDE.md) "standing preferences" listesine de ekle; ilgili belgeyi (STIL, UZUN_FORMAT,
   şablon `video.yaml`, iş akışı istemleri) güncelle ki bir sonraki üretim kendiliğinden uysun.
3. Düzeltmeyi yap, aynı hakem döngüsünden geçir, yeniden teslim et.

## 8. Bütçe ve zaman

| Kalem | Ölçülen (talidomit) | Not |
|---|---|---|
| Uzun anlatım metni | ~8.600 karakter / 10 dk | Düzeltmelerle ~11-13 bin; ses testleri ayrıca ~6 bin |
| Cartesia anahtarı | Bir anahtarın kotası tek videoya yetmedi | Kota dolunca 402 → sıradaki anahtar; ElevenLabs'e geçilecek |
| Kısa reel | ~1 iş günü | Hakem turu ~30-40 dk |
| Uzun video | Hedef 1,5-2,5 gün | Son render (10:33, 18.987 kare, 3 işçi): ~13,5 dk görüntü + ~4 dk ses = **~17,5 dk** (`olcum.json`); hakem turu ~1-1,5 sa |
| Telegram | 473 MB tek parça | Yükleme birkaç dakika |

## 9. Sık sorunlar ve çözümleri

| Belirti | Neden | Çözüm |
|---|---|---|
| TTS `HTTP 402 quota_exceeded` | Cartesia anahtar kotası | Yeni anahtar `CARTESIA_API_KEY_<n>`; motor kendisi geçer |
| Wikimedia `HTTP 429` | Hız sınırı | İstekler arası ≥ 10 sn; kategori sayfası; genel tarayıcı kimliği |
| Videoda 2 karelik ses-görüntü kayması | B-kareleri ve edit list | `libx264 -bf 0`, A/V başlangıcı 0 (renderer'da var) |
| Seste tık | Rubberband klip sonu / `<break>` kenarı sönümsüz | Motor her klibi söndürür; ses onarımında son 20 ms / önceki 45 ms ölç |
| Whisper isim bölüyor ("Tali Domit") | Tanıyıcının dil modeli | Kulak karar verir; gerekirse kelimeyi değiştir, doğru yazım ekranda |
| Telegram 50 MB üstü reddediyor | Bot API sınırı | `TELEGRAM_API_ID/HASH` + `tools/telegram` (`npm install`); düz MTProto vekilden geçmez, WSS kullanılır |
| Python paketi (pyaes) derlenmiyor | Tekerlek yok | sdist'ten elle `site-packages`'a |
| Oturum sınırı iş akışını kesti | Kullanım sınırı / konteyner | Aynı oturumda `resumeFromRunId`; biten ajanlar önbellekten |
| `teslim` "KONTROL ET" yüzünden reddediyor | Whisper uyarısı | Satırı düzelt; bilinçliyse dinleme listesine yaz ve `--zorla` |
| Karakter kadrajda yanlış yöne dönüyor | Bakış kaydı yok (yeni/değişen PNG) | `python -m wojak yon <png> --yon ...` (kayıt sha1 ile) |
