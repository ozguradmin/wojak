# RAPOR — sultanahmet-alti-minare

**BEKLET: YOK.** İki hakem 8/10, MUST yok; hassas konu yok; lisans kararı bekleyen görsel yok; telifli sürüm yok.
**Hassas konu kontrolü:** güncel olay yok, çocuk yok, son 10 yılda ölen yok, yaşayan özel kişi yok, dava yok
(1609-1617 efsanesi). Dinî mekân (Mescid-i Haram) yalnız hikâye metninde, rivayet diliyle anılıyor; videoda yok.

## Konu
Sultanahmet Camii'nin altı minaresi efsanesi: rivayete göre I. Ahmed "altın minare" istedi, mimar "altı" anladı.
"Ne?!" cümlesi (8 kelime testi): **Padişah altın minare istedi, mimar altı minare yaptı.**
Damar: A+ (Türkiye'nin bildiği efsane, sıradan ustanın gözünden). Bir önceki bölüm (`hope-elmasi-posta-1958`) yabancı
hazine/müze nesnesiydi; ondan önceki `topkapi-hanceri-1747` de hazine. Bu bölüm hazine damarından çıkıyor.

### §5 puan tablosu (3 aday)
| Aday | A çapa | B dönüş | C kahraman | D ilk replik | E görsel | Toplam | Karar |
|---|--:|--:|--:|--:|--:|--:|---|
| **Sultanahmet'in altı minaresi ("altın" / "altı")** | 2 | 2 | 2 | 2 | 2 | **10** | SEÇİLDİ |
| Hierapolis "Cehennem Kapısı" (Plutonion, Pamukkale) | 1 | 2 | 2 | 2 | 2 | 9 | yedek |
| Selimiye'deki ters lale (tarlasını satmayan kadın) | 2 | 1 | 2 | 1 | 1 | 7 | elendi (B ≠ 2) |

Gerekçe: A — Sultanahmet Türkiye'nin en tanınan camisi; B — tek cümlelik ironik dönüş; C — usta + saray ağası
(kurgu, sıradan insan); D — "Usta, padişah altın minare istiyor": somut değer (altın) + imkânsızlık, bilinmeyen özel ad
yok; E — Topkapı Kubbealtı renkli gerçek mekân + 1880 arşiv fotoğrafında altı minarenin hepsi.
Sert filtre: üç adayda da çocuk, yaşayan özel kişi, son 10 yılda ölen, dava, güncel olay yok.
Tekrar kontrolü: `data/videos.csv`, `data/instagram_reels.csv`, `data/olay_metinleri.md`, `episodes/`,
`wojak-ozel/teslim/` içinde "minare", "Selimiye", "Hierapolis/Plutonion", "Karagöz" yok; "Sultanahmet" yalnız
`yerebatan-bodrum-balik`'te semt adı olarak geçiyor.

## Sahne listesi (14,0 sn; ffprobe 13,95)
| # | Süre | Sahne | Metin / görsel |
|---|---|---|---|
| 1 | 0,0-2,5 | A saray ağası (sol) — kanca, kapak | "Usta, padişah / altın minare istiyor" |
| 2 | 2,5-5,0 | B usta (sağ) | "Altı minare mi? / Bizde hiç yapılmadı" |
| 3 | 5,0-7,0 | A | "Bir şey olmaz, / hazine altın dolu" |
| 4 | 7,0-8,5 | kart | "Yıllar sonra" |
| 5 | 8,5-10,5 | B, aynı kutu, şok yüzü | "Bekle, altı değil / altın mı demişti" |
| 6 | 10,5-12,0 | kanıt 1 | I. Ahmed portresi (Met Museum, CC0) |
| 7 | 12,0-14,0 | kanıt 2, son kare | At Meydanı'ndan Sultanahmet, altı minare (Abdullah Frères ~1880, LOC, kamu malı) |

Kelime tohumu: "altın" (S1, S3) → ters köşede "altı değil altın"; son kare altı minareyi sessizce sayar.
Son kare türü: arşiv fotoğrafı. Son 5 bölümün son karesi: paket sargısı (hope), müze nesnesi/hançer (topkapı), harita
(piri reis), müze nesnesi/külçe (uluburun), şehir panoraması (ankara).

## Başlık seçenekleri (≤ 60 karakter, çapa "Sultanahmet", ters köşeyi söylemiyor)
1. **Sultanahmet Camii'nde neden tam altı minare var** (47) — kullanılan
2. I. Ahmed'in Sultanahmet minareleri için verdiği emir (51)
3. Sultanahmet Camii'nin altı minaresinin anlatılan hikâyesi (56)

## Hakem turları
| Tur | Görsel | Takipçi + olgu | MUST |
|---|--:|--:|---|
| 1 | **8/10** | **8/10** | yok / yok |
Tur 1'de ikisi de ≥ 8 ve MUST yok: 2. tur yapılmadı (el kitabı §3). Uygulanan SHOULD'lar (check + kare kontrolüyle doğrulandı):
- Görsel 2: B'nin gri ince yüz çizgileri koyulaştırılıp ~1 px kalınlaştırıldı (`chars/uret.py` `cizgi_koyulastir`); PNG artık
  `kasikci-elmasi`'ndakiyle bayt bayt aynı değil (yön yeniden kaydedildi).
- Görsel 4: şok yüzüne 6. alın çizgisi ve 3. damla; yüz değişimi karenin %0,40'ından %0,51'ine çıktı (390 px, eşik 40).
- Görsel 5: karakter boyu 0,54 → 0,50.
- Takipçi 1: hikâye metninin ilk cümlesi sadeleşti ("Sultanahmet Camii" bir kez).
- Takipçi 2: "iki anlatı da belgelerle desteklenmez" yerine Dalal'ın sözü (kanıt zayıf; kimi anlatıda önce, kimisinde sonra);
  TRT/AA uyuşmazlığı ve "hazine boştu" itirazı `ek_maddeler` yorum yönetimine eklendi.
- Takipçi 3: Smarthistory kaynak notu düzeltildi (sayfada altın/altı efsanesi yok; efsanenin kaynağı Haber7/AA ve Wikipedia).
- Takipçi 4: "1616'da ibadete açıldı, 1617'de tamamlandı". Takipçi 8: "At Meydanı'ndan çektiği" → "At Meydanı'nı ve caminin
  altı minaresini gösteren". Takipçi 9: "ilk kanıt karesi". Takipçi 10: kredi satırına Commons kısa adresi eklendi.
Uygulanmayan SHOULD'lar: Görsel 1 (B için farklı taban: uygun hazır karakter yok, aşağıda kusur); Görsel 3 (A ve B farklı
çizim ailesi: orijinallerde de karışık aile var); Görsel 6 (çinilerde ışık yansıması: gerçek fotoğraf, dokunulmadı);
Görsel 7 (portre 1,46x, sınır içinde); Takipçi 5 (kavuğun kırmızı tepesi: 17. yy kavuğunda kırmızı tepe dönemine uygun,
fes değil; sarık içinden çıkan küçük konik parça); Takipçi 7 (TikTok'taki #keşfet #olay #gizem varsayılan etiketleri
`wojak/config.py`'den geliyor; kod değişmedi, öneri `KOD_ONERILERI`'nde zaten var).

## Bilinen kusurlar
- B (usta) karakteri `kasikci-elmasi`'ndaki "bulan" ile aynı taban (wojakland "Peasant Wojak"; çizgiler koyulaştırıldı ama
  yüz aynı). 1609 için uygun, temiz, klasik yüzlü başka hazır kıyafetli karakter bulunamadı (wl/HF aramalarında Osmanlı
  karakterlerinin çoğu fesli: 1829 sonrası). Dikkatli takipçi Kaşıkçı'daki karakteri tanıyabilir.
- TikTok metninde varsayılan #gizem #olay #keşfet etiketleri konuya tam uymuyor (kod varsayılanı).
- TikTok metni 2.194 karakter (sınır 2.200'e yakın).
- A (saray ağası) wojakland "Sultan Chad"; `kanuni-gizlenen-olum`'daki sadrazamla aynı taban (farklı dosya varyantı).
- Arka plan bugünkü Topkapı Kubbealtı (Divan-ı Hümayun); çinilerde pencereden düşen doğal ışık yansıması var.
- Kanıt 1 küçük resimden 1,46x büyütüldü (sınır 1,5).
- Mekke'ye yedinci minare rivayeti belgesiz ve kaynaklarda çelişkili: videoda yok, hikâye metninde "anlatılana göre"
  ve "belgelerle desteklenmez" diye.

## Lisans tablosu
| Görsel | Kaynak | Lisans | Sürüm |
|---|---|---|---|
| arka.jpg (Topkapı Kubbealtı) | Commons, Dosseman, 2016 | CC BY-SA 4.0 (atıf `credits`'te) | A |
| kanit_1.jpg (I. Ahmed portresi) | Commons ← Metropolitan Museum 450516 | CC0 (`{{cc-zero}}`, ham sayfa) | A |
| kanit_2.jpg (Sultanahmet, altı minare) | Commons ← LOC 2003677072, Abdullah Frères 1880 | kamu malı (`{{PD-old-70-1923}}`, LOC no known restrictions) | A |
| Karakterler | wojakland (Sultan Chad, Peasant Wojak) | kanal standardı (27.10 kararı) | A |
Telifli görsel yok; `_telifli` sürüm yok. Lisans kararı bekleyen görsel yok.
Serbest görsel araması: Commons (`tools/commons.py`), İngilizce/Türkçe/Arapça sorgular (araştırmacı raporu). Mekke
görseli aranıp bulundu (Snouck Hurgronje 1889, PD) ama rivayet belgesiz çıktığı için kullanılmadı.

## Adım süreleri
| Adım | Süre |
|---|---|
| Ortam (hazirla.sh, ölçüm) | ~1 dk |
| Konu (veri, 3 aday, tekrar grep'i) | ~3 dk |
| Araştırma (2 alt ajan, paralel; görselde 2 tur) | ~9 dk |
| Karakter + görsel + yaml + render + teslim | ~8 dk (araştırmayla kısmen paralel) |
| Ön kontrol + RAPOR taslağı | ~2 dk |
| Hakemler (paralel, tur 1) | ~4 dk |
| SHOULD düzeltmeleri + yeniden render/teslim | ~3 dk |
| Teslim, commit, push | ~3 dk |
| **Toplam** | **~30 dk** |
Yaklaşık maliyet: ~$12-16 (yapımcı ~$6-8; araştırmacı 2 iş parçacığı ~$4-5; iki hakem ~$2-3).

Ölçümler: süre 13,95 sn (ffprobe), −14,1 LUFS, gerçek tepe −1,5 dBTP; `check` uyarısız; `bakis.jpg` temiz; yüz değişimi
%0,51; hikâye 1.379-1.450 karakter; Instagram 2.118, YouTube 2.151, TikTok 2.194 karakter.

## Alt ajan çağrıları
- Araştırmacı (olgu): 1 görev, ~20 araç çağrısı.
- Araştırmacı (görsel): 2 tur, ~26 araç çağrısı (ilk tur arka plan bulamadı; arka planı Kubbealtı olarak yapımcı buldu, 4 çağrı).
- Hakem görsel (tur 1) ve hakem takipçi (tur 1): birer görev. Raporlar: /tmp/hakem/1-gorsel.md, /tmp/hakem/1-takipci.md.
