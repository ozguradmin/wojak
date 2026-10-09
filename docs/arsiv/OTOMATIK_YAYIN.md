# Arşiv: otomatik yayın ve ücretli görsel API kurulumları

> **Kullanılmıyor (2026-10-09 kararı):** paylaşımı hesap sahibi kendisi yapıyor; görsel üretimi hesap sahibinin
> ağ geçidiyle (`SOL_API_KEY`). Bu sayfa ileride otomatik yayın ya da yedek görsel API'si istenirse diye duruyor.
> Bilgiler 2026-10-09'da resmi Meta/OpenAI/Google/Cloudflare belgelerinden derlendi; menü adları değişebilir.
> İlgili araç: `tools/ig_yayinla.py` (çalışır durumda, kullanılmıyor).

## 0. Gizli bilgi (token / API anahtarı) nasıl eklenir?

1. Bu Claude Code oturumunun başlığındaki **cloud environment** (bulut ortamı) menüsünü aç → **Edit**.
2. **Network secrets** bölümü varsa oraya, yoksa **environment variables** (ortam değişkenleri) bölümüne ekle.
   Uygulaman eski sürümse bölümün adı **API credentials** olabilir.
3. Ad / değer olarak gir, örn. `IG_ACCESS_TOKEN` = `IGAA...`. Kaydet.
4. **Yeni bir oturum aç** — değişkenler yeni oturumda görünür. Bana "token'ı ekledim" demen yeterli;
   değerini yazma.

Resmi açıklama: https://code.claude.com/docs/en/cloud-environments

---

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
python tools/ig_yayinla.py yenile         # 45-50. günde: 60 günü yeniden başlatır
```
- Yenilemeyi ben çalıştırırım ve hatırlatıcı kurarım. Ancak bu oturum ortam değişkenini kendisi değiştiremez:
  yenileme yeni bir token dizesi döndürürse araç bunu söyler ve `IG_ACCESS_TOKEN`'ı senin güncellemen gerekir
  (dönen dizenin aynı mı yeni mi olduğu belgede yazmıyor; ilk yenilemede göreceğiz).
- Süresi dolan token yenilenemez → 2.5'i tekrarla. Instagram şifresi değişirse token'ı yeniden üret.
- İlk test yayınından sonra gönderiyi **çıkış yapılmış bir tarayıcıdan** kontrol et
  (uygulama "Development" modunda gönderilerin herkese görünüp görünmediği resmi olarak doğrulanamadı).

### 2.7 Önemli kısıtlar
- **Video herkese açık bir HTTPS adresinde olmalı** (Instagram Login yolunda Meta videoyu oradan indirir).
  Doğrudan dosya yükleme (resumable) resmi belgeye göre yalnızca Facebook Login yolunda var. Çözüm: **2.8 R2**.
  Alternatif: hesap bir Facebook Sayfasına bağlanıp **Facebook Login**'li ayrı bir uygulama ve token
  (doğrudan yükleme + Instagram müzik kütüphanesinden API ile ses ekleme yalnızca bu yolda var).
- **Yorum sabitleme API'de yok.** Hikâye yorumunu otomatik yazarım; sen telefondan sabitlersin
  (Android: yoruma uzun bas → raptiye; iOS: sola kaydır → raptiye).
- **Yorum düzenlenemez, açıklama düzenlenemez, gönderi API ile silinemez.** Düzeltmede yeni yorum yazıp
  eskisini silerim (`ig_yayinla.py yorum`), sen yenisini sabitlersin. Yayın yasağı ya da aile talebinde
  videoyu sen telefondan kaldırırsın. Yorumları API ile kapatabilirim (`ig_yayinla.py yorumlar --kapat`).
- Günlük API yayın limiti: belgede hem 50 hem 100 geçiyor; `kontrol` komutu gerçek sayıyı gösterir (bize yeter).

### 2.8 Video barındırma: Cloudflare R2 (adım adım)
Video yayın anında R2'ye yüklenir, Meta'ya **2 saatlik imzalı** (tahmin edilemeyen, süreli) bir link verilir,
yayından sonra dosya silinir. Depo herkese açık değildir. Çıkış trafiği ücretsiz, depolama $0.015/GB-ay
(bir video ~10 MB ve birkaç dakika duruyor → pratikte 0).

1. **https://dash.cloudflare.com/sign-up** → e-posta ile ücretsiz hesap.
2. Sol menü **R2 Object Storage** → R2'yi etkinleştir. Ücretsiz kota için bile ödeme yöntemi (kart/PayPal)
   istenebilir (doğrulayamadım).
3. **Create bucket** → ad: `tarihselwojak-yayin` → konum: Automatic → **Create**. **Public access'i açma**.
4. R2 sayfasında **Manage R2 API Tokens** (ya da **API → Manage API tokens**) → **Create API token**:
   - İzin: **Object Read & Write**
   - **Apply to specific buckets only** → `tarihselwojak-yayin`
   - **Create API Token**
5. Çıkan ekrandan **Access Key ID** ve **Secret Access Key**'i al (bir kez gösterilir). **Account ID**
   aynı ekrandaki endpoint adresinde (`https://<ACCOUNT_ID>.r2.cloudflarestorage.com`) ya da panelin sağ
   kenarında yazar.
6. Bölüm 0'daki yöntemle 4 değişken ekle: `R2_ACCOUNT_ID`, `R2_ACCESS_KEY_ID`, `R2_SECRET_ACCESS_KEY`,
   `R2_BUCKET` (= `tarihselwojak-yayin`).
7. İlk denemede bu ortamdan R2'ye bağlanabildiğimi kontrol ederim. Ağ politikası engellerse ortam
   ayarlarında **Network access → Allowed domains**'e `*.r2.cloudflarestorage.com` eklenir
   ([adımlar](https://code.claude.com/docs/en/cloud-environments#network-access)).

Kaynak: [R2 fiyatları](https://developers.cloudflare.com/r2/pricing/) ·
[R2 API token](https://developers.cloudflare.com/r2/api/tokens/)

### 2.9 İlk test yayını (birlikte, bir kez)
Belgelerin net söylemediği şeyleri ilk yayında ölçeceğiz:
1. `python tools/ig_yayinla.py kontrol` → hesap ve kota.
2. Hazır örnek videoyla deneme reel: `yayinla episodes/derinkuyu --dosya ... --r2 --trial`
   (trial reel önce yalnızca takip etmeyenlere gösterilir; takipçiler rahatsız olmaz).
3. Kontrol: gönderi **çıkış yapılmış bir tarayıcıda** görünüyor mu (uygulama "Development" modunda),
   ~1.250 karakterlik hikâye yorumu kesilmeden yazıldı mı, ses ve görüntü bozulmadan işlendi mi.
4. Sorun yoksa normal yayına geçeriz.

Kaynaklar: [Instagram Login API](https://developers.facebook.com/documentation/instagram-platform/instagram-api-with-instagram-login),
[Get Started / token](https://developers.facebook.com/documentation/instagram-platform/instagram-api-with-instagram-login/get-started),
[Content Publishing](https://developers.facebook.com/documentation/instagram-platform/content-publishing),
[App Review (kendi hesap için gerekmez)](https://developers.facebook.com/documentation/instagram-platform/app-review),
[Token yenileme](https://developers.facebook.com/documentation/instagram-platform/reference/refresh_access_token).

---

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
4. **Kuruluş kimlik doğrulaması** (gerekebilir; resmi belgede net değil). İlk görselde "organization must be
   verified" hatası alırsak (araç bunu ayrıca söyler): Settings → Organization → **General** →
   **Verify Organization**. Geçerli bir kimlik (pasaport/ehliyet/kimlik kartı) ve yüz doğrulaması.
   İyi ışıkta tek seferde tamamla (tekrar denemek zor olabiliyor). Erişimin açılması ~15 dk.
   (Türk kimliğinin kabul edildiği doğrulanamadı; pasaport en güvenlisi. Takılırsa 3.2 Gemini kimlik istemiyor.)
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

---

## 4. (İsteğe bağlı) YouTube Shorts otomatik yükleme
Kanalın YouTube'u da büyüyen tarafı (verinin çoğu oradan). İstersen yükleyiciyi yazarım; senden gerekenler:
1. **https://console.cloud.google.com** → yeni proje `tarihselwojak`.
2. **APIs & Services → Library → YouTube Data API v3 → Enable**.
3. **OAuth consent screen:** External → uygulama adı ve e-posta → kapsam `youtube.upload` → kaydet →
   **Publish app** ("In production"). *"Testing"te kalırsa yenileme token'ı 7 günde düşer.* Doğrulanmamış
   uygulama uyarısı çıkar; kendi hesabın için sorun değil.
4. **Credentials → Create OAuth client ID** (Web application, yönlendirme adresi:
   `https://developers.google.com/oauthplayground`).
5. **https://developers.google.com/oauthplayground** → ⚙️ **Use your own OAuth credentials** → client ID/secret →
   kapsam `https://www.googleapis.com/auth/youtube.upload` → kanal hesabıyla izin ver →
   **Exchange authorization code for tokens** → **Refresh token**'ı al.
6. Ekle: `YT_CLIENT_ID`, `YT_CLIENT_SECRET`, `YT_REFRESH_TOKEN`.

Not: API ile yüklenen videolarda yapay zekâ içerik bildirimi (`containsSyntheticMedia`) de gönderilebiliyor.
Kaynak: [videos.insert](https://developers.google.com/youtube/v3/docs/videos/insert) ·
[OAuth yenileme token süresi](https://developers.google.com/identity/protocols/oauth2)

---
