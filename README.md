# Tarihsel Wojak — video üretim hattı

[@tarihselwojak](https://www.instagram.com/tarihselwojak/) (Instagram, ~465K takipçi) ve
[YouTube @tarihselwojak](https://www.youtube.com/@tarihselwojak/shorts) için
"olay" formatındaki wojak videolarını üreten sistem.

**Önce oku:** [`docs/KONSEPT.md`](docs/KONSEPT.md) — formatın neden tuttuğu, kurallar, replik tekniği.

| Belge | İçerik |
|---|---|
| [`docs/KONSEPT.md`](docs/KONSEPT.md) | Konsept kitabı: format, yapı, replik tekniği, karakter dili, başlık, sabit yorum |
| [`docs/ANALIZ.md`](docs/ANALIZ.md) | 223 videonun veri analizi: dönemler, neyin tutup neyin düştüğü |
| [`docs/URETIM_REHBERI.md`](docs/URETIM_REHBERI.md) | Konudan paylaşıma adım adım üretim |
| [`docs/KONU_HAVUZU.md`](docs/KONU_HAVUZU.md) | Yapılmamış konular (öncelikli) |
| [`docs/PROMPTLAR.md`](docs/PROMPTLAR.md) | Wojak/arka plan görsel üretim promptları |
| [`docs/GUNDEM.md`](docs/GUNDEM.md) | Güncel olay oyun kitabı: seçim, hız, uyarlama, hukuk, kontrol listesi |
| [`docs/GEREKENLER.md`](docs/GEREKENLER.md) | **Çalışma düzeni:** teslim paketi, hesap sahibinin yapacakları, görsel üretim anahtarı, kararlar |
| [`data/videos.csv`](data/videos.csv) | Tüm videolar: tarih, süre, izlenme, beğeni, yorum |
| [`data/olay_metinleri.md`](data/olay_metinleri.md) | Hesabın sabit "olay" yorumları (üslup örnekleri) |

## Kurulum

```bash
sudo apt install ffmpeg            # yoksa
pip install -r requirements.txt
python tools/make_sfx.py           # telifsiz ses efektlerini üret (assets/sfx)
python tools/wojak_lib.py index    # karakter indeksi (data/wojak_index.csv zaten repoda)
```

## Hızlı başlangıç

```bash
python -m wojak new yeni-olay                  # episodes/_sablon -> episodes/yeni-olay
# episodes/yeni-olay/episode.yaml'ı düzenle, img/ klasörüne görselleri koy
python -m wojak check  episodes/yeni-olay      # doğrula + zaman çizelgesi
python -m wojak frames episodes/yeni-olay      # her sahneden 1 kare (hızlı kontrol)
python -m wojak render episodes/yeni-olay      # out/yeni-olay/: mp4 + kapak.jpg + paylasim.md + metinler/
python -m wojak teslim episodes/yeni-olay      # onaya: teslim/yeni-olay/ (video, kapak, metinler)
```

**Akış:** videoyu ben hazırlarım → `teslim/<bölüm>/` + sohbette dosya → hesap sahibi onaylar ve kendisi paylaşır
(Instagram: hikâye açıklamada; YouTube: hikâye sabit yorumda). Ayrıntı: [`docs/GEREKENLER.md`](docs/GEREKENLER.md).

Teslim edilen bölümler (`teslim/<bölüm>/`: video, kapak, paylaşım metinleri):

| Bölüm | Tür | Video |
|---|---|---|
| [`episodes/derinkuyu`](episodes/derinkuyu/episode.yaml) | Türkiye gizemi | [`teslim/derinkuyu/`](teslim/derinkuyu/) |
| [`episodes/dyatlov-gecidi`](episodes/dyatlov-gecidi/episode.yaml) | Dünya gizemi | [`teslim/dyatlov-gecidi/`](teslim/dyatlov-gecidi/) |

Örneklerde kanalın imza müziği (`assets/music/imza_gece_vals.mp3`, burada üretildi, hakkı bize ait) ve sentezlenmiş efektler var.

## Ne yapar?

```
episode.yaml ──► sahne kompozisyonu (Pillow) ──► kare kare animasyon ──► ffmpeg (H.264, 30fps)
   │               arka plan + wojak + yazı          zoom, pop-in,            + ses miksi (müzik,
   │               + filigran (1080x1080 kare)        sarsıntı, flaş           efekt, seslendirme)
   └──► paylasim.md + metinler/*.txt: Instagram açıklaması (hikâye dahil), YouTube başlık/açıklama/sabit yorum, TikTok
```

- **Format:** 1080x1920 siyah tuval, ortada 1080x1080 görsel (altın dönem videolarından ölçüldü).
- **Yazı:** Poppins Bold Italic, beyaz + siyah kontur (orijinallerle birebir eşleşiyor), dengeli satır kırma.
- **Sahne tipleri:** `dialog` (arka plan + karakter + replik), `card` ("Bir süre sonra"), `evidence` (gerçek fotoğraflar, 1-4'lü ızgara, haber bandı/etiket).
- **Sansür:** `wojak/censor.py` — başlık ve sabit yorumda hassas kelimeler (`*ldürüldü`, `c!nayet`, `t3c4v*z`).

## Araçlar

| Komut | Ne işe yarar |
|---|---|
| `tools/wojak_lib.py` | 10.378 şeffaf wojak PNG'si (HF `clayshoaf/Wojaks` = wojakparadise arşivi): ara, önizle, indir |
| `tools/cutout.py` | Beyaz/düz zeminli wojak görselini şeffaf PNG'ye çevir |
| `tools/gorsel_uret.py` | Yapay zekâ ile karakter/arka plan (hesap sahibinin ağ geçidi `SOL_API_KEY`; yedek: OpenAI, Gemini) |
| `tools/sol_sor.py` | Ağ geçidine metin/görsel/ses sorusu (bağlantı testi, görsel kontrolü, ses dökümü) |
| `tools/gundem.py` | Gündem tarayıcı: Türkiye haber akışlarından kanala uygun güncel olaylar, `--taslak N` ile bölüm taslağı, `--yasak-takip` ile yayın yasağı takibi |
| `tools/ig_yayinla.py` | (Kullanılmıyor: paylaşımı hesap sahibi yapıyor) Instagram resmi API ile yayın; kurulum `docs/arsiv/OTOMATIK_YAYIN.md` |
| `tools/make_music.py` | Kanalın imza müziğini (ürkütücü müzik kutusu valsi) sentezle |
| `tools/bg_ara.py` | Telifsiz arka plan arama/indirme (Openverse) |
| `tools/make_sfx.py` | Ses efektlerini sentezle |
| `tools/yt_arastir.py` | YouTube kopyasından performans verisi, kapaklar, yorumlar |
| `tools/ig_fetch.py` | Instagram reel istatistikleri/videoları (IG çerezi gerekir) |

## Gizli bilgiler (API anahtarı, çerez)

**Repoya yazılmaz.** Cloud environment ayarlarından ortam değişkeni olarak eklenir ya da repo dışındaki
`~/.config/wojak/secrets.env` dosyasına (AD=değer, izin 600) yazılır (`wojak/config.py: load_secrets`):

| Değişken | Ne için |
|---|---|
| `SOL_API_KEY` (+ ops. `SOL_BASE_URL`, `SOL_MODEL`) | Görsel üretim ve metin/görsel soru-cevap (hesap sahibinin ağ geçidi) |
| `OPENAI_API_KEY` veya `GEMINI_API_KEY` | Yedek görsel üretim |
| `IG_ACCESS_TOKEN`, `R2_*` | Kullanılmıyor (otomatik yayın; `docs/arsiv/OTOMATIK_YAYIN.md`) |
| `IG_SESSIONID` (ops.) | Eski yöntem: çerezle istatistik (`tools/ig_fetch.py`) — token varsa gerekmez, **ikincil hesap** çerezi |

## Araştırma ortamı notları

- Instagram bu sunucudan login duvarı gösteriyor → analiz YouTube kopyası üzerinden yapıldı.
- YouTube video dosyaları indirilemiyor (indirme linkleri IP'ye bağlı, çıkış IP'si değişken);
  metadata, kapak kareleri, storyboard ve yorumlar alınabiliyor. YouTube bot korumasını aşmak için
  `bgutil-ytdlp-pot-provider` sunucusu gerekir:
  `git clone https://github.com/Brainicism/bgutil-ytdlp-pot-provider && cd bgutil-ytdlp-pot-provider/server && npm ci && npx tsc && node build/main.js`
- Wikimedia (API ve `upload.wikimedia.org`) paylaşılan çıkış IP'sini sık sık 429 ile sınırlıyor; Openverse sorunsuz. Commons dosyası gerekiyorsa birkaç dakika arayla tekrar dene.

## Lisanslar

- Fontlar: Poppins, Anton — SIL Open Font License (`assets/fonts/OFL-*.txt`).
- Ses efektleri: `tools/make_sfx.py` ile matematiksel olarak üretildi.
- Wojak görselleri: topluluk meme sanatı (wojakparadise arşivi); örnek arka planlar CC0 (rawpixel) ve Wikimedia Commons.
