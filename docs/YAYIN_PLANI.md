# Yayın planı ve sıradaki işler

> Hesap sahibiyle 15.10.2026'da konuşuldu. Plan sahibindir; ben üretip teslim ederim, paylaşımı hesap sahibi yapar
> (CLAUDE.md "delivery flow"). **21.10 güncellemesi:** ElevenLabs cevabı gelmedi; **kısa reel'lerle şimdi başlanıyor**, uzun
> video ElevenLabs gelince (§4). Yeni imza müziği ayrı bir oturumda yapılıyor; gelene kadar `music: kanal` kalır, gelince
> bölümler yeniden render edilir. Elimizdeki onaylı videolar: 4 kısa (van-depremi-azra-bebek, canakkale-kayip-tabur,
> kiz-kulesi-efsanesi, talidomit-turkiye) + 1 uzun (talidomit-turkiye-uzun; ses ElevenLabs ile yenilenecek). Dört kısa
> eski kanal müziğini kullanıyor: YouTube'a yüklenmeden önce yeni müzikle yeniden render edilmeli (§0).

## 0. YouTube: sıfırdan başlangıç ve hedef (21.10.2026)

- Kanal bir **ihlal** aldı, hangi videodan olduğu bilinmiyor. Eski Shorts 90 günde ~200 bin izlenme getiriyordu, hepsi
  silinecek (yedek: hesap sahibi Google Takeout ile alıyor). Kanalın verileri zaten repoda: `data/videos.csv` (223 Short),
  `data/olay_metinleri.md`.
- **Hedef: YouTube Partner Programı.** İki yol var, ikisi de 1.000 abone ister:
  (a) son 90 günde 10 milyon herkese açık Shorts izlenmesi (günde ~111 bin);
  (b) son 12 ayda 4.000 saat herkese açık uzun video izlenme süresi.
  10 dakikalık videoda ortalama 4 dk izlenirse (b) için toplam ~60 bin izlenme yeter. Uzun videolar bu yolun motorudur;
  Shorts'un izlenmesi saat hesabına girmez. İki yol paralel yürür. Güncel koşullar YouTube Studio → Para kazanma'da kontrol edilir.
- **İhlal hakkında bilinenler:**
  - Video silinince ihtar (uyarı) kalkmaz.
  - İhtar 90 günde düşer. 90 gün içinde 3 ihtar alan kanal kapatılır.
  - Etkin bir Topluluk Kuralları ihtarı varken Partner Programı'na kabul yapılmaz.
- **Önce ihlalin nedeni bulunmalı.** Yeni videolar aynı hatayı tekrarlamasın:
  - YouTube Studio ana sayfasındaki uyarı kartı ve gelen e-posta, ihlalin videosunu ve kuralını gösterir.
  - Telif hakkı menüsünde telif ihtarları ve kaldırma talepleri listelenir.
  - İçerik listesindeki "Kısıtlamalar" sütunu, sorunun hangi videoda olduğunu gösterir.
- **YouTube yüklemesi (hesap sahibi 22.10):** doğrudan **herkese açık** (`tools/yt_yukle.py`, varsayılan public). Yükledikten
  sonra Studio'da "Kontroller" sonucuna bakılır; telif uyarısı gelirse video hemen özele alınır.
- **Otomatik yorum:** API ile yorum için anahtarda `youtube.force-ssl` izni gerekir (22.10 anahtarında var; `tools/yt_yukle.py --yorum-file`). API yorum
  SABİTLEYEMEZ; sabitleme Studio'dan elle yapılır.
- **YouTube sürümleri için riskler** (nedeni öğrenilince karar hesap sahibinin):
  1. Kısa reel'lerin imza müziği bir reel'in sesinden çıkarıldı. Kaynağı üçüncü taraf bir parçaysa YouTube'da Content ID
     eşleşmesi alabilir. Bize ait benzeri üretildi: `assets/music/imza_vals*.m4a` (`tools/imza_muzik.py`, 21.10; hesap sahibi dinleyip seçecek).
  2. `img/telifli/` haber fotoğrafları YouTube'da telif kaldırma talebi alabilir. YouTube sürümünde mümkünse serbest
     lisanslı görsel kullanılır.
  3. Hassas konular (deprem, çocuk, ölüm, şiddet): GUNDEM.md §5 ve §7. Grafik görüntü yok. Çocuk gerçek fotoğrafla
     gösterilmez.

## 1. Hesap sahibinin planı

- **2-3 günde bir konu**, haftada 2-3 video: eski aktifliği geri kazanmak.
- Aynı konu iki biçimde: **öğle vakti** önce **uzun video YouTube'a**, **akşama doğru** aynı konunun **Shorts + Instagram
  Reels**'i.
- Kısa sürümlerin açıklamasında "uzun hali kanalda" yönlendirmesi.

## 2. Görüşüm ve önerilerim (plan iyi; uygulamada şunlar)

1. **Sıra doğru:** uzun video önce çıkmalı, çünkü Short'un "İlgili video" bağlantısı ancak yayındaki bir videoya
   verilebilir. Öğle (12:00-14:00 TR) yüklemesi uzun videoya akşam zirvesinden önce ilk gösterimleri toplama zamanı tanır.
2. **Kısa sürüm 20:00-20:15 TR:** altın dönemde 25/25 reel bu saatteydi (URETIM_REHBERI §7, INSTAGRAM_ANALIZ). Shorts ve
   Reels aynı saatte; Short, uzun videoya akşam zirvesinde izleyici taşır.
3. **Her konu uzun videoyu kaldırmaz.** Haftada 2 konu uzun + kısa, 1 konu yalnız kısa olabilir (efsane, tek sahnelik
   olay). Instagram'ın ritmi haftada 3'ün altına düşmez; uzun video kalitesi takvim için düşürülmez.
4. **Sabit günler** (öneri): **Salı ve Cuma** uzun + kısa; **Pazar** yalnız kısa. İzleyici ritmi öğrenir; üretim de
   haftalık planlanır. Güncel olayda (GUNDEM.md) hız öne geçer: önce kısa (1-2 gün içinde), uzun video ardından.
5. **Stok:** yayından en az bir konu önde üret (bir hazır konu bekletilsin). Bir aksilik (ses, lisans, hakem turu) takvimi
   kaydırmaz.
6. **Bağlantılar** (paketler hazır üretir; `uzun_video` alanı + `paylasim.md`):
   - YouTube Shorts: Studio'da **İlgili video** = uzun video; açıklamada "▶ Uzun hali: <bağlantı>".
   - Instagram: tıklanabilir bağlantı yok; açıklamanın sonunda tek satır "Uzun hali YouTube'da: tarihselwojak" (hashtag
     yok), profil bağlantısı YouTube kanalı. `pack.py` bu satırı henüz Instagram metnine koymuyor (yalnız YouTube
     açıklamasına): üretim yeniden başlayınca `uzun_video` doluysa Instagram metnine de eklenecek (§4 madde 2'yle birlikte).
   - Uzun video: sabit yorum = kapanıştaki A/B/C sorusu; açıklamada kısa sürümün bağlantısı (Short yayınlanınca eklenir).
   - Short'un videosuna "uzun hali kanalda" yazısı eklenmez: altın dönem kuralı kanıttan sonra hiçbir şey göstermez (STIL).
7. **Küçük resim testi:** her uzun videoda 3 küçük resim, YouTube Studio "Test ve karşılaştır"; 48 saat sonra kazanan
   not edilir (hangi tip: yüz + tek kelime mi, harita mı, belge mi) ve sonraki videoların küçük resmini yönlendirir.
8. **Ölçüm** (2 haftada bir, `tools/yt_arastir.py rapor`): uzun videoda TO (CTR), ortalama izlenme süresi, 30. saniyede
   kalan oran; Short'tan uzun videoya geçiş (Studio: İlgili video tıklamaları); Reels izlenme/gün. Sonuçlar
   `docs/ANALIZ.md`'ye; plan verilere göre değişir.

## 3. Haftalık akış (örnek)

| Gün | Yayın | Üretim |
|---|---|---|
| Pazartesi | – | Konu A: uzun videonun hakem turları, teslim; konu B araştırma |
| Salı | **12:00** konu A uzun (YouTube) · **20:00** konu A kısa (Shorts + Reels) | Konu B senaryo + varlıklar |
| Çarşamba | – | Konu B üretim + hakemler; konu C (yalnız kısa) araştırma |
| Perşembe | – | Konu B teslim; konu C üretim |
| Cuma | **12:00** konu B uzun · **20:00** konu B kısa | Konu D araştırma |
| Pazar | **20:00** konu C kısa | – |

## 4. Sıradaki işler: ElevenLabs gelince (hesap sahibi API anahtarını iletecek)

Hesap sahibinin talimatı (15.10): şimdi yeni video ya da düzeltme yok; ElevenLabs sonucu gelince başlanır. Sıra:

1. **Anahtar:** `ELEVENLABS_API_KEY` yalnız `~/.config/wojak/secrets.env` / ortam değişkeni; hiçbir dosyaya yazılmaz.
2. **Motor bağdaştırıcısı:** `wojak/uzun/tts.py`'ye sağlayıcı seçimi (`ses_saglayici: elevenlabs` / `cartesia`); önbellek
   anahtarına sağlayıcı + ses + model + ayarlar girer; `<break>` ve hız karşılıkları; mevcut Whisper QA ve tık
   güvenlikleri aynen. Testler + demo.
3. **Ses seçimi (ölçerek):** Türkçe anlatıcı (erkek) ve ikinci ses (kadın) için 4-6 aday; aynı iki paragraf (isimli ve
   duygusal) okunur; Whisper isim doğruluğu, hece/sn, duraklar ölçülür; en iyi 3'ü hesap sahibine dinletilir, **seçimi o
   yapar**. Karar UZUN_FORMAT §1'e yazılır.
4. **Talidomit uzun videosu yeniden seslendirme** (aynı görüntü kurgusu):
   - bütün anlatım yeni sesle; paylasim.md'deki dinleme listesi (Grünenthal, günlük doz, taahhütlü, Kaymakçalan,
     talidomit, Nejat, lepra/cüzzam) özellikle kontrol edilir;
   - olay zamanlamaları yeni ses sürelerine göre kayar (motor satıra çapalı: çoğu kendiliğinden oturur), sonra kare kare kontrol;
   - `ses_onarim.py` Cartesia çekimlerine özeldi: yeni seste gerekmeyebilir, gerekirse yeniden ölçülür;
   - **filigran kaldırılır** (`filigran: false`; UZUN_FORMAT §2.8);
   - **büyük yüzler düzeltilir** (UZUN_FORMAT §2.9; etkin boyu 0,80 üstünde olan dört sahne: Ankara doruğu 0,96,
     Kaymakçalan tanıtımı 0,94, "Dünyayı Dolaşan" anlatıcı yakın planı 0,94, veteriner 0,87) ve `kontrol`'e etkin boy uyarısı eklenir;
   - dört hakem turu, teslim, Telegram.
5. **Talidomit kısa reel'inin karakterleri:** uzun videonun hazır kıyafetli v2 karakterleri ve temiz yüz varyantlarıyla
   (temsilci: sakin → gergin/terli; veteriner: sakin → ciddi/fark) bir B sürümü; STIL kuralları aynen (durağan, ~%48 boy,
   ters köşede aynı kutu + yüz varyantı). Görsel hakem iki sürümü orijinallerle yan yana karşılaştırır; ikisi hesap sahibine
   gider, seçimi o yapar. Kısa reel sessiz/müzikli olduğundan ElevenLabs'e bağlı değil, ama hesap sahibi bu işi de o
   döneme bıraktı.
6. **Yeni konular:** §2 takvimiyle; her biri ADIM_ADIM.md §3-§4 ve `docs/is_akislari/` şablonlarıyla.

Yapay zekâ görsel üretimi (SOL ağ geçidi) bırakıldı (hesap sahibi 16.10): gerçek görseller ve hazır wojak'lar kullanılır.
