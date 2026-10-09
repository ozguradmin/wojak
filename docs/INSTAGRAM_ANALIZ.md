# @tarihselwojak Instagram analizi: dönem, konu ve zamanlama (1M+ izlenen 75 reel)

> Veri: `data/instagram_reels.csv` (129 gönderi, 2026-10-09). Görsel ölçüler: [`STIL.md`](STIL.md). YouTube kopyası analizi: [`ANALIZ.md`](ANALIZ.md).

**Sonuç:** Videoları milyonlara taşıyan şey formattan çok **konu seçimiydi**. 10M üstüne çıkan 19 reelin 17'si Türkiye'de geçiyor. Bunlar gösterilebilir bir yerde geçen efsane, gizem, deprem mucizesi ya da dehşet verici bir dönüş noktası olan olaylar.

Düşüş üç basamakta geldi:
1. **Konu kaydı:** Türkiye'nin kalıcı efsane/suç konuları bırakıldı, yerine yabancı gizemler geldi.
2. **Format kaydı:** süre uzadı, lisanslı müzik ve reaction kamera eklendi, meme'lere geçildi, en son yapay zekâ çizimine dönüldü.
3. **Paylaşım ritminin çökmesi:** 2 günde 1'den 2025'te ortalama 3 haftada 1'e indi.

İlk düşüşün sıklık ya da formatla ilgisi yok. 21 Şubat 2024'te izlenme yarıya indiğinde format da paylaşım sıklığı da (2 günde 1) hâlâ aynıydı.

## 0. Veri ve yöntem
- **Kaynaklar:**
  - `instagram_reels.csv`: 129 satır. Ekim 2026 tarihli 4 başka hesap gönderisi ile 0 izlenmeli fotoğraf/karusel gönderileri çıkarıldı.
  - `referans/meta.json` ve 75 adet mp4: 1M+ izlenen reellerin hepsinin videosu var.
  - YouTube kopyası `videos.csv` (220 video).
- **Tarihsiz satırlar:** 26 reelin tarihi Instagram kısa kodundan (shortcode → zaman damgası) çıkarıldı. Doğruluğu dakika düzeyinde, tarihli satırlarla birebir tuttu. Bu reellerin konusu YouTube'daki aynı dakikada paylaşılan videonun başlığından alındı. 4 erken dönem ve 2 eşleşmeyen reelin içeriği bilinmiyor.
- **Görüntü ölçümü:** her video 4 fps örneklendi. Ölçülenler: diyalog alanı, son görselin kareden taşıp taşmadığı, karenin altındaki etkinlik (reaction kamera), hareket miktarı ve süre. 75 videonun her birinden 5 kare göz ile de incelendi.
- **Göreli performans:** bir reelin izlenmesi, zamanca ona en yakın 6 Instagram reelinin medyan izlenmesine bölündü. Bu, hesabın o anki tabanına göre ölçmeyi sağlıyor.
- **Uyarılar:**
  - **Hayatta kalma yanlılığı.** Altın dönemde YouTube'da olup Instagram profilinde olmayan 10 video var (örneğin Çumra canavarı, Uruguay 571, şoför cinayeti). Bunlar ya silinmiş/arşivlenmiş ya da hiç paylaşılmamış. Nisan–Aralık 2024'te YouTube'daki 70 video Instagram'da yok. Bu yüzden 2023–2024 Instagram medyanları üst sınır sayılmalı. 2025–2026 için Instagram profili neredeyse tam (23 YouTube videosundan 21'i var).
  - Eski reeller daha uzun süre izlenme topladı. Instagram'ın izlenme metriğini de yıllar içinde değiştirmiş olması mümkün, bu yüzden yıllar arası ham karşılaştırma kaba kalır.
- **Kategori eklemeleri:** "Gerçek suç" kategorisine faciaları da (kezzap, Challenger) dahil ettim. Görev listesinde olmayan bir **"TR dokunaklı"** kategorisi ekledim (Kore'de Ayla, Bekir Çınar, Usta Mediha).
- **Format kodları:**

| Kod | Anlamı |
|---|---|
| O1 | Klasik olay: 720×720 kare, gerçek mekân fotoğrafı, wojak, tek satır ortalı replik, sonda gerçek fotoğraf; 11–15 sn |
| O2 | Uzamış olay: 16 sn üstü, "Bir süre sonra" kartları, kareden taşan son fotoğraflar |
| R | Karenin altında reaction kamerası |
| M | Meme veya skeç |
| H | Wojak açılış, ardından gerçek video ağırlıklı |
| AI | Yapay zekâ çizimi sahne, çok satırlı sol-üst metin, REC efekti |
| X | Arşiv görüntüsü |

## 1. 1M+ izlenen 75 reelin tablosu

| # | Tarih | Konu | İzlenme | Beğeni | Yorum | Beğeni % | Yorum % | Süre (sn) | Tür | Kahraman | Format | Dönem | Göreli |
|--:|---|---|--:|--:|--:|--:|--:|--:|---|---|---|---|--:|
| 1 | 2023-10-02 | Kızlar vs Erkekler "şişman mıyım" meme | 5.08M | 168K | 279 | 3.31 | 0.005 | 7 | Other | yok (meme) | M | D0 | 2.05 |
| 2 | 2023-10-16 | "Kudüs bizim" 1090 vs 2023 meme | 2.89M | 116K | 3.183 | 4.03 | 0.110 | 14 | Other | yok (meme) | M | D0 | 0.85 |
| 3 | 2023-10-17 | Kontrolcü sevgili skeci | 2.07M | 133K | 3.592 | 6.40 | 0.173 | 48 | Other | yok (meme) | M | D0 | 0.54 |
| 4 | 2023-12-02 | DM "annem vefat etti, son kez kekini…" | 1.61M | 88K | 1.674 | 5.42 | 0.104 | 16 | Other | yok (meme) | M | D0 | 0.20 |
| 5 | 2023-12-08 | "Ben Jack'in annesiyim" gamer mesajı | 5.22M | 187K | 549 | 3.58 | 0.011 | 6 | Other | yok (meme) | M | D0 | 0.66 |
| 6 | 2023-12-16 | "Bu kadar kolay mı" | 4.75M | 119K | 1.849 | 2.50 | 0.039 | 8 | Other | yok (meme) | M | D0 | 0.58 |
| 7 | 2023-12-23 | "45 saniye" (şehit haberi yorumu) | 1.31M | 53K | 193 | 4.05 | 0.015 | 32 | TR güncel | anonim | O0 | D0 | 0.12 |
| 8 | 2023-12-25 | Kırkağaç olayı (1996) | 11.36M | 177K | 1.733 | 1.56 | 0.015 | 12 | TR suç/facia | isimli gerçek kişi | O1 | D1 | 1.12 |
| 9 | 2023-12-27 | Davutlu köyü cinleri | 11.20M | 256K | 2.660 | 2.28 | 0.024 | 14 | TR efsane/gizem | mekân | O1 | D1 | 1.11 |
| 10 | 2023-12-29 | Engin Arık / Isparta uçağı | 11.10M | 344K | 1.796 | 3.10 | 0.016 | 14 | TR efsane/gizem | isimli gerçek kişi | O1 | D1 | 0.98 |
| 11 | 2024-01-02 | Pippa Bacca (Gebze) | 9.11M | 138K | 1.484 | 1.52 | 0.016 | 14 | TR suç/facia | isimli gerçek kişi | O1 | D1 | 0.81 |
| 12 | 2024-01-04 | Tarsus gizemli kazı | 17.84M | 359K | 2.088 | 2.01 | 0.012 | 14 | TR efsane/gizem | mekân | O1 | D1 | 1.60 |
| 13 | 2024-01-08 | 129 nolu apartman | 20.20M | 395K | 2.656 | 1.96 | 0.013 | 11 | TR efsane/gizem | mekân | O1 | D1 | 1.91 |
| 14 | 2024-01-10 | İstanbul kesik bacak cinayetleri | 9.11M | 123K | 1.372 | 1.35 | 0.015 | 13 | TR suç/facia | anonim | O1 | D1 | 0.61 |
| 15 | 2024-01-12 | Epstein adası | 11.99M | 183K | 1.814 | 1.53 | 0.015 | 13 | Yabancı suç/facia | isimli gerçek kişi | O1 | D1 | 0.81 |
| 16 | 2024-01-14 | Issız Cuma mezarlığı | 22.23M | 386K | 2.045 | 1.74 | 0.009 | 14 | TR efsane/gizem | mekân | O1 | D1 | 1.86 |
| 17 | 2024-01-16 | NY sinagog altı tünel | 4.03M | 58K | 505 | 1.44 | 0.013 | 12 | Yabancı gizem | mekân | O1 | D1 | 0.34 |
| 18 | 2024-01-18 | Kapalak kızı | 17.67M | 307K | 2.344 | 1.74 | 0.013 | 13 | TR efsane/gizem | efsane kişi | O1 | D1 | 1.48 |
| 19 | 2024-01-20 | Malatya kutsal balıklar | 11.94M | 180K | 1.354 | 1.51 | 0.011 | 13 | TR efsane/gizem | mekân | O1 | D1 | 0.64 |
| 20 | 2024-01-22 | Çivici katil Süleyman Aktaş | 5.64M | 98K | 734 | 1.74 | 0.013 | 14 | TR suç/facia | isimli gerçek kişi | O1 | D1 | 0.38 |
| 21 | 2024-01-24 | Havran mağarası | 19.93M | 313K | 2.946 | 1.57 | 0.015 | 14 | TR efsane/gizem | mekân | O1 | D1 | 1.84 |
| 22 | 2024-01-26 | Sakarya kezzap faciası | 28.09M | 617K | 1.979 | 2.20 | 0.007 | 14 | TR suç/facia | anonim | O1 | D1 | 1.92 |
| 23 | 2024-01-30 | Hacda kaybolan Fahire Kara | 9.70M | 101K | 1.338 | 1.04 | 0.014 | 14 | TR suç/facia | isimli gerçek kişi | O1 | D1 | 0.57 |
| 24 | 2024-02-01 | Pegasus kargo "yardım edin" sesi | 17.25M | 268K | 1.191 | 1.55 | 0.007 | 13 | TR güncel | anonim | O1 | D1 | 1.18 |
| 25 | 2024-02-05 | Bitlisli Belkıs | 12.83M | 192K | 1.290 | 1.49 | 0.010 | 14 | TR efsane/gizem | efsane kişi | O1 | D1 | 1.18 |
| 26 | 2024-02-07 | Depremde 4 yıl önce ölen anne | 16.53M | 576K | 3.261 | 3.48 | 0.020 | 14 | TR deprem mucize | anonim | O1 | D1 | 1.77 |
| 27 | 2024-02-09 | Enkazda "abla" (4 yaşındaki Ayşe) | 12.01M | 401K | 2.859 | 3.34 | 0.024 | 14 | TR deprem mucize | anonim | O1 | D1 | 1.90 |
| 28 | 2024-02-11 | Mızrap (oğlunu kurban eden baba) | 3.34M | 51K | 932 | 1.54 | 0.028 | 14 | TR suç/facia | isimli gerçek kişi | O1 | D1 | 0.36 |
| 29 | 2024-02-13 | Taured'li adam | 6.69M | 106K | 559 | 1.58 | 0.008 | 14 | Yabancı gizem | anonim | O1 | D1 | 0.75 |
| 30 | 2024-02-15 | Erzincan İliç madeni | 5.93M | 102K | 461 | 1.71 | 0.008 | 14 | TR güncel | anonim | O1 | D1 | 1.18 |
| 31 | 2024-02-17 | Molla Zeyrek ahırı | 2.88M | 37K | 162 | 1.29 | 0.006 | 14 | TR efsane/gizem | mekân | O1 | D1 | 0.46 |
| 32 | 2024-02-19 | Annesi erkek çıkan kız (Şükran Aktaş) | 17.45M | 280K | 946 | 1.61 | 0.005 | 14 | Tuhaf gerçek (TR) | isimli gerçek kişi | O1 | D1 | 3.76 |
| 33 | 2024-02-21 | Kore'de Ayla | 2.87M | 109K | 569 | 3.78 | 0.020 | 20 | TR dokunaklı | isimli gerçek kişi | O2 | D2 | 0.46 |
| 34 | 2024-02-27 | Bekir Çınar | 7.31M | 174K | – | 2.37 | – | 14 | TR dokunaklı | isimli gerçek kişi | O1 | D2 | 2.10 |
| 35 | 2024-02-29 | Challenger faciası | 4.09M | 74K | 456 | 1.80 | 0.011 | 14 | Yabancı suç/facia | isimli gerçek kişi | O1 | D2 | 0.81 |
| 36 | 2024-03-04 | Belmez yüzleri | 4.25M | 58K | 398 | 1.35 | 0.009 | 13 | Yabancı gizem | mekân | O1 | D2 | 0.64 |
| 37 | 2024-03-05 | Son Berberi aslanı | 2.08M | 54K | 418 | 2.62 | 0.020 | 61 | Tuhaf gerçek | hayvan | X | D2 | 0.31 |
| 38 | 2024-03-08 | Usta Mediha (8 Mart) | 5.88M | 275K | 785 | 4.68 | 0.013 | 17 | TR dokunaklı | isimli gerçek kişi | O2 | D2 | 0.93 |
| 39 | 2024-03-10 | Depremden 2 saat önce eşini kovan adam | 27.53M | 584K | 2.356 | 2.12 | 0.009 | 14 | TR deprem | isimli gerçek kişi | O1 | D2 | 5.44 |
| 40 | 2024-03-12 | Afyon'da yol ortasındaki türbe | 11.29M | 169K | 802 | 1.50 | 0.007 | 14 | TR efsane/gizem | mekân | O1 | D2 | 1.69 |
| 41 | 2024-03-14 | Mariana Çukuru'na düşen Türk | 8.38M | 159K | 955 | 1.90 | 0.011 | 14 | Tuhaf gerçek (TR) | isimli gerçek kişi | O1 | D2 | 1.25 |
| 42 | 2024-03-16 | Türk reenkarnasyon vakası | 3.94M | 69K | 374 | 1.75 | 0.009 | 14 | TR efsane/gizem | isimli gerçek kişi | O1 | D2 | 0.50 |
| 43 | 2024-03-18 | Annesinin kafasını tencereye koyan kadın | 7.49M | 69K | 1.117 | 0.93 | 0.015 | 14 | TR suç/facia | isimli gerçek kişi | O1 | D2 | 1.61 |
| 44 | 2024-03-22 | Ölümünden sonra çiçek gönderen John | 4.90M | 304K | 517 | 6.20 | 0.011 | 22 | Yabancı dokunaklı | isimli gerçek kişi | O2 | D3 | 1.18 |
| 45 | 2024-03-24 | Boston pekmez tsunamisi | 3.14M | 46K | 292 | 1.48 | 0.009 | 11 | Tuhaf gerçek | mekân | O1 | D3 | 0.75 |
| 46 | 2024-03-26 | Titu reenkarnasyonu | 4.38M | 84K | 550 | 1.91 | 0.013 | 22 | Yabancı gizem | isimli gerçek kişi | O2 | D3 | 1.24 |
| 47 | 2024-03-30 | Jadav Payeng | 2.28M | 95K | 250 | 4.16 | 0.011 | 15 | Yabancı dokunaklı | isimli gerçek kişi | O2 | D3 | 0.49 |
| 48 | 2024-04-01 | 1958'den gelen Sergei | 2.64M | 69K | 392 | 2.61 | 0.015 | 18 | Yabancı gizem | isimli gerçek kişi | O2 | D3 | 0.57 |
| 49 | 2024-04-05 | Üç Harfliler: Nazar (#işbirliği) | 6.61M | 93K | 703 | 1.41 | 0.011 | 17 | Other (reklam) | efsane kişi | O2 | D3 | 1.83 |
| 50 | 2024-04-07 | Sumitra | 8.70M | 141K | 665 | 1.62 | 0.008 | 23 | Yabancı gizem | isimli gerçek kişi | O2 | D3 | 2.29 |
| 51 | 2024-04-11 | Likai (kızını yiyen anne) | 17.06M | 328K | 1.746 | 1.92 | 0.010 | 17 | Yabancı gizem | efsane kişi | O2 | D3 | 4.49 |
| 52 | 2024-04-13 | Khait dağı perileri | 2.86M | 43K | 220 | 1.50 | 0.008 | 14 | Yabancı gizem | mekân | O1 | D3 | 0.50 |
| 53 | 2024-04-15 | Pollock ikizleri | 4.74M | 115K | 392 | 2.42 | 0.008 | 20 | Yabancı gizem | isimli gerçek kişi | O2 | D3 | 1.00 |
| 54 | 2024-05-03 | Mitesh Patel | 2.18M | 25K | 347 | 1.14 | 0.016 | 20 | Yabancı suç/facia | isimli gerçek kişi | R | D4 | 1.43 |
| 55 | 2024-05-06 | Almanya vs Türkiye yemek meme | 1.84M | 62K | 338 | 3.37 | 0.018 | 5 | Other | yok (meme) | R | D4 | 1.09 |
| 56 | 2024-05-08 | "Hiç" meme | 1.07M | 28K | 158 | 2.58 | 0.015 | 10 | Other | yok (meme) | R | D4 | 0.53 |
| 57 | 2024-05-11 | Dorothy Eady | 3.14M | 81K | 451 | 2.58 | 0.014 | 21 | Yabancı gizem | isimli gerçek kişi | R | D4 | 2.07 |
| 58 | 2024-05-14 | 21 yaşında kadınlar vs erkekler | 3.27M | 171K | 1.270 | 5.22 | 0.039 | 9 | Other | yok (meme) | R | D4 | 2.43 |
| 59 | 2024-05-15 | Kurye Ata Emre Akman | 1.20M | 21K | 428 | 1.75 | 0.036 | 12 | TR güncel | isimli gerçek kişi | R | D4 | 0.72 |
| 60 | 2024-05-22 | 2014 vs 2024 challengeler | 1.49M | 35K | 81 | 2.31 | 0.005 | 4 | Other | yok (meme) | R | D4 | 1.13 |
| 61 | 2024-05-26 | GS vs FB (şampiyonluk günü) | 1.44M | 52K | 1.195 | 3.63 | 0.083 | 9 | Other | yok (meme) | R | D4 | 1.07 |
| 62 | 2024-07-22 | Wade Wilson'a af isteyen kadınlar | 2.19M | 31K | 418 | 1.40 | 0.019 | 13 | Yabancı suç/facia | isimli gerçek kişi | O1 | D5 | 2.36 |
| 63 | 2024-08-27 | Narin Güran kayboldu | 5.68M | 124K | 1.781 | 2.18 | 0.031 | 12 | TR güncel | isimli gerçek kişi | O1 | D5 | 8.03 |
| 64 | 2024-08-29 | "Hayat herkes için aynı değil" meme | 1.16M | 26K | 156 | 2.26 | 0.013 | 21 | Other | yok (meme) | M | D5 | 1.64 |
| 65 | 2024-09-06 | KPSS'ye hazırlanan genç, elektrik çarpması | 2.20M | 34K | 301 | 1.55 | 0.014 | 13 | TR güncel | isimli gerçek kişi | O1 | D5 | 3.02 |
| 66 | 2024-12-13 | Bridger Walker | 2.51M | 215K | 2.261 | 8.57 | 0.090 | 65 | Yabancı dokunaklı | isimli gerçek kişi | H | D5 | 3.55 |
| 67 | 2025-02-04 | Aydın'da erzak kolisini düşüren yaşlı adam | 2.15M | 54K | 910 | 2.51 | 0.042 | 16 | TR güncel | anonim | H | D6 | 3.66 |
| 68 | 2025-03-12 | James Harrison | 6.24M | 401K | 2.253 | 6.42 | 0.036 | 27 | Yabancı dokunaklı | isimli gerçek kişi | H | D6 | 9.01 |
| 69 | 2025-05-26 | Ali Asaf için balonlar | 4.72M | 387K | 1.584 | 8.19 | 0.034 | 27 | TR güncel | isimli gerçek kişi | H | D6 | 6.82 |
| 70 | 2025-08-09 | Hayalet tank | 2.18M | 23K | 193 | 1.04 | 0.009 | 13 | Tuhaf gerçek | nesne | H | D6 | 2.68 |
| 71 | 2025-09-12 | Iryna Zarutska | 3.38M | 50K | 767 | 1.49 | 0.023 | 17 | Yabancı suç/facia | isimli gerçek kişi | H | D6 | 4.16 |
| 72 | 2025-09-26 | Boksör Simiso Buthelezi | 1.04M | 13K | 89 | 1.24 | 0.009 | 14 | Yabancı suç/facia | isimli gerçek kişi | H | D6 | 0.53 |
| 73 | 2025-12-14 | Brandon Swanson | 5.01M | 23K | 299 | 0.46 | 0.006 | 15 | Yabancı gizem | isimli gerçek kişi | AI | D6 | 6.88 |
| 74 | 2025-12-19 | Sessiz ikizler | 1.73M | 8K | 40 | 0.48 | 0.002 | 12 | Yabancı gizem | isimli gerçek kişi | AI | D6 | 2.38 |
| 75 | 2025-12-21 | Yuba County beşlisi | 1.30M | 6K | 45 | 0.45 | 0.003 | 16 | Yabancı gizem | isimli gerçek kişi | AI | D6 | 1.79 |

## 2. Dönemler

| Dönem | Tarih | IG reel | 1M+ | Medyan | 10M+ | Beğeni % (med) | Süre (med, sn) | Yabancı | TR | TR kalıcı konu* | Meme | IG reel/hafta | YT video/hafta | YT medyan |
|---|---|--:|--:|--:|--:|--:|--:|--:|--:|--:|--:|--:|--:|--:|
| D0 Meme/viral | 30 Eyl – 23 Ara 2023 | 11 | 7 | 1.61M | 0 | 3.58 | 14.3 | %0 | %9 | %0 | %91 | 0.9 | 3.6 | 357K |
| **D1 Altın dönem** | **25 Ara 2023 – 19 Şub 2024** | 25 | 25 | **11.94M** | **16** | 1.58 | 14.0 | %12 | %88 | %76 | %0 | 3.1 (2 günde 1) | 3.6 | 805K |
| D2 Erime | 21 Şub – 18 Mar 2024 | 11 | 11 | 5.88M | 2 | 1.90 | 14.1 | %27 | %73 | %36 | %0 | 2.9 | 4.1 | 269K |
| D3 Yabancılaşma | 22 Mar – 15 Nis 2024 | 10 | 10 | 4.56M | 1 | 1.92 | 17.9 | **%90** | %10 | %0 | %10 | 2.8 | 3.6 | 93K |
| D4 Çöküş | 16 Nis – 26 May 2024 | 9 | 8 | 1.49M | 0 | 2.58 | 9.8 | %22 | %11 | %0 | **%67** | 1.4 | 6.5 | 42K |
| *Instagram'da boşluk* | 26 May – 22 Tem 2024 | 0 | – | – | – | – | – | – | – | – | – | 0 | ~3 | ~40K |
| D5 Seyrek gündem | 22 Tem – 17 Ara 2024 | 16 | 5 | 769K | 0 | 1.65 | 13.4 | %19 | %56 | %0 | %25 | 0.5 | 1.8 | 52K |
| D6 Seyrek dönüş | 16 Oca 2025 – 6 Haz 2026 | 23 | 9 | 588K | 0 | 1.49 | 16.4 | %61 | %26 | %4 | %17 | **0.3** | 0.3 | 99K |

\*TR kalıcı konu: Türkiye efsane/gizem, Türkiye gerçek suç/facia ve Türkiye deprem kategorileri.

Dönem sınırları şöyle:
- **Altın dönem:** 25 Aralık 2023 – 19 Şubat 2024. 57 gün, 25 reel, 16'sı 10M+. Paylaşımlar istisnasız 2 günde bir, 20:10–20:17 arasında (TR saati).
- **Düşüş:** 21 Şubat – 26 Mayıs 2024, üç basamakta. Medyan önce 5.9M'ye, sonra 4.6M'ye, sonra 1.5M'ye indi. Ardından Instagram'da 57 gün hiç reel yok.
- **Düşüş sonrası:** 22 Temmuz 2024'ten bugüne. Medyan 0.6–0.8M; seyrek ve tek tük hit.

**Format kayması (ölçülen):**

| Dönem | Süre (med, sn) | 16 sn üstü | Diyalog tam 280–1000 kare | Son görsel kareden taşıyor | Karenin altı aktif (reaction) | Lisanslı "slowed" müzik |
|---|--:|--:|--:|--:|--:|--:|
| D1 | 14.0 | %0 | %88 | %8 | %0 | 0/25 |
| D2 | 14.1 | %27 | %82 | %18 | %9 | 1/11 |
| D3 | 17.9 | %70 | %70 | %40 | %0 | 5/10 |
| D4 | 9.8 | %25 | %12 | %75 | **%100** | 1/8 |
| D5 | 13.4 | %40 | %40 | %40 | %20 | 0 |
| D6 | 16.4 | %56 | %67 | %33 | %0 | 0 |

Son 3 video (Aralık 2025) yapay zekâ çizimine geçti: çok satırlı sol-üst metin, sahte REC efekti. Bu üçünde beğeni oranı %0.45–0.48'e düştü; diğer dönemlerde bu oran %1.5–8.6 arası.

**Düşüşün kanıtla açıklaması (önem sırasıyla):**

1. **Konu kaynağı değişti.**
   - Türkiye'nin kalıcı efsane/suç konularının payı D1'de %76 iken D2'de %36'ya, D3'te %0'a indi.
   - Son Türkiye efsanesi 16 Mart 2024'te paylaşıldı. Ondan bir önceki (Afyon türbesi, 12 Mart) bile hâlâ 11.3M aldı.
   - Bu en iyi kategori bir daha hiç denenmedi.
   - Aynı format ve aynı sıklıkla D1–D3'te: Türkiye medyanı 11.2M (31 reel, 17'si 10M+), yabancı medyanı 4.25M (15 reel, 2'si 10M+). Göreli performans Türkiye için 1.34, yabancı için 0.72.
2. **D1'den D2'ye ilk düşüş formatla ya da sıklıkla açıklanmıyor.** İkisi de değişmedi (14 sn, 2 günde 1), ama izlenme yarıya indi. Bu ya konu kalitesindeki düşüşü ya da format yeniliğinin aşınmasını gösteriyor; veriden ikisini ayıramıyorum. YouTube'da aynı düşüş daha sertti (805K → 269K).
3. **Format kayması D3–D4'te geldi.**
   - D1–D3'te süre ile izlenme arasındaki sıra korelasyonu (Spearman) −0.37: uzun videolar daha kötü yaptı.
   - D4'te reellerin %67'si meme/"vs" ve %100'ünde reaction kamerası vardı. Aynı dönemde YouTube medyanı 42K'ya düştü.
4. **Ritim çöktü.**
   - 15 Nisan 2024'e kadar 2 günde bir paylaşılıyordu. Sonra 18 ve 57 günlük boşluklar geldi. 2025–2026'da haftada 0.3 reel (iki paylaşım arası medyan 15.5 gün).
   - Hit'lerin ardından ivme boşa gitti: Harrison (6.24M) sonrası 73 gün, Ali Asaf (4.72M) sonrası 31 gün, Iryna (3.38M) üç hafta içinde iki zayıf paylaşımın ardından 79 gün boşluk.

## 3. Güncel olaylar: olay tarihi, gecikme ve izlenme

Gecikme = paylaşım tarihi − olay tarihi (veya haberin son dalga tarihi). Kaynak sütunu tarihin nereden geldiğini gösteriyor; "web" işaretlileri web aramasıyla doğruladım.

| Paylaşım | Konu | Olay | Haber dalgası | Gecikme (olay) | Gecikme (dalga) | İzlenme | Göreli | Kaynak |
|---|---|---|---|--:|--:|--:|--:|---|
| 2023-10-16 | "Kudüs" meme | 7 Eki 2023 | 7 Eki | 9 | 9 | 2.89M | 0.85 | genel bilgi |
| 2023-12-23 | "45 saniye" | 22 Ara 2023 | 23 Ara (12 şehit) | 1 | 0 | 1.31M | 0.12 | web |
| 2024-01-12 | Epstein | – | 3 Oca 2024 (belgeler açıldı) | – | 9 | 11.99M | 0.81 | genel bilgi |
| 2024-01-16 | Sinagog tüneli | 8 Oca 2024 | 8 Oca | 8 | 8 | 4.03M | 0.34 | web |
| 2024-02-01 | Pegasus | 28 Oca 2024 | 28 Oca | 4 | 4 | **17.25M** | 1.18 | açıklama |
| 2024-02-07 | Deprem: ölmüş anne | 6 Şub 2023 | 6 Şub 2024 (1. yıldönümü) | 366 | 1 | **16.53M** | 1.77 | açıklama + takvim |
| 2024-02-09 | Deprem: "abla" | 6 Şub 2023 | 1. yıldönümü | 368 | 3 | **12.01M** | 1.90 | açıklama + takvim |
| 2024-02-15 | Erzincan İliç | 13 Şub 2024 | 13 Şub | 2 | 2 | 5.93M | 1.18 | açıklama |
| 2024-03-08 | Usta Mediha | – | 8 Mart (takvim) | – | 0 | 5.88M | 0.93 | açıklama |
| 2024-03-10 | Eşini kovan adam (deprem) | 6 Şub 2023 | Mart 2023 haberi | 398 | ~375 | **27.53M** | 5.44 | web |
| 2024-04-05 | Nazar (sponsorlu) | 10 Nis vizyon | – | −5 | −5 | 6.61M | 1.83 | açıklama |
| 2024-05-15 | Ata Emre Akman | 11 May 2024 | 11 May | 4 | 4 | 1.20M | 0.72 | açıklama |
| 2024-05-26 | GS vs FB meme | 26 May 2024 | 26 May | 0 | 0 | 1.44M | 1.07 | genel bilgi |
| 2024-07-22 | Wade Wilson | 27 Haz 2024 (mahkûmiyet) | ~15 Tem (mektup haberleri; duruşma 23 Tem) | 25 | ~7 | 2.19M | 2.36 | açıklama + web |
| 2024-08-17 | İzmir yangını | 13 Ağu | 16 Ağu | 4 | 1 | 690K | 0.73 | web |
| 2024-08-27 | Narin Güran | 21 Ağu 2024 | 21 Ağu | 6 | 6 | **5.68M** | **8.03** | açıklama |
| 2024-09-06 | KPSS/elektrik | ~2 Ağu 2024 | 3 Ağu | 35 | 34 | 2.20M | 3.02 | web |
| 2024-10-30 | Yenidoğan Çetesi | 16 Eki | 18 Eki (iddianame) | 14 | 12 | 806K | 1.20 | web |
| 2024-11-19 | İzmir'de 5 kardeş | 11 Kas | 11 Kas | 8 | 8 | 608K | 0.87 | web |
| 2025-01-19 | Eslem (köpek saldırısı) | 18 Oca 2025 | 18 Oca | 1 | 1 | 814K | 1.39 | web |
| 2025-02-04 | Aydın erzak kolisi | 4 Şub 2025 | 4 Şub | 0 | 0 | 2.15M | 3.66 | web |
| 2025-02-06 | Deprem: Elif'in mesajları | 6 Şub 2023 | 2. yıldönümü | 731 | 0 | 480K | 0.68 | takvim |
| 2025-03-12 | James Harrison | 17 Şub 2025 (ölüm) | 3 Mar (duyuru) | 23 | 9 | **6.24M** | **9.01** | açıklama + web |
| 2025-05-26 | Ali Asaf | 25 May 2025 | 25 May | 1 | 1 | **4.72M** | 6.82 | açıklama |
| 2025-06-26 | Savan Günay | – | 15 Haz 2025 | – | 11 | 427K | 0.29 | web |
| 2025-09-12 | Iryna Zarutska | 22 Ağu 2025 | 5 Eyl (video yayını) | 21 | 7 | 3.38M | 4.16 | açıklama + web |
| 2025-09-26 | Boksör Simiso | 5 Haz 2022 | – | 1209 | – | 1.04M | 0.53 | açıklama |
| 2026-01-25 | Nihilist penguen | 16 Oca 2026 | 23 Oca | 9 | 2 | 412K | 0.51 | web |
| 2026-05-14 | Hantavirüs | ~2 May 2026 | ~6 May | 12 | ~8 | 276K | 0.93 | web |

Doğrulayamadıklarım: hayalet tank videosunun yayılma tarihi, "dedesini öldüren 16 yaşındaki genç", "pilot", "öğretmen" ve Buca'daki evsiz haberinin tarihi.

**Gecikmeye göre gruplar (haber dalgasına göre):**

| Gecikme | Reel | Medyan izlenme | Göreli (med) |
|---|--:|--:|--:|
| 0–2 gün | 11 | 1.44M | 1.07 |
| **3–6 gün** | 4 | **8.85M** | **1.54** |
| 7–14 gün | 10 | 2.54M | 0.90 |
| 30 gün üstü (eski ama güçlü haber) | 3 | 2.20M | 3.02 |

- Hız tek başına hit yaratmıyor. En iyi pencere, olay ya da yeni haber dalgasından **1–6 gün sonrası**.
- Bu pencerede başarılı olanların hepsinde ya gizem/mucize açısı ya da tek isimli masum kurban/kahraman var.
- Yeni bir dalga (belgeler açıldı, video yayınlandı, ölüm duyuruldu, yıldönümü) eski bir olayı da güncel yapıyor: Epstein, Harrison, Iryna ve deprem yıldönümü örnekleri.
- Tutmayanlar: tek yüzü olmayan kurumsal/sistemik haberler (Yenidoğan, 5 kardeş), komplo kokulu şüpheli ölüm (Savan Günay) ve küresel sağlık haberi (hantavirüs).

## 4. Düşüş sonrası 1M+ hit'ler (Haziran 2024 sonrası 14 reel)

Hit'ler: Wade Wilson 2.19M, Narin 5.68M, meme 1.16M, KPSS 2.20M, Bridger 2.51M, Aydın 2.15M, Harrison 6.24M, Ali Asaf 4.72M, tank 2.18M, Iryna 3.38M, Simiso 1.04M, Brandon 5.01M, ikizler 1.73M, Yuba 1.30M.

Ortak noktaları:
- **Kahraman:** 11/14'ünde isimli gerçek kişi var. Aynı dönemde 1M'yi geçemeyen 25 reelde bu oran 6/25.
- **Duygu:** 7/14 masum kurban, çocuk ya da iyilik kahramanı (Narin, Bridger, Ali Asaf, Iryna, KPSS'li genç, Aydın'daki yaşlı adam, Harrison). En yüksek beğeni oranları bunlarda: %6.4–8.6.
- **Görüntü:** 10/14'ü kişinin ya da olayın gerçek video/fotoğrafıyla bitiyor (H formatı, göreli performans medyanı 4.9). Süre 12–27 sn; tek istisna Bridger (65 sn).
- **Zamanlama:** 6/14'ü haber dalgasından 0–9 gün sonra paylaşılmış.
- **Konu yelpazesi:** hiçbiri Türkiye efsanesi değil, çünkü bu kategori hiç denenmedi. 9/14'ü yabancı. Yabancı konular ancak küresel bir dalga varsa (Harrison, Iryna, Wade) ya da yapay zekâ ile yapılan "kayıp gizemi" serisinde tuttu. O serinin beğeni oranı %0.45: izlendi ama bağ kurmadı, dördüncüsü 292K'da kaldı.
- **Tutmayanlar:** meme'ler ("Erkeklerin de duyguları vardır"), kurumsal Türkiye haberleri ve haber kancası olmayan yabancı dokunaklı/gizem konuları (pilot 199K, Salk 300K, Jamison 292K).

## 5. Konu içgörüleri

**İzlenme bandına göre türler:**
- **10M+ (19 reel), 17'si Türkiye'de geçiyor:**
  - 10 Türkiye efsane/gizem: Issız Cuma mezarlığı, 129 nolu apartman, Havran mağarası, Tarsus kazısı, Kapalak kızı, Bitlisli Belkıs, Malatya kutsal balıkları, Afyon türbesi, Davutlu köyü, Engin Arık.
  - 3 deprem: eşini kovan adam, ölmüş anne, "abla".
  - 2 Türkiye suç/facia: kezzap, Kırkağaç.
  - Pegasus ve Şükran Aktaş.
  - Yabancı yalnızca 2 tane: Epstein (küresel haber dalgası) ve Likai (Kırkağaç tipi yamyamlık dönüşü).
  - Ortak şablon: **Türkiye'de gösterilebilir bir mekân + doğaüstü ya da açıklanamayan bir şey + tek cümlelik dehşet/mucize dönüşü.**
- **5–10M (17 reel):** Türkiye gerçek suçları (Fahire Kara, kesik bacak, Pippa Bacca, Çivici, Tuğçe Sayın), Türkiye dokunaklı (Bekir Çınar, Usta Mediha), Mariana, güncel Türkiye (Erzincan, Narin), en güçlü yabancı gizemler (Sumitra, Taured), Harrison, Brandon (yapay zekâ) ve 2 meme.
- **3–5M (14 reel), 9'u yabancı:** reenkarnasyon vakaları (Pollock, Titu, Dorothy), Belmez, Challenger, sinagog, John & Diana, Ali Asaf, Iryna.
- **1–3M (25 reel):** meme'ler (8), reaction formatındaki içerik, zayıf mekân/peri konuları (Molla Zeyrek, Khait), dokunaklı yabancı konular (Jadav, Bridger) ve 2025 dönemi.

**Türkiye vs yabancı:**

| Kapsam | Türkiye medyanı | Yabancı medyanı |
|---|--:|--:|
| Aynı format ve sıklıkla (D1–D3) | 11.2M | 4.25M (2.6 kat düşük) |
| Tüm dönemler | 6.27M | 2.57M |

Yabancı konular Instagram'da YouTube'dan daha iyi taşındı: D3'te Instagram/YouTube oranı 38 kat. Ama tavanları yine de düşük kaldı.

**Kahramanın türü (D1–D3):**

| Kahraman | Reel | Medyan |
|---|--:|--:|
| Efsane kişi | 3 | 17.1M |
| Anonim kurban | 7 | 12.0M |
| Mekân | 12 | 11.3M |
| İsimli gerçek kişi | 22 | 6.6M |

- İsimli gerçek kişi ancak şok edici bir dönüş varsa (Şükran Aktaş 17.45M, eşini kovan adam 27.5M) ya da güncel bir dalga varsa 10M'ye yaklaşıyor.
- Düşüş sonrasında ise tersine döndü: hit'lerin çoğu isimli masum kurban ya da kahraman.

**Beğeni ve yorum oranları:**
- Bu oranlar erişimi öngörmüyor. D1–D3'te Spearman korelasyonu: beğeni%–izlenme −0.01, yorum%–izlenme −0.10.
- 10M+ efsane/suç videolarının beğeni oranı yalnızca %1.5–2.3. Dokunaklı/iyilik videoları %4–8.6 beğeni alıyor ama 2–6M'de kalıyor.
- Yorum oranı en yüksek: meme/kutuplaşma içerikleri (sevgili skeci %0.17, "Kudüs" %0.11, GS-FB %0.08) ve tartışmalı güncel Türkiye olayları (Eslem %0.10, Aydın %0.04).

## 6. Konu seçimi ve zamanlama için 10 kural

1. **Ana damar Türkiye'nin kalıcı gizemleri.** Köy, mezarlık, mağara, apartman, türbe, define kazısı gibi Türkiye'de gösterilebilir bir yerde geçen efsane/gizem/tuhaf ölüm konuları akışın en az %60'ı olsun. Bu kategoride 12 reelin 10'u 10M+ yaptı ve kategori Mart 2024'ten beri hiç denenmedi.
2. **Her konu 8 kelimelik bir dönüş testinden geçsin.** Konu, "tüyler ürperten" ya da "mucize" denebilecek tek cümleye inebilmeli: "eti lokantada servis edildi", "ölmüş anne çocuklarının yerini gösterdi", "annesi erkek çıktı". İnmiyorsa çekme.
3. **Yabancı konu en fazla 4'te 1 olsun** ve iki koşuldan birini taşısın:
   - O hafta küresel bir haber dalgası olsun (Epstein, Harrison, Iryna).
   - Kırkağaç seviyesinde bir dönüşü olsun (Likai).

   Sıradan reenkarnasyon, peri ve paranormal ev konularının tavanı 2–5M.
4. **Güncel Türkiye olayını 1–6 gün içinde paylaş;** tek isimli masum kurban ya da tek sahnelik bir gizem olsun (Pegasus 4 gün 17.3M, Narin 6 gün 5.7M, Ali Asaf 1 gün 4.7M). 7 gün geçtiyse ancak yeni bir dalga varsa paylaş (video yayınlandı, ölüm duyuruldu, iddianame çıktı). Tek yüzü olmayan kurumsal/sistemik haberlere girme.
5. **Takvim kancalarını önceden planla.** Örnekler: 6 Şubat deprem yıldönümü (1–3 gün içinde 16.5M ve 12.0M), 8 Mart, kurban/adak tarihleri, film vizyonları. Yıldönümünde konu yasın kendisi değil, "mucize" ya da "ironik kader" anısı olsun.
6. **Tazelik şart değil, güçlü kader ironisi şart.** Bir yıllık deprem haberi 27.5M, 34 günlük KPSS haberi 2.2M aldı. Gündem zayıfsa bekleme; 1. kuraldaki Türkiye efsanesini çek.
7. **Ritim 2 günde 1, sabit saat 20:00–20:15 (TR).** Altın dönemde 25 reelin hepsi bu düzende paylaşıldı. Bir hit gelirse 7 gün içinde aynı damardan 2–3 video daha çıkar. Hit'ten sonra 31–79 günlük boşluk bırakmak ivmeyi öldürüyor.
8. **Format sabit kalsın.** Altın dönemdeki gibi 11–15 sn ve 720×720 kare: gerçek mekân fotoğrafı, wojak, tek satır ortalı replik, sonda kareye sığan gerçek fotoğraf ya da haber kupürü. Şunlar düşüşle birlikte geldi, yapma:
   - 16 sn üstü süre (D1–D3'te süre–izlenme korelasyonu −0.37)
   - lisanslı "slowed" müzik
   - reaction kamera
   - meme veya "vs" araya karışması
   - yapay zekâ çizimi sahne ve çok satırlı sol-üst metin (beğeni %0.45)

   Güncel olayda sona gerçek görüntü koymak tek olumlu istisna.
9. **Kahramanı türüne göre seç.**
   - Kalıcı konuda: efsane kişi, mekân ya da anonim kurban (medyan 11–17M).
   - Güncel konuda: isimli masum çocuk/genç ya da iyilik kahramanı (beğeni %6–8.6).
   - İsimli fail veya sıradan isimli kişi 3–7M'de kalıyor. Yargısı sürmekte olan şüpheliyi çizme.
10. **Karar ölçütü izlenme ve göreli performans olsun, beğeni değil.** Beğeni ve yorum oranlarının erişimle korelasyonu yaklaşık sıfır. Meme, skeç ve sponsorlu içerik ana akışın en fazla ayda 1'i olsun: D4'te reellerin %67'si meme'ydi, Instagram medyanı 1.5M'ye, YouTube medyanı 42K'ya düştü.

---

**Kaynaklar (web ile doğrulanan tarihler):**
- [Takvim – KPSS/elektrik (3 Ağu 2024)](https://www.takvim.com.tr/yasam/2024/08/03/kpssye-girmek-icin-ders-calisiyordu-elektrik-akimina-kapilip-can-verdi)
- [Halk TV – Aydın erzak](https://halktv.com.tr/turkiye/sokaktaki-goruntuleri-yurek-burkan-yurttas-icin-yeni-gelisme-911440h)
- [Hürriyet – Malatya'da eşini kovan adam](https://www.hurriyet.com.tr/gundem/malatyada-depremden-2-saat-once-evden-kovdugu-esi-ve-kizi-hayatta-kaldi-42235699)
- [Takvim – Tuğçe Sayın kararı (2022)](https://www.takvim.com.tr/yasam/2022/09/21/kan-donduran-cinayette-karar-cikti-annesini-satirla-oldurup-kafasini-kesmisti)
- [AOL – Wade Wilson mektupları](https://www.aol.com/news/judge-gets-mail-women-begging-185815865.html)
- [Fox19 – Iryna videosu (8 Eyl 2025)](https://www.fox19.com/2025/09/08/graphic-video-shows-moment-ukrainian-refugee-stabbed-death-by-man-light-rail-train-charlotte/)
- [WFAE – James Harrison (3 Mar 2025)](https://www.wfae.org/obituaries/2025-03-03/james-harrison-whose-blood-donations-saved-over-2-million-babies-has-died)
- [Medyascope – Yenidoğan Çetesi (18 Eki 2024)](https://medyascope.tv/2024/10/18/adalet-bakani-tunctan-yenidogan-cetesi-aciklamasi-22-supheli-tutuklandi/)
- [BirGün – İzmir'de 5 kardeş](https://www.birgun.net/haber/izmir-de-soba-faciasinda-olen-bes-kardes-defnedildi-helallik-alinmadi-575282)
- [Habertürk – Eslem Teker](https://www.haberturk.com/eslem-teker-12-yasinda-oldu-sokak-kopekleri-barinaga-goturuldu-3757602)
- [İşçi Haber – Savan Günay (15 Haz 2025)](https://www.iscihaber.net/gundem/kanserin-cozumunu-buldum-demisti-doktor-savan-gunay-evinde-olu-bulundu/164552)
- [Al Jazeera – Bondi (14 Ara 2025)](https://www.aljazeera.com/video/newsfeed/2025/12/15/what-we-know-about-the-bondi-hero-at-australia-beach-shooting)
- [Medyascope – Pençe-Kilit şehitleri (23 Ara 2023)](https://medyascope.tv/2023/12/23/kuzey-irakta-alti-asker-sehit-oldu/)
- [Habertürk – İzmir yangını (16 Ağu 2024)](https://www.haberturk.com/izmir-yangin-son-dakika-16-agustos-2024-izmir-orman-yangini-son-durum-nedir-devam-ediyor-mu-sonduruldu-mu-yanginin-cikis-nedeni-ne-3712100)
- [Know Your Meme – Nihilist penguen](https://amp.knowyourmeme.com/memes/penguin-walking-toward-mountain-nihilist-penguin)
- [Bianet – Hantavirüs](https://bianet.org/haber/10-soruda-hantavirus-hakkinda-bilinenler-319442)
- [Global News – Chabad tüneli](https://globalnews.ca/news/10218611/secret-tunnel-nyc-synagogue-chabad-lubavitcher)