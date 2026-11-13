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
- `tests/test_muzik.py` (`test_bolumde_hava_adi`, `test_onaysiz_hava_uyarir`): müzik sırası denetimi gerçek depodaki önceki tr bölümüne bakıyor; önceki bölüm `kanal` çaldıysa testlere "müzik sırası" uyarısı giriyor ve `hazirla.sh` 4 FAIL veriyor (13.11, haydarpasa-patlamasi-1917); testte sıra denetimini monkeypatch'le ya da geçici bölümü sıradan muaf tut.

## Belge düzeltmeleri (eski bilgi taşıyanlar)

- `docs/is_akislari/kisa_reel.js`: CONTEXT'teki okuma listesi (STIL tamamı, INSTAGRAM_ANALIZ, URETIM_REHBERI...) yerine `docs/KISA_REEL_EL_KITABI.md`; `music: kanal` yerine `music: {file: kanal, volume: 0.197}`; Commons "≥ 10 sn" yerine `tools/commons.py`; "Do not commit" yapımcı için güncellenmeli.
- `CLAUDE.md` sert kural 3 ve `docs/ADIM_ADIM.md` §9: Wikimedia "≥ 10 sn" kuralı `tools/commons.py` ile güncellenmeli.
- `docs/ADIM_ADIM.md` §3 ve §8: "kısa reel ~1 iş günü" (gerçekleşen 25-50 dk), §1 "71 test" (şimdi 99), §6 Telegram teslimi (yerine yayın botu).
- `docs/OGRENILENLER.md` §5 madde 6 ve §6.2 "Hızlı başlangıç" 8, 10, 13: eski müzik dosyası, kupür varsayılanı, `/mnt/session/outputs` teslimi; el kitabı geçerli.
- `tools/wojak_lib.py get`: `--yon` seçeneği var ama yazmıyor ("bakış yönü kayıtlı değil" uyarısı); `get` sonrası `python -m wojak yon` otomatik sorulsun ya da `--yon` gerçekten kaydetsin (en-dancing-plague-1518).
- `wojak/config.py`: TR TikTok varsayılan etiketleri (`#olay #gizem`) gizem olmayan konulara da ekleniyor; bölümün `hashtags`ından türet ya da yaml ile ezilebilir yap (30.10, uluburun-kulakli-biskuvi).
- `tools/commons.py`: LoC FSA/OWI renkli koleksiyon araması (`loc.gov/collections/fsa-owi-color-photographs/?q=&fo=json`) ve master TIFF indirme eklensin; renkli 1940'lar arka planı her seferinde elle aranıyor (30.10, en-bat-bomb).
- `wojak/text.py` / `check`: iki satıra sığmayan replik (ör. 37 karakterlik ilk satır) `frames`/`render`'da `RuntimeError: raqm_layout() failed` ile çöküyor, `check` uyarmıyor; `check` satır genişliğini ölçüp "satır sığmıyor, kısalt" desin (31.10, hope-elmasi-posta-1958).
- `tools/commons.py ara`: dosya adını ~60 karakterde kesiyor; uzun Commons adlarında `indir`/`bilgi` için tam ad yazdırılsın (`--tam`) (31.10, sultanahmet-alti-minare).
- `tools/wojak_site.py sheet`: `a|b|c` biçimli çok parçalı sorgu bazı kelime kombinasyonlarında "sonuç yok" döner ("gentleman_wojak|smug_suit..."); tek tek sorgu çalışır; alt çizgi/boşluk normalizasyonu ve | desteği tutarlı olsun (31.10, en-lustig-eiffel-tower).
- `wojak/config.py`: EN TikTok varsayılan etiketleri (`#mystery`) gizem olmayan belgeli konulara da ekleniyor (izleyici hakem SHOULD, en-apollo-moon-disaster); bölümün `hashtags`ından türet ya da yaml ile ezilebilir yap (TR için aynı öneri yukarıda var).
- `tools/wojak_site.py get --out-dir` ve `tools/wojak_lib.py get --out-dir` /tmp gibi repo dışı yolları `data/karakter_yon.json`'a yazıyor; repo dışı yolu kaydetmesin ya da `yon` listesi var olmayan dosyaları ayıklasın (01.11, en-booth-saves-lincoln-son).
- `tools/wojak_site.py get`: `--out-dir` verilmezse PNG'yi `assets/characters/` altına koyup `data/karakter_yon.json`'a "front" girdisi yazıyor; aday denemelerinde repo kirleniyor (git checkout/clean gerekiyor). Varsayılan hedef `/tmp` ya da kaydı yalnız `--yon` verilince yazsın (01.11, en-roosevelt-bullet-speech).
- `check`: arka plan ölçüsünü (Laplace, doygunluk, parlaklık) uyarı olmasa da tek satır yazdırsın ve "blur X için Laplace ~20" önerisini versin; blur seçimi için `denetim.arka_plan_olcu` elle taranıyor (02.11, dumlupinar-denizaltisi-1953).
- `wojak render`: konsol satırı "video -> ... (7.4 sn)" gerçek süreyi (ffprobe 13,95 sn) yanlış basıyor; ffprobe ile okunan süreyi yazsın (02.11, en-arkhipov-b59).
- `tools/commons.py indir --genislik 1920`: özgün dosya 1920'den darsa (ör. 1678x923) özgün yerine 1280 küçük resmi indiriyor; istenen genişlik özgünü aşınca md5 özgün yolunu (429 geri çekilmeli) denesin (03.11, yilanli-sutun-tilsimi).
- `wojak render`: episode.yaml ayrıştırma hatasında (ParserError) sessizce eski mp4'ü bırakıyor ve çıkış koduyla bildirmiyor; hatada dur ve kırmızı uyarı yaz, `teslim` da yaml'ı mp4'ten yeniyse reddetsin (03.11, en-acoustic-kitty).
- `wojak/censor.py`: TR doğal ölüm kalıplarını ("ölümüne dek", "ölümünden sonra", "öldükten sonra") yıldızlama ya da `check` "doğal ölüm sansürlendi, tarih aralığıyla yaz" diye uyarsın (04.11, meryem-ana-evi-1891).
- `wojak` TikTok/hashtag profili (`en`): araç `#mystery #truestory` ekliyor; facia/belgeli olay konularında uymuyor (en-boston-molasses-flood, 04.11); konu etiketine göre ya da yalnız bölüm `hashtags:` ile sınırla.
- `tools/commons.py indir`: özgün çözünürlük seçeneği (`--ozgun`, md5 yolu + 429 geri çekilme) yok; 1920'den büyük kırpım için elle curl gerekti (05.11, cevri-kalfa-1808).
- `wojak/pack.py`: gündem bölümünde (`gundem: true`) TR varsayılan TikTok etiketleri (#gizem #keşfet #olay) hiç eklenmesin; `caption` hiçbir metne girmediği için `check` 'canlandırma notu pinned_comment'te yok' diye uyarsın (05.11, gündem önizlemesi).
- `data/karakter_yon.json`: yeniden üretilen PNG'nin eski sha girdileri birikiyor; `wojak yon` aynı dosya yolunun eski sha girdisini silsin (05.11, en-cadaver-synod).
- `wojak/censor.py`: TR'de "ölü/ölüler" arkeolojik gömü bağlamında da yıldızlanıyor ("*lüler"); bölüm yaml'ında `sansur_haric: [ölü]` gibi bilinçli istisna ya da `check`'te "sansür kelimeyi bozdu, eşanlamlı seç" uyarısı (06.11, catalhoyuk-sekinin-alti).
- `tools/hazirla.sh`: pip adımı gereken modüller zaten içe aktarılabiliyorsa atlansın, `faster-whisper` yalnız uzun video bayrağıyla kurulsun; 08.11'de ilk kurulum ~15 dk sürdü, ajanın 5 dk komut sınırını aştı (hayirsizada-kopekleri-1910).
- `tools/commons.py ara`: başlıkları 60 karakterde kesiyor, tam dosya adı olmadan `bilgi/indir` çalışmıyor; araştırmacı ~15 yerine 30 çağrı harcadı (08.11, en-eiffel-lift-1940 avı): `ara` tam başlığı (ya da `--tam`) yazdırsın.
- `wojak yon`: başka bölümden birebir kopyalanan PNG (aynı sha) kaydedilince mevcut girdinin `file` alanı yeni yolla üzerine yazılıyor (09.11, yeralti-camii-karakoy: hezarfen_emin girdisi); sha zaten kayıtlı ve yön aynıysa dokunmasın.
- `wojak/denetim.py` kart kuralı (`sonra$`): TR'de doğal ileri zaman "Ertesi gün" `[stil]` uyarısı alıyor, "Bir gün sonra"ya zorlanınca takipçi hakem "yapay" diye SHOULD verdi; regex "Ertesi gün|Ertesi sabah|Ertesi akşam"ı da kabul etsin (10.11, sokullu-son-dua-1579).
- `tools/gundem.py`: BBC Türkçe ve DW Türkçe RSS bu ortamdan 403 veriyor (11.11, alanya-adam-atacagi); başarısız akışı tek satır özetle ve oturumlar arası önbellekle atla.
- `tools/commons.py ham_lisans`: Geograph kaynaklı dosyalarda ham sayfa yalnız `{{Geograph from structured data}}` içerir (lisans yapısal veride), `ham_lisans` boş döner ve araştırmacı "doğrulanamadı" der (12.11, en-wojtek-soldier-bear); bu şablonu görünce API `LicenseShortName`i kabul edip "SDC" notu düşsün.
- `python -m wojak new <id>`: bölüm klasörü araştırmacı `img/` açtığı için varsa "zaten var" deyip şablonu yazmıyor (12.11, en-wojtek-soldier-bear); klasör var ama `episode.yaml` yoksa şablonu yazsın.
