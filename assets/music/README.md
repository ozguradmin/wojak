# Müzik

## Hava kütüphanesi (12.11.2026): `hava/`, bize ait

Hesap sahibi: "sürekli aynı müzik sıkıyor". Konuya göre beş hava, her birinde iki parça. Hangi konuya hangisi:
`docs/KISA_REEL_EL_KITABI.md` §6 tablosu. `music: gizem` o havanın parçalarından birini bölüm kimliğine göre sabit seçer,
`music: gizem_b` o parçayı (`wojak/episode.py` `muzik_dosyasi`).

Üretim `python tools/hava_muzik.py --hepsi` (besteler `tools/hava_besteler.py`, nota nota kod). Her çalgı ayrı MIDI
(`mido`), FluidSynth ile MuseScore General SF2 (MIT; yaylılar VSCO-2 CE, CC0; piyano kamu malı Splendid Grand) çalınır, numpy
ile EQ ve ortak sentetik yankı, 14,0 sn kusursuz döngü (yankı kuyruğu başa sarılır), −14 LUFS, gerçek tepe ≤ −1,5 dBTP, AAC
192k. Kayıt, örnek ya da başka bir parçanın sesi yok; melodi ve armoni özgün. Her parça Gölge'nin açılışındaki "5-4 | 3"
iç çekişini küçük bir selam olarak taşır (`masal_b`'de Lidya renkli Do-Si | La). Ölçümler, piyano rulosu ve spektrogram
`out/hava/` altında; `--dinleme` hepsini numaralı kartlarla tek videoda dinletir (`out/hava/hava_dinleme.mp4`).
Kurulum: `apt-get install fluidsynth musescore-general-soundfont-lossless` ve `pip install mido soundfile scipy matplotlib`.

| Dosya | Ad | Ton, ölçü, tempo | Çalgılar |
|---|---|---|---|
| `gizem_a.m4a` | Saat | Re minör, 4/4, 137 | tik-tak çelesta, klarnet, pizzicato bas, tremolo, timpani |
| `gizem_b.m4a` | Dehliz | Mi minör, 6/8, 206 (sekizlik) | yumuşak piyano arpeji, yalnız keman, konser davulu, uzak çan |
| `merak_a.m4a` | Keşif | Sol majör, 4/4, 120 | marimba, glockenspiel, zıplayan pizzicato, shaker, üçgen |
| `merak_b.m4a` | Buluş | Re majör, 6/8, 257 (sekizlik) | flüt, klarnet, arp, pizzicato bas, glockenspiel, tef |
| `ironik_a.m4a` | Sinsi | Re minör, 4/4, 120 | parmak ucunda fagot, pizzicato, glockenspiel göz kırpması, tahta blok |
| `ironik_b.m4a` | Ters Köşe | Fa majör, 3/4, 154 | klarnet, tuba "um-pa-pa", pizzicato, glockenspiel |
| `destansi_a.m4a` | Zafer | Re minör, 4/4, 137 | kornolar (ikinci yarıda trompetler), 3+3+2 yaylı ostinato, timpani, taiko |
| `destansi_b.m4a` | Onur | Sol minör, 4/4, 69 | ağır korno, yaylılar, kontrbas, uzak trampet, timpani |
| `masal_a.m4a` | Kule | Mi minör, 3/4, 116 | flüt + çelesta, arp valsi, yaylılar |
| `masal_b.m4a` | Rüya | Fa Lidya, 6/8, 206 (sekizlik) | çelesta, glockenspiel, arp, "u" korosu, viyolonsel |

## Eski klasik kanal sesi: `music: klasik` (12.11.2026)

Altın dönemin "orijinal ses"i (G1, Do minör vals, 13,75 sn; STIL §10). Hak sahibi belirsiz olduğu için açık repoya girmez:
özel depoda (`wojak-ozel/kanal_orijinal_ses.m4a`) durur, `tools/hazirla.sh` her oturumda `ozel/` altına kopyalar. 22.10'da
YouTube ihlali sonrası bırakılmıştı; 12.11'de hesap sahibi kısıtlanan videoları tek tek izledi, hiçbirinde bu ses yoktu:
"hep olmasa da yine kullanabiliriz". Kural: `kanal` yerine arada bir (son 7 günde en çok 2), yalnız tr kanalı.
`music: orijinal` aynı dosyadır.

## Kanalın imza müziği (22.10.2026): `imza_v2_golge.m4a`, bize ait

`music: kanal` bunu çalar (`wojak/config.py` MUSIC_IMZA); hüzünlü konuların ve kararsız kalınca varsayılanıdır. Eski
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
