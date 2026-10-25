# midas-mezari-altin: üretim raporu (25.10.2026 akşam, A sürümü; telifli görsel yok)

> **Yayın durumu:** BEKLET **yok**. Bölüm hassas konu kuralının hiçbir maddesine girmiyor: konu 1957 kazısı ve MÖ 8.
> yüzyıl mezarı (güncel olay değil, GUNDEM §5/§7 kapsamı dışı), çocuk yok, son 10 yılda ölen yok, yaşayan özel kişi yok,
> süren dava yok. Lisans kararı bekleyen görsel yok: üç fotoğraf da Commons'ta CC (BY 4.0, BY-SA 2.0, BY-SA 4.0);
> lisanslar dosya sayfalarının ham metninden doğrulandı. İki hakem 8/8 verdi, MUST kalmadı.

**Konu:** Ankara Polatlı'daki Gordion'da, efsanede dokunduğu her şeyi altına çeviren Kral Midas'ın adını taşıyan 53
metrelik tümülüs 1957'de açıldı. Tüneli Zonguldak'tan getirilen madenciler kazdı. Mezar hiç soyulmamıştı, ama içinden
tek bir altın eşya çıkmadı: kütük bir oda, 60-65 yaşlarında bir adamın iskeleti, ahşap mobilya ve bronz kazanlar.
Ağaç halkası tarihlemesine göre mezar büyük olasılıkla Midas'ın değil, babası Gordias'ın.

## Ortam

4 çekirdek, 15 GB RAM, 30 GB boş disk, Python 3.11.17, ffmpeg 6.1.1. Avenir fontu ve `referans/` (76 dosya) kuruldu;
render Avenir ile yapıldı. Taze konteynerde `/home/user` yoktu: ilk `ln` başarısız oldu, bir test düştü
(`test_short_youtube_aciklamasi_hikayeyi_tasir`); `mkdir -p /home/user` + bağdan sonra 81/81. `grep MUSIC_IMZA
wojak/config.py` çıktısı `imza_v2_golge.m4a`. İki depo başta ayrık HEAD'deydi; varsayılan dallara
(`claude/kind-albattani-vcp4vk`, `main`) geçilip güncellendi.

## Konu gerekçesi (3 aday)

| Aday | Neden | Karar |
|---|---|---|
| **Kral Midas'ın mezarı açıldı, içinden tek bir altın çıkmadı (Gordion, 1957)** | Tek cümlede "Ne?!": altın dokunuşlu kralın mezarında altın yok. Türkiye'de geçiyor (Polatlı), Türk bağlantısı güçlü (tüneli Zonguldaklı madenciler kazdı; "Midas'ın kulakları" Türk izleyicinin bildiği masal). İroni ("içerisi altın doludur") + ters köşe ("neden hiç altın yok?") kalıba uyuyor. Kaynaklar bağımsız ve güçlü: kazıyı yönetenin 1958 raporu (Penn Expedition), Penn Gazette, Science News, BBC Türkçe/T24, Hürriyet Daily News. Serbest kanıt bol (Commons'ta mezar odası ve bronz kazan, CC). Ağustos 2026'da "Midas'ın değil babasının mezarı" haberiyle yeniden gündemde. Mağdur, çocuk, grafik içerik yok | **Seçildi** |
| Dumlupınar denizaltısı (1953, Çanakkale): batık denizaltıdaki denizcilerle şamandıra telefonuyla konuşuldu | Duygusal olarak çok güçlü ve Türk; ama 81 şehit, aileler hayatta. Ters köşe repliği gerçek kurbanların ağzına söz koymayı gerektiriyor; ton dikkat ister. Kanıt serbest (eski USS Blower'ın ABD Donanması fotoğrafı, kamu malı) | Yedek |
| Zeugma mozaik parçaları 50 yıl bir ABD üniversitesinin deposunda kaldı (2018'de iade) | "Kaçırılan Anadolu eseri geri döndü" teması 21.10'daki Karun hazinesine çok yakın | Elendi |

Kanalda yapılmadığını grep ile kontrol ettim: `data/videos.csv` (223 başlık), `data/instagram_reels.csv`,
`data/olay_metinleri.md`, `docs/KONU_HAVUZU.md`, `episodes/` ve `wojak-ozel/teslim/` (ayasofya, göbeklitepe, hezarfen,
kanuni, karun, kaşıkçı). "Midas", "Gordion", "Dumlupınar", "Zeugma" hiçbir yerde geçmiyor.
**Yakın konu notu:** son bölümlerin çoğu Osmanlı/arkeoloji. Göbeklitepe (24.10) de arkeoloji ironisiydi ("mezar taşı
sandılar, kazmadılar"). Bu bölüm başka bir yer, dönem ve kalıp: kazıldı, beklenen hazine çıkmadı. Karakterler de farklı:
arkeolog yok, iki Zonguldaklı madenci.

## Sahne akışı (14,0 sn)

| Zaman | Sahne | Replik |
|---|---|---|
| 0-2,5 | Genç madenci (sol, gri kasket, bıyık, tulum), arkada tümülüs | Usta, bu tepenin altında / kim yatıyor? |
| 2,5-5,0 | Ustabaşı (sağ, kahverengi kasket, kirli sakal) | Kral Midas, dokunduğu / her şey altın olurmuş |
| 5,0-7,5 | Genç madenci (aynı yüz) | O zaman içerisi / altın doludur |
| 7,5-9,0 | Kart | Bir süre sonra |
| 9,0-11,0 | Genç madenci, aynı kutu, **ters köşe yüzü**: iri göz, iç ucu kalkık kaş, "O" ağız, başın önünde 3 ter damlası | Usta, neden hiç altın yok? |
| 11,0-12,5 | Kanıt 1 | Mezar odasının kütük duvarı ve açılan girişi (Gordion Müzesi yanı, tümülüsün içi) |
| 12,5-14,0 | Kanıt 2 (son kare) | Tümülüsten çıkan sirenli bronz kazan, içi bronz kaselerle dolu (Anadolu Medeniyetleri Müzesi) |

Arka plan: Midas Tümülüsü'nün 1993 fotoğrafı (bugünkü giriş yapısı ve yürüme yolu yok, 1957'ye en yakın görünüm). Tepe
karenin ortasında, iki karakter yanlarda. Renk düzeltildi (doygunluk 0,36 → 0,28, parlaklık 134 → 124). `blur: 2.2`
ölçülerek seçildi (yan şerit Laplace: 2,0 → ~32, 2,5 → ~15; orijinal medyan 22).

Müzik `music: {file: kanal, volume: 0.197}` (imza_v2_golge); ölçüm **−29,6 LUFS, tepe −17,0 dBFS**. Video ve ses
0,000'da başlıyor. Kesmeler kare farkıyla 2,5 / 5,0 / 7,5 / 9,0 / 11,0 / 12,5 sn'de ölçüldü; sahne içi hareket 0,0.
Telefonda (390 px) ters köşe yüz değişimi alt yarıda **%0,87** (eşik %0,40; C4V3 %0,60). Kapak 1. sahne (kanca: dev
tepe + "kim yatıyor?").

**Son kare çeşitliliği:** son 5 bölümün son kareleri: Hezarfen (pul), Kaşıkçı (müze nesnesi), Göbeklitepe (renkli
kupür), Ayasofya (yazıt + levha), Kanuni (minyatür). Bu bölüm **müze nesnesiyle** bitiyor: Kaşıkçı'dan iki bölüm sonra,
arka arkaya değil. Olay basından çok kazı raporuyla bilindiği ve cevap ("altın değil bronz") nesnenin kendisi olduğu
için kupür yapılmadı. Kupür ya da canlandırma kart yok.

## Hakem puanları

Hakemler ayrı bağlamda çalıştırılamadı. Her tur sıfırdan yürütüldü: yalnız `kisa_reel.js` içindeki JUDGE_VISUAL ve
JUDGE_FOLLOWER istemleriyle, yalnız teslim dosyalarına (mp4, kapak, metinler) bakarak. Ölçümler:
- 0,5 sn kareler; C2kk, C4V3 ve C2Fr ile aynı ölçekte yan yana sayfa
- 1:1 yüz kırpımları; telefon boyu (390 px) kareler; yüz değişim alanı
- kare farkıyla kesme tespiti; sahne içi fark; ebur128
- arka plan kenar Laplace varyansı (720 ölçeği), parlaklık ve doygunluk
- ekran, başlık ve metindeki olguların kaynak eşlemesi (12 olgu)

| Tur | Görsel | Takipçi + olgu | MUST | Not |
|---|---|---|---|---|
| Ön kontrol (üretici) | — | — | 0 | Yanaktaki mavi ter çizgileri telefonda gözyaşı gibi okunuyordu (alın kasketin altında): kaldırıldı, "O" ağız büyütüldü, ter damlaları kasket siperliğinden uzaklaştırıldı. İki karakter göğüsten kesildi ki aynı `height`ta yüz büyüsün |
| 1 | 8 | 7,5 | 1 | Takipçi MUST: başlık ("Kral Midas'ın mezarını açtılar, içinden tek bir altın çıkmadı") ters köşeyi baştan söylüyordu (KONSEPT §4: spoiler değil) → "Kral Midas'ın mezarına tünel kazan Zonguldaklı madenciler". Takipçi SHOULD: yahni "kuzu" değil kaynakta "koyun ya da keçi", içki "bal şarabı" → kaynaktaki gibi yazıldı. Görsel: MUST yok; tavan notları aşağıda (B'nin düşük çözünürlüklü kaynağı, kanıt 1'in telefonda "ahşap duvar" gibi okunması) |
| 2 | 8 | 8 | yok | Görsel: format, süre, yazı, kesmeler, bakış ve kanıt yerleşimi orijinallerle uyumlu; arka plan gerçek yer ve doğal renk. Takipçi: kanca 1. saniyede (dev tepe + "kim yatıyor?"); "altın" tohumu S2 → S3 → S5; replikler konuşma dili; olgular kaynakla birebir; başlık merak boşluğu + iki somut ayrıntı (Midas, Zonguldak). Durma noktası: iki hakem ≥ 8, MUST yok |

## Başlık seçenekleri

1. **Kral Midas'ın mezarına tünel kazan Zonguldaklı madenciler** (yayında)
2. Polatlı'daki 53 metrelik tepenin altından çıkan kral
3. Dokunduğu her şeyi altına çeviren kralın mezarını 1957'de açtılar

## Lisans tablosu

| Görsel | Kaynak | Lisans | Sürüm |
|---|---|---|---|
| Arka plan: Midas Tümülüsü, 1993 (kırpıldı, renk düzeltildi) | Commons, "Gordion Midas mound (1993).jpg", Mark Landon | CC BY 4.0 | A |
| Kanıt 1: mezar odasının kütük duvarı (kırpıldı) | Commons, "Tumulus of King Midas 03.jpg", Carole Raddato (Flickr) | CC BY-SA 2.0 | A |
| Kanıt 2 (son kare): sirenli bronz kazan, Anadolu Medeniyetleri Müzesi (kırpıldı) | Commons, "Museum of Anatolian Civilizations Phrygian Smaller sirens' cauldron in 2019 06.jpg", Dosseman | CC BY-SA 4.0 | A |
| Karakter A: genç madenci | wojakland "Worker 2 Wojak" (yüz varyantı bizim) | wojakland, şart yok | A |
| Karakter B: ustabaşı | wojakland "Worker Wojak" (aynalandı) | wojakland, şart yok | A |

B sürümü (telifli) **yok**. Telifli görsel hiçbir sürüme girmedi. Lisans kararı bekleyen görsel yok.

**Serbest görsel araması** (Commons API, `generator=search` + `extmetadata`; lisanslar `action=raw` ile doğrulandı):
- "Tumulus MM Gordion", "Midas tumulus": tümülüs dışı (5), giriş/koridor (6), mezar odası içi (9), müze
  rekonstrüksiyonu (1) adayı; 26 küçük resimlik temas sayfasında karşılaştırıldı.
- "Gordion cauldron", "Gordion bronze Museum of Anatolian Civilizations", "Gordion bowls tumulus bronze": büyük ve
  küçük sirenli kazan, aslan/koç başlı situla fotoğrafları (CC BY-SA 2.0/4.0). Bir vitrin fotoğrafında kafatası
  göründüğü için o dosya elendi.
- 1957 kazı fotoğrafları (Penn Museum arşivi) telifli; kullanılmadı. Commons'ta yeterli serbest görsel bulunduğu
  için Openverse ve Internet Archive'a gerek kalmadı.

## Olgu tablosu (özet)

| Olgu | Güven | Kaynaklar |
|---|---|---|
| Tümülüs 53 m yükseklik, ~300 m çap; Gordion, Polatlı | Y | Penn Expedition (Simpson); Hürriyet Daily News; T24/BBC |
| 1957'de Pennsylvania Üniversitesi Müzesi, Rodney Young; önce sondajla oda bulundu | Y | Penn Expedition (Simpson); Archaeology Magazine (2026) |
| Tüneli Zonguldak maden bölgesinden getirilen madenciler kazdı | Y | Young 1958 (Penn Expedition); Hürriyet Daily News; HeritageDaily; Penn Digital Gordion |
| Kendi ustabaşıları, üç vardiya gece gündüz | D (birincil kaynak) | Young 1958 → metinde "Young'ın anlattığına göre" |
| Taş duvar, kütük katmanları, ahşap oda | Y | Young 1958; Penn Expedition (Simpson) |
| Mezar soyulmamıştı | Y | Broad Street Review ("untouched"); Popular Archaeology ("intact") |
| Altın yoktu | Y | Penn Expedition ("contained no gold"); Penn Gazette ("no trace of gold"); Science News; Penn Almanac |
| İskelet 60-65 yaş | Y | Young 1958; Penn Gazette |
| Bronz kazanlar, kaplar, fibulalar | Y | Penn Gazette; Popular Archaeology; Hürriyet Daily News (99 fibula) |
| Oda ~MÖ 740; Midas MÖ 709'da hayatta; büyük olasılıkla Gordias; mezarda ad yok | Y | Penn Expedition (Tumulus MM); T24/BBC; Hürriyet Daily News; Ancient Origins |
| Cenaze yemeği: koyun/keçi etli mercimekli yahni; şarap + bira + bal şarabı | Y | Penn Expedition (Tumulus MM); Popular Archaeology; Science News |
| Eserler Anadolu Medeniyetleri Müzesi ve Gordion Müzesi'nde | Y | HeritageDaily; Penn Digital Gordion |

Verilmeyenler: tünel uzunluğu (82 m / ~70 m / ~230 ft çelişiyor), bronz kap sayısı (180+ / "onlarca" → "çok sayıda").

## Bilinen kusurlar

- **Ustabaşının kaynağı düşük çözünürlüklü:** wojakland "Worker Wojak" 464x463; ekranda ~1,2 kat büyüdü. Telefonda
  net, 1:1'de hafif yumuşak. Kirli sakal kaynağın kendi çizimi (çene boyunca karalama); 1:1'de dikiş izi gibi
  görünebilir, telefonda sakal okunuyor.
- **Kanıt 1 telefonda "ahşap duvar" gibi:** mezar odasının kütük duvarı ve girişi; odanın "mezar" olduğunu metin
  söylüyor. Sağda küçük kırmızı bir merdiven ve beyaz kablo (bugünkü koruma düzeni) görünüyor; piksellere dokunulmadı.
- **Son kare müze vitrini:** kazan bugünkü müze ışığında; 1957 kazı fotoğrafları telifli olduğu için kullanılmadı.
- **İki madenci de kasketli:** bilerek (1950'lerin işçisi); tulum + bıyık ile ceket + kirli sakal ayrımı telefonda
  okunuyor.
- **Arka plan 1993 fotoğrafı:** sahne 1957; fotoğraf 36 yıl sonra çekildi. Tepe çıplak bozkır; bugünkü giriş yapısı
  ve yürüme yolu kadrajda yok.
- **Konu dizisi:** son bölümlerin çoğu tarih/arkeoloji. Bir sonraki oturum için öneri: tür değiştir (20. yüzyıl
  Türkiye olayı, deniz ya da deprem).

## Adım süreleri (saatle ölçüldü)

| Adım | Süre |
|---|---|
| Hazırlık (git, pip, font, referans, 81 test) + ortam ölçümü + belge okuma | ~5 dk |
| Konu tarama + olgu araştırması (3 web araması) | ~4 dk |
| Görsel avı (Commons, 26 aday, 4 tam çözünürlük) | ~5 dk |
| Karakter avı + yüz varyantı | ~4 dk |
| episode.yaml → check → frames → render → teslim + ön kontrol | ~2 dk |
| 2 hakem turu + düzeltmeler | ~3 dk |
| RAPOR, teslim kopyaları, iki depoya commit, belge | ~3 dk |
| **Toplam (saatle ölçüldü: 19:00 → 19:26)** | **~26 dk** |

(Not: özel depodaki RAPOR kopyası teslimden önce yazıldı ve tahmini ~32 dk diyor; ölçülen süre bu tablodaki.)

**Yaklaşık maliyet:** ücretli API yok (TTS ve görsel üretimi yok). Yalnız model kullanımı (oturumun token tüketimi).
