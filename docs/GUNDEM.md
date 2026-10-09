# Gündem (güncel olay) oyun kitabı

Kanal sadece geçmiş olaylarla değil **güncel olaylarla** da beslenecek. Bu belge: neden, nasıl seçilir,
nasıl anlatılır, nelerden kaçınılır.

## 0. Veri ne diyor? (kanalın 25 güncel olay videosu)

Kaynak: 220 videonun YouTube verisi; olay tarihleri tek tek web'den doğrulandı (23/25). Örneklem küçük,
bulgular kesin değil yön gösterici.

- **Güncel video bir piyango bileti gibi:** Mart 2024 sonrası güncel videolar medyan **89K**, aynı dönem eski
  olaylar **53K**. 300K'yı geçme oranı güncelde **%23**, eskide **%9**.
- **Patlayanların hepsi gündemin zirvesinden 0-7 gün sonra çıktı:** Iryna Zarutska (1.42M, 14.8x), Olimpiyat
  sevimli an (770K, 16.4x), Narin (564K, 12x), Kayseri'de tekerlekli sandalyeli kızın dileği (504K, 10.7x).
  **10 günden geç yayınlanan 6 videonun hiçbiri** yerel ortalamanın 2 katına çıkamadı.
- **Hız tek başına yetmez:** 0-3 günde çıkan 10 videonun 7'si sıradan kaldı. Belirleyici olan konu:
  **adı bilinen tek bir masum insan + tek bir ironik/sevimli an + herkesin gördüğü bir görüntü.**
- **Tutmayanlar:** kahramanı olmayan soyut olaylar (salgın), terör (Bondi 0.75x), suçu aileye yükleyen ya da
  tartışmalı olaylar (5 kardeş yangını, Buca), 20 gün gecikmiş yabancı haberler, 24 sn+ videolar.
- **En güçlü grup "gündem kancalı eski hikâye":** yıldönümü, yeni açılan belgeler, yeni film.
  Epstein Adası (belgeler açılırken, 2.5M), deprem yıldönümünde enkaz hikâyeleri (1.7M) → n=6, medyan 1.28M.
- **Başlık:** sadece isim/etiket ("Ata Emre Akman", "Hantavirüs olayı", "Yenidoğan Çetesi") ≈ 1.0x;
  **"kim + sıradan eylem + ters dönen son"** ("Evine giderken trende katledilen Ukraynalı kız") ≈ 1.5x ve tüm
  büyük patlamalar bu kalıpta.
- **Beğeni oranı** mutlu sonlu iyilik hikâyelerinde en yüksek (%4.5-5.2); trajedilerde %0.8-1.5.
- **Süre:** patlayanların hepsi 10-17 sn. 24 sn ve üstü hiçbir güncel video 2x'e ulaşmadı.

Gecikmeyi **olaydan değil son dalgadan** ölç: görüntünün çıkması, cesedin bulunması, iddianame, yıldönümü.
(Iryna olaydan 21 gün sonra yayınlandı ama görüntülerin yayınlanmasından 7 gün sonraydı.)


## 1. Günlük rutin (15-20 dk)

```bash
python tools/gundem.py                 # son 48 saat -> out/gundem/<tarih_saat>.md
python tools/gundem.py --saat 24 --ilk 30
python tools/gundem.py --sorgu "maden" --sorgu "göçük"   # o gün özel bir konu varsa
python tools/gundem.py --taslak 3      # rapordaki 3. olay için episodes/gundem-... taslağı
```

Rapor her olay için şunu verir: temsilî başlık, puan dökümü (uygunluk, kaç kaynak yazdı, Google Trends,
tazelik, konu dışı cezası), tür (kayıp, mucize, kahramanlık, gizem, suç, kaza, tarih, hayvan),
**⚠️ DİKKAT** işareti (çocuk istismarı, intihar, terör, okul saldırısı, yayın yasağı ihtimali),
4 haber linki ve bir açı önerisi. Ayarlar ve kaynak listesi: `data/gundem_kaynaklar.yaml`.

Bilinen sınır: aynı olay farklı kelimelerle yazıldığında 2-3 kümeye bölünebilir, nadiren iki
benzer olay birleşebilir. Rapor **karar destek** listesidir; linkleri açıp kontrol et.

Kaynaklar (2026-10-09 test, ~70 RSS ve ~60 sorgu denendi): Google News TR + Türkiye bölümü, 16 isabetli
Google News araması (`"haber alınamıyor"`, `"cansız bedeni"`, `"şüpheli ölüm"`, `"saat sonra" kurtarıldı`,
`"faili meçhul"`...), Google Trends TR, Haberler.com, Hürriyet, Sözcü, Habertürk, Cumhuriyet, TRT, NTV, Sabah,
CNN Türk, AA, BBC Türkçe, DW Türkçe. Bir taramada ~2.000 haber, ~10 sn. Tek kelimelik "kahraman", "mucize",
"gizemli", "efsane" sorguları gürültü getirdiği için kullanılmıyor (soyadı Kahraman, "mucize gıda", "efsane cuma").
T24, İHA ve DHA'nın RSS'i bu sunucudan çekilemiyor (içerikleri Google News üzerinden geliyor).

## 2. Hangi güncel olay? (seçim kriterleri)

Bir olayı yapmak için **en az 3 "evet"**, hiç "kırmızı çizgi" yok:

| Soru | Neden |
|---|---|
| Ülke çapında konuşuluyor mu? (≥10 kaynak veya Google Trends'te) | Arama ve paylaşım talebi hazır |
| İçinde net bir **insan hikâyesi** var mı? (kahraman, kurban, kayıp, kurtulan) | Wojak formatı insanı anlatır; "bina çöktü" değil "enkazdan 22 saat sonra çıkan kız" |
| Tek bir **ironik/ürpertici an** var mı? | Replik ondan doğar (son masum cümle, son mesaj, ilk söz) |
| Gizem / mucize / fedakârlık unsuru var mı? | Altın dönemin en güçlü türleri |
| Gerçek fotoğraf/görüntü var mı? | Kanıt sahnesi |

**Kırmızı çizgiler (yapma):** yayın yasağı olan dosya · çocuk istismarı/cinsel suç ayrıntısı ·
intiharı anlatmak (yöntem, mekân) · terör saldırısının failini öne çıkarmak · resmi açıklama yokken
"cinayet" demek · siyasi/partizan konu · olaydan saatler sonra, kimlikler netleşmeden.

## 3. Hız

- Hedef: gündemin **son dalgasından 0-3 gün**, üst sınır **7 gün**. Tek günlük haberleri (yangın, kaza)
  48 saat geçtiyse yapma.
- **Kahramanlık / mucize / iyilik / tuhaf olay:** hemen (24-72 saat). Mutlu son = düşük risk, yüksek beğeni.
- **Kayıp / ölüm / suç:** önce **resmi açıklama** (valilik, emniyet, jandarma, AFAD, savcılık) bekle.
  Ülkenin her gün takip ettiği açık uçlu bir kayıpta erken gir (bilgilendirme + afiş), gelişme oldukça
  devam videosu çek. Sonuç belli olmadan "kurban" anlatımı yapma.
- **Büyük felaket (deprem, çökme):** ilk saatlerde değil; kurtarma hikâyeleri netleşince
  (ör. "22 saat sonra enkazdan çıkarılan..."). Acı tazeyken mizah ve "gizem" tonu yok.
- **Takvim kancaları:** büyük olayların yıldönümlerini (6 Şubat depremi, 17 Ağustos, Soma...) önceden hazırla.

## 4. Formatın güncel olaya uyarlanması

Altın dönem formatı aynen geçerli (11-15 sn, gerçek mekân + wojak + tek replik + gerçek kanıt + sabit yorum).
Farklar:

- **Kanıt sahnesi = haber:** `type: evidence` + `banner: "SON DAKİKA: ..."` ile haber bandı ya da
  haber ekran görüntüsü. Kaynak gazete adı `label:` ile görünür olsun (şeffaflık).
- **Replik yalnızca doğrulanmış bilgiden kurgulanır.** Kişinin gerçek sözü haberlerde varsa onu kullan
  (tırnak içinde, kısaltılmış). Yoksa durumu ima eden genel bir cümle (*"Birazdan dönerim"*).
  Asla olmayan bir suçlamayı karakterin ağzına koyma.
- **Fail/şüpheli:** isim ve yüz benzerliği yok, karar kesinleşmeden "katil" yok ("şüpheli").
- **Başlık:** **[kim] + [sıradan eylem] + [ters dönen son]**, doğrulanmış bilgiden
  (*"Evine giderken trende katledilen Ukraynalı kız"*, *"10 saat aranan çocuk kamyonet kasasında uyurken bulundu"*).
  Sadece isim ya da "X olayı" yazma.
- **Sabit yorum:** kronoloji + "Resmi açıklamaya göre..." + kaynak adı + tarih.
  Gelişme olursa yorumu güncelle ("GÜNCELLEME 12.10: ...").
- **Devam videosu:** büyük gelişmede ikinci video ("Efe'nin bulunduğu an" gibi) — seri izleyici getirir.

## 5. Yayından önce kontrol listesi

<!-- BOLUM:KONTROL -->

## 6. Takvim önerisi

Haftada 5 video: **3 tarihsel/efsane/gündem kancalı eski hikâye + 1-2 güncel**. Güncel video yalnızca olay
Türkiye'de ulusal gündemdeyse ya da küresel viral bir görüntüsü varsa; yoksa stoktaki hazır videolardan
biri yayınlanır (`docs/KONU_HAVUZU.md`). Yıldönümleri takvime önceden işlenir.

<!-- BOLUM:HUKUK -->
