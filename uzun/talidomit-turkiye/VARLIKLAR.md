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
| `anlatici_sakin.png`, `_dusunceli`, `_ciddi`, `_fark`, `_saskin`, `_terli`, `_gozyasli` | 4. tur: anlatıcı/izleyici (bilgi sahnelerinde köşeden tepki veren "feels guy"): saçsız klasik kafa + hardal bisiklet yaka kazak. Yüzler aynı tuvalde | klasik kafa `assets/kit/klasik/sakin.png` (terli, gozyasli: `assets/kit/klasik/`) + bu betikte çizilen kazak ve yüzler | klasik taban (kanalın tabanı); ekler kendi çizimimiz |
| `voss_sakin.png`, `voss_ciddi.png` | 4. tur: Ralf Voss rolü (1959'da firmayı uyaran nörolog): kumral-sarı yandan ayrılmış saç, gözlüksüz, beyaz önlük + açık gri gömlek + lacivert kravat; fotoğrafına benzetilmedi | klasik kafa + kendi çizimimiz | klasik taban; ekler kendi çizimimiz |
| `kelsey_kararli.png` | 4. tur: Kelsey'nin kararlı yüzü ("Onay da vermiyor."): iki kaş alçak, düz dudak | `kelsey_sakin` + kaşlar | Kelsey satırındaki gibi |
| `temsilci2000_gergin.png` | 5. tur: 2000'ler temsilcisinin terli yüzü (SA.6, kapı vuruşunda) | `temsilci2000_sakin` + ter damlaları (`tools/kit_varyant.py` `make()`, damlalar (700,178), (748,262), (402,262), (560,140)); bakış `sag` kayıtlı | temsilci2000 satırındaki gibi |
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
| `arka_koridor_cizim.jpg`, `arka_bakanlik_oda_cizim.jpg`, `arka_eczane_cizim.jpg`, `arka_buro_cizim.jpg` | 4. tur: bakanlık koridoru (SA.6, B6.6), 1950'ler bakanlık odası (B5.2, B5.3c), eczane (B1.8, B2.4b), 1960'lar ABD bürosu (B4.3, B4.5). Yazı, logo, portre, bayrak, kişi yok. Wikimedia bu turda HTTP 429 verdiği için yeni fotoğraf yerine | kendi düz çizimimiz (`img/cizim_uret.py zemin4`) | tarihselwojak | kendi | — (açıklamada "çizimler: tarihselwojak") |
| `doku_tebesir.jpg`, `doku_karton.jpg`, `doku_duvar_yesil.jpg`, `doku_kagit_mavi.jpg`, `doku_ahsap.jpg` | 4. tur dokuları: kara tahta (B5.13, B6.4a), kraft karton (B2.6, B3.8), iki renkli duvar (B1.4, B3.6), mavi kâğıt (B2.5a, B5.11), ahşap masa (B3.11b) | kendi dokumuz | tarihselwojak | kendi | — |
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

4. tur ekleri: `cizim/kanun_1262_sayfa.jpg` (B1.7 sağ panel: masada 1262 sayılı Kanun sayfası; yalnız kanunun adı,
yılı ve belgeli özü, gerçek Resmî Gazete künyesi yok) · `cizim/gazete_2008_canlandirma.png` (B5.8m: adsız 2008 haber
kupürü, CANLANDIRMA; okunur tek yazı "2008", başlık ve sütunlar okunmaz çubuk; kutular: tarih [745, 214, 955, 287],
başlık [140, 360, 1560, 530]).

## 6. Senaryo sahnesi → dosya

Yollar `uzun/talidomit-turkiye/` köküne göre (`chars/...`, `img/...`); `ep/` = `episodes/talidomit-turkiye/chars/`.
Harita, sayaç, nokta ızgarası, zaman çizelgesi, bölüm kartı, metin kartları motorun kendi sahneleridir (görsel dosyası yok).

5. tur eşlemesi (video.yaml ile aynı; 4. turdan farkı: B3.14 dava sahnesi çıktı, B1.5/B1.7/B2.3/B5.4 karakterli). Kural: bir görsel (aynı fotoğrafın kırpımı ya da baskısı dahil) en çok 2 çekimde;
`konuk` = bilgi sahnesinde köşeden giren karakter.

| Sahne | Dosya(lar) |
|---|---|
| SA.1a, SA.1b, SA.2 | dünya / Akdeniz haritası, sayaç · konuk `chars/anlatici_*` |
| SA.3 (kapı) | `img/foto_saglik_bakanligi.jpg` (1/2) · `ep/temsilci_gulumsuyor.png` → `ep/temsilci_gergin.png` · `img/cizim/kapi_acik.png` → `kapi_kapali.png` |
| SA.3 (pano) | keçe pano (motor) · `img/kompozit/dosya_bos_kagit.jpg` (1/2) · konuk anlatıcı |
| SA.4 | `img/foto_contergan_teneke.jpg` (teneke 1/2) |
| SA.4b | `img/arka_eczane_raflar_169.jpg` (eczane fotoğrafı 1/2) · `chars/anne_adayi_sakin.png` · `img/cizim/numune_kutusu_tabletler.png` |
| SA.5 | metin, kâğıt zemin · konuk anne adayı |
| SA.6 | `img/arka_koridor_cizim.jpg` (1/2) · `img/cizim/kapi_kapali.png` · `chars/temsilci2000_sakin.png` → `temsilci2000_gergin.png` |
| B1.1 | `img/foto_stolberg_grunenthal_169.jpg` (1/1, bulanık) · `takvim_aralik_1956.png`, `numune_kutusu_tabletler.png` · anlatıcı |
| B1.2 | zaman çizelgesi, `img/foto_kupferhof_grunenthal_169.jpg` (1/2) · konuk anlatıcı |
| B1.3 | `img/foto_kupferhof_grunenthal_169.jpg` (2/2) · `molekul_beyaz.png` · anlatıcı |
| B1.4 | `img/doku_duvar_yesil.jpg` (1/2) · `fare_kafesi.png`, `kompozit/doz_*.png` · manşet `kompozit/kart_neredeyse_zehirsiz.jpg` |
| B1.5 | `img/doku_kagit.jpg` (1/2) · `kompozit/serit_*.png` · anlatıcı (5. tur) |
| B1.6 | `img/foto_giessen_1957_169.jpg` (1/2) · `kompozit/baski_forte.png` (forte 1/2) · `takvim_1_ekim_1957.png` · `chars/eczaci_sakin.png` |
| B1.7 | bölünmüş: sol arka `foto_giessen_1957_169.jpg` (2/2) \| sağ `img/cizim/kanun_1262_sayfa.jpg` · konuk anlatıcı (5. tur) |
| B1.8 | `img/arka_eczane_cizim.jpg` (1/2) · `chars/eczaci_sakin.png` · `assets/kit/klasik/sakin.png` (müşteri) |
| B1.9 | `img/foto_koln_1960.jpg` (1/2) · konuk anne adayı |
| B1.10, B2.1 | Avrupa haritası; dünya haritası (2/2) · konuk anlatıcı |
| B2.2 | sayaç, arka `foto_koln_1960.jpg` (2/2) · konuk eczacı |
| B2.3 | `img/cizim/distaval_yedek_kart.jpg` (hesap sahibi onaylarsa `img/telifli/distaval_reklam_wellcome.jpg`) · konuk anne adayı (5. tur) |
| B2.4 | `img/arka_eczane_raflar_169.jpg` (2/2) · eczacı + anne adayı |
| B2.4b | `img/arka_eczane_cizim.jpg` (2/2) · `img/cizim/eczane_raf_turkiye_bos.png` · anlatıcı |
| B2.5a / B2.5b | `img/doku_kagit_mavi.jpg` (1/2) · `chars/voss_sakin.png` → `voss_ciddi.png` · `img/cizim/zarf.png` / zaman çizelgesi (koyu zemin) + konuk Voss |
| B2.6, B2.7 | `img/doku_karton.jpg` (1/2) · anlatıcı / metin (koyu, bilinçli düşüş) |
| B3.1, B3.2 | Hint Okyanusu yarıküre haritası + konuk `chars/lenz_sakin.png`; Avustralya haritası |
| B3.3, B3.5 | `img/arka_muayenehane_169.jpg` (1/2, 2/2) · `chars/lenz_*` · takvimler, `zarf_taahhutlu.png` |
| B3.4 | zaman çizelgesi (koyu) · konuk `lenz_ciddi.png` |
| B3.6 | `img/doku_duvar_yesil.jpg` (2/2) · `lenz_ciddi.png` · `takvim_20_kasim_1961.png` |
| B3.7 | `img/cizim/gazete_1961_canlandirma.png` · konuk `chars/lenz_gazete.png` |
| B3.8 | `img/doku_karton.jpg` (2/2) · `takvim_26/27_kasim_1961.png` · `lenz_ciddi.png` → `lenz_sakin.png` |
| B3.8b, B3.9 | Türkiye haritası (1/2); nokta ızgarası · konuk anlatıcı |
| B3.11, B3.11b | metin (kâğıt); `img/doku_ahsap.jpg` + `img/cizim/tablet.png` + anlatıcı |
| B3.12, B3.13 | `img/foto_protez_kollar.jpg` (1/2, 2/2) · konuk anlatıcı |
| B3.15, B5.10 | Kuzey Atlantik haritası (1/2, 2/2) · konuk anlatıcı / `chars/kaymakcalan_sakin.png` |
| B4.1 | `img/foto_kelsey_masa.jpg` (1/2) · konuk `chars/kelsey_sakin.png` |
| B4.2, B4.4 | `img/arka_ofis_169.jpg` (1/2, 2/2) · `chars/kelsey_sakin/supheci/kararli.png` · `dosya_kevadon.png`, `dosya_sinir_hasari_1961.png`, `kompozit/yigin_*.png` |
| B4.3, B4.5 | `img/arka_buro_cizim.jpg` (1/2, 2/2) · Kelsey · `takvim_eylul_1960.png` / `doz_sisesi.png` (karar: `img/telifli/kevadon_1960_fda.jpg`) |
| B4.6 | sayaç · konuk Kelsey |
| B4.7 | `img/foto_kelsey_kennedy_1962.jpg` (1/2) \| `img/foto_kennedy_imza_1962.jpg` (1/2) |
| B4.8 | `img/foto_ankara_panorama_tam.jpg` (kırpım; panorama 1/2) · `kompozit/baski_kelsey.png` (Kelsey fotoğrafı 2/2) · anlatıcı |
| B4.9 | metin (kâğıt, daktilo) |
| B5.1, B5.6 | `img/foto_ankara_bankalar_caddesi.jpg` (1/2, 2/2) · B5.6 `ep/temsilci_gergin.png` + `numune_kutusu_tabletler.png` |
| B5.2, B5.3c | `img/arka_bakanlik_oda_cizim.jpg` (1/2, 2/2) · `ep/temsilci_gulumsuyor.png` (→ `temsilci_gergin.png`) · `numune_kutusu_tabletler.png` |
| B5.3a, B5.3b | `img/foto_ankara_bankalar_kartpostal_ust.jpg` (1/2, 2/2) · `chars/kaymakcalan_*` · `img/cizim/dosya_ruhsat_basvurusu.png` |
| B5.4 | bölünmüş: sol arka `foto_kennedy_imza_1962.jpg` (2/2) \| sağ `foto_saglik_bakanligi.jpg` (2/2) · konuk `ep/temsilci_gergin.png` (5. tur) |
| B5.7, KP.3b | `img/arka_lille_masa_169.jpg` (Lille fotoğrafı 1/2, 2/2) · `ep/veteriner.png` · `yumurta_tablasi.png` |
| B5.8a, B5.8b | mantar pano (1/2, 2/2) · `kompozit/bulten_kagit.jpg` (aynı kart, iki çekim) · `img/foto_tavuk_embriyosu.jpg` · konuk Kaymakçalan (8a) |
| B5.8m | `img/cizim/gazete_2008_canlandirma.png` · konuk anlatıcı |
| B5.9 | `img/foto_dogu_berlin_kacak_ilac_1961.jpg` · konuk anlatıcı |
| B5.11 | `img/doku_kagit_mavi.jpg` (2/2) · `kompozit/telefon_iddia.png` · anlatıcı |
| B5.12, KP.1 | `img/foto_ankara_sergievi_kartpostal_alt.jpg` (1/2, 2/2) · Kaymakçalan / anlatıcı |
| B5.13, B6.4a | `img/doku_tebesir.jpg` (1/2, 2/2) · `molekul_beyaz.png`, `cereblon.png`, `sall4*.png` · anlatıcı |
| B6.1 | `img/arka_hastane_odasi_cizim.jpg` · `chars/sheskin_*` · `numune_kutusu.png` (komodinde) |
| B6.2 | zaman çizelgesi (kâğıt) · konuk Sheskin |
| B6.3 | `img/foto_brezilya_kutu.jpg` · konuk anlatıcı |
| B6.4b, B6.5 | sayaç (kâğıt); `img/doku_kagit.jpg` (2/2) + `makale_behcet_1998_cizim.png` · anlatıcı |
| B6.6, B6.6b | Türkiye haritası (2/2) + konuk `chars/temsilci2000_sakin.png`; `img/arka_koridor_cizim.jpg` (2/2) + kapı + temsilci2000 |
| B6.7 | bölünmüş: sol arka `foto_contergan_teneke_169.jpg` (teneke 2/2) \| sağ metin (kâğıt) · manşet `img/cizim/kub_bolum44_yedek_kart.jpg` (onay: `img/telifli/kub_*`) |
| KP.2 | `foto_kelsey_kennedy_1962.jpg` (2/2) \| `img/kompozit/dosya_bos_kagit.jpg` (2/2) |
| KP.3a | `img/foto_ankara_panorama_tam.jpg` (başka kırpım; panorama 2/2) · Kaymakçalan |
| Bitiş | `img/foto_contergan_forte.jpg` (forte 2/2, bulanık) · `ep/temsilci_gulumsuyor.png` |
| K1 / K3 / K2 | K1 (ana): zemin `img/kompozit/kr_zehirsiz.jpg` + `ep/temsilci_gergin.png` · K3: `img/kompozit/kr_dosya.jpg` + `chars/temsilci_notr.png` · K2: `img/kompozit/kr_harita.jpg` (4. tur: hap simgeleri yok) + `ep/temsilci_gergin.png`. Küçük resimde CC BY-SA fotoğraf yok (senaryo kuralı) |

Görsel sayılmayanlar: motorun kendi ürettiği koyu/kâğıt bilgi zemini (sayaç, metin, zaman çizelgesi; görsel dosyası yok).

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
