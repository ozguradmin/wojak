# OGRENILENLER.md oturum notları, Ekim 2026 (kısa reel "Ek dersler" bölümleri; 29.10.2026'da `docs/OGRENILENLER.md`'den değiştirilmeden taşındı)

### Ek dersler (23.10.2026, Kız Kulesi ve Talidomit'in YouTube sürümleri)

- **Kanıt sonradan değişirse, örneğin telifli bir görsel çıkarsa:** `episode.yaml`'da değiştir (`images`, `credits`,
  `telif_notu`), sonra sırayla `check` → `render` → `teslim` çalıştır. `teslim/` altındaki paketi elle düzenleme:
  atıf satırı ve metinler `credits`'ten üretilir, elle düzenlenen paket bir sonraki `teslim`'de ya eskir ya da silinir.
  Yeni son kareye kareyi çıkarıp bak.
- **Açıklamalardaki yıldızlı kelimeler kasıtlı** (örneğin "*leceğini", "*lümünden"). `wojak/censor.py` hassas
  kelimeleri platform metinlerinde bilinçli olarak maskeler. Hata değil; elle düzeltme, "düzeltmek" için paketi
  değiştirme.

### Ek dersler (23.10.2026, `kanuni-gizlenen-olum`, iki hakemden 8/8, ~50 dk)

Kanıtlanmış yol bu bölümde baştan sona ~50 dk sürdü (tahmin 55-75 dk). Yeni kanıtlanan adımlar:

- **Sesi ölç, güvenme (bu ortamda ZORUNLU):** ffmpeg 6.1.1'de `loudnorm` TP aralığı -9..0. `wojak/audio.py` TP=-17
  verince filtre hata veriyor, kod sessizce `anull`'a düşüyor ve video -15,5 LUFS çıkıyor (hedef -29,5). Her render'dan
  sonra ölç: `ffmpeg -i teslim/<id>/<id>.mp4 -af ebur128=peak=true -f null - 2>&1 | grep -E "I:|Peak:" | tail -2`.
  Kod değişmeden çözüm: `music: {file: kanal, volume: 0.197}` (imza_v2_golge -15,4 LUFS → -29,6 LUFS, tepe -17,0).
  Başka müzik dosyasında katsayı = 10^((-29,5 - dosyanın LUFS'u)/20).
- **Tarihî olayda kanıt = dönemin kendi resimli kroniği:** Commons'ta Osmanlı minyatürleri kamu malı (PD-Art /
  PD-US) ve olayı birebir gösterir. Örnek: "Category:Funeral of Suleiman I", "Nehzetu'l-Ahbar der Sefer-i Sigetvar",
  "History of Sultan Süleyman (CBL T 413)". Kupür üretmeden, telifsiz ve çeşitli bir son kare olur. Kırp, 1080
  genişliğe ölçekle, piksellere dokunma. Arama İngilizce + olayın geçtiği yerin dili (Macarca "Szigetvári vár").
- **Commons dosya sayfasını ham metinle doğrula:** `index.php?title=File:<ad>&action=raw` lisans şablonunu
  (`{{PD-self}}`, `{{PD-Art|...}}`) ve kaynağı tek istekte verir. API'nin "Public domain" kısa adı yetmez.
  Dikkat: aynı yükleyicinin ardışık dosyaları ("vár 2" / "vár 3") karışabilir. Önizlemeyi dosya adıyla eşleyerek
  bak (bu bölümde ilk kırpım yanlış dosyadan, modern bir anıtlı kareden yapılmıştı).
- **Uzun başlıklı karakterde yüz küçük kalıyor (börk, kavuk):** PNG'yi alttan kes (bilek/göğüs; büst zaten
  kadrajın altından kesik). Aynı `height`'ta yüz büyür. İki karakterin `height`'ını eşitle ki yazı bloğu sabit
  kalsın (0,55 iki tarafta da). Telefon testi: 390 px'te alt yarıda eşik 40, yüz değişimi ≥ %0,40 (bu bölüm %0,33 →
  %0,48).
- **Kesimde yarı saydam kalan kontur:** wojakland PNG'lerinde profil çizgisi alfa 100-160 kalabiliyor, koyu zeminde
  kayboluyor. Koyu RGB + alfa > 30 olan pikselleri opak yap (`chars/uret.py:kontur_sabitle`). Yüz silerken silme
  kutusunu konturdan 4-5 px içeride başlat, yoksa profil çizgisi ten rengine döner.
- **"Feels good" sevinç pozu → dehşet:** gözleri kapalı, elleri yanakta janissary çiziminde yalnız gözleri (iri,
  küçük göz bebeği), kaşları (iç uçlar yukarı) ve ağzı ("O") değiştirmek yetiyor. Eller yerinde kalınca poz kendiliğinden
  dehşete dönüyor. Yöntem: `episodes/kanuni-gizlenen-olum/chars/uret.py`.
- **Sansürün bozduğu kelimeyi metinde kullanma:** `censor.py` "ölüm"ü "*lüm", "silahdar"ı "S!lahdar" yapıyor.
  Tarihî metinde "vefat", "son nefesini verdi" ve unvansız ad doğal ve temiz. Teslimden sonra kontrol:
  `grep -n "\*\|!" teslim/<id>/metinler/*.txt`.
- **Hakem kendi kendine yürütülürken önce üretici ön kontrolü:** ses (ebur128), kesmeler (kare farkı), telefon yüz
  değişimi ve satır sonu yetim kelime. Bu dördü bu bölümde ilk render'da üç MUST çıkardı; hakem turundan önce
  yakalandı.

**Çalışmayan (deneme):**
- `music: kanal` tek başına: bu ortamda -15,5 LUFS (yukarıdaki ffmpeg/loudnorm hatası).
- Hikâye metninde "Silahdar": sansür "S!lahdar" yapıyor.
- Commons `iiurlwidth`/thumburl: hâlâ 429. Özgün md5 yolu 3-4 denemede (15 sn arayla) geçti.

**Süre ve maliyet (güncel):**

| Adım | Karun (21.10) | Kanuni (23.10) |
|---|---|---|
| Hazırlık + okuma | ~6 dk | ~8 dk |
| Konu + olgu | ~11 dk | ~7 dk |
| Görsel avı | ~17 dk | ~6 dk |
| Karakter + yüz | ~10 dk | ~5 dk |
| yaml → teslim | ~5 dk | ~4 dk |
| Ön kontrol + hakem turları | tur başına 2-3 dk, 2 tur + kart/kupür turları | ~10 dk (ön kontrol + 2 tur) |
| Teslim + commit + belge | ~8 dk | ~10 dk |
| **Toplam** | ~2 sa (3 teslim turu) | **~50 dk** |

Ücretli API: 0 (TTS ve görsel üretimi yok).

**Kod değişikliği önerileri (uygulanmadı):**
- `wojak/audio.py`: loudnorm TP'yi -9 ile sınırla (ya da ölçüp `volume` ile doğrusal kazanç uygula) ve filtre hata
  verirse sessizce `anull`'a düşme, hata ver. `check`/`teslim` çıktı videonun LUFS'unu ölçüp ±1 LU dışında uyarsın.
- `wojak/censor.py`: "silahdar" gibi unvanları ve "vefat" eş anlamlısını istisna listesine al; metinde yıldız kalınca
  `teslim` uyarsın.
- `tools/`: Commons ham dosya sayfasından lisans şablonunu okuyan küçük doğrulayıcı (`action=raw`).

### Ek dersler (23.10.2026 akşam, `ayasofya-viking-yazisi`, iki hakemden 8/8, ~31 dk ölçüldü)

Kanıtlanmış yol yine baştan sona çalıştı. Yeni kanıtlanan adımlar:

- **Ortam:** taze konteynerde `/home/user` olmayabilir; önce `mkdir -p /home/user`, sonra `ln -sfn`. Testler 81/81
  geçti (hashtag testi bu sefer düşmedi).
- **Arka plan yumuşaklığını ölç, varsayılan blur'a güvenme:** büyük bir fotoğrafı 1080'e küçültüp varsayılan
  `blur: 2,5` verince kenar Laplace varyansı (720 ölçeği) ~7 çıktı; orijinal medyan ~22. Ölçüm: görseli
  `GaussianBlur(b)` ile birkaç değerde dene, üst şerit + iki yan şeridin `scipy.ndimage.laplace` varyansına bak.
  Bu bölümde `blur: 1.6` → ~20. Kural: küçültülen keskin kaynakta 1,2-1,6; zaten yumuşak kaynakta 2,5-3,2.
- **Kanıtı telefon boyunda kırp:** ilk kırpımda runler 390 px'te seçilmiyordu, levha yazısı küçüktü (görsel hakem
  7,5). Nesneyi ve yazıyı kadrajın büyük kısmına alan sıkı kırpım (16:9'a yakın, yine tam genişlik) 8'e çıkardı.
  Hakemden önce: `ffmpeg -ss <t> -frames:v 1 -vf scale=390:-1` ile kanıt karelerine bak.
- **Yeni son kare türü: nesnenin kendisi + yanındaki resmî levha.** Olay basında değil taşın/nesnenin üstünde
  kayıtlıysa (yazıt, grafiti, anıt), nesnenin serbest lisanslı fotoğrafı ve müze/yapı levhası kupürden daha dürüst ve
  çeşitli bir son kare. Commons "Category:Runic inscriptions in Hagia Sophia" gibi kategoriler hem yakın plan hem
  levhalı kare veriyor.
- **İroni kalıbı "kimse fark etmez" → levha:** C2fa iskeletinin geçiştirme repliği ("Bir şey olmaz, ...") son kanıtın
  kendisiyle ödenebilir: A "kimse fark etmez" der, son kare bin yıldır korunan, levhalı yazıyı gösterir. Ters köşe
  yüzü uyaran karakterde (B) olabilir: "Delirdin mi, burası Ayasofya" + şok yüzü yerin adını da verir.
- **Yüzü miğferli/kapalı karakterde değişim alanı küçük:** muhafızın yalnız gözleri ve ağzı değişince telefonda
  %0,37 çıktı. İki karakterin `height`'ını 0,48 → 0,52 yapmak (yazı bloğu yine sabit) ve ter damlalarını büyütmek
  %0,44'e çıkardı. `height` 1080'lik karenin oranıdır (0,52 → 562 px).
- **Kendi teslimini yeniden üretmek:** `teslim` var olan klasörün üstüne yazmaz; düzeltme turlarında bilinçli
  `--zorla`.

**Çalışmayan (deneme):**
- Varsayılan `blur: 2,5` küçültülmüş keskin fotoğrafta: orijinallerden belirgin yumuşak (Laplace ~7).
- Kanıtı geniş kırpıp "bağlam" vermek (nef + korkuluk + runler): telefonda nesne kayboluyor.

**Süre ve maliyet (güncel):**

| Adım | Karun (21.10) | Kanuni (23.10) | Ayasofya (23.10 akşam) |
|---|---|---|---|
| Hazırlık + okuma | ~6 dk | ~8 dk | ~5 dk |
| Konu + olgu | ~11 dk | ~7 dk | ~2 dk |
| Görsel avı | ~17 dk | ~6 dk | ~10 dk |
| Karakter + yüz | ~10 dk | ~5 dk | ~5 dk |
| yaml → teslim | ~5 dk | ~4 dk | ~2 dk |
| Ön kontrol + hakem turları | 2 tur + kart/kupür turları | ~10 dk | ~5 dk (ön kontrol + 2 tur) |
| Teslim + commit + belge | ~8 dk | ~10 dk | ~3 dk |
| **Toplam** | ~2 sa | ~50 dk | **~31 dk** |

Ücretli API: 0.

**Kod değişikliği önerileri (uygulanmadı):**
- `wojak/compose.py`/`check`: arka planın kenar Laplace varyansını ölçüp blur önersin (hedef ~20, 720 ölçeği).
- `check`: kanıt görselini 390 px'e küçültüp "küçük ayrıntı" uyarısı (ör. kenar yoğunluğu düşükse) versin.
- `tools/wojak_lib.py get`: çıktı `head` ile kesilince BrokenPipeError veriyor (zararsız, ama gürültü).

### Ek dersler (24.10.2026 sabah, `gobeklitepe-mezar-tasi`, iki hakemden 8/8,5, ~25 dk ölçüldü)

Kanıtlanmış yol yine baştan sona çalıştı. Yeni kanıtlanan adımlar:

- **Ortam sırası:** sembolik bağ testlerden ÖNCE kurulmalı. `mkdir -p /home/user` olmadan `ln` sessizce başarısız
  oluyor ve `test_short_youtube_aciklamasi_hikayeyi_tasir` düşüyor (eski sabit yol). Bağdan sonra 81/81.
- **Commons küçük resim (24.10 düzeltme notu):** bu oturumda `iiurlwidth=500` + `thumburl` 21 dosyada **429 vermedi**
  (istekler ~2 sn arayla). Temas sayfası için önce bunu dene; yalnız seçilen 3-4 dosyayı md5 özgün yolundan (≥12 sn arayla)
  indir. Arama: `generator=search&gsrnamespace=6&prop=imageinfo&iiprop=url|size|extmetadata` lisansı da verir.
- **Gerçek yerin ayırt edici nesnesi iyi arka plan:** Göbeklitepe'nin doruğundaki dilek ağacı (Commons "Gobekli Tepe
  Wishing tree in 2014") hem gerçek yer hem 1963'te de oradaydı; kazı çatısı/yürüme yolu gibi modern yapılar kadrajda yok.
  Ağacı karenin ortasına al: iki karakter yanlarda, ağaç aralarında kalır.
- **Hazır çizimden sigara/çubuk gibi konturu kesen öğeyi silmek:** yüz dışındaki kısmı saydam yap, kesilen yanağı
  beyazla doldur, kopan konturu `Cizim.cizgi` ile aynı kalınlıkta yeniden çiz, uçtan kalan tek tük pikselleri temizle
  (`episodes/gobeklitepe-mezar-tasi/chars/uret.py:arkeolog_temel`). Sırıtan yüz (smug) kanalda kötü karakter okunur:
  kaş/göz/ağız silinip sakin yüz çizildi, sonra yatay aynalandı (B sağda, sola bakar).
- **Ter damlası göze yakınsa telefonda gözyaşı gibi okunuyor.** Yüz kapalıysa (kask, şapka) damlaları başın dış yanına,
  kontur dışına koy (bakılan karakter tarafına). Düşük çözünürlüklü büst (439 px) göğüs cebinden kesilince (y 370) aynı
  `height`ta yüz büyüdü, telefonda yüz değişimi %0,61.
- **Satır sonu yetim kelime ilk karelerde üç replikte çıktı** (55 px'te satır ~26-27 karakterde kırılıyor). Çözüm:
  virgülde elle kırım ("Mezar taşı bunlar,\neski bir mezarlık", "Daha kazmadınız ki,\nnasıl anladınız?") ya da tek
  satıra sığan kısaltma ("Hocam bu dev taşlar ne?"). `frames` şeridine bakmadan render etme.
- **Kupür tek görünüm değil, parametrelerle değişti** (`episodes/gobeklitepe-mezar-tasi/kupur.py`, ~1 sn): 2018 renkli
  hafta sonu eki gibi daha beyaz kâğıt, Source Serif 4 900 manşet (Karun'da grotesk), **renkli CMYK raster** (C 15°,
  M 75°, Y 0°, K 45°, hücre 3,6 px; soluk kaynağı yüzdelikle ger, doygunluğu x1,35), dikey katlanma izi, alt kenar yırtık,
  +1,2° eğik, mavi-gri kumaş zemin. Gerçek başlık hiyerarşiye bölünebilir, metin değişmeden: üst başlık "Tarihi
  değiştiren dünya mirası:" + ana manşet "Göbeklitepe" + spot aynı haberin spotundan birebir bir cümle. Kanıt yüksekliği
  ≤ 816 px (ilk sürüm 820 idi, `check` uyarmıyor).
- **Kupürdeki alıntılanan sayı bilimsel kaynaktan farklıysa** (Hürriyet "Stonehenge'den 7 bin", Smithsonian ~6.000):
  alıntıyı değiştirme; hikâye metninde sayı vermeden yaz ("binlerce yıl daha eski") ve RAPOR'a kusur olarak yaz.
- **Dramatik ironi + yüz varyantı:** son replik bir fark etme sorusu olmak zorunda değil; yanılan karakterin kendinden
  emin sözü ("Kazmaya değmez, burada önemli bir şey yok") aynı kutuda ter + kaçan gözlerle söylenince ters köşe olur, cevabı
  son kare verir. Canlandırma repliğini belgeli olgunun sınırında tut ve `ek_maddeler`'e yaz.

**Çalışmayan (deneme):**
- `ln -sfn ... /home/user/wojak` `/home/user` yokken (sessizce başarısız, bir test düşer).
- Ter damlasını göz altına koymak (telefonda gözyaşı).

**Süre ve maliyet (güncel):**

| Adım | Karun (21.10) | Kanuni (23.10) | Ayasofya (23.10 akşam) | Göbeklitepe (24.10 sabah) |
|---|---|---|---|---|
| Hazırlık + okuma | ~6 dk | ~8 dk | ~5 dk | ~5 dk |
| Konu + olgu | ~11 dk | ~7 dk | ~2 dk | ~4 dk |
| Görsel avı | ~17 dk | ~6 dk | ~10 dk | ~2 dk |
| Karakter + yüz | ~10 dk | ~5 dk | ~5 dk | ~4 dk |
| yaml → teslim (kupür dahil) | ~5 dk | ~4 dk | ~2 dk | ~3 dk |
| Ön kontrol + hakem turları | 2 tur + kart/kupür turları | ~10 dk | ~5 dk | ~3 dk (ön kontrol + 2 tur) |
| Teslim + commit + belge | ~8 dk | ~10 dk | ~3 dk | ~4 dk |
| **Toplam** | ~2 sa | ~50 dk | ~31 dk | **~25 dk** |

Ücretli API: 0.

**Kod değişikliği önerileri (uygulanmadı):**
- `check`: satır sonunda tek kelime kalan replikte uyarı versin (greedy kırımın son satırı 1 kelimeyse).
- `check`: kanıt görseli 816 px'ten yüksekse uyarsın (STIL §8).
- `tools/`: `kupur.py`'yi genelleştiren üretici (kâğıt yaşı, manşet fontu, gri/renkli raster, yırtık kenar, eğim, zemin
  parametreli); iki bölümde iki ayrı kopya var.
- `tests/`: sabit `/home/user/wojak` yolu yerine depo kökünü kullanan test (taze konteynerde bağsız düşmesin).

### Ek dersler (24.10.2026 akşam, `kasikci-elmasi`, iki hakemden 8/8, ~25 dk)

Kanıtlanmış yol yine baştan sona çalıştı. Yeni kanıtlanan adımlar:

- **Depolar ayrık HEAD'de açılabilir:** iki depo da `HEAD detached` başladı. Önce `git fetch origin`, sonra
  varsayılan dala geç (`git checkout claude/kind-albattani-vcp4vk` / `main`) ve `git pull`. Ayrık HEAD'de commit atma.
- **Yapraklı arka planda blur daha yüksek:** servi + ağaç tacı ağırlıklı kırpımda `blur: 1.6` kenar Laplace ~143
  verdi (orijinal medyan 22); 2,5 → 29, **2,8 → ~20**, 3,2 → 12. Ayasofya'daki 1,2-1,6 kuralı taş/iç mekân için;
  yaprak ve gökyüzü kenarı çoksa 2,5-3,0. Ölçüm: `GaussianBlur(b)` sonrası 720 ölçeğinde üst şerit + iki yan şerit.
- **Tarihî sahnede modern öğe:** gerçek yerin bugünkü fotoğrafında trafik tabelası, şerit ya da araba varsa kırpımı
  kaydır. Dört kırpımı tek temas sayfasında karşılaştır, karakterlerin örtmediği yarıya bak: tek konuşmacılı sahnede
  karşı taraf hep açıkta kalır. Eğrikapı'da (800,0)-(2350,1550) kırpımı servi + kule + sur + Osmanlı hazire
  parmaklığını aldı; tabelalar dışarıda kaldı.
- **Hazır çizimdeki leke ve gri gradyan temizliği:** wojakland "Peasant Wojak"ın yüzündeki kahverengi çamur lekeleri
  telefonda yara gibi okunuyordu, alt yüzdeki gri yumuşak gölge de düz MS-Paint değildi. Çözüm iki adımlı:
  lekeyi kutu içinde `sil(..., tol=-1)` ile beyaza boya; yüz kutusunda nötr açık gri pikselleri (en küçük kanal
  ≥ 168, kanal farkı < 14) beyaza çevir. Çizgiler ve kenar yumuşatması korunuyor (`kasikci-elmasi/chars/uret.py:bulan_temel`).
- **17. yüzyıl Osmanlı halkı için hazır karakter:** `wojak_lib.py search ottoman` sonuçlarının neredeyse hepsi fesli
  ve takım elbiseli (19.-20. yüzyıl). Fes 1829'dan sonra; daha eski sahnede kullanma. wojakland'de `peasant_wojak.png`
  (siyah takke + entari, klasik beyaz yüz) ve `turban_2_chad.png` (beyaz sarık, kır sakal, sola bakan profil; yüzü
  sakin, düzenleme gerekmedi) işe yaradı. Sorgu: `wojak_site.py sheet "turban|peasant|17th|medieval_man" --site wl`.
- **Yeni son kare türü: müze nesnesinin kendisi.** Olay bir nesneyle bitiyorsa (elmas, hançer, mühür) nesnenin gerçek
  yakın plan fotoğrafı kupürden daha dürüst ve çeşitli bir son kare. Commons'ta Topkapı Hazinesi nesnelerinin
  ziyaretçi fotoğrafları CC BY 4.0 (ör. "Spoonmaker's Diamond5, Topkapi Palace, Istanbul 2023.jpg", 9 aday).
  Önüne mekânın kendisi (Hazine binası, kamu malı) konunca sıra "nerede → ne" oluyor.
- **Dikey nesneyi 1080x816'ya sığdırma:** nesneyi kesmeden tam yüksekliği al, gereken genişliği iki yana fotoğrafın
  nesnesiz koyu kenarını (son 8 sütunun ortalaması) yatay uzatarak ekle. Uzatılan şeridi Gauss 24 ile bulanıklaştır,
  fotoğrafa 40 px içeriden yumuşak maskeyle bağla (`kasikci-elmasi/gorsel.py:kanit2`). Koyu vitrin zemininde dikiş
  görünmüyor; ayna kullanılmadı.
- **Kelime tohumu ve adın karşılığı:** S2'de ekilen sıradan kelime ("üç tahta kaşık") son karede nesnenin adında
  karşılığını bulunca ters köşe repliği olgu iddiası taşımadan ödenir. Türk izleyici "Kaşıkçı"yı 3. saniyede yakalar.
- **Commons küçük resim (24.10 akşam):** `iiurlwidth=2000` + `thumburl` 5 dosyanın 4'ünde 200 döndü, biri 429 verdi;
  429 alan dosya md5 özgün yolundan ilk denemede indi.

**Çalışmayan (deneme):**
- `blur: 1.6` yapraklı/servili arka planda (Laplace ~143).
- `wojak_lib.py search ottoman` ile 17. yüzyıl halkı (fes + takım elbise, dönem dışı).
- Gerçek yerin tam kare kırpımı (Eğrikapı kapısı): trafik tabelaları ve sarı-siyah şerit karenin ortasında kalıyordu.

**Süre ve maliyet (güncel):**

| Adım | Kanuni (23.10) | Ayasofya (23.10 akşam) | Göbeklitepe (24.10 sabah) | Kaşıkçı (24.10 akşam) |
|---|---|---|---|---|
| Hazırlık + okuma | ~8 dk | ~5 dk | ~5 dk | ~3 dk |
| Konu + olgu | ~7 dk | ~2 dk | ~4 dk | ~2 dk |
| Görsel avı | ~6 dk | ~10 dk | ~2 dk | ~3 dk |
| Karakter + yüz | ~5 dk | ~5 dk | ~4 dk | ~3 dk |
| yaml → teslim | ~4 dk | ~2 dk | ~3 dk | ~3 dk |
| Ön kontrol + hakem turları | ~10 dk | ~5 dk | ~3 dk | ~5 dk (ön kontrol + blur + 1 tur) |
| Teslim + commit + belge | ~10 dk | ~3 dk | ~4 dk | ~5 dk |
| **Toplam** | ~50 dk | ~31 dk | ~25 dk | **~25 dk** |

Ücretli API: 0.

**Kod değişikliği önerileri (uygulanmadı):**
- `tools/`: dikey nesne kanıtını 1080x816'ya kenar uzatma + bulanıklaştırmayla tamamlayan küçük yardımcı (iki bölümde
  elle yazıldı: Karun kare tamamlama, Kaşıkçı 816 tamamlama).
- `tools/wojak_lib.py` / `wojak_site.py`: dönem süzgeci (ör. `--once 1829` fesli sonuçları gizlesin).

### Ek dersler (25.10.2026 sabah, `hezarfen-galata-ucusu`, iki hakemden 8/8, ~29 dk)

Kanıtlanmış yol yine baştan sona çalıştı. Yeni kanıtlanan adımlar:

- **Yeni son kare türü: posta pulu.** Olay seyahatname/kronik kaynaklıysa ve basında çıkmadıysa, devletin sonradan
  bastığı hatıra pulu hem resmî hem kamu malı bir kanıt: Commons'ta Türk pulları `{{PD-TR}}` (ör. "Hezarfen Ahmed
  Çelebi.jpg", 1950 ICAO pulu). Pul dikeyse tam genişlikte, dişleri iki yanda görünecek biçimde üst kısmından 1080x816
  kırp (başlık + tarih + sahne kadrajda kalsın). 319 px'lik tarama 3,4 kat büyüdü: telefonda net, 1:1'de yumuşak
  (LANCZOS + `UnsharpMask(2, 60, 2)`). Commons'ta "1950 stamps of Turkey" gibi yıl kategorileri var.
- **Dev başlıklı (kavuk + sorguç) karakterde yüz kadrajın en altına düşüyor:** `height` 0,55'i aşınca `check` ve
  `render` `[stil]` uyarısı veriyor (0,58 ve 0,62 denendi). Doğrusu 0,55'te kalmak ve PNG'yi **sakalın altından** kesmek
  (Sultan Wojak 1518x1400 → y 1235). Yüz yine alt yarıda kalır ama okunur; iki karakter 0,55'te yazı bloğu sabit.
  Not: `check` çıktısını `grep -v "^ "` ile süzme; `[stil]` satırları girintili, süzgeç onları da siler (bu oturumda
  uyarı bu yüzden önce gözden kaçtı, render'da görüldü).
- **Kaynak çizimin ağzı anlamı bozuyorsa değiştir:** Sultan Wojak dişlerini sıkıyordu (kanalda öfkeli/kötü okunur).
  Ağız bölgesini sakal rengine boya (`sil(..., tol=-1)`), düz ve hafif aşağı kıvrık tek çizgi çiz. Sakal rengini
  değiştirirken (kır → koyu, genç padişah) **bağlı bölge** kullan (`scipy.ndimage.label`, tohum sakalın içinde); düz renk
  eşiği benzer tondaki kürk yakayı da boyadı.
- **Chad profilinde ters köşe yüzü telefonda zor okunur:** ilk varyant %0,25'ti. Göz beyazını büyüt (yarıçap ~60/46 px,
  1024 px çizimde), açık ağzı pembe dudak + koyu iç olarak sakalın içine çiz (koyu ağız siyah sakalda kaybolur), alına
  5 kalın mavi soğuk ter çizgisi (11 px) ve başın önüne, kontur dışına 3 damla (44/36/26) koy: %0,40. Tuvali sağa 70 px
  aç ki damlalar kesilmesin.
- **Ters köşe repliğinin bilgisi bir önceki replikte ekilmeli:** ilk turda "Cezayir'e mi sürüyorsunuz?" birden
  geliyordu (sürgünü ekranda kimse söylemiyordu). Bilgiyi B'ye ver ("Böyle adamdan korkulur, Cezayir'e gideceksin"),
  A'nın fark etme sorusunu son karenin göstereceği şeye bağla ("Nasıl yani, uçtum diye sürgün mü?" → pulda uçuş).
- **Arka planda kenarı kesen yapı parçası:** gerçek yerin fotoğrafında karenin kenarında yarım kalan baca/sütun bej bir
  şerit gibi göze batıyor; kırpımı 80 px kaydırmak yetti. Dikey öğeyi (kule) karakterlerin başının üstüne denk getir:
  karakterler hep kare tabanında, kule hep görünür kalır.

**Çalışmayan (deneme):**
- `height` 0,58 / 0,62 (yüzü büyütmek için): `check`/`render` `[stil]` uyarısı.
- Sakal rengini düz renk eşiğiyle değiştirmek (kürk yaka da boyandı).
- wojakland "Muslim Wojak" (klasik yüzlü sarıklı): büstsüz kafa, alt kenardan kesilince "kafa havada" kalıyor.

**Süre ve maliyet (güncel):**

| Adım | Ayasofya (23.10 akşam) | Göbeklitepe (24.10 sabah) | Kaşıkçı (24.10 akşam) | Hezarfen (25.10 sabah) |
|---|---|---|---|---|
| Hazırlık + okuma | ~5 dk | ~5 dk | ~3 dk | ~3 dk |
| Konu + olgu | ~2 dk | ~4 dk | ~2 dk | ~5 dk |
| Görsel avı | ~10 dk | ~2 dk | ~3 dk | ~4 dk |
| Karakter + yüz | ~5 dk | ~4 dk | ~3 dk | ~7 dk |
| yaml → teslim | ~2 dk | ~3 dk | ~3 dk | ~2 dk |
| Ön kontrol + hakem turları | ~5 dk | ~3 dk | ~5 dk | ~5 dk (ön kontrol + 2 tur) |
| Teslim + commit + belge | ~3 dk | ~4 dk | ~5 dk | ~3 dk |
| **Toplam** | ~31 dk | ~25 dk | ~25 dk | **~29 dk** |

Ücretli API: 0. En uzun adım karakterdi: 17. yüzyıl Osmanlı bilgini için hazır karakter araması (üç kaynak, iki
sayfa) ve dev kavuklu padişahın yüz yerleşimi.

**Kod değişikliği önerileri (uygulanmadı):**
- `check`/`compose`: başlığı yüksek karakterde (kavuk, sarık) yazı bloğu %32 alt sınırına yapışıyor; yüzün PNG içindeki
  konumuna göre (yüz kutusu alanı) boy önerisi verilebilir.
- `tools/`: Commons'ta yıl kategorisinden pul arayan küçük yardımcı ("Category:<yıl> stamps of Turkey", PD-TR süzgeci).

### Ek dersler (25.10.2026 akşam, `midas-mezari-altin`, iki hakemden 8/8, ~26 dk)

Kanıtlanmış yol yine baştan sona çalıştı. Yeni kanıtlanan adımlar:

- **Başlık ters köşeyi söylemesin (ilk turdaki tek MUST):** "Ne?!" cümlesi ("Midas'ın mezarını açtılar, içinden tek
  bir altın çıkmadı") konu seçimi için doğru ölçü ama başlıkta spoiler. Başlık kanca + somut ayrıntı olsun, cevap
  videoda kalsın: "Kral Midas'ın mezarına tünel kazan Zonguldaklı madenciler". `title`'ı yazarken son replikle
  karşılaştır: başlık son repliğin cevabını veriyorsa değiştir.
- **Kazıyı yöneten arkeoloğun birincil raporu altın kaynak:** Penn Museum Expedition dergisinin eski sayıları
  (`penn.museum/sites/expedition/<baslik>/`) açık erişimli; kazı ekibinin kendi anlatımı ayrıntı veriyor (Zonguldaklı
  madenciler "kendi ustabaşılarını" getirdi, üç vardiya, 25 gün). Tek kaynaklı ayrıntı metinde "X'in anlattığına
  göre" olur; karakter seçimini de belgeye bağlar (B = ustabaşı).
- **Türk bağlantısını yan karakterde bul:** yabancı ekibin kazısında konuşanları yabancı arkeolog yerine işi yapan Türk
  işçiler yapmak (Zonguldaklı madenci + ustabaşı) hem yerelliği hem kancayı ("Usta, bu tepenin altında kim yatıyor?")
  güçlendirdi; arkeoloğun adı yalnız metinde.
- **1950'ler Türk işçisi için hazır karakter:** wojakland `worker_2_wojak.png` (gri kasket, bıyık + keçi sakal,
  tulum; 1153 px, klasik beyaz yüz) ve `worker_wojak.png` (kahverengi kasket, kirli sakal; 464 px, aynalanarak B).
  Sorgu: `wojak_site.py sheet "worker|miner|construction" --site wl`. Kütüphanede (`wojak_lib.py`) maden işçisi yok.
- **Kasketli/şapkalı karakterde mavi ter çizgisi:** alın kapalıysa çizgiyi yanağa koyma (telefonda gözyaşı gibi). İri
  göz + kalkık kaş + büyük "O" ağız + başın önünde 3 damla yetti: telefonda alt yarıda %0,87.
- **Gerçek yerin eski (film) fotoğrafı:** Commons'ta "<yer> (1993)" gibi taranmış eski fotoğraflar bugünkü giriş yapısı,
  yürüme yolu, tabela olmadan yeri gösteriyor; tarihî sahneye daha uygun ve zaten yumuşak (`blur: 2.2` ile yan şerit
  Laplace ~22). Renk: `ImageEnhance.Color(0.75)` + `Brightness(0.93)` → doygunluk 0,28, parlaklık 124.
- **Commons özgün md5 yolu (25.10 akşam):** 5 dosyanın 4'ü 12 sn arayla 1-5 denemede indi; biri 5 denemede de 429
  verdi, aynı dosya `iiurlwidth=2400` thumburl'ünden ilk denemede indi. Kural: md5 yolu 3 kez 429 verirse thumburl'e geç.
  Temas sayfası için 26 küçük resim (`iiurlwidth=500`, 2 sn arayla) hiç 429 vermedi.

**Çalışmayan (deneme):**
- `ln -sfn` taze konteynerde `/home/user` yokken (yine oldu; önce `mkdir -p /home/user`).
- Kasketli karakterin yanağına mavi ter çizgisi (gözyaşı gibi okunuyor).
- Ters köşeyi söyleyen başlık (takipçi hakemi MUST).

**Süre ve maliyet (güncel):**

| Adım | Göbeklitepe (24.10 sabah) | Kaşıkçı (24.10 akşam) | Hezarfen (25.10 sabah) | Midas (25.10 akşam) |
|---|---|---|---|---|
| Hazırlık + okuma | ~5 dk | ~3 dk | ~3 dk | ~5 dk |
| Konu + olgu | ~4 dk | ~2 dk | ~5 dk | ~4 dk |
| Görsel avı | ~2 dk | ~3 dk | ~4 dk | ~5 dk |
| Karakter + yüz | ~4 dk | ~3 dk | ~7 dk | ~4 dk |
| yaml → teslim | ~3 dk | ~3 dk | ~2 dk | ~2 dk |
| Ön kontrol + hakem turları | ~3 dk | ~5 dk | ~5 dk | ~3 dk (ön kontrol + 2 tur) |
| Teslim + commit + belge | ~4 dk | ~5 dk | ~3 dk | ~3 dk |
| **Toplam** | ~25 dk | ~25 dk | ~29 dk | **~26 dk** |

Ücretli API: 0.

**Kod değişikliği önerileri (uygulanmadı):**
- `check`: başlık ile son diyalog repliğinin anahtar kelimelerini karşılaştırıp "başlık ters köşeyi söylüyor olabilir"
  uyarısı (ör. son replikteki olumsuzlanan ad başlıkta "çıkmadı/yok" ile geçiyorsa).
- `tools/`: Commons indiricisi md5 yolu 3 kez 429 verince otomatik `iiurlwidth` thumburl'üne düşsün.
- `tests/`: sabit `/home/user/wojak` yolu yerine depo kökü (taze konteynerde hâlâ düşüyor; önceki öneri).

### Ek dersler (26.10.2026 sabah, `tahran-1985-ertugrul`, iki hakemden 8/8, ~26 dk)

Kanıtlanmış yol yine baştan sona çalıştı. Yeni kanıtlanan adımlar:

- **Yeni son kare türü: arşiv fotoğrafı.** Olay basından çok anma töreniyle hatırlanıyorsa dönemin kamu malı fotoğrafı
  güçlü ve dürüst bir son kare. Commons "Cérémonie funéraire Ertugrul.jpg" ({{PD-Japan-oldphoto}}) torii kapısında
  Osmanlı bayrağını gösteriyor: soruyu ("95 yıl önce ne oldu?") tek karede cevaplıyor. Soluk sepya baskıda yalnız
  `ImageOps.autocontrast(cutoff=(1, 0.5))`; ton değişmez.
- **Dikkat: okuma aracı büyük görseli küçültüp gösteriyor.** 6266 px'lik dosyanın kırpım koordinatlarını gösterilen
  görüntüden okuyunca ilk kırpım yanlış yere düştü. Kırpmadan önce `Image.open(...).size` yazdır, koordinatı ölçekle çarp.
- **Gerçek yerin arşiv fotoğrafı arka plan olarak:** "Mehrabad-1971.jpg" ({{PD-Art|PD-Iran}}, 1971 kitap taraması) apronu,
  uçağı ve terminali gösteriyor. Basılı taramanın deseni `blur: 2.2` ile yumuşadı (yalnız arka planda üst ~19, yanlar ~10-13).
  Renk: `Color(0.62)` + `Brightness(0.9)` → arka plan doygunluğu ~0,21.
- **Kenar Laplace ölçümünü yazının olmadığı yerde yap.** Videodan alınan karede sol şerit (720 ölçeğinde x<150) repliğin
  ucunu içerdiği için 260 çıktı. Arka planı `img/` dosyasından `GaussianBlur(b)` ile ölç ya da yazının altındaki şeridi kullan.
- **Ters köşe yüzü "duygulanma" (korku değil):** animemsi kadın çiziminde kaşları silip iç uçları kalkık kalın (20-21 px)
  kaş çiz, irise iki beyaz parıltı koy, alt kapak boyunca ince (10 px) mavi gözyaşı birikintisi ve yanaktan inen kalın
  (20-22 px) gözyaşı ekle. İlk sürüm (14 px gözyaşı, 13 px kaş) telefonda %0,29 kaldı; güçlendirilince %0,46. Yanaktaki
  gözyaşını yüz konturundan en az 15 px içeride tut. Yöntem: `episodes/tahran-1985-ertugrul/chars/uret.py`.
- **Kelime tohumu deyimle:** "Bizim size ne iyiliğimiz dokundu ki?" → "Dokundu, 95 yıl önce". Deyimin fiili son replikte
  tek kelimelik cevap olunca ters köşe 4 kelimeye iner, son kanıt (Osmanlı bayrağı Japonya'da) sessizce öder.
- **Satır kırımı özel adı bölmesin:** "Türk Hava / Yolları" okunmuyordu. Kurumun halk arasındaki kısa adı ("THY") tek satıra
  sığdırdı.
- **Bakış kaydında eski sha1:** varyantı her yeniden ürettiğinde `yon` yeni girdi ekliyor. Teslimden önce bu bölümün
  dosyalarına ait, güncel sha1'le eşleşmeyen girdileri sil (başkasının girdisine dokunma). Bu bölümde 2 eski girdi silindi.
- **Hassas konu ayrımı:** 1985 olayında pilotlar ve kabin ekibi gerçek ve kısmen hayatta. Adlarını ekrana ve metne koymamak
  ve hostesi "gerçek ekipten kimseyi temsil etmeyen kurgu karakter" diye `ek_maddeler`'e yazmak BEKLET gerektirmedi. Metinde
  yalnız kamu görevlileri (büyükelçiler, başbakan) var.

**Çalışmayan (deneme):**
- Okuma aracında görülen küçültülmüş görüntüden büyük dosyanın kırpım koordinatını almak (yanlış kırpım).
- Yazı içeren video karesinde kenar Laplace ölçmek (yazı konturu ölçümü şişiriyor).
- İnce gözyaşı (14 px) ve ince kaş (13 px) ile "duygulanma" yüzü: telefonda %0,29.

**Süre ve maliyet (güncel):**

| Adım | Kaşıkçı (24.10 akşam) | Hezarfen (25.10 sabah) | Midas (25.10 akşam) | Tahran-Ertuğrul (26.10 sabah) |
|---|---|---|---|---|
| Hazırlık + okuma | ~3 dk | ~3 dk | ~5 dk | ~3 dk |
| Konu + olgu | ~2 dk | ~5 dk | ~4 dk | ~3 dk |
| Görsel avı | ~3 dk | ~4 dk | ~5 dk | ~3 dk |
| Karakter + yüz | ~3 dk | ~7 dk | ~4 dk | ~4 dk |
| yaml → teslim | ~3 dk | ~2 dk | ~2 dk | ~3 dk |
| Ön kontrol + hakem turları | ~5 dk | ~5 dk | ~3 dk | ~4 dk (ön kontrol + 2 tur) |
| Teslim + commit + belge | ~5 dk | ~3 dk | ~3 dk | ~6 dk |
| **Toplam** | ~25 dk | ~29 dk | ~26 dk | **~26 dk** |

Ücretli API: 0.

**Kod değişikliği önerileri (uygulanmadı):**
- `wojak/facing.py`: `yon` aynı dosya yolu için yeni sha1 kaydederken o yolun eski girdilerini silsin (ya da `yon --temizle`).
- `check`: telefon boyu (390 px) yüz değişimini ters köşe sahnesi için kendisi ölçüp %0,40 altında uyarsın (her bölümde elle
  ölçülüyor).
- `check`: satır kırımı bir özel adı (art arda iki büyük harfli kelime) iki satıra bölüyorsa uyarsın.

### Ek dersler (26.10.2026 akşam, `yerebatan-bodrum-balik`, iki hakemden 8/8, ~40 dk)

Kanıtlanmış yol yine baştan sona çalıştı. Yeni kanıtlanan adımlar:

- **Depolar yine ayrık HEAD'de açıldı** (Kaşıkçı dersi geçerli): `git pull` "commit or stash" diye durdu. Çözüm: `git stash -u`
  → `git checkout <varsayılan dal>` (`git remote show origin | grep "HEAD branch"`) → `git pull --rebase origin <dal>` → `git stash pop`.
  Bunu iş başında, dosya yazmadan önce yap.
- **Yeni son kare türü: kitap sayfası (Internet Archive, kamu malı).** Olayın kaydı bir seyahatname/kronikse, olayı birebir
  anlatan sayfanın taraması en dürüst son kare. Yol:
  `archive.org/advancedsearch.php?q=title:(<sözcükler>)+AND+mediatype:texts&fl[]=identifier&fl[]=year&output=json` → tam metin
  `archive.org/download/<id>/<id>_djvu.txt` içinde pasajı grep'le (18. yy. baskısında uzun s "f" diye okunur: "Fifh", "Ciftern")
  → `<id>_page_numbers.json` sayfa numarasından `leafNum` verir → `archive.org/download/<id>/page/n<leaf>_w2000.jpg` (1711x2922,
  ilk denemede indi). 1080x816 kırp, satır aralığında kes, yalnız `autocontrast`. Okunabilir: 55 px'lik replik gibi değil ama
  telefonda seçiliyor. Türk izleyici için hikâye metnine "Videonun son karesi … sayfasıdır" cümlesi ekle (takipçi hakemi SHOULD).
  Pasajda aşağılayıcı ifade varsa (burada "Contempt … in the Inhabitants") kırpımı o satırların dışından al.
- **Turuncu/kırmızı silindir takke telefonda fes okunuyor.** 1829 öncesi sahnede wojakland `medieval_2_wojak`ın turuncu
  takkesi fes gibi duruyordu. Bağlı bölge (`scipy.ndimage.label`, tohum takkenin içinde) koyu kahve keçeye boyandı, tonlama
  korundu (`episodes/yerebatan-bodrum-balik/chars/uret.py:takke_boya`). Hakemden önce kendin sor: "Bu başlık dönem dışı bir şeye
  benziyor mu?"
- **Küçük kaynak PNG (353-523 px):** önce 2-3x LANCZOS + `UnsharpMask(2, 60, 2)` ile büyüt (alfa ayrı korunur), yüz çizimini
  büyütülmüş tuvalde yap. Yeni çizgiler kaynakla aynı kalınlıkta ve temiz çıkıyor.
- **Sakalın içindeki ağzı silmek:** kutuyu `sil(..., tol=-1)` ile beyaza boyamak sakalı da beyazlatır. Yalnız düşük doygunluklu
  koyu pikselleri (max-min < 30, toplam < 640) beyaza çevir (`siyah_sil`); kahve sakal kalır, eski ağız çizgisi ve gri kenar
  yumuşatması gider.
- **Gerçek yerin bugünkü fotoğrafında modern yürüme yolu:** sarnıç fotoğrafında sağdaki çelik korkuluk A'nın sahnelerinde
  açıkta kalıyordu (B'nin arkasında saklanıyor sanılır ama tek konuşmacılı sahnede karşı taraf açıkta; Kaşıkçı dersi). Kırpımı
  korkuluğun soluna aldım; kaçış noktası %63'e kaydı, sorun olmadı.
- **Sıcak ışıklı iç mekân doygunluğu:** turuncu aydınlatmalı sarnıçta `Color(0.85)` 0,33-0,35 verdi; `Color(0.6)` → 0,25-0,27
  (orijinaller 0,20-0,27). Blur 2,4 → kenar Laplace ~20-25.
- **Bodrum/kuyu sahnesi için serbest fotoğraf yok:** "Ottoman house well courtyard", "kuyu bileziği", "wellhead courtyard
  Istanbul" boş döndü. Diyalogu olayın belgeli ikinci anına (kayıkla sarnıçta) taşımak hem gerçek yeri verdi hem kancayı
  güçlendirdi ("bodrumda balık" + arkada Yerebatan).
- **Commons (26.10 akşam):** `generator=search` / `categorymembers` + `iiurlwidth=400/1600` ~2-3 sn arayla 120'den fazla küçük
  resimde hiç 429 vermedi; 1600 istenince 1920 px döndü, arka plan ve kanıt için yetti (özgün dosya indirmeye gerek kalmadı).
- **Hakemler ayrı bağlamda çalıştırılamadı** (bu oturumda alt ajan aracı yoktu): her tur JUDGE_* istemleriyle sıfırdan, yalnız
  teslim dosyalarına bakılarak yürütüldü. Üretici ön kontrolü (ses, kesme, telefon yüz değişimi, yetim kelime, modern öğe,
  dönem dışı kostüm, doygunluk) hakem turundan önce dört sorun yakaladı.
- **Bakış kaydı:** karakter yeniden üretilince eski sha1 girdisi kaldı; `facing.py` biçimiyle (`indent=1, sort_keys=True`) silindi.
  `json.dump(indent=2)` bütün dosyayı yeniden biçimlendirip 1300 satırlık fark yaratıyor, kullanma.

**Çalışmayan (deneme):**
- `git pull` ayrık HEAD'de ve izlenmeyen dosyalar varken (önce stash + checkout).
- Sakal içindeki ağzı `sil(tol=-1)` ya da yalnız `toplam < 260` eşiğiyle silmek (koyu kahve sakal pikselleri de gitti).
- Bodrum/kuyu için serbest arka plan araması (Commons'ta uygun sonuç yok).
- Turuncu silindir takkeyi olduğu gibi bırakmak (fes gibi okunuyor).

**Süre ve maliyet (güncel):**

| Adım | Hezarfen (25.10 sabah) | Midas (25.10 akşam) | Tahran-Ertuğrul (26.10 sabah) | Yerebatan (26.10 akşam) |
|---|---|---|---|---|
| Hazırlık + okuma | ~3 dk | ~5 dk | ~3 dk | ~5 dk |
| Konu + olgu | ~5 dk | ~4 dk | ~3 dk | ~5 dk |
| Görsel avı | ~4 dk | ~5 dk | ~3 dk | ~6 dk |
| Karakter + yüz | ~7 dk | ~4 dk | ~4 dk | ~5 dk |
| yaml → teslim | ~2 dk | ~2 dk | ~3 dk | ~4 dk |
| Ön kontrol + hakem turları | ~5 dk | ~3 dk | ~4 dk | ~8 dk (ön kontrol + 2 tur + 4 düzeltme) |
| Teslim + commit + belge | ~3 dk | ~3 dk | ~6 dk | ~7 dk |
| **Toplam** | ~29 dk | ~26 dk | ~26 dk | **~40 dk** |

Ücretli API: 0.

**Kod değişikliği önerileri (uygulanmadı):**
- `tools/`: Internet Archive sayfa indirici (`<id> <sayfa no>` → `page_numbers.json`'dan leaf → `_w2000.jpg`; djvu metninde pasaj
  arama). Bu bölümde elle curl ile yapıldı.
- `tools/wojak_site.py get`: küçük kaynakları (< 700 px) isteğe bağlı 2-3x büyütüp keskinleştiren `--buyut` seçeneği.
- `check`: diyalog arka planının doygunluğunu ölçüp 0,30 üstünde uyarsın (her bölümde elle ölçülüyor).
- `tests/`: `/home/user` yokken düşen test yine düştü (önceki öneri).
- Bakış kaydı (`data/karakter_yon.json`) sistem isteminin yazma listesinde yok, ama `teslim` kayıt istiyor. Kurala bu dosya
  açıkça eklenmeli ya da kayıt bölüm klasörüne taşınmalı.

### Ek dersler (27.10.2026 sabah, `orban-topu-bizans`, iki hakemden 8,5/8,5, ~25 dk)

Kanıtlanmış yol yine baştan sona çalıştı. Yeni kanıtlanan adımlar:

- **Varsayılan dal bulmak:** `git ls-remote --symref origin HEAD` tek satırda verir (wojak: `claude/kind-albattani-vcp4vk`,
  wojak-ozel: `main`). İki depo yine ayrık HEAD'de açıldı; dosya yazmadan `git checkout <dal> && git pull origin <dal>`.
  `/home/user` yine yoktu (önce `mkdir -p`). Testler 99/99.
- **Yeni son kare türü: kamu malı tablo.** Olayın çağdaş görseli yoksa, olayı sahneleyen 19.-20. yüzyıl tablosu
  (ressam 70+ yıl önce ölmüş, Commons `{{PD-old}}`) hem telifsiz hem güçlü bir son kare. Örnek: Zonaro 1903, dev top
  öküzlerle şehre çekiliyor ("Category:Fall of Constantinople in art", "Category:Ottoman cannons"). Türk izleyici
  Fatih tablosunu anında tanıyor. Kırpım: konu (top) ile kişiyi (Fatih) birlikte tut, 1080x~610.
- **Çağdaş minyatür her zaman olayı göstermez:** BnF fr. 2691 (Chartier) kuşatma minyatüründe top yok; Le Tavernier kuşbakışı
  harita. Minyatürü seçmeden önce tam boyutta aç ve sorunun cevabı (burada "dev top") görünüyor mu, bak.
- **Müze nesnesini dürüst adlandır:** Commons'ta müze kategorisi ("Category:Cannons at Istanbul Military Museum") nesnenin
  levha fotoğrafını da veriyor; levhayı oku ("Fatih Sultan Mehmet dönemi 1451-1481"). Olayın kendi nesnesi yoksa
  ("Orban'ın topu günümüze ulaşmadı") metinde ve `ek_maddeler`'de benzer dönem nesnesi olduğunu açıkça yaz.
- **Kanıt fotoğrafında arka plan:** müze bahçesindeki çöp kutusu, direk ve bina telefonda göze batıyor (görsel hakem
  SHOULD). Nesneyi kesmeden üstten kırp; yükseklik 537 px'in altına düşecekse bir yandan da kırp (burada 1080x560).
- **Dramatik ironi + kelime tohumu (C2fa iskeleti):** "İmparatorum, size dev bir top dökebilirim" → "Hazinede o kadar para
  yok" → "O zaman Osmanlı'ya giderim" → kart → aynı kutuda "Bekle, o dev top da ne?". İzleyici sonu sezse de yüz varyantı ve
  tanıdık tablo ters köşeyi ödüyor. Belgeli nedeni (para) replikte kullan, uydurma tavır (kibir) yazma.
- **Taçlı karakterde yüz küçük kalıyor ama okunuyor:** taç boyun yarısını alınca yüz ~200 px. İri yuvarlak göz + küçük göz
  bebeği + "O" ağız + başın önünde üç damla telefonda alt yarıda %1,04 değişim verdi. Damlaları kontura 20 px yakın tut
  (ilk sürümde 35 px uzaktı, kopuk duruyordu).
- **Başlıkta fiil kaynağa uysun:** "top satmaya gelen" (gevşek) yerine "dev top teklif eden" (kaynaklar "offered"). Tartışmalı
  bir pay ("Saruca'nın da payı vardı") metinde kesin hüküm olmasın: "bazı kaynaklar ... bağlar; tartışılır".
- **Commons (27.10 sabah):** `iiurlwidth=400/1800/2400` + `thumburl` ~20 istekte, 2-3 sn arayla hiç 429 vermedi. Özgün dosya
  (1600 px) API'deki `url` alanından ilk denemede indi.

**Çalışmayan (deneme):**
- Kuşatma minyatürünü (BnF fr. 2691) "dev top" sorusunun cevabı sanmak: minyatürde top yok.
- Ter damlalarını başın konturundan ~35 px uzağa koymak (kopuk ve büyük duruyor).

**Süre ve maliyet (güncel):**

| Adım | Midas (25.10 akşam) | Tahran-Ertuğrul (26.10 sabah) | Yerebatan (26.10 akşam) | Orban (27.10 sabah) |
|---|---|---|---|---|
| Hazırlık + okuma | ~5 dk | ~3 dk | ~5 dk | ~2 dk |
| Konu + olgu | ~4 dk | ~3 dk | ~5 dk | ~3 dk |
| Görsel avı | ~5 dk | ~3 dk | ~6 dk | ~6 dk |
| Karakter + yüz | ~4 dk | ~4 dk | ~5 dk | ~4 dk |
| yaml → teslim | ~2 dk | ~3 dk | ~4 dk | ~3 dk |
| Ön kontrol + hakem turları | ~3 dk | ~4 dk | ~8 dk | ~3 dk (ön kontrol + 2 tur + 4 SHOULD) |
| Teslim + commit + belge | ~3 dk | ~6 dk | ~7 dk | ~4 dk |
| **Toplam** | ~26 dk | ~26 dk | ~40 dk | **~25 dk** |

Ücretli API: 0.

**Kod değişikliği önerileri (uygulanmadı):**
- `tools/`: Commons kategori + levha yardımcısı (müze kategorisindeki nesne fotoğraflarını ve "text"/"label" adlı levha
  fotoğraflarını tek temas sayfasında gösteren). Bu bölümde elle yapıldı.
- `wojak/render`: render satırındaki süre yine yanlış (8,5 sn yazdı; ffprobe 13,95 sn). Süre ffprobe'dan okunmalı.
- Önceki öneriler hâlâ açık: `tests/` sabit `/home/user/wojak` yolu; `data/karakter_yon.json` yazma izni.

### Ek dersler (27.10.2026 akşam, `karakoy-tunel-1874`, iki hakemden 8/8, ~50 dk)

Kanıtlanmış yol yine baştan sona çalıştı. Yeni kanıtlanan adımlar:

- **Ortam:** iki depo yine ayrık HEAD'de açıldı; `/home/user` yine yoktu (bağdan önce 1 test düştü, sonra 99/99). wojak
  uzak deposunda `ls-remote` yalnız `claude/kind-albattani-vcp4vk` dalını gösteriyor (varsayılan dal o).
- **Commons 429, kesin yol:** `Tünel-train.png` (905 px) ve `Chemin de fer...jpg` (2000 px) için md5 özgün yolu 10+ denemede
  429 verdi. Sebep: `iiurlwidth` ≥ özgün genişlik olunca API `thumburl` olarak özgün dosyanın yolunu döndürüyor. Özgünden küçük
  genişlik istenince (`1900`, `500`) gerçek `/thumb/` yolu geliyor ve ilk denemede iniyor. Kanıt için 1920 px yetti.
- **Gerçek yerin bugünkü fotoğrafı dönem dışıysa nesnenin kendisi:** Tünel'in içi (CC BY 4.0, CC BY-SA) kablo kanalı, flüoresan,
  kırmızı yangın borusuyla dolu. Diyalog arka planı olarak müzedeki gerçek ahşap vagonun yan cephesi (Commons, CC0, "Tünel
  Carriage and railway winding engine" kategorisi) kullanıldı; levha ve çatı kadraj dışında. Camdaki modern mavi tabela
  yansıması HSV maskesiyle (ton 125-185, doygunluk > 60) doygunluğu x0,25 yapılarak nötrlendi (`gorsel.py:arka`).
- **Yeni son kare türleri:** (1) **mühendis çizimi**: olayın mühendisinin kendi kitabındaki levha (Gavand 1876, "Profil en long":
  Galata Kulesi'nin altından geçen tünel; kamu malı). Soluk çizgi telefonda kayboluyordu: `gamma 1.8` + `autocontrast(cutoff=
  (0.3, 20))` -> çizgi koyu, kâğıt ≥ 243. (2) **SALT Araştırma arşiv fotoğrafı**: Flickr Commons'tan Commons'a aktarılmış, lisansı
  "No restrictions"; 19. yüzyıl İstanbul'u için zengin ("SALT Research <yer>" ya da "<yer>, İstanbul (1296...).jpg").
- **19. yüzyıl Osmanlı (1829 sonrası) halkı için hazır karakter:** kütüphanede `5_Doomer/13970` (fes, siyah frak, pipo, siyah bıyık)
  ve `5_Crying_Wojak/438` (fes, kır saç, kır bıyık). İkisinde de mavi gözyaşı var; kutuda "mavi" (b > r+25, g > r+10) pikseller
  beyaza, koyu mavi kenar siyaha, açık hayalet kenar (toplam > 330) beyaza çevrilince sakin, ağır kapaklı yüz kalıyor
  (`karakoy-tunel-1874/chars/uret.py:gozyasi_sil`). İki fesli karakter saç rengiyle ayrışıyor (siyah / kır).
- **Filigranlı karakter:** wojakland `victorian_man_wojak.png` (silindir şapka) şapka dokusunda "ChrisClipArt" yazıyor; ancak tam
  boyda görünüyor. Küçük temas sayfasında gözden kaçar: her karakteri tam boyda aç.
- **Fesli karakterde yüz küçük:** PNG'yi göğüsten kes (A, 1x y 450) ama yüzü PNG'de aşağıda olan karakterde çene kadrajdan çıkar
  (B'de y 440 çeneyi kesti, tam boy 492'de kaldı). `bakis.jpg`'de iki tarafın çenesine bak.
- **Kapak ile başlık birlikte okunur:** başlık soruysa ("ilk kim bindi?") ters köşe karesi kapakta cevabı veriyor. Kapak S1 kancası
  yapıldı; ters köşe kapağı hesap sahibine seçenek.
- **Ters köşe "efsane düzeltme" ile güçlenir:** hikâye metninde yaygın anlatıyı ("fetvayla yasaklandı, uzun süre yalnız hayvan
  taşındı") kaynağıyla (Vahdettin Engin'in araştırması) düzeltmek, ekrandaki şaka gibi ters köşeye belge ağırlığı veriyor.
- **wojak-ozel commit yazarı:** depoda son commit yayın botunun; `git log -1 --format=%an` ile yazar almak botu yazar yapar.
  Commit'te açıkça `-c user.name=Claude -c user.email=noreply@anthropic.com` kullan.

**Çalışmayan (deneme):**
- Commons'ta `iiurlwidth` ≥ özgün genişlik (özgün yola düşüyor, 429) ve md5 özgün yolu (aynı 429).
- Tünel içi fotoğraflarını 1874 sahnesine arka plan yapmak (modern donanım her kırpımda).
- Internet Archive'da Gavand'ın 1876 kitabını aramak (yok).
- wojakland `victorian_man_wojak.png` (filigran dokulu şapka).

**Süre ve maliyet (güncel):**

| Adım | Tahran-Ertuğrul (26.10 sabah) | Yerebatan (26.10 akşam) | Orban (27.10 sabah) | Karaköy Tünel (27.10 akşam) |
|---|---|---|---|---|
| Hazırlık + okuma | ~3 dk | ~5 dk | ~2 dk | ~6 dk |
| Konu + olgu | ~3 dk | ~5 dk | ~3 dk | ~9 dk |
| Görsel avı | ~3 dk | ~6 dk | ~6 dk | ~12 dk (429) |
| Karakter + yüz | ~4 dk | ~5 dk | ~4 dk | ~6 dk |
| yaml → teslim | ~3 dk | ~4 dk | ~3 dk | ~3 dk |
| Ön kontrol + hakem turları | ~4 dk | ~8 dk | ~3 dk | ~6 dk (ön kontrol + 2 tur) |
| Teslim + commit + belge | ~6 dk | ~7 dk | ~4 dk | ~8 dk |
| **Toplam** | ~26 dk | ~40 dk | ~25 dk | **~50 dk** |

Ücretli API: 0. En uzun adım görsel avıydı: Commons 429 ve hayvanlı deneme seferini doğrudan gösteren serbest görsel arayışı
(yok; manşet de yok).

**Kod değişikliği önerileri (uygulanmadı):**
- `tools/`: Commons indiricisi `iiurlwidth`'i özgün genişliğin altında seçsin (429'un asıl çözümü; yukarıda).
- `check`: başlık soru biçimindeyse ve `cover_scene` ters köşe sahnesiyse uyarsın (kapak cevabı veriyor olabilir).
- `tools/wojak_site.py get`: indirilen karakterin tam boy önizlemesini kaydetsin (filigran dokusu küçük sayfada görünmüyor).
- Önceki öneriler hâlâ açık: `tests/` sabit `/home/user/wojak` yolu; `data/karakter_yon.json` yazma izni; render satırındaki süre.

### Ek dersler (28.10.2026 sabah, `goeben-fes-1914`, iki hakemden 8/8, ~45 dk)

Kanıtlanmış yol yine baştan sona çalıştı. Yeni kanıtlanan adımlar:

- **Ortam:** iki depo yine ayrık HEAD'de, `/home/user` yine yoktu (önce `mkdir -p /home/user`, sonra `ln -sfn`). Testler 99/99.
- **Yeni son kare türü: gerçek (kamu malı) gazete sayfası.** ABD'de 1929 öncesi gazeteler kamu malı. Commons'ta "The New York
  Times 1914-08-13- Vol 63 Iss 20655 ...pdf" gibi günlük sayılar ve "Victoria Daily Times (1914-08-12)" var. Sayfa önizlemesi:
  `iiurlparam=page1-1500px` ile `thumburl`. Yüksek çözünürlük için Internet Archive'daki kimliği kullan
  (`per_new-york-times-magazine_the-new-york-times_<YYYY-MM-DD>_<cilt>_<sayı>`, `victoriadailytimes<YYYYMMDD>`). Komut:
  `archive.org/download/<id>/page/n0_w4000.jpg`, ilk denemede 6889x8561 indi. Tek sütunluk haberi iki komşu sütundan birer şeritle
  1080x780'e kırp (1,1 kat büyütme, manşetin büyük harf yüksekliği ~65 px; telefonda okunuyor). Kendi kupürümüzü üretmeye gerek
  kalmadı, "Son kare canlandırmadır" satırı da gerekmedi. Hikâye metnine İngilizce manşetin Türkçesini yaz (takipçi hakemi SHOULD).
- **Tarihî grup fotoğrafı için kitap taraması:** "Ambassador Morgenthau's Story" (1918) gibi kamu malı kitapların fotoğraf
  sayfaları Commons'ta. Altyazılı tarama (Jay Dobkin, CC BY-SA 2.0, 1709 px) altyazısız PD-1923 sürümünden (1131 px) büyüktü.
  Altyazıdaki bilgi ("en sol ve en sağdakiler dışında hepsi Alman") hem `ek_maddeler`'e hem `sources`'a girer. Taramanın kenarı eğik
  olabilir: kırpımdan sonra iki yan şeridi büyüterek bak (ilk kırpımda sağda 15 px sayfa beyazı kalmıştı).
- **Görsel tohum:** B'nin başındaki fes, S2'de ters köşenin nesnesini önceden gösteriyor. Son replik ("Bekle, neden bize fes
  verdiler?") kostüm değiştirmeden ödenir. "takıyoruz" denseydi A'nın başında fes olmadığı göze batardı; "verdiler" çelişmiyor.
- **Hazır çizimdeki ülke işaretini silmek:** İspanyol denizci kepindeki kırmızı ponpon ve "MARINA" yazısı Alman denizcisinde dönem
  ve ülke hatası olurdu. Ponpon: ponponun alt konturunu (kepin üst çizgisi) bir eğriyle tanımla, eğrinin 3 px üstünü saydam yap,
  eğriyi aynı kalınlıkta yeniden çiz. Yazı: açık gri harfleri `cv2.inpaint` (TELEA, r=9) ile kapat. Alın beyazını maskeden 13x13
  genişletip çıkar, yoksa inpaint şeride beyaz taşıyor (`goeben-fes-1914/chars/uret.py:denizci_temel`).
  Koordinat tuzağı: ızgara görselinin etiketleri gerçek koordinattır, ama ölçek 2x olunca göz kararı okuma kaydı. Kırpmadan önce
  3x ızgarada tekrar bak.
- **Sırıtan hazır karakteri sakinleştirmek:** Twinkjak Osmanlı subayının dişli yarım sırıtışı silinip düz ağız çizildi. Göz bebekleri
  yarığın sağ ucuna alınınca dosya "sag" kaydedildi, sağda aynalanınca içeri bakıyor. Uzun fesli karakterde yüz küçük kalıyordu;
  PNG göğüsten kesilince (1148 → 880 px) aynı `height`'ta yüz ~%30 büyüdü, yazı bloğu yerinde kaldı.
- **Arka plan: aynı türden yer, dönem gemisi güvertesi.** Commons'ta "Category:Battleship Texas State Historic Site"
  (USS Texas 1914'te hizmete girdi) iyi bir kaynak. Mikasa'nın fotoğraflarının çoğunda modern binalar ve turistler var. Güvertedeki
  turuncu kablo (modern): ton maskesi + maskeli pikseli 34 px yandaki tahtadan kopyalama (iki eşikle iki geçiş). `cv2.inpaint`
  tahtada bulanık bir iz bırakıyordu. Blur 1,8 → kenar Laplace ~20-30 (direk halatları ölçüyü şişiriyor).
- **Sansür yine yakaladı:** "silahsızlandırmak" → "s!lahsızlandırmak", "bombaladı" → "b0mbaladı". Kullanılan karşılıklar:
  "savaş bitene kadar alıkoymak" (tarafsızlık hukukundaki karşılığı) ve "topa tuttu".
- **Commons 429 (28.10 sabah):** art arda arama (generator=search, ~3 sn arayla) dördüncü istekte 429 verdi. Yeniden deneyen ve
  istekler arasında ≥10 sn bekleyen küçük bir `api()` yardımcısı (15/30/45 sn geri çekilme) sonrasında hiç takılmadı. Ham dosya
  sayfası (`index.php?title=File:...&action=raw`) 429 vermedi; yazar ve lisansı oradan doğrula (ilk taslakta yazar adı uydurma
  kalmıştı, ham sayfayla düzeltildi).

**Çalışmayan (deneme):**
- Openverse API (yine yanıt yok).
- Mikasa güvertesi arka plan olarak (turist ve modern bina her kırpımda).
- `cv2.inpaint` ile tahta güvertedeki kabloyu silmek (bulanık iz).
- `iiurlwidth` ≥ özgün genişlik (Morgenthau p185, 1131 px): yine 429 (27.10 dersi geçerli).

**Süre ve maliyet (güncel):**

| Adım | Yerebatan (26.10 akşam) | Orban (27.10 sabah) | Karaköy Tünel (27.10 akşam) | Goeben (28.10 sabah) |
|---|---|---|---|---|
| Hazırlık + okuma | ~5 dk | ~2 dk | ~6 dk | ~7 dk |
| Konu + olgu | ~5 dk | ~3 dk | ~9 dk | ~4 dk |
| Görsel avı | ~6 dk | ~6 dk | ~12 dk (429) | ~10 dk (429) |
| Karakter + yüz | ~5 dk | ~4 dk | ~6 dk | ~6 dk |
| yaml → teslim | ~4 dk | ~3 dk | ~3 dk | ~4 dk |
| Ön kontrol + hakem turları | ~8 dk | ~3 dk | ~6 dk | ~6 dk (ön kontrol + 2 tur) |
| Teslim + commit + belge | ~7 dk | ~4 dk | ~8 dk | ~8 dk |
| **Toplam** | ~40 dk | ~25 dk | ~50 dk | **~45 dk** |

Ücretli API: 0.

**Kod değişikliği önerileri (uygulanmadı):**
- `tools/`: Internet Archive gazete sayfası indirici (`<id>` + sayfa → `page/n<k>_w4000.jpg`) ve Commons PDF sayfa önizlemesi
  (`iiurlparam=page<n>-<w>px`). Bu bölümde elle yapıldı.
- `tools/`: yeniden deneyen, ≥10 sn bekleyen Commons API yardımcısı (bu bölümde `/tmp` altında elle yazıldı; her oturumda yeniden yazılıyor).
- `wojak/censor.py`: "silahsızlandırmak" ve "bombalamak" tarihî metinde sık; istisna listesi ya da `teslim`'de yıldız/rakam uyarısı.
- Önceki öneriler hâlâ açık: `data/karakter_yon.json` yazma izni; render satırındaki süre (yine "9,6 sn", ffprobe 13,95).

### Ek dersler (28.10.2026 akşam, `pera-palas-anahtar-1979`, iki hakemden 8/8, ~40 dk)

Kanıtlanmış yol yine baştan sona çalıştı. Yeni kanıtlanan adımlar:

- **Ortam:** iki depo yine ayrık HEAD'de, `/home/user` yine yoktu. Bağdan önce `test_short_youtube_aciklamasi_hikayeyi_tasir` düştü,
  bağdan sonra 99/99. wojak'ın yerel dalı uzaktan geride açıldı: `git checkout <dal> && git pull origin <dal>` şart.
- **Commons 429, yeni kural (27.10 dersinin düzeltmesi):** `iiurlwidth=2600/1800/2400/790` istekleri `thumburl` olarak
  `upload.wikimedia.org/...?...utm_content=thumbnail_unscaled` (özgün yol) döndürdü; 4 denemede de 429 verdi ve 5 dk kaybettirdi.
  Aynı dosyalar `iiurlwidth=960/1280/1920` ile `thumb.wikimedia.org/.../1280px-...` yolundan ilk denemede indi. Kural: temas sayfası
  için 330 ya da 500, kullanılacak görsel için 1280 ya da 1920 iste. İsteğe yazılan genişliği yanıttaki `thumburl` ile karşılaştır:
  `thumbnail_unscaled` görürsen istemeden standart genişliğe geç.
- **Yeni son kare türü: olayın geçtiği odanın bugünkü renkli fotoğrafı.** Olay belli bir odada geçtiyse ve oda bugün aynı adla
  korunuyorsa ("Agatha Christie Odası"), Commons'taki ziyaretçi fotoğrafı dürüst bir son kare. Odanın kimliğini veren ayrıntıyı
  (duvardaki portre) kadrajda tut, televizyon gibi modern öğeyi dışarıda bırak. Diyalog arka planı aynı odanın kopyası olmasın:
  aynı binanın başka bir odası kullanıldı ("eenpersoonskamer in 2004", yenilemeden önceki hâli).
- **Son kare çeşitliliği için kanıt sırası:** bir önceki bölümün son karesi gazete sayfasıysa, bu bölümdeki gazete sayfası ilk kanıta
  alınır. Bedeli: son kare manşet kadar vurucu olmuyor (görsel hakem 8'de tuttu). Telefonda okunur bir gerçek gazete sayfası ilk
  kanıtta da sorunun "kimin" kısmını cevaplıyor.
- **1926 İngiliz gazetesi kamu malı:** Commons'ta "Christie at Hydro.jpg" (Daily Herald, 15.12.1926, s. 1, yazarı bilinmiyor,
  `{{PD-old-70}}`). 1927 öncesi yayın ABD'de de kamu malı; dosyadaki "Unclear-PD-US" uyarısı eskimiş. 800 px tarama manşet + spot +
  alt başlık üst kırpımıyla (800x575 → 1080x776) telefonda net okunuyor.
- **Gölgeli hazır çizimi düz MS-Paint'e çevirmek:** wojakland `bow_tie_suit_wojak.png` (papyon + yelek; otel görevlisi ya da garson)
  yüzünde gri-mavi yumuşak gölge vardı, başın üstünde ve sağında siyah kontur yoktu. (1) Açık gri-mavi pikseller (en küçük kanal
  ≥ 168, kanal farkı < 40) beyaz. (2) Alfa maskesi `gaussian_filter(2) > 0.5` ile yumuşatıldı. Maskenin 5 px'lik dış şeridi siyah
  yapıldı. Maske dışındaki yarı saydam beyaz hale silindi. Sonuç temiz, eşit kalınlıkta kontur
  (`pera-palas-anahtar-1979/chars/uret.py:otelci`). İlk denemede şerit yalnız "koyu çizgiden uzak" yerlere konmuştu; mevcut
  konturun dışında beyaz benekler kaldı, hepsi siyah yapılınca düzeldi.
- **1970'ler Türk erkeği için hazır karakter:** wojakland `grey_suit_wojak.png` (siyah saç, gri ceket, açık yaka, klasik beyaz yüz,
  900 px). Düzenleme gerekmedi. Ters köşe yüzü: göz/kaş/ağız kutuları beyaza, iri yuvarlak göz (8 px kontur), iç ucu kalkık kaş,
  "O" ağız, alında saç çizgisiyle kırışık arasına 5 mavi çizgi, yüzün önüne 3 damla. Telefonda değişim %1,5.
- **Ters köşe repliği nesneyi değil imkânsızlığı sorsun:** "Bekle, bu paslı anahtar da ne?" izleyicinin S1'den beklediğini
  söylüyordu. "Bekle, anahtarın yerini nereden bildi?" asıl "Ne?!"yi (medyumun yeri bilmesi) soruyor ve yorumda "reklam mı, gerçek
  mi" tartışması açıyor. Özne bir önceki replikte ("Telefonda ... diyor") ekili olduğu için tek başına anlaşılıyor.
- **"Kapının dibini sökün"** kapının kendisini sökmek gibi okunuyordu, "kapının dibindeki döşemeyi sökün" oldu. Replikteki fiilin
  nesnesi tek anlamlı olsun.
- **Kaynaklar bir kişide çelişiyorsa ad yazma:** 2 milyon doları kimin istediği kaynaklarda farklı (otelin sahibi, müdürü, "o dönem
  işletme başkasındaydı"). Metinde "otel yönetimi" yazıldı. Medyumun adı da yazılmadı: yaşıyor olabilir ve "reklam kurgusu" görüşü
  onu dolaylı suçlayabilirdi. `ek_maddeler`'e gerekçesi yazıldı.

**Çalışmayan (deneme):**
- Commons'ta standart dışı `iiurlwidth` (790/1800/2400/2600): `thumbnail_unscaled` özgün yol, 429.
- Openverse API (üç sorgu, 35 sn zaman aşımı; yine yanıt yok).
- Kapı askısındaki kartı `cv2.inpaint` ile silmek (koyu kapıda gri leke). Alttaki aynı kapı panelinden blok kopya işe yaradı.

**Süre ve maliyet (güncel):**

| Adım | Orban (27.10 sabah) | Karaköy Tünel (27.10 akşam) | Goeben (28.10 sabah) | Pera Palas (28.10 akşam) |
|---|---|---|---|---|
| Hazırlık + okuma | ~2 dk | ~6 dk | ~7 dk | ~4 dk |
| Konu + olgu | ~3 dk | ~9 dk | ~4 dk | ~4 dk |
| Görsel avı | ~6 dk | ~12 dk (429) | ~10 dk (429) | ~12 dk (5 dk'sı 429) |
| Karakter + yüz | ~4 dk | ~6 dk | ~6 dk | ~6 dk |
| yaml → teslim | ~3 dk | ~3 dk | ~4 dk | ~3 dk |
| Ön kontrol + hakem turları | ~3 dk | ~6 dk | ~6 dk | ~5 dk (ön kontrol + 2 tur) |
| Teslim + commit + belge | ~4 dk | ~8 dk | ~8 dk | ~8 dk |
| **Toplam** | ~25 dk | ~50 dk | ~45 dk | **~40 dk** |

Ücretli API: 0.

**Kod değişikliği önerileri (uygulanmadı):**
- `tools/`: Commons indiricisi `iiurlwidth`'i standart genişliklere yuvarlasın (330/500/960/1280/1920) ve `thumbnail_unscaled`
  dönen `thumburl`'ü reddetsin. 429'un bugünkü asıl çözümü bu.
- `tools/`: hazır çizimdeki gri gölgeyi düzleştirip eksik baş konturunu ekleyen küçük yardımcı (`otelci()` kalıbı); gölgeli
  wojakland çizimlerinde her bölümde elle yazılıyor.
- Önceki öneriler hâlâ açık: render satırındaki süre (yine "11,2 sn", ffprobe 13,95); `tests/` sabit `/home/user/wojak` yolu;
  `data/karakter_yon.json` yazma izni; Commons API yardımcısı her oturumda `/tmp` altında yeniden yazılıyor.


### EN kanalı (Wojak Past Files): bölüm bölüm ek dersler

**Ek dersler (25.10.2026, `en-lady-be-good`, iki hakemden 8/8, iki tur, ~35 dk duvar saati):**
- **Ters köşe ve kanıt sırası İngilizcede de tutuyor:** "Almost home, just the sea ahead" → "Still over the Mediterranean?"
  → ara kart "A few hours later" → "Wait, where's the sea?" → iki kanıt. Hakem: kart 5,0 sn'de başlamalı; S1 3,0 sn.
- **Belge kanıtı tehlikeli:** askerî kayıp raporunun görüntüsünde grup/filo numarası uyuşmadı (Lady Be Good'un
  376. BG/514. BS'i yerine 333/466), yani kimlik doğrulanamadı. Kanıtı kimliği doğrulanmış fotoğrafla değiştir (USAF
  enkaz fotoğrafı). Belge kullanılacaksa önce Commons dosya sayfasında birim numarasını ve arşiv kimliğini doğrula.
- **Kırpma büyütmesi:** yatay belge kırpımı 560 px genişlikten 1080'e büyütülünce 1,93x bulanıklık ve yetersiz kenar
  üretti (görsel hakem: 482 px yükseklik, 537 altı). Kanıt için tam genişlikte, büyütmesiz görsel seç.
- **Arka plan ölçütü:** düz gökyüzü ağırlıklı kare Laplacian ~2 (hakem: "gradyan, gerçek yer değil"). Kumul rippleli
  ve gölgeli kırpım (Dakhla, CC BY 4.0) Laplacian ~15-20 ve parlaklık ~111 verdi; hakem "kabul" dedi.
- **Düşük çözünürlüklü hazır karakter yüz ifadesini bozuyor:** 205 px'lik `klasik/uzgun` 2,5x büyütüldü ve yumuşadı.
  Renderer'a girmeden önce PNG boyutunu kontrol et (en az ~600 px yükseklik); küçükse aynı kitte büyük varyant seç.
- **Aynı taban yüz iki karakter gibi görünüyor:** A ve B aynı klasik kafa olunca hakem "tek ailede iki yüz" dedi.
  B'yi farklı taban (`ingiliz_er_1915`) ile ayır; kostüm dönemi uymazsa (pith kaskı) bunu RAPOR'da kusur olarak yaz.
- **Ses ayarı (bu ortamda yine):** `music: {file: kanal, volume: 0.197}` → −29,6 LUFS, tepe −17,0 (§ 23.10 notu).
- **Sansür beklenmedik kelime yakalıyor:** İngilizce listesi "died" kelimesini "d*ed" yaptı. Açıklamada "did not survive"
  gibi karşılığı kullan; sansürden sonra `teslim/<id>/metinler/*.txt` kontrol et.
- **Dramatizasyon etiketi:** iki wojak adsız; replikler uydurma; açıklamada ve sabit yorumda "dramatized" notu zorunlu.
  Karakterlere gerçek kişi adı ya da akraba bilgisi girmez. Hakem bunu olgu kontrolünde ayrıca doğruladı.
- **Olgu düzeltmeleri:** yaygın tekrarlanan tarih/sayı farkları (kalıntılar 1960'ta bulundu, 1959'da değil; keşif 1958; yer ziyareti 1959; mesafe 400-440 mil)
  kaynak tablosunda tek satırda uzlaştırıldı; metinde aralık ("400 to 440 miles") kullanıldı.
- **Hakem kalıbı:** iki hakem aynı iş parçacığında ikinci tur için çağrıldı; önceki bulguları bağlamda kaldı, MUST
  kapanışını satır satır tek tek doğruladı. Yeni bağlamda sıfırdan başlatmaya gerek kalmadı.

**Ek dersler (25.10.2026, `en-d-b-cooper`, D.B. Cooper; görsel 4 → 7 → 8, izleyici 6 → 7 → 8; üç tur, ~45 dk duvar saati):**
- **Kafa kesikliği en büyük kusurdu:** kütüphane PNG'si (500x500) üst kısmından kesikti; görsel hakem "kafa düz çizgiyle
  kesilmiş" dedi. Yeni karakter eklemeden önce PNG'nin tepesinin kapalı ve yuvarlak olduğunu aç ve bak. Kit tabanları
  (`assets/kit/klasik`) bu sorunu yaşamadı; önce kit, sonra kütüphane.
- **Kit varyantı ters köşe için yeterli:** `klasik/cok_terli` (kit'in hazır ter varyantı) telefon boyunda okundu; boyama
  yerine kit kullanıldı. Kaş/göz de değişsin istenirse yeni kit varyantı çizilir (hakem SHOULD olarak kaldı).
- **Gün batımı doygun, gün ışığı kabul:** Columbia gün batımı (CC BY-SA) doygunluk 0,57 verdi, hakem reddetti. Gündüz,
  düşük doygunluklu yeni bir fotoğraf (N474US, Northwest 727, doygunluk 0,26) kabul edildi. Hedef: parlaklık ≥ 100,
  doygunluk ≤ 0,35.
- **"Kamu malı" etiketi her ülkede güvenli değil:** Commons'taki bir uçak fotoğrafı "yayımlandı 1978-1989, ihbarsız"
  etiketiyle PD görünüyordu; izleyici hakemi UK ve Almanya telif uyarısı nedeniyle MUST saydı. Kamu malı yalnız ABD
  hükümeti belgelerinde (FBI, NARA) güvenli; sivil fotoğraf CC BY-SA ile.
- **Teletype kanıtı tam satırla kesilir:** yarım satır ("…REVEALS THAT THEY") anlamı kaybettirdi. Satır sınırı arasında
  kes; kağıdı 537 px ve üstüne tamamla; redaksiyon kutularını bozma. Teletype 2,0 sn, son kare 1,5 sn.
- **Kanca bağlamı ilk cümlede:** "Just sit down with me" (ironik ama bağlamsız) izleyiciye hangi olay olduğunu
  söylemiyordu; "Sit down, this is a hijacking" yapıldı. Dramatik ironi için bağlam kelimesi (uçak, kaçırma) ilk
  replikte olmalı.
- **Son replik süre sınırı:** "Wait, they found my money?" (5 kelime) 2,0 sn'ye sığdı; 7 kelime 2,4 sn istedi. Kısaltıp
  `check` ile doğrula. Son replik "para nehirde" biçiminde olay dışı bilgiyi (kaçıranın hayatta olduğunu) çağrıştırmaz.
- **Sansür "bomb" kelimesini bozuyor:** "b0mb" okunmuyordu; NARA'nın "explosive device" ifadesi kullanıldı.
- **Atıf ayrıntısı:** CC BY-SA için kredi "uçak türü ve tescil, tarih, yer, yazar, lisans bağlantısı, kırpma/yumuşatma
  ve büyütme" içermeli; ayrıca "hijack uçağı değil" notu. İzleyici hakemi bu tam biçimi istedi.
- **Olgu notu:** para miktarı FBI ve HISTORY'de 5.800 dolar; Wikipedia 6.000 yazıyor. Metinde "about $5,800" ve kaynak
  satırı yeterli; çelişki açıklamada yazılmaz.

**Ek dersler (26.10.2026, `en-lusitania-warning`, Lusitania uyarı ilanı; görsel 7/10, izleyici 8/10; BEKLET: karakter lisansı + eşik; üç tur):**
- **Görseli tam boyutta incele, önce:** kaynak karakter PNG'si (wojakland `wl_victorian_man_wojak`) şapkada "ChrisClipArt"
  filigranı taşıyordu; küçük önizlemede görünmedi. Yeni karakter için tam boyut gri zeminde bak; filigran, imza, site adı yok mu.
- **Tam yükseklik taşması:** kare kutuda kare ya da yüksek bir kaynak, kutunun tamamına (1080) büyür; alt filigran
  (y≈1495) kanıtın son satırına biner. Çözüm: kaynağı yatayda siyah pay ile genişletmek (1000x826 → kanıt ~890 px).
- **Tek satır replik:** bu bölümde ~28 karakterin üstü ikinci satıra düştü ("Read the paper? She can be / sunk"; "We
  booked the Lusitania for / Saturday"). Hakem yetim kelimeyi MUST saydı. Replik 28 karakter altında tutuldu.
- **Sansür "died" sözcüğünü bozuyor** (yine: "d*ed"). Açıklamada "did not survive" kullanıldı; teslimden sonra
  `metinler/*.txt` kontrol edildi.
- **Kanıt sayfası:** NYT 1915 sayfası gerçek ve kamu malı; Chronicling America (LOC) bu ortamdan 403 (Cloudflare).
  İkincil bir NYT sayfa kopyası yerine Internet Archive taraması yeterli oldu.
- **Karakter lisansı EN kanalı için ana sorun:** wojakland ve HF dataset "Wojaks" topluluk sanatı, lisans sayfası yok ya da
  WTFPL iddiası kazınmış sanata dayanıyor. EN kanalındaki önceki bölümler de kütüphane karakteri kullandı; sahip, kanal
  genelinde bir karar vermeli (BEKLET ile bölüm bazında yönetiliyor).
- **Ter varyantı yetersiz kaldı:** kit tarzı damlalar (üç büyük damla) telefonda görünür ama hakemler yüz ifadesinin
  değişmesini istedi. Golden-era ters köşeleri yüzü değiştirir; EN kanalına temiz bir yüz varyantı kiti gerekir
  (kendi boyamamız değil, hazır çizim).
- **Hakem döngüsü:** tur 1 (görsel 6, izleyici 6) → tur 2 (7, 7) → tur 3 (7, 8). Aynı iş parçacığında ikinci ve üçüncü
  tur; hakemler önceki MUST listesini tek tek kapattı; bu yöntem işe yaradı.
- **Renderer konsolu:** render satırı süreyi bazen yanlış basıyor (10,9 sn; ffprobe 13,95 sn). Kod hatası görünmüyor;
  ilerde `video` satırındaki süre ffprobe ile doğrulanmalı.

**Ek dersler (26.10.2026, `en-great-moon-hoax`, The Great Moon Hoax 1835; görsel 7 → 7,5 → 8, izleyici 7 → 8 → 8; üç tur, ~2 saat duvar saati):**
- **Teslim klasörü yeniden kurulur:** `python -m wojak teslim` `teslim/<id>/` içini siler; RAPOR.md oraya yazılırsa kaybolur. Raporu teslimden sonra bir yedek konumda tut ve wojak-en-ozel'e kopyala.
- **Ters köşe yüzü gözleri de değiştirmeli:** yalnız ter damlası (`cok_terli`) sakin yüzle aynı göz ve kaşları taşıdığı için hakem 7'de kaldı. Klasik kitte gözyaşlı yüz `agliyor` (855 px, göz ve kaşlar değişiyor) iki hakemde de kabul edildi. `uzgun.png` 205 px: kullanılamaz (boy kontrolü).
- **Kanıt başlığı en az 35 px cap ister:** büyük LOC baskısının başlık bloğu 1080 genişliğe ölçeklenince cap ~38 px okundu. 1080x245'lik ince bant hakemde MUST oldu; 1080x720 (alt gravür + başlık) kabul edildi.
- **Commons açıklama alanı kredi kaynağıdır:** "courtesy of the New York Public Library" satırı açıklamadaydı, hakem arama özetinde göremedi. Kredi metnini Commons `ImageDescription` alanından al ve API ile doğrula (`iiprop=extmetadata`).
- **Gazete arşivi 403:** Chronicling America ve loc.gov bu ortamdan erişilemedi. Gerçek 1835 Sun sayfası alınamadı; aynı dönemden baskı (LOC başlık bloğu) kanıt olarak kullanıldı ve açıklamada "print published at the Sun office" yazıldı.
- **Kanıt ve kadraj:** arka plan kenarındaki modern yürüyüşçü kadrajdan çıkarıldı (bg kenar kırpma, zoom yok). Kenar kırpması yalnız görüntünün yatay penceresini kaydırır; ölçek aynı kalır.
- **"Kim konuşuyor" netliği:** B'nin "gazete" olduğu ilk iki replikte belli edildi ("Yeah, our paper says ..."). Açıklamada B'nin yazarın yerini tuttuğu yazıldı.
- **Çelişkili olgu tek cümlede:** "16 Eylül kabulü" Wikipedia'da "admitted fabricated", Civics for Life'ta "resmî düzeltme yok". Metin ikisini de söyledi ("admitted ... though it never printed a formal retraction").
- **Karakter lisansı EN kanalında hâlâ açık:** kit ve kütüphane (wojakland/HF) karakterleri için lisans sayfası yok. Bu bölümde PNG'ler herkese açık depoya konmadı; BEKLET ile sahip kararı bekleniyor.


**Ek dersler (27.10.2026, `en-violet-jessop`, Violet Jessop, Titanic/Britannic; görsel 6 → 7 → 8, izleyici 6 → 7 → 8, olgu 7 → 9 → 9; üç tur, ~25 dk duvar saati):**
- **Ters köşe kelimesi olgusal olmalı:** "Not the Britannic again?" izleyici hakemine göre yanlıştı (Violet Britannic'e daha önce binmemişti; "again" tarihe aykırıydı). Fark etme repliği olgunun içinde kalmalı: "Wait, this is its sister ship?" tur 3'te kabul edildi.
- **Yaş ve sayı cümleleri tek kaynaktaysa yazılmaz:** "at the age of 63" yalnız National Geographic'te vardı, başka kaynak 61 diyordu. Emeklilik yılı ve "about 42 years at sea" bırakıldı.
- **Kit varyantında silüet ve boyut kontrolü:** `klasik/agliyor` (855x1015) kafası küçük ve alt kenarda beyaz blok bıraktı, görsel hakem MUST verdi. `klasik/gozyasli` (899x1022, sakin ile aynı silüet) aynı kutuda kaldı: 6,0 ve 8,5 sn kareleri IoU 0,984 (fark yalnız gözyaşı çizgileri). Ters köşe varyantı seçilirken PNG boyutu ve baş tepesi (y≈997) sakinle karşılaştırılır.
- **Sansür "died" yine bozdu:** "d*ed" çıktı. "lost their lives" ve "lived until" kullanıldı; teslimden sonra `metinler/*.txt` kontrol edildi.
- **Kredi "not cropped" yazarsa hakem düzeltir:** Moudros'un CC BY-SA kredisi "not cropped by us" diyordu, oysa kare kırpılmış ve bulanıklaştırılmıştı; izleyici hakemi MUST yaptı. Değişiklik notu zorunlu: kırpma, doygunluk yüzdesi, parlaklık, bulanıklık, lisans bağlantısı.
- **Açıklama sınırı kredi ve yasal notla aşılır:** "Dramatized" notu ve kredi eklenince Instagram metni 2261 karaktere çıktı (sınır 2200). Kaynak bağlantıları `sources` listesinde zaten var; kredi satırından çıkarıldı.
- **Commons Artist alanı kredi kaynağıdır:** fotoğrafçı adı (Allan C. Green) `extmetadata` içindeki Artist alanından alındı; sayfa açılmasa da API ile doğrulanabildi.
- **"Own work" etiketi tutarsız olabilir:** c. 1915 portre Commons'ta "Own work by ..." diyordu. Kamu malı yaşa göre; not edilir, kırpılmış sürümle karşılaştırılır.
- **Dönem karakteri yoksa kusur olarak yaz:** kütüphanedeki hemşireler modern kıyafetli; 1912–16 kadın wojak bulunamadı. Klasik erkek çizim kullanıldı, RAPOR'da bilinen kusur.
- **Arka plan doygunluğu:** sahil fotoğrafının gökyüzü doygunluğu 0,60 "kartpostal" dedirtti; %55 doygunluk ve −%10 parlaklık ile 0,40 altına indi (görsel hakem 8).
- **Paylaşımlı yön kaydı:** `python -m wojak yon` kaydı `data/karakter_yon.json` içinde sha1 anahtarlarıyla tutar; aynı PNG baytları başka bölümde varsa dosya yolu değişebilir. Commit öncesi `git diff data/karakter_yon.json` ile kontrol edilip başka bölümün girdisi geri alınır.
- **Render satırı süresi yanlış basabiliyor:** render "12,2 sn" yazdı; ffprobe 13,45 sn ve 403 kare gösterdi. Teslimde süre ffprobe ile doğrulanır.

**Ek dersler (27.10.2026, `en-mincemeat`, Operation Mincemeat 1943; görsel 7 → 7,5 → 8, izleyici 5 → 7 → 8; üç tur, ~33 dk duvar saati):**
- **Yön kaydı paylaşımlı, commit öncesi kontrol:** `python -m wojak yon` aynı baytlı mevcut kit PNG'lerinin `data/karakter_yon.json` `file` alanını yeni bölüme çevirir ve bir dosyayı silinmiş bırakabilir. Yönler değişmez; yine de `git diff data/karakter_yon.json` ile kontrol edip başka bölümün girdisini `git checkout` ile geri al.
- **Replik tek satırda kalmalı:** 2 satıra düşen replikte son kelime yalnız kalıyordu ("major", "novel?"); görsel hakem MUST saydı. "Dress him as a Royal Marine" ve "Wait, it came from a novel?" tek satırda kaldı ve kapak kadrajı temizlendi.
- **Sansür "dead", "died", "corpse", "death" kelimelerini bozar:** başlık ve açıklamada "body" ve "passed away" kullanıldı; teslim sonrası `metinler/*.txt` kontrol edildi.
- **Olgu çelişkisi plaket üzerinde:** plaket ölüm tarihini 24 Nisan 1943 yazıyor (kapak hikâyesi tarihi); kayıtlar Ocak 1943. Açıklamada bu tek cümleyle açıklandı; izleyici hakemi MUST 3'ü bununla kapattı.
- **Kelepçe ayrıntısı kaynaklarda çelişiyor** (bilek ya da palto kemeri): metin "chained ... to him" yazdı, ayrıntı vermedi. Tartışmalı ayrıntıyı tek ifadeyle geçmek MUST'ı kapattı.
- **Kimlik kartı fotoğrafı bir MI5 subayına ait:** adını yazmadık (yaşam durumu doğrulanmadı); yalnız "an MI5 officer, not Michael" notu.
- **Arka plan reçetesi (Huelva kıyısı):** 1620x1620 kırpma (gökyüzü ~%25), `ImageEnhance.Color(0.6)` ve `Brightness(0.93)`: ölçü S 0,31, L 122; görsel hakem 0,24-0,27 ve 128-136 ölçtü, kabul.
- **Plaket 1080 genişlikte 871 px yüksek:** 40 px üst ve alt kırpma ile 816 px'e indi (spec 537-816).
- **1915 kaskı (ingiliz_er_1915) 1943 subayı için yanlış dönem:** tek renkli 1939-45 İngiliz karakteri kütüphanede yok; HF renkli adaylar stil uyumsuzluğu yarattı. Bilinen kusur olarak raporlandı; kanal için 1940'lar kit ihtiyacı açık.
- **Ters köşe yalnız ter damlasıyla** (klasik/cok_terli, aynı kutu): telefonda okunur bulundu, görsel hakem 8/10'da kabul etti; kaş ve göz değişimi daha iyi olurdu (SHOULD, açık).


**Ek dersler (28.10.2026, `en-mona-lisa`, Mona Lisa'yı Italy'ye satmaya çalışan hırsız, Peruggia 1911-1913; görsel 7 → 7 → 7, izleyici 6 → 8; üç tur, BEKLET: görsel 7/10):**
- **Bakış kaydı dosyanın kendi gözüyle yapılır, ama render ile birlikte doğrulanır:** PNG'nin gözbebekleri göz merkezinin sağındaysa dosya sağa bakar, kayıt `sag` olmalı. Yanlış kayıt (`sol`) render'da görüntüyü aynalayıp karakteri dışa bakar hale getirdi. Ayrıca gözlerin "sakin" hali ile "şok" varyantı ayrı kontrol edilir: aynı kayıt iki dosyada da doğru olsa bile gözbebeği yerleşimi ayrı ayrı ölçülür.
- **El ile yüz varyantında gözbebeği sonradan ayarlanır:** `klasik` kitinde olmayan şok yüzünü kütüphane gövdesine çizdik; gözbebeği içe bakmadı, nokta kaldı. Hakem 1:1 ölçümüyle yakaladı. Düzeltme: beyaz boyayla eski göz içini silip gözbebeğini oval içinde sağa taşımak, nokta silmek. Sakin göz de aynı mantıkla yeniden çizildi (temiz oval, sağda gözbebeği).
- **İkinci satır yetim kelime:** "The Louvre's Mona Lisa? Seriously?" tek satıra sığmadı, "Seriously?" tek başına kaldı. Elle satır kırma (`\n`) ile iki eşit satır yapıldı; hakem kabul etti.
- **Noktasız repliklerde virgül:** "I've got the Mona Lisa. Want her?" denetimde ve hakemde nokta olarak kaldı. "I've got the Mona Lisa, want her?" yazıldı; konuşma dili korundu.
- **Kanıt kırpımı küçük bir kızın ölümünü gösterebilirdi:** NYT sayfasının orta sütununda bir bomba haberi (küçük bir kız ölümü) vardı. Kırpım manşet sütunu ve bir sonraki sütunun başına kadar yapıldı; alt satır tam kesilmedi. Kanıt kırpımında gazete sayfasının başka haberlerini kontrol et.
- **Olgu ASFi ile düzeltildi:** "Paris'te sandıkta sakladı" ifadesi ASFi'de yok: sandık (çift dipli) Floransa otel odasında arama sırasında bulundu. Mektup İtalya'ya satış teklifi içeriyor; "geri verme" ise Peruggia'nın kendi iddiası. Metinde "offered to sell the painting to Italy" ve iddia "Peruggia said ..." biçiminde. Mektup imzası "Leonard V.", "Leonardo Vincenzo" değil. 500.000 lira "later accounts" ile.
- **Sansür "died" kelimesini bozdu:** "d*ed" yine çıktı; "passed away" kullanıldı, `metinler/*.txt` sansürden sonra kontrol edildi.
- **Görsel hakem: karakter boyu ve kare** 0,48 → 0,53 (STIL aralığı içinde) yüzleri büyüttü; arka plan (Floransa, Palazzo Vecchio, CC0) turistik kartpostal gibi bulundu: bilinen kusur.
- **Kostüm dönemi:** 1911 Louvre işçisinin beyaz önlüğü yerine tulum ve kasket kullanıldı; Geri'nin fötr şapkası 1913 için biraz geç. Kütüphanede uygun dönem karakteri bulunamadı; bilinen kusur olarak RAPOR'da.
