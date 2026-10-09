# Tarihsel Wojak "olay" reel'leri: ölçülmüş stil rehberi

> **Bu belge üretimin ölçü kaynağıdır.** 30 orijinal reel (5,9M–28,1M izlenme) kare kare ölçülerek yazıldı;
> render varsayılanları (`wojak/config.py`) ve `python -m wojak check` stil denetimi buna göre ayarlıdır.
> Konu seçimi ve zamanlama için: [`GUNDEM.md`](GUNDEM.md), [`KONSEPT.md`](KONSEPT.md). Referans videolar
> `referans/` altında (repoya girmez; `tools/ig_fetch.py`/Playwright ile indirilir).


**Kaynak:** @tarihselwojak hesabının en çok izlenen 30 orijinal reel'i (5,9M ile 28,1M izlenme arası).
- 26'sı kısa ve klasik formatta.
- 4'ü aykırı: C5ob ve C5eF lisanslı müzikli, C5Yy film reklamı, DHG 2025 yapımı.

**Ölçek:** Bütün piksel değerleri 1080x1920 ölçeğinde. Orijinaller 720 genişlikte; değerleri 1,5 ile çarpıldı.

**Kare oranı (%):** 1080x1080 görsel karesine göre verilir. Kare tuvalde y=420–1500 aralığında durur.

**Yöntem:**
- ffmpeg ile saniyede 10 kare çıkarıldı. Kesmeler kare farkıyla bulundu; her sahneden bir temiz kare alındı.
- Ölçümler PIL ve numpy ile yapıldı. Üç analistin sahne tabloları bu ölçümlerle karşılaştırıldı.
- Ses için 22 050 Hz mono çıkarıldı. Dalga formu ve kroma çapraz korelasyonu, EBU R128 ve artık (residual) analizi kullanıldı.

---

## 0. Altın kurallar (tek bakışta)

1. Siyah 9:16 tuval. Ortada 1080x1080 kare (y=420–1500). Siyah bantlar boş kalır.
2. Bölüm 13,5–14,0 sn sürer. Sıra: diyalog (3–5 sahne) → isteğe bağlı tek bir ara kart → kanıt (2–3 görsel) en sonda. Kanıttan sonra diyalog hiç gelmez (0/30).
3. Her sahne tamamen durağandır ve sert kesmeyle değişir. Yakınlaşma, kaydırma, sarsıntı, flaş, pop-in, geçiş efekti yoktur (30/30).
4. Her diyalog sahnesinde tek karakter vardır: o an konuşan.
   - Karakter alt kenardan kesilir ve büst olarak görünür.
   - Görünen yüksekliğin medyanı karenin %48'i.
   - İki konuşmacı vardır. Biri hep solda, diğeri hep sağdadır; konuşmacı değişince taraf değişir.
5. Her satır ekrandaki karakterin kendi ağzından, şimdiki zamanda söylenmiş bir repliktir. Anlatıcı, tarih ya da etiket yazısı yoktur. Nokta ve üç nokta kullanılmaz.
6. Yazı Avenir Bold Italic (yaklaşık 6° eğik), beyaz ve siyah konturludur. Boyut 55 px (x-yüksekliği 27 px). En fazla 2 satır olur. Blok yatayda ortalanır ve konuşanın başının yaklaşık 55 px üstünde durur.
7. Diyalog boyunca tek bir arka plan fotoğrafı kullanılır. En fazla 2 olur; ikincisi kart ya da zaman atlamasından sonra gelir. Renkler doğaldır: karartma ve gri ton yoktur. Fotoğraf hafif yumuşaktır.
8. Ters köşe (twist), aynı karakterin aynı kutuda yüz değiştirmesi ve son replikle verilir. Bu son replik çoğunlukla "Bekle, … neden …?" tipi bir fark etme sorusudur.
9. Kanıt görselleri tam genişlikte (1080) ve siyah zemin üzerinde letterbox olarak gösterilir, kare merkezine (y=960) ortalanır. Her biri yaklaşık 1,5 sn kalır. Etiket, bant ya da altyazı eklenmez.
10. Ses tek bir parçadır ve hiç efekt yoktur.
    - Hesabın imza "orijinal ses"i: Do minör, 3/4, yaklaşık 152–155 BPM.
    - Bant geçiren lo-fi melodi, 13,75 sn uzunlukta.
    - Ses düzeyi −29,5 LUFS, tepe −17 dBTP.
11. `tarihselwojak` filigranı her karede bulunur (kart ve kanıt dahil). Sağ altta, kare tabanına yaklaşık 5 px mesafede durur.

---

## 1. Tuval ve yerleşim

| Öğe | Değer (1080 ölçeği) | Kaynak |
|---|---|---|
| Tuval | 1080x1920, saf siyah | 30/30 |
| Görsel karesi | 1080x1080, x=0–1080, y=420–1500 | 29/30 |
| Eski şablon | C1SV (Aralık 2023): 1080x1116, y=402–1518. İçerik yaklaşık 1,35x büyük, filigran resmin içine gömülü | 1/30 |
| Siyah bantlar | Boş | 28/30 |
| Bant istisnası | Yalnız uzun reel'lerde taşan kanıt ve kanıt başlığı (C5eF, DHG) | 2/30 |
| Kare hızı | 30 fps. Kesmeler 33 ms'lik karelere oturur | — |
| İlk kare | 1. sahnenin tam kendisi. Fade-in ya da boş kare yok | 30/30 |

---

## 2. Yapı ve süreler

Aşağıdaki değerler kısa formattaki 26 reel'den alındı: C5eF, DHG, C5ob ve C5Yy hariç.

| Parametre | Ölçüm (min / p25 / medyan / p75 / maks) | Hedef |
|---|---|---|
| Toplam süre | 10,97 / 13,13 / 13,87 / 13,99 / 14,07 sn | 13,5–14,0 sn. Müzik 13,75 sn'de bittiği için en fazla 14,0 sn |
| Sahne sayısı (kart ve kanıt dahil) | 6 / 6 / 6 / 7 / 8 | 6–7 |
| Diyalog sahnesi sayısı | 3 / 3 / 4 / 4 / 6 | 4 |
| Diyalog sahnesi süresi (n=103) | 1,20 / 2,14 / 2,50 / 2,52 / 3,04 sn | 2,5 sn. Uzun replikte 3,0, tek kelimede 2,0 |
| İlk sahne | 2,40 / 2,50 / 2,53 / 3,00 / 3,03 sn | 2,5–3,0 sn |
| Kesmelerin 0,5 sn ızgarasına oturma oranı (±1 kare) | 113/140 kesme (%81) | Süreleri 0,5 sn'nin katı yap |
| Kanıt görseli süresi (n=54) | 0,97 / 1,46 / 1,50 / 1,53 / 2,47 sn | 1,5 sn. Son görsel 1,5–2,0 sn |
| Kanıt görseli sayısı | 0 / 2 / 2 / 3 / 4 | 2–3 |
| Kanıt bloğunun toplam süresi | 1,23 / 2,65 / 3,51 / 4,87 / 6,47 sn | 3,0–4,5 sn |
| Kanıtın başladığı an | 6,37 / 8,01 / 10,0 / 11,2 / 12,77 sn | yaklaşık 10 sn |
| Ara kart (9/26 reel) | süre 1,46 / 1,50 / 1,53 / 1,54 / 2,00 sn; başlangıç 3,0 / 5,0 / 5,5 / 7,4 / 9,3 sn | 1,5 sn, 5,0–7,5 sn arasında |

**Kalıp dağılımı (26 kısa reel):**
- Diyalog → kanıt: 16 reel.
- Diyalog → kart → diyalog → kanıt: 6 reel.
- Diyalog → kart → diyalog, kanıtsız; ters köşe replikle biter: 3 reel. Bu gruba 27,5M ile 1 numaralı C4V3 de girer.
- Yalnız diyalog: 1 reel.

**Değişmez kurallar:**
- Kanıt hep en sondadır ve diyalogla karışmaz (0/30).
- Kart hep iki diyalog sahnesi arasındadır. Kanıta bitişik değildir (10/10).
- Reel kanıtla biter (kanıtlı 25 reel'in 25'i).

---

## 3. Anlatı kalıbı (senarist için)

**Kim konuşur?**
- Replikler %100 ekrandaki karakterin ağzından, o anda söylenen konuşmadır (121/121).
- Anlatıcı satırı 0. Üçüncü şahıs altyazı 0. Ekranda tarih, yer ya da isim etiketi 0.

**Konuşma düzeni:**
- Aynı mekânda, gerçek zamanlı, iki kişilik bir diyalogdur: soru → cevap → karar ya da tırmanış → fark etme.
- 26/30 reel'de iki konuşmacı vardır. C2kk tek kişilik monologdur. Üç konuşmacı istisnadır (C3De, C3S6, C5Yy).

**Bakış açısı karakteri:**
- Olayı yaşayan kişidir (kurban ya da tanık). Genelde 4 replikten 2–3'ünü söyler.
- Son repliği o söyler veya ona söylenir.

**1. replik (kanca):**
- Yaklaşık yarısında soru: "Annemin otopsi sonuçları çıktı mı?", "Burada ne yapıyorsun?", "Gelen sesi duydun mu?".
- Ya da masum veya ironik bir niyet cümlesi: "Gece yarısı oldu hadi ayin yapalım", "Birkaç tane koyunum şu mağaraya girdi…".
- Hikâye hep olay anından başlar. Geçmiş anlatılmaz.

**Son diyalog repliği (ters köşe):**
- Kanıttan hemen önce gelir.
- Çoğu bir fark etme sorusudur: "Bekle, ev neden sallanıyor?" (iki reel'de aynen), "Bekle, deprem mi oluyor?", "Bekle, bunun tadı neden böyle?", "Neden vücudum yanıyor?!", "Neden ormanda durduk?", "Bu şeyler de ne?".
- Ya da dramatik ironi taşıyan bir ifadedir: "Midende", "Siz gelince gitti", "Uçakla Isparta'ya gitmem gerekiyor", "Olamaz deprem oluyor".
- Kanıttan sonra açıklama repliği gelmez. Kanıt sessizce doğrular.

**Uzunluk:**
- Replik başına 1–11 kelime (medyan 5), en fazla 76 karakter.
- Satır başına en fazla 40 karakter (medyan 24).
- Reel toplamı 15–34 kelime (medyan 22).

**Noktalama ve dil:**
- Nokta 0/121, üç nokta 0/121 (bir reel'de bir kez "..").
- Ünlem 3/121.
- Soru işareti yaklaşık %35; virgül yaklaşık %35.
- Cümle düzeni (sentence case) kullanılır. Ağız dili serbesttir: "gidicez", "nerde", "Malesef".

**Ters köşenin görsel anlatımı:**
- 16/30 reel'de aynı karakterin yüzü aynı piksel kutusunda değişir. Tipik dizi: sakin → ter damlası → alnında mavi soğuk ter çizgileri → gözyaşı ya da korku yüzü.
- 14/30 reel'de en az bir kez yalnız yazı veya yalnız yüz değişir; arka plan ve poz aynı kalır.

**Sansür:**
- Hassas kelimeler (öl-, cinayet, kesik) repliğin içinde kırmızı çizgiyle bozulur. Renk yaklaşık RGB 250,22,60; çizgi 7–10 px ya da fırça darbesi. 2/30 reel'de görüldü.
- Kanıtın içinde de olabilir (7/30): yıldız, kırmızı çizgi, siyah bant, pikselleştirme.

---

## 4. Karakterler

**Çizim ailesi:**
- Erkekler: klasik MS-Paint wojak (beyaz dolgu, siyah elle çizgi), meslek ya da dönem aksesuarlı (bere, kask, türban, üniforma).
- Kadınlar ve çocuklar: düz renkli wojak-kız ya da animemsi, yanak allıklı.
- Katil veya ifşa karakteri: sırıtan (creepy-grin) wojak.
- Korku tasarımı yalnız ters köşede: erimiş yüz, maske.
- Temiz kesim kullanılır: sticker kenarı, gölge ve parıltı yok.

**Sahnedeki sayı:** Her diyalog sahnesinde 1 karakter, yani konuşan (117/119). İkili ya da üçlü kadro yalnız 2 istisnada var.

**Taraf:**
- Her karakter reel boyunca tek tarafta kalır (30/30).
- Konuşmacı değişince taraf da değişir.
- Toplam dağılım: sol 67, sağ 53. Ortada tek başına karakter yok.

**Boyut (görünen yükseklik, kareye oranla):**
- Aralık %32–75. Medyan %48 (520 px). Çeyrekler arası (IQR) %44–53 (475–570 px).
- Genişlik %29–56.

**Kadraj:**
- Büst: baş ve omuzlar, en fazla göğüs. Her zaman alt kenardan kesilir (100%).
- Dış kenara yapışık durur (0–30 px). Sık sık yan kenardan da kesilir.
- Karakter merkezinin x'i: solda %22–28, sağda %72–83.

**Baş üstü:** Karenin %44–68'inde, medyan yaklaşık %53 (çerçeve y ≈ 990).

**Bakış:** Kadrajın ortasına ve diğer konuşmacıya doğru, 3/4 açıyla. Ya da göz ucuyla merkeze bakar.

**Yüz varyantı:** Kutu, poz ve taraf aynı kalır; yalnız yüz bölgesi değişir (C4qd'de yüz alanı karenin x %16–36, y %68–86 aralığında).

---

## 5. Replik yazısı

| Parametre | Ölçüm | Hedef değer |
|---|---|---|
| Font | Avenir LT Std Bold Italic (TR). Ölçülen gövde eğimi 6,3° (aralık 5,3–7,4°); "a" iki katlı. Font çizilip üst üste konunca birebir örtüşüyor | `AvenirLTStd-BoldItalic-TR.otf`, ek eğim (shear) 0 |
| x-yüksekliği (beyaz dolgu) | medyan 26 px (IQR 25–30; p5 23, p95 37). C5eF 33–39 px ile aykırı | 27 px, yani 55 px punto (Avenir xh/em = 0,49). İzinli aralık 50–60 px |
| Büyük harf yüksekliği | 38–45 px | yaklaşık 39 px |
| Satır aralığı (taban çizgisinden taban çizgisine) | medyan 59 px (IQR 53–66) | 59 px, puntonun 1,07 katı |
| Dolgu | #FFFFFF | — |
| Kontur | Yaklaşık 4 px dolu siyah, ardından 4–5 px içinde zemine yumuşak geçiş (ofsetli gölge yok, kutu yok) | 4–5 px siyah kontur (yaklaşık 0,08 em) ve dış kenarına yaklaşık 1,5 px Gauss yumuşatma |
| Yatay konum | Merkez x = 542 px (p5–p95 539–571) | Tam ortalı (540) |
| Dikey konum | Blok merkezi medyan %42 (IQR %36,8–44,9; p5–p95 %24–50), yani çerçeve y ≈ 874 (820–905). Blok altı başın %0–12 (medyan %5, yaklaşık 55 px) üstünde. Çoğu reel'de pozisyon sabit (±20 px) | Blok altı = baş üstü − 55 px. Merkez %32–50 (y 766–960) aralığına sıkıştırılır. Reel içinde sabit tutulur |
| En uzun satır genişliği | medyan %68 (IQR %59–74, en fazla %86) | Kutu genişliği 860 px (%80) |
| Satır sayısı | 1 satır %38, 2 satır %60, 3 satır 2/121 | En fazla 2 |
| Satır kırma | Doyurarak (greedy) kırma: üst satır uzun, alt satır kısa kalan ("Otobüsten duman çıkıyor, / herhalde yangın çıktı") | Greedy kırma, satır başına en fazla 6–7 kelime |
| Animasyon | Yok. Sahnenin ilk karesinde var, kesmeyle kaybolur. Yazı görüntüden 1 kare (33 ms) geç değişebilir | Yok |
| Boyut değişimi | Aynı reel içinde çok uzun satırlarda %10–15 küçülme (C4bB) | `min_size` = 50 |

---

## 6. Arka plan

**Kaç fotoğraf:**
- 22/30 reel'de tüm diyalog sahneleri için tek fotoğraf kullanılır.
- 8/30 reel'de 2 fotoğraf olur. Değişim kart, zaman atlaması ya da mekân değişince yapılır (otobüs → dere, koridor → yemek odası).
- Hiçbir reel'de 3 ya da daha fazla yok.

**Ne gösterir:**
- Gerçek fotoğraftır, çizim değildir (30/30).
- Yaklaşık 22/30'unda "aynı türden yer" gösterilir: genel bir morg, otobüs içi, otoyol, uçak kabini.
- Yaklaşık 8/30'unda olayın gerçek yeri gösterilir: mağara, Epstein adası, Afyon türbesi, Kutsal Balıklar Parkı, İliç maden sahası, Engin Arık Sokağı, Tarsus evi, deprem enkazı.

**Renk ve ton:**
- Doğal gün ışığı renkleri.
- Diyalog karesinin parlaklığı medyan 121/255 (IQR 103–138). Doygunluk medyan 0,2.
- Gri ton 0/121. Kasıtlı karartma 1/121 (C2fa S5).

**Netlik:**
- Yumuşak ya da düşük çözünürlükten büyütülmüş.
- Kenar bölgelerinde Laplace varyansı (720 ölçeğinde) medyan 22, IQR 11–47.
- C12O'da güçlü Gauss bulanıklığı var. C1co keskin bir video karesi.

**Ek katman:** Yalnız 4/30 reel'de, hikâyenin gereği olarak ve sert kesmeyle açılıp kapanır:
- duman (C2kk S2),
- sis (C5Yy),
- sis ve yapıştırılmış hayalet yüzleri (C2-U, C1Xe).

**Hareket:** Yok (bkz. §9).

---

## 7. Ara kart

**Kullanım:** 10/30 reel'de, her reel'de en fazla bir kez.

**Metinler:** "Bir süre sonra" (6), "Birkaç saat sonra" (2), "Birkaç gün sonra" (1), "9 yıl sonra" (1).
- Hepsi ileri zaman atlaması.
- Noktalama yok. Geri dönüş (flashback) ya da "Oysa…" gibi karşıtlık kuran metin yok.

**Görünüm:**
- Tüm kare saf siyah. Yazı Anton, beyaz, konturlu değil, tek satır.
- Karenin yatay ve dikey merkezinde (%50/%50; C3De'de %46).
- Punto yaklaşık 160 px; büyük harf yüksekliği yaklaşık 138 px. Uzun ifadede genişlik ≤%88–92 olacak şekilde küçülür (131–135 px).
- Ölçülen genişlik: "Bir süre sonra" 901–957 px (%83–89), "Birkaç saat sonra" 951 px (%88), "9 yıl sonra" 691 px (%64).
- Üç reel'de piksel olarak aynı kart kullanılmış.

**Zamanlama:**
- Süre 1,46–2,00 sn (medyan 1,5).
- 3,0–9,3 sn arasında başlar (medyan 5,5).
- Hep diyalog sahnesine bağlanır.

**Filigran:** Kartta da var.

---

## 8. Kanıt bölümü

**Yer:** 25/30 reel'de reel'in sonunda.
- Kısa reel'lerde 1–4 görsel (medyan 2), her biri yaklaşık 1,5 sn (0,97–2,47).
- Kanıt bloğu 1,2–6,5 sn (medyan 3,5) ve yaklaşık 10. saniyede başlar.

**Yerleşim:**
- Tam genişlik 1080 px.
- Siyah zemin üzerinde letterbox; dikey merkez çerçevenin ortası (y=960; ölçülen medyan 960).
- Yükseklik medyanı yaklaşık 610 px (16:9 için 1080x608). Aralık 537–816 px; görsel karenin içinde kalır (%87).
- Gazete sayfası, portre veya ızgara gibi uzun görseller kareyi doldurabilir ya da taşabilir (en fazla 1260 px, y 330–1590).

**İçerik:**
- Gerçek yer fotoğrafı.
- Haber grafiği veya YouTube küçük resmi, kendi başlığıyla. Son görsel sık sık budur.
- Gerçek kişi fotoğrafı.
- Hazır kolaj.
- Kaynaktaki kırmızı daire ve ok işaretleri olduğu gibi kalır.

**Eklenmeyenler:**
- Etiket, altyazı, kırmızı bant, "Gerçek fotoğraf" ibaresi: 0/70.
- Yakınlaşma ve flaş yok.

**Sansür:** Yıldızlı kelime, kırmızı çizgi, siyah göz bandı veya pikselleştirme (7/30).

**Filigran:** Kanıtın üstünde kalır.

---

## 9. Hareket ve geçişler

**Sahne içi:**
- İlk ve son kare arasındaki ortalama mutlak fark (MAD, 180x180, 0–255 ölçeği): medyan 0,4, p95 1,1. Bu değer kodlayıcı gürültüsüdür.
- En iyi yakınlaşma uyumu 1,000.
- Yani zoom, kaydırma, sarsıntı, pop-in, zıplama, yazı animasyonu, flaş ve kararma yok (30/30).

**Geçiş:**
- %100 sert kesme. Kesmeden sonraki karede karışma 0,3'ün altında.
- Siyah kare yalnız C5ob'un son 2 karesinde var.

**Tek istisna:** C5eF'de ilk kanıta geçişte 0,27 sn süren 1,29x → 1,00x uzaklaşma. Lisanslı müziğin vuruşuna denk getirilmiş. Taklit etme.

---

## 10. Ses (Görev 1 sonuçları)

### 10.1 Gruplama (30 reel)

| Grup | Reel | Kanıt |
|---|---|---|
| **G1: imza "orijinal ses"** | 27/30. 26'sı birebir aynı kazançta; C1SV de aynı parça ama +14,4 dB yüksek ve 0,18 sn kaydırılmış | C2kk'ye göre dalga formu korelasyonu r ≥ 0,994 (C1SV 0,907). Gecikme 0 ms (C2Ah 33 ms). Kazanç 0,0 ± 0,1 dB. Kroma benzerliği 1,000 (C1SV 0,978). Artık sinyal −19 ile −44 dB (codec gürültüsü) |
| **G2: "Verbatim (Slowed Down)", Mother Mother** (lisanslı) | C5ob, C5eF | İkisi birbirine r = 0,968. C5eF, şarkıda 3,23 sn önceden başlıyor. G1 ile kroma benzerliği 0,43–0,48 |
| **G3: başka bir orijinal ses** | DHG (2025) | Diğerleriyle r ≈ 0. G1 ile kroma benzerliği 0,49 |

**Instagram kaydı:** Her yükleme ayrı bir `audio_asset_id` almış. G1 bile her seferinde dosyaya gömülü "orijinal ses" olarak yeniden yüklenmiş.

**İzlenme:** G1 reel'lerinin izlenme medyanı 11,9M (5,9–28,1M). En çok izlenen 9 reel'in hepsi G1'de.

### 10.2 Ana parçanın (G1) tarifi

| Özellik | Ölçüm |
|---|---|
| Uzunluk | Ses 0,00 ile 13,75 sn arasında var (RMS −45 dBFS'nin üstünde), sonra sessizlik. **Döngü yok**: 17 sn'lik C5Yy 13,75 sn'den sonra tamamen sessiz. Daha kısa reel'lerde parça kesilip bitiriliyor |
| Ölçü ve tempo | 3/4 vals. Vuruş aralığı 0,395 sn, yani yaklaşık 152 BPM. Ölçü 1,161 sn (3 x 0,387), yani yaklaşık 155 BPM ve dakikada 52 ölçü. 13,75 sn'de yaklaşık 12 ölçü |
| Ton ve melodi | **Do minör**. Baskın perde izleme: Do5–Mi♭5–Re5–Fa5–Do5–Mi♭5…, 8,4 sn'de La♭5–Sol5. 11,5–12,9 sn arasında 1,4 sn tutulan Do5 ile kalış (kadans). Perde aralığı Re4–La5; çekirdek Do5–Fa5 (523–698 Hz). Kroma tepeleri Do, Sol, La, Re, Mi♭ |
| Tını | Kesintisiz, legato, tutulan tonlar ve zengin harmonikler. Spektrogramda sürekli harmonik katmanlar ve gürültü tabanı görünüyor (lo-fi). Notalar arasında sessizlik yok: 0,25 sn'lik her pencerede RMS −30 ile −43 dB arasında. Akordeon, org veya eski plak hissi. Davul, bas ve vokal yok |
| Spektrum | Enerji dağılımı: <120 Hz %0,43; 120–250 Hz %0,07; 250 Hz–1 kHz %36,9; 1–4 kHz %62,3; >4 kHz %0,3. Merkez frekans 1346 Hz. %95 enerji sınırı 2,5 kHz. Spektral düzlük 0,017 (tonal). 1/3 oktav tepeleri 630 Hz ve 1,6 kHz. 160 Hz −15 dB, 6,3 kHz −34 dB. Kısacası yaklaşık 250–4000 Hz arası telefon ya da gramofon EQ'su |
| Tekrar | Kroma öz-benzerliği 2,40 sn gecikmede (2 ölçü) 0,66 ile en yüksek: motif tekrar ediyor ama birebir döngü yok |
| Ses düzeyi | Entegre −29,6 LUFS, LRA 3,6 LU, örnek tepe −18,3 dBFS (gerçek tepe yaklaşık −17 dBTP), RMS −34,7 dBFS. 2023 sonundaki C1SV dışında hepsi bu seviyede |
| Başlangıç | 0,00 sn. İlk 0,25 sn'de RMS −42 dB, ardından yaklaşık −35 dB |
| Ses efekti (SFX) ve ses | **Yok.** Referans dalga formu çıkarılınca artık sinyal −19 ile −44 dB arasında kalıyor ve yalnız son kesme penceresinde yükseliyor. Kesme anlarında onset gücü 90. yüzdelik dilimin ≈1,0 katı (vuruş, whoosh, boom yok). G2 içinde karşılıklı artık −12 ile −18 dB (eklenmiş SFX yok). Seslendirme veya TTS 0/30 |

### 10.3 Bizim parçamızla karşılaştırma (`assets/music/imza_gece_vals.mp3`)

| | Orijinal G1 | imza_gece_vals |
|---|---|---|
| Ton | Do minör | La minör (KS 0,75) |
| Tempo | 3/4, yaklaşık 152–155 BPM (vuruş 0,39 sn) | 3/4, yaklaşık 129 BPM (vuruş 0,464 sn, ölçü 1,39 sn) |
| Tını | Tutulan legato, gürültü tabanlı lo-fi | Mızraplı müzik kutusu: her nota sönüyor, aralar sessiz, temiz kayıt (gürültü tabanı yok) |
| Spektrum | %99'u 250–4000 Hz arasında; 1–4 kHz %62 | %84'ü 250 Hz–1 kHz arasında; 1–4 kHz %11,6; 250 Hz altı %4,7 |
| Uzunluk ve döngü | 13,75 sn tek cümle, tonik üstünde biter | 46 sn; `audio.py` içinde `-stream_loop -1` ile döngülü |
| Ses düzeyi | −29,6 LUFS, tepe −18 dBFS | Dosya −14,8 LUFS, tepe −5,4 dBFS |
| Benzerlik | — | G1 ile kroma benzerliği 0,36. Bu, ilgisiz şarkılardan (0,43–0,49) bile düşük; his de melodi de tutmuyor |

**Teslim edilen miksler:**
- −16,1 ile −17,0 LUFS; örnek tepeler −0,5 ile −2,1 dBFS.
- Enerjinin %48–65'i 120 Hz'in altında (drone ve boom).
- Müzik, dosyaya göre yaklaşık −9,5 dB'de duruyor; miksle korelasyonu yalnız 0,27–0,34.
- Videoların her birinde 5–6 SFX var; kayıt süresinin yaklaşık %85'ine SFX hâkim.

### 10.4 Ses hedefi

- **Tercih:** Hesabın kendi imza orijinal sesi (G1). Hesap sahibinde var.
- **G1 kullanılamıyorsa:** `tools/make_music.py` ile yeni bir parça üretilir:
  - Do minör, 3/4, 152–155 BPM.
  - Legato tutulan lead (akordeon veya org benzeri), Do5–La♭5 arası.
  - 250 Hz yüksek geçiren ve 4 kHz alçak geçiren filtre, hafif hışırtı tabanı.
  - 13,75 sn tek cümle; 11,5 sn'de tonikte tutulan bir kalış.
- **Miks:**
  - Entegre −29,5 LUFS (±0,5). Gerçek tepe −17 dBTP veya altı.
  - 0,00 sn'de başlar, döngü yok, SFX yok, seslendirme yok, limiter yok.
  - Reel 14,0 sn'yi geçmez.

---

## 11. Filigran

- Metin `tarihselwojak`; replikle aynı font ve stil (Avenir Bold Italic, beyaz, ince siyah kontur).
- Mürekkep kutusu 196–218 x 30–34 px.
- Sağ kenardan karenin sağ kenarına boşluk 63–154 px, medyan yaklaşık 95. Örnek konum: x 772–972 (C4V3, kart karesi).
- Alt kenar karenin tabanının 1–10 px üstünde (medyan yaklaşık 5), yani y yaklaşık 1495.
- Her karede bulunur: diyalog, kart, kanıt (30/30). İstisna: C5Yy'nin film afişi altı.

---

## 12. Kapak

**YouTube kopyalarındaki kapaklar:** 17 reel'in YouTube kapağı incelendi. 17/17'si bir **diyalog sahnesi karesi**: karakter ve replik birlikte; çoğu 1–7. saniyelerden, bazıları ters köşe yüzü. Kart ya da kanıt karesi 0.

**Kapak kuralı:**
- 1080x1920 tam kare kullanılır (siyah bantlar dahil).
- 1. sahnenin kancası ya da ters köşe yüz varyantı seçilir.
- Ek başlık, etiket ya da çip konmaz.

---

## 13. Renderer parametre özeti

| Ayar | Değer |
|---|---|
| `FONT_DIALOG` | `AvenirLTStd-BoldItalic-TR.otf`, `DIALOG_SHEAR` = 0 |
| `DIALOG_SIZE` | 55 (x-yüksekliği 27 px); `min_size` = 50 |
| `DIALOG_PITCH` | 1,07 (59 px) |
| `DIALOG_STROKE` | yaklaşık 0,08 (4–5 px) ve dış kenarda yaklaşık 1,5 px yumuşatma; ofsetli gölge yok |
| `DIALOG_MAX_W` | 860; `DIALOG_MAX_LINES` = 2; satır kırma `greedy` |
| `TEXT_HEAD_GAP` | 55; blok merkezi karenin 0,32–0,50'si arasına sıkıştırılır |
| Karakter `height` | 0,48 (izinli 0,42–0,55); sahne başına 1 karakter; aynı karakter hep aynı `side` |
| Sahne `zoom` / `pan` / `shake` / `flash` / `pop` | 1,0 / (0, 0) / 0 / false / false (hepsi) |
| `darken` / `grayscale` | 0 / false |
| Arka plan `blur` | yaklaşık 2,5 px (hedef: kenar Laplace varyansı medyanı yaklaşık 20) |
| Kart | Anton 160 px, `max_w` 990 (≤ %92), 1,5 sn; metin ileri zaman atlaması |
| Kanıt | Tek görsel, 1080 genişlik, y=960'a ortalı; `label`, `banner`, `zoom` yok; 1,5 sn |
| Filigran | 196–218 x 30–34 px; sağ boşluk yaklaşık 95; taban boşluğu yaklaşık 5; her karede |
| Müzik | G1 parçası (ya da §10.4'e göre üretilen), −29,5 LUFS, döngü yok, limiter yok; `sfx: []` |

---

## 14. Senaryo kalıbı: ölçülen reel'lerden 5 gerçek örnek

### Örnek 1: C4V3eMFM6lF (27,5M), Malatya depremi

Kalıp: diyalog → kart → diyalog. Kanıt yok.

| # | Zaman | Arka plan | Karakter (taraf, yüz) | Replik |
|---|---|---|---|---|
| 1 | 0,00–3,03 | A: apartman koridoru | Anne (sol-orta, mavi gözyaşı) ve kız (sağ alt) | "Gecenin bu saatinde bizi nasıl / kovuyorsun nereye gidicez?" |
| 2 | 3,03–5,53 | A | Koca (sol, sinirli) | "Nereye giderseniz gidin" |
| 3 | 5,53–7,00 | KART | — | "Bir süre sonra" |
| 4 | 7,00–9,50 | B: yemek odası | Koca (sol, rahatlamış) | "Sonunda kurtuldum onlardan" |
| 5 | 9,50–12,00 | B (yalnız yüz ve yazı değişir) | Koca (ter damlası, yan bakış) | "Bekle, ev neden sallanıyor?" |
| 6 | 12,00–14,00 | B (yalnız yüz ve yazı değişir) | Koca (alnında mavi soğuk ter çizgileri) | "Olamaz deprem oluyor" |

### Örnek 2: C2FriLUM2DR (22,2M), Issız Cuma Mezarlığı

Kalıp: diyalog → kart → diyalog → kanıt.

| # | Zaman | Arka plan | Karakter | Replik |
|---|---|---|---|---|
| 1 | 0,00–2,50 | Yosunlu mezar taşları (tek fotoğraf) | Başörtülü kadın (sol, gözü yaşlı) | "İmam bey bu mezarlar ayrı / değil miydi nasıl birleşti?" |
| 2 | 2,50–5,00 | aynı | İmam (sağ, şüpheci) | "Bilmiyorum, ama merak / etme tekrar ayıracağım" |
| 3 | 5,00–6,53 | KART | — | "Birkaç gün sonra" |
| 4 | 6,53–9,03 | aynı | Kadın (sol, aynı yüz) | "Mezarları ayıracağım / demiştiniz ayırmadınız mı?" |
| 5 | 9,03–11,50 | aynı | İmam (sağ, **gözlüklü ve endişeli** varyant) | "Ayırmıştım ama yine / birleşmişler" |
| 6 | 11,50–12,53 | KANIT | Mezarın gerçek fotoğrafı, 1080x606 | — |
| 7 | 12,53–14,03 | KANIT | Haber küçük resmi "ÇANAKKALE'DE YER DEĞİŞTİREN MEZAR!" | — |

### Örnek 3: C12OZjesdVM (20,2M), 129 nolu apartman

Kalıp: diyalog → kanıt; yüz varyantıyla ters köşe.

| # | Zaman | Arka plan | Karakter | Replik |
|---|---|---|---|---|
| 1 | 0,00–2,50 | Bulanık oturma odası (tek fotoğraf) | Kahverengi kapüşonlu kız (sol) | "Gece yarısı oldu hadi ayin yapalım" |
| 2 | 2,50–4,50 | aynı | Mor kapüşonlu kız (sağ, nötr) | "Tamam" |
| 3 | 4,50–6,50 | aynı (yalnız yüz ve yazı değişir) | Mor kız (**şok, iri gözler**) | "Bekle, ev neden sallanıyor?" |
| 4 | 6,50–8,00 | KANIT | Gerçek apartman | — |
| 5 | 8,00–9,47 | KANIT | Pentagramlı terk edilmiş oda | — |
| 6 | 9,47–10,97 | KANIT | Kolaj: apartman ve hayalet | — |

### Örnek 4: C2kkZ8BsngB (28,1M, en çok izlenen), Sakarya kezzap olayı

Kalıp: tek kişilik monolog, yüz ilerlemesi, ardından kanıt.

| # | Zaman | Arka plan | Karakter | Replik |
|---|---|---|---|---|
| 1 | 0,00–2,97 | Otobüs içi | Klasik wojak (sol, ter damlalı) | "Olamaz, otobüs kaza yaptı" |
| 2 | 2,97–5,47 | Otobüs ve duman katmanı | Aynı wojak (gergin, alnında mavi çizgiler) | "Otobüsten duman çıkıyor, / herhalde yangın çıktı" |
| 3 | 5,47–7,97 | Gece, dere | Aynı (gergin) | "En iyisi şu dereye girip / kendimi yangından kurtarayım" |
| 4 | 7,97–10,47 | Aynı dere | **Erimiş yüz** varyantı, aynı kutu | "Neden vücudum yanıyor?!" |
| 5 | 10,47–11,93 | KANIT | "TRAFİK ŞEHİTLİĞİ 11.8.1965" anıtı | — |
| 6 | 11,93–14,00 | KANIT | Gazete kupürü "…ER*YEREK *LDÜ" (kırmızı sansür) | — |

### Örnek 5: C3iXf2zsRvo (17,4M), "Annen aslında erkek"

Kalıp: soru-cevapla ifşa, ardından kanıt.

| # | Zaman | Arka plan | Karakter | Replik |
|---|---|---|---|---|
| 1 | 0,00–2,50 | Morg (tek fotoğraf) | Kız (sol, ağlıyor) | "Annemin otopsi sonuçları çıktı mı?" |
| 2 | 2,50–5,00 | aynı | Doktor (sağ) | "Annen olduğuna emin misin?" |
| 3 | 5,00–8,03 | aynı | Kız (sol, **kaşları çatık ve şaşkın**, gözyaşı yok) | "Ne demek istiyorsun? / Evet beni doğurup büyüten annem" |
| 4 | 8,03–10,53 | aynı | Doktor (sağ, aynı yüz) | "Çünkü bu kişi bir kadın değil erkek" |
| 5 | 10,53–12,03 | KANIT | 3 fotoğraflık kolaj (bir yüz pikselli) | — |
| 6 | 12,03–13,53 | KANIT | Haber başlığı, "ölünce" kelimesi kırmızıyla karalanmış: "ANNEN ASLINDA ERKEK" | — |

### Boş şablon (senarist için)

| Sahne | Süre | Karakter | İçerik |
|---|---|---|---|
| S1 | 2,5–3,0 sn | A (sol) | Kanca: olay anında bir soru ya da masum/ironik bir niyet |
| S2 | 2,0–2,5 sn | B (sağ) | Cevap, uyarı ya da ret |
| S3 | 2,5 sn | A veya B | Karar ya da tırmanış (gerekirse yalnız yazı değişen ikinci replik) |
| [Kart] | 1,5 sn | — | İsteğe bağlı: "Bir süre sonra" / "Birkaç saat sonra" / "Birkaç gün sonra" |
| S4 | 2,0–2,5 sn | Bakış açısı karakteri | Aynı poz, **yüz varyantı**: "Bekle, … neden …?" ya da dramatik ironi |
| Kanıt | 2–3 x 1,5 sn | — | Gerçek yer → kişi ya da haber; son görsel tercihen haber başlığı |

---

## 15. Yapma listesi

1. Ken Burns, zoom, kaydırma, sarsıntı, pop-in, flaş ya da fade kullanma. Kanıtta da kullanma.
2. Kanıttan sonra diyalog ya da kapanış cümlesi koyma.
3. Anlatıcı, özet, geçmiş zamanlı rapor cümlesi yazma ("180 asker bulundu. Sadece ikisi tanınabildi.").
4. Nokta, üç nokta ya da (neredeyse hiç) ünlem kullanma. 3 satırlı replik yazma.
5. Etiket çipi ("Gerçek fotoğraf · …", "İddia · 1965"), kırmızı alıntı bandı, yer/tarih yazısı koyma.
6. Arka planı karartma ya da gri tona çevirme. Sahne başına yeni fotoğraf seçme (en fazla 2 fotoğraf).
7. Karaktersiz diyalog sahnesi bırakma. Aynı karakteri sahneler arasında taraf değiştirtme. 2'den fazla konuşmacı kullanma.
8. Kartı geri dönüş ya da karşıtlık için kullanma ("10 gün önce", "Oysa 1919'da...").
9. SFX koyma (drone, hit, boom, heartbeat, shutter, whoosh). −20 LUFS'tan yüksek miks yapma. Müziği döngüye sokma.
10. Poppins Bold Italic kullanma (tek katlı "a", 9,7° eğim). Kontur dışında kutu ya da ofsetli gölge ekleme.
11. Kanıtı küçültme, kenarlık verme, kağıt rengi zemin üstüne koyma, 2'li veya 4'lü ızgara yapma (kolaj gerekiyorsa hazır tek görsel kullan).
12. Filigranı kartta ya da kanıtta atlama.

---

# Ek: ilk denemelerimizdeki hatalar (2026-10-09, hesap sahibi 3/10 verdi)

İncelenen render'lar `/home/user/wojak/teslim/{canakkale-kayip-tabur,nusret-mayin-gemisi,van-depremi-azra-bebek,derinkuyu,dyatlov-gecidi}`.

**Önemli not:** Teslim render'ları 94ec090 ve 3a15d20 commit'lerinden önce üretildi. Kodun bazı varsayılanları sonradan düzeldi: etiketler kapalı, font Avenir, `zoom` 1,0, `pop` false. Ama episode YAML'ları hâlâ `shake`, `zoom`, `flash`, `darken`, `grayscale`, `label`, `banner`, `text_y` ve `sfx` içeriyor. Yani YAML'lar düzeltilmeden yeniden render edilirse farkların çoğu yine çıkar.

### Yapı ve senaryo

1. **Kanıttan sonra diyalog:** 5 render'ın 5'inde kanıttan sonra bir kapanış diyaloğu var (canakkale S6, nusret S6, van S6, derinkuyu S6, dyatlov S6). Orijinallerde bu 0/30.
   - **Değişiklik:** `type: evidence` sahneleri en sona taşınır. Kapanış repliği silinir ya da kanıttan önceki son diyalog (ters köşe) yapılır.
2. **Anlatıcı dili:** Repliklerin 6'sı nokta, 9'u "...", 4'ü "!" içeriyor. Bir kısmı geçmiş zamanlı özet ("Dokuz kişi. Hiçbiri geri dönmedi.", "Bulduğumuzda hâlâ annesinin kucağındaydı"). Orijinallerde nokta 0, üç nokta 0, ünlem 3/121.
   - **Değişiklik:** Bütün `text:` alanları şimdiki zamanlı, birinci şahıs, iki kişilik bir diyaloğa yeniden yazılır. Nokta ve üç nokta kaldırılır. Son diyalog fark etme sorusu olur.
3. **Konuşma yok, monolog var:** Reel başına 3 farklı konuşmacı var ve birbirlerine cevap vermiyorlar: canakkale'de subay, gazi, papaz; nusret'te Fransız denizci, Osmanlı subayı, İtilaf subayı; dyatlov'da yürüyüşçü, kız, asker. Orijinallerde aynı mekânda soru-cevap yapan 2 kişi var (26/30).
   - **Değişiklik:** Her bölüm 2 karakterle, A↔B sırayla yazılır.
4. **Zaman yayılımı:** Sahneler 1915 → 1965 → 1919 gibi on yıllar ve mekânlar arasında geziyor. Orijinallerde tek gece veya tek olay var; en fazla bir ileri zaman atlaması.
5. **Kart:** Kartlar "Oysa 1919'da..." ve "10 gün önce" (nusret'te S2'de, 3,6. saniyede).
   - **Değişiklik:** Kart metni yalnız "Bir süre sonra", "Birkaç saat sonra", "Birkaç gün sonra" ya da "N yıl sonra" olur; noktalama yok. Konumu 5,0–7,5 sn arası, iki diyalog arasında.
6. **Süreler:** Diyalog süreleri 1,9–3,6 sn ve 0,5 sn ızgarasına oturmuyor (2,6 / 2,7 / 2,8 / 3,3 / 3,6). Kart 1,0–1,1 sn. nusret toplamı 14,47 sn.
   - **Değişiklik:**
     - Diyalog `duration` değerleri 2,0, 2,5 ya da 3,0 olur; ilk sahne 2,5–3,0.
     - Kart `duration` 1,5 olur.
     - Kanıt her biri 1,5 sn, 2–3 görsel.
     - Toplam en fazla 14,0 sn.
7. **Yüz varyantı ve yalnız-yazı kesmesi yok:** Bizde 0 var; orijinallerde 16/30 reel'de var.
   - **Değişiklik:** Ters köşe sahnesinde aynı karakterin yüz varyantı kullanılır (aynı `img` kutusu ve `side`, farklı yüz PNG'si). `tools/kit_varyant.py` ve "Klasik wojak karakter seti" bu iş için kullanılabilir.

### Karakterler

8. **Karaktersiz sahne:** van S2'de ("Sütüm kurudu... Dayan kızım, dayan") karakter yok. Orijinallerde bu 0/121.
   - **Değişiklik:** Her `dialog` sahnesinde tam 1 konuşan karakter olur.
9. **Taraf değiştirme:** Aynı karakter taraf değiştiriyor: derinkuyu köylüsü sağ → sol, mühendis sağ → sol; van kurtarmacısı sağ → sol; dyatlov askeri sağ → sol. Orijinallerde her karakter hep aynı tarafta (30/30).
   - **Değişiklik:** Karakter başına sabit `side`. A hep `left`, B hep `right`.
10. **Boyut:** Görünen yükseklik 0,47–0,62 (medyan 0,58, yaklaşık 626 px). Orijinal medyan 0,48 (520 px), IQR 0,44–0,53.
    - **Değişiklik:** `chars[].height` 0,48 olur (0,42–0,55 aralığında tutulur).
11. **Pop-in:** Her diyalog sahnesinin ilk 0,2–0,27 sn'sinde karakter 0,82 ölçekten taşarak büyüyor. van S1'de ilk 0,2 sn yüz bile farklı.
    - **Değişiklik:** `pop: false`. Şu anki varsayılan bu; YAML'da `pop: true` olmamalı.

### Replik yazısı

12. **Font:** Teslimde Poppins Bold Italic kullanılmış (tek katlı "a", ölçülen eğim 9,7°). Orijinal Avenir LT Std Bold Italic (iki katlı "a", 6,3°).
    - **Değişiklik:** `config.FONT_DIALOG` = `assets/fonts/ozel/AvenirLTStd-BoldItalic-TR.otf`, `DIALOG_SHEAR` = 0. Şu anki kod dosya varsa bunu seçiyor; render makinesinde dosyanın bulunduğu doğrulanmalı.
13. **Boyut:** x-yüksekliği 35–42 px (medyan 41); orijinalde 25–30 (medyan 26). Bizimki yaklaşık 1,55x büyük.
    - **Değişiklik:** `DIALOG_SIZE` = 55 (şu an 58, teslimde Poppins yaklaşık 73 px). `dialog_text(min_size=40)` → 50.
14. **Satır aralığı:** 88–106 px (medyan 97,5); orijinalde 53–66 (medyan 59).
    - **Değişiklik:** `DIALOG_PITCH` 1,10 → 1,07 (55 px puntoda 59 px).
15. **Satır sayısı:** Bizde 14 sahne 2 satır, 3 sahne 3 satır, tek satır 0. Orijinalde %38 tek satır, %60 iki satır.
    - **Değişiklik:** `DIALOG_MAX_LINES` = 2 (şu anki değer). Replikler kısaltılır: 1 satır için en fazla 6 kelime, toplam en fazla 11 kelime. Elle `\n` yerine greedy kırma kullanılır (`wrap="greedy"`).
16. **Dikey konum:** Blok merkezi sabit %30'da (y ≈ 744, üste yaslı). Orijinalde medyan %42 (y ≈ 874; IQR %37–45), blok altı başın yaklaşık 55 px üstünde.
    - **Değişiklik:**
      - `TEXT_HEAD_GAP` 45 → 55.
      - `compose._overlay` içindeki sıkıştırma `max(box*0.20, min(y, box*0.47 - h/2))` yerine blok merkezi 0,32–0,50 aralığına alınır.
      - YAML'daki `text_y` alanları silinir (van S2'de `text_y: 0.42` var).
      - Karakter küçülünce (madde 10) yazı da doğal olarak aşağı iner.
17. **Kontur:** Teslimde yaklaşık 3 px keskin kontur var. Orijinalde yaklaşık 4 px dolu kontur ve 4–5 px yumuşak dış geçiş var. Halkalara göre parlaklık profili: orijinalde 6. pikselde zeminin %59'u, bizde %81'i.
    - **Değişiklik:** `DIALOG_STROKE` 0,08 olur (55 px'te 4,4 px; şu anki 0,095 x 58 = 5,5 px fazla). Kontur alfasının dış kenarına yaklaşık 1,5 px Gauss yumuşatma eklenir (ofsetsiz).
18. **Genişlik:** En uzun satır %61–81 (medyan %77); orijinalde medyan %68, en fazla %86.
    - **Değişiklik:** `DIALOG_MAX_W` 880 → 860. Kısaltılmış repliklerle medyan kendiliğinden yaklaşık %68'e iner.

### Arka plan

19. **Fotoğraf sayısı:** Her diyalog sahnesi farklı fotoğraf (canakkale, nusret, van, derinkuyu ve dyatlov'da diyalog sayısı kadar fotoğraf). Orijinallerde 22/30 reel'de tek, 8/30'da 2 fotoğraf.
    - **Değişiklik:** Bütün diyalog sahnelerinde aynı `bg` kullanılır. İkinci fotoğraf yalnız karttan sonra.
20. **Karartma ve gri ton:** 11 diyalog sahnesinde `darken` 0,15–0,6, 8 sahnede `grayscale: true`. Diyalog parlaklığı medyan 106 (p25 93), doygunluk medyan 0,1. Orijinalde parlaklık 121 (IQR 103–138), doygunluk 0,2, gri ton 0, karartma 1/121.
    - **Değişiklik:** Tüm YAML'lardan `darken` ve `grayscale` silinir. Renkli, gün ışığı fotoğraf seçilir.
21. **Netlik:** Kenar Laplace varyansı (720 ölçeği) bizde medyan 43, orijinalde 22 (IQR 11–47).
    - **Değişiklik:** `Scene.blur` varsayılanı 1,8 → yaklaşık 2,5. Ya da arka plan 540 px'e küçültülüp tekrar büyütülür.

### Hareket ve geçiş

22. **Ken Burns:** Bütün diyalog sahnelerinde arka plan kayıyor; ilk-son kare farkı 5,0–17,1 (medyan 9,0), orijinalde 0,4 (en fazla 1,1). Kanıtta `zoom` 1,04–1,08 var.
    - **Değişiklik:** `zoom: 1.0`, `pan: [0, 0]`. YAML'lardan `zoom` silinir (canakkale S5; nusret S4; van S2, S5; derinkuyu S3; dyatlov S5).
23. **Sarsıntı:** 8–9 px sarsıntı (canakkale S2, van S2, derinkuyu S2, dyatlov S2); kesme içi fark 7–16'ya çıkıyor.
    - **Değişiklik:** `shake` alanı silinir (varsayılan 0).
24. **Flaş:** nusret S4'te beyaz flaş var.
    - **Değişiklik:** `flash` silinir.

### Kart

25. **Boyut:** Anton yaklaşık 148 px, genişlik %65–78. Orijinal yaklaşık 160 px; uzun ifadede ≤ %88–92'ye sığdırılıyor ("Bir süre sonra" 901–957 px).
    - **Değişiklik:** `text.card_block(size=160, max_w=990)`. Şu anki 220/950 ayarı "Bir süre sonra"yı 948 px yapıyor; bu kabul edilebilir ama kısa ifadelerde 160 px tavanı gerekli.
26. **Filigran:** Teslimde kart karesinde filigran yok; orijinallerde her karede var. Şu anki kod ekliyor; yeniden render'da kontrol edilmeli.

### Kanıt

27. **Eklemeler:** Bütün kanıtlarda sol üstte etiket çipi var. canakkale'de kırmızı "“Hiçbiri geri dönmedi.”" bandı ve krem kâğıt zemin var. derinkuyu S5 954 px genişlikte (yanlarında boşluk).
    - **Değişiklik:**
      - `label` ve `banner` YAML'dan silinir (`SHOW_LABELS = False` korunur).
      - Belge görseli kâğıt zemine yerleştirilmez; görsel kendi oranında 1080 genişliğe ölçeklenip y=960'a ortalanır (`_evidence_bg` n=1 durumu).
      - Dikey görsel karenin dışına taşabilir.
      - Sahne başına tek görsel; ızgara (n ≥ 2) yerine hazır kolaj.
28. **Sayı ve yer:** Bizde 1–2 kanıt (1,6–1,8 sn), 8–10. saniyede başlıyor ve ardından diyalog geliyor.
    - **Değişiklik:** Sonda 2–3 x 1,5 sn kanıt, yaklaşık 10. saniyeden başlar. Son görsel tercihen haber başlığı. Hassas kelimeler kırmızı çizgiyle sansürlenir.

### Filigran

29. **Boyut ve yer:** Teslimde 250 x 39 px; sağ boşluk 45 px, taban boşluğu 29 px. Orijinalde 196–218 x 30–34 px; sağ boşluk yaklaşık 95, taban boşluğu yaklaşık 5.
    - **Şu anki kod:** 194 x 35, sağ 100, taban 17.
    - **Değişiklik:** `compose._overlay` içinde `box - wm.height + 2` → `box - wm.height + 14` (12 px aşağı). Yatay konum aynı kalır.

### Ses

30. **Ses düzeyi:** −16,1 ile −17,0 LUFS, tepe −0,5 ile −2,1 dBFS. Orijinal −29,5 LUFS, −17 dBTP; yani bizimki yaklaşık 13 LU yüksek.
    - **Değişiklik:** `audio.build` içinde miksin sonuna `loudnorm=I=-29.5:TP=-17:LRA=4` (iki geçişli) eklenir. `alimiter=limit=0.95` kaldırılır. Sabit kazançla yapılacaksa imza dosyası için `music.volume` yaklaşık 0,18 olur (−14,8'den −29,5 LUFS'a).
31. **SFX:** Her bölümde 5–6 efekt var (drone, hit, boom, heartbeat, shutter, whoosh); enerjinin %48–65'i 120 Hz altında. Orijinalde SFX 0/30.
    - **Değişiklik:** Bütün `sfx:` alanları silinir; `_sablon/episode.yaml`'daki sfx örnekleri kaldırılır.
32. **Parça:** `imza_gece_vals.mp3` La minör, yaklaşık 129 BPM, mızraplı müzik kutusu ve temiz kayıt; G1 ile kroma benzerliği 0,36. Orijinal Do minör, yaklaşık 152–155 BPM, 3/4, tutulan legato, 250–4000 Hz bantlı lo-fi, 13,75 sn.
    - **Değişiklik:** `music.file` = hesabın G1 orijinal sesi. O yoksa `tools/make_music.py` §10.4'teki hedefle yeniden üretilir.
33. **Döngü ve fade:** Müzik 46 sn ve `-stream_loop -1` ile döngüde; `fade_out` 0,3 sn.
    - **Değişiklik:** 13,75 sn'lik tek cümle kullanılır; `-stream_loop` kaldırılır; `fade_out: 0`. Reel en fazla 14,0 sn.

### Kapak

34. **Etiket:** canakkale kapağında "Çanakkale · 12 Ağustos 1915" çipi var.
    - **Değişiklik:** `kapak.jpg` etiketsiz bir diyalog karesi olur (S1 ya da ters köşe yüz varyantı) ve hareketsiz render'dan alınır (`still(at=0.6)` zaten durağan olur).

---
