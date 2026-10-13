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
python -m wojak uzun render     uzun/<id>          # out/<id>-uzun/<id>.mp4 (+ .srt, anlatım izi, olcum.json, paylasim.md)
python -m wojak uzun kucukresim uzun/<id>          # out/<id>-uzun/kucukresim_*.jpg (1280x720)
python -m wojak uzun teslim     uzun/<id>          # teslim/<id>-uzun/: <id>-uzun.mp4 (git'e girmez), <id>-uzun.srt, küçük resimler, paylasim.md
```

Çıktı klasörü `out/<id>-uzun/` (`Video.cikti`): aynı id'li Short `out/<id>/`'yi kullanır; ikisi aynı klasörü paylaşınca uzun
videonun mp4'ü Short teslimine karışıyordu. Teslimde video ve altyazı `<id>-uzun.mp4` / `<id>-uzun.srt` adını alır (6. tur:
Short'un teslimi de `<id>.mp4`; sohbetten ikisi indirilince biri ötekinin üstüne yazılabiliyordu). `teslim` kopyalamadan önce mp4'ün 1920x1080, kare sayısının zaman
çizelgesiyle aynı ve senkronun tamam olduğunu doğrular; Whisper QA'da "KONTROL ET" satırı varsa uyarır (`--zorla`).

Gizli anahtar: `CARTESIA_API_KEY` (yedekler `CARTESIA_API_KEY_2` … `_9`) ortamdan ya da `~/.config/wojak/secrets.env`'den
(`wojak.config.load_secrets`) okunur; bir anahtar HTTP 402 (kota doldu) dönerse sıradakine geçilir;
hiçbir dosyaya, loga, hata mesajına yazılmaz. HTTP isteklerinde genel tarayıcı kimliği kullanılır.

## 2. Mimari

| Modül | İş |
|---|---|
| `spec.py` | YAML -> `Video` / `Bolum` / `Sahne` / `Satir` / `Olay` / `Sfx`; bilinmeyen anahtar, yanlış satır no, eksik zorunlu alan yerini söyleyerek hata verir |
| `zaman.py` | Satır sesleri + aralar -> sahne süresi (kare ızgarası), satır/olay/efekt mutlak zamanları, bölüm başları |
| `tts.py` | Cartesia `POST /tts/bytes` (sonic-3, `Cartesia-Version: 2025-11-04`), önbellek, yeniden deneme, sessizlik kırpma, Whisper QA |
| `sahneler.py` | 8 temel sahne tipi (wojak, foto, manset, harita, sayac, bolum_karti, metin, zaman_cizelgesi) + üst katmanlar (isim etiketi, vurgu kelimesi, daktilo etiketi, konuşma balonu) + filigran; wojak sahnesinin kamerası (`Kam`) ve konuşma sekmesi |
| `bilgi.py` | bolunmus (bölünmüş ekran), izgara (nokta ızgarası), pano (soruşturma panosu) |
| `kanal.py` | marka (kanal imzası / sting), bitis (YouTube bitiş ekranı), `logotip()` |
| `zemin.py` | Bilgi sahnelerinin zemini (koyu / kagit / foto), palet (koyu zeminde beyaz-sarı, kâğıtta mürekkep), boşta hareket (süzülme, toz, ışık, gren) |
| `ust.py` | Her sahnede: lastik damga (`damga` olayı), köşe göstergesi (`kose`) |
| `cizim.py` | Yazı, gölge, yuvarlak kutu, alt piksel afin yerleştirme, Ken Burns, gren, vinyet |
| `harita.py` | Natural Earth verisi (indir/sadeleştir), LAEA / Equal Earth projeksiyonu, taban + ülke maskeleri |
| `easing.py` | out_cubic, in_cubic, in_out_cubic, in_out_sine, out_back (küçük taşma), tumsek |
| `render.py` | Paralel parça render (fork, varsayılan 3 işçi), aynı kodlayıcı ayarlı parçalar, concat `-c copy`, ses ekleme, senkron doğrulama |
| `ses.py` | Anlatım zaman çizelgesi, müzik altlığı + yan zincirli kısma, otomatik efektler, iki geçişli loudnorm, anlatım izi |
| `muzik.py` | Kendi müzik altlığımız (Do minör drone + seyrek vals motifi), `tools/uzun_muzik.py` ile dinlenebilir |
| `altyazi.py` | SRT: <= 42 karakter/satır, <= 2 satır, >= 1 sn, çakışmasız; anlatıcıdan başka sesin satırı (alıntı) `<i>…</i>` |
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
| `muzik` | `{uret: true}` | `tohum`, `seviye` (konuşmada, anlatıma göre dB, -22), `acik` (konuşmasız, -15), `mod` (başlangıç kipi, vars. drone), ya da `dosya:`; `false` = müziksiz |
| `zamanlama` | bas 0.35, ara 0.35, son 0.55, min_sahne 2.0, kart 2.6, sabit 3.0, max_bos 6.0, bindirme 1.2 | saniye (`bindirme`: bindirme bölüm kartının süresi) |
| `kart_bindirme` | `false` | `true`: bütün bölüm kartları bindirme (önceki sahnenin donmuş, kararmış son karesi üstünde, 1,2 sn; siyah ekran yok). Bölüm `kart_bindirme` ile tek tek değişir |
| `gecis` | `kesme` | varsayılan giriş geçişi: `kesme` / `gecis` (8 kare crossfade) / `kaydir` (10 kare push) |
| `filigran` | `tarihselwojak` | `false` = yok |
| `otomatik_sfx` | `true` | sahne tipine göre efektler (aşağıda) |
| `bolumler` | zorunlu | liste |
| `kucukresimler`, `paket` | | §6, §7 |

### Bölüm

`baslik` (zorunlu), `kart` (ilk bölümde `false`, sonrakilerde `true`: siyah kart + "BÖLÜM n" + başlık), `numara`
(vars. kartlı bölümlerin sırası), `kart_sure`, `kart_ust` (numara satırının yerine), `kart_gecis`, `kart_bindirme`
(bu bölümün kartı bindirme mi), `kart_marka` (kartta önce kanal imzası belirir, sonra bölüm başlığı: soğuk açılıştan
sonraki ilk kart için), `kart_muzik_db` (kartta müzik kabarması, ör. 4), `muzik_mod` (bölümün ilk sahnesinden itibaren
müzik kipi), `youtube` (açıklamadaki bölüm adı), `sahneler`.

### Sahne (ortak anahtarlar)

| Anahtar | Açıklama |
|---|---|
| `tip` | `wojak`, `foto`, `manset`, `harita`, `sayac`, `bolum_karti`, `metin`, `zaman_cizelgesi` (takma: `liste`), `bolunmus`, `izgara`, `pano`, `marka`, `bitis` |
| `satirlar` | düz metin = anlatıcı; sözlük: `metin` (zorunlu), `ses`, `duygu` (Cartesia emotion), `hiz`, `once` (önceki ara yerine), `sonra` (ek bekleme; vurgu cümlesinden sonra 0,4-0,6), `db` (ortak seviyeden sonra ek kazanç, ±6), `tts` (TTS'e başka metin), `balon` (wojak: karakter kimliği, satır o karakterin balonunda görünür; karakter konuşurken seker), `konusan` (wojak: karakter kimliği; balonsuz, satır boyunca o karakter seker ve kamera ona yaklaşır). Metinde `<break time="500ms"/>` kullanılabilir; altyazıdan çıkarılır |
| `olaylar` | `{tip, satir, ofset, an, t, ...}` — aşağıdaki tablo |
| `sfx` | `{ad, satir/ofset/an/t, db}`; `ad` = `assets/sfx/<ad>.wav` ya da dosya yolu |
| `gecis`, `gecis_kare` | bu sahneye GİRİŞ geçişi ve kare sayısı |
| `sure`, `min_sure`, `bas`, `ara`, `son` | süre ve sahneye özel aralar (`sure` satırlı sahnede alt sınırdır) |
| `isim_etiketi`, `kelime` | `isim` / `kelime` olaylarının kısayolu |
| `otomatik_sfx` | sahnede otomatik efektleri kapat |
| `kose` | köşe göstergesi, sahne başındaki hâli: `{metin: "GÜN {} / 12", deger: 0, konum: sag_ust\|sol_ust\|sag_alt\|sol_alt, renk, yil: true, giris: false}`; `kose` olaylarıyla değişir. Birden çok sahneye yayılan sayaçta her sahne kendi başlangıcını yazar |
| `muzik_db` | bu sahnede müzik seviyesi (dB; 0 = normal, -8 = kısık, +6 = açık). Sahne başında 0,6 sn rampa; kısma zarfının üstüne çarpılır |
| `muzik_mod` | bu sahneden itibaren müzik kipi: `drone` (vars.), `nabiz` (alçak kalp atışı: geri sayım, takip), `gerilim` (tiz titreyen yarım ton kümesi, crescendo: soruşturma), `major` (Do majör: çözülme). Kip değişimleri 3 sn çapraz geçişle, aynı RMS'te |
| `filigran` | `false`: bu sahnede filigran yok (`marka`da varsayılan) |
| `sfx_db` | bu sahnenin OTOMATİK efektlerine ek kazanç (dB, -24..+6). 5. tur: KÜB alıntısında fosforlu kalem sesi sessiz altlıkta sözün 10-12 dB altındaydı: `sfx_db: -6` |
| `konuk` | (wojak dışı her tip) köşeden/kenardan giren **tepki karakteri** (1-2): `{id, gorsel, x, boy, alt, giris, yon: alt\|sol\|sag, bakis}`; `yuz` / `giris` / `cikis` olayları ve `isim {karakter}` konuk kimliğiyle her tipte kullanılır; kamerasız (ekran koordinatı), yazı katmanlarının altında çizilir; giriş/çıkışta `whoosh_kisa`. 4. tur (talidomit-turkiye): hesap sahibi "wojak kanalı: harita/sayaç/pano tek başına yetmez" dedi; karakterli süre %26 -> %68. Yazıyla çakışmasın: konuk köşedeyken `kelime` `konum: ust`, foto baskısı `x` ile yana |

**Süre:** `bas + satır1 + ara + satır2 + ... + son`, en az `min_sure`; kare sayısına yuvarlanır. Satır sesleri örnek
hassasiyetinde, sahneler kare sınırında başlar: görüntü-ses kayması olmaz.

**Çapa:** `satir: n` (1'den) + `ofset` (sn, eksi olabilir) + `an: bas|son` (satırın başı/sonu); satır yoksa `t`
(sahne başına göre sn). Sonuç sahne süresine kırpılır.

### Olaylar

| tip | Sahne | Parametreler | Ne yapar |
|---|---|---|---|
| `yuz` | wojak (ya da konuklu sahne) | `karakter`, `gorsel` | yüz varyantına geçer (kısa sıkışma) |
| `balon` | wojak | `karakter`, `metin`, `sure` | konuşma balonu (pop ile açılır; kuyruk konuşana) |
| `giris` / `cikis` | wojak (ya da konuklu sahne) | `karakter` | karakter kenarından (ya da `yon: alt` ise alttan) kayarak girer / çıkar |
| `isim` | hepsi | `ad`, `unvan`, `sure`, `konum` (sol/sag) ya da `karakter` | alt bant (lower third), kayarak girer/çıkar |
| `kelime` | hepsi | `metin`, `sure`, `konum` (ust/orta/alt) | ekranda vurgu kelimesi (pop) |
| `etiket` | wojak, foto, manset | — | daktilo etiketinin başlama anı |
| `vurgula` | manset | `kutu` (1'den) | fosforlu kalem o kutudan geçer |
| `basla` | sayac, harita, zaman_cizelgesi, izgara | — | ana animasyon başlar |
| `ulke` | harita | `kod` | o ülke (ya da vurgu ülkesi) bu anda yanar |
| `nokta` | zaman_cizelgesi | `indeks` (1'den) | o nokta bu anda belirir |
| `ceviri` | metin, bolunmus | `taraf` (bolunmus) | çeviri satırı belirir |
| `damga` | hepsi | `metin`, `renk` (kirmizi/yesil/mavi/... ya da [r,g,b]), `x`, `y` (0..1), `aci` (-8), `boy` (84), `sure` (yoksa sahne sonuna dek), `kontur` (true = beyaz ya da renk: harf ve çerçeve çevresine ince dolu kenar; koyu/desenli zeminde okunurluk), `kart` (pano), `kart_y` (kart merkezine göre, kart yüksekliği oranı; vars. görselli kartta görselin ortası, görselsizde 0.2: başlık okunur kalır), `inik` (true: sahne başında zaten basılı, iniş/ses yok: bölünmüş çekimin devamı) | lastik damga ekrana çarparak iner (mürekkep dokulu, çift çerçeve); efekt `damga` |
| `kose` | hepsi | `deger`, `metin`, `sure` (0,6), `takili`, `renk`, `yil` | köşe göstergesi yeni değere sayar (sayı) ya da yuvarlanır (metin); `takili: true` basamaklar karışıp takılır ve ara ara titrer ("1961 -> ????"); yıl göstergesinde (`yil`) yüzyıl basamakları sabit kalır, yalnız son ikisi karışır ("19??" / "20??"; 5. tur: tam karışım "1781", "5940" gösteriyordu) |
| `muzik` | hepsi | `db`, `gecis` (rampa sn, 0,5) | müzik seviyesi bu andan itibaren (incelme, bir an sessizlik: `db: -40`) |
| `deger` | sayac | `deger`, `etiket`, `renk`, `sure` (1,2), `onek`, `sonek` | sayaç bir önceki değerden yenisine sayar; etiket ve renk değişebilir. `sure: 0`: yeni değer bir anda (tık yok, yalnız vuruş; 6. tur: 20.000 -> 17 geri sayarken "en az 16.043" görünüyordu) |
| `panel` | bolunmus | `taraf` (vars. sag) | panel kayarak açılır, ekran ikiye bölünür |
| `soluk` | bolunmus | `taraf` | panel kararıp renksizleşir |
| `buyut` | bolunmus | `taraf` | panel büyüyüp ekranı kaplar (1,2 sn) |
| `kart` | pano | `id` | kart iğnelenir (düşer + raptiye) |
| `ip` | pano | `a`, `b` | iki kartın raptiyeleri arasına kırmızı ip gerilir (`ipler` listesinde yoksa eklenir) |
| `sondur` | izgara | `oran` (0..1), `sure` (1,6), `etiket` | yanık noktaların o oranı rastgele ve sessizce söner (silik iz kalır); etiket yenisiyle değişir |
| `ustunu_ciz` | metin | `renk` | ana yazının üstü satır satır kırmızı çizgiyle çizilir; efekt `kalem` |

Sahne tipine özgü bir olayı başka tipte kullanmak hata verir (ör. `sondur` yalnız izgara).

### Sahne tipleri

| tip | Parametreler | Görüntü |
|---|---|---|
| `wojak` | `arka`*, `kirp` [x0,y0,x1,y1], `odak`, `vinyet` (0.42; düz zeminde bilinçli yakın çekim için 0.7-0.8), `kamera` {zoom: [a,b], merkez: [[x,y],[x,y]], `it` (0.05), `odak` (0.4)}, `karart`, `bulanik`, `doygunluk`, `etiket`, `karakterler` (1-4: `id`, `gorsel`*, `taraf` sol/sag/orta, `x`, `boy` 0.66, `giris` true/false/sn, `yon` sol/sag/alt (giriş yönü), `bakis`, `alt`, `derinlik` 0..1) | Ken Burns arka plan; karakterler kenardan out_back (%4-5 taşma) ile kayarak girer, nefes alır (±%1, 0,3 Hz) ve hafif sallanır, `data/karakter_yon.json`'a göre hep içeri bakar (gerekirse aynalanır). **Kamera** arka planı, karakterleri ve balonları birlikte taşır; biri konuşurken (`balon`/`konusan` satırı, `balon` olayı) konuşana doğru yumuşakça yaklaşır (`it`: zoom artışı, `odak`: merkezin kayma oranı; `it: 0` kapatır). **Konuşma sekmesi**: konuşan karakter satırın sesindeki hece başlarında (10 ms RMS'te > 6 dB yükseliş) küçük bir sekme ve dikey esneme yapar; ses yoksa yapay hece ritmi. **Derinlik** (3 karakterde arkadaki): küçülür (1 - 0,3·d), hafif sisli, az doygun, önce çizilir; taban kadraj altında kalır (kit görselleri göğüsten kesik) |
| `foto` | `gorsel`*, `etiket`, `atif`, `egim`, `giris` (alt/ust/sag/sol), `boy` 0.72, `zoom` 1.05, `arka`, `x` (baskının yatay merkezi, 0.5; ortada değilse atıf baskının altına yazılır: köşedeki konuğa binmesin) | aynı fotoğrafın bulanık-karartılmış hâli üzerinde beyaz kenarlı, gölgeli, eğik "baskı"; düşerek oturur, deklanşör sesi; yavaş yaklaşma; daktilo etiketi |
| `manset` | `gorsel`*, `kutular` (piksel ya da 0..1), `zoom` 1.18, `renk`, `boy`, `arka`, `etiket` | belge/manşet; kutular sırayla fosforlu kalemle (çarpma karışımı, pürüzlü kenar) boyanır; kamera yaklaşır ve kalemi dikeyde izler |
| `harita` | `bolge` (avrupa, bati_avrupa, akdeniz, turkiye, dunya ya da {merkez, sinir}), `ulkeler` (ADM0_A3), `aralik`, `etiketler`, `vurgu` {kod, etiket, renk, ad}, `baslik`, `aciklama` (lejant), `renk`, `zoom`, `cozunurluk` (50m/110m) | ülkeler sırayla parlayarak yanar; vurgu ülkesi farklı renk, nabız gibi atan halka ve çağrı kutusu |
| `sayac` | `deger` (ya da azalan `[60, 0]`) ya da `yil` [a, b], `onek`, `sonek` ("+"; azalanda yok), `ust`, `etiket`, `sure_say`, `renk`, zemin | sabit genişlikli rakamlarla sayma (artan out_cubic, azalan doğrusal); yıl modunda odometre gibi dönen basamaklar; bitişte vuruş + çizgi; `deger` olaylarıyla yeni değerlere (1.267 doktor -> 20.000 hasta -> EN AZ 17); bitince sayı nefes alır |
| `bolum_karti` | (bölümden) `numara`, `baslik`, `ust`; `bindirme`, `marka`, `karart` (0.45) | siyah zemin + gren (ya da bindirme: donmuş son kare kararır ve bulanır, hafif yaklaşır), ortadan açılan sarı çizgi, "BÖLÜM n", soldan silinerek açılan başlık; kısa kartta animasyon orantılı sıkışır |
| `metin` | `metin`*, `ceviri`, `ust`, `alt`, `ceviri_t`, `yazim` (kelime/daktilo), `renk`, `tirnak` (süs tırnağı; vars. yalnız metin tırnakla başlıyorsa), zemin | kelime kelime beliren büyük alıntı (daktilo: harf harf, imleçli, tuş sesli); çeviri koyu zeminde sarı + altı sarı şerit, kâğıtta mürekkep + fosforlu kalem; satırlar hafifçe süzülür |
| `zaman_cizelgesi` | `noktalar`* (2-8; `tarih`, `metin`), `baslik`, zemin | eksen çizilir, noktalar sırayla pop'lar, ilerleme çizgisi, etkin nokta nabız; yazılar süzülür |
| `bolunmus` | `sol`*, `sag`* (panel: `gorsel` ya da `metin` + `ceviri`, `etiket`, `baslik`, `alt` (40 px, koyu bantta, panelin sol altında; 5. tur: 24 px okunmuyordu), `odak`, `zoom`, `zemin`, `arka`), `acik`, `cizgi` | sol panel ekranı kaplar; `panel` olayında sağ panel kayarak açılır (ayraç: koyu + sarı çizgi). Görsel paneller kendi Ken Burns'üyle oynar ve pencereden görünür (kırpılır, ölçeklenmez); metin paneli kendi zemininde, görünen yarıda ortalı |
| `izgara` | `n` (10000), `sutun`, `ust`, `etiket`, `alt`, `renk`, `dolum` (2,5 sn), `say`, zemin | n nokta satır satır dolar (`basla`), noktalar yavaşça ışıldar; `sondur` olayında bir oranı sessizce söner; `say: true` canlı sayı |
| `pano` | `kartlar`* (1-12: `id`, `metin`*, `alt`, `x`, `y` (0..1, kadraja göre), `en`, `egim`, `gorsel`, `stil` kagit/merkez/bos/foto, `asili` (true: sahne başında zaten iğnelenmiş, düşmez, ses yok: panoyu iki çekime bölünce ikincisinde)), `ipler` [[a, b]], `baslik`, `zoom` (1.2: tuvalin kaydırma payı), `yakin` (1.0; > 1 kamera kartlara yaklaşır, ör. 1.35: ilk kartlar büyük okunur), `doku` (mantar \| kece: koyu mavi-gri keçe; aynı pano üçüncü kez görünmesin) | kendi mantar dokumuz; kartlar `kart` olayında düşüp iğnelenir (raptiye sesi), ipler kırmızı ve sarkık çizilir, `damga` olayı `kart:` ile kartın üstüne; kamera 1:1'den %6 yaklaşır ve asılı kartların ağırlık merkezine kayar |
| `marka` | `bindirme`, `karart` (0.72), `wojak`, `yuz` (imzada geçilen yüz), `yazi` (vars. filigran), `arka` | ~1,8 sn kanal imzası: yuvarlak wojak rozeti döner ve büyür, sarı şerit geçerken `tarihselwojak` yazısı açılır, rozet gülümser, sonunda yazı küçülüp filigranın yerine uçar (sahnede filigran yok, son karede gerçek filigranla değişir); efekt `marka` |
| `bitis` | `arka` ya da `bindirme`, `karart` (0.62), `bulanik`, `baslik` (vars. ilk satır; `false`: yok), `kutular` (0-2), `abone` (true), `duzen` (yan_yana/sag/sol), `etiketler`, `karakter` {gorsel, boy, bakis} | YouTube bitiş ekranı: bulanık zemin, üstte kapanış cümlesi, iki boş 16:9 kutu + abone dairesi (`BITIS_DUZENLERI`: kenarlardan uzak, alt %10 oynatıcıya boş). YouTube 5-20 sn ister (§8); 9-12 sn yeterli (talidomit-turkiye: 9,3 sn); son sahne olmalı (`kontrol` uyarır) |

**Zemin** (sayac, metin, zaman_cizelgesi, izgara ve metin panelleri): `zemin: koyu` (vars.; degrade + leke dokusu +
vinyet; 4. turda aydınlatıldı: kare ortalaması ~55-65/255, eskiden ~20; harita denizi ve karası da: dünya haritası ~75), `kagit` (eski kâğıt; yazılar mürekkep rengi), `foto` (`arka`'nın kendisi bulanık-karartılmış); `arka` koyu
zemine `arka_opak` (0.5) oranında karışır. Hepsinde boşta hareket: yavaş itme + yanal süzülme, toz zerreleri ve gezinen
ışık (koyu), gren. Ölçüm (demo, 2 sn arayla bulanık karelerin ortalama farkı): bütün sahnelerde > 1.

**Bindirme sahneleri** (`bolum_karti` + `bindirme`, `marka` + `bindirme`, `bitis` + `bindirme`): render önceki sahnenin
son karesini (filigransız) bir kez çizip sahneye verir; parça önbelleği anahtarı önceki sahnelere bağlıdır. Karartma
donmuş karenin parlaklığına göre artar (kâğıt gibi açık karede yazı okunsun: `cizim.donuk_karart`).

`*` zorunlu. Filigran her karede sağ altta (geçişten sonra eklenir, kaymaz).

### Otomatik efektler (`assets/sfx`, hepsi sentez: `tools/make_sfx.py`)

kaydir geçişi -> `gecis` (süpürmeli whoosh, tepesi geçişin ortasında, soldan sağa); bölüm kartı -> `gecis` + `boom`
(bindirmesizde öncesinde alçak `riser`); foto -> `shutter` + etikette her 4 harfte bir alçak `tus` (`ses.ETIKET_TUS_ADIMI`; 6. tur: anlatımın altında saniyede ~10 tık yoruyordu); manset -> kutu başına `kalem`; harita ->
ülke başına `blip`, vurguda `pop` + `hit`; sayaç -> `tik`'ler (azalanda eşit aralıklı) + her bitişte `hit`; zaman
çizelgesi -> nokta başına `pop`; metin -> `whoosh_kisa` (daktiloda harf başına `tus`) + çeviride `pop` + üstünü çizmede
`kalem`; wojak -> giriş/çıkışta `whoosh_kisa`, balonda `pop`; isim etiketi -> `whoosh_kisa`; vurgu kelimesi -> `pop`;
damga -> `damga`; köşe göstergesi -> `tik` (takılınca `static`); bolunmus -> panel açılışında `whoosh_kisa`, büyütmede
`whoosh`, çeviride `pop`; pano -> kart başına `whoosh_kisa` + `raptiye`, ipte hafif `whoosh_kisa`; marka -> `marka`;
bitis -> kutu ve dairede `pop`; izgara bilerek sessiz.

**Efekt kısması:** bütün efektler (otomatik + `sfx`) tek veriyolunda toplanır ve anlatım konuşurken yan zincirle
kısılır: 10 ms RMS satır seviyesinin (`SATIR_HEDEF_DB`) `EFEKT_PAYI_DB` (9 dB) altına sınırlanır (60 ms önce, 180 ms sonra
dahil). Hiçbir efekt bir kelimeyi örtemez; vurgu efekti (motif, damga, boom, hit) tam sesiyle duyulsun diye cümle
**bitişine** çapalanır: `{ad: turkiye, satir: n, an: son, ofset: 0.05, db: -11}` + satıra `sonra: 0.5`
(talidomit-turkiye 1. hakem turu: motif ve harita pop+hit Türkiye kelimesinin üstüne düşüp onu örtüyordu).

Elle kullanılacak yeni efektler (sahnenin `sfx` listesiyle): `turkiye` (Türkiye ses motifi, minör: Sol-Do-Mi bemol),
`turkiye_major` (aynı motifin majör çözülüşü), `kapi` (iki tok kapı vuruşu), `geri_sarma` (bant geri sarma), `telefon`
(eski telefon zili), `raptiye`, `damga`, `gecis`, `marka`. Örnek: `sfx: [{ad: turkiye, satir: 2, an: son, ofset: 0.05, db: -11}]`.

## 4. Ses

1. Satırlar kırpılmış (tutarlı: -42 dBFS eşiği, 40 ms ön, 100 ms arka pay, yumuşak uçlar) sesleriyle yerleşir; her satır
   konuşulan bölümün RMS'ine göre ortak seviyeye (-18 dBFS, ±12 dB sınırlı) getirilir (Cartesia'da Aylin, Murat'tan ~6 dB
   yüksek çıkıyor).
2. Müzik: `muzik.uret(süre, tohum, mod)` ya da kip değişiyorsa `muzik.uret_bolumlu` (ilk seferde üretilir,
   `out/<id>-uzun/muzik/`, dosya adında kip listesinin özeti). Anlatımın ölçülen yüksekliğine göre:
   konuşmada `seviye` (-22 dB), konuşmasızda `acik` (-15 dB). Kısma anahtarı anlatım izi (20 ms RMS, eşik -42 dBFS,
   0,35 sn tutma, 0,12 sn atak, 0,7 sn bırakma): cümle aralarında pompalama yok, kartlarda müzik açılır.
   Müzik seviyesi eğrisi: sahne `muzik_db` ve `muzik` olayları kısma zarfıyla çarpılır (soğuk açılışta kısık, B3'te
   incelme, bir an sessizlik, bitiş ekranında açık).
3. Efektler ayrı veriyolunda toplanır, anlatımın altında yan zincirle kısılır (`efekt_kismasi`) ve eklenir.
   **Tepe sınırı** (4. tur, `tepe_siniri`): altlığın (müzik + efekt) 100 ms RMS'i medyan konuşma seviyesinin (anlatımın
   konuşulan 100 ms pencereleri) en çok `TEPE_PAYI_DB` (2 dB) üstüne çıkar; bölüm kartı boom/whoosh'u, imza, damga ve
   doruk boom'u kulaklıkta sıçratmasın (talidomit-turkiye 3. tur: +7,5-8,7 dB). `olcum.json`: `altlik_en_yuksek_ustu_db`
   (sınırdan önce), `tepe_siniri_en_cok_db`.
4. Normalizasyon: ölç -> kazanç + tepe sınırlayıcı (alimiter) -> ölç -> `loudnorm ... linear=true` -> -14 LUFS.
   WAV'ın tepe hedefi -2 dBTP (`ses.WAV_TP` = `HEDEF_TP` - `KODEK_PAYI`): AAC kodlaması gerçek tepeyi iki yöne de
   ~0,5-1 dB oynatıyor (talidomit-turkiye'de WAV -1,5 -> mp4 -0,9 dBTP çıktı). Render sonunda mp4'ün kendisi ölçülür
   (`mp4_lufs`, `mp4_tepe_dbtp`; paketteki "Ölçüm (mp4)" satırı); teslim edilen dosya -14 LUFS / <= -1 dBTP olmalı.
   `olcum.json`'da `loudnorm_turu: linear` olmalı.
5. `out/<id>-uzun/<id>_anlatim.wav` (yalnız anlatım) ve `<id>_altlik.wav` (müzik + kısılmış efektler): ikisi de miksle
   aynı toplam kazançta, sınırlayıcısız, 32 bit kayan nokta. (4. tur: anlatım izi mono -> stereo `pan` ile yazılır;
   `-ac 2` -3 dB merkez karışımı uyguluyordu, iz miksten 3 dB alçaktı.) Sınırlayıcı `latency=1` (4 ms gecikme yok) ve
   4x örneklemede (192 kHz) çalışır: 48 kHz'de örnekler arası tepe sınırın ~3 dB üstüne çıkıyor, döngü sınırı
   -9,7 dBFS'e indirip sesin ~4,6 LU'sunu eziyordu; şimdi ~1 LU. AAC 320 kb/sn. **Anlatım / altlık oranını bu ikisinden ölç**; "miks -
   anlatım" farkı miksin sınırlayıcısının sesin tepelerinden kestiğini de altlık sayar (talidomit-turkiye 2. tur:
   gerçek oran 50 ms karelerde medyan 23 dB, %5'lik dilim 7 dB; fark yöntemiyle medyan 8 dB çıkıyordu).

## 5. Render ve senkron

- Sahneler en fazla 180 karelik parçalara bölünür; parçalar `ProcessPoolExecutor` (fork) ile paralel çizilir ve her biri
  `libx264 -preset faster -crf 18 -pix_fmt yuv420p -bf 0 -profile:v high -g 60 -r 30` ile ayrı mp4'e yazılır.
  `--preset medium` daha küçük dosya, 2 kat yavaş (darboğaz kodlayıcı).
- Parça önbelleği: anahtar = sahne içeriği + zamanlama + görsel dosya tarihleri + motor kodunun özeti. Yalnız değişen
  sahneler yeniden çizilir.
- Renk: RGB -> YUV dönüşümü BT.709 matrisiyle, akış BT.709 + sınırlı aralık etiketli (`render.RENK`, her parçada aynı).
  Etiketsiz HD'yi YouTube BT.709 diye çözüyor; eskiden swscale BT.601 ile dönüştürdüğü için renkler kayıyordu
  (Türkiye yeşili (60,255,140) -> (45,229,138)).
- Birleştirme: concat demuxer `-c copy`; ses AAC 48 kHz eklenir (`+faststart`, dil etiketi `tur`, edit list ile AAC ön
  dolgusu atlanır).
- `dogrula()`: video ve ses 0.000'da başlamalı, süre farkı < 1 kare, kare sayısı = zaman çizelgesi.
- Ön izleme: 960x540, `veryfast`, aralık kare/örnek hassasiyetinde kırpılır.

## 6. Küçük resim (`kucukresimler`)

`ad`, `arka`, `karart`, `bulanik`, `odak`, `karakterler` [{gorsel, taraf, boy, x, bakis}] (beyaz "çıkartma" konturu,
içeri bakar), `yazi` (2-4 kelime, Anton, büyük harf, kalın kontur; en dengeli 1-2 satır), `vurgu_kelime` (sarı), `yazi_y`,
`yazi_bolge` [x0, x1] ya da [x0, x1, y0, y1] (yazının alanı; karaktersiz haritada boş deniz gibi),
`ek` {gorsel, konum sag_alt/sol_alt/sag_ust/sol_ust/orta_alt, boy, egim} (beyaz kenarlı arşiv görseli), `ok` {bas, son},
`daire` {x, y, r}. JPEG < 2 MB. Filigran sol altta (sağ alt YouTube'un süre rozetinin altında kalıyor). Telifli görsel
içeren varyant için `teslim` uyarır (teslim/ repoya girer).

## 7. Paket (`paket`)

`baslik_alternatifleri`, `aciklama` (ilk paragraf), `short_url` (yoksa yer tutucu + "yayımlanmadıysa sil" maddesi),
`short_baglanti`, `etiketler` (<= 500 karakter), `sabit_yorum`, `kaynaklar`, `gorsel_atif`, `telif_notu` (liste:
hesap sahibinin lisans kararları için "Telif notu" bölümü), `ara_reklam` (bölüm numarası -> o bölüm kartının İÇİNDEKİ
ilk tam saniye, ya da metin), `yapay_icerik` ("Değiştirilmiş ya da yapay içerik" maddesinin önerisi), `dinle`
(`[{ara: "cüzzam", not: "..."}]`: yayından önce kulakla dinlenecek satırlar; satırın başladığı an zaman çizelgesinden
yazılır, süre değişince kayar), `ek_maddeler` (kontrol listesine). Dinleme listesi zamana göre sıralı yazılır.
Açıklama YouTube API'sinin 5.000 **bayt** sınırına göre de denetlenir (Türkçe harf 2 bayt; Short bağlantısı payı dahil). Bölüm zaman damgaları zaman çizelgesinden hesaplanır
(bölümün ilk sahnesinin, yani kartın başı, **yukarı** yuvarlanır: damga kartın içine düşer; ilki 0:00; kartsız bölümde **aşağı**: yukarı yuvarlanınca ilk kelime kesiliyordu, 5. tur; bindirme kartı tam saniyeden en çok 0,1 sn sonra başlıyorsa da **aşağı**: o an bindirmenin dondurduğu karenin kendisi, 6. tur: yukarı yuvarlanan damga kartın son ~0,25 sn'sine düşüyordu). Bitiş ekranı
öğelerinin başlangıcı da yukarı yuvarlanır (daha erken başlarsa kapanış sahnesinin üstüne biner). Denetim: >= 3 bölüm, her biri >= 10 sn, artan sıra.
Kontrol listesinde "Shorts > İlgili video" bağlantısı ve bitiş ekranı maddeleri var.

## 8. Denetimler (`kontrol`)

- **Altyazı blok ipucu:** satır `metin`indeki satır sonu (`"…gösteren\nönemli bir çalışma…"`) SRT bloğunu orada
  böler; ekrandan ve TTS metninden çıkarılır (önbellek anahtarı değişmez). Sayılar altyazıda rakamla: `metin`
  rakamlı, `tts` kelimeli (anahtar TTS metninden).
- **Altyazı kırılma kuralları** (`altyazi.kirma_cezalari`, 5. tur dil hakemi): soru ekinden (mi/mı/miydi…) önce, belirleyiciden (bir/o/bu/en/her/yarım/aynı…) sonra, sayı (rakamlı ekli sayılar ve 'milyonu' dahil) ile birimi arasında, ilgi hâli ekinden ('Grünenthal'in | laboratuvarında') sonra, ek-fiilden ('yetersiz | olduğunu') önce, sıfat + ad ('günlük | doz') ve özel ad + iyelikli ad ('Behçet | hastalığındaki') arasında kırmak cezalıdır (yasak değil).
- **Altyazı kelime farkı:** SRT'nin kelimeleri satır metinleriyle birebir aynı olmalı (`altyazi.kelime_farki`). Bölme
  hiçbir zaman kelime atmaz: sığmayan birleşim yapılmaz; uzun yan cümle kelime sınırlarından EŞİT parçalara bölünür
  (tek kelimelik yetim parça yok).
- **Hareket:** her sahnenin "vuruşları" (giriş, balon, yüz, etiket, ülke, nokta, kutu, sayaç başı/sonu, olaylar) toplanır;
  `max_bos` (6 sn) boyunca ekrana yeni bir şey gelmiyorsa zaman aralığıyla uyarır.
- **Bölüm:** YouTube kuralları. **Altyazı:** 42/2/1 kuralları. **Paket:** başlık <= 100, etiket <= 500, açıklama <= 5000.
- **Bitiş ekranı:** `bitis` sahnesi son sahne, 5-20 sn (paket kontrol listesine başlangıç anı yazılır).
- **Aynı kayıt:** aynı ses + aynı TTS metni + aynı hız/duygu = aynı önbellek anahtarı = birebir aynı dosya (ör. Aylin'in
  "Tamamen zehirsiz." kaydı açılışta ve sonda); `kontrol` bu grupları "aynı kayıt (n kez, tek seslendirme)" diye listeler,
  görünen metni ve sesi aynı ama ayarı farklı satırlar için uyarır (`tts.tekrarlar`).
- **Ses QA:** `seslendir --qa` isim geçen satırları faster-whisper "medium" ile dinler (ses ffmpeg ile 16 kHz diziye
  çözülür; kütüphanenin kendi çözücüsü kurulu PyAV ile bozuk), benzerlik < 0,72 ise "KONTROL ET". İsim dışı kelimeler de
  denetlenir (`tts.kelime_farklari`, eşik 0,96: 'denenmiyor' -> 'denemiyor', 'cüzzam' -> 'cüzdan'); `--tum` bütün
  satırları dinler. `--yenile N`: başarısız satır en fazla N kez yeniden üretilir, en iyi deneme seçilir
  (`out/<id>-uzun/ses/manifest.json`, `secim`; `secim` elle onarılmış bir dosyaya da işaret edebilir, ör.
  `uzun/talidomit-turkiye/ses_onarim.py`). Döngüye girmez. Not: Whisper nadir adları (talidomit, Lenz) bazen yanlış
  yazar; rapor dinleyip karar vermek içindir.
- **TTS kotası yokken onarım** (`uzun/talidomit-turkiye/ses_onarim.py`, 3. hakem turu): satırlar METNE göre bulunur;
  cümle başındaki bağlaç ya da yanlış okunan ilk cümle kapantı/sessizlik çukurundan kesilir (yaml'da satırın metni de
  kısalır, yeni anahtar onarım dosyasına bağlanır); ikiz ünsüz yanlış okunuyorsa ("cüzzam" -> "cüzdan") z bölümü
  taneli örtüşmeli toplamla ~2 kat uzatılır; hızlı satır rubberband (perde/formant korunur) ile yavaşlatılır. Her
  sonuç iki Whisper çözümlemesiyle (ışın 5 ve 1) dinlenir; komşu parametrelerde de doğru duyulan ayar seçilir.
  Paketteki `dinle` listesi bu satırları hesap sahibinin kulak kontrolüne zaman damgasıyla verir.
  Whisper "talidomit"i bağlama göre "talih domit" diye bölebiliyor: başka satırdan tek kelime duyulan temiz çekim
  nakledildiğinde de bölündü (TTS kusuru değil, tanıyıcının dil modeli).

## 9. Varlıklar ve lisans

| Varlık | Yer | Lisans |
|---|---|---|
| Harita | `assets/harita/ne_{110m,50m}_admin_0_countries.geojson.gz` | Natural Earth, kamu malı (`assets/harita/LISANS.md`) |
| Daktilo yazısı | `assets/fonts/LiberationMono-Bold.ttf` | SIL OFL 1.1 (`OFL-Liberation.txt`) |
| Efektler | `assets/sfx/*.wav` | kendi sentezimiz (`tools/make_sfx.py`; 2. turdakiler numpy ile: `gecis`, `turkiye`, `turkiye_major`, `kapi`, `damga`, `geri_sarma`, `raptiye`, `telefon`, `marka`) |
| Mantar ve kâğıt dokusu | üretilir (`bilgi.mantar_dokusu`, `zemin.kagit_dokusu`) | kendi sentezimiz |
| Müzik | `out/<id>-uzun/muzik/` (üretilir) | kendi sentezimiz (`wojak/uzun/muzik.py`) |
| Kanal yazısı | `assets/fonts/ozel/` (Avenir, yerel) | lisanslı, repoya girmez; yoksa Poppins |

Repoya girmeyenler: `out/`, `uzun/*/img/telifli/`, `teslim/*/*.mp4`, `assets/fonts/ozel/`, `assets/music/ozel/`, `referans/`.

## 10. Ölçümler (demo, 12.10.2026, 4 çekirdek)

`uzun/demo` (61,5 sn, 11 sahne, 15 satır, 2 ses, 86 efekt): render 1920x1080 **~29-30 kare/sn** (3 işçi, `faster`;
4 işçi aynı; `medium` ile ~17), video ~62 sn + ses ~23 sn; değişmemiş parçalar önbellekten (yeniden render ~5 sn).
Ses -14,0 LUFS, WAV'da -1,7 dBTP, AAC sonrası -2,3 dBTP, LRA 3,6, loudnorm doğrusal (sınırlayıcı -3,6 dBFS);
müzik konuşmada anlatımın ~23-25 dB altında. Video ve ses 0,000'da başlıyor, süre farkı 0 ms, 1845/1845 kare, B-kare yok.
Ön izleme (960x540) ~125 kare/sn. TTS: 15 satır ~27 sn; Whisper QA 4 isimli satır, 1 yeniden deneme sonrası hepsi tamam.
9 dakikalık bir video için tahmin: ~9 dk render + ~2-3 dk ses (ilk seferde müzik üretimi ~1 dk).

### 2. tur (12.10.2026): demo 98,8 sn, 15 sahne, 22 satır

Ön izleme (960x540, 3 işçi) ~110-120 kare/sn; ses -14,0 LUFS, -1,6 dBTP, loudnorm doğrusal; video/ses 0,000'da, fark
0,3 ms, 2965/2965 kare. 1920x1080 tek süreçte kare başına: wojak (3 karakter) ~55 ms, sayac/metin/zaman çizelgesi
~45-50 ms (zeminin kamera yeniden örneklemesi ~25 ms), bolunmus (iki görsel) ~43 ms, (iki metin paneli) ~90 ms, izgara
(10.000 nokta) ~72 ms, pano ~55-60 ms, bitis ~52 ms, marka/kart ~35 ms. 3 işçiyle 9-10 dk'lık video için kodlayıcı yine
darboğaz civarında (~8-10 dk).

## 11. Senaryo istekleri (senaryo_v2 §F) ve karşılıkları

| # | İstek | Motorda |
|---|---|---|
| 1 | Bindirme bölüm kartı (son kare donar, %40+ karartma, 1,2 sn; B1'de marka imzasıyla) | `kart_bindirme: true` (üst düzey ya da bölüm), `zamanlama.bindirme: 1.2`, ilk kartlı bölümde `kart_marka: true`; müzik kesilmez |
| 2 | Bölünmüş ekran, ikincisi kayarak açılır | `tip: bolunmus` + `panel`, `soluk`, `buyut` olayları (KP.2: `buyut`) |
| 3 | Nokta ızgarası + yüzdesel sönme | `tip: izgara` (`n: 10000`) + `sondur {oran: 0.4}` (ayrı tip: sayacın sayısı yerine noktalar) |
| 4 | Soruşturma panosu | `tip: pano` (`kartlar`, `ipler`, `kart`/`ip`/`damga kart:` olayları, `kose` ile "YAYIMLANMIŞ BELGE: 0") |
| 5 | Azalan sayaç (60 -> 0) ve köşe sayacı (GÜN 0/12) | `sayac` `deger: [60, 0]`; sahne `kose` + `kose` olayı (her sahnede, birden çok sahneye yayılabilir) |
| 6 | Takılı yıl göstergesi ("1961 -> ????") | `kose: {deger: 1961, yil: true}` + `{tip: kose, deger: "????", takili: true}`; B6.4'te `{tip: kose, deger: 2018, sure: 3}` sayarak akar |
| 7 | Türkiye ses motifi olayı | `assets/sfx/turkiye.wav` (B6.6 için `turkiye_major.wav`), sahne `sfx` listesiyle satıra çapalı |
| 8 | Aylin kaydının yeniden kullanımı | aynı metin + ses + hız = aynı önbellek dosyası; `uzun kontrol` "aynı kayıt" satırıyla doğrular, ayar farkında uyarır |

Ek olarak senaryonun sık kullandığı: lastik damga (`damga` olayı), kâğıt dokusu zemin (`zemin: kagit`), daktilo metin
(`yazim: daktilo`), viral iddianın üstünü çizme (`ustunu_ciz`), müzik incelmesi/sessizliği (`muzik_db`, `muzik` olayı),
kanal imzası (`marka`), bitiş ekranı (`bitis`), yeni efektler (kapı, geri sarma, telefon, raptiye).

## 12. Bilinen sınırlar

- Karakterler alt pikselde yerleşir (`cizim.alt_piksel`: ölçek + kesirli konum tek örneklemede, önceden çarpılmış
  alfa; 713 px boyda ~9 ms). Balonlar, isim etiketleri ve damgalar hâlâ tam piksele yuvarlanır (kamera itmesinde
  balon 1 px adımlarla kayabilir).
- Harita bugünkü sınırları gösterir (1957'nin Batı/Doğu Almanya'sı yok); gerekirse anlatımda belirt.
- Balon yerleşimi karakterin başının üstünü varsayar; çok uzun (boy > 0,8) karakterde balon kadraj üstüne yaslanır.
- Altyazı parçalarının satır içindeki zamanlaması uzunlukla orantılı tahmindir (kelime zaman damgası yok).
- Whisper QA yalnız isimlere bakar; vurgu/tonlama hatalarını yakalamaz.
- Konuşma sekmesi dudak senkronu değildir: hece başlarına küçük sekme. Kamera itmesi arka planın kenar payıyla sınırlıdır
  (konuşana kayma en çok ~%3-4 kadraj).
- Derinlikteki karakter yükseltilmez (kit görselleri göğüsten kesik); uzaklık küçüklük, sis ve çizim sırasıyla verilir.
- Pano kart yerleri elle (`x`, `y`); damga kartın genişliğine sığdırılmaz (`boy` ile ayarla). Bölünmüş ekranda görsel
  panel pencereden görünür (yarı genişlikte kırpılır), metin paneli görünen yarıda ortalanır.
- Nokta ızgarası 10.000 noktada 960x540 ön izlemede doku gibi görünür (nokta ~4 px); asıl render'da 9 px aralık.
