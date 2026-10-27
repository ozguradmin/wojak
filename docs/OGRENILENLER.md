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
| 22.10 | Müzik adaylarının "hepsi benzer"; videoya göre müzik değişebilir mi? | Kanal müziği HEP AYNI: `music: kanal` = `imza_v2_golge.m4a` (altın dönemde 27/30 reel aynı sesi kullanıyordu, tanınırlık bundan). İstisna: havası çok farklı bir konuda aynı aileden varyant (`imza_v2_*.m4a`) ya da aynı melodi biraz yavaş / bir ton aşağı. Uzun videonun müziği kendi motorunda, sahneye göre değişir |
| 22.10 | YouTube'a yükleme private değil, doğrudan herkese açık | `tools/yt_yukle.py` varsayılan public; sonra Studio'da "Kontroller" bakılır, telif uyarısında video özele alınır (YAYIN_PLANI §0) |
| 22.10 | Yüklerken hikâye metni yorum olarak da atılsın | API ile yorum için anahtarda `youtube.force-ssl` izni gerekir (22.10: yeni anahtarda var, doğrulandı). Gelince her yüklemeden sonra hikâye metni yorum olarak atılır (50 birim). API yorum SABİTLEYEMEZ: sabitleme Studio'da elle |
| 21.10 | ElevenLabs cevabı gelmedi: **kısa videolarla başla**, uzun sonra. Yeni bölümler yeni sohbetlerde üretilecek | CLAUDE.md durum satırı güncellendi; yeni oturum özel dosyaları `tools/ozel_indir.py` ile Telegram'dan alır (ADIM_ADIM §1); kanalda yapılmış konu tekrar seçilmez |
| 21.10 | Kanalın sevilen müziğinin bize ait, ihlal yedirmeyecek benzeri; videoya göre değişebilsin | `tools/imza_muzik.py`: aynı his (Do minör vals, legato kamış, gramofon), özgün melodi; 3 varyant `assets/music/imza_vals*.m4a`. Melodik benzerlik ölçülür (`--karsilastir`), orijinalin motifleri yasak |
| 21.10 | Karun reel'inde **telifli Milliyet sayfa görüntüsü kullanılmayacak**; son kare telifsiz manşet kartı olsun (kendi sade kupür tasarımımız, gazetenin logosu/fontu/düzeni taklit edilmez, söz kaynakla birebir, altında "Kaynak: <gazete>, <tarih>") | Telifli sayfa yalnız B sürümü olarak saklanır. Kartta "X: ..." başlığını bir kişinin sözü gibi tırnağa alma: önce haber metnini oku (Karun: "Bakan Koç: Hırsız evin içindeymiş" gazetenin başlığıydı; bakan "Hırsız evin içinde mi?" sorusuna "Evet" demişti) |
| 21.10 | Düz manşet kartı (kâğıt + Anton + çizgi) son kareye **1/10**: "alıntı kartı gibi, hiç gerçekçi değil"; istenen telefonda gerçek gazete kupürü sanılacak kalite | Son kare kupürü **gerçekçi üret** (`kupur.py` ölçüsü, §"Kanıtlanmış yol" K adımı): sararmış dokulu kâğıt, yırtık/makas kenar + gölge, gerçek manşet tipografisi (SIL OFL grotesk/serif), raster fotoğraf, okunmaz komşu sütunlar; Commons gerçek kupürleriyle kıyasla. Düz kart yetmez |
| 16.10 | "Görsel üretimi gerek yok, şu anki hâlini beğendim; gerçek görseller daha iyi" | Yapay zekâ ile görsel (arka plan, karakter, kanıt) üretilmez. Arka plan ve kanıt gerçek fotoğraf/belge ya da kendi düz çizimimiz; karakter hazır wojak. `tools/gorsel_uret.py` ve SOL ağ geçidi üretimde kullanılmaz |
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

### 6.1 Bulut oturumu dersleri (21.10.2026, `karun-hazinesi-bros`, iki hakemden 8/8, 2 tur)

- **Kanıt kareye sığdırılır:** renderer 1080'den uzun kanıtı kesmez, kareye sığdırır. 1260 px'lik görsel 925 px
  genişliğe iner, iki yanında siyah bant kalır (STIL §8 "tam genişlik" bozulur). Kanıtı en çok 1080x1080 hazırla.
  Uzun bir nesne fotoğrafını kare yapmak için iki yanı aynı fotoğrafın nesnesiz kenarından düz şeritlerle doldur
  (8 px yumuşak geçiş). Ayna döşeme kumaşta kaleydoskop deseni yapıyor, kullanma. Gazete kupürünü kare kırp; iki
  yandaki sayfa beyazı kalabilir.
- **Basılı birinci sayfa en iyi son kare:** Milliyet Gazete Arşivi (`gazetearsivi.milliyet.com.tr/Arsiv/YYYY/AA/GG`)
  üyeliksiz tam sayfa görüntü veriyor (sayfadaki `_next/image?url=` içindeki API adresi ~1900x2700). 2000'lerin
  olaylarında altın dönem dilindeki kalın manşeti buradan bul (telifli, `img/telifli/`).
- **Bakış (25.10.2026'dan itibaren):** `faces:` kullanma. Her karakter PNG'sini `python -m wojak yon <png> --yon
  sag|sol|on` ile kaydet: PNG DOSYASININ KENDİ baktığı yön (burun ve göz bebekleri dosyada hangi yana). Karakterin
  bakması gereken yönü yazma; aynalamayı motor yapar. Eski kural (`faces:` yeter) yüzünden ajanlar solda `sag`,
  sağda `sol` yazdı, kayıt ezildi ve Ayasofya ile Lady Be Good'da sağdaki karakter dışarı baktı.
- **Ağ (bu sandbox):** Commons API ve küçük resim (`thumburl`) adresleri sık 429 veriyor; `upload.wikimedia.org`
  üzerindeki özgün dosya adresi (md5 yolu) ise sorunsuz iniyor (istekler arası ≥ 12 sn). Openverse
  (`tools/bg_ara.py`) yanıt vermedi. Playwright'ta `ignore_https_errors=True` gerekiyor (vekilin sertifikası).
- **Taze oturumda 1 test düşer:** `test_short_youtube_aciklamasi_en_cok_uc_hashtag`, git'e girmeyen
  `episodes/talidomit-turkiye/img/telifli/kanit_2_sdd_mobil.png`'yi arıyor. Kod hatası değil, ortam eksiği.
- **Gerçek, hükmü kesinleşmiş ve sonradan ölmüş kişi:** adını videoda ve metinde verme. Kötü yüz kullanma (sakin ve
  kendinden emin). İroniyi onun belgeli sözlerine dayanan repliklerle kur ("Eserleri ABD'den teslim alan benim" →
  "O broşu Amerika'dan ben getirdim"). Metne giren alıntıyı birebir yaz; takipçi hakemi kısaltılmış alıntıyı MUST
  saydı.
- **Telifsiz manşet kartı yetmedi** (`gorsel.py:kanit_2_kart`, artık yok): 1080x760 düz kâğıt + Anton + çizgi; iki
  hakemden 8/8 aldı ama hesap sahibi **1/10** verdi ("alıntı kartı gibi"). Düz kartı son kareye koyma.
- **Gerçekçi gazete kupürü** (`episodes/karun-hazinesi-bros/kupur.py`, ~2 sn üretir, iki hakem 8/8 + "gerçek sanılır"
  8+): sararmış dokulu kâğıt (gren + lif + leke + katlanma izi), üstte yırtık + üç yanda makas kenarı, koyu yüzeyde
  gölge, kupürde kıvrılma ışığı, −1,4° eğik; manşet Libre Franklin 900, spot Source Serif 4 (ikisi SIL OFL); raster
  fotoğraf (45°, sarı-mavi farkından gri ton, yoksa altın ve fon aynı griye düşüyor); komşu sütunlar ve gövde
  **rastgele harften çizilip bulanıklaştırıldı** (okunabilir uydurma metin yok). Gazetenin logosu/adı/düzeni yok;
  yayın adı yalnız alt "Kaynak: <gazete>, <tarih>" satırında. Ölçüt: Commons gerçek kupürleri (ör. "Alas de libertad"
  El Comercio 1996, CC BY 4.0). Font: `raw.githubusercontent.com/google/fonts/main/ofl/<ad>/<Dosya>.ttf` + OFL.txt.

---

## 6.2 Kanıtlanmış yol: kısa reel (baştan sona)

> Bu bölüm bu oturumda (`karun-hazinesi-bros`, 21.10.2026) gerçekten denenip çalışan yolu belgeler; tahmin değil.
> Amaç: bir sonraki kısa reel aynı ya da daha iyi kalitede, **daha kısa sürede ve daha az token/maliyetle**. Ölçü
> kaynağı yine [`STIL.md`](STIL.md); bu bölüm sırayı, komutları ve tuzakları verir.

### Hızlı başlangıç (önce yalnız bunu oku)

1. **Oku:** bu §6.2 + `STIL.md` §0 ve §14 + `OGRENILENLER.md` §0, §3, §4 (üst tablo). Gerisi gerektikçe. Koca
   `INSTAGRAM_ANALIZ.md`/`ANALIZ.md`'yi baştan sona okuma; `KONSEPT.md` §5 (hikâye) ve `KONU_HAVUZU.md` yeter.
2. **Ortam:** `ln -sfn /workspace/wojak /home/user/wojak`; `pip install -q -r requirements.txt pytest faster-whisper
   py7zr multivolumefile`; font + referans (`referans.7z` çıkar). `test_short_youtube_...hashtag` taze oturumda
   düşer (talidomit telifli görseli yok) — normal, kod hatası değil.
3. **Konu:** `KONU_HAVUZU.md` + `data/videos.csv`/`instagram_reels.csv`/`olay_metinleri.md`/`episodes/` içinde
   geçmediğini doğrula (grep). "Ne?!" + 2 kaynak + Türkiye + serbest lisanslı kanıt + ironi/ters köşe.
4. **Olgu:** `web_search` ile doğrula, her ekran iddiası ≥2 bağımsız kaynak; alıntıları **birebir** al.
5. **Arka plan + kanıt 1:** Commons'ta **serbest lisanslı** ara. İndirme: API/thumburl **429 veriyor**; özgün dosya
   adresi (`upload.wikimedia.org/.../<md5>`) sorunsuz. `tools/orute` yerine md5 yolu (aşağıda K-komutları).
6. **Karakterler:** `uzun/talidomit-turkiye/chars/*_v2_*` hazır; yoksa `wojak_lib.py`/`wojak_site.py` get. Yüz
   varyantını `episodes/<id>/chars/uret.py` ile çiz (talidomit `hazir_uret.py`'yi kopyala). Her PNG'ye bak.
7. **Bakış:** her karakter PNG'sini aç ve DOSYANIN baktığı yönü kaydet: `python -m wojak yon <png> --yon sag|sol|on`
   (`faces:` yazma). Render sonrası `python -m wojak bakis episodes/<id>` -> `out/<id>/kareler/bakis.jpg`: solda
   duranın yüzü ve göz bebekleri sağa, sağdakinin sola bakmalı. Değilse kaydı düzelt ve yeniden render et;
   görsel hakem de bu sayfayı görür. `teslim` kayıtsız ya da çelişkili bakışta durur.
8. **episode.yaml:** `python -m wojak new <id>`, talidomit ve bu bölümü şablon al. `music: {file:
   imza_v2_ic_cekis.m4a}`. Süreler 0,5 katı, toplam 14,0.
   *(23.10 düzeltme: müzik artık `music: kanal` = imza_v2_golge; bu ortamda ffmpeg/loudnorm hatası yüzünden
   `music: {file: kanal, volume: 0.197}` yaz ve LUFS'u ölç. Bkz. "Ek dersler (23.10.2026, kanuni-gizlenen-olum)")*
9. **Kanıt kareye sığar:** renderer 1080'den uzun kanıtı kesmez, kareye sığdırır → yanlarda bant. Kanıtı **1080x1080**
   (ya da ≤1080 yüksek) hazırla; uzun nesneyi nesnesiz kenar şeridiyle kareye tamamla.
10. **Son kare = gerçekçi kupür** (`kupur.py`), düz kart değil. Serbest görsel yoksa üret.
    *(23.10 düzeltme: kupür varsayılan değil; son kare kanıtın kendi biçimine uyar, son 5 bölümle aynı tür arka
    arkaya gelmez. Tarihî olayda dönemin kamu malı minyatürü/belgesi iyi bir son kare: `kanuni-gizlenen-olum`)*
11. **Döngü:** `check` (uyarısız; imza müzik uyarısı bilinçli) → `frames` → kareye bak → `render` → `teslim`.
12. **Hakem:** 2 bağımsız mercek, yan yana + ölçüm. Metinde alıntı birebir, canlandırmayı açıkça yaz. İlk seferde
    8/8 hedefle (aşağıda "kalite çıtası").
13. **Teslim:** `/mnt/session/outputs/<id>/` (video, kapak, paylasim.md, metinler, RAPOR.md). Gerçek kişi adını
    hiçbir dosyaya yazma. Hidden Words yalnız sohbette.
14. **Commit:** herkese açık `wojak`'a mp4/`img/telifli/` **girmez** (`git status` + `git diff --cached --name-only |
    grep -E '\.mp4$|telifli'`). Özel teslim `wojak-ozel`'e (video dahil).
15. **Ortam tuzakları:** Commons 429 (≥12 sn, md5 yolu); Openverse (`bg_ara.py`) yanıt vermiyor; Playwright
    `ignore_https_errors=True` + `python -m playwright install chromium` (tek sefer); gazete arşivi için Playwright.
16. *(26.10 ek)* **İş başında iki deponun dalını kontrol et:** ayrık HEAD'de açılıyorlar (`git status | head -1`); dosya yazmadan
    önce varsayılan dala geç. **Son kare türleri şimdiye kadar:** levha, kupür, müze nesnesi, pul, arşiv fotoğrafı, kitap sayfası
    (Internet Archive, `yerebatan-bodrum-balik`). Son 5 bölüme bak, aynısını arka arkaya kullanma.
17. *(27.10 ek)* **Son kare türlerine eklendi: kamu malı tablo** (Zonaro 1903, `orban-topu-bizans`). Varsayılan dal:
    `git ls-remote --symref origin HEAD`. Ayrıntı: "Ek dersler (27.10.2026 sabah, `orban-topu-bizans`)".

### Adım adım (çalışan yol / vakit kaybı / süre / tasarruf)

**A. Hazırlık ve okuma** — Çalışan: hızlı başlangıç 1-2. Vakit kaybı: bütün `docs/`'u okumak; `STIL.md` Ek'teki 34
maddeyi tekrar okumak (varsayılanlar zaten koda girmiş). Süre: oturumda ~4 dk, kanıtlanmış yolla ~2 dk. Tasarruf:
`INSTAGRAM_ANALIZ.md` ve `ANALIZ.md` büyük ve bu üretim için gereksizdi — okuma.

**B. Konu tarama** — Çalışan: `cut -d, -f10- data/videos.csv`, `olay_metinleri.md` başlıkları, `episodes/` listesi,
`KONU_HAVUZU.md`; adaylara `grep -ril`. Süre: ~3 dk → ~2 dk. Tasarruf: 3 aday bul, en güçlüyle başla; zayıfları
araştırma.

**C. Olgu araştırması** — Çalışan: `web_search` (5-6 arama yetti), resmî/ana akım + Vikipedi + akademik; çelişen
sayıyı yuvarla. Süre: ~6 dk → ~5 dk. Tasarruf: her aramanın tüm sonucunu okuma; 2 kaynak doğrulayınca dur.

**D. Görsel avı (Commons)** — Çalışan:
```
# arama (API; istekler arası >= 12 sn)
action=query&list=search&srsearch=<q>&srnamespace=6   (dosya)  / srnamespace=14 (kategori)
action=query&generator=categorymembers&gcmtitle=Category:<ad>&gcmlimit=200&prop=imageinfo&iiprop=url|size|extmetadata
# indirme: thumburl/thumb 429 veriyor -> ÖZGÜN dosya md5 yolu sorunsuz:
n=${ad// /_}; h=md5(n); https://upload.wikimedia.org/wikipedia/commons/${h:0:1}/${h:0:2}/<urlencode(n)>
```
Vakit kaybı: `iiurlwidth` ile thumburl indirmek (429, tekrar tekrar); Openverse (`tools/bg_ara.py`) — bu ortamdan
timeout. Süre: oturumda ~17 dk (çoğu 429 beklemesi) → kanıtlanmış yolla ~8 dk (baştan md5 yolu). Tasarruf: temas
sayfalarını 400 px küçük thumbnail'le incele (tam çözünürlük gereksiz); yalnız seçilen 2-3 dosyayı tam indir.

**E. Haber/gazete arşivi (gerekirse)** — Çalışan: Playwright (`ignore_https_errors=True`, mobil ya da masaüstü UA).
Milliyet Gazete Arşivi: `gazetearsivi.milliyet.com.tr/Arsiv/YYYY/AA/GG`; sayfadaki `_next/image?url=` içindeki API
adresi (`gazetearsivi-api...NewspaperImage/Image/<id>`) ~1900x2700 tam sayfa verir (üyeliksiz). Not: **telifli**.
Vakit kaybı: TLS hatası (`ERR_CERT_AUTHORITY_INVALID`) — `ignore_https_errors=True` şart. Süre: ~6 dk.

**F. Karakter ve yüz** — Çalışan: hazır v2 yüzler; yeni karakter için kaynağı `wojak_lib.py get <id>` /
`wojak_site.py get wl:<dosya>`; yüz içini silip (poligon maske) aynı çizgi kalınlığında yeni kaş/göz/ağız +
`kit_varyant.py` ter/gözyaşı. Grid görsel (NEAREST, koordinat ızgarası) ile hat yerlerini ölç. Vakit kaybı: düşük
çözünürlüklü kaynak (müdür 504 px) — telefonda sorun değil ama 1:1'de yumuşak. Süre: ~10 dk → ~6 dk (talidomit
`hazir_uret.py` kalıbını kopyalayınca). Tasarruf: yüz hattı koordinatlarını tek bir ızgara görselinden oku, deneme
yanılmayı azalt.

**G. episode.yaml + check** — Çalışan: talidomit + bu bölüm şablon; `check` tek "imza müzik" uyarısı bilinçli. Süre:
~3 dk. Tasarruf: replikleri baştan 0,5 ızgara ve 1-11 kelimeye göre yaz (okuma uyarısı dönüşü yok).

**H. frames + render** — Çalışan: `frames` → şerit + kare kare bak; `render` ~8 sn. Süre: ~2 dk. Tasarruf: `frames`
tek seferde yeter; her küçük düzeltmede render 8 sn, ucuz.

**I. Kanıt yerleşimi** — Çalışan: 1080x1080 ya da 1080x≤1080. Uzun nesne: nesnesiz kenar şeridini kopyalayıp kareye
tamamla (ayna değil; ayna kaleydoskop yapıyor). Vakit kaybı: 1260 px kanıt → renderer kareye sığdırınca yan bant.
Süre: ~3 dk.

**J. Hakem turları** — Çalışan: 0,5 sn kare + C2kk/C4V3/C12O/C2Fr yan yana; ebur128; telefon boyu (390 px); kesme =
kare farkı. Süre: tur ~2-3 dk. Tasarruf: ölçüm betiklerini scratchpad'de tut, yeniden yazma; kareleri 360-390 px
çıkar (tam çözünürlük gereksiz).

**K. Manşet kupürü** — Çalışan: `kupur.py` (yukarıda ders). Süre: betik ilk kez ~5-7 dk, sonra kopyala ~2 dk.
Tasarruf: fontları bir kez indir, sakla.

**L. §4 + teslim + outputs + commit** — Çalışan: §4 listesi; `teslim`; `/mnt/session/outputs/<id>/`'e kopya; iki
depo. Süre: ~8 dk. Tasarruf: RAPOR'u üretirken yaz, sonradan değil.

### Kalite çıtası (hakemlerin neye takıldığı → ilk seferde geç)

- **Alıntı birebir olsun.** Takipçi hakemi kısaltılmış/parafraz alıntıyı MUST saydı. Metne gireni kaynaktan kopyala.
- **Canlandırmayı açıkça yaz** (`ek_maddeler` + "Görseller" satırı). Tek kaynaklı iddiayı "anlatılana göre" yap.
- **Son kare gerçekçi** olacak (kupür); düz kart hesap sahibinden 1/10.
- **Kanıt tam genişlik** (kareye sığdırma bandı yok).
- **Gerçek kişi:** ad hiçbir dosyada yok; kötü/sırıtan yüz yok; ironi belgeli sözlerden.
- **Tarih kaynakla uyumlu** ("Mart 2006'da", "2005 sonunda ihbar"); uydurma kesinlik yok.

### Süre ve maliyet

- Bu oturum (ilk teslim + kart turu + kupür turu, hepsi düzeltmelerle): ~2 saat, ücretli API 0.
- **Kanıtlanmış yolla bir sonraki kısa reel:** tahminen **55-75 dk**. En büyük tasarruf: Commons'ta baştan md5 yolu
  (429 beklemesi yok), gereksiz belge okumama, düşük çözünürlüklü inceleme, hazır kupür/karakter kalıpları.

### Kod değişikliği önerileri (uygulanmadı; hesap sahibi değerlendirir)

- `tools/`: **Commons indirici** (md5 özgün yol + ≥12 sn hız sınırı + yeniden deneme). Bu oturumda elle `orig.sh`
  yazıldı; araç olsa her bölümde kazandırır.
- `wojak/compose.py`: kanıt `contain_fit` yerine **genişliğe göre sığdırma** seçeneği (`evidence_fill: width`), uzun
  nesnelerde yan bant olmasın; şimdilik görseli elle 1:1 kareye tamamlıyoruz.
- `tools/`: **gazete kupürü üreticisi** (bu bölümün `kupur.py`'si genelleştirilmiş: metin, kaynak, foto, satır
  sayısı parametreli). Son kare her olayda gerekiyor.
- `tools/bg_ara.py`: Openverse bu ortamda timeout; Commons'a (CC/PD süzgeçli) düşen bir yedek eklenebilir.
- `wojak/facing.py`/`check`: `faces:` alanı yaml'da varken bakış uyarısı zaten susuyor; `yon` kaydının eski sha1
  girdilerini temizleyen bir komut iyi olur (bilinen açık not).

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

### EN kanalı (Wojak Past Files, 25.10.2026'dan itibaren)

İngilizce ikinci kanal. Konsept, stil, müzik ve kalite çıtası yukarıdakiyle aynı; yukarıdaki kanıtlanmış yol burada da
geçerli. Bu alt başlığa yalnız İngilizce kanala özgü dersler eklenir (yalnız ekleme, tarihli).
- Profil: `episode.yaml`'da `kanal: en` (filigran `wojakpastfiles`, `Images:` atfı, İngilizce hashtag, İngilizce sansür
  ve denetim). Yeni bölüm: `python -m wojak new en-<id> --kanal en`. Bölüm id'leri `en-` ile başlar.
- Teslim: `wojak-en-ozel/teslim/<id>/` (tek commit; push anında yayın). `wojak-ozel`'e en bölümü konmaz.
- Ekip: yapımcı ve araştırmacı Claude Haiku 5.5; iki bağımsız hakem Claude Sonnet 5.5 (ayrı bağlam).
- Ara kart İngilizcede "... later" ile biter ("A few hours later"); `check` bunu denetler.
- Atıf satırı: açıklamaya "Images: ..." ve kupür/kart varsa "The final frame is a recreation; the quote is from
  <publication>, <date>." yazılır.

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
