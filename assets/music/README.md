# Müzik

## Kanalın imza müziği (varsayılan)

`imza_gece_vals.mp3` — `python tools/make_music.py` ile sentezlenen özgün, ürkütücü müzik kutusu /
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
