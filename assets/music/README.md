# Müzik

## Hava kütüphanesi v2 (13.11.2026): `hava/`, bize ait, hesap sahibi onayladı

Hesap sahibi 12.11: "sürekli aynı müzik sıkıyor". İlk deneme (10 parça, temiz "orkestra" MIDI'si: marimba, korno,
pizzicato, salon yankısı, kusursuz döngü) 13.11'de reddedildi: "oyun yapıyorsan arka plan müziğine uyar ama bizim wojak
videolarına uymaz; eski klasik sesi iyi incele". Ölçü de aynısını söylüyordu: eski klasik sese benzerlik puanında
(0-100) Gölge 75, o parçalar 13-16.

v2, eski klasik sesin **iskeleti** üzerine beş kardeş valstir (inceleme: `arastirma/hava_muzik/NOTLAR.md`): 3/4, iki
vuruşluk "pa pa" ile başlar, iki akorluk sarkaç baştan sona sürer, ilk 4 ölçü yalnız kamışlı um-pa-pa ("u a a"), ezgi
~4,5 sn'de girer, iki ölçülük hücre yinelenir, ~8 sn'de "çığlık" (videoda ters köşe), son nota kesmeye kadar tutulur
(kanıt görselleri). Ses Gölge'yi yapan ev sesi motorundan çıkar (`tools/ev_sesi/`: FluidR3 örnekleri, MIT + klasik
sesten **ölçülen** lo-fi zincir; klasik sesin kendisinden hiçbir ses kullanılmaz). Melodiler ve armoniler özgün.
Benzerlik puanı 52-64, kanal uyumu 59-72 (klasik 78, Gölge 77, reddedilenler 1-22).

| Dosya | Ad | Ton, tempo | Sarkaç | Renk ve fikir |
|---|---|---|---|---|
| `gizem_a.m4a` | Fısıltı | La minör, 152 | i ↔ ♭vi (La m ↔ Fa m) | klarnet-müzet; yoklayan hücre, yükselip asılı kalan soru, açık biten son |
| `merak_a.m4a` | Acaba | Sol majör, 152 | I ↔ II (Lidya) | tremolo armonika; soru tonlamalı hücre, "buldum" anı, çözülen son |
| `ironik_a.m4a` | Hınzır | Fa majör, 160 | I ↔ V7 | kuru, kesik eşlik; topallayan hücre, "yanlış nota" şakası, sonda kısa bir "tak" |
| `destansi_a.m4a` | Yemin | Fa minör → Fa majör, 152 | i ↔ ♭VII (açık beşliler) | hafif davul; borazan gibi noktalı hücre, ♭VI-♭VII-I ile majöre çıkış |
| `masal_a.m4a` | Bir Varmış | Mi majör, 144 | I ↔ iv | müzik kutusu + kamış; beşik gibi hücre, Hicaz basamaklı kapanış |

Üretim: `python tools/hava_muzik.py --hepsi` (besteler `tools/hava_besteler.py`; aynı JSON + tohum = aynı dosya).
Dinleme: `python tools/hava_muzik.py --onizleme plan.json out/hava/onizleme.mp4` parçaları gerçek yayınlanmış videoların
altında çaldırır. Hesap sahibi 13.11'de dinleyip onayladı ("güzel olmuş hepsi"); seçim tablosu el kitabı §6'da. Her
havada şimdilik tek parça var; ikinci parça eklenince `music: gizem` ikisi arasında bölüm kimliğine göre seçer.

## Eski klasik kanal sesi: `music: klasik` (12.11.2026)

Altın dönemin "orijinal ses"i (G1, Do minör vals, 13,75 sn; STIL §10). Hak sahibi belirsiz olduğu için açık repoya girmez:
özel depoda (`wojak-ozel/kanal_orijinal_ses.m4a`) durur, `tools/hazirla.sh` her oturumda `ozel/` altına kopyalar. 22.10'da
YouTube ihlali sonrası bırakılmıştı; 12.11'de hesap sahibi kısıtlanan videoları tek tek izledi, hiçbirinde bu ses yoktu:
"hep olmasa da yine kullanabiliriz". 13.11'den beri kural: iki kanalda da sırayla, önceki bölüm klasik değilse klasik
("hepsini kullan, eski klasiğe daha çok öncelik ver"); `check` sırayı denetler. en kanalı da dosyayı `wojak-ozel`'den alır.
`music: orijinal` aynı dosyadır.

## Kanalın imza müziği (22.10.2026): `imza_v2_golge.m4a`, bize ait

`music: kanal` bunu çalar (`wojak/config.py` MUSIC_IMZA); klasik sırası olmayan bölümlerde hüzünlü konuların ve kararsız
kalınca seçimidir. Eski
orijinal ses `music: klasik` (yukarıda). Ölçüme dayalı ikinci çalışmanın ürünü (arastirma/imza_muzik/, DURUM.md): özgün melodiler,
orijinalden ses kullanılmadı; eleştirmen puanları 7-7,5/10. Hesap sahibi dördünü "hepsi benzer" buldu: aynı ailedir,
videoya göre dönüşümlü kullanılabilir (`music: {file: imza_v2_ic_cekis_b.m4a}` gibi).

| Dosya | Melodi | Ses | Eleştirmen (ses/müzik) |
|---|---|---|---|
| `imza_v2_golge.m4a` (varsayılan) | Gölge (b1-4d) | FluidR3 akordeon (MIT) | 7,5 / 7,5 |
| `imza_v2_ic_cekis_b.m4a` | İç Çekiş (b1-1) | FluidR3 akordeon | 7 / 7,5 |
| `imza_v2_ic_cekis_hohner.m4a` | İç Çekiş | FreePats Hohner (CC0) | 7 / 7,5 |
| `imza_v2_golge_sentez.m4a` | Gölge | tamamen sentez | 7 / 7 |
| `imza_v2_ic_cekis.m4a` | İç Çekiş, ilk sürüm | FluidR3 | Çanakkale'de yayınlandı |

## Yeni imza: `imza_vals.m4a` (21.10.2026, hesap sahibinin onayı bekleniyor)

Yıllardır kullanılan orijinal sesin (`ozel/kanal_orijinal_ses.m4a`) **bize ait benzeri**. Hesap sahibi YouTube ihlali
sonrası istedi (YAYIN_PLANI §0). `python tools/imza_muzik.py` ile tamamen sentezlenir: kayıt, örnek ya da başka bir
parçanın sesi yok, melodi ve armoni özgün. Aynı his: Do minör, 3/4, ~152 BPM, legato akordeon/harmonyum, gramofon bandı,
13,75 sn tek cümle, sonda tonikte kalış.

| Dosya | Varyant | 1-4 kHz payı (orijinal %62) | Ton/renk benzerliği | Melodik benzerlik |
|---|---|---|---|---|
| `imza_vals.m4a` | imza (ana) | %66 | 0,73 | 0,07 |
| `imza_vals_ikinci.m4a` | ikinci | %61 | 0,83 | 0,10 |
| `imza_vals_ucuncu.m4a` | ucuncu | %63 | 0,80 | 0,16 |

Melodik benzerlik ölçeği (`--karsilastir`): orijinalin kendi kopyası 0,99, alakasız bir parça (`imza_gece_vals`) 0,14.
Bizimkiler alakasız parça düzeyinde, yani melodi kopyalanmadı; ton ve tını ise yakın.
Her video için değiştirmek: `--varyant`, `--ton` (yarım ses), `--tempo`, ya da `MELODILER`'e yeni 12 ölçülük bir melodi
(orijinalin Mi♭5-Re5-Fa5 açılışı ve 8. ölçüdeki La♭5-Sol5 doruğu kullanılmaz). Onaylanınca `music: kanal` bu dosyayı
kullanacak (`wojak/config.py`); şimdilik `episode.yaml`'da `music: {file: imza_vals.m4a}` ile seçilir.

## Eski sentez imza: `imza_gece_vals.mp3`

`python tools/make_music.py` ile sentezlenen özgün, ürkütücü müzik kutusu /
gramofon valsi (La minör, 3/4, plak cızırtısı, 46 sn). **Hakkı bize ait**: Instagram, YouTube ve
TikTok'ta "orijinal ses" olarak gider, sonradan sessize alınmaz, telif talebi almaz.

```yaml
music: {file: imza_gece_vals.mp3, start: 0, volume: 0.7, fade_out: 0.3}
```

Neden: altın dönemde kullanılan ürpertici ses (yorumlarda "u a a u a a") büyük ihtimalle
"Phantomimes" adlı bir vals; hak sahibi belirsiz (orta güven, doğrulanamadı). Başkasının kaydını
dosyaya gömmek sessize alınma riski taşır; Meta sessize alınmış Reels'leri daha az gösteriyor.
Aynı **hissi** (melodiyi değil) veren kendi parçamız bu riski sıfırlar. Instagram'da orijinal ses
bir kez `audio_name` ile adlandırılabilir (ör. "Tarihsel Wojak · Gece Valsi"); kullanım
biriktikçe kendi ses sayfası oluşur.

## Platform bazında

| Platform | Varsayılan | İsteğe bağlı |
|---|---|---|
| Instagram | İmza müzik gömülü | Uygulamadan elle trend ses (hesap **Creator** olmalı: bazı Business hesaplar lisanslı kütüphaneye erişemiyor). API ile ses eklemek (Instagram Audio API, `audio_configuration`) yalnızca **Facebook Login** yolunda var; parça başından başlar, kırpılamaz |
| YouTube Shorts | İmza müzik gömülü | YouTube Ses Kitaplığı parçası (YouTube'da Content ID almaz) |
| TikTok | İmza müzik gömülü | İşletme hesabı yalnızca Ticari Müzik Kütüphanesi (CML) kullanabilir |

Not: "trend ses keşfette öne çıkarır" iddiasının resmi bir dayanağı bulunamadı. Meta'nın resmi
sinyalleri: yeniden paylaşım, sonuna kadar izleme, beğeni ve "ses sayfasına gitme" olasılığı.

## Başka telifsiz kaynaklar (atıf ve risk)

| Kaynak | Atıf | Not |
|---|---|---|
| Meta Sound Collection | Yok | Yalnızca Facebook/Instagram içinde |
| YouTube Ses Kitaplığı | CC parçalarda zorunlu | YouTube için güvenli; IG/TikTok izni doğrulanamadı |
| Pixabay Music | Gerekmez | Bazı parçalar Content ID'ye kayıtlı (sayfada işaretli) — onları kullanma |
| Incompetech (Kevin MacLeod) | CC BY 4.0, görünür atıf zorunlu | Hatalı Content ID eşleşmeleri olabiliyor |
| Free Music Archive | Parçaya göre (CC BY/BY-SA) | NC lisanslıları kullanma |
| Freesound (efekt) | CC0 yok / CC BY var | Yalnızca CC0 ve CC BY süz |

Atıf gereken parça kullanılırsa atıf Instagram/TikTok/YouTube **açıklamasına** yazılır (sabit yorum silinebilir).
