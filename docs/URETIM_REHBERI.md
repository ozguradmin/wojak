# Üretim Rehberi — konudan paylaşıma

Bir bölümün baştan sona üretimi. Hedef: **bir video ≈ 30-45 dakika** (araştırma dahil).

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
- Sabit yorumu bu aşamada yaz (150-300 kelime). Örnek üslup: `data/olay_metinleri.md`.

## 3. Senaryo — episode.yaml

```bash
python -m wojak new kapalak-kizi-2     # episodes/_sablon kopyalanır
```

Kurallar (ayrıntı `docs/KONSEPT.md`):

- **Süre 11-15 sn.** 4-6 sahne. Diyalog sahnesi 2.4-3.0 sn, kart 1.0-1.2 sn, kanıt 1.4-1.8 sn.
- **Replik 3-9 kelime**, konuşma dili, 1-2 satır. Olayı **anlatma**, karakterin ağzından **sezdir**.
- İlk replik **masum/ironik** olmalı (Kırkağaç: *"Bekle, bunun tadı neden böyle?"*).
- Son sahne ya gerçek fotoğraf ya da cevapsız bir replik → video **aniden** biter (tekrar izleme).
- Hassas kelimeler ekranda sansürlü yazılır (`*leceğim`, `c!nayet`). Sabit yorum ve başlık
  `wojak.censor` ile otomatik sansürlenir; ekran yazısını elle yaz.

```bash
python -m wojak check episodes/<id>    # doğrulama + sahne zaman çizelgesi
```

## 4. Görseller

### Arka plan (mekân)
Öncelik sırası:
1. **Olayın gerçek mekânı** (haber fotoğrafı, Google Street View ekran görüntüsü, köy/okul/cami fotoğrafı).
   Altın dönemin gücü buydu: izleyici "burası gerçek" hissediyor.
2. **Telifsiz benzer mekân:** `python tools/bg_ara.py "abandoned school corridor" --sheet`
   (Openverse: CC0/CC-BY; lisans `sources:` alanına).
3. **Yapay zekâ ile üret** (API anahtarı tanımlıysa):
   `python tools/gorsel_uret.py arkaplan "a village cemetery in Anatolia with old tombstones" --zaman "Dusk" -o episodes/<id>/img/mezarlik.jpg`

Kırpma kare (1:1) olduğu için yatay fotoğraflarda `focus: [x, y]` ile odağı ayarla.

### Karakterler (wojak)
1. **Kütüphane (10.378 şeffaf PNG, dönem/ülke etiketli):**
   ```bash
   python tools/wojak_lib.py search police          # İngilizce etiketlerle ara
   python tools/wojak_lib.py search turkey
   python tools/wojak_lib.py sheet doomer girl      # numaralı önizleme -> out/sheet_*.jpg
   python tools/wojak_lib.py get 5_Doomer_Girl/2420 --name kiz_gozluklu
   ```
   Faydalı kategoriler: `Doomer`, `Doomer_Girl`, `Trad_Wife` (masum kadın), `Crying_Wojak`,
   `Bloomer` (iyi kalpli), `Boomer` (yaşlı adam), `Tired_Wojak`, `Withered_Wojak` (ürkütücü),
   `NPC`, `Soyjak` (şaşkın/bağıran), `Yes_Chad` (kahraman), `Rage`.
   **Dikkat:** kütüphane internet meme arşivi; "Turkey" gibi etiketlerin çoğu **siyasi/etnik
   karikatür** (darbeci general, parti, milliyetçi/İslamcı meme'ler, ten rengi karikatürleri).
   Bunları asla kullanma. Rol + kıyafetle ara (`worker`, `farmer`, `police`, `nurse`, `soldier`,
   `doctor`, `1950-1960`, `Civilian (Adult)`) ve önizleme sayfasında gözle seç.
2. **JPG/beyaz zeminli wojak bulduysan:** `python tools/cutout.py dosya.jpg -o assets/characters/isim.png`
3. **Kütüphanede yoksa yapay zekâ ile üret** (stil tutarlılığı için `--ref` ile mevcut bir wojak ver):
   ```bash
   python tools/gorsel_uret.py karakter "a Turkish village imam in his 60s, white turban, grey beard, black robe" \
       --duygu "calm but suspicious" --ref assets/characters/sovyet_asker_kis.png -o assets/characters/imam.png
   ```
   Prompt şablonları ve örnekler: `docs/PROMPTLAR.md`.

**Karakter = rol + benzerlik.** Olaydaki kişiye saç/yaş/kıyafet/dönem olarak benzemeli
(Pippa Bacca → gelinlikli kadın; Kırkağaç → koyu saçlı genç; jandarma → üniformalı).
Kötü karakter **ürkütücü** çizilir (siyah yüz + beyaz göz, kırmızı cilt, sırıtan yüz, kapüşon) —
izleyiciler bunu fark edip yorumluyor.

### Kanıt (gerçek) görseller
Kurbanın/kişinin kamuya açık fotoğrafı, haber ekran görüntüsü, gazete kupürü, olay yeri fotoğrafı.
1-2 tane yeter. `label: "Gerçek fotoğraf"` veya `banner: "..."` ile işaretle.

## 5. Ses

Yorumlardan: *"Ulan bu müzik beni videodan daha çok ürpertiyor"*, *"videonun %90 korkutması zaten müzikten geliyor"*.
Ses formatın yarısı.

- **Varsayılan: kanalın imza müziği** `imza_gece_vals.mp3` (`tools/make_music.py` ile üretilen özgün,
  ürkütücü müzik kutusu valsi; hakkı bize ait). Her bölümde aynı müzik = tanınan bir "kanal sesi".
  `music: {file: imza_gece_vals.mp3, volume: 0.7}`
- Altın dönemdeki ses büyük ihtimalle başkasına ait bir parçaydı ("Phantomimes"); dosyaya gömülmez.
- Instagram'da uygulamadan trend ses eklemek istersen hesap **Creator** olmalı; videodaki sesi %20-30'a çek.
  Bunun keşfete etkisi resmi olarak doğrulanmış değil; trial reels ile A/B test edilebilir.
- Ayrıntı ve telifsiz kaynak listesi: `assets/music/README.md`.
- Efektler (`assets/sfx`, sentezlenmiş, telifsiz): `drone` (altlık, müzikle birlikte 0.3-0.4),
  `hit` (kesme), `boom` (kart), `heartbeat` (gerilim), `shutter` (gerçek fotoğraf), `whoosh`, `riser`, `static`.

## 6. Render ve kontrol

```bash
python -m wojak frames episodes/<id>             # her sahneden 1 kare -> out/<id>/kareler/serit.jpg
python -m wojak render episodes/<id> --preview   # hızlı önizleme (yarım çözünürlük)
python -m wojak render episodes/<id>             # final: out/<id>/<id>.mp4 + kapak.jpg + paylasim.md
python -m wojak render episodes/<id> --square    # 1080x1080 sürüm (gerekirse)
python -m wojak render episodes/<id> --dolgu     # bantlar bulanık arka planla dolu (kenarlık A/B testi, KONSEPT §3)
```

Kontrol listesi:
- [ ] Yazılar karakterin yüzünü/önemli detayı kapatmıyor (`text_y`, `side`, `height` ile oyna)
- [ ] Her replik 1 saniyede okunabiliyor (okuma hızı ≈ 3 kelime/sn + 1 sn)
- [ ] Türkçe karakterler doğru (ğ, ı, ş, İ)
- [ ] Kanıt fotoğrafı net ve gerçekten o olaya ait
- [ ] Süre 11-15 sn, son kare "asılı" bitiyor
- [ ] `python -m wojak check episodes/<id>` uyarısız (güncel olayda `gundem: true` ve
      [`GUNDEM.md`](GUNDEM.md) §5'teki 12 maddelik liste tek tek işaretlendi)

## 7. Paylaşım

`out/<id>/paylasim.md` içinde hazır: başlık, açıklama, sabit yorum, hashtag, kontrol listesi.

- **Saat:** 17:00-21:00 TR (altın dönemde 17-21 arası paylaşımlar medyan 729-812K, 21-24 arası 519K; izleyici videoyu gece "gece shorts" olarak tüketiyor ama dağıtım akşamdan başlamalı).
- **Sıklık:** altın dönemde ~2-3 günde bir video vardı. En az haftada 3, ideali günde 1.
- **İlk 1 dakika:** sabit yorumu yaz ve sabitle. Videonun bütün mekanizması buna dayanıyor
  ("Olayı yorumlara yazdım"). `tools/ig_yayinla.py` yorumu otomatik yazar; **sabitleme elle**
  (API'de yok). Kurulum: [`GEREKENLER.md`](GEREKENLER.md).
- Aynı videoyu **YouTube Shorts** ve **TikTok**'a da yükle (aynı başlık, aynı sabit yorum).
- İlk 1-2 saatte yorumlara cevap ver (özellikle "ben oralıyım" tipi yorumlara).

## 8. Takip

Her 2 haftada: `python tools/yt_arastir.py liste && python tools/yt_arastir.py rapor`
(Instagram çerezi tanımlıysa `python tools/ig_fetch.py`). Yeni videoları `docs/ANALIZ.md`
mantığıyla karşılaştır: izlenme/gün, beğeni oranı, yorum oranı.
