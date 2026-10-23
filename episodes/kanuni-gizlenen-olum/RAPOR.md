# kanuni-gizlenen-olum: üretim raporu (23.10.2026, A sürümü; telifli görsel yok)

> **Yayın durumu:** BEKLET **yok**. Hassas konu kuralının hiçbir maddesine girmiyor: 1566'da geçen tarihî bir olay;
> güncel olay değil (GUNDEM §5/§7 kapsamı dışı), çocuk yok, son 10 yılda ölen yok, yaşayan özel kişi yok, süren
> dava yok. Lisans kararı bekleyen görsel yok (hepsi kamu malı). İki hakem 8/8, MUST yok.

**Konu:** Kanuni Sultan Süleyman 6/7 Eylül 1566 gecesi Zigetvar kuşatmasında öldü. Sadrazam Sokullu Mehmed Paşa
ölümü 42-48 gün ordudan gizledi: askere "padişah hasta" dendi, fermanlar onun ağzından yazıldı, dönüşte "hasta
padişah arabasında" dendi. Kale, padişahın ölümünden hemen sonra düştü.

## Ortam

4 çekirdek, 15 GB RAM, 30 GB boş disk, Python 3.11.17, ffmpeg 6.1.1. Avenir fontu ve 76 referans reel kuruldu,
render Avenir ile yapıldı. Testler: 72/72 geçti. `grep MUSIC_IMZA wojak/config.py` → `imza_v2_golge.m4a`.

## Konu gerekçesi (3 aday)

| Aday | Neden | Karar |
|---|---|---|
| **Kanuni'nin gizlenen ölümü (Zigetvar, 1566)** | Tek cümlelik "Ne?!": ordu haftalarca ölü bir padişahın "emriyle" yürüdü. Dramatik ironi kanalın imza kalıbına birebir uyuyor: "müjdeyi padişaha ben vereyim" → "padişah neden hiç konuşmuyor?". Türk tarihi; 10+ bağımsız kaynak (AA, Vikipedi, Afyoncu, İlber Ortaylı, Daily Sabah, HistoryNet, Smithsonian). Kanıt olarak olayı birebir gösteren 16. yüzyıl Osmanlı minyatürleri var (kamu malı). AA'nın Eylül 2026'daki 460. yıl haberi gündem kancası. Grafik içerik, çocuk ve mağdur yok | **Seçildi** |
| Ayasofya'daki Viking yazısı (Halfdan) | İstanbul'da, eğlenceli ironi, Commons'ta CC fotoğrafı var. "Ne?!" etkisi orta, karanlık/gizem tonu yok | Yedek |
| Piri Reis haritasının 1929'da Topkapı'da bulunuşu | Kamu malı kanıt, Türkiye'de geçiyor. Ters köşesi zayıf; "Antarktika" iddiaları tartışmalı | Yedek |

Kanalda yapılmadığını kontrol ettim: `data/videos.csv` (223 başlık), `data/instagram_reels.csv`, `data/olay_metinleri.md`,
`docs/KONU_HAVUZU.md`, `episodes/`, `uzun/` ve `wojak-ozel/teslim/` (yalnız karun-hazinesi-bros var). Kanuni,
Zigetvar, Sokollu, Halfdan ve Piri Reis hiçbirinde geçmiyor. Son bölümden (Karun broşu, müze hırsızlığı) konu olarak uzak.

## Sahne akışı (14,0 sn)

| Zaman | Sahne | Replik |
|---|---|---|
| 0-2,5 | Yeniçeri (sol, gözleri kapalı sevinç) | Paşam, kale düştü, müjdeyi padişaha ben vereyim |
| 2,5-5,0 | Sadrazam (sağ, ciddi) | Olmaz, padişahımız hasta, kimseyi kabul etmiyor |
| 5,0-6,5 | Kart | Birkaç hafta sonra |
| 6,5-8,5 | Sadrazam (aynı yüz) | Padişahımız arabasında, yola çıkıyoruz |
| 8,5-10,5 | Yeniçeri, aynı kutu, **şok yüzü** (iri gözler, açık ağız, mavi soğuk ter, damlalar) | Bekle, padişah neden hiç konuşmuyor? |
| 10,5-12,0 | Kanıt 1 | Naaşı taşıyan araba, padişahın sarığı içinde (Seyyid Lokman minyatürü, 1579-80) |
| 12,0-14,0 | Kanıt 2 (son kare) | Naaş Belgrad'a varıyor, II. Selim siyah kaftanla arabanın önünde dua ediyor (Nüzhet-i Esrâr minyatürü, 1568-69) |

Arka plan: Zigetvar kalesinin gerçek surları. Müzik: `music: kanal` (imza_v2_golge), -29,6 LUFS, tepe -17,0 dBFS.
**Son kare çeşitliliği:** son 5 bölümün son kareleri: Karun (kendi kupürümüz), Talidomit (mobil haber sayfası),
Kız Kulesi (sergi kartı), Çanakkale (gazete sayfası), Van (mobil manşet). Bu bölüm **arşiv minyatürüyle** bitiyor:
olay basında değil, Osmanlı vakanüvislerinin resimli kroniklerinde kayıtlı. Kupür ya da kart yok.

## Hakem puanları

Hakemler ayrı bağlamda çalıştırılamadı. Her tur sıfırdan yürütüldü: yalnız `kisa_reel.js` içindeki JUDGE_VISUAL ve
JUDGE_FOLLOWER istemleriyle ve yalnız teslim dosyalarına (mp4, kapak, metinler) bakarak. Ölçüm araçları:
- 0,5 sn'lik kareler; C2kk, C4V3, C12O ve C2Fr ile aynı ölçekte yan yana sayfa;
- yüz kırpımları (C4V3, C2Fr ile);
- kare farkıyla kesme tespiti, ebur128, telefon boyu (390 px), yüz değişim alanı.

| Tur | Görsel | Takipçi + olgu | MUST | Not |
|---|---|---|---|---|
| Ön kontrol (üretici) | — | — | 3 | Ses -15,5 LUFS (ffmpeg hatası, aşağıda); yüz değişimi telefonda %0,33 (eşiğin altı); 2 replikte satır sonunda yetim kelime |
| 1 | 8 | 8 | yok | SHOULD: arka plan orijinallerden keskin (blur 2,5 → 3,2); metinde "Turbék" → "Turbek", ilk cümlede "vefat" tekrarı |
| **2** | **8** | **8** | yok | Durma noktası (iki hakem ≥ 8, MUST yok) |

Ön kontrolden sonra yapılanlar:
- Ses: `music: {file: kanal, volume: 0.197}` ile -29,6 LUFS.
- Yeniçeri PNG'si bilekten kesildi (kadrajın altında zaten kesik). Aynı boyda yüz %17 büyüdü, şok gözleri ve ağzı
  büyütüldü. Telefonda yüz değişimi %0,33 → %0,48 oldu (C12O %0,40, C2Fr imamı %0,77).
- Satır kırımları elle yapıldı. Hikâye metninde sansürün bozduğu kelimeler ("*lüm", "S!lahdar") yerine "vefat"
  ve "Cafer Ağa" kullanıldı; metinlerde yıldızlı kelime kalmadı.

Hakemlerin gerekçesi:
- **Görsel 8:**
  - Biçim, süre, kesmeler ve ses STIL'e birebir uyuyor. Yazı bloğu reel boyunca sabit.
  - Karakterler hazır kıyafetli, içeri bakıyor. Yüz varyantı telefonda okunuyor.
  - Arka plan gerçek mekân, kanıtlar tam genişlik ve y=960'ta.
  - Puanı sınırlayan: son karede kalın manşet yok, minyatür telefonda 1,5-2 sn'de "cenaze" diye okunuyor ama bir
    manşet kadar anında değil. Yeniçeri çizimi klasik beyaz wojak'tan daha renkli (C2Fr'deki kadın gibi kabul edilebilir).
- **Takipçi 8:**
  - Kanca 1 sn'de oturuyor: tarihi bilen "Kanuni zaten ölmüştü" diye ürperiyor.
  - Replikler doğal konuşma Türkçesi. Ters köşe "Bekle, ... neden ...?" kalıbında. Başlık spoiler vermiyor.
  - 8 olgu kaynaktan doğrulandı: 6/7 Eylül, kale hemen ardından düştü, 42-48 gün, Sokullu, "Hasta padişah
    arabasında" (İlber Ortaylı), Selim'in Belgrad'da beklemesi, 13. sefer, Turbek 2015.
  - Puanı sınırlayan: sadrazamın beyaz kavuğu ve sakalı Kanuni ikonografisine benziyor; "Paşam" ve "padişahımız"
    sözleri rolü açıklıyor.

## Bilinen kusurlar

1. Son kare minyatür. Telefonda anlam (padişahın cenazesi) kalın bir manşet kadar anında okunmuyor; hikâye metni
   bunu açıklıyor.
2. Sadrazam çizimi ("Sultan Chad") Kanuni'nin bilinen görünümüne benziyor. Bazı izleyiciler onu padişah sanabilir.
   S1'deki "Paşam" ve S2'deki "padişahımız" sözleri rolü gösteriyor.
3. İki karakter de izinli boyun üst sınırında (`height: 0.55`). Yeniçerinin uzun börkü yüzünü küçültüyordu,
   yazı bloğu da iki karakter için aynı yükseklikte kalmalıydı.
4. Gün sayısı kaynaklarda 42-48 arası. Ekranda sayı yok, metinde aralık var.
5. Arabada padişaha benzeyen hizmetkâr anlatısı tartışmalı. Metinde "bazı kaynaklara göre" diye geçiyor, ekranda yok.

## Lisans kararları

Lisans kararı bekleyen görsel **yok**. Telifli görsel hiçbir sürümde yok; yalnız A sürümü var.

| Görsel | Kaynak | Lisans | Sürüm |
|---|---|---|---|
| Arka plan `img/arka_szigetvar.jpg` | Commons "Szigetvár vár 3.jpg", Csanády, 2006 (kırpıldı, doygunluk x0,66) | Kamu malı (PD-self; dosya sayfasında doğrulandı) | A |
| Kanıt 1 `img/kanit_1_araba.jpg` | Commons "1566-The Funeral of Sultan Suleyman the Magnificent-left-large.jpg"; Seyyid Lokman, Tarih-i Sultan Süleyman, Chester Beatty Library T 413, 1579-80 (kırpıldı) | Kamu malı (PD-US, 16. yy) | A |
| Kanıt 2 `img/kanit_2_belgrad.jpg` | Commons "The body of Suleiman I arrives to Belgrade, Selim II is waiting for it A.jpg"; Feridun Ahmed Bey, Nüzhet-i Esrârü'l-Ahyâr, Topkapı H.1339 107b, 1568-69 (kırpıldı) | Kamu malı (PD-Art, PD-old-100-expired) | A |
| Karakter A (yeniçeri) | wojakland "Janissary Ottoman Feels Good Wojak" + kendi yüz varyantımız | Topluluk memesi (wojakland'de şart sayfası yok; kanalın yerleşik pratiği) | A |
| Karakter B (sadrazam) | wojakland "Sultan Chad" | Aynı | A |

Serbest görsel araması: Wikimedia Commons API, İngilizce, Macarca ve Türkçe sorgularla yapıldı:
- "Suleiman funeral miniature", "Szigetvár 1566 miniature";
- "Szigetvár castle walls", "Szigetvári vár";
- kategoriler: "Funeral of Suleiman I", "Castle of Szigetvár".

Olayı birebir gösteren kamu malı minyatürler bulunduğu için kanıt üretmeye gerek kalmadı. Openverse ve Internet
Archive'a gerek olmadı.

## Adım süreleri (UTC, 23.10.2026)

| Adım | Süre |
|---|---|
| Ölçüm + hazırlık (pip ~50 sn, font, referans çıkarma, 72 test ~24 sn) | ~4 dk |
| Belgeleri okuma (CLAUDE, ADIM_ADIM, STIL, OGRENILENLER, KONSEPT, YAYIN_PLANI §0, GUNDEM §5/§7, kisa_reel.js) | ~4 dk |
| Konu tarama + 3 aday | ~2 dk |
| Olgu araştırması (5 web araması) | ~5 dk |
| Görsel avı (Commons API + md5 yolu; birkaç 429, yeniden denemeyle geçti) | ~6 dk |
| Karakterler + yüz varyantı (`chars/uret.py`) | ~5 dk |
| episode.yaml + check + frames + render + teslim | ~4 dk |
| Ön kontrol düzeltmeleri (ses hatası, yüz boyu) + 2 hakem turu | ~10 dk |
| §4 listesi, RAPOR, teslim kopyaları, commit/push, OGRENILENLER | ~10 dk |
| **Toplam** | **~50 dk** |

**Yaklaşık maliyet:**
- Ücretli API kullanılmadı (TTS ve görsel üretimi yok), 0 TL.
- Model kullanımı oturum içi; ek harcama yok.

## Kod hatası (raporlandı, düzeltilmedi: `wojak/` değişmez)

`wojak/audio.py:_loudnorm` ffmpeg'e `loudnorm=TP=-17` veriyor. ffmpeg 6.1.1'de TP aralığı -9..0; filtre hata
veriyor ve kod sessizce `anull`'a düşüyor. Sonuç: imza müzik dosyasının kendi seviyesi, -15,5 LUFS (STIL hedefi
-29,5). Bu bölümde yaml'da sabit kazançla (`volume: 0.197`) aşıldı. Öneri: TP'yi -9 ile sınırla ve hedefe
kazançla in, ya da `volume` filtresiyle doğrusal ayar yap; `check`/`teslim` ses seviyesini ölçüp uyarsın.
Önceki bölümleri etkileyebilir: bu ortamda render edilen her kısa reel -15 LUFS civarında çıkar.
