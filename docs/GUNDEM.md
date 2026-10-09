# Gündem (güncel olay) oyun kitabı

Kanal sadece geçmiş olaylarla değil **güncel olaylarla** da beslenecek. Bu belge: neden, nasıl seçilir,
nasıl anlatılır, nelerden kaçınılır.

<!-- BOLUM:VERI -->

## 1. Günlük rutin (15-20 dk)

```bash
python tools/gundem.py                 # son 48 saat -> out/gundem/<tarih_saat>.md
python tools/gundem.py --saat 24 --ilk 30
python tools/gundem.py --sorgu "maden" --sorgu "göçük"   # o gün özel bir konu varsa
python tools/gundem.py --taslak 3      # rapordaki 3. olay için episodes/gundem-... taslağı
```

Rapor her olay için şunu verir: temsilî başlık, puan dökümü (uygunluk, kaç kaynak yazdı, Google Trends,
tazelik, konu dışı cezası), tür (kayıp, mucize, kahramanlık, gizem, suç, kaza, tarih, hayvan),
**⚠️ DİKKAT** işareti (çocuk istismarı, intihar, terör, okul saldırısı, yayın yasağı ihtimali),
4 haber linki ve bir açı önerisi. Ayarlar ve kaynak listesi: `data/gundem_kaynaklar.yaml`.

Bilinen sınır: aynı olay farklı kelimelerle yazıldığında 2-3 kümeye bölünebilir, nadiren iki
benzer olay birleşebilir. Rapor **karar destek** listesidir; linkleri açıp kontrol et.

Kaynaklar (2026-10-09 test): Google News TR + 12 hedefli Google News araması, Google Trends TR,
Hürriyet, Sözcü, CNN Türk, Habertürk, AA, TRT Haber, BBC Türkçe, DW Türkçe. Bir taramada ~850 haber.

## 2. Hangi güncel olay? (seçim kriterleri)

Bir olayı yapmak için **en az 3 "evet"**, hiç "kırmızı çizgi" yok:

| Soru | Neden |
|---|---|
| Ülke çapında konuşuluyor mu? (≥10 kaynak veya Google Trends'te) | Arama ve paylaşım talebi hazır |
| İçinde net bir **insan hikâyesi** var mı? (kahraman, kurban, kayıp, kurtulan) | Wojak formatı insanı anlatır; "bina çöktü" değil "enkazdan 22 saat sonra çıkan kız" |
| Tek bir **ironik/ürpertici an** var mı? | Replik ondan doğar (son masum cümle, son mesaj, ilk söz) |
| Gizem / mucize / fedakârlık unsuru var mı? | Altın dönemin en güçlü türleri |
| Gerçek fotoğraf/görüntü var mı? | Kanıt sahnesi |

**Kırmızı çizgiler (yapma):** yayın yasağı olan dosya · çocuk istismarı/cinsel suç ayrıntısı ·
intiharı anlatmak (yöntem, mekân) · terör saldırısının failini öne çıkarmak · resmi açıklama yokken
"cinayet" demek · siyasi/partizan konu · olaydan saatler sonra, kimlikler netleşmeden.

## 3. Hız

- **Kahramanlık / mucize / tuhaf olay:** 24-72 saat içinde. Erken olmak avantaj.
- **Kayıp / ölüm / suç:** önce **resmi açıklama** (valilik, emniyet, jandarma, AFAD, savcılık) bekle.
  Kayıp vakalarında sonuç belli olmadan "kurban" anlatımı yapma; "aranıyor" durumunda yapılacaksa
  amaç bilgilendirme olmalı (afiş, ihbar hattı).
- **Büyük felaket (deprem, çökme):** ilk saatlerde değil; kurtarma hikâyeleri netleşince
  (ör. "X saat sonra enkazdan çıkarılan..."). Acı tazeyken mizah ve "gizem" tonu yok.

## 4. Formatın güncel olaya uyarlanması

Altın dönem formatı aynen geçerli (11-15 sn, gerçek mekân + wojak + tek replik + gerçek kanıt + sabit yorum).
Farklar:

- **Kanıt sahnesi = haber:** `type: evidence` + `banner: "SON DAKİKA: ..."` ile haber bandı ya da
  haber ekran görüntüsü. Kaynak gazete adı `label:` ile görünür olsun (şeffaflık).
- **Replik yalnızca doğrulanmış bilgiden kurgulanır.** Kişinin gerçek sözü haberlerde varsa onu kullan
  (tırnak içinde, kısaltılmış). Yoksa durumu ima eden genel bir cümle (*"Birazdan dönerim"*).
  Asla olmayan bir suçlamayı karakterin ağzına koyma.
- **Fail/şüpheli:** isim ve yüz benzerliği yok, karar kesinleşmeden "katil" yok ("şüpheli").
- **Başlık:** olayın en çarpıcı **doğrulanmış** tek cümlesi
  (*"10 saat aranan 5 yaşındaki Efe kamyonet kasasında uyurken bulundu"*).
- **Sabit yorum:** kronoloji + "Resmi açıklamaya göre..." + kaynak adı + tarih.
  Gelişme olursa yorumu güncelle ("GÜNCELLEME 12.10: ...").
- **Devam videosu:** büyük gelişmede ikinci video ("Efe'nin bulunduğu an" gibi) — seri izleyici getirir.

## 5. Yayından önce kontrol listesi

<!-- BOLUM:KONTROL -->

## 6. Takvim önerisi

Haftada en az 3 video: **1-2 güncel + 2 tarihsel/efsane**. Güncel olaylar sıcakken öne alınır; tarihsel
konular `docs/KONU_HAVUZU.md`'den, önceden hazırlanıp bekletilebilir ("stok" video).

<!-- BOLUM:HUKUK -->
