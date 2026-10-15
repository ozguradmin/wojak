# İş akışı şablonları (araştırma → üretim → hakemler → düzeltme)

Onaylı videoları üreten çok ajanlı akışların genelleştirilmiş, yeniden kullanılabilir hâli. Her yeni videoda istemler
baştan yazılmaz; konuya özel bilgi `args` ile verilir. Adımların insan gözüyle anlatımı: [`../ADIM_ADIM.md`](../ADIM_ADIM.md).

| Dosya | Ne üretir | Ajan sayısı (yaklaşık) |
|---|---|---|
| [`kisa_reel.js`](kisa_reel.js) | 14 sn reel: olgu + görsel avı → üretici → **2 hakem** (görsel sadakat, Türk takipçi + olgu) → düzeltme döngüsü | 3 + tur başına 3 (4 turda ~12) |
| [`uzun_video.js`](uzun_video.js) | 8-10 dk YouTube: araştırma → senaryo v1 → 2 eleştirmen → v2 → karakter/varlık + motor → üretici → **4 hakem** (izlenme, karakter/animasyon, Türkçe/olgu, teknik) → düzeltme döngüsü | 9 + tur başına 5 (6 turda ~34) |

## Çalıştırma

Workflow aracı **yalnız hesap sahibi çok ajanlı çalışmayı istediğinde** kullanılır (ör. "workflow kullan", "ultracode").
İstemediyse aynı adımlar tek tek alt ajanlarla ya da elle yürütülür; istemler yine bu dosyalardan kopyalanır.

```text
Workflow(scriptPath: "docs/is_akislari/kisa_reel.js", args: {
  id: "bolum-id",
  konu: "TOPIC: <iddia, kişiler, yıl, yer; viral kaynak varsa ekran görüntüsü yolu; neden şimdi>",
  refs: "C2kkZ8BsngB, C4V3eMFM6lF, C2FriLUM2DR",       // referans/ içindeki en yakın 3-5 orijinal
  sp: "<scratchpad>/uretim/bolum-id",                  // repoya girmeyen çalışma klasörü
  max_tur: 4,
  ozel: "<sahibin bu bölüm için notu (varsa)>"
})

Workflow(scriptPath: "docs/is_akislari/uzun_video.js", args: {
  id: "konu-id", konu: "TOPIC: ...", sp: "<scratchpad>/uzun/konu-id",
  kisa: "<scratchpad>/uretim/konu-id",                 // aynı konunun kısa araştırması (varsa)
  basla: "arastirma",                                  // ya da "uretim" / "hakem"
  max_tur: 6
})
```

- `args` diziyi/nesneyi JSON değeri olarak alır (metne çevrilmiş JSON değil).
- Oturum sınırı ya da konteyner yeniden başlaması akışı keserse: aynı oturumda `resumeFromRunId` ile devam edilir (biten
  ajanlar önbellekten döner). Döngü sınırını artırmak için `max_tur` değiştirilir; yalnız değişen/yeni çağrılar yeniden çalışır.
- Scratchpad oturuma özeldir; yeni oturumda araştırma dosyaları yoktur. Kalıcı olması gereken her şey (`episode.yaml`,
  `video.yaml`, `VARLIKLAR.md`, dersler) repoya yazılır ve commit edilir.

## Hakemlerin ortak sözleşmesi

- Hakem **dosya düzenlemez**; yalnız kendi `hakem/<tur>/<mercek>/` klasöründe çalışır.
- Dönüş şeması: `{overall, scores, fixes, blockers}`. Düzeltmeler etkiye göre sıralı, **MUST/SHOULD**, kesin değerle
  (zaman damgası, yaml anahtarı, yeni Türkçe satır).
- Çapalar: 10 = en iyi örnekten ayırt edilemez; **8 = takipçi/izleyici hiçbir tuhaflık fark etmez**; 6 = düzgün taklit;
  4 = açıkça kanal değil. Genel puan en zayıf görünen öğeyle sınırlıdır.
- Ölçmeden iddia yok: kare çıkarma (kısa: 0,5 sn; uzun: ilk dakika 1 sn, sonra 2 sn ve şüpheli anlarda 30 fps),
  1:1 yüz kırpımları, Whisper dökümü, kare farkı, loudness.
- **Durma noktası:** bütün hakemler ≥ 8 ve engel yok. Ötesindeki cila gerilemeyi kazançtan olası kılar.

## Üreticinin ortak sözleşmesi

- Önce engeller ve MUST, sonra kurala/olguya aykırı olmayan SHOULD. Öncelik: **olgu > saygı > sahibin kuralları >
  izlenme > cila**. Hakemler çelişirse orijinallerin yaptığı (kısa) ya da onaylı uzun video (uzun) kazanır.
- Önceki turun düzeltmesi geri alınmaz; hakemin önerdiği sayı kareye bakılmadan uygulanmaz.
- Kısa reel düzeltme döngüsünde `wojak/` ve `tools/` düzenlenmez (hata raporlanır); uzun videoda motor düzeltmesi
  serbest, testler geçmeli.
- Her tur sonunda rapor + "DERSLER": lider bunları `docs/OGRENILENLER.md`'ye taşır ve commit eder.
