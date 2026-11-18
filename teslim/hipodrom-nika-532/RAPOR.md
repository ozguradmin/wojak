# RAPOR: hipodrom-nika-532

**BEKLET: VAR** (yalnız not; 2.11'den beri yayını durdurmaz). Neden: 3. turda takipçi hakem tek bir metin MUST'ı verdi
(açıklamada "son satırda" ifadesi yeni son kareyle çelişiyordu); düzeltildi (5 metin dosyası + paylasim.md, grep ile
"son satırda" yok), ama tur sınırı (3) dolduğu için düzeltme yeniden puanlanmadı (el kitabı §3). Hassas konu yok
(532 olayı; çocuk, yakın ölüm, yaşayan özel kişi, süren dava, gündem yok).

## Konu
Nika İsyanı, Konstantinopolis, 18 Ocak 532. Eski Ayasofya yanmış, kalabalığa imparatorun kaçtığı söylenmiş; isyancılar
Hipodrom'da (bugünkü Sultanahmet Meydanı) yeni imparator ilan ediyor. Askerler Hipodrom'a iki yandan giriyor.
**"Ne?!" cümlesi:** Sultanahmet Meydanı'nda bir günde 30.000'den fazla kişi öldürüldü (Prokopios); bugünkü Ayasofya bu
isyandan sonra yapıldı.
Damar 2 (Türkiye'de gösterilebilir yerde tarihî facia). Gündem yok (en iyi aday aşağıda).

## Gündem taraması (tools/gundem.py --saat 72 --ilk 15, 18.11 19:09)
En iyi aday: "Çorum'da şüpheli ölüm" (47 kaynak, dalga 17.11): elendi; dalga 1 gün önce sınırda, resmî açıklama yok,
yaşayan özel kişiler ve süren soruşturma (kırmızı çizgi şüphesi). Öteki adaylar (Cizre göçüğü, Kocaeli kaybı) 2-7 kaynak.

## §5 puan tablosu (3 aday)

| Aday | Damar | A yer | B dönüş | C kahraman | D ilk replik | E görsel | Toplam | Karar |
|---|---|---|---|---|---|---|---|---|
| **Nika İsyanı 532: Hipodrom'da toplanan kalabalık, askerler iki yandan girer; bugünkü Ayasofya bu isyandan sonra yapıldı** | 2 | 2 (Sultanahmet Meydanı = Hipodrom, serbest foto) | 2 (bir günde 30.000+ ölü, izleyicilerin çoğu bilmiyor) | 2 (adsız isyancılar) | 2 ("Ayasofya kül olmuş, imparator kaçıyormuş") | 2 (Hipodrom'un yeri + Prokopios'un 1914 sayfası, kamu malı) | **10** | Seçildi |
| Kırkpınar'ın adı: sabaha kadar güreşip ölen iki pehlivan, mezarlarından çıkan pınar | 1 | 1 (efsanenin yeri bugün Yunanistan'da, Samona; Sarayiçi yalnız temsilî) | 2 (çoğu bilmiyor) | 2 | 2 | 1 (yalnız temsilî mekân + minyatür) | 8 | Yedek; resmî kaynaklar aynı çizgi, "kırk pınar" yalnız halk anlatısı |
| Sarayburnu dibinde ayakta duran çuvallar (Sultan İbrahim rivayeti) | 1 | 2 | 2 | 2 | 2 | 1 | 9 | Elendi: rivayet Batılı tek kaynak zincirine dayanıyor; yorum testi ("oryantalist uydurma") videodan güçlü (haydarpasa-patlamasi-1917 raporunda da elenmişti) |

**Yorum testi:** "Aslında yanan Ayasofya ikinciydi, bugünkü üçüncü." Cevap: metin "dönemin Ayasofya'sı" ve "bugünkü Ayasofya
bu isyandan sonra yapıldı" der; video Ayasofya'nın kaçıncı bina olduğunu iddia etmez. İkinci olası yorum sayı (35.000 /
40.000): metinde Prokopios ve Malalas sayısı ayrı ayrı verilir.

## Son 7 tr teslimin damarı
demre-noel-baba-kemik-1087 (1, mezar) · cennet-cehennem-obrugu (1, obruk) · bodrum-mozole-1522 (1, lahit) ·
patrona-halil-1730 (2) · haydarpasa-patlamasi-1917 (2) · eskisehir-cinli-hamam (1, hamam) · alanya-adam-atacagi (1, kale)
→ bu bölüm 2. damar (isyan/katliam). Son 5 bölümün son kareleri: müze nesnesi (şişecikler), mekân fotoğrafı (kilise),
kitap sayfası (Newton & Pullan 1862), tablo (Vanmour), arşiv fotoğrafı. Bu bölüm: kitap sayfası (Loeb 1914, Prokopios);
bir önceki bölümle (müze nesnesi) aynı tür değil.

## Sahne listesi (14,0 sn; ffprobe 13,95)
1. 0,0 A (isyancı, sol), 2,5 sn: "Ayasofya kül olmuş, imparator kaçıyormuş" (kapak)
2. 2,5 B (isyancı, sağ, terli), 2,5 sn: "Çıkalım buradan, sarayda hâlâ asker var"
3. 5,0 A, 2,0 sn: "Bir şey olmaz, binlerce kişiyiz"
4. 7,0 kart, 1,5 sn: "Birkaç saat sonra"
5. 8,5 A şok yüzü (aynı kutu), 2,0 sn: "Bekle, askerler neden iki yandan giriyor?"
6. 10,5 kanıt 1, 1,5 sn: şafakta boş Sultanahmet Meydanı (Hipodrom'un yeri), ortada Dikilitaş
7. 12,0 kanıt 2 (son kare), 2,0 sn: Prokopios, Savaşlar I.xxiv, Dewing 1914, s. 237; sayfanın üstü (başlık "HISTORY OF THE WARS, I. xxiv. 50-56" + 28 tam satır, 1080x1238 dikey); 24. satır "that day more than thirty thousand." filigranın üstünde

Arka plan: Aphrodisias stadyumu (aynı türden yer; Hipodrom'un tribünleri ayakta değil). Müzik: `kanal` (Gölge): önceki tr
bölümü klasikti; konu toplu ölüm/facia. Ses −14,1 LUFS, tepe −1,5 dBTP.

## Başlık seçenekleri
1. 532'de Ayasofya'nın yandığı isyanın Hipodrom'daki sonu (54): kullanılan (tur 2 takipçi: "yakan" fazla kesin)
1b. 532'de Ayasofya'yı yakan kalabalığın Hipodrom'daki sonu (55): tur 2 başlığı
2. Ayasofya yandıktan sonra Hipodrom'da toplanan kalabalık (55): tur 1 başlığı
3. Sultanahmet Meydanı'nda 532'de ne oldu? (39)

## Lisans tablosu

| Görsel | Kaynak | Lisans | Sürüm |
|---|---|---|---|
| img/arka.jpg (arka plan) | Commons "Aphrodisias - Stadium 01.jpg", Bernard Gagnon | CC BY-SA 3.0 (ham şablon self/GFDL/cc-by-sa-3.0,2.5,2.0,1.0) | A |
| img/kanit_1.jpg | Commons "Hippodrome of Constantinople and Obelisk of Theodosius on Sultanahmet Meydanı square (8396071658).jpg", Jorge Láscar | CC BY 2.0 | A |
| img/kanit_2.jpg (son kare) | Internet Archive procopius00procgoog, Procopius, History of the Wars I-II, çev. H. B. Dewing, Loeb 1914, s. 237 | Kamu malı (ABD 1929 öncesi; IA NOT_IN_COPYRIGHT) | A |

Telifli görsel yok; `_telifli` sürümü yok. Lisans kararı bekleyen görsel yok.
Karakterler: wojakland "Peasant Wojak" ve "Medieval 2 Wojak" (kanal standardı, 27.10 kararı); düzenleme `chars/uret.py`.

## Bilinen kusurlar
- Arka plan olay yeri değil (Aphrodisias stadyumu, aynı türden yapı); `ek_maddeler`'de yazılı.
- Karakterlerin kıyafeti genel ortaçağ köylüsü (tunik, takke); B'nin yakalı tuniği telefonda modern ceket gibi okunabilir (tur 1 takipçi SHOULD). 6. yüzyıl Bizans halkına özgü hazır wojak bulunamadı.
- Son kare İngilizce kitap sayfası; Türkçesi hikâye metninde.

## Hakem turları
| Tur | Görsel | Takipçi | MUST | Uygulanan |
|---|---|---|---|---|
| 1 | 6/10 | 7/10 | Görsel 1: son kare telefonda okunmuyor (12 satır, x-yüksekliği ~7 px @390). Takipçi 3: S2 "Hipodrom'a gitme" mekânla çelişiyor; Narses cümlesi Malalas'ta yok ("ayrıldı", "altın"); ilk yorum önerisinde "39 gün" | Son kare 9 satırın sol kısmına kırpıldı (ölçek 0,58 → 0,74; "thirty thousand." satırın sonunda değil ortasında), ikili taramaya hafif kâğıt tonu (kırmızı daire eklenmedi: STIL §8 "kaynaktaki işaretler kalır", biz eklemeyiz). S2 → "Çıkalım buradan, sarayda hâlâ asker var". Narses → "Mavilerin bir kısmına para dağıttı; kalabalık bölünüp birbirine girdi". İlk yorum → "yaklaşık 5 hafta sonra, 23 Şubat 532". SHOULD: başlık, kapanış sorusu, söylenti ve Prokopios atıfları, takke kenarı yumuşatıldı, şok göz bebekleri içeri, blur 3,0 → 2,4. Uygulanmayan: S5 "iki kapıdan birden" (2,0 sn'ye sığmıyor), B'nin ceketi (bilinen kusur), arka plan değişimi |

| 2 | 7/10 | 8/10 | Görsel: tur 1 MUST kısmen kapandı, yeni MUST yok; 7'nin nedeni son karede sağ kenarda sözcük ortası kesik ve başlıksız kesit. Takipçi: 3 MUST kapandı, yeni MUST yok | Son kare sayfanın üstüne çevrildi: başlık satırı + 28 tam satır, kenar boşlukları dahil 1080x1238 (STIL §8 uzun görsel ≤ 1260); "thirty thousand." satırı filigranın üstünde; sağ kenar boşluğundaki tarama lekeleri silindi. Takkeye koyu gri parlaklık kavisi; kanıt 1 816 → 740 px. Başlık "Ayasofya'yı yakan" → "Ayasofya'nın yandığı isyanın". Uygulanmayan: arka plan değişimi, B boyu 0,52 (iki konuşmacı aynı boy kuralı), "iki yandan" (süre) |
| 3 | **8/10**, MUST 0 | **8/10**, MUST 1 | Takipçi: açıklamadaki "son satırda İngilizce 'more than thirty thousand'" cümlesi yeni son karede doğru değil (ifade 28 satırın 24.'sünde) | Cümle "sayfanın alt kısmında İngilizce 'that day more than thirty thousand' (o gün otuz binden fazla) ifadesi geçer" oldu; Instagram açıklaması 2.173/2.200 karakter. Yeniden puanlanmadı (tur sınırı) → BEKLET notu |

Puanlar hakem raporlarından değiştirilmeden aktarıldı (/tmp/hakem/{1,2,3}-{gorsel,takipci}.md).

## Kontrol (§11-§12, son paket)
check uyarısız; ffprobe 13,95 sn; kesmeler 0,5 ızgarasında; ses −14,1 LUFS, tepe −1,5 dBTP; bakis.jpg temiz (herkes içeri
bakıyor); sansür taraması: yalnız kasıtlı "k*nlı", "*ldürüldü"; özel ad bozulması yok ("Ölüm Kapısı" yerine "Nekra");
başlık son repliği söylemiyor, kapak sahne 1 (kanca); hikâye ~197 kelime, soruyla biter; ek_maddeler'de canlandırma notu,
ilk yorum önerisi, "YouTube: yükledikten sonra Kontroller adımını kontrol et".

## Adım süreleri (yaklaşık, toplam ~36 dk duvar saati)
| Adım | Süre |
|---|---|
| Ortam + hazirla.sh (1 test FAIL: test_klasik_varsa_eski_ses, aşağıda) | 2 dk |
| Okuma + gündem taraması + konu (3 aday) | 6 dk |
| Araştırma (2 alt ajan paralel: olgu, görsel) + bu arada karakter arama | 8 dk |
| Karakter düzenleme (chars/uret.py) | 4 dk |
| Görseller (gorsel.py, kanıt 1 yeniden seçildi) + yaml → render → teslim | 5 dk |
| Hakem tur 1-3 + düzeltmeler | 9 dk |
| RAPOR, teslim, commit | 2 dk |

**Alt ajan çağrıları:** Araştırmacı ×2 (olgu ~19 araç çağrısı; görsel ~15), Hakem Görsel ×1 iş parçacığı 3 tur, Hakem Takipçi
×1 iş parçacığı 3 tur. **Yaklaşık maliyet:** ~$12-16 (Opus yapımcı + Sonnet araştırmacı ×2 + Sonnet hakem 6 tur; tahmin,
ölçülmedi).

## Ortam notu
hazirla.sh: 1 test FAIL (`tests/test_muzik.py::test_klasik_varsa_eski_ses`). Neden: test, deponun gerçek bölüm geçmişini
okuyan müzik sırası denetimini çağırıyor; tr kanalının önceki bölümü (demre-noel-baba-kemik-1087) klasik olduğu için
"müzik sırası" uyarısı veriyor. Üretim kodu doğru çalışıyor (bu bölüm sırayı izledi: `kanal`); test depo durumuna bağlı.
Font, referans, klasik ses ve müzikler OK olduğu için üretime devam edildi. Aynı öneri KOD_ONERILERI'nde zaten var (14.11), yeniden eklenmedi.
