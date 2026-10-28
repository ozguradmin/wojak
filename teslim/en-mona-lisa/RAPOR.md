# en-mona-lisa: RAPOR (Wojak Past Files, kanal: en)

**BEKLET.** Görsel hakem son tam puanı 7/10 verdi (tur 3, 1 MUST). Çıta 8/10 ve MUST yok olmadan yayın yapılmaz.
Son MUST (sakin ve şok yüzlerin gözbebekleri) düzeltildi ve kareler kendim kontrol ettim, ama üç tur sınırı dolduğu için
bu düzeltme için yeni hakem puanı alınmadı. Hesap sahibi karar verir: düzeltilmiş dosyayla bir hakem daha mı, yoksa doğrudan mı.

## Konu ve gerekçe

Üç aday (araştırmacı taraması, `konu-taramasi.md`):
1. **Mona Lisa'yı çalan adam, İtalya'ya satmaya çalıştı (Vincenzo Peruggia, 1911-1913). SEÇİLDİ.** Olgular ASFi (Floransa
   Devlet Arşivi) ve 1913 basınıyla doğrulandı; ters köşe güçlü (kendini vatansever sayan adamı Floransalı tacir ve Uffizi
   müdürü ihbar ediyor); kamu malı kanıt var (NYT 13 Aralık 1913 manşeti, Uffizi 1913 fotoğrafı); arka plan CC0.
2. Strasbourg dans salgını, 1518: ilginç ama ölüm sayısı ve yasak tarihi tartışmalı. Yedek.
3. Victor Lustig Eyfel Kulesi'ni sattı (1925): kanca en güçlüsü, ama ana ters köşe tek kaynaklı (1961 anısı). Yedek.

Çakışma: `wojak-en-ozel` teslim klasörlerinde (6 EN) ve Türk kanalı konu listesinde (26 bölüm, `data/videos.csv`) benzeri yok.
Kırmızı çizgi: yaşayan özel kişi yok, çocuk yok, süren dava yok, grafik içerik yok (Peruggia 1925'te öldü).

## Hakem turları

| Tur | Görsel hakem | İzleyici/olgu hakemi | MUST (görsel / izleyici) |
|---|---|---|---|
| 1 | 7/10 | 6/10 | 3 / 3 |
| 2 | 7/10 | 8/10 | 1 / 0 |
| 3 | 7/10 | (yeniden çağrılmadı; metin değişmedi) | 1 / - |

- Tur 1 (görsel): noktalı replik, yetim kelime ("Seriously?"), şok yüzünde içe bakmayan gözbebekleri. Düzeltildi.
- Tur 1 (izleyici): hikâyede kutunun Paris'te olduğu iddiası (ASFi'de yok: sandık Floransa otel odasında bulundu), 500.000 lira
  rakamına bağlı "mektup" cümlesi, toplar sırası. Düzeltildi ve ASFi sayfalarından yeniden doğrulandı.
- Tur 2 (görsel): şok yüzünde gözbebekleri hâlâ dışa bakıyordu. Kök neden: `peruggia.png` ve `peruggia_sok.png` bakış
  kaydı `sol` olarak girilmişti; render görüntüyü aynalıyordu. Kayıt `sag` yapıldı, şok gözbebeği sağa taşındı.
- Tur 3 (görsel): sakin yüzde (sahne 1 ve 3) gözbebekleri sola kaymıştı. Görüntü ayna düzeltmesi sonrası görünür oldu.
  Sakin gözler temiz ovallerle yeniden çizildi, gözbebekleri sağda. Bu son düzeltme hakem tarafından yeniden ölçülmedi.
- Tur 2 izleyici → son metin: "sell the painting to Italy", "Peruggia said ...", "passed away" (sansür "died" kelimesini bozuyordu).
  Bunlar tur 2'den sonra yapıldı ve hakem onayı almadı; küçük ve olgusal olarak kontrol edildi.

Son yayınlanacak sürüm (video, ses, kesmeler): hakem turu 3 ile aynı yapıdadır; sakin göz değişikliği dışında video kare kare
değişmedi. Ses: -29,6 LUFS, tepe -17,0 dBFS. Süre: 13,95 sn.

## Lisans tablosu

| Dosya | Kaynak | Lisans | Durum |
|---|---|---|---|
| `img/ev_1.jpg` (Uffizi, Aralık 1913) | Commons `Monalisa_uffizi_1913.jpg` (Commons kredisi: The Telegraph) | Kamu malı (1913, anonim) | Kabul. Orijinal yayın L'Illustration, 20 Aralık 1913 (captions). Telegraph orijinali kontrol edilmedi. |
| `img/ev_3.jpg` (NYT, 13 Aralık 1913, 1. sayfa, manşet kırpımı) | Commons NYT PDF (Internet Archive kopyası) | Kamu malı (ABD, 1913) | Kabul, manşet kırpıldı; gazetede bomba haberi olan sütun dışarıda. |
| `img/bg_florence.jpg` (Palazzo Vecchio) | Commons `Palazzo_vecchio_Florence.jpg` (Jebulon, 2011) | CC0 | Kabul, kare kırpımı, renk değişmedi. |
| `chars/peruggia.png`, `chars/peruggia_sok.png` | wojakland `worker_2_wojak` | Kanal standardı (27.10 kararı) | Kabul. Şok yüzü el ile düzenlendi (kütüphane gövdesi, göz ve ağız); sakin göz de yeniden çizildi. |
| `chars/geri.png` | wojakland `suit_wojak_1` | Kanal standardı | Kabul. |

Dışarıda bırakılanlar: 1909 Paris polis fotoğrafı (`Vincenzo_peruggia.jpg`; kimlik orta-düşük güvenle, Paris 1909 ve Florence
1913 karıştırılıyor; Corbis EXIF'li kopya reddedildi), Excelsior 1913 (Fransızca), Victoria Daily Times 1913 (küçük yazı). ASFi
1913 polis kartı kullanılmadı (arşiv izni gerekir).

## Olgu notları (ASFi, Floransa Devlet Arşivi; Storia di Firenze; History.com; History Today)

- Hırsızlık: Pazartesi 21 Ağustos 1911, personel kapısından yaklaşık 07.00, tablo çerçevesinden çıkarıldı, iş önlüğüne sarıldı.
- Mektup Kasım 1913, imza "Leonard V." (taranmış mektupta). "Leonardo Vincenzo" kullanılmadı.
- 500.000 lira: "later accounts" ile, belgede doğrulanmadı.
- 11 Aralık: Hotel Tripoli (Via Panzani), Geri ve Poggi. 12 Aralık: tutuklama (polis kartı). Otel odasındaki çift dipli sandık arama sırasında.
- Mahkeme: vatanseverlik iddiası kabul edilmedi; Haziran 1914 ceza 1 yıl 15 gün; temyizde 7 ay 8 gün (zaten çekilmiş).
- Floransa, Roma, Milano'da gösterim (ASFi: 14-18 Aralık Floransa); Louvre'a dönüş 4 Ocak 1914 (ikincil kaynak; ASFi vermiyor).
- Ölüm: 8 Ekim 1925, Saint-Maur-des-Fossés.
- Replikler uydurma; açıklama ve sabit yorumda "Dramatized" notu var.

## Bilinen kusurlar

1. **Peruggia kostümü:** tulum ve kasket; Louvre işçisinin beyaz önlüğü değil. Kütüphanede 1911-1913 dönemine uygun işçi karakteri bulunamadı. Hakem SHOULD olarak aldı.
2. **Geri'nin fötr şapkası ve gri takım** 1913 için biraz geç (fötr yerine bowler daha uygun olurdu).
3. **Arka plan kartpostal gibi:** Palazzo Vecchio tek fotoğraf, gökyüzü parlak; hakem "postcard" dedi. Diyalog bir otel odasında geçiyor; dış mekân yakın eşdeğer.
4. **Şok yüzü el ile düzenlendi:** kütüphane gövdesi, bakış ve kaş değişikliği; "hazır yüz" kuralına tam uymuyor. Gözler yeniden çizildi.
5. **Sakin göz** temiz oval olarak yeniden çizildi; eski, daha ifadeli göz kaybedildi. Hakem yeniden ölçmedi.
6. **500.000 lira** ve **4 Ocak 1914** tarihi tek yönlü kaynaklara dayanıyor; metinde "later accounts" ile.
7. Hikâye metni 246 kelime (sınır 150-250); açıklama 1.344 karakter; `d*ed` yok ("passed away").

## Süre ve maliyet

- Duvar saati: 16:23 (hazırlık başı) - 17:03 UTC, yaklaşık 40 dakika; alt ajan süreleri bu süreye dahil değil.
- Adım süreleri (yaklaşık): hazırlık 12 dk; konu taraması ve üç aday paralel; olgu+görsel araştırma paralel; üretim ve render 15 dk;
  hakem turları ve düzeltmeler 3 tur; teslim.
- Ücretli API maliyeti bu ortamda ölçülmedi. Kullanılan alt ajan çağrıları: 4 araştırmacı, 3 görsel hakem turu, 2 izleyici hakem turu.

## Ajan görev dağılımı

- **Wojak EN Araştırmacı (konu taraması):** 3 aday, gerekçe, kanal çakışma kontrolü, lisans ön kontrolü.
- **Wojak EN Araştırmacı (olgu):** ASFi ve basın doğrulaması, 5 popüler iddiayı düzeltti, İngilizce taslak.
- **Wojak EN Araştırmacı (görsel ve karakter):** NYT, Uffizi, mugshot ve Floransa arka planı adayları; karakter seçimi.
- **Wojak EN Hakem Görsel (3 tur):** kare kare ve 1:1 yüz ölçümü; bakış hatasının kökü.
- **Wojak EN Hakem İzleyici (2 tur):** olgu doğrulama (ASFi, Storia di Firenze, History.com), İngilizce, başlık.
- **Üretici (ben):** `episode.yaml`, bakış kayıtları, şok ve sakin yüz düzeltmeleri, NYT kırpımı, render, teslim paketi.

## Teslim içeriği

`en-mona-lisa.mp4` (13,95 sn, 1080x1920), `kapak.jpg`, `paylasim.md`, `metinler/` (5 dosya), bu RAPOR, `BEKLET`.
YAYINLANDI.json yok; yayın botu bu klasöre dokunmaz (BEKLET nedeniyle).
