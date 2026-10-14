# Talidomit uzun video: karakter haritası (7. tur, 13.10.2026)

> Hesap sahibi (13.10): "kendi çizdiğimiz kıyafetler kötü" (wojak başı + elle boyanmış tişört/önlük, kayık yaka,
> boyunda dikiş izi). Kural (docs/OGRENILENLER.md, üst tablo): kıyafetli karakter **hazır** bulunur; kıyafete
> dokunulmaz; yüz varyantı yalnız temiz yüz düzeltmesidir.
>
> Bu klasördeki `uret.py` karakterlerinin (klasik kafa + bizim çizdiğimiz önlük/kazak/saç/gözlük) yerine
> `hazir_uret.py` çıktıları (`*_v2_*.png`) geçer. Eski dosyalar yapımcı `video.yaml`'ı değiştirene kadar silinmedi.
> Yapımcı 7. turda `video.yaml`'ı bu eşlemeye çevirdi (aşağıda §6).

```bash
python uzun/talidomit-turkiye/chars/hazir_uret.py              # bütün v2 karakterler + bakış kaydı (data/karakter_yon.json)
python uzun/talidomit-turkiye/chars/hazir_uret.py lenz voss     # yalnız bazıları; --kayitsiz: bakış kaydı yazma
```

- Kaynak PNG'ler `kaynak/` altında (indirildiği gibi; şeffaf kenarı kırpılmış). Çizime, kıyafete, saç çizgisine
  dokunulmadı. Yapılanlar yalnız: yüz içi silme + aynı çizgi kalınlığında, kenarı keskin (MS-Paint) yeni kaş/göz/ağız;
  ter ve gözyaşı `tools/kit_varyant.py` ile (kanalın kit dili); düz renk değişimi (saç rengi, allık ve göz altı
  morluğu silme). Her karakterin bütün varyantları aynı tuvalde (yüz değişiminde kutu zıplamaz); tuvalin üstüne
  16 px saydam pay eklendi.
- Hepsi 3/4 profilde sağa bakar; her PNG'ye bakıldı ve `sag` olarak kaydedildi (24 dosya, eski kayıt kalıntısı yok).
- İnceleme sayfaları (repo dışı): `scratchpad/uzun/talidomit-turkiye/karakter/inceleme/` (1:1 yüz kırpımları,
  360 px boy + 120 px telefon satırı, eski/yeni/onaylı kısalar yan yana) ve `karakter/baglam*/` (videonun kendi
  motoruyla eski ve yeni karakterli aynı kareler).

## 1. Eşleme: eski dosya -> yeni dosya

`boy ×`: aynı yüz büyüklüğü için `video.yaml`'daki `boy` değerinin çarpanı (motorla çizilen karşılaştırma
karelerinden ölçüldü; başlangıç değeri, son karar kareye bakarak).

| Eski dosya | Yeni dosya | Rol | Kullanıldığı sahneler (eski) | boy × |
|---|---|---|---|---|
| `anlatici_sakin.png` | `anlatici_v2_sakin.png` | anlatıcı/izleyici "feels guy" | SA.1a, B1.1, B1.1b, B1.7, B2.1, B2.4b, B3.8b, B3.9, B5.13, B6.5 | 1,0 |
| `anlatici_dusunceli.png` | `anlatici_v2_dusunceli.png` | (10. tur: yakın kaş alçak ve düz, uzak kaş yüksek kemer, ağız sağa kaymış ve aşağı eğik: telefonda sakinden ayrılır) | SA.3b, B1.1b, B1.2, B1.3, B1.7, B2.6, B3.8b, B3.11b, B3.15, B4.1, B4.8, B5.8m, B5.8b, B5.9, B5.11, B6.4a, B6.4b, KP.1, KP.2 | 1,0 |
| `anlatici_ciddi.png` | `anlatici_v2_ciddi.png` | (10. tur: kalın V kaşlar, kaş arası kırışık, uçları aşağı ağız; eskisi sakinden 2-5 px kaş farkıydı) | SA.3b, B1.5, B3.11b, B3.13, B5.8m, B5.8b, B5.9, B6.3, KP.1, KP.2 | 1,0 |
| `anlatici_fark.png` | `anlatici_v2_fark.png` | (kalkık kaşlar, açık gözler) | SA.2, B1.2, B1.3, B1.7, B2.1, B2.4b, B3.15, B4.1, B4.8, B5.11, B6.4a, B6.4b, B6.5, KP.1 | 1,0 |
| `anlatici_saskin.png` | `anlatici_v2_saskin.png` | (fark + "o" ağız) | B5.13, KP.1 | 1,0 |
| `anlatici_terli.png` | `anlatici_v2_terli.png` | (endişeli kaşlar + 3 ter damlası) | SA.1a, SA.1b, B1.5, B2.6 | 1,0 |
| `anlatici_gozyasli.png` | `anlatici_v2_gozyasli.png` | (endişeli kaşlar + iki gözyaşı) | SA.1b, SA.2, B3.9, B6.3 | 1,0 |
| `kaymakcalan_sakin.png` | `kaymakcalan_v2_sakin.png` | Şükrü Kaymakçalan rolü | B5.3a, B5.10, B5.12, KP.3 | 1,0 |
| `kaymakcalan_dusunceli.png` | `kaymakcalan_v2_dusunceli.png` | | B5.3a, B5.3b, B5.8a | 1,0 |
| `kaymakcalan_ciddi.png` | `kaymakcalan_v2_ciddi.png` | | B5.3b | 1,0 |
| `kaymakcalan_kollar.png` | `kaymakcalan_v2_kararli.png` | (9. tur: kalın V kaşlar camın üstüne iner + kaş arası kırışık + kısık gözler (üst kapak içten aşağı) + belirgin aşağı uçlu ağız: telefonda 'ciddi'den ayrılır; doruğun "hayır" yüzü) | B5.3b (son yüz), kapanış kartı A | 1,0 |
| `lenz_sakin.png` | `lenz_v2_sakin.png` | Widukind Lenz rolü (taban yüz zaten hafif endişeli) | B3.1, B3.3, B3.8 | 0,92 |
| `lenz_fark.png` | `lenz_v2_fark.png` | | B3.3 | 0,92 |
| `lenz_ciddi.png` | `lenz_v2_ciddi.png` | (10. tur: kalın V kaşlar + kırışık + aşağı uçlu ağız; taban yüz zaten hafif endişeli olduğundan eskisi sakinle aynı okunuyordu) | B3.4, B3.6, B3.8 | 0,92 |
| `lenz_telefon.png` | `lenz_v2_ciddi.png` + ayrı sahne nesnesi `img/cizim/telefon_simge.png` | telefon eden Lenz: çizilmiş el + ahize yerine masadaki telefon (sfx `telefon` zaten var) | B3.5 | 0,92 |
| `lenz_gazete.png` | `lenz_v2_fark.png` (ya da `_ciddi`) | gazete zaten sahnenin ana görseli (B3.7 manşet); konuk yalnız tepki verir | B3.7 | 0,92 |
| `voss_sakin.png` | `voss_v2_sakin.png` | Ralf Voss rolü | B2.5a | 1,0 |
| `voss_ciddi.png` | `voss_v2_ciddi.png` | (10. tur: kalın V kaşlar + kırışık + aşağı uçlu ağız) | B2.5a, B2.5b | 1,0 |
| `sheskin_sakin.png` | `sheskin_v2_sakin.png` | Jacob Sheskin rolü (8. tur: kaynağın püskürtme gri saçı iki düz griye indirildi, `sac_duzle`) | B6.1, B6.2 | 0,96 |
| `sheskin_saskin.png` | `sheskin_v2_saskin.png` | (kalkık kaşlar, camların içinde açık gözler, "o" ağız; çerçeve korunur) | B6.1, B6.2 | 0,96 |
| `eczaci_sakin.png` | `eczaci_v2_sakin.png` | 1950'ler eczacısı (bıyık, papyon, bordo ceket) | B1.6, B1.8, B2.2, B2.4 | 0,85 |
| `kelsey_sakin.png` | `kelsey_v2_sakin.png` | Frances O. Kelsey rolü (aynı hazır taban, aynı renk değişimi; yüzler temiz yeniden; 10. tur: soluk pembe dudak gölgesi silindi, üç yüzde ağız aynı siyah çizgi) | B4.1, B4.2, B4.3, B4.4 | 1,0 |
| `kelsey_supheci.png` | `kelsey_v2_supheci.png` | (9. tur: sol göz kısık + alçak düz kaş, sağ kaş yüksek kemer; 10. tur (izlenme S1): ağız düz, uçları hafif aşağı (kalkık uç kısık gözle 'göz kırpan sırıtma' gibiydi); kısık gözde kirpikler üst kapakta, alt yarı temiz yeniden çizildi) | B4.3, B4.4, B4.6 | 1,0 |
| `kelsey_kararli.png` | `kelsey_v2_kararli.png` | (9. tur: kalın V kaşlar + kaş arası kırışık, iki göz kısık, uçları aşağı sıkılı ağız; 10. tur: kısık gözlerde kirpikler üst kapakta, sağ gözün iç köşe kırıntısı silindi) | B4.4, B4.5, B4.6 | 1,0 |
| `assets/kit/klasik/sakin.png` (B1.8 müşteri) | `musteri_v2_sakin.png` | eczane müşterisi: uykusuz yüz (uyku ilacı almaya gelen); çıplak omuzlu klasik büst yerine giyimli | B1.8 | 0,9 |
| `episodes/talidomit-turkiye/chars/veteriner.png` | `veteriner_v2_sakin.png` (**isteğe bağlı**) | Aygün rolü: kısa videodakiyle aynı yüz, ama boyanmış önlük yerine hazır süveter yelek + gömlek | B5.7, KP.3b | 1,0 |
| — | `veteriner_v2_ciddi.png` | 9. tur: içe doğru inen kalın kaşlar + kaş arası çizgi, uçları aşağı ağız ("Bakanlığı uyarmış") | B5.7 | 1,0 |
| — | `eczaci_v2_konusuyor.png`, `temsilci_gulumsuyor_konusuyor.png`, `temsilci_gergin_konusuyor.png` | 9. tur: aynı tuvalde açık ağız (koyu ağız içi + siyah kontur); motor `balon {agiz}` hecelerde bu yüze geçer. Temsilci tabanı Short'un `episodes/talidomit-turkiye/chars/temsilci_*.png` dosyaları (dokunulmadı; kopyası buraya yazıldı) | B1.8, B2.4, B5.2, B5.6 | 1,0 |

Bir karakterin aynı sahnedeki bütün `yuz` olayları aynı aileden olmalı (v2 tabanla eski varyant karışırsa tuval
boyu farklıdır, kutu zıplar). `isim` etiketleri değişmez.

## 2. Değişmeyenler (hazır kıyafetli, olduğu gibi kalır)

| Dosya | Neden |
|---|---|
| `anne_adayi_sakin.png` | wojakland "Trad Wife", çizime dokunulmamış |
| `temsilci2000_sakin.png`, `temsilci2000_gergin.png` | wojakland "Grey Suit Wojak" (yalnız gömlek rengi) + kit ter damlası; 1:1 temiz |
| `temsilci_notr.png` (K3 küçük resmi) | kısa videonun temsilcisi, yalnız ağız düzeltmesi; 1:1'de yalnız 3x büyütmede görünen soluk iz var, sorun değil |
| `episodes/talidomit-turkiye/chars/temsilci_gulumsuyor.png`, `temsilci_gergin.png` | onaylı kısa videonun karakteri (wojakland "1950s Businessman Wojak") |

## 3. Kaynaklar ve lisans

Hiçbirinin açık lisansı yok (topluluk wojak çizimleri). Kanalın bütün bölümlerindeki pratik: karakter olarak
kullanılır, kaynak yazılır. **Lisans kararı hesap sahibinindir** (CLAUDE.md, teslim akışı 2).

| `kaynak/` dosyası | Kullanan | Kaynak | Not |
|---|---|---|---|
| `anlatici_kaynak_flannel.png` (1043x1111) | anlatici_v2_* | wojakland "Flannel Wojak" https://wojakland.com/wp-content/grand-media/image/original/flannel_wojak.png (sayfa https://wojakland.com/gmedia/flannel_wojak-png/) | wojakland'de kullanım şartı sayfası yok |
| `kaymakcalan_kaynak_office_doomer.png` (1078x1108) | kaymakcalan_v2_* | HF clayshoaf/Wojaks `5_Doomer/13708` "Depressed Office Worker" https://huggingface.co/datasets/clayshoaf/Wojaks/resolve/main/5_Doomer/13708.png | wojakparadise arşivi: yükleyenin malı, açık izin yok (klasik taban ve Kelsey tabanıyla aynı durum) |
| `lenz_kaynak_english.png` (970x987) | lenz_v2_* | wojakland "English Wojak" https://wojakland.com/wp-content/grand-media/image/original/english_wojak.png | |
| `voss_kaynak_blushing_suit.png` (806x849) | voss_v2_* | wojakland "Blushing Suit Wojak" https://wojakland.com/wp-content/grand-media/image/original/blushing_suit_wojak.png | allık silindi, saç kumrala çevrildi |
| `sheskin_kaynak_turtleneck.png` (873x971) | sheskin_v2_* | wojakland "Turtleneck Grey Hair Wojak" https://wojakland.com/wp-content/grand-media/image/original/turtleneck_grey_hair_wojak.png | |
| `eczaci_kaynak_suit.png` (820x768) | eczaci_v2_sakin | wojakland "Suit Wojak" https://wojakland.com/wp-content/grand-media/image/original/suit_wojak.png | değiştirilmedi |
| `musteri_kaynak_tired_blonde.png` (841x821) | musteri_v2_sakin | wojakland "Tired Blonde Wojak" https://wojakland.com/wp-content/grand-media/image/original/tired_blonde_wojak.png | değiştirilmedi |
| `kelsey_kaynak_secretary.png` (mevcut) | kelsey_v2_* | HF clayshoaf/Wojaks `5_Daddys_Girl/11087` "Secretary Daddy's Girl" | eski turla aynı |
| `episodes/talidomit-turkiye/chars/veteriner_kaynak_grandpa.png` (mevcut) | veteriner_v2_sakin | wojakland "Grandpa Wojak" | kısa videoyla aynı kaynak |

Göz kaynağı: `kaymakcalan_v2_*` camlarındaki gözler Flannel Wojak'ın klasik gözleridir (`parca_tasi`): aynı çizgi
ailesinden hazır çizim, elle çizilmedi.

## 4. Yapımcıya notlar

1. `video.yaml`: bölüm 1'deki eşlemeyle `gorsel` yollarını değiştir; `boy` değerlerini çarpanla başlat ve kareye bak
   (özellikle B1.8 müşteri, B5.3b doruk, KP.1 orta plan anlatıcı, KP.3 Kaymakçalan).
2. B5.3b: son `yuz` olayı `kaymakcalan_v2_kararli`. B3.5: `lenz_v2_ciddi` + `img/cizim/telefon_simge.png`
   (`bakis: on`, masanın üstünde, küçük) önerilir. B3.7: konuk `lenz_v2_fark`.
3. Paket metni: `telif_notu` "Açık lisansı olmayan karakter tabanları" maddesi ve `gorsel_atif` "Karakterler (klasik
   wojak ve wojakland çizimleri üzerine)" satırı yeni kaynaklara göre güncellenmeli (Flannel, English, Blushing Suit,
   Turtleneck Grey Hair, Suit, Tired Blonde Wojak: wojakland; Depressed Office Worker: wojakparadise arşivi).
   `VARLIKLAR.md` §1 de bu tabloya göre güncellenmeli (bu turda dokunulmadı).
4. Ses yeniden üretilmez; karakter değişimi sesi etkilemez.

## 5. Dürüst değerlendirme

- Kazanç: yeni satır, onaylı kısaların karakterleriyle aynı dilde (hazır, renkli kıyafet, düz MS-Paint, aynı çizgi
  kalınlığı); eskiler hep aynı önlük + kask gibi saç şablonuydu ve telefonda birbirinden ayrılmıyordu. Artık her rol
  saç rengi, gözlük ve kıyafetle tek bakışta ayrılıyor: Kaymakçalan (siyah saç, kalın siyah gözlük, yeşil gömlek),
  Lenz (koyu kıvırcık saç, palto, ekose kravat), Voss (kumral, siyah takım), Sheskin (kır, gözlük, balıkçı yaka),
  eczacı (bıyık, papyon), anlatıcı (kırmızı ekose gömlek).
- Bilinen bedeller: (a) doktorların hiçbirinde önlük yok: hazır, temiz, dönem uyumlu önlüklü wojak bulunamadı
  (adaylar maskeli/modern, sırıtan ya da ağlayan, kırışık dokulu ya da ~600 px altıydı). 1960'ların hekim fotoğraflarında takım
  elbise olağan; rolü isim etiketi taşır. (b) Lenz'in gerçek fotoğraflarındaki gözlük yok (Kaymakçalan'la
  karışmasın diye bilerek). (c) Kavuşturulmuş kollu Kaymakçalan ve telefon/gazete tutan Lenz yok (eller bizim
  çizimimiz olurdu): yerine yüz ve sahne nesnesi. (d) Sheskin'in kır saçı kaynakta püskürtme gölgeli (düz değil);
  müşterinin saçı 1950'ler için biraz uzun. (e) Anlatıcının ekose gömleği kırmızı: haritadaki kırmızı ülkelerle
  yan yana siyah kareler sayesinde ayrışıyor (SA.1a karesi), ama "kırmızı = tehlike" dilini biraz sulandırabilir.
  (f) Telefon boyunda (120 px) fark/şaşkın/terli/gözyaşlı açıkça okunuyor; sakin, düşünceli ve ciddi arasındaki fark
  kaş düzeyinde (orijinallerdeki gibi) ince.

## 6. Yapımcı uygulaması (7. tur, video.yaml)

- Bütün eski dosyalar v2'ye çevrildi (eski kalan: 0); `boy` çarpanları uygulandı, sonra karelere bakılarak:
  müşteri 0,60 / eczacı 0,58 (B1.8, yalnız baş görünüyordu), Kelsey 0,76 (B4.5, üstteki kelime saçına biniyordu) ve
  0,78 (B4.1, isim etiketi çenesine biniyordu), Kaymakçalan B5.3a x 0,75 / boy 0,84.
- Baş-omuz kesimli hazır çizimlerde çene kadrajın alt çeyreğinde: alt banttaki isim etiketi aynı taraftaysa çeneye
  biniyordu (eski karakterlerde de böyleydi). Etiketler karakterin **karşı tarafına** alındı (Voss, Lenz, Kaymakçalan
  B5.3a ve KP.3, Aygün, Sheskin); o köşedeki nesneler (dosya, yumurta tablası) yukarı, masaya taşındı.
- B3.5: `lenz_telefon` yerine `lenz_v2_ciddi` + masadaki `img/cizim/telefon_simge.png` (ilk denemede telefon Lenz'in
  başına biniyordu; takvim, telefon, zarf ve Lenz soldan sağa sıralandı). B3.7: `lenz_v2_fark`.
- Yeni yüz: `anlatici_v2_mutlu.png` (kapanış çağrısında abone tıkı; kapalı kavisli gözler + yumuşak gülümseme, aynı
  çizgi kalınlığı; `python hazir_uret.py anlatici --yuz mutlu` yalnız bu dosyayı yazar).
- Kapanış çağrısının kartları: `kaymakcalan_v2_kararli`, `img/cizim/kanun_1262_sayfa.jpg`, `img/cizim/zarlar.png`.

## 7. 8. tur (animasyon hakemi S8)

- `kelsey_v2_supheci`: tek ağız (yay silindi); şüphe kalkık kaşla.
- `sheskin_v2_sakin/saskin`: saç iki düz gri (128 / 196), kontur ve yüz değişmedi (`hazir_uret.py sheskin`).
- Anne adayına endişeli yüz **eklenmedi**: B2.4'te anlatım "gönül rahatlığıyla alıyor" diyor ve anne adayı mağdur
  gibi gösterilmiyor (senaryo kuralı); "HAMİLELERDE TEST EDİLMEDİ" izleyicinin bilgisi, onun değil.

## 8. 11. tur (animasyon hakemi M3, S5, S6, S9)

- `temsilci_gergin_konusuyor.png`: açık ağzın sağ köşesinde eski düz çizginin aşağı kancası siyah leke olarak kalmıştı
  (~896-905, 824-832 px); silme kutusu genişletildi (`hazir_uret.py agiz`). 1:1 ve kontrastı 6 kat artırılmış kırpımda
  temiz.
- Balon ağızlarına ara yarık: `eczaci_v2_konusuyor_yari`, `temsilci_gulumsuyor_konusuyor_yari`,
  `temsilci_gergin_konusuyor_yari` (aynı tuval, aynı 9 px çizgi; açık hilal biraz sığlaştı). Motor `agiz: [yarık,
  açık]` ile kapalı -> yarık -> açık sırasında, en az 4 kare tutarak geçer (telefonda yanıp sönen sırıtış yok).
- `kaymakcalan_v2_dusunceli`: yakın kaş camın çok üstünde yüksek kemer, uzak kaş alçak ve düz, göz bebekleri küçük ve
  üst kapağa yapışık (camın içi silinip gözler aynı kalın üst kapakla yeniden çizildi), ağız kısa, yana itilmiş ve
  eğik. `kaymakcalan_v2_ciddi`: kalın kaşlar camın üst kenarına basar (gözler açık), ağız uçları belirgin aşağı.
  Telefon boyunda (baş ~150 px) dört yüz ayrışıyor (`kararli`: V kaş + kısık göz + sert ağız).
- 13. tur (animasyon hakemi S4): `kaymakcalan_v2_dusunceli`'nin yeniden çizilmiş ince badem gözleri öteki üç yüzün
  taşınan klasik Flannel gözlerinden (kalın kontur, büyük göz bebeği) ayrı bir çizim diliydi (6:18-6:30 yakın
  çekimi). Şimdi klasik gözler kalır: üst kapak düz ve aşağıda (gözün üst ~%25'i silinir, 10 px kapak çizgisi; göz
  bebeği kapağın altında yarım ay, yana bakar); kaşlar ve "hmm" ağzı aynı. `hazir_uret.py kaymakcalan --yuz dusunceli`
  (yalnız bu yüz yazılır). Bakış yeniden kaydedildi (`python -m wojak yon … --yon sag`; kayıt sha1 ile tutulur).
- Anne adayına endişeli yüz yine **eklenmedi** (8. turdaki gerekçe; animasyon S5 bunu tekrar istedi): B2.4'te
  "HAMİLELERDE TEST EDİLMEDİ" sözünde kamera anne adayına yavaşça iter (`it`); ironi görüntüde, anne mağdur değil.
- Kapanış kartı A artık `kaymakcalan_v2_sakin` ile başlar, vurgusunda `kararli`ya geçer ve başının yanına küçük
  "HAYIR" damgası iner (motor `secenekler[].vurgu_gorsel`, `damga`).
