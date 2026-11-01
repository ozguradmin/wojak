# RAPOR — hierapolis-cehennem-kapisi

**BEKLET durumu: YOK.** İki hakem ≥ 8, MUST yok (tur 3: görsel 8/10, tur 2: takipçi 8/10); telifli görsel yok, lisans kararı
bekleyen görsel yok.
Hassas konu kuralı: olay antik çağ (Strabon, MÖ 1. yy sonu / MS 1. yy başı) ve 2012-2018 arkeoloji/ölçüm; çocuk, son 10 yılda ölen,
yaşayan özel kişi, süren dava, güncel olay YOK. Adı geçen yaşayan kişiler kamusal akademisyenler (D'Andria, Pfanz), karakter değiller.

## Konu
- **Konu:** Hierapolis Plutonion'u, "Cehennem Kapısı" (Pamukkale, Denizli). Strabon (Geographika 13.4.14) mağaraya attığı
  serçelerin hemen düşüp öldüğünü, boğaların ölü sürüklendiğini, Kybele'nin hadım rahiplerinin (Galli) ise inip sağ çıktığını
  yazar; ama rahiplerin nefeslerini tuttuğunu ve yüzlerinde "bir tür boğulma nöbeti" gördüğünü de not eder.
- **"Ne?!" cümlesi:** Pamukkale'de giren kuşu öldüren antik kapıya rahipler "tanrıça korur" diye giriyordu; Strabon onların da
  boğulmak üzere çıktığını gördü (sebep 2018'de ölçüldü: yerde biriken karbondioksit).
- **Damar:** 1 (Türkiye'de gösterilebilir yerde ürkütücü gizem). Alt tür: mağara/kutsal kapı (son bölüm minare, öncesi hançer).

## Gündem (1.11, `tools/gundem.py --saat 72 --ilk 15`, 19:03)
Uygun olay yok. En iyi aday: "Kağıthane'de kayıp 80 yaşındaki adamın cesedi Boğaz'da bulundu" (19 kaynak, dalga 31.10, <2 gün):
ölüm nedeni açıklanmadı (kırmızı çizgi: resmî açıklama yokken nedeni anlatmak, olası intihar), özel kişi, ironik/ürpertici an yok
→ elendi. İkinci: "4 faili meçhul cinayet aydınlatıldı" (63 kaynak): yeni şüpheliler, dava süreci sürüyor → elendi.

## §5 puan tablosu (3 aday)

| Aday | Damar | A yer | B dönüş | C kahraman | D ilk replik | E görsel | Toplam |
|---|---|--:|--:|--:|--:|--:|--:|
| **Hierapolis Plutonion "Cehennem Kapısı"** (seçildi) | 1 | 2 | 2 | 2 | 2 | 2 | **10** |
| Patrona Halil (1730): padişahı indiren "tellak" iki ay sonra sarayda öldürüldü | 2 | 1 | 2 | 2 | 2 | 2 | 9 |
| Ağrı Dağı 1840: Akori köyünün bir gecede toprak altında kalması | 2 | 2 | 2 | 2 | 2 | 1 | 9 (etnik/siyasi yorum riski) |

- Plutonion: A = Pamukkale/Hierapolis, serbest fotoğraf (Raddato, Interfase); B = giren kuşun öldüğü, rahiplerin "tanrıça
  korur" deyip nefes tutarak girdiği kapı, izleyicilerin çoğu bilmiyor; C = anonim rahip ve gezgin; D = "Bu mağaraya serçe
  attım, anında düşüp öldüler"; E = gerçek kapı fotoğrafı + Strabon'un 1929 çeviri sayfası (kamu malı).
- Patrona Halil yedek: "tellak" bilgisi rivayet, yer fotoğrafı zayıf. Akori: son kare belirsiz, Ermeni köyü olduğu için yorum riski.
- Tekrar kontrolü: videos.csv, instagram_reels.csv, olay_metinleri.md, episodes/, KONU_HAVUZU.md, wojak-ozel/teslim/ (grep
  Hierapolis|Plutonion|Pamukkale|Cehennem Kap): yok.

## Yorum testi
- Bilen izleyici: "Aslında sihir değil, karbondioksit; 2013 ve 2018'de haberlerde çıktı." → CO2 açıklaması Türkiye'de
  haberlerde geçti (takipçi hakemi: B=2 tartışmalı). Videonun dönüşü bu değil, daha az bilinen kısım: Strabon'un "tanrıça korur"
  denen rahiplerin yüzünde boğulma belirtisi görmesi (son replik + son kare). CO2 ölçümü hikâye metninde.
- "Hâlâ her gün kuş ölüyor" → abartı; gaz gölü yalnız güneşsiz/rüzgârsız saatlerde (metin "kazı sırasında birkaç kuş" diyor).

## Son 7 teslimin damarı
sultanahmet-alti-minare (3) · topkapi-hanceri-1747 (3) · uluburun-kulakli-biskuvi (3, arkeoloji) · hope-elmasi-posta-1958
(zayıf: yabancı) · piri-reis-haritasi-1929 (zayıf: arşiv belgesi) · schliemann-sal-1873 (zayıf) · ankara-elci-vagonlari (zayıf).
Bu bölüm 1. damar; son 7'de 1. damar yoktu.

## Sahneler (14,0 sn; ffprobe 13,95)
| # | sn | tür | içerik |
|---|---|---|---|
| 1 | 0,0-2,5 | diyalog A (gezgin, sol) | "Bu mağaraya serçe attım, / anında düşüp *ldüler" |
| 2 | 2,5-4,5 | diyalog B (rahip, sağ) | "Bize bir şey olmaz, / tanrıça korur" |
| 3 | 4,5-6,5 | diyalog A | "Boğalar bile *lü çıkıyor, / sakın inme" |
| 4 | 6,5-8,0 | kart | "Bir süre sonra" |
| 5 | 8,0-10,5 | diyalog B, aynı kutu, boğulma yüzü | "Gördün mü, tanrıça korudu, / sadece nefesim kesildi" |
| 6 | 10,5-12,0 | kanıt | Plutonion'un kemerli kapısı (Interfase 2025) |
| 7 | 12,0-14,0 | kanıt (son kare) | Strabon, Loeb VI (1929) s. 187: serçe, boğa, Galli'nin nefes tutması, boğulma; dipnot "Priests of Cybelê", sayfa no |

Arka plan: Plutonion'un kendisi (mağara ağzı, kemerli kapı, su, theatron basamakları; tur 3'te değişti, önce Apollon Tapınağı). Son kare türü: kitap sayfası (son 5:
zarf, harita, külçe, hançer, arşiv fotoğrafı).

## Başlık seçenekleri
1. Pamukkale'de içine giren kuşu öldüren Cehennem Kapısı (54) — seçilen (araç sansürüyle "*ldüren")
4. Pamukkale'de içine giren kuşu öldüren antik kapı (48) — tur 1 başlığı
2. Pamukkale'deki Cehennem Kapısı'na yalnız rahipler giriyordu (57)
3. Pamukkale'de rahiplerin girip çıktığı Cehennem Kapısı (53)

## Hakem turları
**Tur 1:** görsel **6/10** (MUST 2), takipçi **7/10** (MUST 1).
- Görsel MUST 1: son kare düz metin şeridi gibi (sayfa numarası/dipnot yok, saf beyaz) → kırpım dipnotlar ve "187" dahil
  (135,1477,1385,2196), autocontrast kaldırıldı, beyaz taramaya kitap kâğıdı tonu, son kare 2,0 sn.
- Görsel MUST 2: gezgin (Socrates Wojak) düz wojak ailesinden değil → wojakland "Roman Crying Wojak" (düz MS-Paint, saç bandı,
  kırmızı pelerin); ağlayan yüz silinip sakin klasik wojak yüzü çizildi.
- Takipçi MUST: son kare okunmuyor, dönüş Türkçe görünmüyor → dönüş son repliğe taşındı: "Gördün mü, tanrıça korudu, / sadece
  nefesim kesildi"; son kare 2,0 sn. Not: satırlar tam genişlikte olduğundan gövde metninin büyük harfi ~29 px'te kalıyor
  (35 px için satır 1080'den geniş olmalı); dönüş artık sayfayı okumaya bağlı değil.
- Uygulanan SHOULD'lar: S2 "Bize bir şey olmaz, / tanrıça korur"; kart "Bir süre sonra"; başlığa "Cehennem Kapısı"; hikâye
  metninde "mağara girişinde", "%5'i geçmedi", %57 (2013 sabah) / %68 (2014 gece) ayrımı, Strabon (eğilip iner) / Pfanz (ayakta)
  ayrımı; Raddato kredisi tam başlıkla; rahip yüzündeki gri dikdörtgen leke temizlendi, PNG sakal altından kesildi (yüz büyüdü);
  arka plan Color 0,68 + blur 2,0 (doygunluk 0,22); kanıt_1 kemere ~%10 yakın.

**Tur 2:** görsel **7/10** (MUST 0; tur 1 MUST'ları kapandı), takipçi **8/10** (MUST 0; tur 1 MUST'ı kapandı).
- Görsel 8'i engelleyen: "Bu mağaraya" repliği harabe (Apollon Tapınağı) arka planıyla çelişiyor; son kare İngilizce ve küçük.
- Uygulanan: arka plan Plutonion'un kendisiyle değişti (Interfase "Plutonion in Hierapolis 13", CC BY-SA 4.0; mağara ağzı,
  kemer, su, theatron basamakları; modern korkuluk ve projektör kırpımın dışında; 1,42x büyütme, blur 2,0, doygunluk 0,20).
  Son kare değişmedi (hakem: "kırpımı koru"). Takipçi SHOULD'u: yorum testine CO2'nin bilinen dönüş olduğu notu eklendi.
  Takipçi tur 2'de eşiği geçtiği için yeniden puanlanmadı (değişiklik yalnız görsel: arka plan ve kredi satırı; lisans
  `commons.py bilgi` ile doğrulandı).

**Tur 3 (son):** görsel **8/10** (MUST 0). Alt puanlar: format 8,5 · karakter 7,5 · arka plan 8 · kanıt 7 (kanıt_1 7,5, son
kare 7) · kapak 8. Takipçi (tur 2): kanca 9 · ironi 8 · dil 8 · son kare 7 · başlık 8,5 · konu 7 · olgu 9 · lisans 9.
- Tur 3 SHOULD uygulanan: arka plan Brightness 0,95 → 0,92 (check + render + bakış yeniden doğrulandı, 13,95 sn, −14,1 LUFS).
- Uygulanmayan: kanıt_1'i arka planda görünmeyen bir ayrıntıyla değiştirmek (yazıtın ve kapının dışarıdan serbest fotoğrafı
  bulunamadı; Raddato'nun "Pluto's Gate" fotoğrafları Apollon Tapınağı altındaki eski, yanlış tanımlanmış odayı gösteriyor),
  gezgin konturunu ~%10 kalınlaştırmak (kozmetik, 390 px'te görünmüyor).

## Bilinen kusurlar
- Son kare İngilizce ve telefonda küçük punto (büyük harf ~29 px); dönüş son replikte Türkçe, Türkçesi hikâye metninde.
  İki hakemin de en zayıf bulduğu öğe (7/10).
- Kanıt_1 (kapının yakın planı) arka planla aynı yeri gösteriyor; yeni bilgi az.
- `check` ✎ ipucu: arka plan kaynağı keskin (Laplace 62,5; render'da blur 2,0 ile hakem ölçümü referans aralığında).
- Arka plan 1920 px küçük resimden 760 px kare kırpımın 1,42x büyütülmesi (yumuşatma 2,0 ile gizleniyor). Arka plan ve
  kanıt_1 aynı yerin (Plutonion kapısı) iki ayrı fotoğrafı.
- Taramanın kâğıdı bembeyazdı (255); kitap kâğıdı tonu verildi (renk ayarı, credits'te yazılı).
- Gezgin karakteri wojakland "Roman Crying Wojak"; yüzü elle yeniden çizildi (sakin klasik wojak yüzü). Roma dönemi kostümü
  (saç bandı, pelerin) Strabon dönemine uygun; adsız gezgin.

## Lisans tablosu
| Görsel | Kaynak | Lisans | Sürüm |
|---|---|---|---|
| img/arka.jpg (Plutonion: mağara ağzı, kemer, theatron) | Interfase, Commons "Plutonion in Hierapolis 13" | CC BY-SA 4.0 | A |
| img/kanit_1.jpg (Plutonion kapısı) | Interfase, Commons "Plutonion in Hierapolis 3" | CC BY-SA 4.0 | A |
| img/kanit_2.jpg (Strabon s. 187) | Loeb VI, 1929, çev. H. L. Jones; IA in.ernet.dli.2015.57230 | Kamu malı (ABD 1929 yayını; çevirmen ö. 1932) | A |
Telifli görsel yok; B sürümü yok. Lisans kararı bekleyen görsel yok.

## Adım süreleri (UTC saatleri oturum günlüğünden)
| Adım | Süre |
|---|---|
| Ortam + hazırlık (hazirla.sh, testler 135 geçti) | ~1 dk |
| Gündem taraması + rapor okuma | ~2 dk |
| Veri, konu adayları, tekrar grep'i | ~3 dk |
| Araştırma (2 paralel iş parçacığı: olgu, görsel + Strabon sayfası) | ~8 dk (paralel) |
| Karakterler (2 kaynak, temizlik, boğulma varyantı; tur 1 sonrası gezgin değişimi) | ~8 dk |
| yaml → render → teslim (ilk) | ~3 dk |
| Hakem tur 1 + düzeltme + tur 2 + arka plan değişimi + tur 3 | ~15 dk |
| RAPOR, teslim, commit | ~4 dk |
| **Toplam** | **~40 dk** |

## Alt ajan çağrıları ve yaklaşık maliyet
- Araştırmacı ×2 (olgu; görsel + Strabon sayfası ek görevi), görsel hakem ×3 tur, takipçi hakem ×2 tur.
- Yaklaşık maliyet: yapımcı (Opus) ~$8-10 + araştırmacılar ~$4-6 + hakemler ~$5-7 ≈ **$17-23** (tahmin; ölçülmedi).
