# gobeklitepe-mezar-tasi: üretim raporu (24.10.2026, A sürümü; telifli görsel yok)

> **Yayın durumu:** BEKLET **yok**. Hassas konu kuralının hiçbir maddesine girmiyor: 1963'teki bir arkeolojik yüzey
> araştırması; güncel olay değil (GUNDEM §5/§7 kapsamı dışı), çocuk yok, son 10 yılda ölen yok (adı geçen tek kişi
> Klaus Schmidt, 2014'te öldü), yaşayan özel kişi yok (köylü ve arkeolog adsız kurgu karakterler; 1963 raporunu yazan
> arkeoloğun adı hiçbir yerde yok), süren dava yok. Lisans kararı bekleyen görsel yok (üç fotoğraf CC BY-SA 4.0, Commons
> dosya sayfasının ham metninden doğrulandı; son kare kendi kupür tasarımımız). İki hakem 8/8,5, MUST yok.

**Konu:** Göbeklitepe 1963'te İstanbul ve Chicago üniversitelerinin ortak yüzey araştırmasında kayda geçti. Ekip
çakmaktaşı aletleri Taş Devri'ne ait saydı ama toprağın üstünde görünen büyük kireçtaşı blokları mezar taşı sandı ve
tepede kazı yapılmadı. 1994'te Klaus Schmidt "mezar taşları"nın gömülü dev T dikilitaşların tepeleri olduğunu fark etti.
Yaklaşık 11.500 yıllık yapılar bugün "dünyanın bilinen en eski tapınağı" diye anılıyor.

## Ortam

4 çekirdek, 15 GB RAM, 30 GB boş disk, Python 3.11.17, ffmpeg 6.1.1. Avenir fontu ve referans reel'ler (75 mp4) kuruldu,
render Avenir ile yapıldı. `/home/user` yoktu: `mkdir -p /home/user` sonra sembolik bağ. Testler bağdan önce 80/81 (bir
test eski sabit yolu arıyordu), bağdan sonra 81/81. `grep MUSIC_IMZA wojak/config.py` → `imza_v2_golge.m4a`.

## Konu gerekçesi (3 aday)

| Aday | Neden | Karar |
|---|---|---|
| **Göbeklitepe: 1963'te taşları mezar taşı sanıldı** | Tek cümlede "Ne?!": dünyanın en eski tapınağı sayılan yerin dikilitaşları ilk bulunduğunda mezar taşı sanıldı, 31 yıl kazılmadı. Türkiye'de, herkesin adını bildiği bir yer. İroni + ters köşe kalıbına birebir uyuyor ("Kazmaya değmez, burada önemli bir şey yok" → son karede "Göbeklitepe" manşeti). 6+ bağımsız kaynak (Vikipedi, DAI, Evrim Ağacı, DergiPark, Smithsonian, AA/NTV). Commons'ta onlarca serbest lisanslı fotoğraf. Mağdur, çocuk, grafik içerik yok | **Seçildi** |
| Noel Baba'nın (Aziz Nikolaos) Demre'den çalınan kemikleri (1087) | Türkiye'de, "Ne?!" güçlü, serbest görsel bol. Ama Karun bölümüne tema olarak yakın ("Türkiye'den çalınan eser") ve 2017'deki "asıl mezar Demre'de" iddiası tartışmalı | Yedek |
| Hezarfen Ahmed Çelebi'nin Galata'dan uçuşu ve sürgünü | İroni güçlü (başarıya ödül yerine sürgün). Tek kaynak Evliya Çelebi ("anlatılana göre"); dün akşamki Ayasofya'dan sonra yine İstanbul/Osmanlı | Yedek |

Kanalda yapılmadığını kontrol ettim: `data/videos.csv` (223 başlık), `data/instagram_reels.csv`, `data/olay_metinleri.md`,
`docs/KONU_HAVUZU.md` (Göbeklitepe havuzda, işaretsiz), `episodes/` ve `wojak-ozel/teslim/` (ayasofya, kanuni, karun).
"Göbek" hiçbirinde konu olarak geçmiyor. Dünkü iki bölümden (Kanuni/Zigetvar, Ayasofya Viking yazısı) konu, dönem ve
yer olarak uzak.

## Sahne akışı (14,0 sn)

| Zaman | Sahne | Replik |
|---|---|---|
| 0-3,0 | Köylü (sol, hasır şapka, endişeli merak) | Hocam bu dev taşlar ne? |
| 3,0-5,5 | Arkeolog (sağ, mantar kask, kendinden emin) | Mezar taşı bunlar, / eski bir mezarlık |
| 5,5-8,0 | Köylü (aynı yüz) | Daha kazmadınız ki, / nasıl anladınız? |
| 8,0-10,5 | Arkeolog, aynı kutu, **ters köşe yüzü** (iç uçları kalkık kaşlar, köylüden kaçan gözler, titrek ağız, 2 ter damlası) | Kazmaya değmez, burada / önemli bir şey yok |
| 10,5-12,0 | Kanıt 1 | Kazılmış D yapısı: T biçimli dikilitaş çemberi (2021 fotoğrafı) |
| 12,0-14,0 | Kanıt 2 (son kare) | Kendi kupür tasarımımız: "Tarihi değiştiren dünya mirası: / Göbeklitepe" + spot "Stonehenge'den 7 bin, Mısır piramitlerinden ise 7 bin 500 yıl daha eski." Altında "Kaynak: Hürriyet Seyahat, 9 Temmuz 2018" |

Arka plan: Göbeklitepe'nin doruğundaki dilek ağacı (gerçek yer; `blur: 1.6`, kenar Laplace varyansı yanlar ~19-20).
Müzik: `music: {file: kanal, volume: 0.197}` (imza_v2_golge), **−29,6 LUFS, tepe −17,0 dBFS** (ölçüldü). Video ve ses
0,000'da başlıyor; kesmeler 3,0 / 5,5 / 8,0 / 10,5 / 12,0 sn (kare farkı); sahne içi hareket 0,00. Diyalog karesi
parlaklığı 107-118, doygunluk 0,25-0,28. Telefonda (390 px) ters köşe yüz değişimi %0,61 (eşik %0,40).

**Son kare çeşitliliği:** son 5 bölümün son kareleri: Ayasofya (nesne + levha), Kanuni (minyatür), Karun (sararmış
kupür, gri raster, grotesk manşet), Talidomit (mobil haber sayfası), Kız Kulesi (sergi kartı). Bu bölüm basında çıkan
bir haberle bitiyor: kupür, ama Karun'dan farklı görünümde (2018 renkli hafta sonu eki gibi daha beyaz kâğıt, serif
manşet, renkli CMYK raster fotoğraf, alt kenar yırtık, ters yöne eğik, mavi-gri kumaş zemin). Bir önceki bölümle aynı
tür değil.

## Hakem puanları

Hakemler ayrı bağlamda çalıştırılamadı. Her tur sıfırdan yürütüldü: yalnız `kisa_reel.js` içindeki JUDGE_VISUAL ve
JUDGE_FOLLOWER istemleriyle ve yalnız teslim dosyalarına (mp4, kapak, metinler) bakarak. Ölçüm: 0,5 sn kareler; C2kk,
C4V3, C12O ile aynı ölçekte yan yana sayfa; telefon boyu (390 px); kare farkıyla kesme; ebur128; arka plan kenar
Laplace varyansı (720 ölçeği); kanıt yüksekliği; yüz değişim alanı. "Telefonda bakan biri bunu gerçek gazete kupürü
sanır mı?" sorusu da puanlandı.

| Tur | Görsel | Takipçi + olgu | Kupür "gerçek sanılır" | MUST | Not |
|---|---|---|---|---|---|
| Ön kontrol (üretici) | — | — | — | 3 | İlk karelerde üç replikte satır sonu yetim kelime ("ne?", "mezarlık", "hocam?"); arkeoloğun yüzü küçük; ter damlaları gözyaşı gibi okunuyordu. Replikler virgülde kırıldı/kısaltıldı, arkeolog PNG'si göğüsten kesildi (yüz büyüdü), damlalar başın yanına alındı |
| 1 | 8 | 8 | 8 | yok | Görsel SHOULD: kanıt 1 telefonda soluk (parlaklık 170), kupür 820 px (STIL sınırı 816). Takipçi SHOULD: başlıkta somut yer yok, "Otuz yıl" (gerçekte 31), "Neolitik" sıfat olarak küçük harf |
| 2 | 8 | 8,5 | 8 | yok | SHOULD'lar uygulandı: kanıt 1 gama 1,18 + kontrast (158), kupür 810 px, başlık "Urfa'da arkeologların mezar taşı sandığı taşlar", "Otuz bir yıl sonra", "neolitik". Durma noktası (iki hakem ≥ 8, MUST yok) |

Görsel hakemin tavan notu: arka plandaki gökyüzü orijinallerin çoğundan daha doygun mavi; köylünün hasır şapkası 1963
Urfa'sı için "genel köylü" okunuyor (hazır kıyafetli çizim; elle kıyafet boyamamak için bilerek bırakıldı).

## Başlık seçenekleri

1. **Urfa'da arkeologların mezar taşı sandığı taşlar** (yayında)
2. 1963'te mezar taşı sanılıp 31 yıl kazılmayan tepe
3. Göbeklitepe'yi ilk bulanlar neyi kaçırdı?

## Bilinen kusurlar

- "Kazmaya değmez, burada önemli bir şey yok" repliği canlandırma. Belgeli olan: ekip taşları mezar taşı sandı, tepede
  kazı yapılmadı ve yerin önemi kaçırıldı (DAI). Ekip aletleri neolitik olarak tanımıştı; metin bunu açıkça yazıyor.
- Kupürdeki spot "Stonehenge'den 7 bin" diyor; bilimsel kaynaklar farkı ~6.000-6.500 yıl veriyor. Kupür birebir
  alıntı olduğu için değiştirilmedi; hikâye metni sayı vermeden "binlerce yıl" diyor.
- Hikâye metnindeki tek gerçek kişi adı Klaus Schmidt (kamusal bilim insanı, 2014'te öldü).
- Video süresi ffprobe'da 13,93 sn (önceki onaylı bölümlerle aynı render davranışı).

## Lisans kararları

Lisans kararı bekleyen görsel **yok**. Telifli görsel hiçbir sürümde yok.

| Görsel | Kaynak | Lisans | Sürüm |
|---|---|---|---|
| `img/arka_dilek_agaci.jpg` (tüm diyalog) | Commons, "Gobekli Tepe Wishing tree in 2014 3174.jpg", Dosseman | CC BY-SA 4.0 (`{{self\|cc-by-sa-4.0}}`) | A |
| `img/kanit_1_tapinak.jpg` (kanıt 1) | Commons, "Gobeklitepe.jpg", Kerimbesler, 2021 | CC BY-SA 4.0 (`{{self\|cc-by-sa-4.0}}`) | A |
| `img/kanit_2_kupur.jpg` (son kare) | Kendi tasarımımız (`kupur.py`); içindeki fotoğraf Commons "Gobekli Tepe 4.jpg", Immanuelle, 2018; başlık Hürriyet Seyahat 09.07.2018'den birebir alıntı (logo, yazı karakteri, düzen yok) | Fotoğraf CC BY-SA 4.0; fontlar SIL OFL | A |
| Köylü karakteri | wojakland "Farmer Wojak" | wojakland (şart sayfası yok, topluluk memesi) | A |
| Arkeolog karakteri | wojakland "Safari Wojak" (yüz yeniden çizildi, aynalandı) | wojakland | A |

Atıflar `credits` alanında, bütün açıklamalara giriyor; "Son kare canlandırmadır; söz Hürriyet Seyahat, 9 Temmuz 2018
başlığından." satırı da açıklamalarda. Serbest görsel araması: Commons API (İngilizce "Göbekli Tepe", "Göbekli Tepe tree",
"Göbekli Tepe enclosure D"; Türkçe "Göbeklitepe dilek ağacı", "Örencik Şanlıurfa"). Serbest görsel bol olduğu için Openverse
ve Internet Archive'a gerek kalmadı. Gazete manşetinin serbest lisanslı gerçek görüntüsü yok (Hürriyet sayfası telifli);
bu yüzden kupür kendimiz dizildi.

## Adım süreleri (ölçülen duvar saati: başlangıç 11:09, özel depoya push 11:33; toplam ~25 dk)

| Adım | Süre |
|---|---|
| Hazırlık + ölçüm + okuma | ~5 dk |
| Konu tarama + 3 aday + olgu araştırması (5 arama + 1 sayfa) | ~4 dk |
| Görsel avı (Commons API + küçük resim temas sayfası + ham lisans + md5 indirme) | ~2 dk |
| Karakter + yüz varyantı (uret.py, kontur onarımı) | ~4 dk |
| gorsel.py + kupur.py + episode.yaml + check/frames/render/teslim | ~3 dk |
| Ön kontrol + 2 hakem turu + düzeltme | ~3 dk |
| RAPOR + outputs + iki depo commit + OGRENILENLER | ~4 dk |

(Özel depodaki RAPOR kopyasında ilk tahmin ~32 dk yazıyor; yayın tetiklememek için o kopya yeniden push'lanmadı.)

## Yaklaşık maliyet

Ücretli API yok (TTS ve görsel üretimi yok). Yalnız bu oturumun model kullanımı.
