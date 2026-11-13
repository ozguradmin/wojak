# Hava müzikleri v2: inceleme notları (13.11.2026)

Hesap sahibi ilk 10 hava parçasını reddetti: "oyun yapıyorsan arka plan müziğine uyar ama bizim wojak videolarına
uymaz. Eski klasik sesi iyi incele, en çok beğenilen oydu. Yenileri videolarımıza uyacak şekilde yaptır." Bu dosya o
incelemenin özeti ve v2'nin gerekçesidir. Kimse dinleyemedi: her şey ölçüme, notaya ve iki hakemin okumasına dayanır.

## 1. Eski klasik sesin kaynağı

"Phantomimes", SDM Nation (single, 12.04.2023, 4:56, ISRC TCAHA2337763, "℗ 2023 The SDM Enterprises"). Deezer ve
iTunes'daki 30 sn'lik önizlemelerle bizim 13,75 sn'lik sesin dalga biçimi 0,91 ve 0,90 oranında örtüşüyor (rastgele
eşleşme medyanı 0,005): aynı kayıt. Lo-fi bant (enerjinin %99,7'si 250-4000 Hz) yayınlanan kaydın kendisinde var,
Instagram'ın işi değil. Deezer'daki besteci bilgisi yükleyenin kendi beyanı (ad hesap sahibine sohbette iletildi);
başka kaynak bulunamadı.
Serbest lisans yok, ticari yayın: YouTube'da telif talebi olasılığı var. Kullanım kararı hesap sahibinindir.

## 2. Klasik sesin yapısı (üst düzey; nota dökümü telif nedeniyle repoda tutulmaz)

- 3/4, ~152 BPM, Do minör, 13,75 sn, tek cümle, döngü yok, sert bitiş. Dosya iki parlak "pa" vuruşuyla başlar.
- **Tek bir iki ölçülük akor sarkacı** (tonik ile eksik yedili; bas bir ses çıkıp iner) baştan sona hiç değişmez.
- İlk dört ölçü (0-4,6 sn) yalnız kamışlı um-pa-pa: 1. vuruş koyu ve yumuşak, 2-3. vuruş parlak. Yorumlardaki "u a a" bu.
- Ezgi (çift sesli serbest kamış: tremolo armonika ya da müzet akordeon) 4,9 sn'de, 2. vuruşta girer. **İki ölçülük tek
  bir hücre** üç kez söylenir. İkinci söylenişin sonunda "çığlık" (iki vuruş tutulan yüksek nota, yarım ses düşer;
  ~8,1-9,3 sn). Sonra tonik ~11,6 sn'den kesmeye kadar tutulur.
- Videolarımızla örtüşmesi: ilk kesme 2,5-3 sn (um-pa-pa altında), ara kart 7,0-8,5, ters köşe sahnesi 8,5-10,5 (çığlık),
  kanıt görselleri 10,5-11 sn'den sonra (tutulan nota). 63 bölümümüzün zaman çizelgesinden.
- Sonuç: sevilen şey zenginlik değil **yalınlık ve tekrar**. Gölge (12 ayrı akor, baştan ezgi) klasikten daha karmaşık.

## 3. Hesap sahibinin kendi seçimleri (referans/meta.json, 75 reel)

41 reel klasik sesi kullanıyor. Kalanlarda konuya göre başka ses seçilmiş: paranormal/gizem konularında "Verbatim
(Slowed Down)" (Mother Mother, 5 reel), kahramanlık/iyilik konularında "Memory Reboot" (VØJ, Narvent, 2 reel), 2025'te
iki ayrı "orijinal ses". Ortak yanları: yavaş, koyu, duygusal, tek fikirli; neşeli ya da orkestral olan yok.

## 4. Ölçüm araçları

- `arastirma/imza_muzik/olcum/olcum.py`: klasik sese tını/kayıt benzerliği (TIMBRE_SCORE, 100 = klasik). Klasik ses
  `assets/music/ozel/` altında olmalı; simgesel denetimler için gereken nota dökümü repoda yok.
- `arastirma/hava_muzik/kulak.py`: "kulak". İki AudioSet etiketleyici (AST, PANNs CNN14) ve iki CLAP modeli; klasik ve
  Gölge'ye gömme benzerliği, "oyun müziği / eski plak / meme videosu" gibi karşıt istemler, hava göstergeleri.
  `pip install torch transformers` ve Hugging Face'ten model indirme gerekir. `ref_emb.npz` yalnız gömme vektörleridir.

| | TIMBRE_SCORE | KANAL_UYUMU (kulak) |
|---|---|---|
| eski klasik ses | 100 | 78 |
| Gölge (repo dosyası) | 75 | 77 |
| 21.10'da reddedilen sentez valsler | | 36-38 |
| 13.11'de reddedilen 10 hava parçası | 13-16 | 1-22 |
| **v2: gizem / merak / ironik / destansı / masal** | 62 / 60 / 52 / 64 / 60 | 72 / 70 / 59 / 68 / 71 |

Sınır: kulağın hava göstergeleri aile içinde ayırt etmiyor (kamışlı valsin hepsi "ironik/masal" okunuyor; klasik ses
de öyle). Havanın doğru okunup okunmadığını yalnız hesap sahibinin kulağı söyler.

## 5. v2'nin tasarımı ve hakem düzeltmeleri

Beş parça klasik sesin iskeletinde ve aynı motorla; hava şunlarla değişir: ton/makam, sarkacın iki akoru, hücrenin
ritmi ve yönü, çığlığın türü, bitiş, çalgı rengi, girişin dokusu. Ayrıntı her bestenin açıklamasında
(`tools/hava_besteler.py`). İki bağımsız hakem (besteci gözü, izleyici gözü) ilk taslağa 6-7,5 verdi; işlenenler:

- **Benzerlik riski** ("yine aynı vals"): her havanın girişi ayrıldı (gizemde üç sesli ve tepesi kayan eşlik,
  destansıda üçlüsüz açık beşliler + davul, ironikte kuru kesik eşlik ve 160 BPM, masalda 144 BPM ve müzik kutusu);
  hücre ritimleri ve çığlık türleri birbirinden ayrıldı.
- **ironik**: ilk taslaktaki çığlık klasik sesin çığlığının aynısıydı; "yanlış nota" şakası aşağıdan yukarı kayan
  başka bir notaya taşındı, sondaki kromatik "womp womp" düşüşü çıkarıldı, hücreye kendi (topallayan) ritmi verildi.
- **destansı**: ilk taslak Re minörde "korsan/denizci" ezgilerinin iskeletine oturuyordu; ton, hücre ve doku değişti.
- **gizem**: hücreye dörtlü sıçrayış eklendi, çığlık yükselip asılı kalan bir soruya çevrildi, son nota klasik sesin son
  notası olmaktan çıkarıldı. **masal**: ezgi artık majör üçlüyü söylüyor. **merak**: son akor çözülüyor.

Hakemlerin düzeltmelerinden sonraki sürüm yeniden hakeme okutulmadı (kullanım sınırı); ilk dinleyen hesap sahibidir.

## 6. Açık kalanlar

- Hesap sahibi beğenirse: `config.HAVA_ONAYLI = True`, el kitabı §6 tablosu, her havaya ikinci parça.
- Beğenmezse denenecek ikinci yol: kendi seçimlerinin tarzı (§3: yavaşlatılmış, koyu, tek fikirli) ayrı bir motorla.
