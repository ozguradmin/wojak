# Talidomit ve Türkiye (uzun video): varlıklar ve lisans tablosu

> Senaryo: `senaryo_v2.md` ("Gerekli varlıklar" §A–§E). Hazırlanma: 12.10.2026. Bu dosya her görselin kaynağını,
> yazarını, lisansını ve açıklamaya girecek atıf satırını verir; sonda senaryo sahnesi → dosya eşlemesi var.
> **Lisans kararlarını hesap sahibi verir** (CLAUDE.md, "teslim akışı" madde 2): `img/telifli/` altındakiler karar
> verilene kadar kullanılmaz; her birinin serbest yedeği hazır.

## 0. Yeniden üretme

Bütün çıktılar betikle üretilir; dosyaları elle düzenleme.

```bash
python uzun/talidomit-turkiye/chars/uret.py                 # karakterler + bakış kaydı (data/karakter_yon.json)
python uzun/talidomit-turkiye/img/cizim_uret.py             # kendi çizimlerimiz (img/cizim/), doku ve pano zeminleri
python uzun/talidomit-turkiye/img/arka_uret.py   <kaynak>   # arka plan fotoğraflarının 16:9 kırpımları
python uzun/talidomit-turkiye/img/arsiv_uret.py  <kaynak>   # arşiv kırpımları, img/telifli/, yazı kartları, kutular.json
```

`<kaynak>`: tam boy indirmelerin bulunduğu repo dışı klasör (dosya adları aşağıdaki "Kaynak dosya" sütununda).
Wikimedia'dan indirirken genel tarayıcı kimliği ve istekler arasında en az 10 sn (sık HTTP 429). Büyük dosyalarda
özgün yerine 3840 px standart küçük resim indirildi (Dorfmuseum, Büro).

- Fotoğraf kırpımları 16:9 ve en az 1920x1080 (çoğu 2560x1440: Ken Burns payı). 800 px'lik Bundesarchiv kareleri
  (Köln 1960, Doğu Berlin 1961) yalnız "masaya konmuş fotoğraf" (`foto`) çerçevesinde, küçük boyda kullanılır.
- `img/kutular.json`: fosforlu kalem kutuları (piksel; `manset.kutular` için), dosya → {vurgulanan metin: [x0, y0, x1, y1]}.
- Fotoğraflarda renk düzeltmesi yapılmadı (motorun `doygunluk`/`karart` ayarı); atıflarda "kırpıldı" yeterli.

## 1. Karakterler (`chars/`)

Hepsi düz MS-Paint wojak, 3/4 profilde **sağa** bakar (her PNG'ye bakıldı, `data/karakter_yon.json`'a `sag` olarak
kayıtlı; motor sağdaki karakteri aynalar). Bir karakterin bütün yüz varyantları aynı tuvalde (yüz değişiminde kutu
zıplamaz). Önerilen `boy`: klasik kafalılar (K, L, S, E, müşteri) ~0,62; Kelsey ve anne adayı ~0,72 (yüzleri daha küçük).

| Dosya | Kim / duygu | Taban (kaynak) | Lisans durumu |
|---|---|---|---|
| `kaymakcalan_sakin.png`, `_dusunceli.png`, `_ciddi.png`, `_kollar.png` | K, Şükrü Kaymakçalan rolü (30'ların ortası, siyah saç, kemik gözlük, önlük, bordo kravat; fotoğrafına benzetilmedi). `_kollar` = ciddi yüz + kavuşturulmuş kollar (K2 küçük resmi) | klasik kafa `assets/kit/klasik/sakin.png` + bu betikte çizilen saç, gözlük, önlük, yüz ifadeleri | klasik taban: wojakparadise arşivi (HF clayshoaf/Wojaks 5_Tired_Wojak/10441), kanalın bütün bölümlerinde kullanılan taban; ekler kendi çizimimiz |
| `lenz_sakin.png`, `_fark.png`, `_ciddi.png`, `_telefon.png`, `_gazete.png` | L, Widukind Lenz rolü (kahverengi saç, ince yuvarlak gözlük, önlük, stetoskop). `_telefon` = ciddi + 1960'lar ahizesi; `_gazete` = ciddi + adsız gazete | klasik kafa + kendi çizimimiz | aynı |
| `sheskin_sakin.png`, `_saskin.png` | S, Jacob Sheskin rolü (kır, yüksek alın, gözlüksüz, önlük) | klasik kafa + kendi çizimimiz | aynı |
| `eczaci_sakin.png` | E, 1950'ler eczacısı (kır-kahve saç, geniş sarkık bıyık, papyon). Yalnız sakin (senaryo) | klasik kafa + kendi çizimimiz | aynı |
| `kelsey_sakin.png`, `_supheci.png` | F, Frances O. Kelsey rolü (koyu kahve kabarık saç, lacivert ceket, bluz). **Gözlüksüz**: 1960-62 fotoğraflarında gözlük yok | HF clayshoaf/Wojaks `5_Daddys_Girl/11087` "Secretary Daddy's Girl" (`kaynak/kelsey_kaynak_secretary.png`); saç/ceket yeniden boyandı, ağız ve kaşlar düzenlendi | wojakparadise arşivi (yükleyenin malı, açık izin yok); kanal pratiği: karakter olarak kullanılır, kaynak yazılır |
| `anne_adayi_sakin.png` | 1950'ler anne adayı, yalnız sakin yüz (senaryo) | wojakland "Trad Wife" https://wojakland.com/wp-content/grand-media/image/original/trad_wife.png (`kaynak/anne_kaynak_tradwife.png`), değiştirilmedi | wojakland'de kullanım şartı yok (topluluk memesi) |
| `temsilci2000_sakin.png` | A2, 2000'ler adsız temsilci (şapkasız, siyah saç, gri takım) | wojakland "Grey Suit Wojak" https://wojakland.com/wp-content/grand-media/image/original/grey_suit_wojak.png (`kaynak/temsilci2000_kaynak_greysuit.png`) | aynı |
| `temsilci_notr.png` | A temsilci, gülümsemesi silinmiş nötr yüz (B5.3; kötü/sırıtan yüz yok) | `episodes/talidomit-turkiye/chars/temsilci_gulumsuyor.png` (wojakland "1950s Businessman Wojak"), aynı tuval 1243x1400 | aynı |
| *(yeniden kullanılan)* `episodes/talidomit-turkiye/chars/temsilci_gulumsuyor.png`, `temsilci_gergin.png`, `veteriner.png`; `assets/kit/klasik/sakin.png` (müşteri) | A, B, müşteri | kısa video | kısa videonun kaydı |

## 2. Arka planlar (`img/arka_*`, `img/doku_*`)

| Dosya | Ne | Kaynak dosya / sayfa | Yazar | Lisans | Atıf satırı (açıklamaya) |
|---|---|---|---|---|---|
| `arka_lille_lab_169.jpg` (2560x1440) | Eski bakteriyoloji laboratuvarı (masa, daktilo, küre, laboratuvar masası). Sağdaki prizler kırpımın dışında, masa altındaki priz yamalandı | `lille_calmette_guerin_lab.jpg` · https://commons.wikimedia.org/wiki/File:Lille_Mus%C3%A9e_de_l%27Institut_Louis_Pasteur_Labo_Calmette-Guerin.JPG | Pierre André Leclercq | CC BY-SA 4.0 | Laboratuvar: Pierre André Leclercq / Wikimedia Commons, CC BY-SA 4.0 (kırpıldı, rötuşlandı) |
| `arka_lille_masa_169.jpg` (1920x1080) | Aynı odanın laboratuvar masası yakın kırpımı (B5.7 yumurta tablası için) | aynı | aynı | aynı | aynı satır |
| `arka_lille_yazihane_169.jpg` | Aynı odanın yazı masası kırpımı (yedek) | aynı | aynı | aynı | aynı satır |
| `arka_eczane_169.jpg`, `arka_eczane_raflar_169.jpg` | Eski eczane odası (kırmızı raflar, çekmeceler, terazi). Kapı yanındaki modern prizler yamalandı. **Yer etiketi yok** | `arppeanum_eczane_cc0.jpg` · https://commons.wikimedia.org/wiki/File:Apothecary_room_-_Arppeanum_-_DSC05136.JPG | Daderot | CC0 1.0 | (atıf gerekmez) Eczane: Daderot / Wikimedia Commons, CC0 |
| `arka_muayenehane_169.jpg` | 1950'ler-60'lar köy hekimi muayenehanesi (göz tabloları, alet dolabı, muayene sedirinin kenarı). **Yer etiketi yok** | `arztpraxis_dorfmuseum_moenchhof_ccby3.jpg` · https://commons.wikimedia.org/wiki/File:Dorfmuseum_M%C3%B6nchhof,_Arztpraxis.jpg | Dguendel | CC BY 3.0 | Muayenehane: Dguendel / Wikimedia Commons, CC BY 3.0 (kırpıldı) |
| `arka_ofis_169.jpg` | 1950'ler-60'lar bürosu (yeşil çuhalı masa, daktilolar, santral, raf). **Yer etiketi yok** | `buero_arbeitsplatz_cc0.jpg` · https://commons.wikimedia.org/wiki/File:B%C3%BCro-Arbeitsplatz_im_Werk.JPG | Wolf1949H | CC0 1.0 | (atıf gerekmez) Büro: Wolf1949H / Wikimedia Commons, CC0 |
| `arka_hastane_odasi_cizim.jpg` | 1960'lar hastane odası, sağda boş yatak kenarı (hasta yok). Serbest ve hastasız bir fotoğraf bulunamadı (adaylarda balmumu hastalar vardı) | kendi düz çizimimiz (`img/cizim_uret.py`) | tarihselwojak | kendi | — |
| `arka_mantar_pano.jpg` | Soruşturma panosu zemini (mantar + ahşap çerçeve) | kendi dokumuz | tarihselwojak | kendi | — |
| `doku_kagit.jpg`, `doku_kagit_koyu.jpg` | Açık ve koyu kâğıt dokusu (metin, kontrol listesi, nokta ızgarası zemini) | kendi dokumuz | tarihselwojak | kendi | — |

## 3. Arşiv görselleri, serbest (`img/foto_*`)

| Dosya | Ne | Kaynak dosya / sayfa | Yazar | Lisans | Atıf satırı |
|---|---|---|---|---|---|
| `foto_contergan_teneke.jpg`, `foto_contergan_teneke_169.jpg` | Contergan tenekesi (24 tablet) | `contergan_teneke_oesterreich_ccbysa3.jpg` · https://commons.wikimedia.org/wiki/File:Contergan_package.jpg | Kai Oesterreich (User:Codc) | CC BY-SA 3.0 | Contergan tenekesi: Kai Oesterreich / Wikimedia Commons, CC BY-SA 3.0 |
| `foto_contergan_forte.jpg` | Contergan forte kutusu (vitrin yansıması kırpıldı) | `contergan_forte_kutu_tobitoaster_ccbysa4.jpg` · https://commons.wikimedia.org/wiki/File:Contergan-Verpackung.jpg | TobiToaster | CC BY-SA 4.0 | Contergan forte kutusu: TobiToaster / Wikimedia Commons, CC BY-SA 4.0 |
| `foto_kupferhof_grunenthal_169.jpg` | Kupferhof Grünenthal avlusu, Stolberg (firmanın kurulduğu bina) | `kupferhof_grunenthal_stolberg_ccby3.jpg` · https://commons.wikimedia.org/wiki/File:Kupferhof_Gr%C3%BCnenthal,_Stolberg,_Totale.JPG | ArthurMcGill | CC BY 3.0 | Kupferhof Grünenthal, Stolberg: ArthurMcGill / Wikimedia Commons, CC BY 3.0 |
| `foto_stolberg_grunenthal_169.jpg` | Stolberg'deki Grünenthal binası (2006) | `stolberg_grunenthal_merkez_2006_ccbysa3.jpg` · https://commons.wikimedia.org/wiki/File:Stolberg_Gr%C3%BCnenthal.jpg | Norbert Schnitzler | CC BY-SA 3.0 | Grünenthal binası, Stolberg: Norbert Schnitzler / Wikimedia Commons, CC BY-SA 3.0 |
| `foto_giessen_1957_169.jpg` | Gießen pazar yeri, 1957, renkli | `giessen_marktplatz_1957_ccbysa4.jpg` · https://commons.wikimedia.org/wiki/File:Gie%C3%9Fen-1957-Marktplatz.gif | Manfred & Barbara Aulbach | CC BY-SA 4.0 | Gießen, 1957: Manfred & Barbara Aulbach / Wikimedia Commons, CC BY-SA 4.0 |
| `foto_koln_1960.jpg` (800x768) | Köln alışveriş caddesi, 2.6.1960 | `koln_alisveris_caddesi_1960_bundesarchiv_ccbysa3de.jpg` · https://commons.wikimedia.org/wiki/File:Bundesarchiv_B_145_Bild-F008275-0003,_K%C3%B6ln,_Einkaufsstra%C3%9Fe.jpg | Rolf Unterberg / Bundesarchiv | CC BY-SA 3.0 DE | Köln 1960: Bundesarchiv, B 145 Bild-F008275-0003 / Unterberg / CC BY-SA 3.0 DE |
| `foto_dogu_berlin_kacak_ilac_1961.jpg` (800x574) | Doğu Berlin gümrük sergisi, Noel kolilerinde kaçak ilaç (CONTERGAN kutusu), 19.12.1961. Alttaki arşiv künye şeridi kırpıldı | `ddr_ilac_kacakciligi_1961_0002_contergan_bundesarchiv_ccbysa3de.jpg` · https://commons.wikimedia.org/wiki/File:Bundesarchiv_Bild_183-89187-0002,_Medikamentenschmuggel_in_Weihnachtssendungen.jpg | Christa Hochneder / Bundesarchiv | CC BY-SA 3.0 DE | Doğu Berlin 1961: Bundesarchiv, Bild 183-89187-0002 / Hochneder / CC BY-SA 3.0 DE |
| `foto_protez_kollar.jpg` | Yapay kollar (Roehampton, 1961-65), kişi yok | `protez_kollar_roehampton_sciencemuseum_ccbysa2.jpg` · https://commons.wikimedia.org/wiki/File:Artificial_limbs_for_a_thalidomide_child,_1961-1965._(9660575567).jpg | Science Museum London / SSPL | CC BY-SA 2.0 | Yapay kollar: Science Museum London / Science & Society Picture Library, CC BY-SA 2.0 |
| `foto_kelsey_masa.jpg` | Frances O. Kelsey FDA'da masasında, dosya yığınları | `kelsey_portre_1960lar_pd.jpg` · https://commons.wikimedia.org/wiki/File:Frances_O._Kelsey_(FDA_171)_(8211251003).jpg | U.S. FDA | Kamu malı (PD-USGov) | Frances Kelsey: U.S. FDA / Wikimedia Commons (kamu malı) |
| `foto_kelsey_kennedy_1962.jpg` | Kennedy, Kelsey'ye ödül veriyor, 7.8.1962 | `kelsey_jfk_1962_pd.jpg` · https://commons.wikimedia.org/wiki/File:Frances_Oldham_Kelsey_and_John_F._Kennedy.jpg | Beyaz Saray | Kamu malı | Kennedy ve Kelsey, 1962: Beyaz Saray / Wikimedia Commons (kamu malı) |
| `foto_kennedy_imza_1962.jpg` | 1962 ilaç yasasının imzası, 10.10.1962 | `jfk_imza_1962_ilac_yasasi_pd.jpg` · https://commons.wikimedia.org/wiki/File:President_Signing_the_1962_Drug_Amendments.jpg | Abbie Rowe (NPS) | Kamu malı | 1962 ilaç yasası imzası: Abbie Rowe, Beyaz Saray / Wikimedia Commons (kamu malı) |
| `foto_ankara_panorama_tam.jpg` (5528x906) | Kaleden Ankara panoraması (yatay kaydırma için tam boy; kenar boşluğu kırpıldı) | `ankara_kaleden_panorama_salt_kisitsiz.jpg` · https://commons.wikimedia.org/wiki/File:A_Panoramic_View_of_Ankara_from_Ankara_Castle_(12984588473).jpg | SALT Araştırma | Bilinen telif kısıtlaması yok | Ankara kartpostalları ve panorama: SALT Araştırma / Wikimedia Commons (bilinen telif kısıtlaması yok) |
| `foto_ankara_bankalar_caddesi.jpg` | Ulus, Bankalar Caddesi kartpostalı (tek). **Yıl yazılmaz** | `ankara_bankalar_caddesi_salt_kisitsiz.jpg` · https://commons.wikimedia.org/wiki/File:Bankalar_Street,_Ankara_(13080311644).jpg | SALT Araştırma | aynı | aynı satır |
| `foto_ankara_bankalar_kartpostal_ust.jpg` | İkili kartpostalın **üst** yarısı: "BANKALAR CADDESİ" | `ankara_sergievi_bankalar_salt_kisitsiz.jpg` · https://commons.wikimedia.org/wiki/File:Ankara_Sergi_Evi_and_Bankalar_Street,_Ankara_(14669857295).jpg | SALT Araştırma | aynı | aynı satır |
| `foto_ankara_sergievi_kartpostal_alt.jpg` | İkili kartpostalın **alt** yarısı: "Sergi evi ve Bankalar C." | aynı | SALT Araştırma | aynı | aynı satır |
| `foto_saglik_bakanligi.jpg` | Sıhhiye'deki Sağlık Bakanlığı binası (2014; alttaki araçlar kırpıldı). Etiket "(BUGÜN)" | `saglik_bakanligi_bina_2014_ccbysa3.jpg` · https://commons.wikimedia.org/wiki/File:Sa%C4%9Fl%C4%B1k_Bakanl%C4%B1%C4%9F%C4%B1.JPG | Vikiçizer | CC BY-SA 3.0 | Sağlık Bakanlığı binası, Sıhhiye: Vikiçizer / Wikimedia Commons, CC BY-SA 3.0 |
| `foto_tavuk_embriyosu.jpg` | Işıkla bakılan 11 günlük döllü yumurta. Etiket "TEMSİLÎ GÖRSEL" şart | `tavuk_embriyosu_11gun_cdc_pd.jpg` · https://commons.wikimedia.org/wiki/File:CDC_PHIL_10149_%E2%80%93_fertilized_egg,_11_days_old.jpg | CDC / Dr. Joseph McDade | Kamu malı | Tavuk embriyosu: CDC PHIL 10149 (kamu malı) |
| `foto_brezilya_kutu.jpg`, `foto_brezilya_piktogram.jpg` (540x540) | Brezilya'da bugünkü talidomit kutusu (2009) ve kutudaki uyarı piktogramının kırpımı | `brezilya_talidomid_kutusu_2009_ccbysa4.jpg` · https://commons.wikimedia.org/wiki/File:Talidomida.jpg | Gadogado123 | CC BY-SA 4.0 | Brezilya'daki talidomit kutusu: Gadogado123 / Wikimedia Commons, CC BY-SA 4.0 |
| `talidomit_molekul_pd.png` (+ `cizim/molekul_beyaz.png`, `molekul_siyah.png`) | Talidomit yapı formülü | `talidomit_molekul_pd_beyaz.png` · https://commons.wikimedia.org/wiki/File:Thalidomide_structure.svg | Aethyta | Kamu malı | Talidomit formülü: Wikimedia Commons (kamu malı) |

## 4. Telifli / izin bekleyen (`img/telifli/`, git'e girmez)

| Dosya | Ne | Kaynak | Hak sahibi | Durum | Yedek (serbest) |
|---|---|---|---|---|---|
| `kevadon_1960_fda.jpg` | Kevadon şişesi, "investigational use" (B4.5, B5.4) | https://commons.wikimedia.org/wiki/File:Kevadon_(thalidomide),_1960.jpg | U.S. FDA (EXIF'te fotoğrafçı Cade Martin) | Commons'ta PD-USGov, EXIF'te "All Rights Reserved": **hesap sahibi kararı**. Kullanılırsa atıf: "Kevadon şişesi: U.S. FDA / Wikimedia Commons" | `cizim/doz_sisesi.png` (adsız şişe) |
| `distaval_reklam_wellcome.jpg` (797x1024) | Distaval broşürü: "Safe Sedation 'DISTAVAL' … no known toxicity and free from untoward side-effects" | https://wellcomecollection.org/works/atrvxkxg | The Distillers Company (Biochemicals) Ltd / Wellcome Collection | In copyright: **hesap sahibi kararı** | `cizim/distaval_yedek_kart.jpg` (senaryodaki İngilizce cümle daktiloyla) |
| `tfd_bulten26_1994_kapak.jpg`, `tfd_bulten26_1994_s2.jpg` | TFD Bülteni 26 (Temmuz 1994): kapak ve Kayaalp'in anma yazısı (s. 2). Kutular: başlık + "Sağlık Bakanlığına başta İlaç ve Eczacılık Genel Müdürlüğü olmak üzere danışman ve yol gösterici olarak yaptığı katkıdır" | http://www.tfd.org.tr/sites/default/files/Klasor/Dosyalar/ebultenler/26_1994.pdf | Türk Farmakoloji Derneği | telifli: **hesap sahibi kararı** (atıf: "TFD Bülteni 26 sayfası: Türk Farmakoloji Derneği") | `cizim/bulten_karti_yedek.png` |
| `tfd_bulten114_2012_kirpim.png` | TFD E-Bülteni 114 (2012) Kaymakçalan paragrafı (demo'daki kırpım; B5.8 pano kartı için isteğe bağlı) | http://www.tfd.org.tr/sites/default/files/Klasor/Dosyalar/ebultenler/114_2012_4_0.pdf | Türk Farmakoloji Derneği | telifli: **hesap sahibi kararı** | pano kartı yazısı |
| `kub_bolum44_kesit.png`, `kub_bolum44_kesit_gri.png` | THALIDOMIDE CELGENE KÜB s. 5, bölüm 4.4 kesiti; `_gri`: atlanan "veya … gebe kalabilecek kadınlar" kısmı soluk | https://titck.gov.tr/storage/kubKtAttachments/eaz5rIWQcA6im.pdf | TİTCK / ruhsat sahibi | Kamu belgesi: **hesap sahibi onayı** (atıf: "Kısa Ürün Bilgisi: TİTCK") | `cizim/kub_bolum44_yedek_kart.jpg` |
| `kub_ilk_ruhsat_2004.png` | Aynı KÜB s. 21 §9: "İlk ruhsat tarihi: 31/05/2004" | aynı | aynı | aynı | takvim yaprağı `cizim/takvim_31_mayis_2004.png` |

## 5. Kendi çizimlerimiz (`img/cizim/`, `cizim_uret.py`)

Gerçek firma/gazete/dergi adı ya da logosu yok; kişi, bebek, hasta yok. Hepsi tarihselwojak'ın kendi çizimi.

| Dosya | Ne | Sahne |
|---|---|---|
| `numune_kutusu.png`, `numune_kutusu_tabletler.png`, `tablet.png` | Adsız beyaz numune/ilaç kutusu (yalnız mavi şerit), tabletler, tek tablet | SA.6, B1.1, B3.11, B5.2, B6.1, B6.4, K1 |
| `fare_kafesi.png`, `doz_sisesi.png` | Fare kafesi (3 gri fare), adsız kahverengi doz şişesi (Kevadon yedeği de bu) | B1.4, B4.5, B5.4 |
| `molekul_beyaz.png`, `molekul_siyah.png`, `cereblon.png`, `sall4.png`, `sall4_kirik.png` | Formülün saydam hâlleri; cereblon simgesi (cepli mor kütle); SALL4 bloğu sağlam/kırık | B1.3, B5.13, B6.4 |
| `kapi_acik.png`, `kapi_kapali.png` | Kapı (açık, karanlık boşluk / kapalı) | B5.4 |
| `gazete_1961_canlandirma.png` | Adsız, logosuz "pazar gazetesi" (canlandırma): tarih satırı "SONNTAG, 26. NOVEMBER 1961", manşet "CONTERGAN?", okunmaz sütunlar. Kutu: `CONTERGAN` | B3.7 |
| `bulten_karti_yedek.png` | TFD 1994 sayfası yerine bilgi kartı ("bilgi kartı · kendi çizimimiz") | B5.8 |
| `yumurta_tablasi.png` | Kuluçka yumurtası tablası | B5.7 |
| `dosya_bos_acik.png`, `dosya_kapali.png`, `dosya_k3_etiketli.png`, `dosya_ruhsat_basvurusu.png`, `dosya_kevadon.png`, `dosya_sinir_hasari_1961.png` | Manila dosyalar: açık ve BOMBOŞ; kapalı; "TALİDOMİT / RUHSAT BAŞVURUSU / ANKARA 19??"; kalın "RUHSAT BAŞVURUSU"; "KEVADON"; "SİNİR HASARI RAPORLARI · 1961" | SA.3, K3, B6.6, B4.2, B4.4 |
| `makale_behcet_1998_cizim.png` | Hamuryudan ve ark. 1998 ilk sayfasının çizimi (gerçek başlık ve yazarlar, dergi adı/logosu yok) | B6.5 |
| `eczane_raf_dolu.png`, `eczane_raf_turkiye_bos.png` | Düz çizim eczane rafı + tezgâh; ikincisinde ortadaki kutunun yeri boş (sarı çerçeve) | B1.8 (yedek), B2.4 "TÜRKİYE" tezgâhı |
| `takvim_*.png` (10) | Koparılan takvim yaprakları: ARALIK 1956, 1 EKİM 1957, EYLÜL 1960, 30 EKİM 1961 (gri), 15/16/20/26/27 KASIM 1961, 31 MAYIS 2004 | B1.1, B1.6, B3.4–B3.8, B4.2, B6.6 |
| `telefon_simge.png`, `zarf.png`, `zarf_taahhutlu.png` | Çevirmeli telefon; zarf; "TAAHHÜTLÜ" damgalı zarf | B3.5 |
| `raptiye.png`, `buyutec.png` | Kırmızı raptiye, büyüteç | B1.7, B5.8, K3 |
| `telefon_cerceve.png` | Akıllı telefon çerçevesi, ekran saydam (70,150)-(630,1290) | B5.11 viral iddia kartı |
| `hap_simge.png` | Harita için beyaz tablet simgesi | SA.1, B2.1 |
| `gebelik_yasak_piktogram.png` | Yandan hamile kadın silüeti + yasak çemberi (genel simge) | K1 (isteğe bağlı) |
| `distaval_yedek_kart.jpg` | Kâğıt dokulu kart: "Distaval can be given with complete safety / to pregnant women and nursing mothers / without adverse effect on mother or child." + "İngiltere'deki Distaval reklamından (1958-61)". Kutular: `complete safety`, `pregnant women and nursing mothers` | B2.3 (varsayılan) |
| `kub_bolum44_yedek_kart.jpg` | KÜB 4.4 cümlesi, atlanan kısım gri. Kutular: `gebe kadınlar`, `kesinlikle kullanılmamalıdır.` | B6.7 (yedek) |

## 6. Senaryo sahnesi → dosya

Yollar `uzun/talidomit-turkiye/` köküne göre (`chars/...`, `img/...`); `ep/` = `episodes/talidomit-turkiye/chars/`.
Harita, sayaç, nokta ızgarası, zaman çizelgesi, bölüm kartı, metin kartları motorun kendi sahneleridir (görsel dosyası yok).

| Sahne | Dosya(lar) |
|---|---|
| SA.1–SA.2 | harita + `img/cizim/hap_simge.png` |
| SA.3 | `img/foto_ankara_panorama_tam.jpg` (panoramanın 1. kullanımı) · `img/cizim/dosya_kapali.png` → `dosya_bos_acik.png` |
| SA.4 | `img/foto_contergan_teneke.jpg` |
| SA.5, B6.7 sol | metin; arka `img/foto_contergan_teneke_169.jpg` (bulanık) |
| SA.6–SA.7 | `img/arka_lille_lab_169.jpg` · `ep/temsilci_gulumsuyor.png` → `ep/temsilci_gergin.png` · `img/cizim/numune_kutusu.png` |
| B1.1–B1.2 | `img/cizim/takvim_aralik_1956.png` · arka `img/foto_kupferhof_grunenthal_169.jpg` (bulanık) · `img/cizim/numune_kutusu_tabletler.png` |
| B1.3 | `img/foto_kupferhof_grunenthal_169.jpg` · `img/cizim/molekul_siyah.png` (ya da `_beyaz`) |
| B1.4 | `img/cizim/fare_kafesi.png`, `doz_sisesi.png` · `img/doku_kagit.jpg` |
| B1.5 | metin/kontrol listesi, `img/doku_kagit.jpg` |
| B1.6 | `img/foto_giessen_1957_169.jpg` + `img/foto_contergan_forte.jpg` · `img/cizim/takvim_1_ekim_1957.png` |
| B1.7 | bölünmüş ekran: `img/foto_giessen_1957_169.jpg` \| `img/foto_ankara_bankalar_kartpostal_ust.jpg` · `img/cizim/raptiye.png` |
| B1.8 | `img/arka_eczane_169.jpg` · `chars/eczaci_sakin.png` (sağ) · `assets/kit/klasik/sakin.png` (müşteri, sol) |
| B1.9, B2.2 | `img/foto_koln_1960.jpg` (foto çerçevesi; B2.2'de bulanık arka) |
| B2.3 | varsayılan `img/cizim/distaval_yedek_kart.jpg` (kutular hazır) · hesap sahibi onaylarsa ek kesme `img/telifli/distaval_reklam_wellcome.jpg` (kutular: "Safe Sedation", "no known toxicity") |
| B2.4 | `img/arka_eczane_raflar_169.jpg` · `chars/eczaci_sakin.png` + `chars/anne_adayi_sakin.png` · "TÜRKİYE" tezgâhı `img/cizim/eczane_raf_turkiye_bos.png` |
| B2.5 | zaman çizelgesi, `img/doku_kagit.jpg` |
| B2.6–B2.7 | `img/foto_contergan_teneke_169.jpg` (kararan) |
| B3.3 | `img/arka_muayenehane_169.jpg` · `chars/lenz_sakin.png` → `lenz_fark.png` |
| B3.4 | takvim akışı: `img/cizim/takvim_30_ekim_1961.png` (gri) … · arka muayenehane bulanık |
| B3.5 | `chars/lenz_telefon.png` · `img/cizim/takvim_15_kasim_1961.png`, `takvim_16_kasim_1961.png`, `telefon_simge.png`, `zarf_taahhutlu.png` |
| B3.6 | `img/cizim/takvim_20_kasim_1961.png` |
| B3.7 | `chars/lenz_gazete.png` → manşet `img/cizim/gazete_1961_canlandirma.png` (kutu `CONTERGAN`) · `takvim_26_kasim_1961.png` |
| B3.8 | `img/cizim/takvim_27_kasim_1961.png` |
| B3.9–B3.10 | nokta ızgarası, `img/doku_kagit_koyu.jpg` |
| B3.11 | `img/doku_kagit.jpg` + `img/cizim/tablet.png` |
| B3.12–B3.13 | `img/foto_protez_kollar.jpg` |
| B3.14 | `img/foto_stolberg_grunenthal_169.jpg` |
| B4.1, B4.8 | `img/foto_kelsey_masa.jpg` (B4.8'de → `img/foto_ankara_panorama_tam.jpg`, panoramanın 2. kullanımı) |
| B4.2–B4.4 | `img/arka_ofis_169.jpg` · `chars/kelsey_sakin.png` → `kelsey_supheci.png` · `img/cizim/dosya_kevadon.png`, `dosya_sinir_hasari_1961.png`, `takvim_eylul_1960.png` |
| B4.5 | `img/telifli/kevadon_1960_fda.jpg` (karar) ya da `img/cizim/doz_sisesi.png` |
| B4.7, KP.2 sol | `img/foto_kelsey_kennedy_1962.jpg` · ara kesme `img/foto_kennedy_imza_1962.jpg` |
| B4.9 | metin, panorama silüeti üstünde |
| B5.1 | `img/foto_ankara_bankalar_caddesi.jpg` |
| B5.2–B5.6, B5.12 | `img/arka_lille_lab_169.jpg` · `ep/temsilci_gulumsuyor.png` → `chars/temsilci_notr.png`; B5.6 `ep/temsilci_gergin.png` · `chars/kaymakcalan_sakin.png` → `_dusunceli.png` → `_ciddi.png` · `img/cizim/numune_kutusu.png` |
| B5.4 | bölünmüş ekran: sol `doz_sisesi.png`/Kevadon \| sağ `img/foto_saglik_bakanligi.jpg` · `img/cizim/kapi_acik.png` → `kapi_kapali.png` |
| B5.7 | `img/arka_lille_masa_169.jpg` + `img/cizim/yumurta_tablasi.png` · `ep/veteriner.png` (Kaymakçalan bu karede YOK) |
| B5.8, KP.2 sağ, KP.3 | `img/arka_mantar_pano.jpg` · `img/cizim/raptiye.png`, `buyutec.png` · `img/telifli/tfd_bulten26_1994_s2.jpg` (karar; kutular hazır) ya da `img/cizim/bulten_karti_yedek.png` · `img/foto_tavuk_embriyosu.jpg` ("TEMSİLÎ GÖRSEL") |
| B5.9 | `img/foto_dogu_berlin_kacak_ilac_1961.jpg` (küçük foto) |
| B5.11 | `img/cizim/telefon_cerceve.png` |
| B5.13 | `img/cizim/molekul_beyaz.png` (karanlık karede) |
| B6.1 | `img/arka_hastane_odasi_cizim.jpg` · `chars/sheskin_sakin.png` → `sheskin_saskin.png` (sol) · `img/cizim/numune_kutusu.png` (eski adsız kutu) |
| B6.3 | `img/foto_brezilya_kutu.jpg` → `img/foto_brezilya_piktogram.jpg` |
| B6.4 | `img/cizim/tablet.png` → `molekul_beyaz.png`, `cereblon.png`, `sall4.png` → `sall4_kirik.png` |
| B6.5 | `img/doku_kagit.jpg` + `img/cizim/makale_behcet_1998_cizim.png` |
| B6.6 | `img/cizim/takvim_31_mayis_2004.png` · `img/arka_lille_lab_169.jpg` + `chars/temsilci2000_sakin.png` + `img/cizim/dosya_ruhsat_basvurusu.png` |
| B6.7 sağ | `img/telifli/kub_bolum44_kesit_gri.png` + `kub_ilk_ruhsat_2004.png` (onay) ya da `img/cizim/kub_bolum44_yedek_kart.jpg` |
| KP.1 | `img/foto_ankara_sergievi_kartpostal_alt.jpg` |
| KP.3 | iki ayrı kare: `img/arka_lille_lab_169.jpg` + `chars/kaymakcalan_sakin.png`; `img/arka_lille_masa_169.jpg` + `ep/veteriner.png` |
| KP.4 | `img/foto_contergan_teneke_169.jpg` (bulanık) |
| K1 / K2 / K3 | K1: `ep/temsilci_gergin.png` + `img/cizim/numune_kutusu.png` (+ `gebelik_yasak_piktogram.png`) · K2: `chars/kaymakcalan_kollar.png` + `img/cizim/hap_simge.png` · K3: `img/cizim/dosya_k3_etiketli.png` / `dosya_bos_acik.png` + `buyutec.png` + `ep/temsilci_gulumsuyor.png`. Küçük resimde CC BY-SA fotoğraf yok (senaryo kuralı) |

## 7. Senaryoya düzeltme notları (varlık hazırlanırken çıkanlar)

1. **B2.3 Distaval:** Wellcome'daki görsel bir broşür ("Safe Sedation … no known toxicity and free from untoward
   side-effects"); senaryonun vurgulattığı "complete safety … pregnant women and nursing mothers" cümlesi **bu görselde
   yok**. O cümlenin fosforlu kalemi yalnız kendi kartımızda (`cizim/distaval_yedek_kart.jpg`) olabilir. Wellcome
   görseli onaylanırsa "no known toxicity" vurgusuyla ayrı bir kesme olarak kullanılabilir.
2. **İkili SALT kartpostalı ters:** ÜST yarı Bankalar Caddesi, ALT yarı Sergi Evi ve Bankalar Caddesi. B1.7 →
   `foto_ankara_bankalar_kartpostal_ust.jpg`, KP.1 → `foto_ankara_sergievi_kartpostal_alt.jpg`.
3. **B6.3 Brezilya piktogramı:** kutudaki işaret çarpılı bir **kadın başı** (eli ağız hizasında), yanında
   "Proibido para mulheres em idade de ter filhos" ve "Não deixe que isto aconteça na sua família". "Hamile kadın
   piktogramı" diye etiketlenmemeli. Kırpım 540 px: ekranı doldururken yumuşak görünür (kısa tutulmalı).
4. **B6.1 hastane odası:** serbest ve hastasız bir dönem fotoğrafı bulunamadı (adaylarda balmumu hastalar ya da
   kalabalık müze salonu vardı); düz çizim arka plan hazırlandı.
5. **B4.2 / B3.3 yer:** büro ve muayenehane fotoğrafları FDA ya da Hamburg değil (fabrika müzesi, Avusturya köy
   müzesi); yer etiketi konmaz.
6. **Kelsey gözlüksüz** çizildi (1960-62 fotoğraflarıyla tutarlı).

## 8. Açıklamaya eklenecek görsel atıfları (senaryodaki "GÖRSELLER" listesine ek)

- Eczane: Daderot / Wikimedia Commons, CC0
- Muayenehane: Dguendel / Wikimedia Commons, CC BY 3.0
- Büro: Wolf1949H / Wikimedia Commons, CC0
- Senaryo listesindekiler değişmedi (Lille laboratuvarı, teneke, forte, Kupferhof, Stolberg, Gießen, Köln, Doğu Berlin,
  yapay kollar, Sağlık Bakanlığı, Brezilya kutusu, SALT, kamu malı görseller). Hesap sahibi `img/telifli/` altındakileri
  kullanırsa §4'teki atıflar eklenir.
- Karakterler: klasik wojak tabanı ve wojakland çizimleri üzerine tarihselwojak düzenlemesi; kendi çizimlerimiz ve
  haritalar tarihselwojak.
