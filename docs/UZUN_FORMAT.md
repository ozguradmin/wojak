# YouTube uzun format: karar belgesi

> Kısa reel'lerin (STIL.md) uzun, anlatımlı YouTube sürümü. Aynı konu iki biçimde çıkar: kısa sürüm Instagram
> Reels + YouTube Shorts, uzun sürüm YouTube. Short, "İlgili video" bağlantısıyla uzun videoya izleyici taşır.
> İlk örnek: Talidomit ve Türkiye (`uzun/talidomit-turkiye/`).

## 1. Neden böyle (kararlar ve gerekçeleri)

| Konu | Karar | Gerekçe |
|---|---|---|
| Süre | **8-10 dk** (hedef ~9 dk, ~1.200-1.350 kelime anlatım) | 8 dk üstü videoya ara reklam konabilir; tek bir olayın hikâyesi bu sürede şişirilmeden anlatılır; yüzü görünmeyen belgesel kanallarında izlenme süresi en verimli aralık |
| Görüntü | 1920x1080, 30 fps, H.264 yüksek profil, AAC 48 kHz | YouTube standardı |
| Ses düzeyi | **-14 LUFS**, tepe -1 dBTP | YouTube normalizasyon hedefi; kısa reel'lerdeki -29,5 değil |
| Anlatıcı | **Murat** (Cartesia sonic-3, `5a31e4fb-…`), hız 0,95 | Türkçe derin erkek anlatıcı, "tarih/gizem" türünün sesi; testte en çok vurgulu duraklama |
| İkinci ses | **Aylin** (`bb2347fe-…`) alıntılar, reklam sloganları, kadın karakterler | İsimleri en doğru okuyan kadın ses; ses değişimi dikkati tazeler |
| Yedek kadın sesler | Leyla (`fa7bfcdc-…`, ifadeli), Azra (`0f95596c-…`, resmî) | Duygusal tanıklıkta Leyla denenebilir |
| Müzik | Kendi sentezimiz (`tools/make_music.py` ailesi), anlatımın altında ~-22 dB, konuşmada otomatik kısılır | Kanalın Instagram "orijinal ses"i YouTube'da Content ID riski taşır; uzun videoda 13,75 sn'lik döngü de bıktırır |
| Efekt | Kendi sentez efektlerimiz (`assets/sfx`): geçişte whoosh, fotoğrafta deklanşör, açılışta düşük boom, balonda hafif pop | Hareketli kurgunun ritmini sesle de verir; kısa reel'deki "efekt yok" kuralı uzun formatta geçerli değil |
| Altyazı | `.srt` dosyası (YouTube'a yüklenir); ekranda yalnız vurgu kelimeleri | Tam altyazıyı YouTube kendisi gösterir; ekrana gömülü tam altyazı görseli kalabalıklaştırır |

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
7. **Bölüm kartı:** siyah zemin, bölüm numarası + başlık (kanalın Avenir yazısı), whoosh.
8. **Filigran:** `tarihselwojak` sağ altta, her karede.

## 3. Hikâye yapısı (şablon)

| Bölüm | Süre | İş |
|---|---|---|
| Soğuk açılış (kanca) | 0:00-0:40 | En çarpıcı gerçek + Türkiye sorusu; logo/giriş müziği YOK. İlk 5 sn'de merak boşluğu |
| Marka anı | ~2 sn | `tarihselwojak` imza görüntüsü (kısa) |
| 3-5 bölüm | ~1:30-2:30 her biri | Kronolojik anlatım; her bölüm küçük bir merak sorusuyla biter |
| Türkiye bölümü | ~1:30 | Hikâyenin "neden giremedi" cevabı; ihtilaflı kısımlar "anlatılana göre" diliyle |
| Ters köşe / bugün | ~1:00 | Hikâyenin beklenmedik devamı |
| Kapanış | ~0:30 | İzleyiciye soru (yoruma çağrı) + kısa versiyona / sonraki videoya yönlendirme; son 15-20 sn bitiş ekranı alanı |

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
