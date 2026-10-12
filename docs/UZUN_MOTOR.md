# Uzun format motoru (`wojak/uzun/`)

> YouTube için 16:9, 8-10 dakikalık anlatımlı videoları tek bir YAML dosyasından üretir. Kararların gerekçesi:
> [`UZUN_FORMAT.md`](UZUN_FORMAT.md). Kısa reel hattı (`wojak/*.py`, `episodes/`) bundan etkilenmez.
> Açıklamalı şablon: [`uzun/_sablon/video.yaml`](../uzun/_sablon/video.yaml). Çalışan örnek: [`uzun/demo/`](../uzun/demo/video.yaml).

## 1. Akış

```bash
cp -r uzun/_sablon uzun/<id>                       # id'yi düzelt, görselleri uzun/<id>/img/ (telifliler img/telifli/)
python -m wojak uzun kontrol    uzun/<id>          # zaman çizelgesi, hareket/bölüm/altyazı denetimi (ses yoksa tahmini süre)
python -m wojak uzun seslendir  uzun/<id> --qa     # Cartesia TTS + Whisper isim denetimi (--yenile 1: başarısızı 1 kez yeniden üret)
python -m wojak uzun onizle     uzun/<id>          # 960x540 hızlı ön izleme; --bas 2:10 --bit 3:00 ile yalnız bir aralık
python -m wojak uzun kare       uzun/<id> --t 1:05 --t 2:30   # tek kareler (PNG)
python -m wojak uzun render     uzun/<id>          # out/<id>/<id>.mp4 (+ .srt, anlatım izi, olcum.json, paylasim.md)
python -m wojak uzun kucukresim uzun/<id>          # out/<id>/kucukresim_*.jpg (1280x720)
python -m wojak uzun teslim     uzun/<id>          # teslim/<id>-uzun/: video (git'e girmez), küçük resimler, paylasim.md, .srt
```

Gizli anahtar: `CARTESIA_API_KEY` ortamdan ya da `~/.config/wojak/secrets.env`'den (`wojak.config.load_secrets`) okunur;
hiçbir dosyaya, loga, hata mesajına yazılmaz. HTTP isteklerinde genel tarayıcı kimliği kullanılır.

## 2. Mimari

| Modül | İş |
|---|---|
| `spec.py` | YAML -> `Video` / `Bolum` / `Sahne` / `Satir` / `Olay` / `Sfx`; bilinmeyen anahtar, yanlış satır no, eksik zorunlu alan yerini söyleyerek hata verir |
| `zaman.py` | Satır sesleri + aralar -> sahne süresi (kare ızgarası), satır/olay/efekt mutlak zamanları, bölüm başları |
| `tts.py` | Cartesia `POST /tts/bytes` (sonic-3, `Cartesia-Version: 2025-11-04`), önbellek, yeniden deneme, sessizlik kırpma, Whisper QA |
| `sahneler.py` | 8 sahne tipi + üst katmanlar (isim etiketi, vurgu kelimesi, daktilo etiketi, konuşma balonu) + filigran |
| `cizim.py` | Yazı, gölge, yuvarlak kutu, alt piksel afin yerleştirme, Ken Burns, gren, vinyet |
| `harita.py` | Natural Earth verisi (indir/sadeleştir), LAEA / Equal Earth projeksiyonu, taban + ülke maskeleri |
| `easing.py` | out_cubic, in_cubic, in_out_cubic, in_out_sine, out_back (küçük taşma), tumsek |
| `render.py` | Paralel parça render (fork, varsayılan 3 işçi), aynı kodlayıcı ayarlı parçalar, concat `-c copy`, ses ekleme, senkron doğrulama |
| `ses.py` | Anlatım zaman çizelgesi, müzik altlığı + yan zincirli kısma, otomatik efektler, iki geçişli loudnorm, anlatım izi |
| `muzik.py` | Kendi müzik altlığımız (Do minör drone + seyrek vals motifi), `tools/uzun_muzik.py` ile dinlenebilir |
| `altyazi.py` | SRT: <= 42 karakter/satır, <= 2 satır, >= 1 sn, çakışmasız |
| `kucukresim.py` | 1280x720 küçük resim varyantları |
| `paket.py` | paylasim.md (başlık alternatifleri, açıklama + bölüm damgaları, kaynak, atıf, etiket, sabit yorum, kontrol listesi) |
| `cli.py` | `python -m wojak uzun ...` |

## 3. Spesifikasyon başvurusu (`uzun/<id>/video.yaml`)

Yollar önce spesifikasyon klasörüne, sonra repo köküne göre çözülür. Tüm alanlar şablonda yorumlu.

### Üst düzey

| Anahtar | Varsayılan | Açıklama |
|---|---|---|
| `id`, `baslik` | zorunlu | id klasör adıyla aynı (`[a-z0-9_-]`) |
| `sesler` | murat, aylin, leyla, azra | ad -> Cartesia ses kimliği |
| `anlatici` | `{ses: murat, hiz: 0.95}` | düz metin satırlarının sesi ve hızı |
| `model`, `dil` | `sonic-3`, `tr` | |
| `telaffuz` | `{}` | yazım -> okunuş; **yalnız TTS metninde**, kelime sınırıyla (`Contergan: Kontergan`) |
| `qa.isimler` | `[]` | `seslendir --qa`'da duyulup duyulmadığı denetlenecek isimler (+ telaffuz anahtarları) |
| `muzik` | `{uret: true}` | `tohum`, `seviye` (konuşmada, anlatıma göre dB, -22), `acik` (konuşmasız, -15), ya da `dosya:`; `false` = müziksiz |
| `zamanlama` | bas 0.35, ara 0.35, son 0.55, min_sahne 2.0, kart 2.6, sabit 3.0, max_bos 6.0 | saniye |
| `gecis` | `kesme` | varsayılan giriş geçişi: `kesme` / `gecis` (8 kare crossfade) / `kaydir` (10 kare push) |
| `filigran` | `tarihselwojak` | `false` = yok |
| `otomatik_sfx` | `true` | sahne tipine göre efektler (aşağıda) |
| `bolumler` | zorunlu | liste |
| `kucukresimler`, `paket` | | §6, §7 |

### Bölüm

`baslik` (zorunlu), `kart` (ilk bölümde `false`, sonrakilerde `true`: siyah kart + "BÖLÜM n" + başlık), `numara`
(vars. kartlı bölümlerin sırası), `kart_sure`, `kart_ust` (numara satırının yerine), `kart_gecis`, `youtube` (açıklamadaki
bölüm adı), `sahneler`.

### Sahne (ortak anahtarlar)

| Anahtar | Açıklama |
|---|---|
| `tip` | `wojak`, `foto`, `manset`, `harita`, `sayac`, `bolum_karti`, `metin`, `zaman_cizelgesi` (takma: `liste`) |
| `satirlar` | düz metin = anlatıcı; sözlük: `metin` (zorunlu), `ses`, `duygu` (Cartesia emotion), `hiz`, `once` (önceki ara yerine), `sonra` (ek bekleme), `tts` (TTS'e başka metin), `balon` (wojak: karakter kimliği, satır o karakterin balonunda görünür). Metinde `<break time="500ms"/>` kullanılabilir; altyazıdan çıkarılır |
| `olaylar` | `{tip, satir, ofset, an, t, ...}` — aşağıdaki tablo |
| `sfx` | `{ad, satir/ofset/an/t, db}`; `ad` = `assets/sfx/<ad>.wav` ya da dosya yolu |
| `gecis`, `gecis_kare` | bu sahneye GİRİŞ geçişi ve kare sayısı |
| `sure`, `min_sure`, `bas`, `ara`, `son` | süre ve sahneye özel aralar (`sure` satırlı sahnede alt sınırdır) |
| `isim_etiketi`, `kelime` | `isim` / `kelime` olaylarının kısayolu |
| `otomatik_sfx` | sahnede otomatik efektleri kapat |

**Süre:** `bas + satır1 + ara + satır2 + ... + son`, en az `min_sure`; kare sayısına yuvarlanır. Satır sesleri örnek
hassasiyetinde, sahneler kare sınırında başlar: görüntü-ses kayması olmaz.

**Çapa:** `satir: n` (1'den) + `ofset` (sn, eksi olabilir) + `an: bas|son` (satırın başı/sonu); satır yoksa `t`
(sahne başına göre sn). Sonuç sahne süresine kırpılır.

### Olaylar

| tip | Sahne | Parametreler | Ne yapar |
|---|---|---|---|
| `yuz` | wojak | `karakter`, `gorsel` | yüz varyantına geçer (kısa sıkışma) |
| `balon` | wojak | `karakter`, `metin`, `sure` | konuşma balonu (pop ile açılır; kuyruk konuşana) |
| `giris` / `cikis` | wojak | `karakter` | karakter kenarından kayarak girer / çıkar |
| `isim` | hepsi | `ad`, `unvan`, `sure`, `konum` (sol/sag) ya da `karakter` | alt bant (lower third), kayarak girer/çıkar |
| `kelime` | hepsi | `metin`, `sure`, `konum` (ust/orta/alt) | ekranda vurgu kelimesi (pop) |
| `etiket` | wojak, foto, manset | — | daktilo etiketinin başlama anı |
| `vurgula` | manset | `kutu` (1'den) | fosforlu kalem o kutudan geçer |
| `basla` | sayac, harita, zaman_cizelgesi | — | ana animasyon başlar |
| `ulke` | harita | `kod` | o ülke (ya da vurgu ülkesi) bu anda yanar |
| `nokta` | zaman_cizelgesi | `indeks` (1'den) | o nokta bu anda belirir |
| `ceviri` | metin | — | çeviri satırı belirir |

### Sahne tipleri

| tip | Parametreler | Görüntü |
|---|---|---|
| `wojak` | `arka`*, `kirp` [x0,y0,x1,y1], `odak`, `kamera` {zoom: [a,b], merkez: [[x,y],[x,y]]}, `karart`, `bulanik`, `doygunluk`, `etiket`, `karakterler` (1-3: `id`, `gorsel`*, `taraf` sol/sag/orta, `x`, `boy` 0.66, `giris` true/false/sn, `bakis`, `alt`) | Ken Burns arka plan; karakterler kenardan out_back (%4-5 taşma) ile kayarak girer, nefes alır (±%1, 0,3 Hz) ve hafif sallanır, `data/karakter_yon.json`'a göre hep içeri bakar (gerekirse aynalanır) |
| `foto` | `gorsel`*, `etiket`, `atif`, `egim`, `giris` (alt/ust/sag/sol), `boy` 0.72, `zoom` 1.05, `arka` | aynı fotoğrafın bulanık-karartılmış hâli üzerinde beyaz kenarlı, gölgeli, eğik "baskı"; düşerek oturur, deklanşör sesi; yavaş yaklaşma; daktilo etiketi |
| `manset` | `gorsel`*, `kutular` (piksel ya da 0..1), `zoom` 1.18, `renk`, `boy`, `arka`, `etiket` | belge/manşet; kutular sırayla fosforlu kalemle (çarpma karışımı, pürüzlü kenar) boyanır; kamera yaklaşır ve kalemi dikeyde izler |
| `harita` | `bolge` (avrupa, bati_avrupa, akdeniz, turkiye, dunya ya da {merkez, sinir}), `ulkeler` (ADM0_A3), `aralik`, `etiketler`, `vurgu` {kod, etiket, renk, ad}, `baslik`, `aciklama` (lejant), `renk`, `zoom`, `cozunurluk` (50m/110m) | ülkeler sırayla parlayarak yanar; vurgu ülkesi farklı renk, nabız gibi atan halka ve çağrı kutusu |
| `sayac` | `deger` ya da `yil` [a, b], `onek`, `sonek` ("+"), `ust`, `etiket`, `sure_say`, `arka` | sabit genişlikli rakamlarla sayma (out_cubic); yıl modunda odometre gibi dönen basamaklar; bitişte vuruş + sarı çizgi |
| `bolum_karti` | (bölümden) `numara`, `baslik`, `ust` | siyah zemin + gren, ortadan açılan sarı çizgi, "BÖLÜM n", soldan silinerek açılan başlık |
| `metin` | `metin`*, `ceviri`, `ust`, `alt`, `arka`, `ceviri_t` | kelime kelime beliren büyük alıntı; çeviri sarı, altı fosforlu çizgiyle |
| `zaman_cizelgesi` | `noktalar`* (2-8; `tarih`, `metin`), `baslik`, `arka` | eksen çizilir, noktalar sırayla pop'lar, sarı ilerleme çizgisi, etkin nokta nabız |

`*` zorunlu. Filigran her karede sağ altta (geçişten sonra eklenir, kaymaz).

### Otomatik efektler (`assets/sfx`, hepsi sentez: `tools/make_sfx.py`)

kaydir geçişi -> `whoosh_kisa`; bölüm kartı -> `boom` (+ öncesinde alçak `riser`); foto -> `shutter` + harf başına `tus`;
manset -> kutu başına `kalem`; harita -> ülke başına `blip`, vurguda `pop` + `hit`; sayaç -> `tik`'ler + bitişte `hit`;
zaman çizelgesi -> nokta başına `pop`; metin -> `whoosh_kisa` + çeviride `pop`; wojak -> giriş/çıkışta `whoosh_kisa`,
balonda `pop`; isim etiketi -> `whoosh_kisa`; vurgu kelimesi -> `pop`.

## 4. Ses

1. Satırlar kırpılmış (tutarlı: -42 dBFS eşiği, 40 ms ön, 100 ms arka pay, yumuşak uçlar) sesleriyle yerleşir; her satır
   konuşulan bölümün RMS'ine göre ortak seviyeye (-18 dBFS, ±12 dB sınırlı) getirilir (Cartesia'da Aylin, Murat'tan ~6 dB
   yüksek çıkıyor).
2. Müzik: `muzik.uret(süre, tohum)` (ilk seferde üretilir, `out/<id>/muzik/`). Anlatımın ölçülen yüksekliğine göre:
   konuşmada `seviye` (-22 dB), konuşmasızda `acik` (-15 dB). Kısma anahtarı anlatım izi (20 ms RMS, eşik -42 dBFS,
   0,35 sn tutma, 0,12 sn atak, 0,7 sn bırakma): cümle aralarında pompalama yok, kartlarda müzik açılır.
3. Efektler eklenir.
4. Normalizasyon: ölç -> kazanç + tepe sınırlayıcı (alimiter) -> ölç -> `loudnorm ... linear=true` -> -14 LUFS, -1 dBTP.
   `olcum.json`'da `loudnorm_turu: linear` olmalı.
5. `out/<id>/<id>_anlatim.wav`: yalnız anlatım (aynı toplam kazanç).

## 5. Render ve senkron

- Sahneler en fazla 180 karelik parçalara bölünür; parçalar `ProcessPoolExecutor` (fork) ile paralel çizilir ve her biri
  `libx264 -preset faster -crf 18 -pix_fmt yuv420p -bf 0 -profile:v high -g 60 -r 30` ile ayrı mp4'e yazılır.
  `--preset medium` daha küçük dosya, 2 kat yavaş (darboğaz kodlayıcı).
- Parça önbelleği: anahtar = sahne içeriği + zamanlama + görsel dosya tarihleri + motor kodunun özeti. Yalnız değişen
  sahneler yeniden çizilir.
- Birleştirme: concat demuxer `-c copy`; ses AAC 48 kHz eklenir (`+faststart`, edit list ile AAC ön dolgusu atlanır).
- `dogrula()`: video ve ses 0.000'da başlamalı, süre farkı < 1 kare, kare sayısı = zaman çizelgesi.
- Ön izleme: 960x540, `veryfast`, aralık kare/örnek hassasiyetinde kırpılır.

## 6. Küçük resim (`kucukresimler`)

`ad`, `arka`, `karart`, `bulanik`, `odak`, `karakterler` [{gorsel, taraf, boy, x, bakis}] (beyaz "çıkartma" konturu,
içeri bakar), `yazi` (2-4 kelime, Anton, büyük harf, kalın kontur; en dengeli 1-2 satır), `vurgu_kelime` (sarı), `yazi_y`,
`ek` {gorsel, konum sag_alt/sol_alt/sag_ust/sol_ust/orta_alt, boy, egim} (beyaz kenarlı arşiv görseli), `ok` {bas, son},
`daire` {x, y, r}. JPEG < 2 MB. Telifli görsel içeren varyant için `teslim` uyarır (teslim/ repoya girer).

## 7. Paket (`paket`)

`baslik_alternatifleri`, `aciklama` (ilk paragraf), `short_url` (yoksa yer tutucu), `short_baglanti`, `etiketler`
(<= 500 karakter), `sabit_yorum`, `kaynaklar`, `gorsel_atif`. Bölüm zaman damgaları zaman çizelgesinden hesaplanır
(bölümün ilk sahnesinin başı, aşağı yuvarlanır; ilki 0:00). Denetim: >= 3 bölüm, her biri >= 10 sn, artan sıra.
Kontrol listesinde "Shorts > İlgili video" bağlantısı ve bitiş ekranı maddeleri var.

## 8. Denetimler (`kontrol`)

- **Hareket:** her sahnenin "vuruşları" (giriş, balon, yüz, etiket, ülke, nokta, kutu, sayaç başı/sonu, olaylar) toplanır;
  `max_bos` (6 sn) boyunca ekrana yeni bir şey gelmiyorsa zaman aralığıyla uyarır.
- **Bölüm:** YouTube kuralları. **Altyazı:** 42/2/1 kuralları. **Paket:** başlık <= 100, etiket <= 500, açıklama <= 5000.
- **Ses QA:** `seslendir --qa` isim geçen satırları faster-whisper "medium" ile dinler (ses ffmpeg ile 16 kHz diziye
  çözülür; kütüphanenin kendi çözücüsü kurulu PyAV ile bozuk), benzerlik < 0,72 ise "KONTROL ET". `--yenile N`: başarısız
  satır en fazla N kez yeniden üretilir, en iyi deneme seçilir (`out/<id>/ses/manifest.json`, `secim`). Döngüye girmez.
  Not: Whisper nadir adları (talidomit, Lenz) bazen yanlış yazar; rapor dinleyip karar vermek içindir.

## 9. Varlıklar ve lisans

| Varlık | Yer | Lisans |
|---|---|---|
| Harita | `assets/harita/ne_{110m,50m}_admin_0_countries.geojson.gz` | Natural Earth, kamu malı (`assets/harita/LISANS.md`) |
| Daktilo yazısı | `assets/fonts/LiberationMono-Bold.ttf` | SIL OFL 1.1 (`OFL-Liberation.txt`) |
| Efektler | `assets/sfx/*.wav` | kendi sentezimiz (`tools/make_sfx.py`) |
| Müzik | `out/<id>/muzik/` (üretilir) | kendi sentezimiz (`wojak/uzun/muzik.py`) |
| Kanal yazısı | `assets/fonts/ozel/` (Avenir, yerel) | lisanslı, repoya girmez; yoksa Poppins |

Repoya girmeyenler: `out/`, `uzun/*/img/telifli/`, `teslim/*/*.mp4`, `assets/fonts/ozel/`, `assets/music/ozel/`, `referans/`.

## 10. Ölçümler (demo, 12.10.2026, 4 çekirdek)

`uzun/demo` (61,5 sn, 11 sahne, 15 satır, 2 ses, 86 efekt): render 1920x1080 **~29-30 kare/sn** (3 işçi, `faster`;
4 işçi aynı; `medium` ile ~17), video ~62 sn + ses ~23 sn; değişmemiş parçalar önbellekten (yeniden render ~5 sn).
Ses -14,0 LUFS, WAV'da -1,7 dBTP, AAC sonrası -2,3 dBTP, LRA 3,6, loudnorm doğrusal (sınırlayıcı -3,6 dBFS);
müzik konuşmada anlatımın ~23-25 dB altında. Video ve ses 0,000'da başlıyor, süre farkı 0 ms, 1845/1845 kare, B-kare yok.
Ön izleme (960x540) ~125 kare/sn. TTS: 15 satır ~27 sn; Whisper QA 4 isimli satır, 1 yeniden deneme sonrası hepsi tamam.
9 dakikalık bir video için tahmin: ~9 dk render + ~2-3 dk ses (ilk seferde müzik üretimi ~1 dk).

## 11. Bilinen sınırlar

- Karakter nefes ölçeği 0,001 adımla nicemlenir ve konum tam piksele yuvarlanır (hız için); çok yavaş sallanmada 1 px
  adımlar teorik olarak seçilebilir.
- Harita bugünkü sınırları gösterir (1957'nin Batı/Doğu Almanya'sı yok); gerekirse anlatımda belirt.
- Balon yerleşimi karakterin başının üstünü varsayar; çok uzun (boy > 0,8) karakterde balon kadraj üstüne yaslanır.
- Altyazı parçalarının satır içindeki zamanlaması uzunlukla orantılı tahmindir (kelime zaman damgası yok).
- Whisper QA yalnız isimlere bakar; vurgu/tonlama hatalarını yakalamaz.
