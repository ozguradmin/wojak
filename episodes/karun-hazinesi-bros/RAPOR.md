# karun-hazinesi-bros: üretim raporu (21.10.2026)

**Konu:** Uşak Arkeoloji Müzesi'nde Karun Hazinesi'nin altın Kanatlı Denizatı Broşu 2005'te sahtesiyle
değiştirildi. Bunu yapan, hazineyi Amerika'dan geri alan heyette yer almış olan müze müdürünün kendisiydi.
Vitrindeki sahte broş, 14,3 gramlık orijinalden 9 gram ağırdı.

## Ortam

4 çekirdek, 15 GB RAM, 30 GB boş disk, Python 3.11.17, ffmpeg 6.1.1. Lisanslı Avenir fontu ve 75 referans reel
kuruldu; render'da Avenir kullanıldı. Testler: 70 geçti, 1 düştü. Düşen test, git'e girmeyen talidomit telifli
görselini arıyor; kod hatası değil, ortam eksiği.

## Konu gerekçesi (3 aday)

| Aday | Neden | Karar |
|---|---|---|
| **Karun Hazinesi broşu (Uşak, 2006)** | "Hazineyi Amerika'dan geri getiren müdür, sahtesini koyup aslını sattı." Ters köşe tek cümlede anlatılıyor; Türkiye'de geçiyor. Dramatik ironi var: "Onu ben getirdim", "Bana emanet". "Karun'un laneti" yorum çeker. Serbest lisanslı kanıt da var: vitrindeki **sahte broşun gerçek fotoğrafı** (CC BY-SA). 20+ kaynak var, hüküm kesinleşmiş. Grafik içerik ve çocuk yok | **Seçildi** |
| Ertuğrul Fırkateyni → 1985 Tahran tahliyesi | Dokunaklı ve Türkiye bağlantılı. Ama çok bilinen bir hikâye, ters köşesi tahmin edilebilir | Yedek |
| Yorgun Herakles heykeli (Perge/Boston) | İki yarısı 30 yıl ayrı kaldı, kanıt CC. "Ne?!" etkisi zayıf, ironi az | Yedek |

Kanalda yapılmadığını kontrol ettim: `data/videos.csv` (223 başlık), `data/instagram_reels.csv`,
`data/olay_metinleri.md`, `episodes/` ve `KONU_HAVUZU.md` içinde Karun, Uşak, broş ya da Lidya geçmiyor.

## Sahne akışı (14,0 sn)

| Zaman | Sahne | Replik |
|---|---|---|
| 0-3,0 | Müfettiş (sol, sakin) | Müdür bey, broş sahte diye ihbar var |
| 3,0-6,0 | Müdür (sağ, sakin) | İmkânsız, o broşu Amerika'dan ben getirdim |
| 6,0-8,0 | Müdür (aynı yüz) | Buyrun tartın, o bana emanet |
| 8,0-10,5 | Müfettiş, aynı kutu, **şok yüzü + ter** | Bekle, bu broş neden / bu kadar ağır? |
| 10,5-12,0 | Kanıt 1 | Vitrindeki SAHTE broşun fotoğrafı (Uşak, 2012; CC BY-SA 4.0) |
| 12,0-14,0 | Kanıt 2 | Milliyet 31.05.2006 1. sayfa: "DÜNYAYA REZİL OLDUK / **Bakan Koç: Hırsız evin içindeymiş**" (telifli) |

## Hakem puanları

Hakemler ayrı bağlamda çalıştırılamadı. Her tur sıfırdan yürütüldü: yalnız `kisa_reel.js` JUDGE istemleriyle ve
yalnız teslim dosyalarına bakarak. Ölçüm araçları: 0,5 sn'lik kareler, C2kk, C4V3, C12O ve C2Fr ile aynı ölçekte
yan yana sayfa, kare farkıyla kesme tespiti, telefon boyu (390 px), ebur128.

| Tur | Görsel | Takipçi + olgu | MUST |
|---|---|---|---|
| 1 | 8 | 7,5 | 2 olgu: ihbarın tarihi (2006 başı değil, 2005 sonu) ve müdürün alıntısı (kısaltılmıştı) |
| 2 | **8** | **8** | yok |

Düzeltmeler:
- 1. turdan sonra: ihbar cümlesi kaynakla uyumlu hâle geldi ("isimsiz ihbarın ardından Mart 2006'da"). Alıntı
  birebir yazıldı ("Müdürüm, Karun'un laneti sizi de tutar"). "Güre köyü" yerine "Güre beldesi" yazıldı. İlk
  paragrafa aranan ad olarak "Karun soygunu" eklendi.
- 2. turda kendi ölçümümle bir sorun yakaladım: renderer kanıtı kareye sığdırıyor, bu yüzden iki kanıtın yanında
  siyah bant kalıyordu. İkisi de 1080x1080'e alındı; ölçümle tam genişlik doğrulandı.

Ölçümler:
- Süre 14,0 sn; kesmeler 3,0 / 8,0 / 10,5 / 12,0 sn'de (6,0'daki kesmede yalnız yazı değişir). Sahne içi hareket 0.
- Görüntü ve ses 0,000'da başlıyor.
- Ses −29,6 LUFS, tepe −17,8 dBFS, efekt yok.
- Arka plan parlaklığı 123/255, doygunluk 0,21.
- Karakter boyu 0,48; telefon boyunda yüz değişimi %0,58 (C4V3: %0,60-1,01).
- Filigran her karede.

## Bilinen kusurlar / sapmalar

- `check` bir uyarı veriyor: "imza ses dışında bir müzik". Bilinçli: istem gereği `imza_v2_ic_cekis.m4a`
  kullanıldı. Kod `music: kanal` öneriyor.
- Arka plan Uşak Müzesi değil, Bursa Arkeoloji Müzesi salonu ("aynı türden yer", CC). Uşak Müzesi'nin serbest
  lisanslı geniş açı fotoğrafı yok.
- Kanıt 1'in iki yanındaki ~63 px, aynı fotoğrafın broşsuz kenarındaki kumaşla dolduruldu (broşun piksellerine
  dokunulmadı). Yakından bakılırsa kumaş deseninde hafif bir ek yeri görülebilir.
- Müdür çiziminin kaynağı düşük çözünürlüklü (504x544). Ekranda yaklaşık 1:1 görünüyor, yumuşaklık fark edilmiyor.
- İnceleme sırasında broşun tartılması bir canlandırma. Ağırlık farkı belgeli (bilirkişi raporu). Müdürün o gün
  odada olup olmadığı bilinmiyor; `ek_maddeler`'de "canlandırma" diye yazıyor.
- Müdürün iki repliği onun mahkemede söylediği belgeli sözlerin canlandırması: "Eserleri ABD'den teslim alan
  benim", "Eserler benim üzerime zimmetli". Gerçek kişinin adı hiçbir dosyada yok.
- Kaynaklarda küçük çelişki var: bir yerel yetkilinin 2012'de verdiği sayılar 13,5 g / 22,5 g. Bilirkişi raporu ve
  iddianame 14,3 g / 23,5 g diyor; metinde rapor esas alındı.

## Lisans kararları (hesap sahibinde)

| Görsel | Durum |
|---|---|
| `img/arka_muze.jpg`: Bursa Arkeoloji Müzesi, Canercangul | CC BY-SA 4.0, atıf açıklamada |
| `img/kanit_1_sahte_bros.jpg`: sahte broş, Dosseman (2012) | CC BY-SA 4.0, atıf açıklamada |
| **`img/telifli/kanit_2_milliyet_310506.jpg`**: Milliyet 31.05.2006 1. sayfa | **TELİFLİ, karar bekliyor.** Yedek 1: Milliyet 20.04.2006 "KARUN HAZİNESİ SOYULDU" (o da telifli). Yedek 2: son kanıtı çıkarıp yalnız CC broş fotoğrafıyla bitirmek |
| Karakterler: wojakland "Grey Suit Wojak", HF clayshoaf 5_Doomer/13657 | Kanalın olağan kaynakları |

## Adım süreleri

| Adım | Süre |
|---|---|
| Kurulum + ölçüm (font, referans, testler) | ~1 dk (19:59-20:00) |
| Belgeleri okuma + konu tarama ve seçimi | ~3 dk |
| Olgu araştırması (25+ kaynak) | ~6 dk |
| Görsel avı: Commons 429 beklemeleri, Milliyet arşivi, haber yakalamaları | ~17 dk |
| Karakterler + yüz varyantı (`chars/uret.py`) | ~10 dk |
| `episode.yaml`, check, frames, render, teslim | ~4 dk (tek render ~8,5 sn) |
| Hakem turu 1 + düzeltme | ~4 dk |
| Hakem turu 2 + kanıt tam genişlik düzeltmesi | ~6 dk |
| §4 kontrol listesi, ders notu, teslim, commit | ~8 dk |
| **Toplam** | **~1 saat** (19:59 → ~21:00 UTC) |

## Yaklaşık maliyet

- Harici ücretli API: **0**. TTS, görsel üretimi ve SOL kullanılmadı; Telegram kullanılmadı.
- Hesaplama: tek bir 4 çekirdekli sandbox oturumu, yaklaşık 1 saat. Render başına ~8 sn CPU.
- Model kullanımı: tam ölçemiyorum. Uzun bağlam ve çok sayıda görsel incelemeyle kabaca birkaç milyon girdi token'ı
  sürdü (yaklaşık **10-30 USD** aralığında tahmin; kesin rakam faturada).
