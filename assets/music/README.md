# Müzik

Bu klasöre gerilim/korku müzikleri konur (repoya **telifsiz** olanlar eklenmeli).

## Öneri
1. **Instagram/TikTok:** videoyu müziksiz render edip uygulama içinden **trend ses** ekle.
   Trend ses keşfette ek itme sağlar ve telif sorunu yaratmaz.
2. **YouTube Shorts:** YouTube Studio'daki ses kitaplığından ya da Shorts ses seçiminden ekle,
   veya buraya koyduğun telifsiz müziği `episode.yaml > music:` ile göm.

## Telifsiz kaynaklar
- YouTube Ses Kitaplığı (Studio > Ses kitaplığı) — "Dark", "Cinematic", "Horror" türleri
- Pixabay Music — "horror", "dark ambient", "suspense" (atıf gerekmez)
- Free Music Archive — CC-BY parçalar (atıf `sources:` alanına)

## Kullanım
```yaml
music: {file: gerilim_01.mp3, start: 12.5, volume: 0.85, fade_out: 0.3}
```
`start`: parçanın kaçıncı saniyesinden başlanacağı (en gerilimli kısmı seç).
