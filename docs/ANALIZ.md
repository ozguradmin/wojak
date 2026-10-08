# Veri Analizi — @tarihselwojak (YouTube Shorts kopyası)

Kaynak: YouTube @tarihselwojak kanalındaki 223 short (Instagram'daki videolarla aynı). 223 videonun tam
metadata'sı alındı; 3 reklam videosu hariç **220 video** analiz edildi.
Tarih: 2026-10-08. Ham veri: [`data/videos.csv`](../data/videos.csv). Yeniden üretmek için:
`python tools/yt_arastir.py liste && python tools/yt_arastir.py detay && python tools/analiz.py`.

> YouTube izlenmeleri Instagram'dakinin aynısı değil ama **göreli** performansı (hangi dönem/format
> daha iyi) güvenilir şekilde gösteriyor. Instagram verisi için `tools/ig_fetch.py` (çerez gerekir).

## Ana bulgular

1. **Altın dönem (10 Ara 2023 – 6 Mar 2024) tartışmasız en iyi dönem:** 47 videonun medyanı **705K**,
   %62'si 500K üstü. Sonraki dönemin medyanı **54K** (13 kat düşüş).
2. **Dönem 2'deki dev rakamlar (6.5M, 4.2M, 3.8M) ödünç içerik:** "Low Budget Stories" çevirileri ve
   WTFCEVIRI split-screen'leri (55-60 sn). Hesabı ilk büyüten bunlar ama kanalın kendi formatı değil
   ve tekrarlanabilir değil. Kendi formatının (olay) medyanı dönem 2'den (331K) 2 kat yüksek.
3. **Süre:** kanalın kendi formatında en iyi bant **11-15 sn** (altın dönem medyanı 14 sn).
4. **"Olayı yorumlara yazdım" ibaresi tek başına fark yaratmıyor** (ibareli 538K, ibaresiz aynı dönem
   658K). Önemli olan sabit yorumun **varlığı**, başlıktaki ibare değil.
5. **Saat:** 17:00-21:00 TR paylaşımları belirgin şekilde daha iyi; altın dönem içinde bile 21:00
   sonrası paylaşımlar medyanda ~%35 geride (519K'ya karşı 729-812K).
6. **Sıklık çöktü:** altın dönemde haftada 3.8 video; 2025-26'da haftada 0.3 (ayda ~1). 2026'da 4 ayda
   2 video ve izlenmeler 12-14K.
7. **2025 dönüşü yarım kaldı:** format geri geldi ama replikler uzun anlatı metnine dönüştü
   (4-5 satır, sola yaslı, farklı font), sahneler yapay zekâ ile üretildi, konular az bilinen yabancı
   vakalara kaydı. Beğeni/izlenme oranı %3.2'den **%1.3**'e düştü — izleyici bağı zayıfladı.
   İstisna: gündem + güçlü insan hikâyesi (Iryna Zarutska, **1.42M**) hâlâ çalışıyor.
8. **Konu türü (altın dönem, elle etiketlenmiş):** Türkiye'den doğaüstü/efsane/deprem mucizesi
   (~920K medyan) > dokunaklı/fedakârlık (~840K) > ünlü/şok edici suç (~750K) > tuhaf gerçek (~545K)
   > kaza/felaket (~350K). Az bilinen yabancı gizemler 110-260K'da kaldı.

## Dönem tanımları

Kapak kareleri (223 adet) tek tek incelenerek belirlendi:

| Dönem | Görsel dil |
|---|---|
| 1 Tarihsel | 2. Dünya Savaşı fotoğrafı + asker wojak + konuşma balonu |
| 2 Viral repost | "Low Budget Stories / Zero Budget Stories" animasyon çevirileri (kredili), WTFCEVIRI üst + doomer alt split-screen, "Kızlar vs Erkekler" meme'leri |
| 3 OLAY | Gerçek mekân fotoğrafı + benzer wojak + tek satır beyaz italik replik + gerçek fotoğraf kapanışı, 11-15 sn |
| 4 Dağılma | Gerçek haber/video kesitleri, alt köşede yabancı yayıncının reaction kamerası, "vs" meme'leri, WePlay reklamları |
| 5 Dönüş | Olay formatı ama AI ile üretilmiş sahneler, 4-5 satırlık sola yaslı kalın yazı, sahte "REC" kamera efektleri |


## Dönemler

| Dönem | Video | Medyan izlenme | Ortalama | ≥500K oranı | Medyan süre | Beğeni/izlenme |
|---|---:|---:|---:|---:|---:|---:|
| 1-Tarihsel (WW2/Çanakkale wojak) | 6 | 508K | 709K | %50 | 17 sn | %3.8 |
| 2-Viral repost/meme (Low Budget Stories, split-screen) | 30 | 331K | 917K | %40 | 39 sn | %3.7 |
| 3-OLAY altın dönem | 47 | 705K | 788K | %62 | 14 sn | %3.3 |
| 4-Dağılma (gerçek video, reaction, 'vs' meme, reklam) | 115 | 54K | 125K | %7 | 15 sn | %2.9 |
| 5-Olay'a dönüş (uzun yazı, AI sahne, seyrek) | 22 | 96K | 170K | %5 | 16 sn | %1.3 |

### Paylaşım sıklığı (dönem içi)

| Dönem | İlk | Son | Video | Video/hafta |
|---|---|---|---:|---:|
| 1-Tarihsel (WW2/Çanakkale wojak) | 2023-10-19 | 2023-10-24 | 6 | 6.0 |
| 2-Viral repost/meme (Low Budget Stories, split-screen) | 2023-10-25 | 2023-12-08 | 30 | 4.8 |
| 3-OLAY altın dönem | 2023-12-10 | 2024-03-06 | 47 | 3.8 |
| 4-Dağılma (gerçek video, reaction, 'vs' meme, reklam) | 2024-03-08 | 2024-12-17 | 115 | 2.8 |
| 5-Olay'a dönüş (uzun yazı, AI sahne, seyrek) | 2025-01-19 | 2026-05-14 | 22 | 0.3 |

## Süre (tüm dönemler)

| Süre | Video | Medyan izlenme | Ortalama | ≥500K oranı | Medyan süre | Beğeni/izlenme |
|---|---:|---:|---:|---:|---:|---:|
| ≤10 sn | 23 | 75K | 244K | %22 | 7 sn | %3.6 |
| 11-15 sn | 94 | 155K | 406K | %29 | 14 sn | %2.8 |
| 16-30 sn | 69 | 80K | 249K | %16 | 21 sn | %3.2 |
| 31-60 sn | 34 | 128K | 765K | %29 | 60 sn | %3.6 |

## Süre — sadece 2024-03 sonrası (format karışık dönem)

| Süre | Video | Medyan izlenme | Ortalama | ≥500K oranı | Medyan süre | Beğeni/izlenme |
|---|---:|---:|---:|---:|---:|---:|
| ≤15 sn | 71 | 70K | 133K | %7 | 13 sn | %2.4 |
| 16-30 sn | 50 | 59K | 137K | %6 | 21 sn | %2.5 |
| 31-60 sn | 16 | 42K | 115K | %6 | 52 sn | %3.3 |

## Başlıkta 'olayı yorumlara yazdım' tipi ibare

| İbare | Video | Medyan izlenme | Ortalama | ≥500K oranı | Medyan süre | Beğeni/izlenme |
|---|---:|---:|---:|---:|---:|---:|
| Var | 11 | 538K | 748K | %55 | 16 sn | %3.2 |
| Yok (aynı dönem 2023-11-25..2024-03-06) | 46 | 658K | 716K | %57 | 14 sn | %3.4 |

## Paylaşım saati (TR saati, tüm dönemler)

| Saat | Video | Medyan izlenme | Ortalama | ≥500K oranı | Medyan süre | Beğeni/izlenme |
|---|---:|---:|---:|---:|---:|---:|
| 12-17 | 2 | 431K | 431K | %50 | 18 sn | %3.6 |
| 17-21 | 120 | 176K | 495K | %30 | 14 sn | %3.1 |
| 21-24 | 98 | 65K | 272K | %16 | 17 sn | %3.2 |

## Paylaşım saati — sadece altın dönem

| Saat | Video | Medyan izlenme | Ortalama | ≥500K oranı | Medyan süre | Beğeni/izlenme |
|---|---:|---:|---:|---:|---:|---:|
| 17-19 | 16 | 812K | 814K | %56 | 14 sn | %3.5 |
| 19-21 | 22 | 729K | 837K | %68 | 14 sn | %3.2 |
| 21-24 | 9 | 519K | 619K | %56 | 14 sn | %3.3 |

## Paylaşım saati — sadece dağılma dönemi

| Saat | Video | Medyan izlenme | Ortalama | ≥500K oranı | Medyan süre | Beğeni/izlenme |
|---|---:|---:|---:|---:|---:|---:|
| 00-17 | 1 | 770K | 770K | %100 | 10 sn | %4.8 |
| 17-19 | 5 | 231K | 220K | %0 | 17 sn | %4.2 |
| 19-21 | 41 | 61K | 128K | %7 | 14 sn | %2.9 |
| 21-24 | 68 | 48K | 107K | %6 | 16 sn | %2.8 |

## En çok izlenen 25

| # | Tarih | Süre | İzlenme | Beğeni | Dönem | Başlık |
|---:|---|---:|---:|---:|---|---|
| 1 | 2023-11-24 | 55 | 6.52M | 253K | 2 | Kalbiniz yok |
| 2 | 2023-11-11 | 60 | 4.25M | 153K | 2 | Çocuk YouTuber'ların karanlık hayatı |
| 3 | 2023-11-01 | 60 | 3.77M | 136K | 2 | Üniversiteden sonra hayat |
| 4 | 2023-11-05 | 60 | 3.48M | 86K | 2 | Sıradan biriyken kıyafet değişip popüler olmak |
| 5 | 2024-01-12 | 13 | 2.50M | 25K | 3 | Epstein Adası |
| 6 | 2024-03-01 | 11 | 2.43M | 86K | 3 | Sıradan bir kuştan çok daha fazlası… |
| 7 | 2023-10-24 | 45 | 2.35M | 114K | 1 | 29 yıl ormanda yaşayan asker |
| 8 | 2023-12-25 | 12 | 2.06M | 30K | 3 | Kırkağaç olayı (Olayı yorumlara yazdım) 🔞⛔️ |
| 9 | 2024-02-09 | 14 | 1.74M | 62K | 3 | Enkaz altından çıkarılınca yemek yediğini söyleyen 4 yaşındaki kız |
| 10 | 2024-02-07 | 14 | 1.68M | 0 | 3 | 4 yıl önce vefat eden anne 2 çocuğunun yerini söyleyip kurtardı |
| 11 | 2024-02-21 | 20 | 1.48M | 71K | 3 | Kore savaşında ailesini kaybetmiş koreli kızı evlat edinen Türk asker |
| 12 | 2024-01-18 | 13 | 1.43M | 39K | 3 | Kapalak kızı |
| 13 | 2024-01-02 | 14 | 1.43M | 35K | 3 | Gelinlikle dünyayı gezerken Türkiye’de hayatını kaybeden Pippa Bacca ( |
| 14 | 2025-09-12 | 17 | 1.42M | 12K | 5 | Evine giderken trende katledilen Ukraynalı kız |
| 15 | 2023-11-21 | 16 | 1.24M | 51K | 2 | Bir Türk gencinin hayatı |
| 16 | 2024-02-19 | 14 | 1.18M | 31K | 3 | Doğumundan beri yanında olup onu büyüten annesi erkek çıkan kız |
| 17 | 2024-01-30 | 14 | 1.13M | 26K | 3 | Hacda kaybolan kadın: Fahire Kara |
| 18 | 2023-11-25 | 16 | 1.02M | 33K | 2 | Olayı yorumlara yazdım |
| 19 | 2024-02-03 | 14 | 985K | 38K | 3 | Üşümesin diye aldığı ‘müşteri’ tarafından katledilen şoför |
| 20 | 2023-12-14 | 9 | 983K | 31K | 3 | Erkekler sahip olduğu tüm eşyalara değer verir ve sever.. |
| 21 | 2024-01-14 | 14 | 963K | 26K | 3 | Issız cuma mezarlığı |
| 22 | 2024-01-08 | 11 | 951K | 24K | 3 | 129 nolu apartman |
| 23 | 2024-02-05 | 14 | 922K | 26K | 3 | Bitlisli Belkıs |
| 24 | 2023-12-20 | 21 | 887K | 36K | 3 | Milyonlarca insanı kurtarmak için hayatlarını feda eden 3 işçi.. (Olay |
| 25 | 2024-01-28 | 14 | 882K | 30K | 3 | Uruguay 571 sefer sayılı uçuş |

## Son 15 video

| Tarih | Süre | İzlenme | Başlık |
|---|---:|---:|---|
| 2025-06-26 | 13 | 156K | Kanserin çözümünü buldum diyen Türk doktor evinde ölü bulundu |
| 2025-08-09 | 13 | 114K | Etrafında dönen tank |
| 2025-09-04 | 28 | 81K | Ölümünde bile öğrencileri düşünen öğretmen 🫡 |
| 2025-09-12 | 17 | 1.42M | Evine giderken trende katledilen Ukraynalı kız |
| 2025-09-20 | 29 | 79K | Güney Kore’de çocuklarla yaşlılar birlikte okula gidiyor |
| 2025-09-26 | 14 | 383K | Boks maçında hayatını kaybeden boksör |
| 2025-12-14 | 15 | 86K | Karanlıktaki Son Çığlık: Brandon Swanson |
| 2025-12-16 | 18 | 72K | Bondi Plajındaki katliamı durduran kahraman |
| 2025-12-19 | 12 | 171K | Birbirine Kilitli İki Zihin: Silent Twins’in Çözülmeyen Gizemi |
| 2025-12-21 | 16 | 104K | Çalışan Arabayı Terk Edip Ölüme Yürüdüler: Yuba County Beşlisi Gizemi |
| 2025-12-26 | 15 | 105K | Çölde Kaybolan Bir Aile: Jamison Ailesi Vakası |
| 2026-01-11 | 15 | 91K | Öğrencisini Kurtarmak İçin Canını Veren Pilot |
| 2026-01-25 | 18 | 114K | Sürüsünden ayrılıp dağlara gitmeyi tercih eden Penguen |
| 2026-04-28 | 29 | 14K | Çocuk felci açısını bulup para kazanmayı reddeden bilim insanı |
| 2026-05-14 | 24 | 12K | Hantavirüs olayı |
