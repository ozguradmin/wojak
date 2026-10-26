# tahran-1985-ertugrul: üretim raporu (26.10.2026 sabah, A sürümü; telifli görsel yok)

> **Yayın durumu:** BEKLET **yok**. Bölüm hassas konu kuralının hiçbir maddesine girmiyor:
> - Konu 1985 tahliyesi ve 1890 batışı; güncel olay değil, GUNDEM §5/§7 kapsamı dışında.
> - Çocuk karakter ya da tanınabilir çocuk yok.
> - Son 10 yılda ölen hiç kimse videoda ya da metinde anılmıyor. Pilotların ve kabin ekibinin adı bilerek kullanılmadı.
> - Yaşayan özel kişi adı yok; yalnız kamu görevlileri (iki büyükelçi, Özal) metinde geçiyor.
> - Süren dava yok.
>
> Lisans kararı bekleyen görsel yok. Üç görsel de Commons'ta kamu malı (PD-Iran, PD-old-100/PD-Turkey,
> PD-Japan-oldphoto); lisanslar dosya sayfalarının ham metninden doğrulandı. İki hakem 8/8 verdi, MUST kalmadı.

**Konu:** 19 Mart 1985'te, İran-Irak Savaşı sürerken, Irak'ın İran hava sahasındaki bütün uçakları vuracağını ilan ettiği
günlerde hiçbir havayolu Tahran'daki 215 Japonu almadı. THY'nin "İzmir" adlı DC-10'u onları, süre dolmadan yaklaşık üç
saat önce çıkardı. Ters köşe: bu jest Türkiye'de ve Japonya'da 95 yıl önceki olaya bağlanır. 1890'da Japonya açıklarında
batan Ertuğrul fırkateyninin 69 denizcisini Kuşimoto halkı kurtarmıştı.

## Ortam

4 çekirdek, 15 GB RAM, 30 GB boş disk, Python 3.11.17, ffmpeg 6.1.1.
- Avenir fontu ve `referans/` (76 dosya) kuruldu; render Avenir ile yapıldı.
- Testler 99/99 geçti. `/home/user` bu sefer vardı ve bağ ilk denemede kuruldu.
- `grep MUSIC_IMZA wojak/config.py` çıktısı `imza_v2_golge.m4a`.
- İki depo ayrık HEAD'de başladı; varsayılan dallara (`claude/kind-albattani-vcp4vk`, `main`) geçilip güncellendi.

## Konu gerekçesi (3 aday)

| Aday | Neden | Karar |
|---|---|---|
| **1985 Tahran tahliyesi ve Ertuğrul (1890)** | "Ne?!" cümlesi: "Hiçbir havayolunun almadığı 215 Japonu THY çıkardı; Japonlara göre sebep 95 yıl önce batan bir Osmanlı gemisiydi." Türkiye merkezli. Dokunaklı/vefa damarı (KONSEPT §2.7'de ~840K medyan). Dramatik ironi var: "Bizim size ne iyiliğimiz dokundu ki?" → "Dokundu, 95 yıl önce". Kaynaklar bağımsız: AA (2014, 2025), Hürriyet (2004, 2018), Akşam, THY bülteni, Daily Sabah, ResearchGate makalesi, T.C. Tokyo Büyükelçiliği, CNN Türk. Kanıtlar kamu malı (1890 tören fotoğrafı, Osman Nuri Paşa tablosu). Mağdurla alay, grafik içerik ya da çocuk yok | **Seçildi** |
| Piri Reis haritası (1929'da Topkapı'da, sarayı müzeye çevirirken bulundu) | Harita kamu malı, Türkiye merkezli; ama "Ne?!" etkisi orta, ters köşe zayıf | Yedek |
| Yerebatan Sarnıcı'ndaki ters Medusa başları | Görsel bol; neden ters konduğu efsane düzeyinde, kanıtla ödenen bir ters köşe yok | Elendi |

Kanalda yapılmadığını grep ile kontrol ettim: `data/videos.csv`, `data/instagram_reels.csv`, `data/olay_metinleri.md`,
`docs/KONU_HAVUZU.md`, `episodes/` ve `wojak-ozel/teslim/`. "Ertuğrul", "Tahran", "Japon", "Piri" hiçbirinde konu
olarak geçmiyor. **Yakın konu notu:** son bölümlerin çoğu Osmanlı/arkeoloji/hazine (Midas, Kaşıkçı, Karun, Göbeklitepe).
Bu bölüm başka bir tür: yakın tarih, havacılık, vefa. Kazı ve hazine yok.

## Sahne akışı (14,0 sn)

| Zaman | Sahne | Replik |
|---|---|---|
| 0-3,0 | Japon mühendis (sol; gözlük, siyah takım; başın önünde iki ter damlası), arkada Mehrabad apronu | Bu akşam uçakları vuracaklar, / Tahran'da bize yer yok |
| 3,0-5,5 | THY hostesi (sağ; mavi üniforma, kırmızı fular) | Hadi binin, sizi THY götürüyor |
| 5,5-8,0 | Japon mühendis (aynı yüz) | Neden? Bizim size ne / iyiliğimiz dokundu ki? |
| 8,0-10,5 | Hostes, aynı kutu, **ters köşe yüzü**: iç uçları kalkık hüzünlü kaş, dolu göz, gözyaşı | Dokundu, 95 yıl önce |
| 10,5-12,0 | Kanıt 1 | Osman Nuri Paşa'nın tablosu: Osmanlı sancaklı Ertuğrul fırtınalı denizde |
| 12,0-14,0 | Kanıt 2 (son kare) | 1890, Japonya: Ertuğrul kazazedeleri için tören. Torii kapısında ay-yıldızlı Osmanlı bayrağı, yandaki direkte "土耳其軍艦遭難者兆域" (Türk savaş gemisi kazazedeleri mezarlığı) |

- **Kalıp:** A B A B soru-cevap, kartsız (Kız Kulesi ritmi, C3iX). Kelime tohumu "iyiliğimiz dokundu" → "Dokundu".
- **Arka plan:** Mehrabad Havalimanı'nın 1971 fotoğrafı (gerçek yer; Iran Air 707'si, yer araçları, terminal ve kule).
  - Renk düzeltildi: doygunluk ~0,31 → ~0,21; kare ölçümünde parlaklık 123, doygunluk 0,25 (hostesin mavisi dahil).
  - `blur: 2.2`; yalnız arka planda kenar Laplace ölçümü: üst ~19, yanlar ~10-13 (orijinal medyan 22, IQR 11-47).
- **Müzik:** `music: {file: kanal, volume: 0.197}` (imza_v2_golge). Ölçüm **−29,6 LUFS, tepe −17,0 dBFS**.
- **Zamanlama:** video ve ses 0,000'da başlıyor. Kesmeler kare farkıyla 3,0 / 5,5 / 8,0 / 10,5 / 12,0 sn'de ölçüldü; sahne
  içi hareket 0,0-0,1.
- **Yüz değişimi:** telefonda (390 px, eşik 40, yazı hariç alt yarı) %0,46 (eşik %0,40). İlk sürüm %0,29'du; gözyaşı ve
  kaş güçlendirildi.
- **Bakış:** `bakis.jpg` kontrol edildi; A sağa, B sola bakıyor. Üç PNG dosyanın kendi yönüyle (sağ) kaydedildi; `faces:` yok.
- **Kapak:** 1. sahne (kanca: Japon mühendis + "Bu akşam uçakları vuracaklar" + IRAN AIR uçağı).

**Son kare çeşitliliği:** son 5 bölümün son kareleri: Midas (müze nesnesi), Hezarfen (pul), Kaşıkçı (müze nesnesi),
Göbeklitepe (renkli kupür), Ayasofya (yazıt + levha). Bu bölüm **arşiv fotoğrafıyla** (1890 tören fotoğrafı) bitiyor;
bu tür son 5'te yok. Olay bir gazete manşetiyle değil anma töreni ve anıtla hatırlandığı için kupür yapılmadı. Kupür ya da
canlandırma kart yok.

## Hakem puanları

Hakemleri ayrı bağlamda çalıştıramadım. Her turu `docs/is_akislari/kisa_reel.js` içindeki JUDGE_VISUAL ve JUDGE_FOLLOWER
istemleriyle, yalnız teslim dosyalarına bakarak sıfırdan yürüttüm. Kullanılanlar: yan yana sayfa (bizim 0,5/3/6/9/11,5/13
sn + C2kk, C4V3, C12O aynı ölçekte), `check`, `bakis.jpg`, ölçümler (ses, kesme, yüz değişimi, arka plan) ve kaynak URL'leri.

| Tur | Görsel | Takipçi/olgu | MUST | Not |
|---|---|---|---|---|
| Ön kontrol | – | – | 1 | Yüz değişimi %0,29 < %0,40 → gözyaşı ve kaş güçlendirildi (%0,46). "Türk Hava / Yolları" satır kırımı özel adı bölüyordu → "Hadi binin, sizi THY götürüyor" |
| 1 | 8 | 8 | 0 | SHOULD: arka plan doygunluğu yüksek (0,23 → 0,21); metinde "İstanbul'a getirildi" tartışmalı → "Türkiye'ye götürüldü"; "çoğu mühendis" → "aileler ve çocuklar" |
| 2 | 8 | 8 | 0 | SHOULD'lar uygulandı, yeni sorun yok. Durma noktası |

**Tavan notu:** ters köşe "ürperti" değil "vefa/duygulanma". Van'daki gibi tavan 8-8,5. Ertuğrul'u bilen izleyici 9. saniyede
yakalar; bilmeyen için son kare (Osmanlı bayrağı Japonya'da) cevabı veriyor.

## Bilinen kusurlar (açıkça)

- **Motif canlandırma:** hostesin "Dokundu, 95 yıl önce" sözü belgeli bir alıntı değil. Ertuğrul bağlantısını Türk
  yetkililer ve basın sonradan kurdu (AA 2014: Büyükelçi Kılıç "küçük bir cevap"). Kararın o günkü gerekçesi belgede yok.
  Metinde "bağlanır" yazıldı ve `ek_maddeler`'e eklendi.
- **Arka plan yılı:** Mehrabad fotoğrafı 1971'den, olay 1985'te. Aynı havalimanı, ama 14 yıl önce; arkadaki uçak Iran
  Air'in 707'si, THY uçağı değil.
- **Hostes üniforması** genel bir mavi kabin üniforması; THY'nin 1985 üniformasıyla birebir aynı olduğu doğrulanmadı.
  Çizim stili animemsi (dudak ve allık geçişli), Japon mühendis ise klasik düz wojak. Orijinallerde de bu karışım var (C4V3).
- **Kanıt 1 bir tablo:** Osman Nuri Paşa'nın tablosu batışı değil, Japonya seferindeki fırtınayı gösteriyor.
- **Tören fotoğrafının tarihi:** Commons'ta "1890" yazıyor. Anıtın 1891'de yapıldığı biliniyor, tören o kış ya da ertesi yıl
  olabilir. Metinde fotoğrafa tarih verilmedi; yalnız `credits`'te Commons'un tarihi var.
- **Tartışmalı sayılar:** Ertuğrul'da ölen sayısı kaynaklarda 530-587 arasında (metinde "500'den fazla"). Irak'ın verdiği süre
  48 ya da 72 saat (verilmedi). Kurtarma için tek mi iki mi uçak gittiği farklı anlatılıyor; tek "İzmir" uçağı anıldı.
- Hakemler ayrı bağlamda değil, aynı bağlamda sıfırdan yürütüldü (sistem istemindeki yedek yol).

## Lisans tablosu

| Görsel | Kaynak | Lisans | Sürüm |
|---|---|---|---|
| Arka plan: Mehrabad Havalimanı 1971 (`img/arka_mehrabad.jpg`) | Commons "Mehrabad-1971.jpg"; *Land of Kings*, Tahran: Information Ministry Press, 1971 | Kamu malı ({{PD-Art\|PD-Iran}}) | A |
| Kanıt 1: Ertuğrul tablosu (`img/kanit_1_ertugrul.jpg`) | Commons "Voyage of frigate Ertugrul to Japan by Commodore Mirliva Nuri 1839 1906.jpg"; Osman Nuri Paşa, İstanbul Deniz Müzesi | Kamu malı (PD-old-100, PD-Turkey; PD-scan) | A |
| Kanıt 2: 1890 tören fotoğrafı (`img/kanit_2_cenaze.jpg`) | Commons "Cérémonie funéraire Ertugrul.jpg"; kaynak İstanbul Araştırmaları Enstitüsü sergisi | Kamu malı ({{PD-Japan-oldphoto}}) | A |
| Karakter A: Japon mühendis | wojakland "Japan Business Wojak" | Topluluk memesi (wojakland şart sayfası yok) | A |
| Karakter B: hostes | wojakland "Flight Attendant Female Wojak" | Topluluk memesi | A |

Telifli görsel yok; `_telifli` sürümü yok. Değerlendirilip kullanılmayan serbest adaylar şunlardı:
- TC-JAY'in kendisi, Mayıs 1985 Frankfurt fotoğrafı (Simon Butler, CC BY 2.0).
- Tahran terminali 1974 (Dick Gilbert, CC BY 2.0).
- Kuşimoto Ertuğrul anıtı (CC BY-SA 3.0/4.0).

**Arama yolu:** Commons API (`generator=search`): "TC-JAY", "Turkish Airlines DC-10", "Ertugrul frigate",
"Ertuğrul Kushimoto", "エルトゥールル号", "Ertugrul 1890 shipwreck", "Mehrabad airport 1970s". Kategoriler: "Ertuğrul
(ship, 1863)", "Sinking of the Ertuğrul (ship, 1863)", "Mehrabad International Airport". Serbest görsel bulunduğu için
kendi ürettiğim kanıt yok.

## Adım süreleri (duvar saati, UTC)

| Adım | Süre |
|---|---|
| Hazırlık (ölçüm, pull, kurulum, referans, test) + okuma | ~3 dk (08:00-08:03) |
| Konu + olgu (3 web araması) | ~3 dk |
| Görsel avı (Commons API + kategori + temas sayfası + md5 indirme, 429 yok) | ~3 dk |
| Karakter + yüz varyantı | ~4 dk |
| yaml → check → frames → render → teslim | ~3 dk |
| Ön kontrol + 2 hakem turu + düzeltme | ~4 dk |
| Teslim + rapor + commit + belge | ~6 dk |
| **Toplam** | **~26 dk** |

## Yaklaşık maliyet

Ücretli API 0 (TTS yok, görsel üretimi yok, yalnız Commons ve web araması). Model kullanımı oturum faturasında; bu
oturumu ayrıca ölçemiyorum.
