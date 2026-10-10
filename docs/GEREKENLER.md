# Gerekenler ve çalışma düzeni

Güncelleme: 2026-10-09. **Karar:** videoyu ben hazırlarım, sen onaylar ve kendin paylaşırsın.
Bu yüzden Instagram token'ı, video barındırma (R2) ve Creator hesabı **gerekmiyor**. O kurulumlar ileride
istenirse diye [`arsiv/OTOMATIK_YAYIN.md`](arsiv/OTOMATIK_YAYIN.md) içinde duruyor.

## Özet

| Ne | Durum |
|---|---|
| Görsel üretimi (wojak karakteri, arka plan) | **Senin ağ geçidin** (`SOL_API_KEY`), anahtar alındı. Bkz. §1 |
| Metin/görsel/ses soru-cevap | Aynı ağ geçidi (`tools/sol_sor.py`). Senaryoyu ben yazıyorum, ayrı anahtar gerekmez |
| Müzik | **Hazır**: hesabın kendi imza "orijinal ses"i, reel'lerden çıkarıldı (repoya girmez). Bkz. §4 |
| Yayın | **Sen**. Ben her video için hazır paket gönderirim (§2) |
| Gizli bilgiler | Sohbete yazdığın anahtar repoya **yazılmadı**; repo dışında, sadece bu oturumun dosyasında (§1) |

---

## 1. Görsel üretimi: ağ geçidi anahtarı

- Kod `SOL_API_KEY`'i önce ortam değişkenlerinden, yoksa repo **dışındaki** `~/.config/wojak/secrets.env`
  dosyasından okur (izin 600). Repoya, loglara ve paylaşım metinlerine hiçbir zaman yazılmaz.
- **Kalıcılık:** bu bulut oturumu kapanınca konteyner ve o dosya silinir. Yeni oturumlarda anahtarı tekrar
  yazmamak için bir kez şunu yap: oturum başlığındaki **cloud environment** menüsü → **Edit** →
  **environment variables** → `SOL_API_KEY` = (anahtar) → kaydet. Sonraki oturumlar otomatik görür.
  (İstersen `SOL_BASE_URL` ve `SOL_MODEL` da eklenebilir; varsayılanlar `https://sol.ozgurguler.tech/v1`
  ve `gpt-5.6-sol-web`.)
- Kullanım:
  ```bash
  python tools/sol_sor.py --durum                              # ağ geçidi ayakta mı
  python tools/sol_sor.py "Sadece OK yaz."                     # metin testi
  python tools/gorsel_uret.py karakter "an old Anatolian shepherd, flat cap, thick mustache" \
      --duygu wary --ref assets/characters/koylu_kasketli_biyikli.png -o assets/characters/coban.png
  ```
- Arkada ChatGPT sohbeti açıldığı için şeffaf zemin garanti değil: varsayılan olarak **düz yeşil zeminde**
  üretilip otomatik kesiliyor (`WOJAK_SOL_TRANSPARENT=1` ile şeffaf istenir). Kütüphanede uygun wojak varsa
  hiç üretmiyorum (10.378 hazır şeffaf PNG).
- Yedek: ağ geçidi çalışmazsa OpenAI/Gemini anahtarı da destekleniyor (kurulumu arşivde).

## 2. Teslim akışı (ben → sen)

Her video için `teslim/<bölüm>/` klasörü ve sohbete dosya olarak. **Video dosyası sohbetten gelir, repoya
konmaz:** repo herkese açık; videoda kanalın imza sesi ve bazen telifli haber görseli var. Metinler ve kapak repoda da durur.

| Dosya | Ne için |
|---|---|
| `<bölüm>.mp4` | Video (1080x1920, H.264 + AAC, Instagram/YouTube/TikTok uyumlu) |
| `kapak.jpg` | Instagram'da "Kapağı düzenle → Galeriden ekle" |
| `paylasim.md` | Bütün metinler + yükleme kontrol listesi |
| `metinler/instagram_aciklama.txt` | Instagram açıklaması: **başlık + hikâyenin tamamı + görsel atfı + en fazla 5 hashtag** (≤2.200) |
| `metinler/youtube_baslik.txt` | YouTube Shorts başlığı (≤100) |
| `metinler/youtube_aciklama.txt` | YouTube açıklaması (kısa + hashtag + #shorts) |
| `metinler/youtube_sabit_yorum.txt` | YouTube'da yazıp **sabitleyeceğin** hikâye yorumu |
| `metinler/tiktok_aciklama.txt` | TikTok (isteğe bağlı) |
| `<bölüm>_dolgu.mp4`, `kapak_dolgu.jpg` | (Bazı bölümlerde) kenarlık A/B testi sürümü: Instagram'da **deneme reel** olarak (KONSEPT §3) |

Senin adımların: izle → "onay" ya da düzeltme notu → (onaydan sonra) paylaş → YouTube'da yorumu sabitle.
Düzeltme notu gelirse aynı gün yeni sürümü gönderirim.

## 3. Senden istenenler (az)

1. **Onay / geri bildirim:** her videoya kısa bir "tamam" ya da "şunu değiştir".
2. **Sonuç bildirimi (isteğe bağlı ama çok faydalı):** paylaşımdan 2-3 gün sonra Instagram'daki izlenme
   sayısını yaz ya da Reels istatistik ekranının görüntüsünü at. YouTube sayılarını herkese açık veriden ben
   çekerim (`tools/yt_arastir.py`). Neyin tuttuğunu buna göre ayarlarım.
3. **(İsteğe bağlı) Eski ses:** Hello Kitty cinayeti videosunun sesini Shazam'la dinletip adını yaz.
4. **(İsteğe bağlı) Referans videolar:** şu videoların mp4'ünü `referans/` klasörüne at (ya da sohbete):
   Kırkağaç, Epstein Adası, Kapalak kızı, Enkaz altından çıkarılan 4 yaşındaki kız, Pippa Bacca, Hello Kitty
   cinayeti, Ukraynalı kız (Iryna), Hantavirüs. Kurgu temposunu birebir ölçerim.

## 4. Müzik — senden bir şey gerekmiyor

- **Kanalın kendi sesi:** altın dönem reel'lerinin 27/30'unda aynı "orijinal ses" var (Do minör vals, ~153 BPM,
  13,75 sn). Bu ses hesabın reel'lerinden çıkarıldı ve her videoda o kullanılıyor (`music: kanal`); izleyici
  kanalı sesinden tanıyor. Dosya repoya konmaz (`assets/music/ozel/`, herkese açık repoda dağıtılmasın diye).
- Paylaşırken ayrıca müzik ekleme; videodaki ses yeterli.
- Yedek: dosya bulunmazsa burada sentezlenen özgün vals (`assets/music/imza_gece_vals.mp3`, hakkı bize ait).
- Ayrıntı: `STIL.md` §10, `assets/music/README.md`.

## 5. Alınan kararlar

| Konu | Karar |
|---|---|
| Onay | Her video senin onayından geçer |
| Paylaşım | Sen paylaşırsın (Instagram, YouTube, isteğe bağlı TikTok) |
| Hikâye metni | Instagram'da **açıklamada**; YouTube'da **sabit yorumda** (sen sabitlersin) |
| Görsel üretimi | Senin ağ geçidin; önce hazır kütüphane |

Önerim (itiraz etmezsen böyle ilerliyorum):
- **Sıklık:** 2 günde 1 video (altın dönem ritmi), paylaşım saati 20:00-20:15. Akışın en az %60'ı Türkiye
  efsane/gizem; yabancı konu en fazla 4'te 1 (bkz. `INSTAGRAM_ANALIZ.md`).
- **Gündem sınırları:** [`GUNDEM.md`](GUNDEM.md) §2'deki kırmızı çizgiler (yayın yasaklı dosya, çocuk
  istismarı/cinsel suç, intihar, terör failini öne çıkarma, siyaset yok; mağdur ya da şüpheli bir çocuğun
  kimliği hiçbir zaman verilmez).
- **Taze trajedide ton:** yalnızca kurtarma/mucize/iyilik açısı; saf trajedi en az 1 yıl sonra "tarihsel" olarak.
- **Gündem hızı:** taramayı günde 1-2 kez yapar, en iyi adayı videoyla birlikte gönderirim (pencere 7 gün).
