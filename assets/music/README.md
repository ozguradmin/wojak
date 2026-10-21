# Müzik

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
