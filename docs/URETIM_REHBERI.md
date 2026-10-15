# Üretim Rehberi — konudan paylaşıma

Bir bölümün baştan sona üretimi. Yeni gelen biri önce [`ADIM_ADIM.md`](ADIM_ADIM.md)'yi okusun (kısa + uzun, sırayla). Gerçekleşen
süre 8/10 kalitede **yaklaşık bir iş günü** (OGRENILENLER §6); eski "30-45 dakika" hedefi gerçekçi değildi.

```
konu seç → araştır/doğrula → senaryo (episode.yaml) → görseller → render → kontrol → paylaşım paketi → paylaş → ilk 1 saat takip
```

---

## 1. Konu seçimi

Kaynak: `docs/KONU_HAVUZU.md` + gündem. Bir konuyu seçmeden önce 5 soruluk filtre:

| Soru | Neden |
|---|---|
| Tek cümlede "Ne?!" dedirtiyor mu? | Başlık bu cümleden çıkacak. Dedirtmiyorsa geç. |
| Gerçek mi, kaynağı var mı? | Sabit yorumda isim/tarih/yer vereceğiz. Uydurma = güven kaybı. |
| Türkiye bağlantısı var mı? | Yerel olaylar yorumda "ben oralıyım" etkisi yaratıyor (Malatya, Kırkağaç, Bitlis...). |
| Gerçek fotoğrafı / mekânı bulunabilir mi? | Kanıt sahnesi formatın yarısı. |
| Kanalda daha önce yapıldı mı? | `data/videos.csv` başlıklarında ara. |

**Gündem:** `python tools/gundem.py` her gün Türkiye haber akışlarını tarar ve kanala uygun güncel
olayları puanlar; `--taslak N` ile bölüm taslağı açar. Hangi olay, ne kadar hızlı, hangi kırmızı çizgiler:
[`docs/GUNDEM.md`](GUNDEM.md).

## 2. Araştırma ve doğrulama

- En az **2 bağımsız kaynak** (Vikipedi + haber sitesi / resmi açıklama). `sources:` alanına yaz.
- Tarih, yer, isim, sayı (kaç kişi, kaç yaşında) kontrolü. Efsanelerde "iddiaya göre", "anlatılana göre" kullan.
- Hikâye metnini (`pinned_comment`) bu aşamada yaz (150-250 kelime, ≤ ~1.950 karakter; Instagram'da açıklama olur). Örnek üslup: `data/olay_metinleri.md`.

## 3. Senaryo — episode.yaml

```bash
python -m wojak new kapalak-kizi-2     # episodes/_sablon kopyalanır (A/B kalıbı, music: kanal)
```

Ölçü kaynağı [`STIL.md`](STIL.md) (30 orijinal reel kare kare ölçüldü). Kısaca:

- **Süre 13,5-14,0 sn**, bütün süreler 0,5 sn'nin katı. Diyalog 2,0-3,0 sn (ilk sahne 2,5-3,0),
  isteğe bağlı tek ara kart 1,5 sn (yalnız ileri zaman: "Bir süre sonra"), **kanıt en sonda** 2-3 görsel × 1,5 sn.
  Kanıttan sonra hiçbir şey gelmez.
- **İki kişi konuşur:** A hep solda, B hep sağda; her diyalog sahnesinde yalnız o an konuşan görünür.
- **Replik:** şimdiki zaman, birinci ağız, günlük dil, 1-11 kelime (medyan 5). Nokta ve üç nokta yok,
  anlatıcı/tarih/etiket yazısı yok. İlk replik kanca (olay anından bir soru ya da masum/ironik niyet).
- **Ters köşe:** son diyalogda aynı karakter, aynı kutu, **yüz varyantı** (sakin → terli → çok terli / gözyaşlı)
  ve "Bekle, … neden …?" tipi fark etme.
- Ekrandaki hassas kelimeleri elle yaz (`*leceğim`, `c!nayet`); başlık ve hikâye metni `wojak.censor` ile
  otomatik sansürlenir.

```bash
python -m wojak check episodes/<id>    # doğrulama + zaman çizelgesi + [stil] uyarıları (hepsi giderilmeli)
```

## 4. Görseller

### Arka plan (mekân)
Diyalog boyunca **tek** gerçek renkli fotoğraf (en fazla 2; ikincisi karttan sonra). Doğal renk, karartma ve
gri ton yok; renderer hafif yumuşatır. Öncelik sırası:
1. **Olayın gerçek mekânı** (Wikimedia Commons, kurum fotoğrafı). İzleyici "burası gerçek" hissetmeli.
2. **Telifsiz benzer mekân:** `python tools/bg_ara.py "abandoned school corridor" --sheet`
   (Openverse: CC0/CC-BY; lisans `sources:` alanına, CC BY atfı `credits:` alanına).
3. ~~Yapay zekâ ile üret~~ **Kullanılmıyor** (hesap sahibi 16.10: "görsel üretimi gerek yok, gerçek görseller daha iyi").
   Gerçek fotoğraf bulunamazsa kendi düz çizimimiz (oda, koridor, masa; uzun videodaki gibi) ya da sahne yeniden kurgulanır.
   (`tools/gorsel_uret.py` repoda durur ama üretimde kullanılmaz.)

Yatay fotoğraflarda `focus: [x, y]` ile kare kırpmanın odağını ayarla.

### Karakterler (wojak)
Yalnız temiz, düz çizim (MS Paint) wojak: beyaz yüz, tek çizgi kalınlığı, düz dolgu. Gölgeli/ressamsı/yapay
zekâ görünümlü çizim yok. Görünen yükseklik karenin ~%48'i (renderer varsayılanı).
1. **Klasik kit** `assets/kit/klasik/` (sakin, terli, cok_terli, gozyasli, agliyor...): aynı yüzün duygu
   varyantları. Başka bir taban için varyant: `python tools/kit_varyant.py` (`assets/kit/<isim>/kit.json`).
2. **wojakland + wojaksparadise:** `python tools/wojak_site.py search turkish` → `sheet` → `get <id> --out-dir episodes/<id>/chars`
3. **Kütüphane (10.378 şeffaf PNG):** `python tools/wojak_lib.py search police` → `sheet` → `get`.
   **Dikkat:** "Turkey" etiketlilerin çoğu siyasi/etnik karikatür, asla kullanma; rol + kıyafetle ara.
4. ~~Hiçbiri yoksa yapay zekâ~~ **Kullanılmıyor** (16.10): karakter her zaman hazır wojak çizimidir; uygun olanı bulunamazsa
   rol/kıyafet aramasını genişlet ya da yüz varyantıyla en yakın hazır karakteri uyarla.

**Bakış yönü:** her yeni PNG'yi gözle bak ve kaydet: `python -m wojak yon <png> --yon sag|sol|on`.
Renderer karakteri hep kadrajın içine çevirir (solda sağa, sağda sola bakar).

**Karakter = rol + benzerlik:** saç/yaş/kıyafet/dönem olaydaki kişiye uymalı. Kötü karakter ürkütücü çizilir.

### Kanıt (gerçek) görseller
Olayın gerçek fotoğrafı, gazete kupürü, Türkçe haber başlığı; tam genişlik, ortalı, **etiket/bant yok**.
Kamu malı/CC görsel öncelikli. Haber fotoğrafı ya da haber başlığı kullanılacaksa kaynak linki `sources:`
alanına yazılır ve teslimde hesap sahibine ayrıca sorulur (lisans kararı onundur). Telifli görseller
`img/telifli/` altına konur: bu klasör repoya girmez (repo herkese açık).

## 5. Ses

Ses formatın yarısı (yorumlardan: *"videonun %90 korkutması zaten müzikten geliyor"*).

- **`music: kanal`** (şablon varsayılanı): hesabın kendi reel'lerinden çıkarılan imza "orijinal ses"
  (`assets/music/ozel/`, repoya girmez). Dosya yoksa sentez yedek `imza_gece_vals.mp3` kullanılır.
- Düzey −29,5 LUFS, tepe −17 dBTP (renderer otomatik ayarlar). Döngü yok, **ses efekti yok**.
- Ayrıntı: `STIL.md` §10, `assets/music/README.md`.

## 6. Render ve kontrol

```bash
python -m wojak frames episodes/<id>             # her sahneden 1 kare -> out/<id>/kareler/serit.jpg
python -m wojak render episodes/<id> --preview   # hızlı önizleme (yarım çözünürlük)
python -m wojak render episodes/<id>             # final: out/<id>/<id>.mp4 + kapak.jpg + paylasim.md
python -m wojak render episodes/<id> --dolgu     # bantlar bulanık arka planla dolu (kenarlık A/B testi, KONSEPT §3)
python -m wojak teslim episodes/<id>             # teslim/<id>/: video, kapak, paylasim.md, metinler/
```

Kontrol listesi:
- [ ] `python -m wojak check episodes/<id>` hiç `[stil]` uyarısı vermiyor
- [ ] Yazı yüzü kapatmıyor; karakterler içeri bakıyor; A solda, B sağda sabit
- [ ] Türkçe karakterler doğru (ğ, ı, ş, İ)
- [ ] Kanıt görseli net ve gerçekten o olaya ait; tarih/sayılar başlık ve hikâyeyle çelişmiyor
- [ ] Orijinal bir reel'le yan yana kare karşılaştırması yapıldı (`referans/`)
- [ ] Güncel olayda `gundem: true` ve [`GUNDEM.md`](GUNDEM.md) §5'teki liste tek tek işaretlendi

## 7. Paylaşım

Paylaşımı **hesap sahibi** yapar. Ben `python -m wojak teslim episodes/<id>` ile `teslim/<id>/` klasörünü
(video, kapak, `paylasim.md`, `metinler/*.txt`) hazırlayıp sohbette dosya olarak gönderirim; onaydan sonra paylaşılır.
Platform metinleri: Instagram açıklaması = başlık + hikâyenin tamamı (**hashtag yok**, hesap sahibi 13.10); YouTube = başlık + kısa açıklama (2-3 hashtag),
hikâye sabit yorumda.

- **Saat ve ritim:** 2-3 günde 1, kısa sürüm **20:00-20:15** TR (Instagram altın döneminde 25/25 reel bu düzende); aynı
  konunun uzun videosu aynı gün öğlen YouTube'da. Takvim ve gerekçe: [`YAYIN_PLANI.md`](YAYIN_PLANI.md).
- **Sıklık:** altın dönemde ~2-3 günde bir video vardı. En az haftada 3, ideali günde 1.
- **YouTube'da ilk dakika:** hikâye yorumunu yaz ve sabitle (videonun mekanizması buna dayanıyor).
- Aynı videoyu **YouTube Shorts** ve isteğe bağlı **TikTok**'a da yükle (metinler pakette hazır).
- Ayrıntı ve kararlar: [`GEREKENLER.md`](GEREKENLER.md).
- İlk 1-2 saatte yorumlara cevap ver (özellikle "ben oralıyım" tipi yorumlara).

## 8. Takip

Her 2 haftada: `python tools/yt_arastir.py liste && python tools/yt_arastir.py rapor`
(Instagram çerezi tanımlıysa `python tools/ig_fetch.py`). Yeni videoları `docs/ANALIZ.md`
mantığıyla karşılaştır: izlenme/gün, beğeni oranı, yorum oranı.
