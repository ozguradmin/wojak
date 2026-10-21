# İmza müziği v2: yarıda kalan çalışma (21.10.2026, kullanım kotası yüzünden durduruldu)

Hesap sahibi ilk üç sentezi (assets/music/imza_vals*.m4a) beğenmedi. Bu klasör ikinci, ölçüme dayalı denemenin kod ve
notlarıdır (iş klasörünün metin/kod kopyası; ses ve görseller yok). Orijinalin melodi dökümü (analiz/muzik.*) telif
riski yüzünden repoda değil; tam yedek hesap sahibinin Telegram sohbetinde (`muzik2_yedek.tar.xz`).

Durum:
- Bitti: tını/kayıt zinciri çözümlemesi (`analiz/tini.md`), ölçüm aracı (`olcum/olcum.py`, kalibrasyon ve teşhis),
  8 özgün beste (`besteler/b1`, `besteler/b2`) + yargı (`besteler/YARGI.md`): ilk üç b1-1 (8,5), b1-4d, b2-2d
  (düzeltilmiş, `besteler/DUZELTME.md`).
- Ses motorları (`motor/`): `sf` bitti (FluidR3 SoundFont, deneme melodisinde TIMBRE 70,4; reddedilen denemeler 23-27).
  `spektral` ve `hibrit` yarıda kaldı (hibrit dışarıdan bir akordeon örnek paketi kullanıyor: lisansı kullanmadan önce
  doğrulanmalı; paket repoda yok).
- Sıradaki adım: `wf_tasarim.js` ile her motor üç melodiyi işler, ses ve müzik eleştirmenleri puanlar; en iyiler
  düzeltilir, `tools/imza_muzik.py` yeniden yazılır, yeni dosyalar assets/music/'e girer. Yollar iş klasörüne göredir
  (SP = scratchpad/muzik2); yeni oturumda bu klasör SP olarak kopyalanıp orijinal ses `assets/music/ozel/` altına konur.
