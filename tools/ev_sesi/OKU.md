# Ev sesi motoru (`tools/ev_sesi/`)

Kanalın müziklerinin ortak sesi: Gölge'yi (`assets/music/imza_v2_golge.m4a`) yapan motorun 13.11.2026'da genişletilmiş
kopyası. Bir melodi-JSON'unu alır, FluidR3 örnekleriyle çalar ve eski klasik sesten **ölçülen** kayıt zincirinden
geçirir (250-4000 Hz bant, kısa oda, wow, tek kanala yakın stereo, hafif uğultu). Klasik sesin kendisinden hiçbir ses
kullanılmaz; yalnız ölçülen sayılar ve 1/3 oktav uzun dönem spektrum hedefi vardır.

```bash
python tools/ev_sesi/render.py parca.json cikti.wav --seed 1      # ~7 sn; -29,5 LUFS; rapor JSON'u stdout'ta
python tools/ev_sesi/master.py cikti.wav cikti.m4a                # düz kazanç: -15 LUFS, tepe <= -2 dBTP, AAC 192k
python tools/ev_sesi/ornek/uret_ornek.py                          # 25 çalışan örnek JSON (biçim için; beste değil)
```

Kurulum: `apt-get install fluidsynth fluid-soundfont-gm` (FluidR3_GM.sf2, MIT, Frank Wen) ve
`pip install pyfluidsynth soundfile scipy numpy`. İsteğe bağlı ikinci SoundFont: MuseScore_General_Full.sf2 (MIT).

## Melodi-JSON (özet; ayrıntı `render.py` başlığında, örnekler `ornek/uret_ornek.py` içinde)

- `tempo_bpm`, `beats_per_bar` (3; 2 ve 4 de çalışır, 6/8 = 2 vuruş x 3 dilim), `pickup_beats`.
- `notes`: `{bar, beat, dur_beats, midi, vel, art: "stacc"|"accent", bend: [[vuruş, sent], ...]}`.
- `chords`: `{bar, beat, dur_beats, midi: [Do4 çevresinde ses sınıfları], bass, pattern}`; motor seslendirmeyi kendi yapar.
- `accomp.pattern`: vuruş başına rol. `B` bas (um), `C` akor (pa), `H` tutulan akor, `F` beşli bas, `R` sus, `C.` kesik.
- `perc` (isteğe bağlı, aynı zincirden geçer): `{"pattern": "D . x"}`; `K` kasa, `D` davul, `S` trampet, `T` tef, `W` tahta,
  `X` çubuk; küçük harf hafif vuruş.
- `engine`: parça başına ayar. `{"profile": "m3"}` her yeni parçada açık olmalı. Sık kullanılanlar:
  `lead.layers` (çalgı katmanları: `prog`, `gain_db`, `detune`, `oct`, `kind: "struck"`), `accomp.pah_voices` (3 ya da 4),
  `accomp.oom_bright_db`, `accomp.pah_bright_db`, `accomp.pah_low_db` (um-pa-pa parlaklık karşıtlığı), `perc.level_db`,
  `chain.end_s` (bütün ses bu anda biter; varsayılan 13,74 sn).

Ezgi renkleri (hepsi aynı zincirden): varsayılan tango akordeon + armonika; tremolo armonika `[{prog 22}, {prog 22,
detune 20}]`; klarnet-müzet `[{prog 71}, {prog 71, detune 20}]`; müzik kutusu `{prog 10, kind "struck"}`; ayrıca
harmonyum 20, ıslık 78, zurna 111, trompet 59 (örneklerde).

## Kurallar

- Aynı JSON + tohum = aynı dosya. Varsayılan ayarlarla Gölge'nin JSON'u (`arastirma/imza_muzik/besteler/b1/b1-4d.json`,
  tohum 1) eski motorla aynı örnekleri verir: `python tools/ev_sesi/md5wav.py` çıktısı `92e494647a4c5058fc750c0c0c47ce77`.
  Yeni davranışlar yalnız JSON'dan açılır.
- um-pa-pa'nın "u a a" karşıtlığı parçadan parçaya değişir (ezgi 1. vuruşu ne kadar dolduruyorsa). Hedef klasik sesin
  ölçüsü: parlak vuruşlar koyu vuruştan ~3,8 dB parlak. `accomp.oom_bright_db` / `pah_bright_db` ile ayarlanır ve
  `arastirma/imza_muzik/olcum/olcum.py` ile ölçülür (`accent_uaa.contrast_db`).
- Limiter yok, doyurma yok, temiz yankı yok: bunlar sesi aileden çıkarır.
