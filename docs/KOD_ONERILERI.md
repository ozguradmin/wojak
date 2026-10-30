# Kod önerileri (açık liste, tekrarsız)

> Oturumlarda bulunan ve düzeltme turunda uygulanamayan kod önerileri burada **tek satır** olarak durur. Yeni öneri
> yoksa eklenir, varsa dokunulmaz (oturum notlarına tekrar yazılmaz). Kaynak: `docs/OGRENILENLER.md`'deki oturum
> notlarının "Kod değişikliği önerileri" listeleri (21-28.10.2026), tekilleştirildi. Yapılan öneri silinir ya da işaretlenir.
> İşaret: **[uygulanıyor 29.10]** = başka bir ajan şu an yazıyor.

## Araçlar ve kurulum

- **[uygulanıyor 29.10]** `tools/commons.py` (`ara`, `bilgi`, `indir`): standart genişlik 330/500/960/1280/1920, `thumbnail_unscaled` yolunu reddet, 429'da geri çekilme, lisans/yazar `action=raw` + `extmetadata`'dan. Her oturumda `/tmp`'de yeniden yazılıyordu.
- **[uygulanıyor 29.10]** `tools/hazirla.sh <özel-depo>`: `/home/user` + bağ, iki deponun varsayılan dalı + pull, pip, font, referans, kısa pytest özeti, müzik kontrolü.
- `tools/`: Internet Archive sayfa indirici (`<id>` + sayfa no → `page_numbers.json` leaf → `page/n<k>_w2000|w4000.jpg`; `djvu.txt` içinde pasaj arama; Commons PDF sayfası `iiurlparam=page<n>-<w>px`).
- `tools/`: gazete kupürü üreticisini genelleştir (metin, kaynak, foto, kâğıt yaşı, manşet fontu, gri/renkli raster, yırtık kenar, eğim, zemin parametreli; şimdilik iki bölümde ayrı `kupur.py`).
- `tools/`: dikey/uzun nesne kanıtını 1080x816'ya (ya da kareye) nesnesiz kenarı uzatıp bulanıklaştırarak tamamlayan yardımcı.
- `tools/`: gölgeli hazır çizimi düz MS-Paint'e çevirip eksik baş konturunu ekleyen yardımcı (`pera-palas-anahtar-1979/chars/uret.py:otelci` kalıbı).
- `tools/`: Commons yıl kategorisinden pul arayan (`Category:<yıl> stamps of Turkey`, `PD-TR` süzgeci) ve müze kategorisindeki nesne + levha fotoğraflarını tek temas sayfasında gösteren yardımcı.
- `tools/bg_ara.py`: Openverse bu ortamda zaman aşımına düşüyor; Commons'a (CC/PD süzgeçli) yedek.
- `tools/wojak_site.py get`: küçük kaynakları (< 700 px) isteğe bağlı 2-3x büyütüp keskinleştiren `--buyut`; indirilen karakterin tam boy önizlemesini kaydet (filigran küçük sayfada görünmüyor).
- `tools/wojak_lib.py` / `wojak_site.py`: dönem süzgeci (ör. `--once 1829` fesli sonuçları gizlesin).
- `tools/wojak_lib.py get`: çıktı `head` ile kesilince BrokenPipeError (zararsız gürültü).

## `check` / `teslim` denetimleri

- **[uygulanıyor 29.10]** `check`: satır sonunda tek kelime kalan replik (greedy kırımın son satırı 1 kelime).
- **[uygulanıyor 29.10]** `check`/`teslim`: sansür izi (`*`, `!`, harf arasında rakam) metinlerde kalınca uyar.
- **[uygulanıyor 29.10]** `check`: kanıt yüksekliği 537-816 px dışında ya da genişlik 1080 değilse uyar.
- **[uygulanıyor 29.10]** `check`: diyalog arka planının doygunluğu (> 0,30) ve kenar Laplace varyansı (hedef ~20, 720 ölçeği) için uyarı ve blur önerisi.
- **[uygulanıyor 29.10]** `check`: başlık son repliğin cevabını veriyor olabilir (anahtar kelime karşılaştırması).
- **[uygulanıyor 29.10]** `teslim`: klasörü yeniden kurarken `RAPOR.md`'yi silmesin.
- `check`: ters köşe sahnesinde telefon boyu (390 px, eşik 40) yüz değişimini ölçüp %0,40 altında uyar.
- `check`: satır kırımı bir özel adı (art arda iki büyük harfli kelime) iki satıra bölüyorsa uyar.
- `check`: başlık soru biçimindeyse ve `cover_scene` ters köşe sahnesiyse uyar (kapak cevabı veriyor).
- `check`: kanıt görselini 390 px'e küçültüp "küçük ayrıntı / soluk" uyarısı (kenar yoğunluğu, manşet yüksekliği).
- `check`/`compose`: başlığı yüksek karakterde (kavuk, sarık, fes) yüzün PNG içindeki konumuna göre boy/kesim önerisi.

## Renderer ve ses

- **[uygulanıyor 29.10]** `wojak/audio.py`: loudnorm TP'yi -9..0 aralığında tut ya da ölçüp doğrusal kazanç uygula; filtre hata verirse sessizce `anull`'a düşme; çıktı LUFS'u ±1 LU dışındaysa `check`/`teslim` uyarsın.
- `wojak/compose.py`: kanıt için `evidence_fill: width` seçeneği (uzun nesnede yan bant olmasın).
- `wojak/render`: render satırındaki süre yanlış (8,5-12,2 sn yazıyor; ffprobe 13,45-13,95); süre ffprobe'dan okunmalı.
- Renderer: yazı bloğu bazı karakterlerde baş üstünden ~80 px yukarıda (hedef 55) (`en-lusitania-warning`).
- `wojak/censor.py`: tarihî metinde sık kelimeler için istisna ya da öneri ("silahdar", "silahsızlandırmak", "bombalamak"; en: "died", "bomb").
- `wojak/config.py`: EN TikTok varsayılan etiketleri (`#mystery #truestory`) yerine konu etiketleri.
- `pack.py`: Instagram metnine `#tarihselwojak #wojak` ekliyordu (12.10 notu); hesap sahibi kararı hashtag yok, hâlâ ekliyorsa kaldır.
- `frames`: eski kare dosyalarını silmiyor (eski kareler yeni sanılabiliyor).

## Bakış kaydı

- **[uygulanıyor 29.10]** `wojak/facing.py` / `yon`: aynı dosya yolu için yeni sha1 kaydederken o yolun eski girdilerini sil (`yon --temizle`); aynı baytlı başka bölüm PNG'sinin `file` alanını değiştirmesin.
- Konsol ajanlarının sistem istemi: `data/karakter_yon.json` yazma listesinde yok ama `teslim` kayıt istiyor; listeye eklenmeli.

## Testler

- `tests/`: sabit `/home/user/wojak` yolu yerine depo kökünü kullan (taze konteynerde bağ yokken `test_short_youtube_aciklamasi_hikayeyi_tasir` düşüyor); talidomit telifli görseline bağlı hashtag testi ortam eksiğinde düşmesin.
- `wojak check`/denetim: kanıt görsellerinde koyu piksel oranı (<15) > %1 ise `[stil]` uyarısı (yarı ton taramada ezik gölge; schliemann-sal-1873 tur 1 MUST'ı).

## Belge düzeltmeleri (eski bilgi taşıyanlar)

- `docs/is_akislari/kisa_reel.js`: CONTEXT'teki okuma listesi (STIL tamamı, INSTAGRAM_ANALIZ, URETIM_REHBERI...) yerine `docs/KISA_REEL_EL_KITABI.md`; `music: kanal` yerine `music: {file: kanal, volume: 0.197}`; Commons "≥ 10 sn" yerine `tools/commons.py`; "Do not commit" yapımcı için güncellenmeli.
- `CLAUDE.md` sert kural 3 ve `docs/ADIM_ADIM.md` §9: Wikimedia "≥ 10 sn" kuralı `tools/commons.py` ile güncellenmeli.
- `docs/ADIM_ADIM.md` §3 ve §8: "kısa reel ~1 iş günü" (gerçekleşen 25-50 dk), §1 "71 test" (şimdi 99), §6 Telegram teslimi (yerine yayın botu).
- `docs/OGRENILENLER.md` §5 madde 6 ve §6.2 "Hızlı başlangıç" 8, 10, 13: eski müzik dosyası, kupür varsayılanı, `/mnt/session/outputs` teslimi; el kitabı geçerli.
- `tools/wojak_lib.py get`: `--yon` seçeneği var ama yazmıyor ("bakış yönü kayıtlı değil" uyarısı); `get` sonrası `python -m wojak yon` otomatik sorulsun ya da `--yon` gerçekten kaydetsin (en-dancing-plague-1518).
- `wojak/config.py`: TR TikTok varsayılan etiketleri (`#olay #gizem`) gizem olmayan konulara da ekleniyor; bölümün `hashtags`ından türet ya da yaml ile ezilebilir yap (30.10, uluburun-kulakli-biskuvi).
- `tools/commons.py`: LoC FSA/OWI renkli koleksiyon araması (`loc.gov/collections/fsa-owi-color-photographs/?q=&fo=json`) ve master TIFF indirme eklensin; renkli 1940'lar arka planı her seferinde elle aranıyor (30.10, en-bat-bomb).
