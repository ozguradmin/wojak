# Gündem (güncel olay) oyun kitabı

Kanal sadece geçmiş olaylarla değil **güncel olaylarla** da beslenecek. Bu belge: neden, nasıl seçilir,
nasıl anlatılır, nelerden kaçınılır.

## 0. Veri ne diyor? (kanalın 25 güncel olay videosu)

Kaynak: 220 videonun YouTube verisi; olay tarihleri tek tek web'den doğrulandı (23/25). Örneklem küçük,
bulgular kesin değil yön gösterici.

- **Güncel video bir piyango bileti gibi:** Mart 2024 sonrası güncel videolar medyan **89K**, aynı dönem eski
  olaylar **53K**. 300K'yı geçme oranı güncelde **%23**, eskide **%9**.
- **Patlayanların hepsi gündemin zirvesinden 0-7 gün sonra çıktı:** Iryna Zarutska (1.42M, 14.8x), Olimpiyat
  sevimli an (770K, 16.4x), Narin (564K, 12x), Kayseri'de tekerlekli sandalyeli kızın dileği (504K, 10.7x).
  **10 günden geç yayınlanan 6 videonun hiçbiri** yerel ortalamanın 2 katına çıkamadı.
- **Hız tek başına yetmez:** 0-3 günde çıkan 10 videonun 7'si sıradan kaldı; medyan izlenmede 4-9 gün grubu
  (545K) 0-3 gün grubunu (91K) geçti. Tek net sınır: **10 gün ve üstü 0/6**. Belirleyici olan konu:
  **adı bilinen tek bir masum insan + tek bir ironik/sevimli an + herkesin gördüğü bir görüntü.**
- **Tutmayanlar:** kahramanı olmayan soyut olaylar (salgın), terör (Bondi 0.75x), suçu aileye yükleyen ya da
  tartışmalı olaylar (5 kardeş yangını, Buca), 20 gün gecikmiş yabancı haberler, 24 sn+ videolar.
- **En güçlü grup "gündem kancalı eski hikâye":** yıldönümü, yeni açılan belgeler, yeni film.
  Epstein Adası (belgeler açılırken, 2.5M), deprem yıldönümünde enkaz hikâyeleri (1.7M) → n=6, medyan 1.28M.
- **Başlık:** sadece isim/etiket ("Ata Emre Akman", "Hantavirüs olayı", "Yenidoğan Çetesi") ≈ 1.0x;
  **"kim + sıradan eylem + ters dönen son"** ("Evine giderken trende katledilen Ukraynalı kız") ≈ 1.5x ve tüm
  büyük patlamalar bu kalıpta.
- **Beğeni oranı** mutlu sonlu iyilik hikâyelerinde en yüksek (%4.5-5.2); trajedilerde %0.8-1.5.
- **Süre:** patlayanların hepsi 10-17 sn. 24 sn ve üstü hiçbir güncel video 2x'e ulaşmadı.

Gecikmeyi **olaydan değil son dalgadan** ölç: görüntünün çıkması, cesedin bulunması, iddianame, yıldönümü.
(Iryna olaydan 21 gün sonra yayınlandı ama görüntülerin yayınlanmasından 7 gün sonraydı.)


## 1. Günlük rutin (15-20 dk)

```bash
python tools/gundem.py                 # son 48 saat -> out/gundem/<tarih_saat>.md
python tools/gundem.py --saat 24 --ilk 30
python tools/gundem.py --sorgu "maden" --sorgu "göçük"   # o gün özel bir konu varsa
python tools/gundem.py --taslak 3      # rapordaki 3. olay için episodes/gundem-... taslağı
python tools/gundem.py --yasak-takip   # yayınlanmış gündem bölümleri: sonradan yayın yasağı geldi mi?
```

Akış: tarama günde 1-2 kez (sabah ve öğleden sonra) → en iyi aday hazırlanıp videoyla birlikte hesap sahibine
(diğer 2 aday kısa notta) → onay → hesap sahibi paylaşır → yayından sonra 2 hafta boyunca her gün `--yasak-takip` (yasaklar olaydan günler sonra gelebiliyor;
Narin'de kayboluştan 8 gün sonra). Yasak gelirse hesap sahibine hemen yazılır, video kaldırılır.

Rapor her olay için şunu verir: temsilî başlık, puan dökümü (uygunluk, kaç kaynak yazdı, Google Trends,
tazelik, konu dışı cezası), tür (kayıp, mucize, kahramanlık, gizem, suç, kaza, tarih, hayvan),
**⚠️ DİKKAT** işareti (çocuk istismarı, intihar, terör, okul saldırısı, yayın yasağı ihtimali),
4 haber linki ve bir açı önerisi. Ayarlar ve kaynak listesi: `data/gundem_kaynaklar.yaml`.

Bilinen sınır: aynı olay farklı kelimelerle yazıldığında 2-3 kümeye bölünebilir, nadiren iki
benzer olay birleşebilir. Rapor **karar destek** listesidir; linkleri açıp kontrol et.

Kaynaklar (2026-10-09 test, ~70 RSS ve ~60 sorgu denendi): Google News TR + Türkiye bölümü, 16 isabetli
Google News araması (`"haber alınamıyor"`, `"cansız bedeni"`, `"şüpheli ölüm"`, `"saat sonra" kurtarıldı`,
`"faili meçhul"`...), Google Trends TR, Haberler.com, Hürriyet, Sözcü, Habertürk, Cumhuriyet, TRT, NTV, Sabah,
CNN Türk, AA, BBC Türkçe, DW Türkçe. Bir taramada ~2.000 haber, ~10 sn. Tek kelimelik "kahraman", "mucize",
"gizemli", "efsane" sorguları gürültü getirdiği için kullanılmıyor (soyadı Kahraman, "mucize gıda", "efsane cuma").
T24, İHA ve DHA'nın RSS'i bu sunucudan çekilemiyor (içerikleri Google News üzerinden geliyor).

## 2. Hangi güncel olay? (seçim kriterleri)

Bir olayı yapmak için **en az 3 "evet"**, hiç "kırmızı çizgi" yok:

| Soru | Neden |
|---|---|
| Ülke çapında konuşuluyor mu? (≥10 kaynak veya Google Trends'te) | Arama ve paylaşım talebi hazır |
| İçinde net bir **insan hikâyesi** var mı? (kahraman, kurban, kayıp, kurtulan) | Wojak formatı insanı anlatır; "bina çöktü" değil "enkazdan 22 saat sonra çıkan kız" |
| Tek bir **ironik/ürpertici an** var mı? | Replik ondan doğar (**doğrulanmış** son mesaj, ilk söz, kurtarmacının sözü; uydurma "son söz" yok) |
| Gizem / mucize / fedakârlık unsuru var mı? | Altın dönemin en güçlü türleri |
| Gerçek fotoğraf/görüntü var mı? | Kanıt sahnesi |

**Kırmızı çizgiler (yapma):** yayın yasağı olan dosya · çocuk istismarı/cinsel suç ayrıntısı ·
intiharı anlatmak (yöntem, mekân) · terör saldırısının failini öne çıkarmak · resmi açıklama yokken
"cinayet" demek · siyasi/partizan konu · olaydan saatler sonra, kimlikler netleşmeden.

## 3. Hız

- Üst sınır: gündemin **son dalgasından 7 gün**. 0-3 gün tercih edilir ama şart değil: doğrulama ve hukuk
  kontrolü için 1-2 gün beklemek izlenmeyi düşürmüyor. Tek günlük haberleri (yangın, kaza) 48 saat geçtiyse yapma.
- **Kahramanlık / mucize / iyilik / tuhaf olay:** hemen (24-72 saat). Mutlu son = düşük risk, yüksek beğeni.
- **Kayıp / ölüm / suç:** önce **resmi açıklama** (valilik, emniyet, jandarma, AFAD, savcılık) bekle.
  Açık uçlu bir kayıpta yalnızca **yetişkin** ve yetkililerin/ailenin yaydığı arama duyurusu varsa bilgilendirme
  videosu (afiş, son görüldüğü yer) yapılabilir. **Çocuk kaybında ve soruşturma başlamış dosyada yapma:** yasak
  genelde birkaç gün içinde gelir ve devam videosu imkânsızlaşır (Narin). Sonuç belli olmadan "kurban" anlatımı yok.
- **Büyük felaket (deprem, çökme):** ilk saatlerde değil; kurtarma hikâyeleri netleşince
  (ör. "22 saat sonra enkazdan çıkarılan..."). Acı tazeyken mizah ve "gizem" tonu yok.
- **Takvim kancaları:** büyük olayların yıldönümlerini (6 Şubat depremi, 17 Ağustos, Soma...) önceden hazırla.

## 4. Formatın güncel olaya uyarlanması

Altın dönem formatı aynen geçerli (11-15 sn, gerçek mekân + wojak + tek replik + gerçek kanıt + sabit yorum).
Farklar:

- **Kanıt sahnesi = haber:** `type: evidence` + `banner: "SON DAKİKA: ..."` ile haber bandı ya da
  haber ekran görüntüsü. Kaynak gazete adı `label:` ile görünür olsun (şeffaflık).
- **Replik yalnızca doğrulanmış bilgiden kurgulanır.** Kişinin gerçek sözü haberlerde varsa onu kullan
  (tırnak içinde, kısaltılmış). Yoksa kurtaran, arayan ya da yetkili tarafın nötr bir cümlesi
  (*"Ses geliyor, burada biri var!"*). Kurbana uydurma "son söz" ve olmayan bir suçlama koyma.
- **Fail/şüpheli:** isim ve yüz benzerliği yok, karar kesinleşmeden "katil" yok ("şüpheli").
- **Başlık:** **[kim] + [sıradan eylem] + [ters dönen son]**, doğrulanmış bilgiden
  (*"Evine giderken trende katledilen Ukraynalı kız"*, *"10 saat aranan çocuk kamyonet kasasında uyurken bulundu"*).
  Sadece isim ya da "X olayı" yazma.
- **Sabit yorum:** kronoloji + "Resmi açıklamaya göre..." + kaynak adı + tarih.
  Gelişme olursa `episode.yaml`'da metnin en üstüne "GÜNCELLEME 12.10: ..." eklenir, `python -m wojak paket episodes/<id>`
  (teslim/<id>/metinler de güncellenir) ile yeni metin hesap sahibine gönderilir; o da Instagram açıklamasını (⋯ → Düzenle) ve YouTube'daki sabit yorumu düzenler.
- **Devam videosu:** büyük gelişmede ikinci video ("Efe'nin bulunduğu an" gibi) — seri izleyici getirir.

## 5. Yayından önce kontrol listesi

Maddelerin tamamı "evet" olmadan güncel olay yayınlanmaz. `python -m wojak check` dil denetimini otomatik yapar
(`gundem: true` bölümlerde "katil", "itiraf" gibi kelimeleri maskelenmiş hâlleriyle bile yakalar).

1. [ ] **Yayın yasağı:** RTÜK "Mahkeme Yayın Yasakları" sayfası (rtuk.gov.tr/mahkeme-yayin-yasaklari) ve
   "<olay> yayın yasağı" haber araması yapıldı; tarih-saat not edildi; yasak yok. (`tools/gundem.py` ilk adaylar için
   otomatik arar ve 🔴 işaretler — ama RTÜK sayfasından elle teyit şart.)
2. [ ] **Kaynak:** Her bilgi en az 1 resmî açıklamaya (valilik, başsavcılık, emniyet, jandarma, AFAD, bakanlık) ve
   2 bağımsız ana akım kaynağa dayanıyor. Sızıntı, "kulis", sosyal medya iddiası yok. Görüntünün tarihi doğrulandı.
3. [ ] **Masumiyet:** "Katil", "itiraf", "cani" yok (hüküm kesinleşmedikçe). Şüpheli baş harfleriyle; yüz, kelepçe,
   gözaltı fotoğrafı yok. **Şüpheliye wojak karakteri ya da korkunç yüz verilmez** — tanınabilirlik karikatürle de olur (TCK 126).
4. [ ] **Çocuk:** 18 yaş altı mağdur/şüpheli tanınamıyor (isim, yüz, okul, mahalle, ebeveyn adı yok). Konu cinsel suç değil.
5. [ ] **Mahremiyet:** Adres, plaka, kimlik no, sağlık bilgisi, özel mesaj, özel hesaptan fotoğraf yok. Aileye resmî bildirim yapılmış.
6. [ ] **Grafik içerik:** Ceset, kan, ölüm/saldırı anı, failin çektiği görüntü yok. İlk 3 saniyede şok yok.
   Kamera görüntüsü yalnızca **kurumun kendisinin yayımladığı** (emniyet, valilik, ulaşım idaresi) ve saldırı/ölüm
   anı içermeyen kısımsa; sızdırılmış görüntü hiçbir zaman (TCK 285).
   **Bağlam videonun içinde** (`top_text`: tarih, yer, "resmî açıklamalara göre").
7. [ ] **Fail:** Adı, yüzü, silahı öne çıkmıyor; övgü/haklı gösterme yok; etnik köken/bölge genellemesi yok.
8. [ ] **Afet ve kamu düzeni:** Sayılar ve tehlike bilgisi yalnızca AFAD/bakanlık/valilikten, saatiyle. "Gizleniyor",
   "yeni felaket geliyor" iddiası yok (TCK 217/A — anonim hesap cezayı artırır).
9. [ ] **Ton ve replik:** Wojak çizimi kanalın anlatım dili, ama replikte ve açıklamada espri, emoji, meme kalıbı yok
   (taze trajedide yalnızca kurtarma/mucize/iyilik açısı: GEREKENLER §5). Replik ya doğrulanmış bir alıntı ya da kimseyi suçlamayan nötr bir cümle.
   **Yakın tarihli kurbana uydurma "son söz" ya da kendi ölümünü anlatan replik verilmez** — kurtaran, arayan, yetkili
   ya da dilek-gerçekleşme yapısı kullanılır.
10. [ ] **Özgünlük ve yapay zekâ:** Haber ekran görüntüsü tek içerik değil (Instagram bunu "özgün olmayan" sayıyor);
    kurgu ve kanıt sahnesi bize ait. Fotogerçekçi yapay zekâ görseli varsa `ai_generated: true` (etiket otomatik).
11. [ ] **Yorumlar:** Gizli kelimeler (Hidden Words) filtresi açık; ilk 2 saat yorumlar izlenip isim ifşası, hakaret,
    linç, nefret içerenler siliniyor (yorumlardan hesap sahibi de sorumlu tutulabiliyor).
12. [ ] **Düzeltme ve kayıt:** Kaynak linkleri arşivlendi. Gelişme/düzeltme olursa güncel metni gönderirim, hesap sahibi
    açıklamayı/sabit yorumu düzenler; linç riskinde yorumları kapatır. Yasak ya da aile talebinde video
    telefondan kaldırılır. Yayından sonra 2 hafta `gundem.py --yasak-takip`.


## 6. Takvim önerisi

Haftada 5 video: **3 tarihsel/efsane/gündem kancalı eski hikâye + 1-2 güncel**. Güncel video yalnızca olay
Türkiye'de ulusal gündemdeyse ya da küresel viral bir görüntüsü varsa; yoksa stoktaki hazır videolardan
biri yayınlanır (`docs/KONU_HAVUZU.md`). Yıldönümleri takvime önceden işlenir.

## 7. Hukuk ve platform kuralları (özet)

> **Hukuki tavsiye değildir.** Kamuya açık mevzuat, platform kuralları ve basın kaynaklarından derlenmiş risk özetidir
> (09.10.2026). Sınırda kalan vakada (yayın yasağı, çocuk, cinsel suç, şüpheli kimliği) bir medya/ceza hukukçusuna danış.

**8 temel kural**
1. **Yayın yasağı olan olay yapılmaz.** Yasaklar genelde sosyal medyayı açıkça kapsıyor (Narin Güran kararı:
   "sosyal medya ve internet ortamında... her türlü haber"); yasak varken görüntü paylaşan kişiler gözaltına alındı
   (Kahramanmaraş, Nisan 2026). Yasaklar çoğu zaman günler içinde kalkar (Kartalkaya 1 gün, Narin 11 gün): beklemek ucuz.
2. **Yalnızca resmî açıklamalardaki bilgi.** Sızdırılmış ifade, otopsi, HTS, sızdırılmış kamera görüntüsü kullanılmaz
   (CMK 157, TCK 285: soruşturmanın gizliliği "herkes" için; 285/5: kişiyi suçlu gösteren görüntü 6 ay-2 yıl).
3. **Hüküm kesinleşmeden "katil" denmez** (Anayasa 38/4, Basın Meslek İlkeleri md. 9). Baş harf ya da karikatür,
   kişi tanınabiliyorsa korumaz (TCK 126).
4. **18 yaş altı tanınamaz; cinsel suç hiç işlenmez** (ÇKK 5395 md. 4/1-l, Basın Meslek İlkeleri md. 16, UNICEF).
5. **Afette sayı ve tehlike yalnızca resmî kaynaktan** (TCK 217/A dezenformasyon; anonim hesapta ceza yarı oranında artar;
   sosyal ağ kimliği savcılığa vermek zorunda).
6. **Failin adı, yüzü, kendi çektiği görüntü kullanılmaz; fail "efsane" gibi anlatılmaz** (TCK 215; Meta ve YouTube kuralları).
7. **Sansürlü yazım (c!nayet, k4til) hukuki riski sıfırlamaz.** Suç tanımı yazılışa değil anlama bakar; YouTube'un
   kuralları da maskenin altını okuyor. Maskeleme kanalın üslubu olarak kalabilir ama güvenlik önlemi değildir.
8. **Hata aynı gün görünür biçimde düzeltilir**; yasak gelirse ya da aile isterse içerik kaldırılır.

**Diğer riskler:** özel hayat (TCK 134, 136; KVKK 28), hakaret / ölünün hatırasına hakaret / iftira (TCK 125, 130, 267;
TMK 24-25 tazminat), suçu övme ve kin-düşmanlığa tahrik (TCK 215, 216), 5651 md. 8/A ile 4 saat içinde erişim engeli.
1.11.2026'dan itibaren 7578 sayılı Kanun: sosyal ağlar 15 yaş altına hizmet veremeyecek (kitle genç olabilir;
token gelince takipçi yaş dağılımını ölçeceğiz). 7590 sayılı Kanun'la 5651'deki yetki BTK'dan Siber Güvenlik
Başkanlığı'na geçti.

**Telif (FSEK, ayrıntılı araştırılmadı):** haber fotoğrafı ve videosu telifle korunur. Kanıt sahnesinde öncelik
resmî kurum görselleri, CC lisanslı ya da kamu malı görseller; haber görseli kullanılırsa kısa süre, kaynak adı
görünür (`label:`) ve anlatımın parçası olarak. Bir haber fotoğrafını birebir wojak'a çevirmek yerine sahneyi
kendimiz kurgularız.

**Platformlar**
- **Instagram:** ölümü/trajediyi alaya almak yasak; taze trajediyi meme tonuyla anlatmak doğrudan risk. Şiddet içerebilecek
  içerik takipçi olmayanlara önerilmeyebilir. Başkasının işinin ekran görüntüsü "özgün olmayan içerik" (30.04.2026'dan beri
  daha sıkı). Hesap Durumu ekranı düzenli kontrol edilmeli.
- **YouTube:** eğitsel/belgesel istisnası için **bağlam videonun içinde** olmalı (açıklama yetmez) → güncel olayda `top_text`.
  Hassas olaydan kâr sağlayan içerik reklam alamayabilir. "Özgün olmayan içerik" (şablon hikâyeler) para kazanamaz →
  her video kendi araştırması ve anlatısıyla farklı olmalı.
- **TikTok:** kriz anlarında doğrulanmamış bilgi "Sana Özel"e girmez; grafik görüntü 18+ ile sınırlanır.

**Etik:** kurbanın hayatını anlat, ölüm anını değil; yas/cenaze görüntüsü yok; süren soruşturmada "kim yaptı?" anketi ya da
"gizem" tonu yok; **intihar olayları hiç işlenmez** (DSÖ: yöntem/mekân verilmez).

Kaynaklar: [TCK](https://www.mevzuat.gov.tr/mevzuatmetin/1.5.5237.pdf) · [CMK](https://www.mevzuat.gov.tr/mevzuatmetin/1.5.5271.pdf) ·
[5651](https://www.mevzuat.gov.tr/mevzuatmetin/1.5.5651.pdf) · [5395 ÇKK](https://www.mevzuat.gov.tr/mevzuatmetin/1.5.5395.pdf) ·
[Basın Meslek İlkeleri](https://basinkonseyi.org.tr/basin-meslek-ilkeleri/) ·
[Narin Güran yayın yasağı](https://bianet.org/haber/narin-guran-haberlerine-yayin-yasagi-299141) ·
[Meta şiddet/grafik](https://transparency.meta.com/policies/community-standards/violent-graphic-content/) ·
[Instagram özgün içerik](https://creators.instagram.com/original-content-guidelines/) ·
[YouTube şiddet/grafik](https://support.google.com/youtube/answer/2802008) · [WHO intihar haberciliği](https://www.who.int/publications/i/item/9789240076846)

