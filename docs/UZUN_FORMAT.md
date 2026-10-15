# YouTube uzun format: karar belgesi

> Kısa reel'lerin (STIL.md) uzun, anlatımlı YouTube sürümü. Aynı konu iki biçimde çıkar: kısa sürüm Instagram
> Reels + YouTube Shorts, uzun sürüm YouTube. Short, "İlgili video" bağlantısıyla uzun videoya izleyici taşır.
> İlk örnek: Talidomit ve Türkiye (`uzun/talidomit-turkiye/`, 10:33; hesap sahibi 15.10: "baya iyi olmuş beğendim").
> Adım adım üretim: [`ADIM_ADIM.md`](ADIM_ADIM.md) §4. Yayın takvimi: [`YAYIN_PLANI.md`](YAYIN_PLANI.md).

## 1. Neden böyle (kararlar ve gerekçeleri)

| Konu | Karar | Gerekçe |
|---|---|---|
| Süre | **8-10 dk** (hedef ~9 dk, ~1.200-1.350 kelime anlatım) | 8 dk üstü videoya ara reklam konabilir; tek bir olayın hikâyesi bu sürede şişirilmeden anlatılır; yüzü görünmeyen belgesel kanallarında izlenme süresi en verimli aralık |
| Görüntü | 1920x1080, 30 fps, H.264 yüksek profil, AAC 48 kHz | YouTube standardı |
| Ses düzeyi | **-14 LUFS**, tepe -1 dBTP | YouTube normalizasyon hedefi; kısa reel'lerdeki -29,5 değil |
| Ses sağlayıcısı | **ElevenLabs'e geçilecek** (hesap sahibi 13.10 Cartesia sesini beğenmedi; başvuru sonucu ve API anahtarı bekleniyor). Seçim ölçerek, son kararı hesap sahibi verir (YAYIN_PLANI §4) | Aşağıdaki Cartesia satırları ilk videonun kaydıdır |
| Anlatıcı | **Murat** (Cartesia sonic-3, `5a31e4fb-…`), hız 0,95 | Türkçe derin erkek anlatıcı, "tarih/gizem" türünün sesi; testte en çok vurgulu duraklama |
| İkinci ses | **Aylin** (`bb2347fe-…`) alıntılar, reklam sloganları, kadın karakterler | İsimleri en doğru okuyan kadın ses; ses değişimi dikkati tazeler |
| Yedek kadın sesler | Leyla (`fa7bfcdc-…`, ifadeli), Azra (`0f95596c-…`, resmî) | Duygusal tanıklıkta Leyla denenebilir |
| Müzik | Kendi sentezimiz (`tools/make_music.py` ailesi), anlatımın altında ~-22 dB, konuşmada otomatik kısılır | Kanalın Instagram "orijinal ses"i YouTube'da Content ID riski taşır; uzun videoda 13,75 sn'lik döngü de bıktırır |
| Efekt | Kendi sentez efektlerimiz (`assets/sfx`): geçişte whoosh, fotoğrafta deklanşör, açılışta düşük boom, balonda hafif pop | Hareketli kurgunun ritmini sesle de verir; kısa reel'deki "efekt yok" kuralı uzun formatta geçerli değil |
| Altyazı | `.srt` dosyası (YouTube'a yüklenir; alıntılar italik); ekranda yalnız vurgu kelimeleri | Tam altyazıyı YouTube kendisi gösterir; ekrana gömülü tam altyazı görseli kalabalıklaştırır |

## 2. Görsel dil: hareket şart

Kısa reel'de her sahne durağandı (altın dönem ölçümü). Uzun formatta tam tersi: **izleyici en geç 4-6 sn'de bir
yeni bir hareket ya da görüntü görmeli.** Kullanılan yapı taşları:

1. **Wojak sahnesi:** gerçek arka plan fotoğrafı üzerinde yavaş kamera (Ken Burns: %3-8 yakınlaşma/kaydırma),
   karakterler kenardan kayarak ve hafif sekerek girer (ease-out + küçük taşma), konuşurken nefes alır gibi hafifçe
   büyüyüp küçülür, duygu anında yüz varyantına geçer (kısa sıkışma efektiyle). Sahne içi replikler konuşma balonu.
   Karakter kuralları kısa formatla aynı: düz MS-Paint wojak, solda sağa / sağda sola bakar.
2. **Arşiv fotoğrafı / belge:** beyaz kenarlı, hafif eğik, gölgeli "masaya konmuş fotoğraf"; kayarak girer, yavaşça
   yakınlaşır; sol altta yer-tarih etiketi daktilo efektiyle yazılır.
3. **Manşet / belge vurgusu:** gazete ya da reklam görseli, önemli kelimenin üstünden fosforlu kalem geçer.
4. **Harita:** sade dünya/Avrupa haritası; ilacın satıldığı ülkeler sırayla yanar, Türkiye en sonda yeşil
   "giremedi" etiketiyle ayrışır.
5. **Sayaç ve zaman çizgisi:** büyük sayı sayarak yükselir (10.000+), yıl göstergesi 1957 → 1961 akar.
6. **İsim etiketi (lower third):** kişi ilk göründüğünde adı ve unvanı.
7. **Bölüm kartı:** siyah zemin, bölüm numarası + başlık (kanalın Avenir yazısı), whoosh. Talidomit uzun videosundan
   beri tercih **bindirme** kart: son kare donar ve kararır, kart 1,2 sn üstünde açılır; siyah ekran yok, müzik
   kesilmez (`kart_bindirme`, UZUN_MOTOR.md §3).
8. **Filigran (karar 15.10.2026):** ilk videoda `tarihselwojak` sağ altta her karedeydi. **ElevenLabs ile yeniden
   seslendirmeden itibaren uzun videoda gömülü filigran yok** (`filigran: false`). Gerekçe: büyük belgesel kanalları
   gömülü yazı kullanmıyor; kanalı imza anı, karakterler ve kapanış tanıtıyor; sağ alt köşe YouTube'un ilerleme çubuğu,
   altyazı ve bitiş ekranı öğeleriyle yarışıyor ve 8 turda en az üç çakışma çıkardı (damga, temsilci kravatı). Yerine
   YouTube Studio → Özelleştirme → Markalama → **Video filigranı** (tıklanınca abone olunur). Kısa reel'lerde filigran
   **kalır**: altın dönem stilinin parçası (STIL §11) ve başka sayfalarda yeniden paylaşılınca kaynağı gösterir.
9. **Yüz boyu (kural 15.10.2026):** karakterin ekrandaki **etkin boyu = `boy` × kamera `zoom` (en büyük) × `yakin`**
   kare yüksekliğinin **≤ 0,80**'i; rahat aralık 0,55-0,75. Bilinçli dramatik yakın plan en çok 0,88, videoda 1-2 kez,
   baş tepesi ve çene kadrajda. Hazır kıyafetli v2 çizimler baş-omuz kesimli olduğundan baş PNG'nin büyük kısmıdır: eski
   tam boy çizimlerle aynı `boy` çok daha büyük yüz verir. Hesap sahibi ilk videoda yüzlerin bazı sahnelerde fazla büyük
   ve altta kesik olduğunu fark etti: dört sahnede etkin boy 0,87-0,96'ydı (Ankara doruğu: `boy` 0,74 × zoom 1,3 = 0,96).
   Düzeltme ve `kontrol` uyarısı ElevenLabs turunda (YAYIN_PLANI §4).

## 3. Hikâye yapısı (şablon)

| Bölüm | Süre | İş |
|---|---|---|
| Soğuk açılış (kanca) | 0:00-0:40 | En çarpıcı gerçek + Türkiye sorusu; logo/giriş müziği YOK. İlk 5 sn'de merak boşluğu |
| Marka anı | ~2 sn | `tarihselwojak` imza görüntüsü (kısa): `marka` sahnesi ya da ilk bölüm kartında `kart_marka` |
| 3-5 bölüm | ~1:30-2:30 her biri | Kronolojik anlatım; her bölüm küçük bir merak sorusuyla biter |
| Türkiye bölümü | ~1:30 | Hikâyenin "neden giremedi" cevabı; ihtilaflı kısımlar "anlatılana göre" diliyle |
| Ters köşe / bugün | ~1:00 | Hikâyenin beklenmedik devamı |
| Kapanış | ~0:30 | Hikâyenin açık sorusu A/B/C seçenekleriyle (`kapanis` sahnesi: kartlar tepki verir, imleç abone/zil/beğen, yorum balonu; sabit yorum aynı soru). **Video kutusu yok** (hesap sahibi 13.10; kanalda yeterli uzun video olunca yeniden düşünülür). Son 5-20 sn YouTube'un kendi bitiş ekranı öğelerine uygun kalır |

Kurallar: anlatıcı dili sade ve konuşur gibi; cümleler kısa; her bölüm sonunda "ama asıl şaşırtıcı olan…" türünden
köprü; sayılar ve isimler araştırma notundan; tartışmalı her bilgi yumuşatılmış dille; mağdurlara saygı (engellilikle
alay yok, sansasyonel çocuk fotoğrafı yok).

## 4. Teslim paketi (uzun video)

`teslim/<id>-uzun/`: video, küçük resim (1280x720, 2-3 alternatif: YouTube "Test ve karşılaştır" için), başlık
alternatifleri, açıklama (bölüm zaman damgaları + kaynaklar + görsel atıfları + Short bağlantısı yeri), etiketler,
sabit yorum, `.srt` altyazı, yükleme kontrol listesi. Short paketinin açıklamasına "Uzun hali kanalda" satırı ve
Shorts'ta **İlgili video** olarak uzun videoyu bağlama talimatı eklenir.

## 5. Gizlilik ve lisans

- `CARTESIA_API_KEY` yalnız `~/.config/wojak/secrets.env` içinde (repo dışı, izin 600); kalıcılık için ortam
  değişkeni olarak eklenmeli (GEREKENLER.md §1'deki gibi).
- Telifli arşiv görselleri `img/telifli/` altında (repoya girmez); hesap sahibi lisans kararını verir.
- Videolar repoya girmez, sohbetten teslim edilir.
