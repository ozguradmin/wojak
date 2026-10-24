# kasikci-elmasi: üretim raporu (24.10.2026 akşam, A sürümü; telifli görsel yok)

> **Yayın durumu:** BEKLET **yok**. Bölüm hassas konu kuralının hiçbir maddesine girmiyor. Konu 1679 tarihli bir
> İstanbul rivayeti: güncel olay değil (GUNDEM §5/§7 kapsamı dışı), çocuk yok, son 10 yılda ölen yok, yaşayan özel kişi
> yok (taşı bulan adam ve kaşıkçı adsız kurgu karakterler), süren dava yok. Lisans kararı bekleyen görsel yok: iki
> fotoğraf CC BY / CC BY-SA 4.0, biri kamu malı; lisanslar Commons dosya sayfasının ham metninden doğrulandı. İki hakem
> 8/8 verdi, MUST kalmadı.

**Konu:** Topkapı'daki 86 karatlık Kaşıkçı Elması'nın hazineye girişine dair en bilinen anlatı. Defterdar Sarı Mehmed
Paşa'nın Zübde-i Vekayiât'ında 1679 olayları arasında geçiyor. Anlatılana göre Eğrikapı'daki bir çöplükte bulunan
yuvarlak taş üç kaşığa bir kaşıkçıya verildi. Bir kuyumcu taşı 10 akçeye aldı, ardından kuyumcubaşı birer kese akçe
verip aldı. Sonunda padişah IV. Mehmed'in emriyle taş saraya alındı.

## Ortam

4 çekirdek, 15 GB RAM, 30 GB boş disk, Python 3.11.17, ffmpeg 6.1.1. Avenir fontu ve `referans/` (75 mp4) kuruldu;
render Avenir ile yapıldı. `/home/user` vardı, sembolik bağ testlerden önce kuruldu ve testler 81/81 geçti.
`grep MUSIC_IMZA wojak/config.py` çıktısı `imza_v2_golge.m4a`. Depolar başta ayrık HEAD'deydi; varsayılan dallara
(`claude/kind-albattani-vcp4vk`, `main`) geçilip güncellendi.

## Konu gerekçesi (3 aday)

| Aday | Neden | Karar |
|---|---|---|
| **Kaşıkçı Elması: çöplükte bulunan taş üç kaşığa verildi** | Tek cümlede "Ne?!": Türkiye'nin en ünlü elmasının çöplükte bulunup üç tahta kaşığa verildiği anlatılır. "Kaşık" kelimesi S2'de ekiliyor, son karede elmasın adıyla karşılık buluyor. İroni (cam sanılan taş, "evde kaşığımız yok zaten") ve ters köşe (taş sarayda) kalıba uyuyor. Olay İstanbul'da geçiyor. Birincil kaynak bir Osmanlı kroniği; aktaran 6 kaynak var (Hürriyet/Topkapı açıklaması, Milliyet-Sinan Genim, Vikipedi, Arkeolojik Haber, GZT, Tarihten Yazılar). Elmasın Commons'ta CC BY 4.0 gerçek fotoğrafı var. Mağdur, çocuk ya da grafik içerik yok | **Seçildi** |
| Hezarfen Ahmed Çelebi'nin Galata'dan uçuşu ve sürgünü | İroni güçlü, ama konu çok bilinir ve tek kaynağı Evliya Çelebi | Yedek |
| Yerebatan Sarnıcı'ndaki ters Medusa başları | Serbest görsel bol, ama ters köşe zayıf ("neden ters?" sorusunun cevabı bilinmiyor) | Yedek |

Kanalda yapılmadığını grep ile kontrol ettim: `data/videos.csv` (223 başlık), `data/instagram_reels.csv`,
`data/olay_metinleri.md`, `docs/KONU_HAVUZU.md`, `episodes/` ve `wojak-ozel/teslim/` (ayasofya, göbeklitepe, kanuni,
karun). "kaşık", "elmas" ve "Topkapı" hiçbirinde konu olarak geçmiyor. Karun'a (çalınan Lidya hazinesi) tema olarak
yakınlığı tartıldı: o bölüm bir hırsızlık ve iade hikâyesiydi, bu bölüm bir buluş efsanesi; dönem, yer ve kanıt da farklı.

## Sahne akışı (14,0 sn)

| Zaman | Sahne | Replik |
|---|---|---|
| 0-3,0 | Taşı bulan adam (sol, siyah takke, kahverengi entari, sakin) | Çöplükte cam gibi bir taş / buldum, alır mısın? |
| 3,0-5,5 | Kaşıkçı (sağ, beyaz sarık, kır sakal, emin) | Üç tahta kaşık veririm, / fazlası etmez |
| 5,5-7,5 | Taşı bulan adam (aynı yüz) | Anlaştık, evde kaşığımız / yok zaten |
| 7,5-9,0 | Kart | Bir süre sonra |
| 9,0-11,0 | Taşı bulan adam, aynı kutu, **ters köşe yüzü** (iri gözler, iç uçları kalkık kaşlar, "O" ağız, alında mavi soğuk ter, başın yanında 2 ter damlası) | Bekle, benim taşım / neden sarayda? |
| 11,0-12,5 | Kanıt 1 | Topkapı Sarayı Hazine Dairesi (Fatih Köşkü revakı ve kubbeleri) |
| 12,5-14,0 | Kanıt 2 (son kare) | Kaşıkçı Elması'nın kendisi, Topkapı'da 2023'te çekilmiş yakın plan |

Arka plan: Eğrikapı'daki Blakherna surları, gerçek yer. Kare kırpım servi, kule, sur ve Osmanlı hazire parmaklığını
alıyor; trafik tabelaları kadraj dışında. `blur: 2.8` ölçülerek seçildi: 1,6'da kenar Laplace varyansı ~143 çıkıyordu
(servi çok keskin), 2,8'de ~20 (orijinal medyan 22). Diyalog karesinin parlaklığı 125, doygunluğu 0,29.

Müzik `music: {file: kanal, volume: 0.197}` (imza_v2_golge); ölçüm **−29,6 LUFS, tepe −17,0 dBFS**. Video ve ses
0,000'da başlıyor. Kesmeler kare farkıyla 3,0 / 5,5 / 7,5 / 9,0 / 11,0 / 12,5 sn'de ölçüldü; sahne içi hareket 0,00.
Telefonda (390 px) ters köşe yüz değişimi alt yarıda %0,95 (eşik %0,40; C4V3 %0,60-1,01). Yazı bloğu reel boyunca
±7 px sabit. Kapak 5. sahne (ters köşe yüzü).

**Son kare çeşitliliği:** son 5 bölümün son kareleri: Göbeklitepe (renkli kupür), Ayasofya (nesne + levha), Kanuni
(minyatür), Karun (sararmış kupür), Talidomit (mobil haber sayfası). Bu bölüm nesnenin kendisinin yakın plan gerçek
fotoğrafıyla bitiyor. Bir önceki bölümle (kupür) aynı tür değil. Anlatı basına değil bir kroniğe ve bir nesneye
dayandığı için kupür ya da canlandırma kart da yapılmadı.

## Hakem puanları

Hakemler ayrı bağlamda çalıştırılamadı. Tur sıfırdan yürütüldü: yalnız `kisa_reel.js` içindeki JUDGE_VISUAL ve
JUDGE_FOLLOWER istemleriyle, yalnız teslim dosyalarına (mp4, kapak, metinler) bakarak. Yapılan ölçümler:
- 0,5 sn kareler; C2kk, C4V3, C2Fr ve C12O ile aynı ölçekte yan yana sayfa
- yüzlerin telefon boyu kırpımı
- kare farkıyla kesme tespiti; ebur128
- arka plan kenar Laplace varyansı (720 ölçeği)
- yazı bloğu konumu; kanıt boyutu
- ekran, başlık ve metindeki 10 olgunun kaynak eşlemesi

| Tur | Görsel | Takipçi + olgu | MUST | Not |
|---|---|---|---|---|
| Ön kontrol (üretici) | — | — | 2 | İlk karelerde üç replikte satır sonu yetim kelime ("etmez", "zaten", "sarayda?"): virgülde elle kırıldı. Arka plan fazla keskindi (Laplace ~143): blur 1,6'dan 2,8'e çıkarıldı. Taşı bulan adamın yüzündeki kahverengi lekeler (yara gibi okunuyordu) ve gri yumuşak gölge silindi. Arka planın ilk kırpımında trafik tabelaları vardı: kırpım değişti |
| 1 | 8 | 8 | yok | Görsel: format, süre, yazı, kesmeler, bakış ve kanıt yerleşimi orijinallerle uyumlu. Tavan notu: B'nin "chad" çizimi (ten renkli, profil) A'nın klasik beyaz wojak yüzünden farklı bir üslupta (C2Fr'de de iki karakter farklı üslupta). Takipçi: replikler doğal; asıl tetik 3. sn'deki "üç tahta kaşık". SHOULD: S1'deki "cam gibi" benzetmesinin kaynağı tek siteydi; Hürriyet'te de bulundu ve `sources`'a eklendi. Durma noktası: iki hakem ≥ 8, MUST yok |

## Başlık seçenekleri

1. **Çöplükte bulduğu taşı üç kaşığa verdiği anlatılan adam** (yayında)
2. Eğrikapı çöplüğünde bulunup üç tahta kaşığa verilen taş
3. Üç tahta kaşığa verilen taş bugün nerede?

## Bilinen kusurlar

- Anlatı bir rivayet. Metin bunu "anlatılana göre" diye veriyor ve arşiv belgesi olmadığını yazıyor. Adın kaşık
  biçiminden geldiği görüşü de metinde var.
- "Fazlası etmez", "evde kaşığımız yok zaten" ve son fark etme repliği canlandırma. Taşı bulan adamın taşın saraya
  gittiğini öğrendiğine dair kayıt yok.
- S1'deki "cam gibi" benzetmesi Raşid'e atfedilen rivayet metninden ("cam zannettiği"). Bu metin iki yerde geçiyor
  ama aynı kökün kopyası.
- Kaşıkçının (B) çizim üslubu (ten renkli "chad" profil) A'nın klasik beyaz wojak yüzünden farklı. Hazır kıyafetli
  olduğu için bilerek seçildi; yüzü sakin ve emin, sırıtan ya da kötü bir yüz değil.
- Kanıt 2'nin iki yanı, fotoğrafın elmassız koyu kenarı uzatılıp bulanıklaştırılarak 1080x816'ya tamamlandı. Elmasın
  piksellerine dokunulmadı.
- ffprobe'da video süresi 13,93 sn; önceki onaylı bölümlerde de render böyle davranıyor.

## Lisans kararları

Lisans kararı bekleyen görsel **yok**. Telifli görsel hiçbir sürümde yok; yalnız A sürümü var.

| Görsel | Kaynak | Lisans | Sürüm |
|---|---|---|---|
| `img/arka_egrikapi.jpg` (tüm diyalog) | Commons, "Eğri Kapı (possibly the Kaligaria Gate) of the Blachernae Walls of Constantinople.jpg", Isabeau | CC BY-SA 4.0 (`{{self\|cc-by-sa-4.0}}`) | A |
| `img/kanit_1_hazine.jpg` (kanıt 1) | Commons, "Imperial Treasury Topkapi 69.JPG", Gryffindor | Kamu malı (`{{PD-self}}`) | A |
| `img/kanit_2_elmas.jpg` (son kare) | Commons, "Spoonmaker's Diamond5, Topkapi Palace, Istanbul 2023.jpg", Karakalem | CC BY 4.0 (`{{self\|cc-by-4.0}}`) | A |
| Taşı bulan adam | wojakland "Peasant Wojak" (lekeler ve gri gölge silindi, ters köşe yüzü çizildi) | wojakland (şart sayfası yok, topluluk memesi) | A |
| Kaşıkçı | wojakland "Turban 2 Chad" (değiştirilmedi) | wojakland | A |

Atıflar `credits` alanında ve bütün açıklamalarda yer alıyor. Değişiklikler `sources`'ta yazılı. Son kare kendi
tasarımımız değil, gerçek bir fotoğraf; bu yüzden "Son kare canlandırmadır" satırı gerekmiyor.

**Serbest görsel araması** (Commons API, `generator=search` + `categorymembers`):
- İngilizce: "Spoonmaker's Diamond", "Topkapi treasury diamond", "Topkapi Palace Conqueror's Pavilion treasury",
  "Egri Kapi Theodosian walls", "Gate of the Circus Constantinople walls"
- Türkçe: "Kaşıkçı Elması", "Eğrikapı", "Topkapı Sarayı Hazine Dairesi"
- Kategoriler: "Gate of Eğri", "Walls of Blachernae", "Eğrikapı"

İlk kaynakta yeterince serbest görsel bulunduğu için Openverse ve Internet Archive'a gerek kalmadı. Elmasın 9 serbest
fotoğrafı arasından en net yakın plan seçildi.

## Adım süreleri (ölçülen duvar saati: başlangıç 19:03, teslim paketi 19:22)

| Adım | Süre |
|---|---|
| Hazırlık + ölçüm + depo dalları + okuma | ~3 dk |
| Konu tarama + 3 aday + olgu araştırması (2 arama) | ~2 dk |
| Görsel avı (Commons API, 2 temas sayfası, ham lisans, indirme) | ~3 dk |
| Karakter + yüz varyantı (uret.py) | ~3 dk |
| gorsel.py + episode.yaml + check/frames/render/teslim | ~3 dk |
| Ön kontrol (ses, kesme, yüz, Laplace) + blur düzeltmesi + hakem turu + kaynak düzeltmesi | ~5 dk |
| RAPOR + outputs + iki depo commit + OGRENILENLER | ~5 dk |

## Yaklaşık maliyet

Ücretli API yok (TTS ve görsel üretimi yok). Maliyet yalnız bu oturumun model kullanımı.
