# Gerekenler ve adım adım kurulum

Bu belge hesap sahibinin yapması gerekenleri sırayla anlatır. Bilgiler 2026-10-09'da resmi Meta,
OpenAI ve Google dokümanlarından derlendi; menü adları zamanla değişebilir.

## Özet: ne lazım?

| # | Ne | Zorunlu mu? | Ne işe yarar | Maliyet | Süre |
|---|---|---|---|---|---|
| 1 | Instagram'ı **Creator (İçerik Üretici)** hesap yapmak | Önerilir | API ile yayın + müzik kütüphanesi erişimi | 0 | 2 dk |
| 2 | **Instagram yayın token'ı** (`IG_ACCESS_TOKEN`) | Otomatik yayın için evet | Videoyu Instagram'a benim yüklemem, yorumu yazmam, istatistik okumam | 0 | 20-30 dk |
| 3 | **Görsel üretim API anahtarı** (`OPENAI_API_KEY`) | Önerilir | Kütüphanede olmayan karakterleri (jandarma, imam...) ve arka planları üretmek | ~$2-12/ay | 15 dk + kimlik doğrulama |
| 4 | Müzik | **Hayır** — hazır | Kanalın imza müziği üretildi (`assets/music/imza_gece_vals.mp3`), hakkı bize ait | 0 | — |
| 5 | Eski ses doğrulaması | İsteğe bağlı | Altın dönem sesi neydi? (Shazam ile 10 sn) | 0 | 1 dk |
| 6 | Referans videolar | İsteğe bağlı | Eski videoların ses/kurgu temposunu birebir görmek | 0 | 5 dk |
| 7 | Kararlar (aşağıda) | Evet | Yayın düzeni ve onay akışı | — | — |

Gizli bilgiler (token, API anahtarı) **sohbete ya da repoya yazılmaz**. Hepsi bölüm 0'daki yöntemle eklenir.

---

## 0. Gizli bilgi (token / API anahtarı) nasıl eklenir?

1. Bu Claude Code oturumunun başlığındaki **cloud environment** (bulut ortamı) menüsünü aç → **Edit**.
2. **Network secrets** bölümü varsa oraya, yoksa **environment variables** (ortam değişkenleri) bölümüne ekle.
   Uygulaman eski sürümse bölümün adı **API credentials** olabilir.
3. Ad / değer olarak gir, örn. `IG_ACCESS_TOKEN` = `IGAA...`. Kaydet.
4. **Yeni bir oturum aç** — değişkenler yeni oturumda görünür. Bana "token'ı ekledim" demen yeterli;
   değerini yazma.

Resmi açıklama: https://code.claude.com/docs/en/cloud-environments

---

## 1. Instagram hesabını Creator yap

Telefonda: profil → sağ üst ☰ → **Ayarlar ve hareketler** → **Profesyoneller için** → **Hesap türü ve araçlar**
→ (zaten profesyonelse) **Hesap türünü değiştir** → **İçerik üreticisi hesabına geç**.

- API yayını Business ve Creator'ın ikisinde de çalışır.
- Ama Meta, lisanslı müzik kütüphanesini "bazı işletme hesaplarına" kapatıyor; Creator'da bu kısıt yok.
- Kategori seçimi hesap türünü değiştirmez; istediğin an geri dönebilirsin.
- Hesap **herkese açık** kalmalı (API şartı).
- Test: Reels → Ses ekranında popüler bir Türkçe şarkı ara. Sadece "Sound Collection" görünüyorsa hesap kısıtlı.

(Menü adları üçüncü taraf rehberlerden; Türkçe arayüzde birebir farklı olabilir.)

---

## 2. Instagram yayın token'ı (adım adım)

**Yol: "Instagram API with Instagram Login"** — Facebook Sayfası gerekmez, token panelden tek tıkla
60 günlük gelir, kendi hesabın için **App Review gerekmez**. Kullanılan API sürümü: v26.0.

Gerekenler: bir **Facebook hesabı** (geliştirici paneline sadece Facebook hesabıyla girilir; Sayfa gerekmez),
telefon ve e-posta doğrulaması. Facebook ve Instagram'da iki adımlı doğrulamayı açman önerilir.

### 2.1 Meta geliştirici kaydı (bir kez)
1. Facebook'a girişliyken **https://developers.facebook.com/async/registration** adresini aç.
2. **Next** ile şartları kabul et → telefon ve e-postaya gelen kodları gir → mesleğini seç.

### 2.2 Uygulama oluştur
1. **https://developers.facebook.com/apps/creation/** (ya da panelde **Create App**).
2. **App details:** ad (ör. `Tarihsel Wojak Yayin`), iletişim e-postası → **Next**.
3. **Use cases:** **Manage messaging & content on Instagram** → **Next**.
   (Listede yoksa: **Other** → **Next** → **Business** → **Next**; uygulama açılınca **Instagram** ürününde **Set up**.)
4. **Business:** **I don't want to connect a business portfolio yet** → **Next** → **Requirements: Next** →
   **Go to dashboard**.

### 2.3 İzinleri ekle (token'dan ÖNCE)
1. Sol menü **Dashboard** → **Customize the Manage messaging and content on Instagram use case** →
   **API setup with Instagram login**.
2. **Add all required permissions**.
3. Sol menü **Permissions and features** → şunları da ekle:
   - `instagram_business_content_publish` — Reels yayını
   - `instagram_business_manage_comments` — hikâye yorumunu yazmak
   - `instagram_business_manage_insights` — izlenme/erişim istatistiklerini okumak (benim analiz yapmam için;
     böylece çerez gerekmez)

### 2.4 Instagram hesabına "Instagram Tester" rolü ver
1. Panel → **App roles** → **Roles** → **Add People** → **Instagram Tester** → `tarihselwojak` → **Add**
   (durum "Pending" görünür).
2. Bilgisayarda tarayıcıdan instagram.com'a `tarihselwojak` ile gir → **Ayarlar** → **Uygulamalar ve web siteleri**
   → **Test kullanıcısı davetleri** (Tester invites) → uygulamanın davetinde **Kabul et**.
   Doğrudan adres: https://www.instagram.com/accounts/manage_access/
3. Panelde "Pending" yazısı kalkmalı. (Bu adım atlanırsa token üretirken hata alınıyor.)

### 2.5 Token üret
1. Sol menü **Instagram** → **API setup with Instagram login** → **Generate access tokens** bölümü.
2. **Add account** → **Continue** → Instagram'a `tarihselwojak` ile gir → izinleri onayla.
3. Hesabın yanındaki **Generate token** → tekrar giriş → **token'ı kopyala** (IGAA... ile başlar).
   Panelden gelen token zaten **60 günlüktür**.
4. Bölüm 0'daki yöntemle ekle: `IG_ACCESS_TOKEN` = (token).

### 2.6 Test ve bakım (bunları ben çalıştırırım)
```bash
python tools/ig_yayinla.py kontrol        # hesap adı, tipi, user_id, günlük kota
python tools/ig_yayinla.py yenile         # ~50 günde bir: 60 günü yeniden başlatır
```
- Süresi dolan token yenilenemez → 2.5'i tekrarla. Instagram şifresi değişirse token'ı yeniden üret.
- İlk test yayınından sonra gönderiyi **çıkış yapılmış bir tarayıcıdan** kontrol et
  (uygulama "Development" modunda gönderilerin herkese görünüp görünmediği resmi olarak doğrulanamadı).

### 2.7 Önemli kısıtlar
- **Video herkese açık bir HTTPS adresinde olmalı** (Instagram Login yolunda Meta videoyu oradan indirir).
  `--dosya` ile doğrudan yükleme denenecek; resmi olarak yalnızca Facebook Login yolunda var.
  Olmazsa iki seçenek: (a) videoyu herkese açık bir depoya koymak (ör. Cloudflare R2 / S3 kısa ömürlü
  link), (b) hesap bir Facebook Sayfasına bağlıysa **Facebook Login** yoluna geçmek (doğrudan yükleme +
  Instagram müzik kütüphanesinden API ile ses ekleme bu yolda var). İlk denemede birlikte karar veririz.
- **Yorum sabitleme API'de yok.** Hikâye yorumunu otomatik yazarım; sen telefondan sabitlersin
  (Android: yoruma uzun bas → raptiye; iOS: sola kaydır → raptiye).
- API ile gönderi silinemez (yanlış gönderi uygulamadan silinir).
- Günlük API yayın limiti 50-100 (bize fazlasıyla yeter).

Kaynaklar: [Instagram Login API](https://developers.facebook.com/documentation/instagram-platform/instagram-api-with-instagram-login),
[Get Started / token](https://developers.facebook.com/documentation/instagram-platform/instagram-api-with-instagram-login/get-started),
[Content Publishing](https://developers.facebook.com/documentation/instagram-platform/content-publishing),
[App Review (kendi hesap için gerekmez)](https://developers.facebook.com/documentation/instagram-platform/app-review),
[Token yenileme](https://developers.facebook.com/documentation/instagram-platform/reference/refresh_access_token).

---

## 3. Görsel üretim API anahtarı (adım adım)

**Öneri: OpenAI, model `gpt-image-2.5-flare`.** Şeffaf PNG'yi doğrudan veriyor (wojak karakteri için kritik),
orta kalitede dikey görsel ≈ $0.01. Yedek: Google Gemini `gemini-nano-banana-2.1` (şeffaflık yok; yeşil zeminde
üretip keserim).

> Model durumu (2026-10): `gpt-image-1` 23 Ekim, `gpt-image-1.5` 1 Aralık 2026'da kapanıyor;
> `gemini-2.5-flash-image` kullanımdan kalktı. Kod güncel modellere ayarlı.

### 3.1 OpenAI
1. **https://platform.openai.com** → kayıt ol (ChatGPT aboneliğinden ayrı; Türkiye destekleniyor).
2. **Kredi yükle:** Settings → Organization → **Billing** → ödeme yöntemi ekle → **en az $5** kredi al.
   Otomatik yüklemeyi (auto-recharge) kapalı bırak.
3. **Harcama sınırı:** platform.openai.com/settings/organization/limits → **Spend** → **Edit spend limit** →
   **$20** → **Enforce a hard limit** açık → **Save**. Ayrıca **$10** uyarı (spend alert) ekle.
4. **Kuruluş kimlik doğrulaması** (görsel modeller için büyük olasılıkla gerekli): Settings → Organization →
   **General** → **Verify Organization**. Geçerli bir kimlik (pasaport/ehliyet/kimlik kartı) ve yüz doğrulaması.
   İyi ışıkta tek seferde tamamla (tekrar denemek zor olabiliyor). Erişimin açılması ~15 dk.
   (Türk kimliğinin kabul edildiği resmi olarak doğrulanamadı; pasaport en güvenlisi.)
5. **Proje:** Settings → **Projects** → yeni proje `tarihselwojak`.
6. **Anahtar:** platform.openai.com/settings/organization/api-keys → **Create new secret key** → proje
   `tarihselwojak` → bir **son kullanma tarihi** ver → anahtar bir kez gösterilir, kopyala.
7. Bölüm 0'daki yöntemle ekle: `OPENAI_API_KEY` = (anahtar).

### 3.2 Gemini (yedek ya da alternatif)
1. **https://aistudio.google.com** → Google hesabıyla gir → şartları kabul et (otomatik bir anahtar oluşur;
   ek anahtar: aistudio.google.com/api-keys → **Create API key**).
2. **Faturalandırma zorunlu** (görsel modellerinde ücretsiz katman yok): API keys / Projects sayfası →
   **Set up billing** → kart → **en az $5 ön ödeme**.
3. Harcama tavanı: aistudio.google.com/spend → **Monthly spend cap** → $15.
4. Ekle: `GEMINI_API_KEY`.

### 3.3 Aylık maliyet tahmini
Haftada 5 video × (~4 yeni karakter + 2 arka plan) ≈ ayda 130 görsel:
OpenAI medium ≈ **$2-3**, high ≈ $6-12; Gemini ≈ $4-9. Kütüphanede bulunan karakterler için hiç ödeme yok.

Kaynaklar: [OpenAI görsel rehberi](https://developers.openai.com/api/docs/guides/image-generation),
[fiyatlar](https://developers.openai.com/api/docs/pricing), [kullanımdan kaldırmalar](https://developers.openai.com/api/docs/deprecations),
[harcama sınırı](https://developers.openai.com/api/docs/guides/spend-limits),
[Gemini görsel](https://ai.google.dev/gemini-api/docs/image-generation), [Gemini fiyat](https://ai.google.dev/gemini-api/docs/pricing).

---

## 4. Müzik — senden bir şey gerekmiyor

- **Kanalın imza müziği hazır:** `assets/music/imza_gece_vals.mp3` — özgün, ürkütücü müzik kutusu valsi,
  burada sentezlendi, **hakkı bize ait**. Her videoda aynı ses = tanınan bir kanal sesi; sessize alınma veya
  telif talebi riski yok.
- Altın dönemdeki ses (yorumlarda "u a a u a a") büyük ihtimalle **"Phantomimes"** adlı bir vals
  (orta güven). Hak sahibi belirsiz olduğu için dosyaya gömmüyoruz.
- Ayrıntı: `assets/music/README.md`.

## 5. (İsteğe bağlı) Eski sesi doğrula
Instagram'da Hello Kitty cinayeti videosunu aç → alttaki ses etiketine dokun ya da Shazam'la 10 sn dinlet →
adını bana yaz.

## 6. (İsteğe bağlı) Referans videolar
Token (2.3'teki `instagram_business_manage_insights` izniyle) eklenince eski Reels'lerin izlenme ve
istatistiklerini API'den okuyabilirim. Videoların ses/kurgusunu birebir görmek için şu 8 videonun mp4'ünü
repoya `referans/` klasörüne yükleyebilirsin: Kırkağaç, Epstein Adası, Kapalak kızı, Enkaz altından çıkarılan
4 yaşındaki kız, Pippa Bacca, Hello Kitty cinayeti, Ukraynalı kız (Iryna), Hantavirüs.

---

## 7. Senin karar vermen gerekenler

1. **Onay akışı:** Ben her videoyu hazırlayıp `out/<bölüm>/` altına (video + kapak + açıklama + sabit yorum)
   koyayım, sen bakıp "yayınla" de → ben yayınlayayım? Yoksa tamamen otomatik mi? (Öneri: ilk 2 hafta onaylı.)
2. **Yayın sıklığı:** öneri haftada 5 (3 tarihsel/efsane + 1-2 gündem), saat 17:00-21:00.
3. **Gündem sınırları:** `docs/GUNDEM.md` §2'deki kırmızı çizgiler senin için uygun mu? (yayın yasaklı
   dosya, çocuk istismarı/cinsel suç, intihar, terör failini öne çıkarma, siyaset hiç yapılmaz; mağdur ya da
   şüpheli bir çocuğun kimliği hiçbir zaman verilmez.)
4. **Sabit yorum:** API sabitleyemiyor; yayından sonraki ilk dakikalarda telefondan sabitleyebilir misin?
   (Bildirim gidecek.) Alternatif: hikâyeyi açıklamaya (2.200 karakter) koymak.
