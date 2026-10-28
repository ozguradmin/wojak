# Kısa reel el kitabı (iki kanal: `tr` Tarihsel Wojak, `en` Wojak Past Files)

> **Her kısa reel oturumunda okunacak TEK dosya budur** (29.10.2026). Başka belgeyi baştan sona okuma; gerekirse §15'teki
> dizinden yalnız ilgili bölümü aç. Bu dosya eski okuma listesinin (ADIM_ADIM, STIL, OGRENILENLER, KONSEPT, GUNDEM,
> `kisa_reel.js` bağlamı) yerine geçer. Çelişki olursa sıra: hesap sahibinin yeni notu > `CLAUDE.md` sert kuralları >
> bu dosya > öteki belgeler. Ölçülerin kaynağı yine `STIL.md`'dir; burada yalnız gereken özü var.
> Hedef: bir reel **≤ 35 dk**, iki bağımsız hakemden **≥ 8/10 ve MUST yok**, bilinen kusur varsa RAPOR'da açıkça yazılı.

---

## 1. Sert kurallar (pazarlıksız)

1. **Gizli anahtarlar** yalnız ortam değişkeninde ya da `~/.config/wojak/secrets.env`'de; hiçbir dosyaya, loga, rapora,
   komut satırına yazılmaz.
2. **`wojak` deposu herkese açık.** Asla commit edilmez: `*.mp4`, `img/telifli/`, `assets/fonts/ozel/`,
   `assets/music/ozel/`, `referans/`, `.env`, çerez. Her commit'ten önce `git status` ve
   `git diff --cached --name-only | grep -E '\.mp4$|telifli|ozel/|referans'` (boş çıkmalı).
3. **Ağ:** genel tarayıcı User-Agent; e-posta ya da kişisel tanımlayıcı hiçbir başlıkta/istekte yok; vekil sunucu atlanmaz.
4. **Mahremiyet:** reşit olmayanın soyadı, anne-baba adı, okulu, mahallesi, bugünkü fotoğrafı hiçbir dosyada yok (yaml
   notları ve git geçmişi dahil). Özel kişilerin aile adı yazılmaz. Hidden Words listesi yalnız sohbette.
5. **Saygı:** kurbanla alay, grafik içerik, gerçek kişiye uydurma tırnaklı söz, yakın zamanda ölene "son söz" yok.
   Siyasi/etnik/dini kutuplaştırma konusu seçilmez.
6. **Olgu:** ekrandaki, başlıktaki ve metindeki her iddia ≥ 2 bağımsız kaynakla. Tek kaynaklı ya da tartışmalı olan
   "anlatılana göre / iddiaya göre" olur ya da çıkarılır. Efsane efsane diye anılır. Alıntı kaynaktan **birebir**.
7. **Yapay zekâ görseli yok.** Arka plan ve kanıt gerçek fotoğraf/belge ya da kendi ürettiğimiz gerçekçi kupür/belge;
   karakterler hazır wojak çizimi.
8. **Telifli görsel hiçbir sürüme girmez** (§9). Lisans şüphesi = BEKLET.
9. `teslim/` elle düzenlenmez: değişiklik `episode.yaml`'da, sonra yeniden üret. Düzeltme turunda `wojak/` ve `tools/`
   düzenlenmez; hata `docs/KOD_ONERILERI.md`'ye tek satır olarak yazılır.
10. Force-push ve geçmiş yeniden yazımı yok.

## 2. Hesap sahibinin kararları (hakemlerden önce gelir; en yenisi üstte)

- **27.10 Karakter lisansı:** `assets/kit/` ve kütüphane karakterleri (wojakland, wojakparadise, HF `clayshoaf/Wojaks`)
  kanal standardıdır ve serbesttir; lisans sayfası olmaması BEKLET nedeni değildir, atıf gerekmez. Filigran, imza ya da site
  adı taşıyan karakter kullanılmaz (tam boyda bak). Karakter PNG'leri `episodes/<id>/chars/` altında commit edilir.
  Lisans kuralları yalnız kanıt, arka plan ve kupür içindir.
- **25.10 Bakış:** `faces:` yazılmaz; PNG'nin kendi yönü `yon` ile kaydedilir (§10). İki yayımlanmış reel'de karakter
  dışarı bakmıştı.
- **22.10 Müzik:** her kısa reel aynı imza: `music: {file: kanal, volume: 0.197}` (bizim `imza_v2_golge.m4a`). `orijinal`
  asla (YouTube riski). Havası çok farklı konuda yalnız aynı aileden varyant.
- **22-23.10 YouTube:** herkese açık yükleme, hikâye metni yorum olarak; bunu yayın botu yapar. Elle yükleme yok.
- **21.10 Son kare:** telifli gazete sayfası kullanılmaz. Düz "alıntı kartı" (kâğıt + yazı + çizgi) hesap sahibinden
  **1/10** aldı (iki hakem 8/8 vermişti): son kare ya gerçek serbest belge ya da gerçek sanılacak kalitede kupür (§9).
- **16.10 Görsel:** yapay zekâ görseli yok; gerçek görseller daha iyi.
- **13.10 Kıyafet ve yüz:** kıyafetli karakter **hazır** bulunur (wojak başına kıyafet boyanmaz, yama/dikiş izi yok).
  Yüz varyantları temiz: aynı çizgi kalınlığı, telefonda okunur fark.
- **13.10 Metinler:** Instagram açıklamasında hashtag yok (YouTube'da 2-3 serbest). Başlık "AI slop" gibi durmaz: abartı
  sıfatı, emoji, "ŞOK" yok; merak boşluğu + somut ayrıntı (yer, sayı, kişi).
- **13.10 Çıta:** "Yapayım geçeyim değil, benchmarktasın gibi." Bilinen kusurla sessiz teslim yok; varsa RAPOR'da yazılır.
- **09-12.10 Referans:** ilk parti 3/10 aldı (atıf yazıları, dışarı bakan karakterler). Onaylı referans seti:
  `van-depremi-azra-bebek`, `canakkale-kayip-tabur`, `kiz-kulesi-efsanesi`, `talidomit-turkiye`. 8'den 9'a cila değil
  **konu** taşır: az bilinen, doğrulanabilir, "bekle, NE?!" dedirten olay.

## 3. Ekip, turlar, BEKLET ve yayın

**Roller.** Yapımcı (tr: Opus, en: Sonnet; araştırmacı ve hakemler Sonnet) bölümü kurar ve **kendini hiç puanlamaz**.
- **Araştırmacı alt ajanı:** konu taraması (3 aday), olgu doğrulaması (olgu tablosu + kaynaklar + güvenli ifade + hikâye
  taslağı), görsel avı (arka plan 3 aday, 2-3 kanıt, karakter önerisi, lisanslar, temas sayfası). Yapımcı bu işleri kendi
  bağlamında yapmaz; yalnız özet dosyaları okur (`olgular.md`, `gorseller.md`).
- **İki bağımsız hakem alt ajanı** (taze bağlam, dosyaya dokunmaz): görsel sadakat (orijinallerle kare kare, ölçerek) ve
  takipçi + senaryo + olgu (kaynak URL'lerini açarak ≥ 5 olgu). İstemler: `docs/is_akislari/kisa_reel.js` içindeki
  JUDGE_VISUAL / JUDGE_FOLLOWER; okuma listesi olarak hakeme yalnız bu dosyayı ve `STIL.md` §0, §14'ü ver.
  Puan çapaları: 10 = orijinalden ayırt edilemez, 8 = uzun süreli takipçi telefonda hiçbir şey fark etmez, 6 = düzgün taklit.
  En zayıf görünen öğe genel puanı sınırlar.

**Turlar.**
- Tur 1 iki hakemden **≥ 8 ve MUST yok** ise 2. tur YAPILMAZ: SHOULD'ları uygula, `check` + kendi kare kontrolünle doğrula.
- MUST varsa düzelt, aynı hakem iş parçacığına 2. turu ver; hakem önceki MUST listesini satır satır kapatır.
- **En fazla 3 tur.** Çıta geçilmediyse ya da son turdaki düzeltme yeniden puanlanmadıysa → `BEKLET`.
- Hakemler çelişirse orijinaller ne yapıyorsa o yapılır. Hakemin önerdiği sayıyı kareye bakmadan uygulama.

**BEKLET** (bölüm klasöründe boş `BEKLET` dosyası; hesap sahibi karar verir) şu durumlardan biri varsa:
güncel olay (GUNDEM), çocuk, son 10 yılda ölmüş kişi, yaşayan özel kişi, süren dava, hakem çıtası geçilmedi ya da MUST
kaldı, kanıt/arka plan/kupürde lisans şüphesi. Karakter lisansı BEKLET nedeni değildir.

**Yayın.** Özel depodaki GitHub Actions botu teslimi push'tan **~10 dk sonra** yayınlar (yayından önce BEKLET'e tekrar
bakar): `tr` → `wojak-ozel/teslim/<id>/`, `en` → `wojak-en-ozel/teslim/<id>/`. Bir kanalın bölümü asla öbür depoya konmaz.
- **BEKLET kararı teslim commit'inden ÖNCE verilir;** BEKLET varsa aynı ve tek commit'e girer. Sonradan BEKLET commit'i
  atılmaz (27.10'da `en-mincemeat` yayına girdikten 8 sn sonra BEKLET eklendi; video zaten yayındaydı).
- `YAYINLANDI.json`'a dokunma. YouTube'a elle yükleme yok (bot çift yükler).
- Instagram'ı hesap sahibi Telegram'dan paylaşır; bölüme özel notlar `ek_maddeler`'e.

## 4. Hızlı başlangıç (çalışan yol, sırayla)

1. **Ortam (~3 dk):** `bash tools/hazirla.sh <özel-depo-yolu>` (bağ, iki deponun varsayılan dalı + pull, pip, font,
   referans, kısa pytest özeti, müzik kontrolü). Çıktıdaki uyarıyı düzelt, sonra devam et. Elle kurulum gerekirse:
   `mkdir -p /home/user` bağdan ÖNCE; depolar ayrık HEAD'de açılır, dosya yazmadan varsayılan dala geç.
2. **Konu (~4 dk):** §5. Araştırmacıya 3 aday taratıp en güçlüsünü seç.
3. **Araştırma (alt ajan, paralel ~8 dk):** olgu + görsel + karakter önerisi. Sen bu arada karakter kitine bak.
4. **Bölümü aç:** `python -m wojak new <id>` (en: `python -m wojak new en-<id> --kanal en`). Şablon: §8.
5. **Görseller:** `python tools/commons.py ara|bilgi|indir ...` (`--help`); kendi Commons/429 betiğini YAZMA. Kanıtı ve arka
   planı §9'a göre hazırla (`episodes/<id>/gorsel.py`).
6. **Karakterler:** §10. Her PNG'yi tam boyda aç, `yon` ile kaydet, ters köşe varyantını hazırla.
7. **Döngü:** `python -m wojak check episodes/<id>` (hiç `[stil]` uyarısı yok; çıktıyı `grep -v "^ "` ile süzme, `[stil]`
   satırları girintilidir) → `python -m wojak frames episodes/<id>` → **tek bir şerit/temas sayfasına** bak →
   `python -m wojak render episodes/<id>` → `python -m wojak bakis episodes/<id>` → `out/<id>/kareler/bakis.jpg`'ye bak →
   `python -m wojak teslim episodes/<id>` (düzeltme turunda bilinçli `--zorla`).
8. **Ön kontrol (~3 dk):** §11'deki liste. Hakemden önce bulunan her sorun bir tur kazandırır.
9. **Hakemler:** iki alt ajan paralel (§3).
10. **Son kontrol:** §12. BEKLET kararı (§3). RAPOR.md (§13).
11. **Teslim:** paket → özel depo, tek commit, push. Herkese açık `wojak`'a bölüm dosyaları (yaml, betikler, `chars/`,
    serbest `img/`) ve `data/karakter_yon.json`'daki **yalnız kendi girdilerin**.
12. **Ders:** `docs/DERS_KUTUSU.md`'ye en çok 10 satır, yalnız gerçekten yeni olan (§14).

Süre bütçesi: ortam 3 · konu 4 · araştırma 8 (paralel) · karakter 5 · yaml→render 4 · ön kontrol 3 · hakem 5 · teslim 4.
Kabuk komutlarını toplu çalıştır (tek betikte birden çok adım); tek tek kare yerine tek birleşik sayfaya bak
(`serit.jpg`, `bakis.jpg`, 360-390 px temas sayfası). Büyük görseli tam çözünürlükte bağlama alma.

## 5. Konu seçimi

- **Önce performans verisi:** özel depodaki `istatistik.csv` (video başına izlenme, beğeni, ortalama izlenme %, abone;
  günlük güncellenir). Konuyu seçmeden oku; en iyi performans gösterenlerin kalıbına yaslan. 29.10 TR durumu:
  `kasikci-elmasi` 110K, `midas-mezari-altin` 79K, `ayasofya-viking-yazisi` 67K; `tahran-1985-ertugrul`,
  `yerebatan-bodrum-balik`, `gobeklitepe-mezar-tasi` ~28K. Hazine, ünlü nesne ve sıradan insanın gözünden olay; soyut
  diplomasi ve arkeoloji daha zayıf. Ortalama izlenme %110-137 (döngü izlemesi): son kare başa bağlanmalı.
- **Filtre:** tek cümlelik "Ne?!" var mı; ≥ 2 bağımsız kaynak; ironi/ters köşe kurulabiliyor mu; serbest lisanslı güçlü
  son kare var mı; `tr` için Türkiye bağlantısı (10M+ reel'lerin 17/19'u Türkiye'de geçiyor).
- **Tekrar yok:** kanalda yapılmış konu seçilmez. `data/videos.csv`, `data/instagram_reels.csv`, `data/olay_metinleri.md`,
  `episodes/`, `KONU_HAVUZU.md` ve özel deponun `teslim/` klasöründe grep'le. Bir önceki bölümle aynı damardan arka arkaya
  gitme.
- Güncel olay ise önce `GUNDEM.md` §5 ve §7; yayın BEKLET'li.

## 6. Format (STIL §0 + §15 özü)

- Siyah 9:16 tuval, ortada 1080x1080 kare (y 420-1500). Toplam **13,5-14,0 sn**, bütün süreler **0,5 sn'nin katı**.
- Sıra: diyalog (3-5 sahne, 2,0-3,0 sn; ilk sahne 2,5-3,0) → isteğe bağlı **tek** ara kart 1,5 sn (yalnız ileri zaman:
  "Bir süre sonra", "Birkaç gün sonra"; en: "... later") → **kanıt en sonda** 2-3 görsel, her biri 1,5 sn (son 1,5-2,0).
  Kanıttan sonra hiçbir şey yok. Kanıt ~10,5-11,0 sn'de başlar.
- Her sahne durağan, sert kesme. Zoom, Ken Burns, kaydırma, sarsıntı, flaş, pop-in, fade, ses efekti YOK.
- Her diyalog sahnesinde yalnız konuşan karakter; iki kişi, aynı yer, aynı an; **A hep solda, B hep sağda**.
- Replik: karakterin kendi ağzından, şimdiki zaman, konuşma dili; 1-11 kelime (medyan 5); **nokta ve üç nokta yok**, ünlem
  neredeyse yok; en çok 2 satır. Okuma kuralı: kelime/3,5 + 0,4 ≤ süre + 0,15 (2,0 sn ≈ 6 kelime, 2,5 ≈ 7, 3,0 ≈ 9).
  Anlatıcı, özet, tarih/yer yazısı, etiket çipi, alıntı bandı yok.
- Tek arka plan fotoğrafı (en çok 2; ikincisi karttan sonra), doğal renk, karartma/gri ton yok, hafif yumuşak.
- Ters köşe: **aynı karakter, aynı kutu, yüz varyantı** + fark etme sorusu ya da dramatik ironi; cevabı son kanıt sessizce
  verir.
- Kanıt tam genişlik (1080), y=960'a ortalı, 537-816 px yükseklik; kenarlık, bant, ok, ızgara, kolaj yok.
- Filigran her karede (kart ve kanıt dahil); renderer koyar. Font Avenir Bold Italic (Poppins'e düşerse kanal değil).
- Ses: tek parça imza müzik, ~-29,5 LUFS (tepe ~-17 dBTP), efekt yok, döngü yok.

## 7. Senaryo, başlık, hikâye metni

**İskeletler** (ikisi de onaylı):
- *C2fa (dramatik ironi):* A masum/ironik niyet → B uyarır → A geçiştirir ("Bir şey olmaz, ...") → kart → aynı kutuda yüz
  değişir, fark eder → 2 kanıt.
- *A-B-A-B soru-cevap:* son replik bir soru, cevabı son kanıt.

**İşe yarayanlar:**
- İlk replik olay anında kancadır ve bağlamı söyler (uçak, kaçırma, mezar...): "Sit down, this is a hijacking".
- Kelime tohumu: S2'deki sıradan kelime son karede karşılığını bulur ("üç tahta kaşık" → Kaşıkçı; "dokundu" → "Dokundu,
  95 yıl önce"). Görsel tohum da olur (B'nin başındaki fes).
- Ters köşe repliği nesneyi değil **imkânsızlığı** sorar ("Bekle, anahtarın yerini nereden bildi?"); resmin zaten
  gösterdiğini söylemez. Bilgisi bir önceki replikte ekilmiş olmalı. Repliğin her kelimesi olguya uyar ("again" gibi
  tarihe aykırı kelime MUST olur).
- Belgeli nedeni replikte kullan; uydurma tavır yazma. Gerçek kişiye replik gerekiyorsa belgeli sözüne dayan; gerçek ve
  özel kişiyi kurgu rolle temsil et ("gerçek ekipten kimseyi temsil etmez" notu `ek_maddeler`'e).
- Yüz kodu anlam taşır: sırıtma = kötü karakter. Şüpheli, firma, gerçek kişi ya da sevecen karakterde kötü yüz yok.
- Replikteki fiilin nesnesi tek anlamlı olsun ("kapının dibindeki döşemeyi sökün").

**Başlık** (`title`): 3-12 kelime; olayın adı ya da en şaşırtıcı tek cümlesi; **ters köşeyi söylemez** (son replikle
karşılaştır); fiil kaynağa uyar ("teklif eden", "gördüğünü söyleyen"); somut yer/sayı/kişi. Başlık soruysa kapak
(`cover_scene`) cevabı göstermesin: kapak = kanca sahnesi, ters köşe kapağı alternatif.

**Hikâye metni** (`pinned_comment`): 150-250 kelime, ≤ ~1.950 karakter (Instagram açıklaması kredi ve notlarla ≤ 2.200),
3-6 paragraf, ansiklopedi dili. İlk cümle: "X olayı, YYYY yılında [yer]'de yaşanan ve ... olarak bilinen bir olaydır."
Kronolojik; kişiler unvanıyla tanıtılır; yaygın yanlış anlatıyı kaynağıyla düzelt (efsane düzeltme ters köşeye ağırlık
verir). Yabancı dilli son kare için "Videonun son karesi ... sayfasıdır" + Türkçesi. Son satır yorum getiren soru.

## 8. `episode.yaml` iskeleti

```yaml
id: <id>                       # en: en-<id>
# kanal: en                    # yalnız İngilizce kanal
title: "<başlık>"
music: {file: kanal, volume: 0.197}   # bu ortamda ~-29,6 LUFS; render sonrası ölç
scenes:
  - {type: dialog, duration: 3.0, bg: img/arka.jpg, blur: 1.7,
     chars: [{img: chars/a.png, side: left, height: 0.50}], text: "Kanca, olay anında"}
  - {type: dialog, duration: 2.5, bg: img/arka.jpg, blur: 1.7,
     chars: [{img: chars/b.png, side: right, height: 0.50}], text: "Cevap ya da uyarı"}
  - {type: dialog, duration: 2.5, bg: img/arka.jpg, blur: 1.7,
     chars: [{img: chars/a.png, side: left, height: 0.50}], text: "Tırmanış, bilgi ekilir"}
  - {type: dialog, duration: 2.5, bg: img/arka.jpg, blur: 1.7,      # ters köşe: B, aynı kutu, yüz varyantı
     chars: [{img: chars/b_sok.png, side: right, height: 0.50}], text: "Bekle, ... nasıl ...?"}
  - {type: evidence, duration: 1.5, images: [img/kanit_1.jpg]}
  - {type: evidence, duration: 2.0, images: [img/kanit_2.jpg]}      # son kare
cover_scene: 1
cover_at: 0.5
caption: |
  <başlık>
  Olayın tamamı sabit yorumda 👇
hashtags: [konu1, konu2, konu3]      # YouTube için 2-3; Instagram'a hashtag konmaz
pinned_comment: |
  <150-250 kelimelik hikâye metni, soru ile biter>
credits: "<eser adı> (<yazar>, <lisans>; kırpıldı, renk düzeltildi, ...), Wikimedia Commons; ..."
ai_generated: false
ek_maddeler:
  - "**Video bir canlandırmadır:** karakterler kurgu, ekrandaki sözler belgeli alıntı değildir. Belgeli olan: ..."
  - "Gizli kelimeler (Hidden Words) listesi sohbette"
sources:
  - "<olgu kaynağı, ne doğruladığı>: <URL>"
  - "GÖRSEL img/kanit_2.jpg (son kare) — '<Commons dosya adı>', <yazar>, <lisans şablonu>: <URL>. Değişiklik: <kırpım, renk>"
```
Ayrıntı ve tam örnek: `episodes/pera-palas-anahtar-1979/episode.yaml`. Süreler toplamı 14,0; `faces:` alanı YOK.

## 9. Görseller: lisans, kaynak, arka plan, kanıt, son kare

**Lisans.** Yalnız kamu malı, CC0, CC BY, CC BY-SA. Lisansı Commons ham dosya sayfasından doğrula
(`commons.py bilgi` ya da `index.php?title=File:<ad>&action=raw`); API'nin "Public domain" kısa adı ve "Own work" etiketi
yetmez. Yazar/kredi metni `extmetadata` Artist ve ImageDescription alanından. "PD" sivil fotoğraf ülkeye göre riskli: ABD
hükümeti (FBI, NARA), ABD'de 1929 öncesi yayın, yazarı 70+ yıl önce ölmüş eser güvenli; şüphede başka görsel ya da BEKLET.
Serbest görsel yoksa **kendi gerçekçi kupürümüz/belgemiz** (uydurma manşet yok; söz kaynaktan birebir; gazetenin logosu,
adı, fontu, düzeni taklit edilmez; altta "Kaynak: <yayın>, <tarih>"; komşu sütunlar rastgele harften ve bulanık;
açıklamaya "Son kare canlandırmadır; söz <yayın>, <tarih>" / en: "The final frame is a recreation; the quote is from
<publication>, <date>."). Örnek üretici: `episodes/gobeklitepe-mezar-tasi/kupur.py`.

**Kaynak sırası.** Commons (`commons.py`) → Internet Archive (kitap/gazete taraması:
`archive.org/download/<id>/page/n<leaf>_w2000.jpg` ya da `_w4000`; sayfa → leaf için `<id>_page_numbers.json`, metin için
`<id>_djvu.txt`) → LOC. Openverse güvenilmez (zaman aşımı); Chronicling America/loc.gov bu ortamdan 403 verebilir.
Commons'ta küçük resmi yalnız standart genişlikte iste (temas sayfası 330/500; kullanılacak görsel 960/1280/1920);
`thumbnail_unscaled` dönen yol 429'da kalır. `commons.py` bunu ve geri çekilmeyi zaten yapar.

**Arka plan.** Olayın gerçek yeri, tanınır açıdan, gün ışığı, renkli; yoksa aynı türden yer (dönem gemisi, eski film
fotoğrafı "<yer> (1993)"). Modern öğe yok: tabela, şerit, araba, korkuluk, kablo, turist, çöp kutusu; tek konuşmacılı
sahnede karşı yarı hep açıktadır, oraya da bak. Kenarda yarım kalan yapı parçasını kırpımla at. Hedef: parlaklık ~115-130,
doygunluk 0,20-0,27 (en çok 0,30; gün batımı/kartpostal göğü reddedilir), kenar Laplace varyansı ~20 (720 ölçeği, yazısız
bölgede ya da `img/` dosyasında ölç). Blur: küçültülmüş keskin taş/iç mekân 1,2-1,8; yaprak/gökyüzü/zaten yumuşak 2,2-3,0.
Renk: `ImageEnhance.Color(0,6-0,85)` + `Brightness(0,9-0,95)`; değişikliği `credits`'e yaz.

**Kanıt.** 1080 genişlik, 537-816 px yükseklik; kareye sığdırılan daha uzun görsel yanlarda bant bırakır, önceden kırp.
Telefonda okunmalı (390 px'te bak): manşet büyük harf yüksekliği ≥ 35 px, nesne kadrajın çoğunda, sıkı kırpım. 1,5 kattan
fazla büyütmeden kaçın. Belgeyi tam satırda kes. Gazete sayfasında komşu haberlere bak (çocuk ölümü vb. kadraja girmesin).
Kimliği doğrulanmamış belge kullanma (birim numarasını, arşiv kimliğini kontrol et). İki kanıt aynı fotoğraftan olmasın.
Soluk taramada yalnız `autocontrast`/gama; manşet piksellerine dokunma. Dikey nesneyi 1080x816'ya nesnesiz kenarı uzatarak
tamamla (ayna değil). Sıra soruya göre: önce "kim/nerede", son kare cevap.

**Son kare kataloğu** (bir önceki bölümün son karesiyle aynı tür arka arkaya gelmesin; son 5 bölümün RAPOR'una bak):
gerçek kamu malı gazete sayfası (ABD 1929 öncesi; 1926 Daily Herald) · kitap/seyahatname sayfası (Internet Archive) ·
dönemin minyatürü/resimli kroniği · kamu malı tablo (ressam 70+ yıl önce ölmüş) · arşiv fotoğrafı (kamu malı; SALT
"No restrictions") · müze nesnesinin yakın planı · nesne + resmî levha · hatıra pulu (`{{PD-TR}}`) · mühendis çizimi/teknik
levha · olayın geçtiği odanın bugünkü fotoğrafı · gerçekçi kupür (yalnız serbest belge yoksa).
Olayın kendi nesnesi yoksa benzer dönem nesnesi olduğunu metinde ve `ek_maddeler`'de açıkça yaz.

## 10. Karakterler ve bakış

- Önce `assets/kit/` (klasik ve öteki kitler, hazır yüz varyantlarıyla), sonra `python tools/wojak_site.py
  search|sheet|get` (wojakland/wojakparadise) ve `python tools/wojak_lib.py search|sheet|get` (kütüphane). Rol + kostüm +
  dönemle ara, milliyetle değil. Örnek sorgu: `wojak_site.py sheet "worker|miner|turban|peasant" --site wl`.
- **Her PNG'yi tam boyda aç:** filigran/imza/site adı yok mu (ör. `victorian_man_wojak` şapkasında yazı var), baş tepesi
  kapalı mı (500x500 kütüphane PNG'leri kesik olabilir), yükseklik ≥ ~600 px mi (küçükse 2-3x LANCZOS + `UnsharpMask(2,60,2)`,
  yüz çizimini büyütülmüş tuvalde yap). Düz MS-Paint ailesi: gölgeli/ressamsı çizimi düzleştir ya da kullanma.
- Dönem: fes 1829 sonrası; turuncu/kırmızı silindir takke telefonda fes okunur; ülke işareti (ponpon, yazı) silinir.
  Uygun dönem karakteri yoksa RAPOR'da bilinen kusur. A ve B farklı taban yüz olsun ("tek ailede iki yüz" olmasın).
- Boy: `height` 0,42-0,55 (medyan 0,48; 0,55 üstü `[stil]` uyarısı). İki konuşmacı aynı `height` (yazı bloğu sabit kalsın).
  Uzun başlıklı (kavuk, fes, taç, kask) karakterde PNG'yi göğüsten/sakalın altından kes: yüz büyür; çene kesilmesin.
- **Ters köşe yüzü** telefonda (390 px, eşik 40) yüz bölgesinin **≥ %0,40**'ı değişmeli. Çalışan tarif: iri yuvarlak göz +
  küçük göz bebeği, iç ucu kalkık kalın kaş, "O" ağız, alında 4-5 düzensiz mavi çizgi (yanağa değil: gözyaşı sanılır),
  başın önünde kontur dışında ~20 px uzakta 3 damla. Yalnız ter damlası yetmez (en kanalında defalarca 7'de kaldı).
  Kit varyantı seçerken silüet aynı olsun (en: `klasik/gozyasli` uyuyor; `agliyor` silüeti farklı, `uzgun` 205 px).
- Düzenleme `episodes/<id>/chars/uret.py` ile (önceki bölümlerdeki `uret.py`'leri kopyala); renk değiştirirken bağlı bölge
  (`scipy.ndimage.label`) kullan, düz eşik komşu bölgeleri de boyar. Koordinatı küçültülmüş önizlemeden değil gerçek boyuttan al.
- **Bakış:** `faces:` asla. Her PNG (varyantlar dahil) için DOSYANIN KENDİ baktığı yön: `python -m wojak yon <png> --yon
  sag|sol|on` (burun ve göz bebekleri dosyada hangi yana). Aynalamayı motor yapar. Render sonrası
  `python -m wojak bakis episodes/<id>` → `out/<id>/kareler/bakis.jpg`: soldakinin yüzü ve göz bebekleri sağa, sağdakinin
  sola. Sakin ve şok varyantının göz bebeğini ayrı ayrı kontrol et. `teslim` kayıtsız ya da çelişkili bakışta durur.
  Varyantı yeniden ürettiysen yeniden kaydet. `data/karakter_yon.json` commit edilebilir: `git diff` ile bak, yalnız kendi
  girdilerin kalsın, eski sha1 girdilerini `facing.py` biçimini bozmadan sil (başkasının girdisine dokunma).

## 11. Hakemlerden önce yap (ilk turda en sık düşülenler)

**TR (13 bölüm, sıklık sırasıyla):**
1. Ters köşe yüz değişimi telefonda %0,40 altı ya da yüz başlık altında küçük (7/13) → §10 tarifi, PNG'yi göğüsten kes.
2. Arka plan keskin/doygun ya da modern öğeli (7/13) → Laplace ~20, doygunluk ≤ 0,27, kırpımı iki yarıdan kontrol et.
3. Satır sonunda yetim kelime ya da özel adın bölünmesi (6/13) → 55 px'te satır ~26-27 karakterde kırılır; virgülde elle
   `\n` ya da kısalt ("THY"); `frames` şeridine bakmadan render etme.
4. Başlık (6/13): ters köşeyi söylüyor (MUST), fiil kaynaktan gevşek, somut yer yok, kapak cevabı veriyor.
5. Olgu/alıntı kesinliği (6/13): kısaltılmış alıntı (MUST), tarih kaynakla uyumsuz, tartışmalı pay kesin hüküm gibi.
6. Kanıt telefonda soluk/küçük (3/13), dönem dışı kostüm (3/13), sansürün bozduğu kelime (2/13).

**EN (7 bölüm, ilk turda toplam 38 MUST):**
1. Ters köşe yüzü zayıf ya da bozuk (6/7): yalnız ter damlası, farklı silüetli varyant, dışa bakan göz bebeği.
2. Tek kaynaklı/tartışmalı olgu (5/7): yaş, tarih, mesafe; çelişkiyi tek cümlede söyle ya da çıkar.
3. Arka plan doygun ya da düz (5/7): gün batımı, düz gökyüzü (Laplace ~2), kartpostal görünüm.
4. Sansür "died" → "d*ed" (5/7). Kanıt küçük/okunmaz (4/7): 339-482 px, 17 px başlık, yarım satır.
5. Kredi metni (4/7): yazar, lisans bağlantısı, yapılan değişiklik eksik ya da "not cropped" gibi yanlış; "Images: Images".
6. Karakter PNG'si (3/7): kesik baş, 205 px kaynak, filigran. Kancada bağlam yok (2/7).

**Ön kontrol listesi (render'dan sonra, hakemden önce; tek betikte):**
- Ses: `ffmpeg -i teslim/<id>/<id>.mp4 -af ebur128=peak=true -f null - 2>&1 | grep -E "I:|Peak:" | tail -2` → ~-29,6 LUFS.
- Süre ffprobe ile (render satırındaki süre yanlış basabilir); kesmeler 0,5 ızgarasında, sahneler durağan.
- Telefon boyu (390 px) şerit: yetim kelime, yüz değişimi, kanıt okunurluğu, modern öğe, kostüm dönemi.
- `bakis.jpg`: herkes içeri bakıyor, çeneler ve baş tepeleri kadrajda.
- Sansür: `grep -nE '\*|!|[a-zçğıöşü]0[a-zçğıöşü]' teslim/<id>/metinler/*.txt` ile bozuk kelime ara. TR: "ölüm" → "vefat", "son nefesini verdi";
  "silahdar", "silahsızlandırmak", "bombaladı" yerine unvansız ad, "alıkoymak", "topa tuttu". EN: died/dead/death/corpse →
  "passed away", "did not survive", "lost their lives", "body"; "bomb" → "explosive device".
- Başlığı son replikle karşılaştır; kapak cevabı vermiyor.
- Metin uzunluğu (kelime ve karakter), kredi satırı tam, `ek_maddeler`'de canlandırma notu.

## 12. Teslim öncesi kontrol listesi

**Yapı:** `check` uyarısız · 13,5-14,0 sn, 0,5 ızgarası · tek kart, ileri zaman · kanıt sonda, sonrasında hiçbir şey yok.
**Replik:** iki kişi, aynı yer ve an, A solda B sağda · ilk replik kanca · son diyalog ters köşe (aynı kutu, yüz varyantı)
· nokta/üç nokta yok, yetim kelime yok · hiçbir replik olguyla çelişmiyor, gerçek kişiye uydurma söz yok.
**Karakter:** düz hazır wojak, filigransız · duyguya uygun yüz, kötü yüz yalnız kötüde · `yon` kayıtlı, `bakis.jpg` temiz ·
yüz değişimi ≥ %0,40 · boy 0,42-0,55 · kostüm döneme uygun ya da kusur RAPOR'da.
**Arka plan ve kanıt:** tek (en çok iki) renkli gerçek fotoğraf, modern öğe yok · kanıtlar 1080 genişlik, 537-816 px, ek
yok · son kare sorunun cevabı, bir önceki bölümle aynı tür değil.
**Ses, kapak:** imza müzik ~-29,6 LUFS, efekt yok · `kapak.jpg` doğru sahne, etiketsiz.
**Metinler:** başlık sonu söylemiyor · hikâye 150-250 kelime, soruyla biter · açıklama ≤ 2.200 karakter · `metinler/*.txt`
sansürden sonra okundu · `ek_maddeler`'de canlandırma notu, ilk yorum önerisi.
**Olgu, lisans, mahremiyet:** her olgu ≥ 2 kaynak, çelişen sayı yuvarlandı ya da çıktı · her görselin lisansı ve değişikliği
`sources`'ta, CC atfı `credits`'te · telifli görsel yok · reşit olmayan/özel kişi bilgisi hiçbir dosyada yok.
**Süreç:** iki bağımsız hakem ≥ 8, MUST yok (ya da BEKLET) · BEKLET kararı verildi · `git status` temiz (mp4, telifli,
özel font/ses, referans yok).

## 13. Teslim paketi ve RAPOR

- Paket (`python -m wojak teslim`): `<id>.mp4`, `kapak.jpg`, `paylasim.md`, `metinler/`; özel depoya bunlar + `RAPOR.md`
  (+ gerekiyorsa `BEKLET`). `teslim` klasörü yeniden kurar: RAPOR'u teslimden SONRA yaz ya da kopyala.
- **RAPOR.md** (kısa, ~60-90 satır): BEKLET durumu ve gerekçesi · konu ve "Ne?!" cümlesi, öbür iki aday · sahne listesi ·
  başlık seçenekleri · hakem turları (puan, MUST, uygulanan düzeltme; puanlar hakem raporundan değiştirilmeden) · bilinen
  kusurlar · lisans tablosu · adım süreleri (tek tablo) · alt ajan çağrıları.
- Özel depo: tek commit, Türkçe konu ("Teslim: <id> (iki hakemden 8/8, telifsiz, BEKLET yok)"), push. Son commit botun
  olabilir: yazarı açıkça ver (`git -c user.name=Claude -c user.email=noreply@anthropic.com commit ...`).
- Herkese açık `wojak`: `git pull --rebase` sonra commit ve push (oturumun dalı); konu satırı aynı biçimde.

## 14. Oturum sonu: dersler

- `docs/OGRENILENLER.md`'ye artık **ekleme yapılmaz**.
- `docs/DERS_KUTUSU.md`'ye en çok **10 satır**, yalnız bu el kitabında ve kutuda olmayan gerçekten yeni ders (tarih + bölüm
  id). Süre tablosu, tekrar eden ders, ortam şikâyeti yazma.
- Kod önerisi `docs/KOD_ONERILERI.md`'de yoksa tek satır olarak eklenir; varsa dokunma.
- Kutu haftada bir bu el kitabına işlenir ve boşaltılır.

## 15. İhtiyaç olursa (dizin; yalnız ilgili bölümü aç)

| Gerekirse | Nereye bak |
|---|---|
| Ölçülerin tamamı (yerleşim, süreler, karakter, yazı, arka plan, kart, kanıt, ses, kapak) | `docs/STIL.md` §1-§13 |
| Gerçek senaryo örnekleri ve boş şablon | `docs/STIL.md` §14 |
| İlk denemelerdeki 34 hata | `docs/STIL.md` "Ek: ilk denemelerimizdeki hatalar" |
| Diyalog iskeleti, ters köşe görseli, kanıt sırası, olgu disiplini | `docs/OGRENILENLER.md` §2.4-§2.7 |
| Hata türleri tabloları (karakter, replik, kanıt, arka plan, yazı, zamanlama, hikâye metni, lisans, mahremiyet) | `docs/OGRENILENLER.md` §3.1-§3.11 |
| Gerçekçi kupür nasıl üretilir | `docs/OGRENILENLER.md` §6.1; `episodes/karun-hazinesi-bros/kupur.py`, `episodes/gobeklitepe-mezar-tasi/kupur.py` |
| Piksel düzenleme tarifleri (kontur sabitleme, leke/gölge temizliği, sakal içinde ağız, takke boyama, gözyaşı silme, ponpon/yazı silme, gölgeli çizimi düzleştirme) | `docs/arsiv/OGRENILENLER_oturum_notlari_2026-10.md` (bölüm başlığındaki id) ve o bölümün `chars/uret.py`'si |
| Internet Archive sayfa indirme, NYT/İngiliz gazete sayfası, pul, minyatür, SALT arşivi ayrıntısı | aynı arşiv dosyası: `yerebatan-bodrum-balik`, `goeben-fes-1914`, `hezarfen-galata-ucusu`, `kanuni-gizlenen-olum`, `karakoy-tunel-1874` bölümleri |
| EN kanalına özgü eski dersler | aynı arşiv dosyası, "EN kanalı" bölümleri; `docs/OGRENILENLER.md` "EN kanalı" |
| Dramatik ironi, yerellik, kanalın neden tuttuğu | `docs/KONSEPT.md` §2 |
| Etik çizgi | `docs/KONSEPT.md` §8 |
| Güncel olay: seçim, hız, yayın öncesi liste, hukuki kırmızı çizgiler | `docs/GUNDEM.md` §5, §7 |
| Konu havuzu | `docs/KONU_HAVUZU.md` |
| YouTube ihlali ve yayın planı | `docs/YAYIN_PLANI.md` §0 |
| Hakem ve yapımcı istemleri | `docs/is_akislari/kisa_reel.js` (içindeki uzun okuma listesi yerine bu dosyayı ver) |
| Teslim/sırlar kurulumu | `docs/GEREKENLER.md`; `docs/ADIM_ADIM.md` §1 |
| Uzun video | `docs/ADIM_ADIM.md` §4, `docs/UZUN_FORMAT.md`, `docs/UZUN_MOTOR.md`, `docs/OGRENILENLER.md` §7 |
| Hesap sahibi geri bildirimlerinin tam tablosu | `docs/OGRENILENLER.md` en üstteki tablo |
