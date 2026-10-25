# hezarfen-galata-ucusu: üretim raporu (25.10.2026 sabah, A sürümü; telifli görsel yok)

> **Yayın durumu:** BEKLET **yok**. Bölüm hassas konu kuralının hiçbir maddesine girmiyor. Konu IV. Murad dönemine
> (1630'lar) ait bir İstanbul anlatısı: güncel olay değil (GUNDEM §5/§7 kapsamı dışı), çocuk yok, son 10 yılda ölen yok,
> yaşayan özel kişi yok, süren dava yok. Lisans kararı bekleyen görsel yok: iki fotoğraf CC BY-SA (4.0 ve 3.0), son kare
> 1950 tarihli bir PTT pulu, kamu malı (PD-TR). Lisanslar Commons dosya sayfasının ham metninden doğrulandı. İki hakem
> 8/8 verdi, MUST kalmadı.

**Konu:** Evliya Çelebi'nin Seyahatnâme'sine göre Hezarfen Ahmed Çelebi, IV. Murad Sarayburnu'ndaki Sinan Paşa
Köşkü'nden izlerken Galata Kulesi'nden kanatlarla havalanıp Üsküdar'da Doğancılar Meydanı'na indi. Padişah ona bir
kese altın verdi. Ardından "Bu adam pek korkulacak bir adamdır, her ne murad ederse elinden gelir, böyle kimselerin
bekası câiz değil!" diyerek onu Cezayir'e sürdü. Cumhuriyet 1950'de onun uçuşunu bir hatıra pulunda resmetti.

## Ortam

4 çekirdek, 15 GB RAM, 30 GB boş disk, Python 3.11.17, ffmpeg 6.1.1. Avenir fontu ve `referans/` (76 dosya) kuruldu;
render Avenir ile yapıldı. `/home/user` vardı, sembolik bağ testlerden önce kuruldu ve testler 81/81 geçti.
`grep MUSIC_IMZA wojak/config.py` çıktısı `imza_v2_golge.m4a`. İki depo da başta ayrık HEAD'deydi; varsayılan dallara
(`claude/kind-albattani-vcp4vk`, `main`) geçilip güncellendi.

## Konu gerekçesi (3 aday)

| Aday | Neden | Karar |
|---|---|---|
| **Hezarfen: Galata'dan uçan adama padişah önce altın verdi, sonra sürgüne yolladı** | Tek cümlede "Ne?!": Boğaz'ı uçarak geçen adam ödül olarak sürgün yiyor. İroni (övünme → "böyle adamdan korkulur") ve ters köşe ("uçtum diye sürgün mü?") kalıba uyuyor. Olay İstanbul'da geçiyor. Birincil kaynak tek (Seyahatnâme), ama aktaran bağımsız kaynaklar var: TDV İslâm Ansiklopedisi, İstanbul Ansiklopedisi (Koçu), GZT, Vikipedi. Kanıt telifsiz: 1950 PTT pulu (kamu malı) uçuşun kendisini gösteriyor. Mağdur, çocuk ya da grafik içerik yok | **Seçildi** |
| Karagöz ile Hacivat'ın gerçek işçiler olduğu ve idam edildiği efsanesi (Bursa) | "Ne?!" güçlü, ama Commons'ta mezarın serbest fotoğrafı bulunamadı; kalan kanıt müze nesnesi (tasvir figürü), bu da bir önceki bölümün son kare türüyle (Kaşıkçı: müze nesnesi) aynı | Yedek |
| IV. Murad'ın içki ve tütün yasağı / yasakçı padişahın ölüm nedeni | İroni güçlü, ama ölüm nedeni kaynaklarda tartışmalı ve kanıtı zayıf (türbe fotoğrafı) | Yedek |

Kanalda yapılmadığını grep ile kontrol ettim: `data/videos.csv` (223 başlık), `data/instagram_reels.csv`,
`data/olay_metinleri.md`, `docs/KONU_HAVUZU.md`, `episodes/` ve `wojak-ozel/teslim/` (ayasofya, göbeklitepe, kanuni,
karun, kaşıkçı). "Hezarfen" yalnız Kaşıkçı ve Göbeklitepe raporlarında **yedek aday** olarak geçiyor; üretilmemiş.
Önceki oturum "çok bilinir" diye yedekte bırakmıştı. Uçuşu bilen çok, ama padişahın ödülden sonra sürgüne yolladığını
bilen az. Ters köşe de bu ikinci yarıya kuruldu.

## Sahne akışı (14,0 sn)

| Zaman | Sahne | Replik |
|---|---|---|
| 0-2,5 | Hezarfen (sol, beyaz sarık, siyah sakal, kendinden emin) | Padişahım, Galata Kulesi'nden / Üsküdar'a uçtum |
| 2,5-4,5 | IV. Murad (sağ, sorguçlu kavuk, kürklü kaftan, ciddi) | Gördüm, al şu bir kese altını |
| 4,5-6,5 | Hezarfen (aynı yüz) | Sağ olun, daha neler / yapabilirim neler |
| 6,5-9,0 | IV. Murad (aynı yüz) | Böyle adamdan korkulur, / Cezayir'e gideceksin |
| 9,0-11,0 | Hezarfen, aynı kutu, **ters köşe yüzü**: iri göz, iç ucu kalkık kaş, açık ağız, alında mavi soğuk ter, başın önünde 3 ter damlası | Nasıl yani, uçtum diye / sürgün mü? |
| 11,0-12,5 | Kanıt 1 | Galata Kulesi'nden Sarayburnu: Topkapı Sarayı, Adalet Kulesi, arkada Boğaz ve Anadolu yakası |
| 12,5-14,0 | Kanıt 2 (son kare) | 1950 PTT ICAO Kongresi 20 kuruşluk hatıra pulu: Galata Kulesi'nden kanatla uçan adam |

Arka plan: Topkapı Sarayı'nın Harem'inden görünen Galata Kulesi. Gerçek yer ve doğru bakış (padişahın sarayından kuleye).
Kule karenin üst ortasında, karakterlerin başının üstünde kalıyor; sağ kenardaki Harem bacası kadraj dışına alındı.
`blur: 2.5` ölçülerek seçildi; kenar Laplace varyansı ~20 (orijinal medyan 22).

Müzik `music: {file: kanal, volume: 0.197}` (imza_v2_golge); ölçüm **−29,6 LUFS, tepe −17,0 dBFS**. Video ve ses
0,000'da başlıyor. Kesmeler kare farkıyla 2,5 / 4,5 / 6,5 / 9,0 / 11,0 / 12,5 sn'de ölçüldü; sahne içi hareket 0,01.
Telefonda (390 px) ters köşe yüz değişimi alt yarıda **%0,40** (eşik %0,40; C12O %0,40, Talidomit %0,39). Yazı bloğu
reel boyunca sabit (iki karakter de `height: 0.55`). Kapak 1. sahne (kanca: kule + "uçtum").

**Son kare çeşitliliği:** son 5 bölümün son kareleri: Kaşıkçı (müze nesnesi fotoğrafı), Göbeklitepe (renkli kupür),
Ayasofya (yazıt + levha), Kanuni (minyatür), Karun (sararmış kupür). Bu bölüm **gerçek bir posta puluyla** bitiyor;
kanalda yeni bir son kare türü. Anlatı basına değil bir seyahatnameye dayandığı için kupür ya da canlandırma kart
yapılmadı; uçuşu gösteren resmî ve serbest bir belge (pul) bulundu.

## Hakem puanları

Hakemler ayrı bağlamda çalıştırılamadı. Her tur sıfırdan yürütüldü: yalnız `kisa_reel.js` içindeki JUDGE_VISUAL ve
JUDGE_FOLLOWER istemleriyle, yalnız teslim dosyalarına (mp4, kapak, metinler) bakarak. Ölçümler:
- 0,5 sn kareler; C2kk, C4V3, C12O ve C2Fr ile aynı ölçekte yan yana sayfa (onaylı Van mp4'ü repoda yok)
- telefon boyu (390 px) kareler; yüz değişim alanı
- kare farkıyla kesme tespiti; ebur128
- arka plan kenar Laplace varyansı (720 ölçeği)
- ekran, başlık ve metindeki olguların kaynak eşlemesi (9 olgu)

| Tur | Görsel | Takipçi + olgu | MUST | Not |
|---|---|---|---|---|
| Ön kontrol (üretici) | — | — | 2 | İlk karelerde IV. Murad'ın yüzü kadrajın en altındaydı ve sakalı kesiliyordu (dev kavuk): PNG sakalın altından kesildi. `height` 0,58/0,62 denendi ama `[stil]` uyarısı verdi; ikisi de 0,55'e döndü. Ters köşe yüz değişimi telefonda %0,25'ti: göz, ağız, ter çizgileri ve damlalar büyütüldü, %0,40'a çıktı. Kaynak çizimdeki dişlerini sıkan ağız (kanalda "öfkeli/kötü" okunur) düz, ciddi bir ağızla değişti. Kır sakal genç padişah için koyulaştırıldı. Kürk yakaya taşan ilk boyama bağlı bölge süzgeciyle düzeltildi |
| 1 | 8 | 7,5 | yok | Görsel SHOULD: sağ kenarda Harem bacasının bej şeridi göze batıyor → kırpım 80 px sola kaydı. Takipçi SHOULD: S5'te "Cezayir" birden geliyor, ekranda sürgünü söyleyen yok → S4 "Her istediğini yapabilen adamdan korkulur" yerine "Böyle adamdan korkulur, Cezayir'e gideceksin"; S5 "Nasıl yani, uçtum diye sürgün mü?" (cevabı son kare: uçuşun kendisi). Kaynak satırındaki pul tarihi (Commons 17.11.1950, pulun üstünde 17-X-1950) belirsizdi → iki tarih de yazıldı, metinde yalnız "1950" |
| 2 | 8 | 8 | yok | Görsel: format, süre, yazı, kesmeler, bakış ve kanıt yerleşimi orijinallerle uyumlu. Tavan notu: Hezarfen "chad" çizimi (ten renkli, profil), Murad klasik beyaz wojak; C2Fr'de de iki karakter farklı üslupta. Pul 319 px'lik kaynaktan büyütüldü: telefonda net, 1:1'de yumuşak. Takipçi: kanca 1. saniyede ("uçtum"); zincir S3 "daha neler yapabilirim" → S4 "böyle adamdan korkulur" Evliya'daki "her ne murad ederse elinden gelir"in canlandırması; alıntı Koçu'daki metinle birebir. Durma noktası: iki hakem ≥ 8, MUST yok |

## Başlık seçenekleri

1. **Galata Kulesi'nden Üsküdar'a uçan adama padişahın verdiği ödül** (yayında)
2. Boğaz'ı kanatla geçen adama IV. Murad'ın verdiği ödül
3. Galata'dan Üsküdar'a uçtu, ödülü bir kese altın ve sürgün oldu

## Lisans tablosu

| Görsel | Kaynak | Lisans | Sürüm |
|---|---|---|---|
| Arka plan: Galata Kulesi, Topkapı Harem'inden (kırpıldı) | Commons, "Galata Tower from the Harem - 2014.10.23 (1).JPG", Derzsi Elekes Andor | CC BY-SA 4.0 | A |
| Kanıt 1: Galata Kulesi'nden Topkapı Sarayı / Sarayburnu (kırpıldı) | Commons, "View of Topkapı Palace from the Galata Tower, Istanbul, Turkey 001 cropped.jpg", Moonik | CC BY-SA 3.0 | A |
| Kanıt 2 (son kare): 1950 ICAO Kongresi 20 kuruşluk pulu (üst kısmı kırpıldı, büyütüldü) | Commons, "Hezarfen Ahmed Çelebi.jpg", Türkiye Cumhuriyeti Postaları | Kamu malı ({{PD-TR}}) | A |
| Karakter A: Hezarfen | wojakland "Panjabi Muslim Chad" (yüz varyantı bizim) | wojakland, şart yok | A |
| Karakter B: IV. Murad | wojakland "Sultan Wojak" (sakal rengi ve ağız bizim) | wojakland, şart yok | A |

B sürümü (telifli) **yok**. Telifli görsel hiçbir sürüme girmedi. Lisans kararı bekleyen görsel yok.

**Serbest görsel araması** (Commons API, `generator=search` + lisans; Openverse ve Internet Archive):
- "Hezarfen": pul (PD-TR) ve heykel fotoğrafı (CC BY-SA 4.0) bulundu. Heykel çağdaş bir eser; Türkiye'de panorama
  özgürlüğü belirsiz olduğu için kullanılmadı. Openverse'te aynı Commons dosyaları çıktı; IA'da kullanılabilir görsel yok.
- "ICAO 1950 stamp Turkey", "Türkiye Cumhuriyeti Postaları 1950": pulun daha büyük taraması yok (319x493 tek kopya).
- "Topkapı Palace view Galata Tower", "Galata Tower from Topkapi", "Golden Horn from Topkapı Palace", "Sarayburnu
  Galata view": arka plan için 7 aday temas sayfasında karşılaştırıldı.
- Karagöz adayı için "Karagöz Hacivat mezarı", "Karagöz tomb Bursa" sorguları sonuç vermedi.

## Olgu tablosu (özet; tam not scratchpad olgular.md)

| Olgu | Güven | Kaynaklar |
|---|---|---|
| Hezarfen hakkında tek kaynak Evliya Çelebi'nin Seyahatnâme'si (I, 670) | Y | TDV İA; İstanbul Ansiklopedisi (Koçu); GZT |
| Okmeydanı'nda kartal kanatlarıyla 8-9 kez talim | Y (tek kök) | TDV İA; Koçu; Vikipedi |
| IV. Murad Sarayburnu'ndaki Sinan Paşa Köşkü'nden izledi; Galata Kulesi → Doğancılar Meydanı; lodos | Y (tek kök) | TDV İA; Koçu; GZT; Vikipedi |
| Bir kese altın; "Bu adam pek korkulacak bir adamdır..." sözü; Cezayir'e sürgün, orada vefat | Y (tek kök) | TDV İA; Koçu (alıntı birebir buradan); GZT |
| Yıl kaynakta yok (1632, 1638 sonradan verilen tahminler) | Y | GZT; TDV (yıl vermiyor); Vikipedi ("circa 1630–1632") |
| Bazı tarihçiler efsane sayıyor (başka kayıtta yok) | Y | GZT; RayHaber/Vikipedi TR aktarımı |
| PTT 1950'de İstanbul'daki ICAO kongresi için 20 kuruşluk pulda uçuşu resmetti | Y | İstanbul Ansiklopedisi (Koçu); Pul ve Posta; Commons dosya açıklaması |

## Bilinen kusurlar

- **Pul büyütülmüş:** tek serbest tarama 319x493; son kare 3,4 kat büyütüldü. Telefonda net, 1:1'de yumuşak.
- **Karakter üslupları farklı:** Hezarfen ten renkli bir "chad" profili, IV. Murad klasik beyaz wojak. 17. yüzyıl
  Osmanlı bilgini için klasik yüzlü, büstlü hazır çizim bulunamadı. Wojakland'deki tek klasik yüzlü sarıklı çizim
  ("Muslim Wojak") büstsüz, havada bir kafaydı.
- **Bir önceki bölümle benzerlik:** Kaşıkçı'nın kaşıkçısı da sarıklı bir chad'di (kır sakallı, başka çizim). İki
  bölümün kanıt 1'i de Topkapı'yı gösteriyor (orada Hazine avlusu, burada Galata'dan saray silueti). Son kare türleri
  farklı.
- **IV. Murad'ın yüzü kadrajın alt yarısında:** dev kavuk yüzünden. `height` 0,55 sınırı aşılmadı.
- **Arka planda bugünkü Karaköy binaları:** 17. yüzyıl sahnesi, bugünkü fotoğraf. Orijinaller de bugünkü yer
  fotoğrafını kullanıyor; kule ve saray öğesi ön planda.
- **Anlatı tek kaynaklı:** metin bunu ve efsane görüşünü açıkça yazıyor; ekrandaki övünme ve son fark etme repliği
  canlandırma (`ek_maddeler`'de yazılı).

## Adım süreleri (ölçüldü)

| Adım | Süre |
|---|---|
| Hazırlık (git, pip, font, referans, 81 test) + ortam ölçümü + belge okuma | ~3 dk |
| Konu tarama + kanıt ön kontrolü (3 aday, Commons) | ~4 dk |
| Karakter avı + yüz varyantları + olgu araştırması (2 web araması) + görsel avı + kırpımlar | ~12 dk |
| episode.yaml → check → frames → render → teslim + ön kontrol (yüz konumu, yüz değişimi) | ~4 dk |
| 2 hakem turu + düzeltmeler | ~3 dk |
| RAPOR, teslim kopyaları, iki depoya commit, belge | ~3 dk |
| **Toplam (saatle ölçüldü)** | **~29 dk** |

**Yaklaşık maliyet:** ücretli API yok (TTS ve görsel üretimi yok). Yalnız model kullanımı (oturumun token tüketimi).
