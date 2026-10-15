# Öğrenilenler: kısa reel'de 3/10'dan 8/10'a

> Ekibin bilgi defteri (12.10.2026). Kaynaklar: dört onaylı kısa bölüm (`van-depremi-azra-bebek`,
> `canakkale-kayip-tabur`, `kiz-kulesi-efsanesi`, `talidomit-turkiye`), bunların `episode.yaml` ve
> `teslim/*/paylasim.md` dosyaları, yeniden üretim turlarındaki hakem ve üretici raporları, talidomit araştırma notları.
> Ölçü kaynağı yine [`STIL.md`](STIL.md)'dir; bu belge **neden** ve **nasıl** sorularını cevaplar.
> Uzun format kararları: [`UZUN_FORMAT.md`](UZUN_FORMAT.md). Güncel olay ve hukuk: [`GUNDEM.md`](GUNDEM.md) §5, §7.

---

## Hesap sahibinin doğrudan geri bildirimi (hakemlerden önce gelir)

| Tarih | Ne dedi | Bundan sonra kural |
|---|---|---|
| 09.10 | İlk parti 3/10: "tarihselwojak kalitesinde değil"; atıf yazıları ve dışarı bakan karakterler | STIL.md ölçüleri; etiket yok; karakter hep içeri bakar |
| 11.10 | Yeniden yapılan 3 kısa video: "güzel duruyolar beğendim" | Bu üçü + talidomit = kısa reel referans seti |
| 12.10 | Talidomit kısa: "çok iyi, uzmanlaştın" | Kısa reel hattı oturdu; uzun format başladı |
| 13.10 | Uzun video: **videoyu beğendi, sesi beğenmedi** (Cartesia Murat) | Ses ElevenLabs kredisi gelince yeniden üretilecek; o zamana kadar ses değişmez. Yeni sağlayıcıda sesler yine ölçerek seçilir (§ uzun format) |
| 13.10 | **Kendi çizdiğimiz kıyafetler kötü** (wojak başı + elle boyanmış tişört/yaka, boyun dikiş izleri) | Kıyafetli karakter **hazır** bulunur (wojakland, wojaksparadise, kütüphane: tek parça çizim). Kıyafet çizmek/yamamak son çare; yapılırsa hakem yakın plan kontrolü zorunlu. Hazır kıyafetliler "okay" |
| 13.10 | Yüz ifadeleri beğenildi ama daha iyi olabilir | Varyant: aynı çizgi kalınlığı, temiz göz/ağız, telefonda okunur fark; yakın plan yüz sayfası her bölümde |
| 13.10 | Animasyon kalitesi beğenildi ama **hatalar var**, daha iyisi yapılabilir | Uzun videoda ayrı bir "animasyon/karakter" hakemi: kare kare sıçrama, titreme, kırpılma, çakışma, katman sırası |
| 13.10 | Bitiş ekranındaki 2 video kutusu gereksiz (kanalda henüz 2 uzun video yok) | Bitişte video kutusu yok (kanalda yeterli video olunca yeniden düşünülür). Abone/beğeni/yorum çağrısı **düz değil, ilgi çekici**: hikâyeye bağlı soru + wojak'lı animasyon |
| 13.10 | Instagram açıklamalarında **hashtag kullanmıyoruz** | `pack.py` Instagram metnine hashtag koymaz. YouTube'da 2-3 hashtag serbest |
| 13.10 | YouTube başlığı **"AI slop" gibi durmamalı**, ilgi çekici olmalı | Başlıkta abartı sıfatı, emoji, "şok" kalıbı yok; merak boşluğu + somut ayrıntı (yer, sayı, kişi) |
| 13.10 | Teslim: videolar Telegram botuyla (kalite kaybı olmadan) | `tools/telegram_gonder.py`: 50 MB altı Bot API belgesi; üstü TELEGRAM_API_ID/HASH ile tek parça (<= 2 GB, `tools/telegram/gonder.js`: MTProto, WSS üzerinden, çünkü ortamın vekili düz MTProto'yu geçirmiyor), yoksa 7-Zip parçaları. Sohbet dosya sınırı 30 MB |
| 13.10 | "Yapayım geçeyim değil, sınırlarını zorla; benchmarktasın gibi düşün" | Her teslimden önce: hakemler 8+ VE kendi gözümüzle kare kare kontrol; bilinen bir kusurla teslim yok, varsa açıkça yazılır |
| 15.10 | Uzun video (14. tur): **"baya iyi olmuş beğendim"**; bundan sonraki uzun videolar bu kalitede | `uzun/talidomit-turkiye` uzun video referansı. Bütün adımlar yeni gelen biri için [`ADIM_ADIM.md`](ADIM_ADIM.md)'de, ajan istemleri [`is_akislari/`](is_akislari/README.md)'nde |
| 15.10 | Bazı sahnelerde **yüzler fazla büyük**, altta kesik (Kaymakçalan + "RUHSAT BAŞVURUSU" dosyası) | Ölçüldü: etkin boy (`boy` × zoom × `yakin`) dört sahnede 0,87-0,96. Kural ≤ 0,80, dramatik yakın plan ≤ 0,88 ve en çok 1-2 kez (UZUN_FORMAT §2.9). Düzeltme ElevenLabs turunda |
| 15.10 | Uzun videoda filigran gerekli mi? Kaldırılabilir, ama **şimdi değil**, ElevenLabs sesleriyle birlikte | Karar: uzun videoda gömülü filigran yok (`filigran: false`), YouTube Studio markalama filigranı; kısa reel'de kalır (UZUN_FORMAT §2.8) |
| 15.10 | Talidomit kısa reel'inin karakterleri de uzun videodaki kadar kaliteli olsun (yüz ifadeleri) | v2 karakterlerle B sürümü, görsel hakem orijinallerle karşılaştırır, seçim hesap sahibinin (YAYIN_PLANI §4.5) |
| 15.10 | Yayın planı: 2-3 günde bir konu; öğlen uzun video YouTube'a, akşam aynı konunun Shorts + Reels'i; açıklamalar uzun videoya yönlendirir | [`YAYIN_PLANI.md`](YAYIN_PLANI.md). **Yeni video ve düzeltme ElevenLabs başvurusu sonuçlanınca** başlar |

### Uzun format: ilk videodan dersler (talidomit, 12-13.10)

- **Kredi bütçesi:** 10 dk'lık anlatım ~8.600 karakter; düzeltmelerle video başına ~11-13 bin. Ses testleri ve
  deneme videosu ayrıca ~6 bin harcadı. Önbellek şart: yalnız değişen satır yeniden seslendirilir.
- **Wojak payı:** ilk kurguda karakterli sahne süresi %27'ydi ("wojak kanalı için az"); misafir wojak katmanı,
  anlatıcı wojak ve sayaç/harita yanında tepki veren karakterlerle %50'nin üstüne çıktı. Hedef baştan %50+.
- **Tekrar eden görsel:** aynı fotoğraf 5 kez kullanılınca hakem "dolgu" dedi; görsel başına en fazla 2 kullanım.
- **Yazı çakışmaları:** damga/etiket/kelime katmanları yüzlere ve başka yazılara biniyordu; her turda kare taraması.
- **Efekt tepe sesleri:** bölüm kartı boom/whoosh kulaklıkta irkiltiyordu; konuşma medyanının en fazla +3 dB üstü.
- **Doruk anı:** başlığın cevabı (Ankara'daki "hayır") ilk kurguda zayıf kaldı; doruk sahnesi en güçlü kamera,
  damga ve yüz değişimiyle kurulmalı, en az 1,2 sn okunur kalmalı.
- **Puan seyri:** izlenme 7 → 6,5 → 7 → 8 → 7,5; Türkçe/olgu 6,5 → 8,5; teknik 8,5 → 9,5. İzlenme hakemi en zor
  ikna olan; sahibin beğenisi geldi, kalan kusurlar yukarıdaki tabloda kural oldu.

---

## 0. Tek bakışta: puanı yükselten 10 ders

1. **Tahmin etme, orijinali ölç.** Puanı en çok yükselten adım 30 altın dönem reel'inin kare kare ölçülmesiydi
   (STIL.md). Ölçüler kodun varsayılanına ve `python -m wojak check` içindeki `[stil]` denetimine girdi. Kural bir
   kişinin hafızasında değil, kodda durmalı.
2. **Hakemi orijinale göre kalibre et.** İlk partiye kendi eleştirmenimiz 7-7,5/10 vermişti; hesap sahibi 3/10 verdi.
   Hakemler aynı ölçekte yan yana karşılaştırma (bizim kareler + C2kk, C4V3...) ve sabit çapalarla puanlamaya
   başlayınca puanlar dürüstleşti: 10 = orijinalden ayırt edilemez, 8 = uzun süreli takipçi telefonda hiçbir şey
   fark etmez, 6 = düzgün taklit. **Genel puan ortalama değildir; en zayıf görünen öğe puanı sınırlar.**
3. **İki bağımsız hakem, iki farklı mercek.** Görsel sadakat hakemi ve Türk takipçi + senaryo + olgu hakemi. Biri
   ötekinin kaçırdığını yakaladı (örnekler §2.3).
4. **İki kişi, aynı yer, aynı an.** A hep solda, B hep sağda; B önce A'ya cevap verir; her sahnede yalnız konuşan
   görünür. İlk denemelerdeki üç konuşmacılı, on yıllar arasında gezen monologlar formatı öldürüyordu.
5. **Ters köşe = aynı kutu, yüz varyantı + fark etme sorusu; cevabı son kanıt sessizce verir.** Van: "Bekle, sütün
   yoksa 2 gündür nasıl dayandı?" → son kare Takvim manşeti "Anne, Azra'yı tükürüğüyle besledi".
6. **Çift anlamlı replik ve önceden ekilmiş kelime.** Çanakkale: "Bir şey olmaz, öbür tarafta görüşürüz" ilk
   izleyişte bulutun öbür tarafı, ikincisinde öbür dünya. S1'deki "tabur", S5'teki "koca tabur"u hazırlar.
7. **Yüz kodu anlam taşır.** Kanalda sırıtma kötü karakter demek. Kız Kulesi'nin imparatoru sinsi göründüğü için
   ters köşe "baba bilerek yaptı" diye okunuyordu; sevecen yüzle trajediye döndü.
8. **Son kare döngü noktasıdır.** Sorunun cevabını vermeli ve altın dönemin dilinde olmalı: kalın manşetli küçük
   resim ya da basılı kupür. Gri yazılı mobil web sayfası ya da koyu müze kartı puanı 8'de tuttu.
9. **Olgu disiplini.** Güven düzeyli olgu tablosu, kaynak soy ağacı ve "güvenli ifade" listesi. Zayıf kanıtlı
   bilgi ekranda bulgu değil niyet olur ("Ben önce tavuk embriyosunda deneyeceğim"), metinde "anlatılana göre".
10. **Her şey `episode.yaml` ve betiklerden üretilir.** `teslim/` elle düzenlenmez. Hesap sahibine giden her not
    (lisans, moderasyon, ilk yorum) `telif_notu` ve `ek_maddeler` ile pakete girer; `notes` hesap sahibine ulaşmaz.

---

## 1. Puan tarihçesi

| Tarih | Ne oldu | Puan |
|---|---|---|
| 09.10 öğleden sonra | İlk parti: Çanakkale, Nusret, Van (ve daha önce Derinkuyu, Dyatlov). İç eleştirmen orijinallerle yan yana bakmadı, kendi kurallarımıza göre puanladı | İç eleştirmen 7-7,5/10, **hesap sahibi 3/10** ("tarihselwojak kalitesi değil") |
| 09.10 akşam | 30 orijinal ölçüldü → STIL.md; render varsayılanları ve `check` stil denetimi buna çekildi | — |
| 10.10 | Yeniden üretim turları (Van, Çanakkale, Kız Kulesi; Nusret çıktı), hakem ölçümüyle | 6-7/10 |
| 11.10 öğlen | Son kalite turu, iki bağımsız hakem | Van 8/8, Çanakkale 7,5/7,5, Kız Kulesi 7,5/7,5 |
| 11.10 akşam | Rötuş turları | Van 8/8, Çanakkale 8/8, Kız Kulesi 8/8 |
| 12.10 | **Yeni bölüm, öğrenilen akışla baştan sona:** Talidomit ve Türkiye. Sabah araştırma, öğleden sonra 3 hakem turu | 8/8, aynı gün teslim |

Hakemlerin tavan notları: Van'ın ödülü "ürperti" değil "şefkat" (tükürükle beslenen bebek), tavan 9'un altında.
Çanakkale ve Kız Kulesi'nin ters köşesi bilinen bir efsaneyi doğruluyor, şaşırtmıyor (Kız Kulesi için bir ara tur hakemi
"en iyi ihtimalle ~7" demişti; arka plan, yüz ve kanıt düzeltmeleriyle yine de 8'e çıktı). **8'den 9'a cila değil konu taşır:**
az bilinen, doğrulanabilir, "bekle, NE?!" dedirten olaylar (C2kk, C2Fr, C2P kalıbı).

---

## 2. Puanı yükselten dersler (örneklerle)

### 2.1 Ölçüm koda girer

İlk teslimdeki hataların neredeyse hepsi ölçülebilir sapmaydı (STIL.md Ek, 34 madde): kanıttan sonra diyalog (5/5
reel'de; orijinalde 0/30), noktalı ve üç noktalı anlatıcı cümleleri, sahne başına yeni ve karartılmış arka plan, Ken
Burns, sarsıntı, flaş, pop-in, Poppins font, 1,55 kat büyük yazı, −16 LUFS (orijinal −29,5) ve her videoda 5-6 ses
efekti. Bunlar bölüm bölüm düzeltilseydi tekrar ederdi. Çözüm kodda:

- Render varsayılanları STIL.md değerlerinde (Avenir Bold Italic 55 px, 2 satır, greedy kırma, baş üstünde 55 px,
  karakter boyu 0,48, hareket yok, filigran her karede, `music: kanal`, −29,5 LUFS, efekt yok).
- `python -m wojak check` her sapmayı `[stil]` uyarısı olarak verir. **Uyarıyla tartışılmaz, düzeltilir.**
- Yolda bulunan render hataları da düzeltildi: video sesten 2 kare geç başlıyordu ve her kesme 67 ms kayıyordu
  (`-bf 0`); yazı katman kutusuna göre konuyordu, görünen mürekkebe göre değil; okuma süresi uyarısı orijinallere
  göre ayarlandı; render kapağı her seferinde 1. sahneyle eziyordu (`cover_scene` / `cover_at` alanları geldi).

### 2.2 Hakem kalibrasyonu

- Hakem dosyalara dokunmaz, kendi klasöründe çalışır, önce ölçer sonra iddia eder.
- Yöntem: 0,5 sn'de bir kare (bizim reel + en az 3 orijinal, C2kk ve C4V3 her zaman); aynı ölçekte yan yana
  sayfalar; yüz kırpımları 1:1 ve 2x; telefon boyu (390 px) ve profil ızgarası (3:4, ~260 px) görünümü; kare
  farkıyla kesme tespiti; sahne içi ilk-son kare farkı; yazı bloğu merkezi; yüz değişim alanı.
- Çapalar sabit (§0, madde 2). Düzeltmeler etkiye göre sıralı, **MUST / SHOULD / COULD** etiketli ve uygulanabilir
  değerlerle verilir: kırpım kutusu, yeni replik, dosya yolu, süre.
- "Engeller" alanı: olduğu gibi yayınlanırsa hesap sahibini utandıracak her şey.

### 2.3 İki hakem birbirini tamamlar

| Bölüm | Görsel hakem yakaladı | Takipçi/olgu hakemi yakaladı |
|---|---|---|
| Van | Annenin yüzü C3De'deki kadından %21 küçük; Takvim karesi %35 saf beyaz, manşet gri | Kurtarmacının S4 bakışı anneden **dışarı** kaçıyor (görsel hakem tersini yazmıştı); hikâye metnindeki "aile enkaz altında kaldı" yanlışı (dede dışarıdaydı); repodaki eski commit'lerde soyadı |
| Çanakkale | Kanıt 2 kanıt 1'in fotoğrafına yakınlaşma gibi okunuyor; E1 telefonda soluk | Hikâye metninde dört olgu hatası (bulut "yere indi" değil "yere oturmuş"; 1919 mesafesi kaynaklarda çelişiyor) |
| Kız Kulesi | Sébah fotoğrafında kule küçük, üstünde boş gökyüzü fazla | İmparatorun yüzü "sinsi"; başlıkta "nasıl yani?" fiili yok; isim kökeni cümlesi eksik |
| Talidomit | Ters köşedeki 6 özdeş mavi çubuk "tarak" gibi; telefon arayüzü simgeleri kanıtta | Kaynaksız "1950'lerin sonunda" tarihi; S2-S5 zinciri ("hamileler → embriyo → bebekler") |

Hakemler çelişirse **orijinaller ne yapıyorsa o yapılır** (karelere bakılarak). Örnek: Van S2'de görsel hakem
"metne dokunma", takipçi "Duyuyoruz" dedi; orijinallerde B önce A'nın sorusuna cevap verdiği için (C3De, C2Fr)
"Duyuyoruz abla, delik dar, bebeği uzat" seçildi.

### 2.4 Diyalog iskeleti

- **C2fa (Havran mağarası) iskeleti** iki bölümde birebir işe yaradı: A masum ya da ironik niyet → B uyarır
  ("Emin misin? ...") → A geçiştirir ("Bir şey olmaz, ...") → "Bir süre sonra" kartı → B ya da A aynı kutuda yüz
  değiştirip fark eder → 2 kanıt. Çanakkale ve Talidomit bu kalıpla yazıldı.
- **A B A B soru-cevap kalıbı** (C2kk, C3iX mekanizması): son replik bir soru, cevabı son kanıt. Van ve Kız Kulesi.
- İlk replik olay anında ve konuşanın ağzından kancadır: "Sesimi duyan yok mu?" (Türk deprem hafızasının "Sesimi
  duyan var mı?" cümlesini tersine çevirir), "İyi ki doğdun kızım, bak sana üzüm getirdim" (efsaneyi bilen 1 sn'de
  "eyvah, üzüm" der), "Almanya'da reçetesiz satılıyor, hamileler bile kullanıyor" (sonunu bilene ilk saniyede ürperti).
- Zincir kur: Talidomit'te S1 "hamileler" → S2 "embriyo" → S5 "bebekler". Kız Kulesi'nde S1 "getirdim" → S4
  "getirdiğin üzümler" (yılanı koruyucu babanın kendisi getirdi).

### 2.5 Ters köşe görseli

- Aynı karakter, aynı piksel kutusu, yalnız yüz değişir: sakin → terli → alında mavi soğuk ter → gözyaşı/korku.
- Telefon boyunda okunmalı. Hakemlerin ölçüsü: 390 px'te, eşik 40, karenin yüzde kaçı değişti. Orijinaller
  C4V3 %0,60 ve %1,01, C2Fr imamı %0,77. Bizde Van annesi %0,52, kurtarmacı %0,85, Kız Kulesi prensesi %1,57;
  Talidomit'te şapka yüzü küçük tuttuğu için %0,39 (C12O'nun %0,40'ı düzeyinde, alt sınırda).
- En güçlü ters köşe aracı arka planın kendisi olabilir: Çanakkale'de S1-S3 aynı kare + bulut katmanı + buluta
  yürüyen tabur kolu; S5 aynı kare, katman yok. "Aynı vadi, bulut gitti, tabur yok" telefonda anında okunur.

### 2.6 Kanıt sırası ve son kare

- Sıra soruya göre kurulur. Van'da bir turda "en güçlü kareyle bitsin" diye AFP fotoğrafı sona alındı; S4 bir soru
  olduğu için son turda geri çevrildi: önce AFP (bebek yaşıyor), sonra manşet (nasıl yaşadı).
- Altın dönem son kareleri: kalın manşetli küçük resim, gazete kupürü, TV alt bandı (75 referansın son karesi
  tarandı). Bizim en iyi son karelerimiz: East Oregonian 1916 sayfası ("The Men Who Never Came Back") ve kamu malı
  1915 fotoğrafı üstüne kendi Anton başlığımız ("ÇANAKKALE'DE / KAYBOLAN TABUR!", medya logosu yok).
- Puanı tutan son kareler: Van'daki Takvim mobil sayfası (gri manşet, 253 px'ten büyütülmüş fotoğraf; daha iyisi
  bulunamadı) ve Kız Kulesi'ndeki koyu, imzalı sergi kartı (yılanı gösteren tek görsel).

### 2.7 Olgu disiplini (Talidomit örneği)

Araştırma notu (`olgular.md`) şu bölümlerle yazıldı ve bütün metin kararlarını taşıdı:

- **Olgu tablosu, güven düzeyiyle:** Y (≥2 bağımsız kaynak), O (aynı kök ya da sözlü tanıklık), D (tek kaynak), ✗.
- **Kaynak soy ağacı:** kim kimi tekrarlıyor. Aygün'ün tavuk embriyosu anlatısı tek bir 2008 haberine dayanıyordu;
  Kaymakçalan'ın olumsuz görüşü dört meslektaşın tanıklığına. Viral gönderi bu iki bağımsız kökü tek bir
  neden-sonuç zincirine bağlamıştı; hiçbir kaynak bunu söylemiyor.
- **Viral gönderi cümle cümle:** "kutusunda yazıyor" yanlış (İngiliz reklamında), ad yanlış yazılmış, "tek iki ülke"
  yanlış (ABD'de de vaka var, Doğu Almanya da ruhsat vermedi).
- **Güvenli ifade kalıpları** ve **kullanılmayacaklar** ("tek bir mağdur yok", "1957'de Bakanlık reddetti").
- **Dramatizasyon sınırları:** kim, nerede, ne diyebilir. Temsilci adsız (firma adı, logo yok; kötü yüz yok);
  Aygün ile Kaymakçalan aynı sahnede yok; mağdur bebek ya da anne çizilmez.

---

## 3. Tekrarlayan hata türleri ve çözümleri

### 3.1 Karakterler

| Belirti (örnek) | Çözüm |
|---|---|
| Duyguyla çelişen yüz: ilk Van'da anne enkaz altında gülümseyen, allıklı bir çizimdi; bir sahnede hiç karakter yoktu | Her diyalog sahnesinde tam 1 konuşan; duyguya uygun taban çizim; varyantlar aynı tabandan (`tools/kit_varyant.py`) |
| Stil dışı çizim (gölgeli, ressamsı, yapay zekâ görünümlü, yamalı) | Önce en yakın hazır çizim: `tools/wojak_site.py` (wojakland/wojaksparadise), `tools/wojak_lib.py`. Van annesi wojakland "Blushing Hijab Wojak"tan, C3De'deki kadına neredeyse birebir. Düzenleme elle değil `assets/kit/<ad>/uret.py` ile |
| Bakış dışarı kaçıyor (Van S4'te göz bebekleri dış köşede) | Her yeni PNG'ye bak ve `python -m wojak yon <png> --yon sag|sol|on` ile kaydet; gerekirse her gözü kendi kutusunda aynala. İstisna: orijinal de yapıyorsa ters köşede dışa kaçan bakış (C2fa S5, Çanakkale S5) |
| Yüz kodu yanlış anlam veriyor (Kız Kulesi imparatoru ağır kapaklı yan bakış + yarım sırıtış = "sinsi") | Sevecen karakterde düz kaşlar, açık yuvarlak gözler, açık gülüş; dişler tek tek çizilmez (creepy grin'e kaymasın). Kötü yüz yalnız gerçekten kötü karaktere; şüpheli, firma ya da gerçek kişiye asla |
| Ters köşede taban yüz değişiyor (Van: Tired → Nervous Wojak) | Mümkünse aynı taban + ter/mavi çizgi (C4V3, C2kk). Değişecekse kostüm aynı kalsın; telefonda baret ve mont farkı örter |
| Mavi soğuk ter çizgileri yapay (Talidomit'te 6 özdeş 11 px çubuk "tarak" gibi) | 4-5 düzensiz, hafif S kıvrımlı, kancalı el çizgisi; ekranda ~3 px; kaşları kesmez (C2kk 4,0 sn ve C4V3 12,5 sn alınları örnek) |
| Karakter küçük ya da büyük (Van annesinin yüzü C3De'den %21 küçük) | `height` medyanı 0,48, izinli 0,42-0,55 (onaylı bölümler 0,49-0,53); iki konuşmacının baş üstü yakın olsun ki yazı bloğu reel boyunca ±20 px sabit kalsın |
| Kafa havada, büst yok (Kız Kulesi prensesi) | Büst alt kenardan kesilir; kitte kırpımı aşağı uzat |
| Dönem dışı kostüm | Kaynaktan doğrula: 1915 Norfolk tropik üniforma + Wolseley mantar miğfer (Brodie 1916'da geldi); İzmir kurtarmacısının kırmızı mont ve bareti AFP fotoğrafındakiyle aynı |
| Taç "sarı baret" gibi, saç "bere" gibi okunuyor | Telefon boyunda bak: taça inci dizisi ve haç; saçı düz gri + 3 ince tel. 1:1'de görünüp telefonda görünmeyen ayrıntıya (pendilia) emek harcama |
| Gerçek kişiye benzerlik | Fotoğraftaki belirgin özellikler (Aygün'de gözlük ve bıyık yok → Grandpa Wojak'tan silindi). Serbest fotoğraf yoksa benzerlik genel kalır |
| Bakış kaydında eski sha1 girdileri kalıyor | Yeniden üretilen dosyaya yeni ad ver ya da eski girdiyi temizle (`data/karakter_yon.json`); başkasının girdisine dokunma |

### 3.2 Ters köşe repliği

| Belirti | Çözüm |
|---|---|
| Kanıttan sonra açıklama ya da kapanış repliği (ilk partide 5/5) | Kanıt en sonda ve sessiz; ters köşe son diyalogdur |
| Replik resmin zaten gösterdiğini anlatıyor ("Bekle, bulut kalktı, tabur nerde?") | İmkânsız olanı sor: "Bekle, koca tabur nereye gitti?" |
| İzleyici sonu başlıktan ve S1'den tahmin ediyor (Çanakkale, Kız Kulesi) | Konu seçiminde çöz; replikle telafi edilemez. Hiç değilse başlık sonu söylemesin |
| "Aww" etkisi, "bekle, NE?!" değil (Van) | Kabul et ya da konu değiştir; tavan 8 |
| İstenmeyen çağrışım (Van'da "neyle besledin?" kanaldaki Uruguay 571 yamyamlık repliğini çağırıyordu) | Kanalın eski reel'lerini bil; soruyu hikâyenin kendi kelimesine bağla ("sütün yoksa") |
| Satır sonunda tek kelime kalıyor ("... bebeklere / ne oluyor?" yerine greedy "oluyor?"u yalnız bırakıyordu) | Elle `\n` ile soru öbeğini bütün tut; üst satır uzun, alt satır kısa kalsın |
| "Şimdiki zaman" kuralını gramer sanmak (Çanakkale'de "geçicez" reddedilmişti) | Kural "o anda söylenmiş" demek; orijinaller "gidicez", "dönerim", "kurtarayım" kullanır |
| Yazı dili ("rüzgarda bile") | Konuşma dili: "Emin misin? Rüzgar var, bulut hiç kıpırdamıyor". Hakemin önerdiği replik de `check`'ten geçmeli: 8 kelimelik öneri 2,5 sn'de okuma uyarısı verdiği için 7 kelimeye indirildi |

### 3.3 Kanıt seçimi

| Belirti | Çözüm |
|---|---|
| Etiket, bant, kâğıt zemin, ok, ızgara (ilk Çanakkale: kırmızı "Hiçbiri geri dönmedi." bandı, krem kâğıt, keyfi bir eri gösteren kırmızı ok) | Tek görsel, 1080 genişlik, y=960'a ortalı, 537-816 px yükseklik; hiçbir ekleme yok |
| İki kanıt aynı fotoğraftan (kesme yakınlaşma gibi okunuyor) | İkinci kanıt başka bir kare olsun (Sandringham Bölüğü 1915) |
| Son kare soru cevaplamıyor ya da yanlış dilde (mobil web sayfası, müze kartı) | Önce basılı sayfa ya da kalın manşetli küçük resim ara. Bulunamazsa mevcut olanı tut, sahte haber ya da kendi "haber" grafiğini üretme. Gri manşete yalnız genel ton düzeltmesi (siyah nokta) yapılabilir |
| Telefon arayüzü, çerez penceresi, reklam görüntüde | Yakalamayı CSS ile temizle, simgeleri çubuk rengiyle boya; manşet ve fotoğraf piksellerine dokunma; yapılanı `sources` ve `telif_notu`'na yaz |
| Yapay zekâ çizimli, yazım hatalı ya da sunucu yüzlü küçük resimler (Kız Kulesi'nde 14 aday, Çanakkale'de 12 aday incelendi) | Kullanma; gerçek kamu malı fotoğraf daha güçlü kanıttır |
| Konu küçük, göz başka yere gidiyor (Sébah fotoğrafında kayık) | Konuya göre 16:9 kırp; insanları ortadan kesme |
| Telefonda soluk belge (East Oregonian) | Gama/kontrast ayarı; kâğıt beyazı ≥243 kalsın |
| Manşet hikâyenin tartışmalı yanını kesin gibi gösteriyor ("kurtaran büyük doktor: Aygün") | `telif_notu`'nda açıkça uyar, sayfadaki yanlış iddiaları listele, iki hazır yedek ver (biri izin gerektirmeyen) |
| Mağdur görüntüsü şok malzemesi | Kişi değil nesne: talidomit çocuğu için yapılmış protez (Science Museum, CC BY-SA 2.0) |

### 3.4 Arka plan

| Belirti | Çözüm |
|---|---|
| Her sahneye yeni fotoğraf, karartma, gri ton (ilk parti) | Bütün diyalog için tek renkli, gün ışığı fotoğraf; ikincisi yalnız karttan sonra ya da gerçek mekân değişince |
| "Aynı türden yer" zayıf kalıyor (Kız Kulesi'nde Alanya Kızılkule iç mekânı mavi, pencere patlamış) | Olayın gerçek yeri, tanınır açıdan: Kız Kulesi'nin kendisi (Türk izleyici 0,3 sn'de tanır), Suvla ovası, AKUT'un Van enkazı fotoğrafı |
| Düz gökyüzü kareyi kaplıyor | Kare kırpımı aşağı kaydır (Van: 530 px aşağı → çökmüş döşemeler kareyi doldurdu) |
| Renk ve parlaklık | Diyalog karesi parlaklığı ~115-125, doygunluk ~0,20; `ImageEnhance` ile ve değişiklik `credits`'e "kırpıldı, renk düzeltildi" |
| Kaynak zaten yumuşak, varsayılan blur 2,5 fazla geliyor | Kenar Laplace varyansını ölç (720 ölçeğinde hedef medyan ~22); Çanakkale'de 2,5 ile ~4 çıkıyordu, `blur: 1.2` ile 17-22 |
| Hikâye katmanı yapay (sis alt kenarı cetvel gibi düz, siluetler dev) | Alt kenar gürültülü; silüet boyunu ağaç tepelerine göre dene (38 → 30 → 18 px) |
| Yazı arkası çok parlak (Çanakkale'nin sisi) | Okunuyorsa bırak; hakem daha sıkı kırpım ve griye çekmeyi denedi, daha kötü çıktı. Ölçmeden "düzeltme" yapma |

### 3.5 Ekran yazısı

- Font Avenir LT Std Bold Italic (`assets/fonts/ozel/`, lisanslı, repoya girmez). Poppins'e düşmesin: render
  makinesinde dosyanın varlığını kontrol et.
- Replik 1-11 kelime (medyan 5); nokta ve üç nokta yok, ünlem neredeyse yok; en fazla 2 satır, greedy kırma.
- **Okuma kuralı** (`check`): kelime/3,5 + 0,4 ≤ süre + 0,15. Pratikte 2,0 sn → en fazla 6 kelime, 2,5 sn → 7,
  3,0 sn → 9.
- Blok baş üstünden 55 px yukarıda, reel boyunca sabit; büyük "İ"nin noktası bloğu ~11 px yükseltir, normaldir.
- Elle kırımı yalnız cümle sınırında ya da virgülde kullan ("Ne gerek var hocam, / tamamen zehirsiz").

### 3.6 Zamanlama

- Toplam 13,5-14,0 sn, bütün süreler 0,5 sn'nin katı. Onaylı ritimler:
  - Çanakkale (C2fa): 2,5 / 2,5 / 2,5 / kart 1,5 / 2,0 / 1,5 / 1,5
  - Van (C2kk ile kare kare aynı): 3,0 / 2,5 / 2,5 / 2,5 / 1,5 / 2,0
  - Kız Kulesi (kartsız): 3,0 / 3,0 / 2,5 / 2,5 / 1,5 / 1,5
  - Talidomit: 2,5 / 2,5 / 2,0 / kart 1,5 / 2,0 / 1,5 / 2,0
- Kanıt ~10,5-11,0 sn'de başlar; son kanıt 1,5-2,0 sn.
- Üçüncü kanıt çoğu zaman 14,0 sn'yi aşar ya da bir diyalogu 2,0 sn'ye indirip okuma uyarısı doğurur: genellikle değmez.

### 3.7 Hikâye metni (sabit yorum / Instagram açıklaması)

| Belirti | Çözüm |
|---|---|
| Uzunluk sınırı | 150-250 kelime; açıklamanın tamamı ≤ 2.200 karakter (Kız Kulesi 2.164 ile sınırdaydı). `paket`/`teslim` sayımına bak |
| Aranan adlar yok | İlk paragrafta halkın kullandığı adlar: "kaybolan Norfolk Alayı", "düşmanı yutan bulut" |
| Kişi tanıtılmamış | "Çanakkale'deki İtilaf kuvvetlerinin başkomutanı General Ian Hamilton" |
| Belirsiz virgül ("Türk kaynaklarına göre ilerleyen birlik, ...") | Virgülü taşı: "Türk kaynaklarına göre, ileri atılan birlik ..." |
| Kaynaksız tarih ("1950'lerin sonunda") | "Aynı yıllarda" gibi kaynakla çelişmeyen ifade |
| Yaşayan çocuk için geçmiş zaman ("hayali ... olmaktı" → "öldü mü?" sorusu) | "Dedesi 2017'de ... çocuk doktoru olmak istediğini anlatmıştı" |
| "Aha" eksik | Efsanenin isim kökeni (Kız Kulesi), bilinen bir sonraki olaya köprü |
| Kapanış sorusu yorum getirmiyor | Yerel ya da ikili tartışma sorusu: "Aranızda o gün Van'da ya da Erciş'te olan var mı?", "Sizce o gün Anafartalar'da gerçekten bir bulut var mıydı?" |
| Sansür kelimeyi bozuyor | `teslim/<id>/metinler/*.txt` dosyalarını sansürden sonra oku |
| Moderasyon ve ilk yorum önerisi `notes`'ta kalmış | `ek_maddeler`'e yaz; `paylasim.md` kontrol listesine yalnız o girer |

### 3.8 Olgular

- Her ekran repliği, başlık ve metin cümlesi en az iki bağımsız kaynakla; hakemler kaynak URL'lerini açıp 10-12
  olguyu tek tek doğruladı. Bunu üretici de yapmalı.
- Kaynaklar çeliştiğinde sayı yuvarlanır ya da hiç verilmez: Van'da 45,5 / 46 / 47 / 48 saat → "yaklaşık 47 saat";
  Çanakkale'de 1919 kalıntılarının mesafesi 500 ve 800 yarda → yalnız "Türk ön hattının gerisinde".
- Kim neredeydi, tek tek: Van'da dede apartman çökerken dışarıda kalmıştı, "aile enkaz altında kaldı" yanlıştı.
- Bulut yere "indi" değil, bildiriye göre "yere oturmuş"tu: kaynaktaki kelimeyi çevir, yorumlama.
- Efsane efsane olarak anılır ("söylenen", "anlatılana göre", "Bu iddiayı doğrulayan bir belge yok").
- Zayıf kanıtlı bilgi ekranda niyet, metinde "anlatılana göre". Gerçek kişiye uydurma tırnaklı söz yazılmaz; yakın
  tarihte ölen birine son söz verilmez (Van'da hayatını kaybeden babaya replik yok, tek nötr cümle).
- Viral gönderiyi cümle cümle kontrol et; gönderinin kurduğu neden-sonuç zincirini kaynak kurmuyorsa sen de kurma.

### 3.9 Lisanslar

- Öncelik kamu malı ve CC. Her görselin lisansı, URL'si ve yapılan değişiklik `sources`'ta; CC BY/BY-SA atfı
  `credits`'te (CC BY-SA 3.0 eserin adını ve lisans URI'sini ister). Lisansı Commons dosya sayfasında doğrula.
- Telifli görsel (ajans fotoğrafı, gazete sayfası, belediye sergisi çizimi) `episodes/<id>/img/telifli/` altında
  durur (git'e girmez). `telif_notu`: ne olduğu, kimin olduğu, neyin değiştirildiği, izin kimden istenmeli, hazır
  serbest yedek ve yedekte `credits`'in nasıl değişeceği. **Karar hesap sahibinin.**
- Haber görseli kullanılıyorsa kaynak adı açıklamada kalır (alıntıda kaynak gösterme); silmek durumu kötüleştirir.
- Kendi küçük resmimizde yazı fontu Anton (SIL OFL). Wojak çizimleri: wojakland'de şart yok, wojaksparadise
  yükleyenin malı; kaynağı `sources`'a yaz.
- Wikimedia sık 429 verir: istekler arasında en az 10 sn; olmuyorsa birkaç dakika sonra.

### 3.10 Çocuk mahremiyeti ve ağ gizliliği

- **Yaşayan reşit olmayan** (Van'daki bebek bugün 15 yaşında): yalnız ailenin kamuya açıkladığı ilk ad ve 2011
  yenidoğan fotoğrafları. Soyadı, anne-baba adı, mahalle, okul, bugünkü fotoğraf ya da "şimdi nerede" bilgisi
  hiçbir yerde yok.
- **Repo herkese açık.** Bu bilgiler `episode.yaml` notlarına, `sources`'a, `paylasim.md`'ye de yazılmaz. Gizli
  kelimeler (Hidden Words) listesi hesap sahibine **yalnız sohbette** verilir; `ek_maddeler` listeyi ad vermeden
  tarif eder.
- **Ders:** iki eski commit'in notlarında babanın tam adı (yani çocuğun soyadı) kalmıştı ve dal herkese açıktı.
  Geçmişi temizlemek hesap sahibinin kararıdır (repoyu gizli yapmak ya da onaylı geçmiş yeniden yazımı); ajan
  push/force-push yapmaz. Önlem: özel kişilerin aile adlarını taslak notlara bile yazma; `.cache/` gibi izlenmeyen
  klasörlerde de kalmasın.
- Mağdurlara saygı: engellilik şok ya da şaka malzemesi değil; mağdur çizilmez; hakaret kelimeleri gizli kelime
  listesine ("ucube", "oh olsun", "geberdi").
- **Ağ:** bir hakem bir kez Commons'a giden isteğin User-Agent'ına hesap e-postasını koymuştu (raporunda kendisi
  açıkladı). Her istekte genel bir tarayıcı User-Agent'ı; e-posta ya da kişisel tanımlayıcı hiçbir başlıkta ya da
  istekte yok; ağ vekil sunucusu (proxy) asla atlanmaz.

### 3.11 Kapak, ses, filigran

- Kapak bir diyalog karesi, etiketsiz: `cover_scene` + `cover_at`. Seçim ölçütü profil ızgarasında konunun
  okunması: kanca karesi konuyu söylüyorsa (Çanakkale S1'de bulut ve tabur) onu, ters köşe yüzü daha güçlüyse onu
  seç; alternatifi hesap sahibine ver.
- Ses `music: kanal`, −29,6 LUFS civarı, efekt yok; video ve ses 0,000'da başlar.
- Filigran her karede (kart ve kanıt dahil).

---

## 4. Teslim öncesi kontrol listesi

**Yapı ve zaman**
- [ ] `python -m wojak check episodes/<id>`: hiç `[stil]`, okuma süresi ya da bakış uyarısı yok
- [ ] 13,5-14,0 sn; bütün süreler 0,5 sn katı; ilk sahne 2,5-3,0; kart (varsa) tek, ileri zaman, iki diyalog arasında
- [ ] Kanıt en sonda, 2-3 görsel; kanıttan sonra hiçbir şey yok
- [ ] Teslim edilen mp4'te kesmeler ölçüldü (kare farkı), sahneler durağan, video ve ses 0,000'da başlıyor

**Replik**
- [ ] İki kişi, aynı yer, aynı an; A hep solda, B hep sağda; her sahnede yalnız konuşan
- [ ] İlk replik kanca (olay anı, konuşanın ağzından); B önce A'ya cevap veriyor
- [ ] Son diyalog ters köşe: aynı kutu, yüz varyantı, fark etme sorusu ya da dramatik ironi; cevabı son kanıt veriyor
- [ ] Nokta yok, üç nokta yok, ünlem neredeyse yok; konuşma dili; satır sonunda yetim kelime yok
- [ ] Hiçbir replik olgularla çelişmiyor; gerçek kişiye uydurma söz yok

**Karakter**
- [ ] Düz MS-Paint wojak ailesi; duyguya uygun yüz; kötü yüz yalnız kötü karakterde
- [ ] Her yeni PNG'ye bakıldı ve `yon` ile kaydedildi; karakterler içeri bakıyor
- [ ] Yüz değişimi telefon boyunda (390 px) okunuyor; boy 0,42-0,55; kostüm döneme uygun

**Arka plan ve kanıt**
- [ ] Tek (en fazla iki) renkli gerçek fotoğraf; karartma, gri ton, hareket yok
- [ ] Kanıtlar 1080 genişlik, y=960 merkez, 537-816 px; etiket, bant, ok, kenarlık yok
- [ ] Son kare sorunun cevabı ve altın dönem dilinde; telefon arayüzü ve reklam temiz

**Ses, filigran, kapak**
- [ ] `music: kanal`, ~−29,5 LUFS, efekt yok; filigran her karede
- [ ] `kapak.jpg` doğru sahne (`cover_scene`), etiketsiz, bantlar saf siyah

**Metinler**
- [ ] Başlık KONSEPT §4 kalıbında, sonu söylemiyor, dürüst ("söylenen")
- [ ] Hikâye 150-250 kelime, ansiklopedik ilk cümle, kronolojik, soruyla bitiyor; açıklama ≤ 2.200 karakter
- [ ] `metinler/*.txt` sansürden sonra okundu; bozuk kelime yok
- [ ] Moderasyon, ilk yorum, zamanlama `ek_maddeler`'de; hashtag'ler yerel aramaya uygun

**Olgu, lisans, mahremiyet**
- [ ] Ekrandaki, başlıktaki ve metindeki her olgu ≥2 kaynakla; çelişen sayılar yuvarlandı ya da çıkarıldı
- [ ] Her görselin lisansı ve değişikliği `sources`'ta; CC atfı `credits`'te; telifli görsel `img/telifli/` altında
  ve `telif_notu` + serbest yedek hazır
- [ ] Reşit olmayanın soyadı, ebeveyn adı, okul, mahalle hiçbir dosyada yok (yaml notları dahil); gizli kelime
  listesi yalnız sohbette
- [ ] Güncel olaysa GUNDEM.md §5'in 12 maddesi tek tek işaretlendi

**Süreç**
- [ ] `frames` → kareler gözle incelendi → `render` → `teslim`; `teslim/` elle düzenlenmedi
- [ ] Yan yana sayfa (bizim kareler 0,5 / 3,0 / 6,0 / 9,0 / 11,5 / 13,0 sn + 2 orijinal, aynı ölçek) yapıldı ve
  dürüstçe değerlendirildi
- [ ] İki hakem ≥ 8/10, MUST ve engel kalmadı
- [ ] `git status`: video, telifli görsel, özel font ve kanal sesi listede yok

---

## 5. İşe yarayan üretim akışı

```
araştırma ──► üretim ──► iki bağımsız hakem (paralel) ──► düzeltme ──► (hakemler) ... ──► teslim ──► commit
 olgular.md     yaml, kit,     görsel sadakat               MUST + SHOULD    iki hakem ≥8,    teslim/<id>/   video ve telifli
 gorseller.md   check→frames→   takipçi + senaryo + olgu     çelişkide        MUST yok         + sohbette     görsel hariç
                LOOK→render→
                teslim, yanyana
```

1. **Araştırma** (scratchpad'de, repoya değil):
   - `olgular.md`: kısa hüküm, güven düzeyli olgu tablosu, kaynak soy ağacı, viral iddia cümle cümle, tartışmalı
     noktalar, güvenli ifade kalıpları, dramatizasyon sınırları, hikâye metni taslağı, kaynak URL'leri.
   - `gorseller.md`: kanıt, arka plan ve karakter adayları sıralı, lisansıyla; temas sayfaları (contact sheet);
     hazır atıf satırları.
2. **Üretim:** üretici STIL.md'yi baştan sona okur, ilgili orijinalleri izler (en az C2kk, C4V3, C2Fr, C12O, C3De,
   C3In), `episode.yaml`'ı yazar, kitleri `uret.py` ile kurar, `check` → `frames` → bakar → `render` → `teslim`
   yapar, yan yana sayfayı kurar ve raporunu `son_uretici_raporu.md`'ye yazar.
3. **İki bağımsız hakem**, paralel, dosyalara dokunmadan (§2.2). Çıktı: genel puan, alt puanlar ve ölçümler,
   sıralı düzeltmeler (MUST/SHOULD/COULD, kesin değerlerle), engeller.
4. **Düzeltme döngüsü:** üretici önce engelleri ve MUST'ları, sonra sert kuralı ya da olguları bozmayan SHOULD'ları
   uygular. Çelişkide orijinallere bakar. Önceki turların iyileştirmelerini geri almaz. Her düzeltme için ne yapıldı,
   ne yapılamadı ve neden, raporda yazar. Kod (`wojak/`, `tools/`) bu döngüde düzenlenmez; hata raporlanır.
5. **Durma noktası:** iki hakem ≥ 8 ve MUST yok. Ötesindeki cila gerilemeyi kazançtan daha olası kılar (Çanakkale'nin
   son görsel hakemi: "Further churn at this stage risks regressions"). 9 için konu değiştir.
6. **Teslim:** `python -m wojak teslim` → `teslim/<id>/` → dosyalar sohbetten hesap sahibine; lisans kararları ve
   gizli kelime listesi sohbette. Onaydan sonra hesap sahibi kendisi paylaşır.

---

## 6. Zaman ve emek notları

- URETIM_REHBERI'ndeki "bir video ≈ 30-45 dk" hedefi 8/10 kalite için gerçekçi değil. Gerçekleşen:
  - İlk parti (3 video): yaklaşık bir gün, sonuç 3/10.
  - Ölçüm (30 reel) ve render ayarı: aynı günün akşamı, birkaç saat. En yüksek getirili iş buydu.
  - Üç bölümün yeniden üretimi: yaklaşık 1,5 gün, bölüm başına 4-6 tur.
  - Yeni bölüm, oturmuş akışla (Talidomit): yaklaşık bir iş günü. Sabah olgu araştırması, öğlen görsel avı,
    üretim ve 3 hakem turu yaklaşık 2-2,5 saat; tur başına (hakemler + düzeltme) ~30-40 dk.
- Zamanın çoğu nereye gidiyor: (1) karakter kitleri (hazır çizimi bulmak, düzenlemek, yüz varyantları);
  (2) kanıt avı ve lisans (14 küçük resim adayı, mobil/masaüstü yakalama denemeleri); (3) Wikimedia 429 beklemeleri.
- Yeniden kullanılabilir kitler zaman kazandırır: `assets/kit/` altında `klasik`, `kurtarmaci_klasik`,
  `anne_basortulu2`, `ingiliz_er_1915(_biyikli)`, `prenses_genc`; Nervous Wojak tabanı (`ingiliz_er_1915/taban/`)
  Talidomit'in ters köşe yüzünde tekrar kullanıldı.
- Hakem ölçüm betikleri ve referans kareleri scratchpad'de kalır; her yeni bölümde baştan yazılmaz.
- Açık kod notları (raporlanan, düzeltilmedi): bakış kaydı eski sha1 girdilerini tutuyor; `frames` eski kare
  dosyalarını silmiyor; `pack.py` Instagram'da `#tarihselwojak #wojak` etiketlerini her zaman ekliyor (yerel etiket
  takası hesap sahibine `ek_maddeler` ile bırakıldı).

---

## 7. Uzun formata ne taşınır?

UZUN_FORMAT.md bazı kısa format kurallarını bilerek tersine çevirir: sürekli hareket (4-6 sn'de bir yeni şey),
anlatıcı sesi, efekt, −14 LUFS, isim etiketi ve bölüm kartları serbest. **Aynen taşınanlar:**

- Olgu disiplini: aynı olgu tablosu ve güvenli ifade kalıpları; zayıf kanıt "anlatılana göre"; viral zincir kurulmaz;
  tartışmalı kişiler aynı sahnede gösterilmez.
- Karakter dili: düz MS-Paint wojak, içeri bakış, duyguya uygun yüz, kötü yüz yok, mağdur çizilmez; ters köşede yüz
  varyantı.
- Kanıt mantığı: gerçek belge sorunun cevabıdır; telifli olan `img/telifli/` altında ve hesap sahibinin kararına.
- Mahremiyet, lisans, ağ gizliliği ve gizli anahtar kuralları birebir.
- İki bağımsız hakem + düzeltme döngüsü; hakem çapaları uzun format için yeniden yazılmalı (izlenme süresi, tempo,
  seslendirmenin isimleri doğru okuması).

### 7.1 Uzun format, talidomit-turkiye hakem turlarından (13.10.2026)

- **14. tur (14.10):** Yavaşlatılmış (rubberband) her klibin son 5-9 ms'i tam bantlı bir patlamaydı: videoda 11 tık,
  hiçbir görsel denetim görmez. Ses onarımında klip sonu ölçülür (son 20 ms / önceki 45 ms); motor artık her klibi
  söndürür ve patlamayı bildirir. Yakın pano kamerası ağırlık merkezine kayınca uzun kartı kesiyordu: kamera kartları
  güvenli alanda tutar. Kelimenin baskı kenarına "yapıştırılmış" durması için kenar bandı denetimi on yer buldu
  (hakem dördünü görmüştü). Bir denetimi geçen düzeltmeye yine bak: dosya yukarı kayıp kadrajdan taşınca yazı
  "içinde" sayıldı; kare görünce dosya aşağı alındı.
  Tık taramasını yalnız klip sonlarında değil, anlatım izinin sıfıra inip çıktığı HER yerde yap: Cartesia `<break>`
  araları da konuşmayı sönümsüz kesiyordu (hakemin listesinde yoktu; 8:11'de -12 dBFS'ten sıfıra). Motor artık bu
  kenarları da yumuşatır.

- **Vurgu damgası en az 1,2 sn ekranda kalmalı.** Damganın iniş anından sahne sonuna kadar 0,5-0,8 sn kalınca hakem
  "flaş gibi geçiyor" dedi: vurgu satırına `sonra: 1.1-1.3`. Koyu zeminde koyu kırmızı damga okunmuyor: beyaz/sarı, ya
  da kırmızıyı açık bir nesnenin (dosya, kâğıt) üstüne bas. Aynı tipten damga 30'u geçince etkisi düşüyor.
- **Kanca ilk 15 sn'de bir wojak göstermeli** (küçük resim karakter vaat ediyorsa) ve vurgu cümlesinin görseli 1+ sn
  okunur kalmalı. Doruk (hikâyenin cevabı) bilgi kartıyla değil, karakterli bir sahneyle verilir.
- **Ardışık iki çekimde aynı karakter aynı tarafta kalır** (taraf atlaması göze batıyor).
- **Kesik kafa:** kaynak PNG'nin satır 0'ında opak piksel varsa saç tuvalden taşmıştır; tuvali tepeye aç.
- **Havada duran nesne:** göğüsten kesik karakterlerin yanında nesnenin alt kenarı da kadraj altına taşmalı
  (`alt` pozitif); negatif `alt` nesneyi yukarı kaldırır.
- **Zaman damgaları YUKARI yuvarlanır** (bölüm, ara reklam, bitiş ekranı): aşağı yuvarlanan damga önceki cümlenin
  ortasına düşer.
- **TTS kotası bittiğinde:** yanlış okunan ilk kelime/cümle sessizlikten kesilebilir, ikiz ünsüz ("cüzzam") z
  uzatılarak düzeltilebilir, hızlı satır rubberband ile yavaşlatılabilir; her sonuç iki Whisper çözümlemesiyle
  doğrulanır ve hesap sahibine zaman damgalı dinleme listesi verilir. Whisper nadir adları bağlama göre böler
  ("talih domit"): temiz bir çekimi nakletmek de bunu her zaman düzeltmez, kulak karar verir.
- **4. tur (hesap sahibi + üç hakem):** "Wojak kanalı": harita/sayaç/pano/belge sahneleri tek başına karakter taşımaz.
  Bilgi sahnelerine köşeden tepki veren karakter (`konuk`) eklendi; anlatıcı (hardal kazaklı klasik wojak) ya da
  sahnenin kişisi (Lenz haritada, Kelsey FDA sayacında, Kaymakçalan Türkiye haritasında). Ölçüm (zaman çizelgesi,
  kişi karakterin görünür olduğu süre / toplam): %26 -> %68. Yazıyla çakışmaması için konuk köşede, kelime üstte,
  fotoğraf baskısı yana (`x`).
- **Görsel tekrarı:** aynı fotoğraf (kırpımı ya da baskısı dahil) en çok 2 çekimde. 5 kez görünen Sağlık Bakanlığı,
  teneke, büro yerine kendi düz çizimlerimiz (koridor, bakanlık odası, eczane, büro, kara tahta, karton, duvar). Aynı
  dünya haritası da "görsel"dir: bölgesel görünümler (Kuzey Atlantik, Hint Okyanusu yarıküresi) kullan.
- **Karanlık kare:** koyu bilgi zemini ve harita denizi telefonda "kapkara" (kare ortalaması ~15-25/255). Hedef
  >= 45 (bölüm kartı ve bilinçli düşüşler hariç): motor paletini aç, `karart` 0,2-0,3.
- **Efekt tepesi 100 ms pencerede ölçülür:** bölüm kartı boom'u ve imza, medyan konuşmanın +7-9 dB üstündeydi;
  motor artık altlığı medyan konuşma +2 dB ile sınırlar (`tepe_siniri`).
- **Sayılar altyazıda rakamla** (Türkçe altyazı geleneği: ondan büyük sayılar rakam): `metin` rakamla, `tts` eski
  kelimeli metin (önbellek anahtarı TTS metninden: yeniden seslendirme gerekmez).
- **Sınırlayıcı 4x örneklemede:** 48 kHz'de alimiter örnekler arası tepeyi kaçırıyordu (gerçek tepe sınırın ~3 dB
  üstü); doğrusal loudnorm koşulu için döngü sınırı -9,7 dBFS'e indiriyor, sesin ~4,6 LU'sunu eziyordu. 192 kHz'de
  sınırlama: 100 ms pencerelerde medyan kazanç düşümü 2,9 -> 0,0 dB.
- **5. tur (yeni Cartesia anahtarlarıyla):** kesik/uzatılmış çekimler temiz çekimle değişince dinleme listesi 22 -> 11
  satır, Whisper "KONTROL ET" 17 -> 2. Dersler:
  - Açıklayıcı iki noktada TTS durmuyor ("bir boşluk var:|Türkiye"): `tts` alanında `<break time="300ms"/>`. Cartesia
    araya 0,5-1,0 sn koyuyor; öteki cümle sonları kadar olsun diye en çok ~0,5 sn'ye kısaltıldı (`ses_onarim.py durak`).
  - Durak yeri anlamı değiştirir: "Asıl soru, hiç araştırılmamış hamile bir kadın…" (yanlış). Durak gereken yerde
    cümleyi böl ("…kimse araştırmamış. <break/> Hamile bir kadın…").
  - Cartesia `speed` 0,9 hece hızını az düşürür (9,3 -> 8,1 hece/sn); 0,82-0,86 gerekti. Hız değişince anahtar da değişir.
  - Her yeniden çekim zar atmak: 2-6 deneme üretip iki Whisper çözümlemesiyle seç ("En önemlisi" 3 denemenin
    1'inde 'denenmiyor'). İkiz zz ("cüzzam") hiçbir yazımla düzelmedi ('cüz-zam', 'cüzzzam'; 'cüzam' tek z okunur):
    z uzatılmış eski çekim kaldı. Whisper "talidomit"i ara durak sonrası hep "Tali Domit" yazıyor (tanıyıcının dili).
  - Yeni duraklar ve yavaş okuma süreyi uzatır (+13 sn): 10:15 sınırı için sahne sonu 0,32 -> 0,26, damga sonrası
    1,2 -> 1,0 sn, bitiş ekranı 10,5 sn ve Türkiye sorusuna katkısı en az olan sahne (Alman davası) çıktı.
- **6. tur (üç hakem + hesap sahibi):** yeni TTS yalnız metni/hızı değişen satırlara, satır başına bir çekim (9 istek).
  Dersler:
  - Tez damgası cümleyle yarışmasın: videonun vardığı cümlenin damgası cümle BİTİNCE iner, ardından 1,3 sn sessizlik
    (`sonra: 1.3` + `muzik db:-40`); 0,55 sn'de "flaş" gibi geçiyordu. Süre bitiş ekranından (10,5 -> 9,3 sn) alındı.
  - Whisper'ın her çözümde yanlış duyduğu kısaltma ("FDA" -> "FTA"), yeniden çekim yerine iki sessizliğin arasından
    kesilebilir; bilgi ekranda kalır (altyazıda parantez içinde). Kelsey adını en net söyleyen çekim korunmuş olur.
  - Cartesia `speed` her çekimde farklı tepki veriyor: 0,92 bir satırı %9 yavaşlattı, 0,9 öbürünü %2; 0,85 virgüle
    0,7 sn durak koydu (0,45'e kısaltıldı). Yavaşlatılan bir çekim "faciayı"yı yuttu: eski çekim kaldı. Her yeni çekimi
    iki Whisper çözümüyle dinle; bozuksa eskisini koru.
  - Tekrarlanan kelimeyi metinden çıkarmak ("Talidomite" -> "İlaca") tanıyıcının bölme sorununu da bitirir.
  - Damga sahnenin kendi yazısının (takvimdeki ay, şişe) üstüne basılmaz: yanına ya da üstüne; açık zeminde varsayılan
    kırmızı soluk pembe görünüyor: `renk: [168, 0, 22]` + `kontur`. Yüze binen damga yasak (B5.3c'de ilk deneme yüze
    biniyordu: kare kontrolüyle yakalandı).
  - Aynı karakter art arda dört çekimde aynı kadrajda kalmasın: boyu değiştir (0,56 / 0,72 / 0,86), tarafı değil.
  - Düz doku zemin (mavi kâğıt, karton) "ucuz" görünüyor: ya kendi çizimimiz bir oda (hekim odası) ya da bilinçli
    yakın çekim (`vinyet: 0.8` + kamera 1,0 -> 1,3).
  - Küçük resimde en çok üç öğe (yazı, karakter, bir simge); zemin doygun kırmızı-siyah radyal: açık ve koyu akışta
    öne çıkar.
- **7. tur (animasyon sorumlusu, hesap sahibinin "animasyonda hatalar var" notu):** göz kararı değil ölçüm:
  `tools/uzun_animasyon_denetimi.py` videoyu 30 fps çözer, motoru öğe öğe izler (her çizim çağrısı), şüpheli anları
  zaman damgasıyla verir; her bulguya tam çözünürlükte bakılır. Bulunanların çoğu motordaydı ve düzeltildi
  (UZUN_MOTOR §3 "Hareket dili"): kenardan giren karakter kare başına 150-280 px "zıplıyordu" (hareket bulanıklığı +
  eğilip yaylanma), hızlı sayaçta rakamlar her karede titriyordu (tekerlek), köşe göstergesi kutusu ±9 px titriyordu
  (tabular rakam), vurgu kelimesi kesmede yarı saydam kalıyordu, süzülen yazı 1 px adımlarla zıplıyordu (alt piksel),
  damga sesi 40 ms erken, whoosh ve deklanşör 0,22 sn geçti (efekt dosyasının vuruş anı ölçülerek). YAML tarafındaki
  dersler: `konum: ust` kelime varken karakterin baş üstü >= 0,25 H; kamera itmesi olan sahnede yan karakter x 0,28-0,72
  (itme onu kadrajdan çıkarır); vurgu ülkesi/çağrı kesmeden en az ~1 sn önce gelsin; dekor (kapı, raf) `canli: false`.
- **Bitiş:** iki "sıradaki video" kutusu yerine `kapanis` sahnesi (açık soru + seçenek kartları + imleçle abone/zil/beğen
  + yorum balonu); kanalda yeterli uzun video olunca kutular yeniden düşünülür.
- **7. tur yapımcı (hazır kıyafetli karakterler, kapanış çağrısı):**
  - Baş-omuz kesimli hazır çizimlerde çene kadrajın alt çeyreğine iner: alt banttaki isim etiketi aynı taraftaysa çeneye
    biner. Etiket karakterin karşı tarafına (`konum`), o köşedeki nesne yukarı/masaya.
  - Kapanış çağrısının seçenekleri, videonun kendi açık sorusuyla (KP.1: kahraman mı, kural mı, şans mı?) aynı olsun;
    belgesiz anlatı (Aygün) seçenek yapılmaz. Sabit yorum aynı A/B/C sorusu. Yeni ses yalnız "Sizce hangisi?".
  - Kapanışın zemini koyu kalmasın (karart 0,55'te ilk saniye 37/255: "video bitti" hissi); 0,38 yeterli.
  - Masaya/duvara konmuş dekorda `canli: false` + sahnede `kamera: {paralaks: 0}`; havadaki nesneler salınabilir.
  - Motor hataları (bu turda yaml ile aşıldı, rapor): wojak sahnesinde `yon: pop` küçük ölçekte `alt_piksel`'de çöküyor;
    foto atıfı yakınlaşmasız baskı boyuna göre konuyor, `zoom` > ~1,04'te baskı atıfın üstüne büyüyor.
- **8. tur (dört hakem: izlenme 8, animasyon 6,5, dil 8,4, teknik 9):**
  - Hareket bulanıklığı bütün sprite'ı bulandırınca yüz yarı saydam "hayalet"e dönüyor (girişlerde kafatası gibi
    görünen anlatıcı, arkasından rafları görünen anne adayı). Doğrusu: keskin, tam opak katman üstte, en çok 40 px'lik
    iz altta (çizgi film "smear" dili). Bir karede bakınca da temiz olmalı: hakem duraklatıp 1:1 bakıyor.
  - Çapraz geçiş aynı karakteri iki kez gösterir (biri sönerken öbürü belirir): 20 yerde vardı. Aynı karakterli iki
    çekim arasında kesme ya da itme; `kontrol` artık uyarıyor.
  - Sayaçta basamak sayısı baştan sabit olmalı (9.999 -> "0.000" -> 10.000+ ve yana kayma kancanın 6. saniyesindeydi);
    bir anda gelen değer "yumruk" ile insin, etiketler sırayla değişsin (üst üste binmesin).
  - Tek karede açık -> kapalı olan kapı kancanın kilit vuruşunda zayıf: 2 ara çizimle 4-5 karede kapanış + 2-3 karelik
    sarsıntı. Aynı kapı Türkiye bölümünde geri dönünce (B5.4) tekrar eden sayılar yerine anlam taşır.
  - Kapanışta vurgu döngüsü son seçenekte biterse o seçenek cevap gibi okunur: üçü birlikte nabız + eşit vurgu.
  - LAEA'da merkezden ~70° uzaktaki ülke (Kuzey Atlantik görünümünde Türkiye) eğik bir şeride döner: iki kıtalı
    görünümde Equal Earth. Damga yer adının üstüne (HAMBURG Türkiye'nin üstündeydi): kare kare bakılmadan bulunmuyor.
  - TTS'te nadir kelime (cüzzam, kupür, multipl) Whisper'ın dil modeline yenilir: 3 çekim de 2 nat eşiğini geçemezse
    kelimeyi değiştir ("bu hastalığın", "gazete haberi"); doğru yazım ekranda kalsın. Yeni çekim eskisinden kötü
    olabilir ("yalnızca Grünenthal" çekiminde ad bozuldu): değiştirmeden önce ölç, kötüyse eskiyi koru.
  - Hareket çizgisi: anlatıcıyı hikâyenin dışında bir "gözlemci" gibi değil, sahneye tepki veren biri gibi kullan
    (kapanışta balona eğilir, her vurguda onaylar); havadaki nesneye düşen gölge onu masaya "koyar".
- **9. tur (dört hakem: izlenme 8, animasyon 7,5, dil 8,1, teknik 9):**
  - Küçük resimde yazı katmanları birbirine binmesin: "RUHSAT YOK" bloğu Türkiye'nin konturu ve başlık altında "PUHSAT"
    okunuyordu. Blok, konturdan SONRA ve şeklin dışında (altında) çizilir; her varyant 168x94'te ve süre rozetiyle bakılır.
  - Aynı zeminde iki çekim arasında kesme süreklilik hatası gibi okunur (takvim kayboluyor, kutu zıplıyor, tablet sayısı
    değişiyor): ya gerçek yakın plan (≥ 1,35x, başka kadraj) ya da tek çekim + kamera vurgu itmesi (`it` olayı).
  - Yüz varyantı telefonda (baş ~120 px) okunmalı: kaş açısının birkaç pikseli görünmüyor. Kararlı = kalın V kaş +
    kısık göz (üst kapak aşağı) + ağız uçları aşağı; şüpheci = tek göz kısık + tek kaş kalkık. Silme çokgeni yüz
    konturuna/saça taşmasın (yalnız renksiz çizgiyi sil: `sil_notr`).
  - Balonlu replikte konuşma sekmesi yetmiyor: aynı tuvalde açık ağızlı yüz, hecelerde açılıp kapanır (`balon {agiz}`).
  - TTS'te "h" ile başlayan kelime ("96 hastanın") zayıf okununca bambaşka bir kelimeye dönebiliyor ("aslanın", 9/9):
    anlam aynıysa kelimeyi değiştir ("96 kişinin"), ekrandaki damga terimi taşır.
  - Koyu sahneden kâğıda kesme telefonda flaş gibi (75 -> 212): kâğıt zemine `karart`, yazıdan yazıya ya da aynı
    karakterli geçişte `gecis: karart` (karanlıktan geçiş). Çapraz geçiş, bindirme kartının donmuş karesini aydınlık
    odanın üstünde "hayalet" gibi gösteriyordu.
  - Takılı yıl göstergesi geriye akmamalı (1961 -> "20??" altında 1948): zaman ileri giden hikâyede sayaç da ileri.
  - Ekranda olup söylenmeyen yazı ("(FDA)") uzunlukla orantılı SRT bölmesini 1,4 sn kaydırır: bölme sınırı sesin iç
    sessizliğine oturmalı.
- **10. tur (dört hakem: izlenme 8, animasyon 7,5, dil 8,3, teknik 9; motor 10. tur: yerleşim denetimi):**
  - İsim etiketi uzunluğu yüz büyüklüğüne bağlı: "farmakolog (1923–1984) · kaynak: meslektaş tanıklıkları" gibi iki
    bilgi tek etikete sığmaz, motor küçültür ya da çeneye biner. Kaynak notu aynı sahnede başka yerde söyleniyorsa
    etiketten çıkar; `kontrol`ün "küçültüldü" uyarısı = etiketi kısalt.
  - Bir üst katman başka bir fotoğrafa taşmasın: etiket bir fotoğrafı tanıtıyorsa o fotoğraf tam ekrandayken gelir ve
    çıkar, bölünmüş panel ondan SONRA açılır (Kennedy ödül töreni etiketi yasa imzası fotoğrafının üstündeydi).
  - Sayaçta her değer en az ~0,6 sn yerleşmiş okunmalı: anlatılan sayı ("1.267 doktor") hiç oturmuyorsa ilk sayımı
    kısalt (`basla {sure}`); ek bilgi (17 vakanın 10'u) sayının altına değil, boş üst alana küçük damgayla.
  - Yüz varyantları için telefon testi: ciddi = kalın V kaş + kaş arası kırışık + uçları aşağı ağız; düşünceli = bir kaş
    yüksek kemer, öbürü alçak düz + yana kaymış ağız. Şüpheci yüzde ağzın tek ucu kalkarsa kısık gözle birlikte "göz
    kırpan sırıtma" okunur: ağız düz. Kısık gözde kirpik üst kapakta kalmalı (alt yarıyı temiz yeniden çiz).
  - Hakemin "bakışı yanlış" notunu motorun aynalamasıyla birlikte doğrula: PNG'de sağa bakan göz bebekleri, karakter
    sağ tarafta aynalanınca içeri bakar (Lenz'in "fark" yüzü videoda doğruydu).
  - Yazılı kartpostal/fotoğrafın basılı yazısı kenarda yarım kalmasın: `kirp` ile çıkar ya da tamamen kadrajda tut.
  - Küçük resimde büyüteç tek bir şeyi büyütsün: üç satırlık etiket camın altında bulamaç oluyordu. Etikette tek temiz
    satır, büyütülecek ayrıntı ("19??") ayrı satırda; gölgeli sprite'ın kırpma payını hesapla (cam 40 px kayıyordu).
  - Eklenen her `<break>` ve "Sheskin," gibi açıklık kelimesi süre ekler (bu tur +3,3 sn): yeni çekimin duraklarını
    `ses_onarim.py durak` ile öteki satırların düzeyine indir, sonra olay anlarını Whisper kelime zamanlarına göre kaydır.
- **11. tur (dört hakem: izlenme 8,1, animasyon 7, dil 8,5, teknik 9):**
  - Kesmede aynı karakter ya aynı yer ve boyda kalır ya da değişim bilinçli ve geçişlidir: köşedeki anlatıcının 0,50 ->
    0,42 boy değiştirmesi, soldan sağa sıçraması ya da kamera itmesiyle büyüyüp sonraki sahnede küçülmesi "jump cut"
    okunur. Ekrandaki boyu kamerayla birlikte hesapla (yaml boyu değil); `kontrol`ün yeni zıplama denetimi bunu yapar.
    Çözümler: x/boy/kamera eşitle, `gecis: karart` (zaman atlaması) ya da `kaydir`; eşleşen kesmede sahnedeki
    nesneler (takvim, damga, köşe göstergesi) de devam etmeli, yoksa kaybolur.
  - Nesnenin yolu yüzden geçmesin: numune kutusu sağdan girip çıkarken ağlayan temsilcinin yüzünün içinden geçiyordu.
    Hikâyenin yönünden gelsin (dışarıdan kapıya: soldan) ve yüzün olduğu bölgeyi hiç kesmesin (`yon` + `x` sınırı).
  - Bölünmüş ekranda ortalı yazı (kelime) her konumda ayracı keser: panelin içine damga/etiket olarak koy.
  - Yüz düzenlemesinde silme kutusu eski çizginin uçlarını (kanca, uç kıvrımı) da kapsasın; kontrastı 6 kat artırılmış
    kırpımda leke ara (temsilcinin açık ağzının köşesinde kalan kanca hakem gözüyle bulundu).
  - Balon ağzı iki durumda (ince sırıtış <-> geniş hilal) telefonda yanıp sönen sırıtış gibi: ara yarık ağız + en az 4
    kare tutma (saniyede <= 7,5 değişim), kapalıdan açığa atlamadan.
  - Kapanış kartında yalnız çerçeve yanması yetmez: vurguda içerideki çizim de bir şey yapsın (yüz değişir, damga iner,
    zar döner); gerçek kişinin yüzüne/ağzına damga basılmaz (başın yanındaki boşluğa).
  - Fotoğrafın atıf satırı da engel: isim etiketi lisans satırını örtmesin (motor: `sabit_engeller`).
  - Dramatik sessizlik dijital sıfır olmasın (-70/-78 dBFS hoparlörde ses kesilmesi gibi): müzik incelmesi -15/-18 dB.
  - Rubberband ile yavaşlatmada başa 0,3 sn sessizlik ekle, sonra at: tempo 0,92'de "Ölümünün" Whisper'da
    "Bölümünün" duyuluyordu (başlangıç geçişi bozuluyordu).
  - Tempo oranını hedefe göre seç, hakemin önerdiği sayıyı körü körüne uygulama: 0,92, 8,2 hece/sn'lik satırı ~7,5'te
    bırakıyordu (hedef <= 7,0). En hızlı üç satır 0,85 (Whisper iki çözümde de tam doğru), ötekiler 0,9-0,92.
  - Damga mürekkebi yarı saydam: yazılı kartların üstüne basılan damga ("HİÇBİRİ YAYIMLANMADI") kartların yazısıyla
    birbirine karışıyordu. Büyük tez damgasını boş zemine (kartların hemen altındaki mantar) koy.
  - Anne adayı yine endişeli çizilmedi (hakem ikinci kez istedi): anlatım "gönül rahatlığıyla alıyor" diyor, mağdur anne
    çizilmez; duygu kamera itmesiyle verildi. Hakemin isteği olgu/saygı kuralıyla çakışırsa gerekçe raporda yazılır.
- **12. tur (dört hakem: izlenme 8, animasyon 7,5, dil 8,2, teknik 8,5):**
  - Yavaş sayan sayaçta sürekli yuvarlanma yırtık rakam üretir: adım ~2,75 karede gelince neredeyse her kare yarım
    dönmüş iki rakam ("52"nin 2'sinin üstünde 1'in kuyruğu), gri bulanıklık bandı ve pencerenin altında gelen rakamın
    tepesi görünüyordu. Yavaşta değer round(v) ile adım adım ilerler, yeni rakam 2 karede kayarak belirir, iz yok;
    sayaçları her zaman 30 fps şeritle kare kare kontrol et (motor: `SayacCizici._gosterilen`).
  - Hareket izi (motion blur) yalnız rakamların zaten okunmadığı hızda: kare başına ~1 adımda dikey iz, rakamın kendi
    boşluklarını gri, düz kenarlı bantlarla dolduruyordu ("35"in 5'inde çubuk). Teşhis için kontrastı 3 kat artırılmış
    1:1 kırpım ve iki karenin farkı yetti; küçük temas sayfasında görünmüyordu.
  - SRT blok kırmasında 42 karakter sınırı bazen iyi kırımı imkânsız kılar ("Kelsey her seferinde daha fazla veri
    istiyor." 46 karakter): satırı `metin`'de `\n` ile iki bloğa böl (`tts`/ses değişmez, önbellek anahtarı aynı).
  - Başlığın konusu olan vuruş (haritada "boşluk: Türkiye") 10 px'lik gri bir leke olmasın: kancadaki rengiyle, kamera
    o ülkeye itilerek ve ~1 sn tutularak verilir (motor: haritada `it`, hedef vurgu ülkesi).
  - Koyu/mavi-gri haritada sarı damga 360 px'te okunmuyor: beyaz + kontur.
  - İki noktalı zaman çizelgesi karenin yarısını boş bırakır: yazı 1,3 kat, eksen ortada, köşedeki konuk büyük ve
    eksen onun yanında biter (`olcek`, `y`, `x`); konuk eksenin üstüne binmesin (kare kontrolüyle yakalandı).
  - Siyah çubuklu "haber" çizimi yer tutucu gibi okunur; gerçek başlık uydurulamıyorsa vuruşu zaten var olan
    nesneye (pano kartı, ip, kaynak kartı) taşı; aynı tahtaya gidip gelen pano -> kupür -> pano da biter.
  - Kapanışta kartların kendi tepkileri sorudan hemen sonra gelsin (A, B, C ~0,85 sn arayla), abone/beğen/yorum
    ondan sonra: vedadan sonraki son 1,6 sn'yi izleyicilerin çoğu görmez, YouTube'un bitiş ekranı öğeleri de örter.
  - Kesmede karakter kaybolup ~0,2 sn sonra aynı yere yeniden giriyorsa köşe "göz kırpar": `giris: false` ile eşleşen
    yerde başlat, önceki sahnede çıkar ya da karanlıktan geç (`kontrol` artık bunu da bildirir).
  - Cartesia (Murat) ikiz zz'yi "cüzdan" okuyor: yeni metinle ("lepra, yani cüzzam") de, z 1,5-2,2 kat uzatılınca da
    Whisper 4/4 "cüzdan" yazdı. Okunamayan kelimeyi zorlamak yerine eş anlamlısını seslendir ("lepra"), ekranda ikisini
    birden yaz ("LEPRA (CÜZZAM)"). "Nejat" da 4 denemede "Necad" yazıldı: zorlanmış skorda en iyi çekim seçildi,
    kulak testi listesinde ve ElevenLabs notunda.
  - Satır kırma noktalama sonrasını dengeden önce seçmeli ("Peki ruhsat vermemek yeterli miydi? | Her zaman değil.");
    tamlama, sıfat + ad, ikileme ve satır başında "bile" bölünmez.
  - Denetim aracının kendi hatası da yanlış uyarı üretir: ayırıcı eksen denetimi ilk eksende dönünce eğik iki kart
    260 px uzakken "değiyor" görünüyordu. Uyarıyı düzeltmeden önce ölç.
- **13. tur (dört hakem: izlenme 8, animasyon 7,5, dil 8,2, teknik 8,5; engelleyici: 9:23'te kamera itmesi):**
  - Kamera itmesi (`it`) köşedeki karakteri kadrajdan çıkarabilir: makaleye itilince anlatıcının yüzünün yarısı sağ
    kenarla makalenin arasında kaldı, tepkisi ('fark') kayboldu. Hakem bunu "makale önde çiziliyor" diye okudu; asıl
    neden kadraj dışına kayan yüzdü. İtme hedefini karakterin tarafına al, `guc` küçük (<= 0,05) ve karakteri içeri
    çek. `kontrol` artık her sahnede kamera ve itme dahil yüzün kadraj dışındaki payını ve sonra çizilen görselin yüzü
    örtmesini ölçüyor (yeni denetim aynı turda dört sahnede daha buldu: 0:50, 4:01, 6:40, 8:14).
  - Yarı saydam sönen yazı da çakışır: kontrol çakışmayı opaklık >= 0,3 iken sayıyordu, 6 karelik "çift yazı"yı
    kaçırdı. Aynı yerdeki iki vurgu kelimesi arasında öncekinin sönmesinden sonra en az 0,3 sn olsun (denetim).
  - Sahnenin sabit kutuları (harita lejantı, foto atfı) da karakter engelidir: lejant anlatıcının omzuna biniyordu.
    Aynı anlamı daha kısa söyle ("satıldığı belgelenen bazı ülkeler"); `aciklama_en` iki satıra kırar ama alttaki
    kırmızı ülkenin (Brezilya) üstüne çıkıyordu.
  - Yeniden üretilen yüz varyantının bakış kaydı silinir (kayıt dosyanın sha1'iyle): motor yönü tahmin edip karakteri
    aynaladı, yüz kadrajdan taştı. Her yeni ya da değişen karakter görselinden sonra `python -m wojak yon <png> --yon
    sag|sol|on` (kontrol artık kayıtsız görseli bildirir).
  - Yüz varyantı taşınan gözlerin çizim dilinde kalsın: Kaymakçalan'ın 'düşünceli' gözleri camın içinde yeniden
    çizilmiş ince badem gözlerdi, öteki üç yüzün klasik Flannel gözlerinden ayrı okunuyordu. Klasik göz korunur, ifade
    kapakla (düz, aşağıda), kaşla ve ağızla verilir.
  - Konturlu damgada beyaz kenar dolgusu harflerin ALTINI da doldurunca mürekkep boşlukları beyaz görünür (kırmızı yazı
    pembe-beyaz benekli, mantar panoda soluk): harf izinin altına mürekkebin kendi rengi, kenar yalnız dışta halka.
  - Tek geçişli kutu bulanıklığı, itme geçişinde eğik çizgileri (yüz, saç) basamaklı hayalet kopyalara çevirir: aynı
    varyansta üç geçiş (~Gauss). Küçültülmüş karede çift genişlikli kutu her geçişte yarım piksel kaydırır: tek genişlik.
  - Hakemin önerdiği sayıyı kareye bakmadan uygulama: kontrol listesi şeritleri için önerilen boy 0,24 sağdaki anlatıcıya
    biniyordu (şeritler 6,5:1 enli), pano için yakin 1,4 kartları Kaymakçalan'ın başına bindiriyor ve alttaki kartı
    kesiyordu. Kompozisyonu değiştir (anlatıcı şeritlerin altında; yakin 1,22) ve kareyle doğrula.
  - Tırnak içindeki ekran yazısı söylenmemiş söz olmasın: Distaval reklamı için önerilen "‘ANNEYE DE ÇOCUĞA DA
    ZARARSIZ’" reklamda yok; reklamın kendi ifadesi kullanıldı: "‘OLUMSUZ ETKİSİ YOK’" ("ÇOCUĞA DA" ekli hali iki
    satıra kırılıp kartın üst kenarına biniyordu).
