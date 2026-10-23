# ayasofya-viking-yazisi: üretim raporu (23.10.2026, A sürümü; telifli görsel yok)

> **Yayın durumu:** BEKLET **yok**. Hassas konu kuralının hiçbir maddesine girmiyor: yaklaşık bin yıllık tarihî bir
> yazıt; güncel olay değil (GUNDEM §5/§7 kapsamı dışı), çocuk yok, son 10 yılda ölen yok, yaşayan özel kişi yok, süren
> dava yok. Lisans kararı bekleyen görsel yok (iki CC BY-SA 4.0, bir kamu malı; hepsi Commons dosya sayfasının ham
> metninden doğrulandı). İki hakem 8/8, MUST yok.

**Konu:** Ayasofya'nın güney üst galerisindeki mermer korkulukta runik harflerle kazınmış bir yazı var. 1964'te fark
edildi, 1970'te yayımlandı; okunabilen tek kelime bir İskandinav erkek adı: Halvdan (Halfdan). Kim olduğu bilinmiyor;
Vareg muhafızı olabileceği düşünülüyor. Yazı bugün şeffaf bir koruma altında, yanındaki levhayla gösteriliyor.

## Ortam

4 çekirdek, 15 GB RAM, 30 GB boş disk, Python 3.11.17, ffmpeg 6.1.1. Avenir fontu ve referans reel'ler kuruldu,
render Avenir ile yapıldı. Testler: 81/81 geçti. `grep MUSIC_IMZA wojak/config.py` → `imza_v2_golge.m4a`.
`/home/user` yoktu: `mkdir -p /home/user` sonra sembolik bağ.

## Konu gerekçesi (3 aday)

| Aday | Neden | Karar |
|---|---|---|
| **Ayasofya'daki Viking yazısı (Halvdan)** | Tek cümlelik "Ne?!": Ayasofya'nın mermerinde bin yıllık bir Viking "buradaydım" yazısı var ve bugün levhasıyla korunuyor. İstanbul'da, herkesin bildiği yapıda. İroni kanalın imza kalıbı: "kimse fark etmez" → son karede yazının levhası. 6+ bağımsız kaynak (Vikipedi EN/TR, Euronews TR 21.08.2026, Arkeonews, Atlas Obscura, viking.archeurope). Euronews'in Ağustos 2026 haberi gündem kancası. Kanıtın kendisi Commons'ta serbest lisanslı fotoğraf. Grafik içerik, çocuk, mağdur yok | **Seçildi** |
| Kaşıkçı Elması efsanesi (çöplükte bulunup üç kaşığa satılan taş) | Türkiye'de, ironi güçlü. Ama tek kökenli efsane; Topkapı'da fotoğraf yasak, serbest lisanslı kanıt zayıf | Yedek |
| Süleymaniye'nin "is odası" (kandil isinden mürekkep) | Türkiye'de, "Ne?!" orta. Kanıt fotoğrafı (is odası) Commons'ta bulunamadı; ters köşe zayıf | Yedek |

Kanalda yapılmadığını kontrol ettim: `data/videos.csv` (223 başlık), `data/instagram_reels.csv`, `data/olay_metinleri.md`,
`docs/KONU_HAVUZU.md`, `episodes/` ve `wojak-ozel/teslim/` (kanuni-gizlenen-olum, karun-hazinesi-bros). "Viking",
"Halfdan", "Vareg" hiçbirinde konu olarak geçmiyor (yalnız kanuni RAPOR'unda "yedek aday" olarak). Bugünkü 11:00
bölümünden (Kanuni, Zigetvar) konu ve dönem olarak uzak.

## Sahne akışı (14,0 sn)

| Zaman | Sahne | Replik |
|---|---|---|
| 0-3,0 | Viking (sol, huysuz yüz) | Bu ayin hiç bitmiyor, sıkıldım ya |
| 3,0-5,5 | Bizans muhafızı (sağ, ciddi) | Sessiz ol, herkes bize bakıyor |
| 5,5-8,0 | Viking (aynı yüz) | Adımı şu mermere kazıyorum, / kimse fark etmez |
| 8,0-10,5 | Muhafız, aynı kutu, **şok yüzü** (iri gözler, kalkık kaşlar, "O" ağız, ter damlaları) | Delirdin mi, burası Ayasofya |
| 10,5-12,0 | Kanıt 1 | Galerideki mermer korkulukta, pleksiglas altında runik yazı (2024 fotoğrafı) |
| 12,0-14,0 | Kanıt 2 (son kare) | Yazı ve yanındaki levha: "9. yy'a tarihlenen Viking'ce yazı ....HALVDAN....adı okunabilmektedir" (2005 fotoğrafı) |

Arka plan: Ayasofya'nın üst galerisi (mermer korkuluk, sütunlar, nef). Müzik: `music: {file: kanal, volume: 0.197}`
(imza_v2_golge), **-29,6 LUFS, tepe -17,0 dBFS** (ölçüldü). Video ve ses 0,000'da başlıyor; kesmeler 3,0 / 5,5 / 8,0 /
10,5 / 12,0 sn (kare farkı); sahne içi hareket 0,00-0,01.

**Son kare çeşitliliği:** son 5 bölümün son kareleri: Kanuni (Osmanlı minyatürü), Karun (kendi kupürümüz), Talidomit
(mobil haber sayfası), Kız Kulesi (sergi kartı), Çanakkale (gazete sayfası). Bu bölüm **gerçek nesnenin fotoğrafıyla,
yanındaki levhayla** bitiyor: olay basında değil taşın üstünde kayıtlı. Kupür, kart, minyatür yok.

## Hakem puanları

Hakemler ayrı bağlamda çalıştırılamadı. Her tur sıfırdan yürütüldü: yalnız `kisa_reel.js` içindeki JUDGE_VISUAL ve
JUDGE_FOLLOWER istemleriyle ve yalnız teslim dosyalarına (mp4, kapak, metinler) bakarak. Ölçüm: 0,5 sn kareler; C2kk,
C4V3, C2Fr, C12O ile aynı ölçekte yan yana sayfa; telefon boyu (390 px); kare farkıyla kesme; ebur128; arka plan kenar
Laplace varyansı (720 ölçeği); kanıt yüksekliği ve merkezi; yüz değişim alanı.

| Tur | Görsel | Takipçi + olgu | MUST | Not |
|---|---|---|---|---|
| Ön kontrol (üretici) | — | — | 1 | Telefonda yüz değişimi %0,37 (eşik %0,40): boy 0,48 → 0,52, ter damlaları büyütüldü → %0,44 |
| 1 | 7,5 | 8 | yok | Görsel: telefonda kanıt 1'in runleri seçilmiyor, levha yazısı küçük (en zayıf öğe puanı sınırlar). Takipçi SHOULD: "büyük ihtimalle" fazla kesin, "yakıştırma" sert, "müzenin levhası" (yapı artık cami) |
| **2** | **8** | **8** | yok | Kanıtlar sıkı kırpıldı (runler ve levha telefonda okunuyor); arka plan orijinallerden yumuşaktı (Laplace ~7, orijinal medyan ~22): blur 2,5 → 1,6 (~20). Metin düzeltmeleri yapıldı. Durma noktası |

Hakemlerin gerekçesi (2. tur):
- **Görsel 8:** Biçim, süreler, yazı (Avenir, 55 px, reel boyunca sabit) ve ses STIL'e birebir. Karakterler hazır
  kıyafetli, içeri bakıyor, ters köşe yüzü telefonda okunuyor. Arka plan gerçek mekân, doğal renk. Kanıtlar tam
  genişlik, y=960 merkez, 608 ve 675 px. Puanı sınırlayan: son kare kalın bir manşet değil, levha yazısı küçük
  punto; Viking çizimi klasik beyaz wojak'tan daha gölgeli; muhafızın yüzü miğfer içinde küçük.
- **Takipçi 8:** Kanca 1 sn'de oturuyor (Ayasofya'da sıkılan bir Viking). Replikler doğal konuşma Türkçesi. İroni
  ("kimse fark etmez" → levha) son karede sessizce ödeniyor. 7 olgu kaynaktan doğrulandı: 1964, Svärdström 1970,
  okunabilen tek kelime Halvdan, Vareg muhafızları 10. yüzyıl sonu (988), Miklagard, 1975'te ikinci yazı (Árni),
  şeffaf koruma; levhadaki "9. yy" fotoğrafta. Puanı sınırlayan: son replik bir "Bekle, ...?" sorusu değil, şaşkın
  tepki; ters köşe Kırkağaç düzeyinde bir şok değil, eğlenceli bir "Ne?!".

## Bilinen kusurlar

1. Son kare bir levha fotoğrafı; levha yazısı telefonda okunuyor ama kalın bir manşet kadar anında değil. 2005
   fotoğrafı, flaşlı ve hafif karanlık.
2. Arka planda (2004 fotoğrafı) uzakta küçük bir Osmanlı hat levhası görünüyor; sahne Bizans dönemi. Telefonda yazının
   arkasında küçük kalıyor.
3. Arka plan, yazının bulunduğu güney galerisi değil, aynı katın kuzeydoğu tarafı (galerinin serbest lisanslı en
   temiz fotoğrafı).
4. Muhafızın kaynak çizimi 460 px; ekranda ~1,2 kat büyütüldü, 1:1'de hafif yumuşak.
5. "Ayin sırasında sıkıldı" anlatısı popüler bir yorum; ekranda canlandırma, metinde "anlatılana göre".
6. Video süresi 13,93 sn (son kare ffmpeg'in kare yuvarlaması; önceki bölümlerde de aynı).

## Lisans kararları

Lisans kararı bekleyen görsel **yok**. Telifli görsel hiçbir sürümde yok; yalnız A sürümü var.

| Görsel | Kaynak | Lisans | Sürüm |
|---|---|---|---|
| Arka plan `img/arka_galeri.jpg` | Commons "Hagia Sophia upper gallery NE side to right of Loge of the Empress in 2004 4673.jpg", Dosseman, 2004 (kırpıldı, gama 0,72) | CC BY-SA 4.0 (`{{self|cc-by-sa-4.0}}`, dosya sayfasında doğrulandı) | A |
| Kanıt 1 `img/kanit_1_runler.jpg` | Commons "PXL 20241210 064800376.MP ... Halfdan inscription Viking runic inscription 23.jpg", Sourabh.biswas003, 2024 (kırpıldı) | CC BY-SA 4.0 (`{{self|cc-by-sa-4.0}}`) | A |
| Kanıt 2 `img/kanit_2_levha.jpg` | Commons "Hagia-sofia-viking.jpg", en.wikipedia kullanıcısı Not home, 2005 (kırpıldı, gama 0,9) | Kamu malı (`{{PD-user-en}}`) | A |
| Karakter A (Viking) | wojakland "Viking Wojak" (viking_wojak_1.png), değişmeden | Topluluk memesi (wojakland'de şart sayfası yok; kanalın yerleşik pratiği) | A |
| Karakter B (Bizans muhafızı) | wojakland "Byzantine Knight Wojak" + kendi yüz varyantımız (`chars/uret.py`) | Aynı | A |

CC BY-SA atıfları `credits` alanında, açıklamaların sonunda (lisans adresiyle). Levhanın metni basit bilgi yazısı.

Serbest görsel araması (Wikimedia Commons API, İngilizce ve Türkçe):
- "Halfdan runes Hagia Sophia", "runic inscription Hagia Sophia" → 9 aday indirildi, temas sayfasında incelendi;
- "Hagia Sophia south gallery", "Hagia Sophia gallery columns marble", "Ayasofya galeri", "Hagia Sophia upper gallery
  interior", "Hagia Sophia gallery marble balustrade", "Hagia Sophia north/west gallery", "Hagia Sophia empress loge"
  → arka plan için 17 aday.
Olayı birebir gösteren serbest lisanslı fotoğraflar bulunduğu için kanıt üretmeye gerek kalmadı. Openverse ve
Internet Archive'a gerek olmadı.

## Adım süreleri (UTC, 23.10.2026)

| Adım | Süre (saat damgasıyla ölçüldü) |
|---|---|
| Ölçüm + hazırlık + belgeleri okuma (81 test ~21 sn) | ~5 dk |
| Konu tarama + 3 aday + olgu araştırması (2 web araması; 6+ kaynak) | ~2 dk |
| Görsel avı (Commons API + md5 yolu; birkaç 429; 26 aday) | ~10 dk |
| Karakterler + yüz varyantı (`chars/uret.py`) | ~5 dk |
| episode.yaml + check + frames + render + teslim | ~2 dk |
| Ön kontrol + 2 hakem turu + düzeltmeler | ~5 dk |
| RAPOR, teslim kopyaları, commit/push, OGRENILENLER | ~3 dk |
| **Toplam** | **~31 dk** |

Not: özel depodaki RAPOR kopyası adım başına daha yüksek bir tahmin (~45 dk) taşıyor. Yayın botu tetiklenmesin diye
o kopya değiştirilmedi; ölçülen değer bu tablodur.

**Yaklaşık maliyet:** Ücretli API kullanılmadı (TTS ve görsel üretimi yok), 0 TL. Model kullanımı oturum içi.

## Kod hatası (raporlandı, düzeltilmedi: `wojak/` değişmez)

Kanuni bölümünde bulunan `wojak/audio.py` loudnorm hatası sürüyor (ffmpeg 6.1.1'de TP=-17 reddediliyor, sessizce
`anull`). Bu bölümde de `volume: 0.197` ile aşıldı ve ölçüldü (-29,6 LUFS).
