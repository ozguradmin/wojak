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
| `kanal.py` | marka (kanal imzası / sting), bitis (YouTube bitiş ekranı, iki video kutusu), `logotip()` |
| `kapanis.py` | 7. tur: kapanış çağrısı (`kapanis`): soru + seçenek kartları + imleçle abone/zil/beğen + yorum balonu; kendi simgelerimiz (imleç, zil, başparmak) |
| `zemin.py` | Bilgi sahnelerinin zemini (koyu / kagit / foto), palet (koyu zeminde beyaz-sarı, kâğıtta mürekkep), boşta hareket (süzülme, toz, ışık, gren) |
| `ust.py` | Her sahnede: lastik damga (`damga` olayı), köşe göstergesi (`kose`) |
| `yerlesim.py` | 10. tur: karakter görselinin alfa kutusu ve yüz bölgesi (`yuz_kutusu`: baştan boyuna), çokgen geometrisi (ayırıcı eksen), isim etiketi metnini ikiye bölme, `kontrol`ün üst katman çakışma denetimi (`denetle`) |
| `cizim.py` | Yazı, gölge, yuvarlak kutu, alt piksel afin yerleştirme, Ken Burns, gren, vinyet; 7. tur: `bindir_alt` (kesirli konum), `hareket_izi` (hareket bulanıklığı), `yatay_bulanik` (itme geçişi), `afin_pm` (önceden çarpılmış alfa ile döndürme), `tabular_yazi`, `cizgi_katmani`, `golge_katmani` |
| `harita.py` | Natural Earth verisi (indir/sadeleştir), LAEA / Equal Earth projeksiyonu, taban + ülke maskeleri |
| `easing.py` | out_cubic, in_cubic, in_out_cubic, in_out_sine, out_back (küçük taşma), tumsek |
| `render.py` | Paralel parça render (fork, varsayılan 3 işçi), aynı kodlayıcı ayarlı parçalar, concat `-c copy`, ses ekleme, senkron doğrulama |
| `ses.py` | Anlatım zaman çizelgesi, müzik altlığı + yan zincirli kısma, otomatik efektler, iki geçişli loudnorm, anlatım izi |
| `muzik.py` | Kendi müzik altlığımız (Do minör drone + seyrek vals motifi), `tools/uzun_muzik.py` ile dinlenebilir |
| `altyazi.py` | SRT: <= 42 karakter/satır, <= 2 satır, >= 1 sn, çakışmasız; anlatıcıdan başka sesin satırı (alıntı) `<i>…</i>`; 10. tur: satır içi sınırlar sesin iç sessizliklerine metne göre oturur (`sinirlari_hizala`) |
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
| `gecis` | `kesme` | varsayılan giriş geçişi: `kesme` / `gecis` (8 kare crossfade) / `kaydir` (10 kare push) / `karart` (9. tur: 10 karelik karanlıktan geçiş; önceki kare koyuya söner, yenisi koyudan açılır: aynı karakterli sahneler, yazıdan yazıya geçiş, kâğıt/koyu parlaklık sıçraması) |
| `filigran` | `tarihselwojak` | `false` = yok |
| `hareket` | bulaniklik/ikincil/canli: true, paralaks: 0, doku: false | 7. tur hareket dili (aşağıda "Hareket dili") |
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
| `tip` | `wojak`, `foto`, `manset`, `harita`, `sayac`, `bolum_karti`, `metin`, `zaman_cizelgesi` (takma: `liste`), `bolunmus`, `izgara`, `pano`, `marka`, `bitis`, `kapanis` (takma: `cagri`, `cta`) |
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
| `konuk` | (wojak dışı her tip) köşeden/kenardan giren **tepki karakteri** (1-3; 10. tur: 3. öğe ör. karakterin elindeki nesne): `{id, gorsel, x, boy, alt, giris, yon: alt\|sol\|sag, bakis}`; `yuz` / `giris` / `cikis` olayları ve `isim {karakter}` konuk kimliğiyle her tipte kullanılır; kamerasız (ekran koordinatı), yazı katmanlarının altında çizilir; giriş/çıkışta `whoosh_kisa`. 4. tur (talidomit-turkiye): hesap sahibi "wojak kanalı: harita/sayaç/pano tek başına yetmez" dedi; karakterli süre %26 -> %68. Yazıyla çakışmasın: konuk köşedeyken `kelime` `konum: ust`, foto baskısı `x` ile yana |

**Süre:** `bas + satır1 + ara + satır2 + ... + son`, en az `min_sure`; kare sayısına yuvarlanır. Satır sesleri örnek
hassasiyetinde, sahneler kare sınırında başlar: görüntü-ses kayması olmaz.

**Çapa:** `satir: n` (1'den) + `ofset` (sn, eksi olabilir) + `an: bas|son` (satırın başı/sonu); satır yoksa `t`
(sahne başına göre sn). Sonuç sahne süresine kırpılır.

### Olaylar

| tip | Sahne | Parametreler | Ne yapar |
|---|---|---|---|
| `yuz` | wojak (ya da konuklu sahne) | `karakter`, `gorsel`, `sik`, `buyu` | yüz varyantına geçer (kısa sıkışma; 8. tur: `sik: false` sıkışmasız: kapı kanadının 2 karelik ara çizimleri gibi art arda geçişler; 9. tur: `buyu: true` yeni görsel eskisinin görünür boyundan out_back ile 0,3 sn'de büyüyerek oturur: doz şişesi tek karede 1,3 kat büyüyordu) |
| `balon` | wojak | `karakter`, `metin`, `sure`, `agiz` | konuşma balonu (pop ile açılır; kuyruk konuşana). 9. tur: `agiz` = aynı tuvalde açık ağızlı yüz: balon açıkken hece vuruşlarında (konuşma değeri > 0,3) bu görsele geçer (animasyon hakemi: balon repliklerinde oyunculuk yoktu). **11. tur: `agiz: [yarık, açık]`** (animasyon hakemi S6: gülümseyen temsilcinin ağzı her hecede ince sırıtışla geniş hilal arasında gidip geliyordu, telefonda yanıp sönen sırıtış): zaman 4 karelik adımlara bölünür (`Karakter.AGIZ_ADIM`; saniyede en çok 7,5 değişim), adımdaki en yüksek konuşma değeri > 0,55 açık, > 0,2 yarık; kapalıdan açığa (ya da tersi) atlanmaz, araya yarık adımı girer. Tek görselde de 4 kare tutulur |
| `giris` / `cikis` | wojak (ya da konuklu sahne) | `karakter` | karakter kenarından (ya da `yon: alt` ise alttan) kayarak girer / çıkar |
| `isim` | hepsi | `ad`, `unvan`, `sure`, `konum` (sol/sag) ya da `karakter` | alt bant (lower third), kayarak girer/çıkar. **11. tur: sahnenin sabit kutuları da engel** (`Cizici.sabit_engeller()`; foto: atıf satırı. Animasyon hakemi S4: Kelsey'nin etiketi "(kamu malı)" atfını örtüyordu). **10. tur: yerini kendisi seçer** (animasyon hakemi M1: iki etiket 4-5 sn çeneye/ağza biniyordu): kutusu her karakterin alfa kutusundan en az 40 px (`yerlesim.BOSLUK`; `canli: false` nesneden 8 px), öteki üst katmanlardan 20 px uzak. Sıra: istenen kenar (`konum`; `karakter` verilince onun tarafı) > o karakterin hemen yanı > öbür kenar > engellerin arasındaki boşluk; sığmazsa en geniş satır iki satıra (` · `/virgülden), sonra ikisi, sonra %86 boy. Hiçbir yer temiz değilse yüzü değil gövdeyi örten yer seçilir ve `kontrol` uyarır; küçültme de bildirilir (telefonda küçük). Kenardaki etiket kenardan kayarak, boşluğa yerleşen kısa kayma + belirmeyle gelir (karakterin üstünden geçmesin) |
| `kelime` | hepsi | `metin`, `sure`, `konum` (ust/orta/alt) | ekranda vurgu kelimesi (pop) |
| `etiket` | wojak, foto, manset | — | daktilo etiketinin başlama anı |
| `vurgula` | manset | `kutu` (1'den), `stil` (kalem \| daire \| alt_cizgi), `renk` | kalem: fosforlu kalem o kutudan geçer; daire: elle çizilmiş kırmızı çember (geniş kutuda süperelips: satır aralığında kalır, komşu satırların üstünü çizmez), alt_cizgi: dalgalı, sonu kıvrık alt çizgi (0,7 sn'de çizilir; efekt `kalem`) |
| `basla` | sayac, harita, zaman_cizelgesi, izgara | `sure` (sayac) | ana animasyon başlar; 10. tur: sayaçta `sure` ilk sayımın süresi (`sure_say` yerine) |
| `ulke` | harita | `kod` | o ülke (ya da vurgu ülkesi) bu anda yanar |
| `nokta` | zaman_cizelgesi | `indeks` (1'den) | o nokta bu anda belirir |
| `ceviri` | metin, bolunmus | `taraf` (bolunmus) | çeviri satırı belirir |
| `damga` | hepsi | `metin`, `renk` (kirmizi/yesil/mavi/... ya da [r,g,b]), `x`, `y` (0..1), `aci` (-8), `boy` (84), `sure` (yoksa sahne sonuna dek), `kontur` (true = beyaz ya da renk: harf ve çerçeve çevresine ince dolu kenar; koyu/desenli zeminde okunurluk; açık zeminde beyaz damgaya koyu kontur `[24, 24, 30]`), `kart` (pano), `kart_y` (kart merkezine göre, kart yüksekliği oranı; vars. görselli kartta görselin ortası, görselsizde 0.2: başlık okunur kalır), `inik` (true: sahne başında zaten basılı, iniş/ses yok: bölünmüş çekimin devamı; 11. tur: `sure` ile birlikte sahne başından `sure` sn sonra söner: eşleşen kesmede önceki sahnenin damgası taşınır) | lastik damga ekrana çarparak iner (mürekkep dokulu, çift çerçeve); efekt `damga` |
| `kose` | hepsi | `deger`, `metin`, `sure` (0,6), `takili`, `renk`, `yil` | köşe göstergesi yeni değere sayar (sayı) ya da yuvarlanır (metin); `takili: true` basamaklar karışıp takılır ve ara ara titrer ("1961 -> ????"); yıl göstergesinde (`yil`) takılırken yıl **geriye gitmez** (9. tur, izlenme S1: "40+ YIL SONRA" altında 1948 ve 1987 görünüyordu): eski yıldan hedef yüzyıla ("20??" -> 2000; "????" -> eski + 45) hızla ileri akar, sonra takılır; titreşimde de yalnız eski yıldan sonraki yıllar |
| `muzik` | hepsi | `db`, `gecis` (rampa sn, 0,5) | müzik seviyesi bu andan itibaren (incelme, bir an sessizlik: `db: -40`) |
| `deger` | sayac | `deger`, `etiket`, `renk`, `sure` (1,2), `onek`, `sonek` | sayaç bir önceki değerden yenisine sayar; etiket ve renk değişebilir. `sure: 0`: sayım yok (tık yok, yalnız vuruş; 6. tur: 20.000 -> 17 geri sayarken "en az 16.043" görünüyordu); 10. tur (animasyon hakemi S2: "≈20.000" -> "en az 17" tek karede kesme gibiydi): yeni değer 0,26 sn'de tekerlek penceresinde **yuvarlanarak** gelir (eski yukarı çıkar, yeni alttan out_back ile oturur; `SAYAC_GECIS`), oturduğu anda (`varis`) yumruk + renk parlaması ve `hit`. Değişen önek (1.267 -> "≈20.000") 0,22 sn'de açılır. **Her değer, sonraki değişimden önce yerleşir ve en az `tut` (0,6 sn) okunur kalır**: sayım gerekirse kısalır (en az 0,6 sn), yetmezse sonraki değer ertelenir (`kontrol` ikisini de bildirir; animasyon hakemi M2: "1.267 doktor" hiç okunmuyordu) |
| `panel` | bolunmus | `taraf` (vars. sag) | panel kayarak açılır, ekran ikiye bölünür |
| `soluk` | bolunmus | `taraf` | panel kararıp renksizleşir |
| `buyut` | bolunmus | `taraf` | panel büyüyüp ekranı kaplar (1,2 sn) |
| `kart` | pano | `id` | kart iğnelenir (düşer + raptiye) |
| `ip` | pano | `a`, `b` | iki kartın raptiyeleri arasına kırmızı ip gerilir (`ipler` listesinde yoksa eklenir) |
| `sondur` | izgara | `oran` (0..1), `sure` (1,6), `etiket` | yanık noktaların o oranı rastgele ve sessizce söner (silik iz kalır); etiket yenisiyle değişir |
| `ustunu_ciz` | metin | `renk` | ana yazının üstü satır satır kırmızı çizgiyle çizilir; efekt `kalem` |
| `rota` | harita | `a`, `b` (ISO3 kodu ya da [boylam, enlem]), `sure` (1,2), `kavis` (0,22), `kesik`, `renk` (sarı), `etiket` | a'dan b'ye yukarı kabaran yay çizilerek uzanır (gölgeli; ucunda parlayan nokta, varışta genişleyen halka + kalıcı nokta, isteğe bağlı etiket); efekt: çizimde hafif `whoosh_kisa`, varışta `blip` |
| `tikla` | kapanis | `hedef` (abone \| zil \| begen \| yorum) | imleç bu anda hedefe tıklar (varsayılan sıra ve anlar aşağıda) |
| `secenek` | kapanis | `indeks` (1'den) | seçenek kartı vurgulanır; olay verilirse varsayılan sıra yerine bunlar |
| `sarsinti` | hepsi | `guc` (px, 1080p; 7), `sure` (0,1) | 8. tur: kamera sarsıntısı (kapı çarpması, darbe): bütün kare sönümlü, yön değiştiren ötelemeyle kayar (kenar boşluğu kalmasın diye o kadar büyür); filigran sarsılmaz |
| `it` | wojak | `guc` (0,08), `sure` (0,5), `x`, `y` | 9. tur: kamera vurgu itmesi: o andan itibaren zoom x(1+guc) out_cubic ile; `x`/`y` verilirse merkez oraya kayar; kalıcı (sahnenin kendi kamerasıyla çarpılır). Tek çekimde "yakın plan": B1.1'de takvim çıkarken kutuya ve anlatıcıya itme (aynı zeminli kesme süreklilik hatası gibiydi), SA.6'da kapıya |

Sahne tipine özgü bir olayı başka tipte kullanmak hata verir (ör. `sondur` yalnız izgara).

### Sahne tipleri

| tip | Parametreler | Görüntü |
|---|---|---|
| `wojak` | `arka`*, `kirp` [x0,y0,x1,y1], `odak`, `vinyet` (0.42; düz zeminde bilinçli yakın çekim için 0.7-0.8), `kamera` {zoom: [a,b], merkez: [[x,y],[x,y]], `it` (0.05), `odak` (0.4), `paralaks`}, `karart`, `bulanik`, `doygunluk`, `etiket`, `doku` (true \| {gren, toz}), `karakterler` (1-4: `id`, `gorsel`*, `taraf` sol/sag/orta, `x`, `boy` 0.66, `giris` true/false/sn, `yon` sol/sag/alt/ust/pop (giriş yönü; pop: yerinde büyüyerek belirir), `bakis`, `alt`, `derinlik` 0..1, `canli` (false: dekor/nesne, nefes-salınım-eğim yok), `golge` (8. tur: true = sağ alta düşen yumuşak gölge; havada duran nesne masaya konmuş çıkartma gibi okunur)) | Ken Burns arka plan; karakterler kenardan out_back (%4-5 taşma) ile kayarak girer, nefes alır (±%1, 0,3 Hz) ve hafif sallanır, `data/karakter_yon.json`'a göre hep içeri bakar (gerekirse aynalanır). **Kamera** arka planı, karakterleri ve balonları birlikte taşır; biri konuşurken (`balon`/`konusan` satırı, `balon` olayı) konuşana doğru yumuşakça yaklaşır (`it`: zoom artışı, `odak`: merkezin kayma oranı; `it: 0` kapatır). **Konuşma sekmesi**: konuşan karakter satırın sesindeki hece başlarında (10 ms RMS'te > 6 dB yükseliş) küçük bir sekme ve dikey esneme yapar; ses yoksa yapay hece ritmi. **Derinlik** (3 karakterde arkadaki): küçülür (1 - 0,3·d), hafif sisli, az doygun, önce çizilir; taban kadraj altında kalır (kit görselleri göğüsten kesik) |
| `foto` | `gorsel`*, `etiket`, `atif`, `egim`, `giris` (alt/ust/sag/sol), `boy` 0.72, `zoom` 1.05, `arka`, `x` (baskının yatay merkezi, 0.5; ortada değilse atıf baskının altına yazılır: köşedeki konuğa binmesin) | aynı fotoğrafın bulanık-karartılmış hâli üzerinde beyaz kenarlı, gölgeli, eğik "baskı"; düşerek oturur, deklanşör sesi; yavaş yaklaşma; daktilo etiketi |
| `manset` | `gorsel`*, `kutular` (piksel ya da 0..1), `zoom` 1.18, `renk`, `boy`, `arka`, `etiket` | belge/manşet; kutular sırayla fosforlu kalemle (çarpma karışımı, pürüzlü kenar) boyanır; kamera yaklaşır ve kalemi dikeyde izler |
| `harita` | `bolge` (avrupa, bati_avrupa, akdeniz, turkiye, dunya ya da {merkez, sinir}), `ulkeler` (ADM0_A3), `aralik`, `etiketler`, `vurgu` {kod, etiket, renk, ad}, `baslik`, `aciklama` (lejant), `renk`, `zoom`, `cozunurluk` (50m/110m) | ülkeler sırayla parlayarak yanar; vurgu ülkesi farklı renk, nabız gibi atan halka ve çağrı kutusu |
| `sayac` | `deger` (ya da azalan `[60, 0]`) ya da `yil` [a, b], `onek`, `sonek` ("+"; azalanda yok), `ust`, `etiket`, `sure_say` (ya da `basla {sure}`), `renk`, `olcek` (9. tur: `log` = geometrik sayım, her basamak eşit sürede eklenir; 0 -> 300 milyon out_cubic'te ilk karede 8 basamağa sıçrıyordu), `tut` (10. tur: değer değişmeden ve sahne bitmeden önce en az okunma süresi, 0,6), zemin | sabit genişlikli rakamlarla sayma (artan out_cubic, azalan doğrusal); yıl modunda odometre gibi dönen basamaklar; bitişte vuruş + çizgi; `deger` olaylarıyla yeni değerlere (1.267 doktor -> 20.000 hasta -> EN AZ 17); bitince sayı nefes alır |
| `bolum_karti` | (bölümden) `numara`, `baslik`, `ust`; `bindirme`, `marka`, `karart` (0.45) | siyah zemin + gren (ya da bindirme: donmuş son kare kararır ve bulanır, hafif yaklaşır), ortadan açılan sarı çizgi, "BÖLÜM n", soldan silinerek açılan başlık; kısa kartta animasyon orantılı sıkışır |
| `metin` | `metin`*, `ceviri`, `ust`, `alt`, `ceviri_t`, `yazim` (kelime/daktilo), `renk`, `tirnak` (süs tırnağı; vars. yalnız metin tırnakla başlıyorsa), zemin | kelime kelime beliren büyük alıntı (daktilo: harf harf, imleçli, tuş sesli); çeviri koyu zeminde sarı + altı sarı şerit, kâğıtta mürekkep + fosforlu kalem; satırlar hafifçe süzülür |
| `zaman_cizelgesi` | `noktalar`* (2-8; `tarih`, `metin`), `baslik`, zemin | eksen çizilir, noktalar sırayla pop'lar, ilerleme çizgisi, etkin nokta nabız; yazılar süzülür |
| `bolunmus` | `sol`*, `sag`* (panel: `gorsel` ya da `metin` + `ceviri`, `etiket`, `baslik`, `alt` (40 px, koyu bantta, panelin sol altında; 5. tur: 24 px okunmuyordu), `odak`, `zoom` (9. tur: metin panelinde de: zemin daha çok yaklaşır, yazı bloğu hafifçe büyür), `say` (9. tur: metindeki sayılar panel açılınca 0'dan sayar, satırlar `\n` ile, rakamlar sabit genişlikte), `say_sure` (1,5), `zemin`, `arka`), `acik`, `cizgi` | sol panel ekranı kaplar; `panel` olayında sağ panel kayarak açılır (ayraç: koyu + sarı çizgi). Görsel paneller kendi Ken Burns'üyle oynar ve pencereden görünür (kırpılır, ölçeklenmez); metin paneli kendi zemininde, görünen yarıda ortalı |
| `izgara` | `n` (10000), `sutun`, `ust`, `etiket`, `alt`, `renk`, `dolum` (2,5 sn), `say`, zemin | n nokta satır satır dolar (`basla`), noktalar yavaşça ışıldar; `sondur` olayında bir oranı sessizce söner; `say: true` canlı sayı |
| `pano` | (10. tur, animasyon hakemi S6: ip araya giren kartların ALTINDAN geçer; öbür ucu kartın altındaysa ip kartın alt kenarındaki ikinci raptiyeye bağlanır: üst raptiyeden kartın kendi yazısının üstünden iniyordu; `kontrol` üst üste binen kartları bildirir) `kartlar`* (1-12: `id`, `metin`*, `alt`, `x`, `y` (0..1, kadraja göre), `en`, `egim`, `gorsel`, `stil` kagit/merkez/bos/foto, `asili` (true: sahne başında zaten iğnelenmiş, düşmez, ses yok: panoyu iki çekime bölünce ikincisinde)), `ipler` [[a, b]], `baslik`, `zoom` (1.2: tuvalin kaydırma payı), `yakin` (1.0; > 1 kamera kartlara yaklaşır, ör. 1.35: ilk kartlar büyük okunur), `doku` (mantar \| kece: koyu mavi-gri keçe; aynı pano üçüncü kez görünmesin) | kendi mantar dokumuz; kartlar `kart` olayında düşüp iğnelenir (raptiye sesi), ipler kırmızı ve sarkık çizilir, `damga` olayı `kart:` ile kartın üstüne; kamera 1:1'den %6 yaklaşır ve asılı kartların ağırlık merkezine kayar |
| `marka` | `bindirme`, `karart` (0.72), `wojak`, `yuz` (imzada geçilen yüz), `yazi` (vars. filigran), `arka` | ~1,8 sn kanal imzası: yuvarlak wojak rozeti döner ve büyür, sarı şerit geçerken `tarihselwojak` yazısı açılır, rozet gülümser, sonunda yazı küçülüp filigranın yerine uçar (sahnede filigran yok, son karede gerçek filigranla değişir); efekt `marka` |
| `bitis` | `arka` ya da `bindirme`, `karart` (0.62), `bulanik`, `baslik` (vars. ilk satır; `false`: yok), `kutular` (0-2), `abone` (true), `duzen` (yan_yana/sag/sol), `etiketler`, `karakter` {gorsel, boy, bakis} | YouTube bitiş ekranı: bulanık zemin, üstte kapanış cümlesi, iki boş 16:9 kutu + abone dairesi (`BITIS_DUZENLERI`: kenarlardan uzak, alt %10 oynatıcıya boş). YouTube 5-20 sn ister (§8); 9-12 sn yeterli (talidomit-turkiye: 9,3 sn); son sahne olmalı (`kontrol` uyarır). **7. tur: kanalda yeterli uzun video olana dek yerine `kapanis`** (hesap sahibi: kutular gereksiz) |
| `kapanis` | (10. tur, animasyon hakemi S8: anlatıcının başı A kartının köşesine biniyordu: kart sırası karakterin alfa kutusundan 28 px uzak durur; en az kaydırma, gerekirse ara ve kart eni daralır) `arka` ya da `bindirme`, `karart` (0.6), `bulanik`, `ust` (ör. "SON SORU"), `soru` (vars. ilk satır), `secenekler` (0-3: `metin`*, `alt` (11. tur: 34 px; telefonda 24 px okunmuyordu), `gorsel` (karakter PNG'si ya da resim), `harf`, `bakis`; **11. tur, animasyon hakemi S9: kartlar yanıyor ama içindeki çizim hiçbir şey yapmıyordu**: `vurgu_gorsel` (ilk vurguda yüz değişir, kısa sıkışmayla; aynı tuval), `damga` (metin ya da {metin, renk}: küçük lastik damga iner; karakterli kartta başın yanındaki boşluğa, yüze/ağza değil; belgede görselin alt yarısına), `hareket: yuvarlan` (zar gibi bir tur döner ve sekerek oturur) \| `sicra`), `karakter` {gorsel, yuz, boy 0.34, taraf sol/sag, bakis} (vars. klasik wojak sakin -> mutlu), `yorum` (vars. "A mı, B mi, yoksa C mi?\nCevabını yorumlara yaz"; `\n` satır sonu), `dugmeler` (abone, zil, begen, yorum: sıra ve seçim), `bos_alan` (false \| true = sag_ust \| sol_ust), `renk` (vurgu, vars. sarı) | **Kapanış çağrısı (~8-12 sn, vars. 10; video kutusu yok).** Üstte hikâyenin açık sorusu kelime kelime belirir, sarı çizgi açılır; ortada seçenek kartları (A/B/C rozetli, sarı ad plakalı, karakter pencerede) zıplayarak gelir; solda wojak aşağıdan yükselir, düğmeler gelir; elinden çıkan imleç ABONE OL'a tıklar (düğme basılır, griye döner: "ABONE OLUNDU" + tik; wojak gülümser, sıçrar), zile (zil sönümlü sallanır, çınlama yayları), BEĞEN'e (başparmak sarıya döner, kıvılcım); yorum balonu "Yorum ekle…" yer tutucusundan soruyu daktiloyla yazar; sonra kartlar tek tek vurgulanır (sarı kalın çerçeve, büyüme, içindeki karakter sıçrar) sonra **üçü birden** nabız gibi atar ve eşit, hafif vurguda kalır: sahne nötr biter (hiçbir seçenek "doğru cevap" gibi işaretli kalmaz; 8. tur: son karede C tek başına sarıydı). Karakter yorum yazılırken balona eğilir, her vurguda başıyla onay verir. Anlar (10 sn; kısa sahnede orantılı): soru 0,2, kartlar 0,8+0,18·i, karakter 1,7, düğmeler 2,0+0,1·j, imleç 2,4, tık abone 3,1 / zil 3,9 / beğen 4,7, yorum yazımı son tık+0,5 (24 harf/sn), vurgular yazım bitince +0,4, 0,6 sn arayla. `tikla`/`secenek` olayları anları satıra çapalar. Kartlar birbirine bağlanmaz (ip/ok yok): tartışmalı kişiler ayrı seçenek (OGRENILENLER §2.7). `bos_alan`: o köşede ~280x280 px YouTube Studio "Abone ol" öğesine boş kalır (soru öbür yana, kartlar 50 px aşağı). Efektler: soru whoosh, kart pop, karakter whoosh, tıkta `klik`, abonede pop, zilde `zil`, beğende pop, yazımda seyrek tuş, vurguda blip. Son sahne olmalı (`kontrol`), 5-20 sn |

**Zemin** (sayac, metin, zaman_cizelgesi, izgara ve metin panelleri; 9. tur: `karart` 0..1 zemini koyulaştırır, koyu sahneden kâğıda kesmede parlaklık sıçramasın): `zemin: koyu` (vars.; degrade + leke dokusu +
vinyet; 4. turda aydınlatıldı: kare ortalaması ~55-65/255, eskiden ~20; harita denizi ve karası da: dünya haritası ~75), `kagit` (eski kâğıt; yazılar mürekkep rengi), `foto` (`arka`'nın kendisi bulanık-karartılmış); `arka` koyu
zemine `arka_opak` (0.5) oranında karışır. Hepsinde boşta hareket: yavaş itme + yanal süzülme, toz zerreleri ve gezinen
ışık (koyu), gren. Ölçüm (demo, 2 sn arayla bulanık karelerin ortalama farkı): bütün sahnelerde > 1.

**Bindirme sahneleri** (`bolum_karti` + `bindirme`, `marka` + `bindirme`, `bitis` + `bindirme`): render önceki sahnenin
son karesini (filigransız) bir kez çizip sahneye verir; parça önbelleği anahtarı önceki sahnelere bağlıdır. Karartma
donmuş karenin parlaklığına göre artar (kâğıt gibi açık karede yazı okunsun: `cizim.donuk_karart`).

`*` zorunlu. Filigran her karede sağ altta (geçişten sonra eklenir, kaymaz).

### Hareket dili (`hareket`, 7. tur)

Hesap sahibi (13.10): "animasyon kalitesi güzel ama hatalar var; sınırlarını zorla". Kare kare ölçümde (§13) bulunan
motor kaynaklı kusurlar düzeltildi ve üst düzey animasyon kanallarının dili eklendi. Varsayılanı açık olanlar her
sahnede daha iyi; paralaks ve doku sahneye göre karar ister.

| Anahtar | Vars. | Ne yapar | Neden |
|---|---|---|---|
| `bulaniklik` | true | Hızlı harekette hareket bulanıklığı (180° obtüratör: son karedeki yer değiştirmenin yarısı kadar iz, `C.hareket_izi`; **8. tur: iz keskin ve tam opak katmanın ALTINDA, en çok 40 px, %60 opak**; animasyon hakemi: bütün sprite bulanınca yüz yarı saydam "hayalet"e dönüyordu, 0:15'te anlatıcı kafatası gibiydi): karakter/konuk giriş-çıkışı (> 10 px/kare), kayan isim etiketi, düşen fotoğraf baskısı; itme (`kaydir`) geçişinde bütün karede yatay bulanıklık (kamera savrulması). Hızlı sayan sayaç tekerlek gibi döner: her basamak bir tekerlek (kilometre sayacı: üst basamak alttakiler 9'dan 0'a geçerken döner), hızlı tekerlek dikeyde en çok 0,38 hücre bulanık | talidomit-turkiye: 97 giriş/çıkışta 559 kare > 60 px/kare (en çok 283 px/kare) keskin "zıplıyordu" (stroboskop); sayaç 0 -> 20.000'de alt basamaklar her karede değişip titreşiyordu (2:20, 60+ ardışık 1 karelik "pop") |
| `ikincil` | true | Yandan giren karakter kayıp dururken üstü öne gider, geri yaylanıp oturur (girişin ivmesine sönümlü yay tepkisi: `yay_egrisi`, 1,8 Hz, sönüm 0,36, en çok 2,6°, tabandan döndürme); alttan girende esner, üstten inende basılır (%5,5); çıkışta hızlanırken üstü geride kalır (2,2°). Fotoğraf baskısı ve pano kartı inerken gölgeleri uzak, yumuşak ve soluk; değince sıkılaşır | Takip hareketi (follow-through): eğilmeyen gövde kayan bir çıkartma gibi görünüyordu |
| `canli` | true | Karakter başına (ad + görsel adından kararlı) farklı nefes (0,25-0,35 Hz) ve salınım ritmi/genliği + tabandan çok hafif baş eğimi (±0,3-0,55°, ~0,09 Hz). Karakter `canli: false`: nefes, salınım, eğim yok (kapı, şişe, dosya gibi dekor) | Bütün karakterler aynı frekansta nefes alıyordu (yalnız faz farkı) |
| `paralaks` | 0 | Wojak sahnesinde arka plan kamerayı `1 - paralaks` oranında izler; karakterler tam, derinlikteki karakter arada. Konuşana itmede karakter arka plandan çok büyür: derinlik | Kapalı: arka planda masaya "konmuş" nesne (karakter olarak çizilen kutu, şişe) paralaksla kayar. Öneri 0,3-0,45; o sahnede `kamera: {paralaks: 0}` |
| `doku` | false | Wojak sahnesinde yalnız arka plana film greni (0,035) + süzülen toz (18 zerre, alt pikselde); karakterler net | Gerçek fotoğrafı arşiv havasına sokar, karakteri öne çıkarır; düz çizim arka planda (kendi odalarımız) gerekmez |

Her zaman açık (hata düzeltmesi; ayar yok):

- **Alt piksel yazı** (`C.bindir_alt`): süzülen metin kelimeleri (belirmesi biten satır tek katman), daktilo satırı,
  çeviri, sayaç etiketleri, zaman çizelgesi yazıları, bölünmüş ekran metinleri, harita ülke etiketleri ve çağrı
  çizgisi (kenarı yumuşatılmış katman), konuşma balonu, isim etiketi. Eskiden tam piksele yuvarlanıyordu: 124 pt yazı
  0,3-0,4 sn'de bir 1 px zıplıyor, harita etiketi altındaki (alt pikselde kayan) haritaya göre titriyordu.
- **Ortak taban çizgisi:** kelime kelime dizilen yazıda (metin, kapanış sorusu) kelimeler satır yüksekliğinde
  (`C.yazi(..., dikey_kirp=False)`): "ne" gibi çıkıntısız kelime yukarı kaymaz; daktiloda harf eklendikçe satır
  zıplamaz.
- **Köşe göstergesi sabit genişlik:** rakamlar tabular, kutu bütün durumların en genişinde: sayarken/takılırken kutu
  5-9 px genişleyip daralmıyor (talidomit-turkiye: 0:01, 0:36, 4:27, 5:10, 9:12'de sol kenar titriyordu).
- **Sayaç tekerlekleri sabit sayıda (8. tur):** basamak sayısı baştan bölümün en büyük değerine göre ayrılır; öndeki boş
  tekerlek alttakiler 9'dan 0'a dönerken boştan 1'e döner (eskiden 9.999 -> "0.000" -> 10.000+ ve yana kayma). Görünen
  genişlik 0,27 sn'lik ortalamayla değişir (basamak eklenince sayı yumuşakça sola açılır); önek (≈) ilk rakama yapışık.
  `sure: 0` ile bir anda gelen değer bulanık dönmez: 1,15'ten 1'e "yumruk" + rengiyle kısa parlama; eski etiket önce
  söner, yenisi sonra gelir (üst üste binmez).
- **9. tur:** sayaçta öndeki boş tekerlek sayı o basamağa varana dek tamamen boş (hızlıyken bulanık şeritteki 9/1
  komşuları "01.500.000" gibi bir "0" gösteriyordu); `sure: 0` değerinden 0,2 sn ÖNCE eski etiket söner ("en az 17
  hasta" 3 kare okunuyordu); daktilo yazısı ve imleci giriş geçişi (çapraz/karart) bitince başlar (imleç sönen önceki
  karenin üstündeydi); kapanışta imleç karakterin göğsünün önünde küçükten büyüyerek doğar ve son 1,8 sn bütün kare
  hafifçe yaklaşır (durağan son yok); kodlayıcı `setsar=1` (SAR açıkça 1:1).
- **10. tur (hakem 9: sayaç 6,5, yerleşim 6,5):**
  - **Sayaç tekerleği hiç geri okunmaz** (animasyon hakemi S1: "38 -> 30 -> 40", "292,9 M -> 202,0 M", "≈6.318 ->
    ≈0.310"; ölçüm: tekerlek konumları zaten tekdüzeydi, ama hücre 0,26-0,38 hücre boyu kutu bulanıktı ve bulanıklık
    sayının hızından geliyordu: DURAN 6, 8, 9 bile bulanıp "0" okunuyordu). Şimdi: birler kare başına yarım
    hücreden hızlıysa sayaç **sayısal** (her kare `round(v)`'nin rakamları; üst basamaklar aynı karede ilerler, yarım
    dönmüş üst basamağın yanında duran 9 "39 -> 30" gibi okunmaz); yavaşta **mekanik kilometre sayacı**
    (`_konumlar`: üst tekerlek = floor(v/10^k) + yalnız alttaki tekerlek 9'dan 0'a dönerken in_out_sine kesir). İz
    keskin rakamın ALTINDA, %38 opak, pencerenin üst/alt kenarında söner (`IZ_OPAK`, karakterlerin hareket izi gibi);
    iz uzunluğu tekerleğin bu karedeki gerçek dönüşünden (yavaşta) ya da kendi ortalama hızından (sayısalda, yalnız
    yarım hücre/kareyi aşan tekerlekte). Basamak sayısı hedeften; öndeki tekerlek sayı varana dek boş, boştan 1'e
    döner, öndeki sıfır hiç çizilmez; boş şeridin bulanığı üstten 9'u sarmalamaz. Önek ("≈") görünen ilk rakamın
    solunda kalır (9.999 -> 10.000'de ortalamalı genişlik geride kalınca yeni "1"in üstüne biniyordu).
  - **Yerleşim:** isim etiketi karakterlerden kaçar (olay tablosu `isim`); kapanış kartları ve pano ipleri yukarıda.
- **İtme geçişinin bulanıklığı (8. tur):** 20 px/kare altında yok, 60'ta tam, en çok 160 px (itmenin son karelerinde
  varılan yüz "basamaklı" görünüyordu).
- **Kesmede yarıda kalmaz:** vurgu kelimesi, isim etiketi ve süreli damga sahne kesmeyle (ya da donmuş kare
  bindirmesiyle) bitiyorsa çıkış animasyonu kesmede yarıda kalmaz, öğe kesmeye dek tam görünür (talidomit-turkiye:
  8 vurgu kelimesi kesmede %18-95 saydam kesiliyordu). Çapraz geçişte söner (önceki sahne geçiş boyunca çizilir).
- **Bindirme kartı kararması** 0,18 sn out_cubic -> 0,3 sn in_out_sine (ikinci karede bir anda %46 kararıp bulanıyordu,
  kare farkı 37/255).

Maliyet (1080p, tek süreç, talidomit-turkiye sahnelerinin ilk 90 karesi): girişli wojak sahnesi 37 -> 55 ms/kare,
girişsiz 50 -> 55, sayaç 54 -> 66, pano 69 -> 68; bütün videoda render ~%20-30 uzar. Kapatmak için `hareket` anahtarları.

### Otomatik efektler (`assets/sfx`, hepsi sentez: `tools/make_sfx.py`)

kaydir geçişi -> `gecis` (süpürmeli whoosh, tepesi geçişin ortasında, soldan sağa); bölüm kartı -> `gecis` + `boom`
(bindirmesizde öncesinde alçak `riser`); foto -> `shutter` + etikette her 4 harfte bir alçak `tus` (`ses.ETIKET_TUS_ADIMI`; 6. tur: anlatımın altında saniyede ~10 tık yoruyordu); manset -> kutu başına `kalem`; harita ->
ülke başına `blip`, vurguda `pop` + `hit`, rotada hafif `whoosh_kisa` + varışta `blip`; sayaç -> `tik`'ler (azalanda eşit aralıklı) + her bitişte `hit`; zaman
çizelgesi -> nokta başına `pop`; metin -> `whoosh_kisa` (daktiloda harf başına `tus`) + çeviride `pop` + üstünü çizmede
`kalem`; wojak -> giriş/çıkışta `whoosh_kisa` (`yon: pop` girişte `pop`), balonda `pop`; isim etiketi -> `whoosh_kisa`; vurgu kelimesi -> `pop`;
damga -> `damga`; köşe göstergesi -> `tik` (takılınca `static`); bolunmus -> panel açılışında `whoosh_kisa`, büyütmede
`whoosh`, çeviride `pop`; pano -> kart başına `whoosh_kisa` + `raptiye`, ipte hafif `whoosh_kisa`; marka -> `marka`;
bitis -> kutu ve dairede `pop`; kapanis -> §3 tablosu (`klik`, `zil` yeni); izgara bilerek sessiz.

**Ses-görüntü eşlemesi (7. tur, efekt dosyalarının vuruş anı ölçülerek):** `damga.wav`'ın vuruşu 0 ms'de: efekt damganın
kâğıda değdiği an (`Damga.INIS` = 0,14 sn; eskiden +0,1, 40 ms erken); `whoosh_kisa`'nın tepesi 0,22 sn'de: girişte
tepe girişin en hızlı karelerine (giriş + 0,1 sn; eskiden girişten 0,22 sn sonra, karakter %81 içerideyken), çıkışta
in_cubic'in hızlandığı sona (çıkış + 0,35), isim etiketinde ilk kareye; `shutter` baskının hedefe ilk değdiği an
(iniş + 0,36; eskiden oturmada, 0,22 sn geç).

**Efekt kısması:** bütün efektler (otomatik + `sfx`) tek veriyolunda toplanır ve anlatım konuşurken yan zincirle
kısılır: 10 ms RMS satır seviyesinin (`SATIR_HEDEF_DB`) `EFEKT_PAYI_DB` (9 dB) altına sınırlanır (60 ms önce, 180 ms sonra
dahil). Hiçbir efekt bir kelimeyi örtemez; vurgu efekti (motif, damga, boom, hit) tam sesiyle duyulsun diye cümle
**bitişine** çapalanır: `{ad: turkiye, satir: n, an: son, ofset: 0.05, db: -11}` + satıra `sonra: 0.5`
(talidomit-turkiye 1. hakem turu: motif ve harita pop+hit Türkiye kelimesinin üstüne düşüp onu örtüyordu).

Kapanışta (11. tur) seçenek kartının ilk vurgusunda: `damga` varsa `damga` (iniş anında), `hareket: yuvarlan` varsa hafif
`whoosh_kisa` + oturuşta `tik`.

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
   incelme, bir an sessizlik, bitiş ekranında açık). 7. tur: bir an sessizlikten (<= -30 dB) dönen müzik (>= 20 dB
   yükseliş) en az `SESSIZLIK_DONUS` (1,6 sn) rampayla açılır (0,6 sn'de 40 dB yükselip "patlayarak" geliyordu).
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
  `libx264 -preset faster -crf 18 -pix_fmt yuv420p -bf 0 -profile:v high -g 60 -r 30` ile ayrı mp4'e yazılır
  (yükleme kopyası `render --crf 16`, ~9 Mb/sn; talidomit-turkiye teslimi böyle).
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
(bölümün ilk sahnesinin, yani kartın başı, **yukarı** yuvarlanır: damga kartın içine düşer; ilki 0:00; kartsız bölümde **aşağı**: yukarı yuvarlanınca ilk kelime kesiliyordu, 5. tur; 11. tur (teknik hakem S3): kartsız bölümde ilk ses yukarıdaki tam saniyeden en az `KARTSIZ_PAY` (0,1 sn) sonra başlıyorsa yine **yukarı**: aşağıdaki "Kapanış" 9:38 önceki satırın son hecesine düşüyordu; bindirme kartı tam saniyeden en çok 0,1 sn sonra başlıyorsa da **aşağı**: o an bindirmenin dondurduğu karenin kendisi, 6. tur: yukarı yuvarlanan damga kartın son ~0,25 sn'sine düşüyordu). Bitiş ekranı
öğelerinin başlangıcı da yukarı yuvarlanır (daha erken başlarsa kapanış sahnesinin üstüne biner). Denetim: >= 3 bölüm, her biri >= 10 sn, artan sıra.
Kontrol listesinde "Shorts > İlgili video" bağlantısı ve bitiş ekranı maddeleri var. 11. tur (teknik hakem S1): kapanış
maddesi Studio'nun bitiş ekranında en az bir video/oynatma listesi öğesi isteyebileceğini söyler; yalnız "Abone ol"
kaydedilmezse bitiş ekranı boş bırakılır ya da kanal filigranı (Özelleştirme > Marka) kullanılır.

## 8. Denetimler (`kontrol`)

- **Altyazı blok ipucu:** satır `metin`indeki satır sonu (`"…gösteren\nönemli bir çalışma…"`) SRT bloğunu orada
  böler; ekrandan ve TTS metninden çıkarılır (önbellek anahtarı değişmez). Sayılar altyazıda rakamla: `metin`
  rakamlı, `tts` kelimeli (anahtar TTS metninden).
- **Altyazı kırılma kuralları** (`altyazi.kirma_cezalari`, 5. tur dil hakemi): soru ekinden (mi/mı/miydi…) önce, belirleyiciden (bir/o/bu/en/her/yarım/aynı…) sonra, sayı (rakamlı ekli sayılar ve 'milyonu' dahil) ile birimi arasında, ilgi hâli ekinden ('Grünenthal'in | laboratuvarında') sonra, ek-fiilden ('yetersiz | olduğunu') önce, sıfat + ad ('günlük | doz') ve özel ad + iyelikli ad ('Behçet | hastalığındaki') arasında kırmak cezalıdır (yasak değil).
- **Altyazı kelime farkı:** SRT'nin kelimeleri satır metinleriyle birebir aynı olmalı (`altyazi.kelime_farki`). Bölme
  hiçbir zaman kelime atmaz: sığmayan birleşim yapılmaz; uzun yan cümle kelime sınırlarından EŞİT parçalara bölünür
  (tek kelimelik yetim parça yok).
- **Çapraz geçişte aynı karakter (8. tur):** `gecis: gecis` ile birleşen iki sahnede aynı karakter ailesi (`chars/` altında,
  yüz eki atılmış ad: `anlatici_v2_sakin` -> `anlatici_v2`) varsa uyarır: geçiş boyunca karakter iki kez görünür
  (talidomit-turkiye 7. tur: 20 yerde). Kesme ya da itme kullan.
- **Üst katman çakışması (10. tur, `yerlesim.denetle`):** bütün üst katmanlar (isim, kelime, damga, daktilo
  etiketi, köşe göstergesi) sahne boyunca 0,1 sn arayla, gerçek animasyonlu yerleriyle örneklenir (çıkış kayması dahil:
  9. turda Kennedy etiketi çıkarken "BU ÖDÜLÜ ALAN 2. KADIN" üstüne çizildi). Bir yüze 8 px'ten derin giren ve başka
  bir üst katmanla 8 px'ten yakın (değme, köşeden binme dahil; döndürülmüş damga çokgen olarak) olanlar zaman
  aralığıyla bildirilir (0,15 sn'den kısası geçiş sayılır). Yüz = karakter görselinin baştan boyuna bölgesi
  (`yuz_kutusu`); `canli: false` ya da `chars/`/kit dışı görsel nesne sayılır (belgeye basılan damga bilerek). Ayrıca:
  isim etiketi hiçbir yerde 40 px uzak duramıyorsa ya da küçültüldüyse; pano kartları üst üste biniyorsa. Kontrol
  sahne çizicilerini 960x540'ta kurar (kare çizmez; talidomit-turkiye ~10 sn).
- **Sayaç (10. tur, `sayac_denetimi`):** bir sayım sonraki değerden ya da sahne sonundan önce `tut` kadar
  yerleşsin diye kısaltıldıysa ya da sonraki değer ertelendiyse bildirir.
- **Hareket:** her sahnenin "vuruşları" (giriş, balon, yüz, etiket, ülke, nokta, kutu, sayaç başı/sonu, olaylar) toplanır;
  `max_bos` (6 sn) boyunca ekrana yeni bir şey gelmiyorsa zaman aralığıyla uyarır.
- **Bölüm:** YouTube kuralları. **Altyazı:** 42/2/1 kuralları. **Paket:** başlık <= 100, etiket <= 500, açıklama <= 5000.
- **Bitiş ekranı:** `bitis` sahnesi son sahne, 5-20 sn (paket kontrol listesine başlangıç anı yazılır).
- **Aynı kayıt:** aynı ses + aynı TTS metni + aynı hız/duygu = aynı önbellek anahtarı = birebir aynı dosya (ör. Aylin'in
  "Tamamen zehirsiz." kaydı açılışta ve sonda); `kontrol` bu grupları "aynı kayıt (n kez, tek seslendirme)" diye listeler,
  görünen metni ve sesi aynı ama ayarı farklı satırlar için uyarır (`tts.tekrarlar`).
- **Kesmede zıplama (11. tur, `ziplama_denetimi`; animasyon hakemi M2: köşedeki anlatıcı kesmede 0,50 -> 0,42 boy
  değiştiriyor, soldan sağa sıçrıyordu):** kesmenin (geçişsiz) iki yanında görünen aynı karakter ailesinin ekrandaki
  yüz kutusu (orta x, üst y) ve alfa kutusu yüksekliği karşılaştırılır (sahne kameraları ve `it` dahil: yakın çekimle
  eşleşen kesme uyarı vermez). Yan değiştirme hep uyarılır; aynı yanda > 0,012 kayma, > 0,03 dikey ya da > %4 boy farkı
  uyarılır (ekranın beşte birinden çok kayma ya da %50'den çok boy değişimi bilinçli sayılır). Çözüm: x/boy/kamera
  eşitle ya da `gecis: karart` / `kaydir`.
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

### 10. tur (13.10.2026): demo 99,0 sn, 16 sahne (anlatımsız sayaç sahnesi eklendi)

Ön izleme (960x540, 3 işçi) 2971 kare 26,7 sn (~111 kare/sn); ses -14,0 LUFS, -2,3 dBTP, loudnorm doğrusal; video/ses
0,000'da, fark -0,3 ms, 2971/2971 kare. `kontrol` talidomit-turkiye'de ~15 sn (90 sahnenin çizicisi 960x540'ta
kurulur, kare çizilmez). Test: `python -m pytest tests -q` 66 test (11. tur: 67; kesmede zıplama denetimi ~9 sn ekler).

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

## 12. Animasyon denetimi (7. tur): `tools/uzun_animasyon_denetimi.py`

Hesap sahibinin "animasyonda hatalar var" notundan sonra her teslimden önce kare kare ölçüm (OGRENILENLER: ayrı bir
"animasyon/karakter hakemi"). Araç dört adım: `kareler` (videoyu 30 fps çözer, 480x270'te 20x10 karo farkları
|f[k]-f[k-1]|, |f[k]-f[k-2]|, |f[k]-f[k-3]|), `oge` (motoru çalıştırıp her `C.bindir` çağrısını kaydeder: öğe, yer, boy,
opaklık, görünen kutu, çizim sırası; render ile aynı kod ve video.yaml gerekir: `parcalar()` anahtarları dosyalarla
aynıysa öyledir), `rapor` (1-2 karelik değişim, geçişin 2. karesinde sıçrama, POP, kesmede yarı saydam, kısa kalış,
kenar kırpılması, yazının yüze/yazıya binmesi + z-düzeni, > 60 px/kare hız), `seri` (şüpheli anın tam çözünürlük
şeridi). Her bulguya bakılır: yüz değişimi, hece sekmesi, sayaç, hızlı giriş de "değişim" sayılır.

talidomit-turkiye (13.10, 18.403 kare) bulguları ve motor düzeltmeleri: §3 "Hareket dili" tablosu. YAML kaynaklı
bulgular üreticiye kesin değişikliklerle verildi (sahne, an, anahtar).

## 13. Bilinen sınırlar

- Karakterler alt pikselde yerleşir (`cizim.alt_piksel`: ölçek + kesirli konum tek örneklemede, önceden çarpılmış
  alfa; 713 px boyda ~7 ms; eğimli karede `afin_pm` ~12 ms). 7. turdan beri süzülen yazı, balon, etiket de alt
  pikselde; damga ve köşe göstergesi durağan olduğu için tam pikselde.
- Hareket bulanıklığı yalnız öteleme içindir (ölçek/dönme hızı bulanıklaştırılmaz: damga inişi, pop girişi). Kare
  başına ~0,1 sn ek iş, yalnız hızlı karelerde (talidomit-turkiye'de ~560 kare).
- Sayaç hızlıyken (birler > 0,5 birim/kare) sayısal sayaç gibi her kare tam sayıyı gösterir (gerçek dönüş
  stroboskopla geri dönüyormuş gibi görünürdü); dönüş hissini keskin rakamın altındaki iz verir; yavaşlayınca gerçek
  kilometre sayacı dönüşü (geçiş anı tekdüze).
- Harita bugünkü sınırları gösterir (1957'nin Batı/Doğu Almanya'sı yok); gerekirse anlatımda belirt.
- Balon yerleşimi karakterin başının üstünü varsayar; çok uzun (boy > 0,8) karakterde balon kadraj üstüne yaslanır.
- Altyazı parçalarının satır içindeki zamanlaması tahmindir (kelime zaman damgası yok). 10. tur (teknik hakem S1:
  9. turun "en yakın sessizliğe otur" kuralı sınırı başka kelime arasındaki duraklamaya çekiyordu, 5 yerde 1-2 sn):
  `altyazi.sinirlari_hizala` kelimeleri harf + noktalama ağırlığıyla (rakamlar okunuşuyla: `soylenis`, "1954'te" ~25
  harf) tartar, noktalamalı kelime aralarını ve bölme noktalarını iç sessizliklerle (en az 0,08 sn) sıra koruyarak
  eşler (dinamik programlama; noktalamada ±2 sn, noktalamasız bölmede ±0,5 sn); bölme noktası eşlenmiş bir
  sessizlikteyse oraya oturur, değilse eşlenmiş sessizlikler arasında doğrusal hesaplanır. Sonuç sıra/en az süre
  kuralını bozarsa 9. turun yöntemi. talidomit-turkiye: Whisper kelime zamanlarına göre 5 hatalı sınırın 5'i düzeldi,
  en yüksek okuma hızı 29 -> 20 krk/sn.
- Whisper QA yalnız isimlere bakar; vurgu/tonlama hatalarını yakalamaz.
- Konuşma sekmesi dudak senkronu değildir: hece başlarına küçük sekme. Kamera itmesi arka planın kenar payıyla sınırlıdır
  (konuşana kayma en çok ~%3-4 kadraj).
- Derinlikteki karakter yükseltilmez (kit görselleri göğüsten kesik); uzaklık küçüklük, sis ve çizim sırasıyla verilir.
- Pano kart yerleri elle (`x`, `y`); damga kartın genişliğine sığdırılmaz (`boy` ile ayarla). Bölünmüş ekranda görsel
  panel pencereden görünür (yarı genişlikte kırpılır), metin paneli görünen yarıda ortalanır.
- Nokta ızgarası 10.000 noktada 960x540 ön izlemede doku gibi görünür (nokta ~4 px); asıl render'da 9 px aralık.
