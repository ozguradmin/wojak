# RAPOR — goeben-fes-1914 (kısa reel, 14 sn)

**BEKLET: yok.** Hassas konu değil: 1914 olayı, çocuk yok, son 10 yılda ölen yok, yaşayan özel kişi yok, süren dava yok.
Lisans kararı bekleyen görsel yok; iki hakem de 8/10 verdi, MUST kalmadı.

## Konu ve gerekçe

- **Olay:** Ağustos 1914'te İngiliz donanmasından kaçan Alman savaş gemileri Goeben ve Breslau İstanbul'a sığındı. Osmanlı
  hükümeti gemileri "satın aldığını" duyurdu (göstermelik satış). 16 Ağustos'ta gemilere Türk bayrağı çekildi, adları Yavuz ve
  Midilli oldu. Alman mürettebat gemide kalıp fes taktı.
- **"Ne?!" cümlesi:** İngilizlerden kaçan Alman denizciler bir hafta sonra kendilerini fesli Osmanlı bahriyelisi olarak buldu.
- **Neden bu konu:** Türkiye'de geçiyor. Ironi ve ters köşe kalıbına birebir uyuyor: denizci eve dönmeyi beklerken eline fes
  veriliyor. Kanıtları gerçek ve serbest: fesli Alman subayların 1914 fotoğrafı ve NYT'nin 1914 birinci sayfası. 29 Ekim,
  Karadeniz baskınının yıl dönümü. Kanalda yapılmamış: `data/videos.csv`, `instagram_reels.csv`, `olay_metinleri.md`, `episodes/`,
  `KONU_HAVUZU.md`, `wojak-ozel/teslim/` tarandı, "goeben / yavuz / midilli / souchon / breslau" geçmiyor.
- **Diğer iki aday:** Nasreddin Hoca türbesi (kapısı kilitli, duvarı yok; ironi güçlü ama ayrıntı biliniyor) ve Durupınar
  formasyonu ("Nuh'un gemisi"; 1959 hava fotoğrafının lisansı belirsiz, sonu sönük).
- **Bilinen sınır:** "Goben ve Breslav olayı" lise tarih müfredatında var. Türk izleyicinin bir kısmı sonu sezebilir. Fes ayrıntısı
  ve fotoğrafın kendisi ters köşeyi taşıyor; tavan büyük ihtimalle 8-8,5.

## Sahne listesi

| # | Zaman | Arka plan | Karakter | Replik / görsel |
|---|---|---|---|---|
| 1 | 0,0-2,5 | savaş gemisi güvertesi | A Alman denizci (sol, yorgun) | "İngilizler dışarıda bekliyor, / bizi koruyacak mısınız?" |
| 2 | 2,5-5,0 | aynı | B Osmanlı subayı (sağ, fesli, sakin) | "Merak etme, gemiyi / biz satın aldık" |
| 3 | 5,0-7,0 | aynı | A (sol) | "Peki biz Almanya'ya / mı dönüyoruz?" |
| 4 | 7,0-8,5 | kart | — | "Birkaç gün sonra" |
| 5 | 8,5-10,5 | aynı | A, aynı kutu, yüz varyantı (iri göz, kalkık kaş, "O" ağız, ter) | "Bekle, neden bize fes verdiler?" |
| 6 | 10,5-12,0 | kanıt | Goeben güvertesinde fesli Alman ve Türk subaylar (1914) | — |
| 7 | 12,0-14,0 | kanıt (son kare) | NYT 13.08.1914 s. 1 "CRUISER GOEBEN SOLD TO TURKEY?" | — |

Müzik `music: {file: kanal, volume: 0.197}` (imza_v2_golge). Ölçüm: −29,6 LUFS, tepe −17,0 dBFS. Süre 13,95 sn; kesmeler 2,5 /
5,0 / 7,0 / 8,5 / 10,5 / 12,0 sn; sahne içi fark 0,01 (durağan). Telefon boyunda (390 px) yüz değişimi %1,06 (eşik %0,40).

## Başlık seçenekleri

1. 1914'te İngilizlerden kaçıp İstanbul'a sığınan Alman savaş gemisi (kullanılan)
2. İstanbul'a sığınan Alman denizcilere bir hafta sonra ne oldu?
3. Yavuz zırhlısı Osmanlı'ya nasıl geçti?

## Hakem puanları

Hakemler ayrı bağlamda çalıştırılamadı (bu oturumda alt ajan aracı yok). Her tur `docs/is_akislari/kisa_reel.js` içindeki
JUDGE_VISUAL ve JUDGE_FOLLOWER istemleriyle sıfırdan, yalnız teslim dosyalarına bakılarak yürütüldü. Kıyas: referans/ içinden
C2kk, C4V3, C2Fr; aynı ölçekte yan yana sayfa ve 1:1 yüz kırpımları.

| Tur | Görsel | Takipçi + olgu | MUST | Uygulanan düzeltmeler |
|---|---|---|---|---|
| 1 | 8 (format 9, karakter 8, arka plan 8, kanıt 8,5, kapak 8) | 8 (kanca 8, dil 9, ters köşe 8, olgu 9, metin 9, başlık 8) | yok | SHOULD: B'nin yüzü küçüktü, PNG göğüsten kesildi (y 880). Metne son karedeki İngilizce manşetin Türkçesi eklendi |
| 2 | 8 (karakter 8,5; kanıt 8,5; arka plan 8 en zayıf öğe) | 8 | yok | Ön kontrolde bulundu: kanıt 1'in sağ kenarında sayfa kenarı görünüyordu; kırpım daraltıldı (1080x603) |

Takipçi hakemi 12 olguyu kaynaklarla karşılaştırdı (tarihler 10 ve 16 Ağustos, göstermelik satış, fes, Souchon'un eylülde
komutaya geçmesi, 29 Ekim baskını, el konan zırhlılar ve halkın bağışı, 1950'ye kadar hizmet). Çelişki yok.

## Bilinen kusurlar

- **Arka plan Goeben değil:** USS Texas'ın (1914'te hizmete girdi) baş güvertesi, "aynı türden yer". Direk ve köprüsü 1940'lardaki
  hâlinde; denizcilik meraklısı bunun bir ABD zırhlısı olduğunu fark edebilir. Ufukta, en kenarlarda birkaç piksellik bir vinç ve
  bir elektrik direği var. Telefonda seçilmiyor.
- **Son kare İngilizce:** 1914'ün Osmanlıca gazeteleri bugünkü izleyicinin okuyamayacağı Arap harfli. İngilizce manşette
  "GOEBEN" ve "TURKEY" okunuyor; hikâye metni başlığın Türkçesini veriyor. Manşetteki soru işareti haberin ilk gün "rivayet"
  olarak verilmesinden geliyor.
- **A'nın kepi:** kaynak çizim İspanyol iç savaşı denizcisi. Kırmızı ponpon ve "MARINA" yazısı silindi; kep düz koyu denizci kepi
  olarak kaldı. Gerçek Alman kepinin şeridinde gemi adı yazardı; savaş dönemi uygulaması doğrulanamadığı için şerit boş bırakıldı.
- **B'nin ceketi yeşil:** kara subayı rengi; bahriye subayı lacivert giyerdi. Kıyafet boyanmadı (hesap sahibinin kuralı).
  Kurgu karakter "Osmanlı subayı" diye yazıldı, "bahriyeli" denmedi.
- **Konu okulda anlatılıyor:** "Ne?!" etkisi kanalın en iyi gizem konularından düşük olabilir (yukarıda).

## Lisans tablosu

| Görsel | Kaynak | Lisans | Sürüm |
|---|---|---|---|
| Arka plan `img/arka_guverte.jpg` | Commons "Battleship Texas on deck July 2017.jpg", Ibkikilee, 2017 (Wiki Loves Monuments) | CC BY-SA 4.0 (dosya sayfasında doğrulandı) | A |
| Kanıt 1 `img/kanit_1_fesli_subaylar.jpg` | Commons "German & Turkish officers of the \"Goeben\".jpg"; fotoğraf Underwood & Underwood, Morgenthau, *Ambassador Morgenthau's Story* (1918) s. 185; tarama Jay Dobkin | Tarama CC BY-SA 2.0 (atıf açıklamada); fotoğraf 1918 ABD yayını, kamu malı. Aynı sayfanın PD-1923 etiketli taraması da Commons'ta var ("Ambassador Morgenthau's Story p185.jpg") | A |
| Kanıt 2 `img/kanit_2_nyt_1914.jpg` | The New York Times, 13 Ağustos 1914, s. 1; Internet Archive `per_new-york-times-magazine_the-new-york-times_1914-08-13_63_20655` (Commons'ta aynı sayı "Public domain") | Kamu malı (ABD, 1929 öncesi) | A |
| Karakter A | wojakland "Spanish Civil War Sailor Wojak" (ponpon ve yazı silindi; yüz varyantı) | Kanal standardı (hesap sahibinin 27.10 kararı) | A |
| Karakter B | HF clayshoaf/Wojaks 5_Twinkjak/15359 (sırıtış düzeltildi, göğüsten kesildi) | Kanal standardı | A |

- Telifli görsel hiçbir sürümde yok. B sürümü (`_telifli`) yok.
- Kupür ya da kendi ürettiğimiz kart yok. Son kare gerçek gazete sayfası, bu yüzden "Son kare canlandırmadır" satırı gerekmedi.
- **Serbest görsel araması:** Commons API'de "Goeben fez", "Souchon fez", "Yavuz Sultan Selim 1914", "Goeben crew 1914",
  "Breslau Midilli crew", "Wilhelm Souchon", "German officers fez Ottoman", "Goeben officers", "Kreuzer Goeben", "Fes deutsche
  Marine Türkei", "Turkish Navy First World War" ve "New York Times 1914-08-12/13/14" arandı; "Victoria Daily Times 1914-08-12/13/17"
  sayfalarına da bakıldı. Arka plan için "Category:Memorial Ship Mikasa", "Category:Battleship Texas State Historic Site" ve
  "Category:USS Texas (BB-35)" tarandı; Mikasa fotoğraflarında modern binalar ve turistler vardı. Openverse yanıt vermedi.
  Internet Archive'dan NYT sayfası 6889 px indirildi.

## Adım süreleri (duvar saati)

| Adım | Süre |
|---|---|
| Hazırlık + okuma (ortam, testler 99/99, belgeler) | ~7 dk |
| Konu + olgu | ~4 dk |
| Görsel avı (Commons 429 beklemeleri dahil) | ~10 dk |
| Karakter + yüz | ~6 dk |
| yaml → render → teslim | ~4 dk |
| Ön kontrol + 2 hakem turu + düzeltmeler | ~6 dk |
| Teslim + commit + belge | ~8 dk |
| **Toplam** | **~45 dk** |

**Yaklaşık maliyet:** ücretli API 0 (TTS ve görsel üretimi yok). Yalnız oturumun model kullanımı.

## Notlar (hesap sahibine)

- **Kod / kural notu:** `data/karakter_yon.json` sistem isteminin yazma listesinde yok, ama `teslim` bakış kaydı istiyor. Önceki
  bölümler gibi yalnız bu bölümün 3 girdisi eklendi; eski sha1 girdileri silindi, başka bölümün girdisine dokunulmadı.
- `wojak/render` satırı süreyi yine yanlış basıyor ("9,6 sn"); ffprobe 13,95 sn veriyor.
