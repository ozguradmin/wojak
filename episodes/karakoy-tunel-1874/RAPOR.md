# RAPOR: karakoy-tunel-1874 (kısa reel, 14 sn)

**Hassas konu yok, BEKLET yok.** 1874-1875 olayı; çocuk, yakın tarihte ölen, yaşayan özel kişi ya da süren dava yok. Bütün
görseller kamu malı / CC0 / "bilinen telif kısıtlaması yok"; lisans kararı bekleyen görsel yok. İki mercek de 8, MUST yok.

## Konu ve gerekçe

**"Ne?!" cümlesi:** Dünyanın en eski ikinci yeraltı demiryolu İstanbul'daki Tünel'in açılıştan önceki deneme seferlerinde
vagonlarda yolcu yerine hayvan taşındı.

- Türkiye'de, herkesin bildiği bir yerde (Karaköy-Beyoğlu); ironi + ters köşe kalıbına oturuyor ("ilk yolcular hazır" ->
  "ilk yolcular hayvan mı?").
- En az iki bağımsız kaynak: İETT'nin istasyondaki tarihî levhası ve kronolojisi, CNN Türk, Gazete Birlik, TRT Haber, RayHaber
  (Vahdettin Engin'in araştırması), Milliyet (Cem Sorguç), İTÜ, Vikipedi.
- Kanalda yapılmadı: `data/videos.csv`, `data/instagram_reels.csv`, `data/olay_metinleri.md`, `episodes/`,
  `docs/KONU_HAVUZU.md`, `wojak-ozel/teslim/` tarandı ("Tünel", "Karaköy", "Gavand", "metro" yok). Son bölümler (Orban, Yerebatan,
  Tahran, Midas, Hezarfen...) Bizans/Osmanlı/arkeoloji; bu bölüm 19. yüzyıl İstanbul'u ve teknoloji: konu olarak uzak.
- Gerçek ve serbest kanıt: Gavand'ın 1876 kitabındaki profil çizimi (kamu malı), 1884 Pera istasyonu fotoğrafı (SALT),
  Tünel'in ahşap vagonu (CC0).

**Değerlendirilen 3 aday:**
1. **Tünel'in hayvanlı deneme seferleri (seçildi):** yukarıdaki gerekçe; ayrıca metinde "fetvayla yasaklandı" şehir
   efsanesini kaynakla düzeltme imkânı ("aha").
2. **Osmanlı denizaltısı Abdülhamid (1886):** su altından torpido atan ilk denizaltı; ama "mürettebat bulunamadı" ters köşesi
   tek ve zayıf kaynaklı, Commons fotoğrafı 265 px.
3. **Schliemann'ın Truva (Priam) hazinesi (1873):** güçlü ama Karun/Midas'tan sonra üçüncü "hazine" konusu (çok yakın tema).

## Sahne listesi

| Zaman | Arka plan | Karakter | Replik |
|---|---|---|---|
| 0,0-2,5 | Tünel'in ahşap vagonu | A esnaf (sol, sakin) | Yerin altından Pera'ya / vagon mu gidecek? |
| 2,5-5,0 | aynı | B şirket memuru (sağ) | Evet efendi, deneme / seferleri başladı |
| 5,0-7,0 | aynı | A | Yerin altı mezar gibi, kim biner? |
| 7,0-9,0 | aynı | B | Merak etmeyin, ilk yolcular hazır |
| 9,0-11,0 | aynı | A, aynı kutu, şok yüzü + ter | Bekle, ilk yolcular hayvan mı? |
| 11,0-12,5 | KANIT | Gavand 1876, tünel profili (Galata Kulesi) | — |
| 12,5-14,0 | KANIT (son kare) | Pera istasyonu, 1884 (arşiv fotoğrafı) | — |

Son kare türü: arşiv fotoğrafı + mühendis çizimi (son 5 bölüm: tablo, kitap sayfası, arşiv fotoğrafı, müze nesnesi, pul; aynı tür
arka arkaya gelmiyor). Kupür ya da kendi ürettiğimiz kart yok.

## Hakem puanları

Hakemler ayrı bağlamda çalıştırılamadı (alt ajan aracı yok). Her tur `docs/is_akislari/kisa_reel.js` içindeki JUDGE_VISUAL ve
JUDGE_FOLLOWER istemleriyle sıfırdan, yalnız teslim dosyalarına ve ölçümlere bakılarak yürütüldü.

| Tur | Görsel sadakat | Türk takipçi + olgu | MUST | Yapılan |
|---|---|---|---|---|
| Ön kontrol | — | — | — | yetim kelime (S1, S2), kapak başlığa cevap veriyordu (S5 -> S1), kanıt 1 telefonda soluk, yüzler küçük (göğüsten kesim), B'nin çenesi kesik |
| 1 | 8,0 | 8,0 | yok | SHOULD: "Merak etme" -> "Merak etmeyin" (hitap tutarlılığı) |
| 2 | 8,0 | 8,0 | yok | — |

Ölçümler: 13,95 sn; kesmeler 2,5/5,0/7,0/9,0/11,0/12,5; sahne içi fark ≤ 0,12; -29,6 LUFS / -17,0 dBFS; yazı bloğu merkezi %37-41
(C2kk %39, C4V3 %39); telefon (390 px) yüz değişimi %0,55; arka plan L 127, S 0,17, blur 2,5; kanıt 1080x547 ve 1080x760.

## Bilinen kusurlar

1. Son kare hayvanlı deneme seferini göstermiyor: öyle bir görsel yok. Son kare 1884'te istasyonu ve insanları gösteriyor;
   cevabı hikâye metni veriyor.
2. Arka plan müzedeki (Rahmi M. Koç) gerçek Tünel vagonu; camlarda bulanık müze çatısı yansıması var, telefonda "istasyonda eski
   vagon" okunuyor. Mavi tabela yansımasının doygunluğu düşürüldü.
3. Şok yüzündeki gözler düz yuvarlak (biraz "çıkartma" hissi; Orban'daki ev diliyle aynı). Pipo yerinde kaldı.
4. Kanıt görselleri Commons küçük resimlerinden (1920 px; özgün dosya yolu 429 verdi): telefonda net, 1:1'de hafif yumuşak.
5. "Dünyanın ikinci metrosu" ifadesi Türk basınında yerleşik; bazı yabancı kaynaklar Liverpool/New York'u da sayar. Metinde
   "olarak bilinen" dendi.
6. Hakemler aynı bağlamda yürütüldü (yukarıda).

## Lisans kararları

| Görsel | Kaynak | Lisans | Sürüm |
|---|---|---|---|
| Arka plan: Tünel ahşap vagonu, Rahmi M. Koç Müzesi | Commons, Александр Сигачёв, 2026 ("...2026-03 - p05.jpg") | CC0 | A |
| Kanıt 1: "Profil en long", Chemin de fer métropolitain de Constantinople | Commons, Eugène-Henri Gavand, 1876 | Kamu malı (PD-old-70) | A |
| Kanıt 2: Pera'da Tünel istasyonu | Commons / SALT Araştırma (Flickr Commons), B. Kargopoulo, 1884 | Bilinen telif kısıtlaması yok (fotoğrafçı 1886'da öldü: kamu malı) | A |
| Karakterler: 5_Doomer/13970, 5_Crying_Wojak/438 | HF clayshoaf/Wojaks (wojakparadise arşivi) | Kanal standardı (hesap sahibi kararı 27.10); filigran/imza yok, tam boyda bakıldı | A |

Telifli görsel yok; B (`_telifli`) sürümü yok. Lisans kararı bekleyen görsel yok.

Görsel avı: Commons API (`generator=search`, kategori "Tünel", "Karaköy (Tünel)", "Tünel Carriage and railway winding engine"),
İngilizce/Türkçe/Fransızca sorgular ("Tünel Istanbul 1875", "Galata Pera tunnel funicular", "Tunnel de Galata", "chemin de fer
souterrain Constantinople", "SALT Research Tünel", "Rahmi Koç Tünel carriage"); Internet Archive'da Gavand'ın kitabı bulunamadı.
Elenen: tünel içi fotoğrafları (CC BY 4.0, CC BY-SA): kablo kanalı, flüoresan, kırmızı yangın borusu (1874 sahnesine aykırı);
Gavand'ın tren çizimi ("Tünel-train.png", yolcu vagonu + yük/hayvan platformu): özgün dosya 429, küçük resim 500 px.

## Adım süreleri (ölçülen, saat damgalarıyla)

| Adım | Süre |
|---|---|
| Hazırlık + okuma | ~6 dk |
| Konu + olgu | ~9 dk |
| Görsel avı (Commons 429 beklemeleri dahil) | ~12 dk |
| Karakter + yüz | ~6 dk |
| yaml -> teslim | ~3 dk |
| Ön kontrol + 2 hakem turu | ~6 dk |
| Teslim + commit + belge | ~8 dk |
| **Toplam** | **~50 dk** |

## Yaklaşık maliyet

Ücretli API: 0 (TTS, görsel üretimi, ücretli arama yok). Maliyet yalnız bu oturumun model kullanımı (tek ajan, alt ajan yok).
