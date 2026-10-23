"""Uzun format motoru testleri.

    python -m pytest tests/ -q        # pytest varsa
    python tests/test_uzun.py         # pytest olmadan (düz assert)
"""

from __future__ import annotations

import math
import shutil
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from wojak import config  # noqa: E402
from wojak.uzun import altyazi, easing as E, paket, spec, tts, zaman  # noqa: E402

KOK = config.ROOT


def _video(bolumler, **ek):
    d = {"id": "test", "baslik": "Test", "bolumler": bolumler, **ek}
    return spec.yukle_sozluk(d, KOK)


def _sureler(v, sureler):
    it = iter(sureler)
    for s in v.sahneler:
        for st in s.satirlar:
            st.sure = next(it)


def _hata_bekle(fn, *parca):
    try:
        fn()
    except spec.SpecHatasi as e:
        for p in parca:
            assert p in str(e), (p, str(e))
        return
    raise AssertionError("SpecHatasi bekleniyordu")


# ---------------------------------------------------------------- easing

def test_easing_uclar():
    for ad, f in E.EGRILER.items():
        assert abs(f(0.0)) < 1e-9, ad
        assert abs(f(1.0) - 1.0) < 1e-9, ad
        assert abs(f(-3.0) - f(0.0)) < 1e-9 and abs(f(5.0) - f(1.0)) < 1e-9, ad  # kırpılır


def test_easing_monoton_ve_tasma():
    xs = [i / 200 for i in range(201)]
    for f in (E.out_cubic, E.in_cubic, E.in_out_cubic, E.in_out_sine):
        ys = [f(x) for x in xs]
        assert all(b >= a - 1e-12 for a, b in zip(ys, ys[1:]))
    # out_back: küçük taşma, sonra 1'e oturur
    tepe = max(E.out_back(x, 1.2) for x in xs)
    assert 1.03 < tepe < 1.08, tepe
    assert abs(tepe - 1 - E.back_tasma(1.2)) < 2e-3
    assert abs(E.back_tasma(1.70158) - 0.1) < 2e-3      # klasik "back": %10
    assert E.tumsek(0) == 0 and abs(E.tumsek(0.5) - 1) < 1e-9 and abs(E.tumsek(1)) < 1e-9
    assert E.ilerleme(1.5, 1.0, 1.0) == 0.5 and E.ilerleme(0.0, 1.0, 1.0) == 0.0


# ---------------------------------------------------------------- spesifikasyon

def test_spec_yukleme_ve_varsayilanlar():
    v = _video([
        {"baslik": "Giriş", "sahneler": [
            {"tip": "metin", "metin": "x", "satirlar": ["Anlatıcı cümlesi.", {"ses": "aylin", "metin": "Alıntı.",
                                                                               "duygu": "content"}]}]},
        {"baslik": "İkinci", "sahneler": [{"tip": "sayac", "deger": 10000, "satirlar": ["Bir."]}]},
        {"baslik": "Üçüncü", "kart": False, "sahneler": [{"tip": "liste", "noktalar": [{"tarih": "1"}, {"tarih": "2"}]}]},
    ])
    assert v.anlatici_ses == "murat" and abs(v.anlatici_hiz - 0.95) < 1e-9
    assert v.sesler["aylin"].startswith("bb2347fe")
    s = v.sahneler
    # ilk bölümde kart yok (varsayılan), ikincide var, üçüncüde kapalı
    assert [x.tip for x in s] == ["metin", "bolum_karti", "sayac", "zaman_cizelgesi"]
    assert s[1].p["numara"] == 1 and s[1].p["baslik"] == "İkinci"
    assert s[0].satirlar[0].ses == "murat" and s[0].satirlar[1].ses == "aylin"
    assert s[0].satirlar[1].duygu == "content"
    assert s[0].gecis == "kesme"


def test_spec_hatalari():
    _hata_bekle(lambda: _video([{"baslik": "a", "sahneler": [{"tip": "uzay"}]}]), "uzay")
    _hata_bekle(lambda: _video([{"baslik": "a", "sahneler": [{"tip": "metin", "metin": "x", "renkk": 1}]}]),
                "bilinmeyen", "renkk")
    _hata_bekle(lambda: _video([{"baslik": "a", "sahneler": [{"tip": "metin", "metin": "x", "satirlar": ["a"],
                                                               "olaylar": [{"tip": "ceviri", "satir": 3}]}]}]),
                "satir 3")
    _hata_bekle(lambda: _video([{"baslik": "a", "sahneler": [{"tip": "metin", "metin": "x",
                                                               "satirlar": [{"ses": "hakan", "metin": "a"}]}]}]),
                "hakan")
    _hata_bekle(lambda: _video([{"baslik": "a", "sahneler": [{"tip": "metin", "metin": "x",
                                                               "olaylar": [{"tip": "yuz", "karakter": "a",
                                                                            "gorsel": "x.png"}]}]}]),
                "wojak")
    _hata_bekle(lambda: _video([{"baslik": "a", "sahneler": [{"tip": "sayac"}]}]), "deger")


def test_telaffuz_yalniz_transkriptte():
    v = _video([{"baslik": "a", "sahneler": [{"tip": "metin", "metin": "x", "satirlar": [
        "Contergan'ın adı Contergan.<break time=\"400ms\"/> Contergani değil."]}]}],
        telaffuz={"Contergan": "Kontergan"})
    st = v.sahneler[0].satirlar[0]
    tr = v.transkript(st)
    assert tr.startswith("Kontergan'ın adı Kontergan.") and "<break time=\"400ms\"/>" in tr
    assert "Contergani" in tr                      # kelime sınırı: başka kelimenin içine dokunmaz
    assert st.altyazi == "Contergan'ın adı Contergan. Contergani değil."   # altyazıda yazım + etiket yok
    assert abs(spec.ara_sureleri(st.metin) - 0.4) < 1e-9


# ---------------------------------------------------------------- zamanlama

def test_sahne_zamanlama():
    v = _video([{"baslik": "a", "sahneler": [
        {"tip": "metin", "metin": "x", "satirlar": ["bir", "iki", {"metin": "üç", "once": 1.0, "sonra": 0.2}],
         "olaylar": [{"tip": "ceviri", "satir": 2, "an": "son", "ofset": -0.2}, {"tip": "basla", "t": 0.5}],
         "sfx": [{"ad": "pop", "satir": 3, "ofset": 0.1}]},
        {"tip": "bolum_karti", "baslik": "kart"},
        {"tip": "sayac", "deger": 5, "satirlar": ["kısa"], "min_sure": 4.0},
    ]}], zamanlama={"bas": 0.4, "ara": 0.3, "son": 0.5})
    _sureler(v, [2.0, 3.0, 1.0, 0.5])
    z = zaman.hesapla(v)
    s0, s1, s2 = z.sahneler
    assert [round(x.t0, 3) for x in s0.satirlar] == [0.4, 2.7, 6.7]
    # 0.4 + 2 + 0.3 + 3 + 1.0 + 1 + 0.2 + 0.5 = 8.4 sn = 252 kare
    assert s0.n_kare == 252 and abs(s0.sure_hesap - 8.4) < 1e-9
    assert abs(s0.olaylar[0].zaman - (2.7 + 3.0 - 0.2)) < 1e-9
    assert abs(s0.olaylar[1].zaman - 0.5) < 1e-9
    assert abs(s0.sfx[0].zaman - 6.8) < 1e-9
    assert s1.n_kare == round(v.zamanlama["kart"] * 30)
    assert s2.n_kare == 120                    # min_sure 4.0 > 0.4 + 0.5 + 0.5
    assert s1.bas_kare == 252 and s2.bas_kare == 252 + s1.n_kare
    assert z.toplam_kare == s0.n_kare + s1.n_kare + s2.n_kare
    # mutlak satır zamanları = sahne başı (kare sınırı) + yerel
    sz = z.satirlar()
    assert abs(sz[3].bas - (s2.bas_kare / 30 + 0.4)) < 1e-9 and abs(sz[3].son - sz[3].bas - 0.5) < 1e-9
    assert z.sahne_at(8.39)[0] is s0 and z.sahne_at(8.41)[0] is s1


def test_kare_izgarasi_ve_tahmin():
    v = _video([{"baslik": "a", "sahneler": [{"tip": "metin", "metin": "x", "satirlar": ["Bir cümle burada."]}
                                             for _ in range(5)]}])
    z = zaman.hesapla(v, tahmin=True)
    assert all(st.tahmini and st.sure > 0.5 for s in z.sahneler for st in s.satirlar)
    toplam = 0
    for s in z.sahneler:
        assert s.bas_kare == toplam and abs(s.sure_hesap * 30 - s.n_kare) < 1e-9
        toplam += s.n_kare
    assert z.toplam_kare == toplam
    assert zaman.tahmini_sure("a" * 145, 1.0) == round(145 / zaman.TR_HIZ + 0.2, 3)


# ---------------------------------------------------------------- altyazı

def _altyazi_video():
    uzun = ("Meslektaşlarının anlattığına göre farmakolog Şükrü Kaymakçalan, deneyleri yetersiz bulup "
            "olur vermedi; Bakanlık da bu görüşe uydu ve ilaca ruhsat vermedi. Türkiye böylece kurtuldu.")
    v = _video([{"baslik": "a", "sahneler": [{"tip": "metin", "metin": "x", "satirlar": [
        "Kısa.", uzun, "Ağır doğum kusurları: İğne, ıhlamur, şövalye, çöp, Ünye, Ödemiş."]}]}])
    _sureler(v, [0.6, 9.5, 4.0])
    return zaman.hesapla(v)


def test_srt_kurallari():
    z = _altyazi_video()
    ps = altyazi.parcalar(z)
    assert altyazi.denetle(ps) == [], altyazi.denetle(ps)
    assert len(ps) >= 4
    for p in ps:
        assert all(len(s) <= 42 for s in p.metin.split("\n")) and p.metin.count("\n") <= 1
        assert p.son - p.bas >= 1.0 - 1e-9
    for a, b in zip(ps, ps[1:]):
        assert b.bas >= a.son
    metin = altyazi.srt(ps)
    assert "İğne, ıhlamur, şövalye, çöp, Ünye, Ödemiş" in metin.replace("\n", " ")
    assert metin.startswith("1\n00:00:00,350 --> ")
    assert altyazi.zaman_damgasi(3725.5) == "01:02:05,500"


def test_srt_dosya_utf8():
    import tempfile
    z = _altyazi_video()
    with tempfile.TemporaryDirectory() as d:
        p = altyazi.yaz(z, Path(d) / "x.srt")
        b = p.read_bytes()
    assert not b.startswith(b"\xef\xbb\xbf")
    assert "Kaymakçalan" in b.decode("utf-8")


def test_iki_satir():
    assert altyazi.iki_satir("kısa") == "kısa"
    t = altyazi.iki_satir("bir iki üç dört beş altı yedi sekiz dokuz on on bir on iki on üç")
    a, b = t.split("\n")
    assert len(a) <= 42 and len(b) <= 42 and abs(len(a) - len(b)) < 12
    assert altyazi.iki_satir("x" * 50) is None


# ---------------------------------------------------------------- bölüm zaman damgaları

def test_bolum_damgalari():
    v = _video([
        {"baslik": "Giriş", "sahneler": [{"tip": "metin", "metin": "x", "sure": 41.7}]},
        {"baslik": "İkinci", "youtube": "İkinci bölüm", "sahneler": [{"tip": "metin", "metin": "x", "sure": 100}]},
        {"baslik": "Üçüncü", "sahneler": [{"tip": "metin", "metin": "x", "sure": 3725}]},
    ])
    z = zaman.hesapla(v)
    d = paket.bolum_damgalari(z)
    assert d[0] == (0, "Giriş")
    assert d[1] == (42, "İkinci bölüm")              # kart dahil bölüm başı, YUKARI yuvarlanır (damga kartın içinde)
    import math
    assert d[2][0] == math.ceil(41.7 + v.zamanlama["kart"] + 100 - 1e-3)   # 3. bölümün kartı kendi başında
    assert paket.yukari(181.0000001) == 181 and paket.yukari(180.9) == 181
    assert paket.bolum_metni(d).splitlines()[0] == "0:00 Giriş"
    assert paket.bolum_denetle(d, z.sure) == []
    assert zaman.zaman_str(3725) == "1:02:05" and zaman.zaman_str(65) == "1:05"
    u = paket.bolum_denetle([(0, "a"), (5, "b")], 30)
    assert any("en az 3" in x for x in u) and any("10 sn" in x for x in u)
    assert any("0:00" in x for x in paket.bolum_denetle([(3, "a"), (20, "b"), (40, "c")], 60))


# ---------------------------------------------------------------- TTS yardımcıları

def test_tts_kirpma_ve_anahtar():
    sr = 44100
    t = np.arange(int(sr * 1.0)) / sr
    ses = (0.3 * np.sin(2 * np.pi * 220 * t)).astype(np.float32)
    x = np.concatenate([np.zeros(int(0.5 * sr), np.float32), ses, np.zeros(int(0.8 * sr), np.float32)])
    y, a, b = tts.sessizlik_kirp(x, sr)
    k = tts.KIRPMA
    assert abs(a - (0.5 - k["on_pay"])) < 0.012 and abs(b - (0.8 - k["arka_pay"])) < 0.012
    assert abs(len(y) / sr - (1.0 + k["on_pay"] + k["arka_pay"])) < 0.02
    assert abs(y[0]) < 1e-6 and abs(y[-1]) < 1e-3     # yumuşak giriş/çıkış
    k1 = tts.anahtar("sonic-3", "id", "metin", 0.95, None, "tr")
    assert k1 == tts.anahtar("sonic-3", "id", "metin", 0.95, None, "tr")
    assert k1 != tts.anahtar("sonic-3", "id", "metin", 1.0, None, "tr")
    assert k1 != tts.anahtar("sonic-3", "id", "metin", 0.95, "sad", "tr")
    assert k1 != tts.anahtar("sonic-3", "id", "metin", 0.95, None, "tr", deneme=1)


def test_istek_govdesi_ve_isim_denetimi():
    v = _video([{"baslik": "a", "sahneler": [{"tip": "metin", "metin": "x", "satirlar": [
        {"ses": "aylin", "metin": "Contergan güvenli.", "duygu": "content", "hiz": 1.1}]}]}],
        telaffuz={"Contergan": "Kontergan"}, qa={"isimler": ["Contergan"]})
    g = tts.istek_govdesi(v, v.sahneler[0].satirlar[0])
    assert g["model_id"] == "sonic-3" and g["language"] == "tr"
    assert g["voice"] == {"mode": "id", "id": spec.VARSAYILAN_SESLER["aylin"]}
    assert g["output_format"] == {"container": "wav", "encoding": "pcm_s16le", "sample_rate": 44100}
    assert g["generation_config"] == {"speed": 1.1, "emotion": "content"}
    assert g["transcript"] == "Kontergan güvenli."
    assert tts.satirdaki_isimler(v, v.sahneler[0].satirlar[0]) == ["Contergan"]
    assert tts.isim_duyuldu_mu("Kaymakçalan", "farmakolog Şükrü Kaymakçalan'ın görüşü")[0]
    assert tts.isim_duyuldu_mu("Süreyya Tahsin Aygün", "veteriner hekim süreyya tahsin aygün de")[0]
    assert tts.isim_duyuldu_mu("Lenz", "doktoru Vido Kindlentz alarm", "Lents")[0]
    assert not tts.isim_duyuldu_mu("Kaymakçalan", "farmakolog bir hoca görüş verdi")[0]


# ---------------------------------------------------------------- harita, müzik, render (küçük entegrasyon)

def test_harita_projeksiyon():
    from wojak.uzun.harita import HaritaCizer
    h = HaritaCizer("avrupa", 480, 270, "110m")
    x, y = h.etiket_noktasi("TUR")
    assert 0 < x < 480 and 0 < y < 270
    xd, yd = h.etiket_noktasi("DEU")
    assert xd < x and yd < y                     # Almanya Türkiye'nin kuzeybatısında
    m, bbox = h.maske("TUR")
    assert m.size == (bbox[2] - bbox[0], bbox[3] - bbox[1])


def test_harita_dunya_kesim_boylami_serit_cizmez():
    # dünya haritası merkez 10° iken kesim boylamı -170°: Çukotka ve St. Lawrence adası bu boylamı aşar;
    # sarılınca haritayı boydan boya geçen ince bir şerit çiziliyordu
    from wojak.uzun.harita import HaritaCizer
    h = HaritaCizer("dunya", 960, 540, "50m")
    for kod in ("RUS", "USA"):
        for poly in h._poligonlar(kod, 1):
            xs = [p[0] for p in poly]
            assert max(xs) - min(xs) < 0.5 * 960, kod


def test_muzik_uretimi():
    from wojak.uzun import muzik
    x = muzik.uret(4.0, tohum=3)
    assert x.shape == (4 * muzik.SR, 2) and np.isfinite(x).all() and np.abs(x).max() <= 0.95
    y = muzik.uret(4.0, tohum=3)
    assert np.array_equal(x, y)                  # aynı tohum = aynı parça


def test_mini_render_senkron():
    """Küçük çözünürlükte uçtan uca: kare sayısı ve ses/görüntü senkronu."""
    from wojak.uzun import render, ses
    v = spec.yukle_sozluk({"id": "test-uzun", "baslik": "t", "muzik": {"uret": True, "tohum": 1},
                           "bolumler": [{"baslik": "a", "sahneler": [
                               {"tip": "metin", "metin": "deneme yazısı", "ceviri": "test", "sure": 1.0},
                               {"tip": "sayac", "deger": 100, "sure": 1.2, "gecis": "gecis"},
                               {"tip": "zaman_cizelgesi", "sure": 1.0, "gecis": "kaydir",
                                "noktalar": [{"tarih": "1957"}, {"tarih": "1961"}]}]}]}, KOK)
    z = zaman.hesapla(v)
    od = v.cikti
    try:
        rb = render.video_render(v, z, od / "sessiz.mp4", 320, 180, isci=1, onizleme=True, log=lambda *a: None)
        assert rb["cizilen_kare"] == z.toplam_kare == 96
        b = ses.miks(v, z, od / "ses", log=lambda *a: None)
        assert b["ornek"] == z.toplam_kare * 1600
        out = render.birlestir(od / "sessiz.mp4", Path(b["ses"]), od / "t.mp4")
        d = render.dogrula(out, z.toplam_kare)
        assert d["kare_ok"] and d["senkron_ok"], d
    finally:
        shutil.rmtree(od, ignore_errors=True)


# ---------------------------------------------------------------- 2. tur: yeni sahne tipleri ve olaylar

LAB = "episodes/talidomit-turkiye/img/arka_lille_lab_kaynak.jpg"
KUTU = "uzun/demo/img/contergan_kutu.jpg"
TEMSILCI = "episodes/talidomit-turkiye/chars/temsilci_gulumsuyor.png"
VETERINER = "episodes/talidomit-turkiye/chars/veteriner.png"


def _yeni_tipler_video():
    """Bütün 2. tur özelliklerini kullanan küçük video (sesler tahmini)."""
    return _video([
        {"baslik": "Açılış", "sahneler": [
            {"tip": "wojak", "arka": LAB, "muzik_db": -8,
             "karakterler": [{"id": "a", "gorsel": TEMSILCI, "taraf": "sol"},
                             {"id": "b", "gorsel": VETERINER, "taraf": "sag"},
                             {"id": "c", "gorsel": "assets/kit/klasik/sakin.png", "x": 0.52, "derinlik": 0.7}],
             "satirlar": [{"metin": "Bu ilaç tamamen güvenli.", "konusan": "a"},
                          {"metin": "Önce embriyoda deneyelim.", "balon": "b"}],
             "olaylar": [{"tip": "damga", "metin": "RUHSAT VERİLMEDİ", "satir": 2, "ofset": 0.3}],
             "kose": {"metin": "GÜN {} / 12", "deger": 0}},
            {"tip": "marka", "bindirme": True}]},
        {"baslik": "Bir", "kart_marka": True, "sahneler": [
            {"tip": "sayac", "deger": [60, 0], "etiket": "gün", "satirlar": ["Altmış gün."],
             "olaylar": [{"tip": "deger", "deger": 17, "etiket": "bebek", "renk": "kirmizi", "satir": 1, "an": "son"},
                         {"tip": "kose", "deger": 5, "t": 0.5}]},
            {"tip": "metin", "metin": "anne karnında", "yazim": "daktilo", "zemin": "kagit",
             "satirlar": ["Anne karnında."], "olaylar": [{"tip": "ustunu_ciz", "satir": 1, "an": "son"}]},
            {"tip": "zaman_cizelgesi", "zemin": "kagit", "arka": KUTU, "baslik": "On iki gün",
             "noktalar": [{"tarih": "15 Kasım"}, {"tarih": "27 Kasım"}],
             "kose": {"deger": 1961, "yil": True, "konum": "sol_ust"},
             "olaylar": [{"tip": "kose", "deger": "????", "takili": True, "t": 0.4}], "satirlar": ["On iki gün."]}]},
        {"baslik": "İki", "sahneler": [
            {"tip": "bolunmus", "sol": {"gorsel": KUTU, "etiket": "BATI ALMANYA"},
             "sag": {"metin": "Ruhsat şart", "ceviri": "1928", "zemin": "kagit", "baslik": "TÜRKİYE"},
             "satirlar": ["Batı Almanya'da kayıt yetiyor."],
             "olaylar": [{"tip": "panel", "taraf": "sag", "t": 0.5}, {"tip": "soluk", "taraf": "sol", "t": 1.2},
                         {"tip": "buyut", "taraf": "sag", "satir": 1, "an": "son"}]},
            {"tip": "izgara", "n": 400, "say": True, "ust": "dünya", "etiket": "bebek", "dolum": 1.0,
             "satirlar": ["On binden fazla bebek."],
             "olaylar": [{"tip": "basla", "t": 0.2}, {"tip": "sondur", "oran": 0.4, "t": 1.5, "sure": 0.5,
                                                      "etiket": "≈ %40"}]},
            {"tip": "pano", "baslik": "Elimizdekiler", "kose": {"metin": "BELGE: {}", "deger": 0},
             "kartlar": [{"id": "m", "metin": "BAKANLIK", "stil": "merkez"}, {"id": "k", "metin": "KAYMAKÇALAN",
                                                                             "alt": "tanıklık"},
                         {"id": "y", "metin": "YIL ?", "stil": "bos"}],
             "ipler": [["k", "m"]], "satirlar": ["Elimizdekiler."],
             "olaylar": [{"tip": "kart", "id": "m", "t": 0.2}, {"tip": "kart", "id": "k", "t": 0.6},
                         {"tip": "damga", "kart": "k", "metin": "BELGE YOK", "t": 1.2}]},
            {"tip": "bitis", "arka": KUTU, "satirlar": ["Görüşmek üzere."], "sure": 15}]},
    ], kart_bindirme=True)


def test_yeni_tipler_spec_ve_sureler():
    v = _yeni_tipler_video()
    z = zaman.hesapla(v, tahmin=True)
    tipler = [s.tip for s in z.sahneler]
    assert tipler == ["wojak", "marka", "bolum_karti", "sayac", "metin", "zaman_cizelgesi", "bolum_karti",
                      "bolunmus", "izgara", "pano", "bitis"], tipler
    marka, kart = z.sahneler[1], z.sahneler[2]
    assert abs(marka.sure_hesap - 1.8) < 1e-9 and not marka.filigran      # imza: filigran kendisi
    assert kart.p["bindirme"] and kart.p["marka"] and abs(kart.sure_hesap - 1.2) < 1e-9
    assert abs(z.sahneler[-1].sure_hesap - 15.0) < 1e-9                    # bitiş ekranı en az 15 sn
    assert z.sahneler[0].muzik_db == -8 and z.sahneler[0].kose["metin"] == "GÜN {} / 12"
    assert z.sahneler[0].satirlar[0].konusan == "a"
    assert z.sahneler[0].p["karakterler"][2]["derinlik"] == 0.7
    assert z.sahneler[9].p["ipler"] == [["k", "m"]]
    assert paket.bitis_denetle(z) == []


def test_yeni_tipler_hatalari():
    w = {"tip": "wojak", "arka": LAB, "karakterler": [{"id": "a", "gorsel": TEMSILCI}]}
    _hata_bekle(lambda: _video([{"baslik": "a", "sahneler": [{**w, "satirlar": [{"metin": "x", "konusan": "z"}]}]}]),
                "konusan", "'z'")
    _hata_bekle(lambda: _video([{"baslik": "a", "sahneler": [{"tip": "metin", "metin": "x",
                                                               "satirlar": [{"metin": "y", "konusan": "a"}]}]}]),
                "wojak")
    _hata_bekle(lambda: _video([{"baslik": "a", "sahneler": [{"tip": "metin", "metin": "x",
                                                               "olaylar": [{"tip": "sondur", "oran": 0.4}]}]}]),
                "izgara")
    _hata_bekle(lambda: _video([{"baslik": "a", "sahneler": [{"tip": "pano", "kartlar": [{"id": "a", "metin": "x"}],
                                                               "ipler": [["a", "q"]]}]}]), "kart 'q' yok")
    _hata_bekle(lambda: _video([{"baslik": "a", "sahneler": [{"tip": "bolunmus", "sol": {"etiket": "x"},
                                                               "sag": {"metin": "y"}}]}]), "gorsel", "metin")
    _hata_bekle(lambda: _video([{"baslik": "a", "sahneler": [{"tip": "sayac", "deger": [1, 2, 3]}]}]), "[60, 0]")
    _hata_bekle(lambda: _video([{"baslik": "a", "sahneler": [{"tip": "metin", "metin": "x",
                                                               "kose": {"konum": "orta"}}]}]), "kose konum")
    _hata_bekle(lambda: _video([{"baslik": "a", "sahneler": [{"tip": "metin", "metin": "x", "zemin": "mor"}]}]),
                "zemin")
    _hata_bekle(lambda: _video([{"baslik": "a", "sahneler": [
        {**w, "karakterler": [{"id": "a", "gorsel": TEMSILCI, "derinlik": 2}]}]}]), "derinlik")
    _hata_bekle(lambda: _video([{"baslik": "a", "sahneler": [{"tip": "bitis", "duzen": "alt"}]}]), "duzen")


def test_sayac_bolumleri_ve_metin_daktilo():
    from wojak.uzun.sahneler import metin_zamanlari, sayac_bolumleri
    v = _yeni_tipler_video()
    z = zaman.hesapla(v, tahmin=True)
    b = sayac_bolumleri(z.sahneler[3])
    assert [(x["a"], x["b"]) for x in b] == [(60.0, 0.0), (0.0, 17.0)]
    assert b[0]["sonek"] == "" and b[1]["etiket"] == "bebek" and b[1]["renk"] == (214, 58, 50)
    assert b[1]["t0"] > b[0]["t0"]
    m = metin_zamanlari(z.sahneler[4])
    bas, hiz = m["daktilo"]
    assert m["kelimeler"] == [bas, bas + len("anne ") / hiz]   # kelime = ilk harfinin anı


def test_kamera_itmesi_ve_konusma():
    from PIL import Image
    from wojak.uzun.sahneler import Baglam, Kam, Konusma, cizici, yapay_heceler
    k = Kam(1.0, 0.5, 0.5, 1920, 1080)
    assert k.nokta(300, 700) == (300, 700)                       # zoom 1: kimlik
    k2 = Kam(1.1, 0.2, 0.5, 1920, 1080)                          # merkez kırpılır: pencere dışına taşmaz
    assert abs(k2.cx - 0.5 / 1.1) < 1e-9
    v = _yeni_tipler_video()
    z = zaman.hesapla(v, tahmin=True)
    s = z.sahneler[0]
    cz = cizici(s, Baglam(v, 480, 270))
    a, b = s.satirlar
    assert cz.kam(0.0).z < cz.kam((a.t0 + a.t1) / 2).z            # konuşurken kamera yaklaşır
    ka = cz.kam((a.t0 + a.t1) / 2)
    assert ka.cx < 0.5                                           # ... soldaki konuşana doğru
    kb = cz.kam((b.t0 + b.t1) / 2 + 0.6)
    assert kb.cx > ka.cx                                         # sonra sağdakine
    assert cz.cizim_sirasi[0].derinlik == 0.7                    # arkadaki önce çizilir
    kn = cz.karakterler[0].konusma
    ic = [kn.deger(a.t0 + i * 0.02) for i in range(int((a.t1 - a.t0) / 0.02))]
    assert max(ic) > 0.5 and kn.deger(a.t1 + 1.0) == 0.0          # konuşurken seker, sonra durur
    assert cz.karakterler[2].konusma.deger(a.t0 + 0.5) == 0.0      # konuşmayan sekmez
    hc = yapay_heceler(2.0)
    assert 5 <= len(hc) <= 12 and all(0 <= t < 2.0 for t, _ in hc)
    assert Konusma().deger(1.0) == 0.0
    assert isinstance(cz.kare(a.t0 + 0.3), Image.Image)


def test_hece_anlari_ses_dosyasindan():
    import tempfile
    from wojak.uzun.sahneler import hece_anlari
    sr = 44100
    t = np.arange(int(sr * 2.0)) / sr
    zarf = np.zeros_like(t)
    for h in (0.2, 0.55, 0.9, 1.3, 1.7):                         # beş 'hece'
        zarf += np.exp(-((t - h - 0.06) / 0.05) ** 2)
    x = (0.4 * zarf * np.sin(2 * np.pi * 180 * t)).astype(np.float32)
    with tempfile.TemporaryDirectory() as d:
        p = Path(d) / "h.wav"
        tts.wav_yaz(p, x, sr)
        hc = hece_anlari(p)
    assert len(hc) == 5, hc
    assert all(abs(a - b) < 0.08 for (a, _), b in zip(hc, (0.2, 0.55, 0.9, 1.3, 1.7)))
    assert hece_anlari(None) is None


def test_izgara_duzeni_ve_sondurme():
    from wojak.uzun.bilgi import izgara_duzeni
    from wojak.uzun.sahneler import Baglam, cizici
    for n in (1, 17, 400, 10000):
        cols, rows, pitch = izgara_duzeni(n, 1600, 500)
        assert cols * rows >= n and cols * pitch <= 1600 + 1e-6 and rows * pitch <= 500 + 1e-6
    v = _yeni_tipler_video()
    z = zaman.hesapla(v, tahmin=True)
    cz = cizici(z.sahneler[8], Baglam(v, 480, 270))
    a0, a1 = cz.alfa(1.4)[:-1], cz.alfa(3.0)[:-1]
    assert (a0 > 0.85).all()                                     # doldu, henüz sönmedi
    sonuk = (a1 < 0.3).mean()
    assert abs(sonuk - 0.4) < 0.01, sonuk                        # %40'ı söndü
    assert cz.alfa(0.0)[:-1].max() == 0.0 and cz.alfa(0.0)[-1] == 0.0


def test_kose_gostergesi():
    from wojak.uzun.sahneler import Baglam
    from wojak.uzun.ust import KoseGostergesi, kose_olaylari
    v = _yeni_tipler_video()
    z = zaman.hesapla(v, tahmin=True)
    c = Baglam(v, 480, 270)
    s = z.sahneler[3]                                            # kose olayı var, sahne anahtarı yok
    kg = KoseGostergesi(s, c, kose_olaylari(s))
    assert kg.goster_t == 0.5 and kg._metin(5.0)[0] == "5"
    s = z.sahneler[0]
    s.olaylar.append(spec.Olay(tip="kose", p={"deger": 12}, zaman=1.0))
    kg = KoseGostergesi(s, c, kose_olaylari(s))
    assert kg._metin(0.2)[0] == "GÜN 0 / 12" and kg._metin(1.3)[0] not in ("GÜN 0 / 12", "GÜN 12 / 12")
    assert kg._metin(2.0)[0] == "GÜN 12 / 12"                    # sayarak varır
    s = z.sahneler[5]
    kg = KoseGostergesi(s, c, kose_olaylari(s))
    assert kg._metin(0.1)[0] == "1961"                           # yıl: binlik ayırıcı yok
    assert kg._metin(0.4 + 0.8 + 0.5)[0] == "????"               # takıldı
    assert kg._metin(0.4 + 0.8 + 0.05)[0] != "????"              # ara ara titrer


def test_muzik_egrisi_ve_otomatik_efektler():
    from wojak.uzun import ses
    v = _yeni_tipler_video()
    z = zaman.hesapla(v, tahmin=True)
    e = ses.muzik_egrisi(z)
    assert e[0] == (0.0, -8.0, 0.6) and e[1][1] == 0.0           # soğuk açılış kısık, sonra normale döner
    n = int(z.sure * ses.SR)
    g = ses.muzik_kazanci(e, n)
    assert abs(g[0] - 10 ** (-8 / 20)) < 1e-4 and abs(g[-1] - 1.0) < 1e-4
    assert ses.muzik_kazanci([], n) is None
    ef = ses.otomatik_efektler(z)
    adlar = [a for _, a, _ in ef]
    for ad in ("gecis", "boom", "marka", "damga", "raptiye", "tus", "kalem", "tik", "static"):
        assert ad in adlar, ad
    kart = z.sahneler[2]
    assert any(a == "gecis" and abs(t - (z.sahne_basi(kart) - 0.24)) < 1e-6 for t, a, _ in ef)
    for ad in set(adlar):
        assert (spec.SFX_DIR / f"{ad}.wav").exists(), ad          # bütün otomatik efekt dosyaları var


def test_ayni_kayit_tekrari():
    v = _video([{"baslik": "a", "sahneler": [
        {"tip": "metin", "metin": "x", "satirlar": [{"ses": "aylin", "metin": "Tamamen zehirsiz."}]},
        {"tip": "metin", "metin": "y", "satirlar": ["Ara.", {"ses": "aylin", "metin": "Tamamen zehirsiz."}]},
        {"tip": "metin", "metin": "z", "satirlar": [{"ses": "aylin", "metin": "Tamamen zehirsiz.", "hiz": 1.2}]},
    ]}])
    gruplar, uyari = tts.tekrarlar(v)
    assert gruplar == [["bölüm 1, sahne 1, satır 1", "bölüm 1, sahne 2, satır 2"]]
    assert len(uyari) == 1 and "farklı ayarla" in uyari[0]
    a, b = v.sahneler[0].satirlar[0], v.sahneler[1].satirlar[1]
    assert tts.satir_wav(v, a) == tts.satir_wav(v, b)           # aynı önbellek dosyası = aynı ses


def test_bitis_denetimi():
    v = _video([{"baslik": "a", "sahneler": [{"tip": "bitis", "sure": 25}, {"tip": "metin", "metin": "x"}]}])
    u = paket.bitis_denetle(zaman.hesapla(v))
    assert any("son sahnesi" in x for x in u) and any("5-20" in x for x in u)


def test_zemin_stilleri_ve_donuk_karartma():
    from PIL import Image
    from wojak.uzun import cizim as C, zemin as Z
    from wojak.uzun.sahneler import Baglam
    v = _video([{"baslik": "a", "sahneler": [{"tip": "metin", "metin": "x"}]}])
    c = Baglam(v, 320, 180)
    assert Z.Zemin(c, {"zemin": "kagit"}).palet is Z.KAGIT
    assert Z.Zemin(c, {"zemin": "foto"}).stil == "koyu"          # fotoğrafsız 'foto' -> koyu
    zf = Z.Zemin(c, {"zemin": "foto", "arka": spec.yol_coz(KUTU, KOK)})
    assert zf.stil == "foto" and zf.palet is Z.KOYU
    a, b = zf.ciz(0.0, 6.0), zf.ciz(2.0, 6.0)
    assert a.size == (320, 180) and np.abs(np.asarray(a, np.float32) - np.asarray(b, np.float32)).mean() > 0.5
    assert Z.renk("kirmizi", (0, 0, 0)) == C.KIRMIZI and Z.renk(None, (1, 2, 3)) == (1, 2, 3)
    acik, koyu = Image.new("RGB", (64, 36), (230, 220, 200)), Image.new("RGB", (64, 36), (20, 20, 24))
    assert C.donuk_karart(koyu, 0.45) == 0.45                     # koyu kare: verilen oran
    k = C.donuk_karart(acik, 0.45)
    assert k > 0.7 and abs(220 * (1 - k) - 58) < 8                # açık kare: yazı okunacak kadar karartılır


def test_yeni_tipler_kareleri_ve_bindirme():
    """Her yeni sahne tipinden kare üretilir; bindirme sahnesinin ilk karesi önceki sahnenin son karesidir."""
    from wojak.uzun import render
    v = _yeni_tipler_video()
    z = zaman.hesapla(v, tahmin=True)
    W, H = 320, 180
    for i, s in enumerate(z.sahneler):
        ku = render.KareUretici(v, z, i, W, H)
        for k in (0, s.n_kare // 2, s.n_kare - 1):
            im = ku.kare(k)
            assert im.size == (W, H) and im.mode == "RGB", (s.tip, k)
    i = 2                                                        # bindirme bölüm kartı (önceki: marka)
    onceki = render.son_kare(v, z, i - 1, W, H)
    ilk = render.KareUretici(v, z, i, W, H).cz.kare(0.0)
    fark = np.abs(np.asarray(onceki, np.float32) - np.asarray(ilk, np.float32)).mean()
    assert fark < 6.0, fark                                      # donmuş kare (yalnız gren farkı)
    # bindirme parçasının önbellek anahtarı önceki sahneye bağlı
    a = {p.sahne_i: p.anahtar for p in render.parcalar(v, z, Path("/tmp"), W, H, {"preset": "x", "crf": 1})}
    z.sahneler[1].p["yazi"] = "baska"
    b = {p.sahne_i: p.anahtar for p in render.parcalar(v, z, Path("/tmp"), W, H, {"preset": "x", "crf": 1})}
    assert a[2] != b[2] and a[3] == b[3]


# ---------------------------------------------------------------- 3. tur (talidomit-turkiye 2. hakem turu)

def test_srt_kelime_kaybi_yok_ve_yetim_yok():
    """Eski hata: altyazi.parcalar() sığmayan parçayı ilk 2 satıra kesiyordu ("Aygün," ve "yazın." düşüyordu);
    açgözlü bölme tek kelimelik yetim parçalar bırakıyordu ("sentezleniyor.")."""
    uzun1 = ("1954'te Alman ilaç firması Grünenthal'in laboratuvarında yeni bir molekül sentezleniyor.")
    uzun2 = ("Anlatılana göre Ankara Veteriner Fakültesi'nden virolog Süreyya Tahsin Aygün, ilacı tavuk "
             "embriyolarında denemiş ve Bakanlığı uyarmış.")
    uzun3 = ("O yıllardan bir belge, bir gazete kupürü ya da ailenizden dinlediğiniz bir anı varsa yorumlara yazın.")
    v = _video([{"baslik": "a", "sahneler": [{"tip": "metin", "metin": "x", "satirlar": [uzun1, uzun2, uzun3]}]}])
    _sureler(v, [3.6, 5.5, 4.4])            # gerçekten kısa: eskiden birleştirip 2 satıra kesiyordu
    z = zaman.hesapla(v)
    ps = altyazi.parcalar(z)
    assert altyazi.kelime_farki(z, ps) == [], altyazi.kelime_farki(z, ps)
    assert altyazi.denetle(ps) == [], altyazi.denetle(ps)
    for p in ps:
        assert len(p.metin.replace("\n", " ").split()) >= 2, p.metin
    b = altyazi._dengeli_bol(uzun1 + " " + uzun1)
    assert " ".join(b) == uzun1 + " " + uzun1 and max(len(x) for x in b) - min(len(x) for x in b) < 30


def test_efekt_kismasi_konusmada():
    from wojak.uzun import ses
    sr = ses.SR
    n = 4 * sr
    an = np.zeros(n, np.float32)
    t = np.arange(sr) / sr
    an[sr:2 * sr] = 0.18 * np.sin(2 * np.pi * 180 * t)          # 1-2 sn konuşma (~ -18 dBFS)
    ef = np.zeros((n, 2), np.float32)
    ef[:, :] = 0.5                                              # yüksek, sürekli efekt
    g = ses.efekt_kismasi(an, ef)
    orta = 20 * np.log10(g[int(1.5 * sr)])
    assert orta < -15, orta                                     # konuşmanın içinde efekt kısılır
    assert g[int(3.5 * sr)] > 0.99 and g[int(0.5 * sr)] > 0.99  # konuşma yokken dokunulmaz
    lv = 20 * np.log10(0.5 * g[int(1.5 * sr)])
    assert lv <= ses.SATIR_HEDEF_DB - ses.EFEKT_PAYI_DB + 1.0, lv


def test_muzik_kipleri_ve_bolumlu_uretim():
    from wojak.uzun import muzik, ses
    x = muzik.uret_bolumlu(24.0, 5, [(0, "drone"), (8, "nabiz"), (16, "major")])
    y = muzik.uret_bolumlu(24.0, 5, [(0, "drone"), (8, "nabiz"), (16, "major")])
    assert x.shape == (24 * muzik.SR, 2) and np.isfinite(x).all() and np.abs(x).max() <= 0.95
    assert np.array_equal(x, y)
    _hata_bekle(lambda: _video([{"baslik": "a", "sahneler": [{"tip": "metin", "metin": "x", "sure": 2,
                                                              "muzik_mod": "caz"}]}]), "muzik_mod")
    v = _video([{"baslik": "a", "sahneler": [{"tip": "metin", "metin": "x", "sure": 10},
                                             {"tip": "metin", "metin": "y", "sure": 10, "muzik_mod": "gerilim"}]},
                {"baslik": "b", "kart_muzik_db": 4, "muzik_mod": "major",
                 "sahneler": [{"tip": "metin", "metin": "z", "sure": 10}]}])
    z = zaman.hesapla(v)
    k = ses.muzik_kipleri(z)
    assert [m for _, m in k] == ["drone", "gerilim", "major"] and abs(k[1][0] - 10.0) < 1e-6
    kart = z.sahneler[2]
    assert kart.tip == "bolum_karti" and kart.muzik_db == 4 and kart.muzik_mod == "major"


def test_satir_db_ve_cikti_klasoru():
    v = _video([{"baslik": "a", "sahneler": [{"tip": "metin", "metin": "x",
                                             "satirlar": [{"metin": "Merhaba.", "db": 1.5}]}]}])
    assert v.sahneler[0].satirlar[0].db == 1.5
    assert v.cikti.name == "test-uzun"                          # Short'un out/<id>/'sine karışmaz
    _hata_bekle(lambda: _video([{"baslik": "a", "sahneler": [{"tip": "metin", "metin": "x",
                                                              "satirlar": [{"metin": "a", "db": 9}]}]}]), "db")


def test_qa_kelime_farklari():
    assert tts.kelime_farklari("İlaç hiçbir gebe hayvanda denenmiyor.", "ilaç hiçbir gebe hayvanda denemiyor") \
        == ["denenmiyor"]
    assert tts.kelime_farklari("ağır bir cüzzam hastası", "ağır bir cüzdan hastası") == ["cuzzam"]
    assert tts.kelime_farklari("Lenz'in 15 Kasım'da", "Lents'in 15 Kasım'da", haric=["Lenz", "Lents"]) == []


def test_alt_piksel_yerlesim():
    from PIL import Image
    from wojak.uzun import cizim as C
    kare = Image.new("RGBA", (20, 20), (255, 255, 255, 255))
    src = C.alt_piksel_hazirla(kare)
    def merkez(x):
        spr, x0, y0 = C.alt_piksel(src, x, 10.0, 1.0, 1.0)
        dst = Image.new("RGB", (60, 40), (0, 0, 0))
        C.bindir(dst, spr, x0, y0)
        a = np.asarray(dst, np.float32)[..., 0]
        return (a.sum(axis=0) * np.arange(60)).sum() / a.sum()
    m0, m1 = merkez(20.0), merkez(20.5)
    assert abs((m1 - m0) - 0.5) < 0.08, (m0, m1)                # yarım piksel kayma görünür (eskiden 0 ya da 1)


def test_paket_telif_ve_ara_reklam():
    import tempfile
    v = _video([{"baslik": "Giriş", "kart": False, "sahneler": [{"tip": "metin", "metin": "x", "sure": 20}]},
                {"baslik": "Bir", "sahneler": [{"tip": "metin", "metin": "y", "sure": 20}]},
                {"baslik": "İki", "sahneler": [{"tip": "metin", "metin": "z", "sure": 20}]}],
               paket={"telif_notu": ["Videoda telifli görsel yok."], "ara_reklam": [2],
                      "ek_maddeler": ["Bitiş kutularını ört"], "yapay_icerik": "Hayır öner."})
    v.paket["dinle"] = [{"ara": "z", "not": "dinle"}, {"ara": "yok böyle"}]
    v.bolumler[1].sahneler[0].satirlar  # metin sahneleri satırsız: dinle araması bulamaz, yine de yazılır
    z = zaman.hesapla(v)
    k = v.bolumler[2].sahneler[0]
    t0 = z.sahne_basi(k)
    y = paket.ara_reklam_yerleri(v, z)
    assert y[0].startswith(zaman.zaman_str(paket.yukari(t0)) + " (2. bölüm kartı")
    assert t0 <= paket.yukari(t0) < t0 + k.sure_hesap        # reklam kartın İÇİNDE, önceki cümlenin üstünde değil
    with tempfile.TemporaryDirectory() as d:
        md = paket.yaz(v, z, Path(d), None, None, []).read_text(encoding="utf-8")
    assert "Telif notu" in md and "Videoda telifli görsel yok." in md and "Bitiş kutularını ört" in md
    assert "Hayır öner." in md and "[Short bağlantısı]" in md
    assert "kulakla dinle" in md and "'yok böyle' (satır bulunamadı)" in md
    assert "yukarıdaki 'Telif notu'" not in md


def test_paket_kucukresim_yedek():
    """11. tur: `test: false` varyant yedek yazılır; paket "hepsini yükle" demez (ek maddeyle çelişiyordu)."""
    import tempfile
    v = _video([{"baslik": "Giriş", "kart": False, "sahneler": [{"tip": "metin", "metin": "x", "sure": 20}]}])
    v.kucukresimler = [{"ad": "a"}, {"ad": "b"}, {"ad": "c", "test": False}]
    z = zaman.hesapla(v)
    with tempfile.TemporaryDirectory() as d:
        ks = [Path(d) / f"kucukresim_{a}.jpg" for a in "abc"]
        md = paket.yaz(v, z, Path(d), None, None, ks).read_text(encoding="utf-8")
    assert "`kucukresim_c.jpg` (yedek: teste ekleme)" in md and "`kucukresim_a.jpg`\n" in md
    assert "hepsini yükle" not in md and "yedek olmayan varyantlar eklendi" in md
    v.kucukresimler = [{"ad": "a"}, {"ad": "b"}]
    with tempfile.TemporaryDirectory() as d:
        md = paket.yaz(v, z, Path(d), None, None, [Path(d) / "kucukresim_a.jpg"]).read_text(encoding="utf-8")
    assert "hepsini yükle" in md and "yedek" not in md.split("## Küçük resimler")[1].split("##")[0]



def test_altyazi_kirma_kurallari():
    # sayı öbeği, özel ad, tırnak içi bölünmez; ayrı 'da' satır başına düşmez (talidomit-turkiye 3. hakem turu)
    t = altyazi.iki_satir("Ve ABD'de de en az on yedi bebek etkileniyor.")
    assert "on\nyedi" not in t and "on yedi" in t
    t = altyazi.iki_satir("Ama aynı yıllarda Ankara'da da bir ‘hayır’ denmişti.")
    assert not t.split("\n")[1].startswith("da ")
    ps = altyazi.parcala("Anlatılana göre Ankara Veteriner Fakültesi'nden virolog Süreyya Tahsin Aygün, ilacı "
                         "tavuk embriyolarında denemiş ve Bakanlığı uyarmış.")
    duz = [p.replace("\n", " ") for p in ps]
    assert any("Ankara Veteriner Fakültesi'nden" in p for p in duz)
    assert all("Veteriner\nFakültesi" not in p for p in ps)
    ps = altyazi.parcala("İnternette sık duyduğunuz ‘etkilenmeyen tek iki ülke Türkiye ve ABD’ sözü ise yanlış.")
    assert any("‘etkilenmeyen tek iki ülke Türkiye ve ABD’" in p.replace("\n", " ") for p in ps)
    c = altyazi.kirma_cezalari("on yedi, bebek".split())
    assert c[1] > 0 and c[2] == 0                     # virgülden sonra kırmak serbest
    # 12. tur (dil hakemi S10): noktalama sonrası kırma dengeden önce; tamlama, sıfat + ad, ikileme bölünmez;
    # bağlaçtan önce kırmak iyi
    assert altyazi.iki_satir("Peki ruhsat vermemek yeterli miydi? Her zaman değil.") == \
        "Peki ruhsat vermemek yeterli miydi?\nHer zaman değil."
    assert altyazi.iki_satir("Kural şu: FDA 60 gün içinde yanıt vermezse,").startswith("Kural şu:\n")
    assert altyazi.iki_satir("26 Kasım'da haber bir pazar gazetesine düşüyor.") == \
        "26 Kasım'da haber\nbir pazar gazetesine düşüyor."
    assert "artırırlarsa artırsınlar," in altyazi.iki_satir("Dozu ne kadar artırırlarsa artırsınlar, fareler ölmüyor.")
    assert altyazi.iki_satir("Bugün bir kanser ilacı olarak kullanılıyor;") == "Bugün bir kanser ilacı\nolarak kullanılıyor;"
    assert "uyku\nilacını" not in altyazi.iki_satir("Sheskin, elinde kalan eski bir uyku ilacını veriyor: talidomit.")
    assert "yan\netki" not in altyazi.iki_satir("Firma, böyle bir yan etki duymadığını söylüyor.")


def test_pano_asili_kart_ve_inik_damga():
    # bölünmüş panonun ikinci çekimi: asılı kartlar düşmez/ses çıkarmaz, inik damga önceden basılı (3. hakem turu)
    from wojak.uzun import bilgi, ses
    from wojak.uzun.ust import Damga
    v = _video([{"baslik": "a", "sahneler": [{
        "tip": "pano", "sure": 6, "yakin": 1.2,
        "kartlar": [{"id": "m", "metin": "BAKANLIK", "asili": True}, {"id": "k", "metin": "K", "asili": True},
                    {"id": "g", "metin": "G"}],
        "ipler": [["k", "m"], ["g", "m"]],
        "olaylar": [{"tip": "kart", "id": "g", "t": 2.0},
                    {"tip": "damga", "kart": "m", "metin": "YOK", "t": 0.0, "inik": True}]}]}])
    z = zaman.hesapla(v)
    s = z.sahneler[0]
    pz = bilgi.pano_zamanlari(s)
    assert pz["kartlar"]["m"] < 0 and pz["kartlar"]["k"] < 0 and abs(pz["kartlar"]["g"] - 2.0) < 1e-6
    ipler = {(a, b): t for a, b, t in pz["ipler"]}
    assert ipler[("k", "m")] < 0 and ipler[("g", "m")] > 2.0
    efektler = ses.otomatik_efektler(z)
    assert all(t >= 0 for t, *_ in efektler)                          # asılı kart/ip ses çıkarmaz
    assert not any(ad == "damga" for _, ad, *_ in efektler)          # inik damga ses çıkarmaz
    assert sum(ad == "raptiye" for _, ad, *_ in efektler) == 1       # yalnız inen kart (g)
    o = next(o for o in s.olaylar if o.tip == "damga")

    class _C:
        S, W, H = 0.25, 480, 270
    assert Damga(o, _C(), 0).t0 < 0                                   # sahne başında basılı


def test_paket_dinle_satir_zamani():
    v = _video([{"baslik": "Giriş", "kart": False, "sahneler": [
                    {"tip": "metin", "metin": "x", "satirlar": ["Birinci cümle.", "Ağır bir cüzzam hastası uyuyamıyor."]}]},
                {"baslik": "Bir", "sahneler": [{"tip": "metin", "metin": "y", "satirlar": ["Cüzzam tedavisinde."]}]}],
               paket={"dinle": [{"ara": "cüzzam", "not": "'cüzdan' duyuluyor"}]})
    _sureler(v, [2.0, 3.0, 2.5])
    z = zaman.hesapla(v)
    d = paket.dinlenecekler(v, z)
    bas = [sz.bas for sz in z.satirlar()]
    assert len(d) == 2                                           # büyük/küçük harf duyarsız, iki satır
    assert d[0].startswith(zaman.zaman_str(bas[1]) + " «") and "cüzdan" in d[0]
    assert d[1].startswith(zaman.zaman_str(bas[2]) + " «Cüzzam tedavisinde.»")


# ---------------------------------------------------------------- 4. tur (talidomit-turkiye 3. hakem turu)

def test_konuk_karakter_her_sahnede():
    """Wojak dışı sahnede köşeden giren tepki karakteri: spec, yüz olayı, hareket vuruşu, efekt, kare (4. tur)."""
    from wojak.uzun import render, ses
    from wojak.uzun.sahneler import vuruslar
    kl = "assets/kit/klasik/"
    v = _video([{"baslik": "a", "kart": False, "sahneler": [
        {"tip": "sayac", "deger": 100, "sure": 4,
         "konuk": {"id": "z", "gorsel": kl + "sakin.png", "x": 0.87, "boy": 0.5, "yon": "alt", "giris": 0.4},
         "olaylar": [{"tip": "yuz", "karakter": "z", "gorsel": kl + "terli.png", "t": 2.0},
                     {"tip": "isim", "karakter": "z", "ad": "X", "t": 1.0}]},
        {"tip": "harita", "bolge": "akdeniz", "vurgu": {"kod": "TUR"}, "sure": 3,
         "konuk": [{"id": "l", "gorsel": kl + "sakin.png", "x": 0.1}],
         "olaylar": [{"tip": "giris", "karakter": "l", "t": 1.5}]}]}])
    z = zaman.hesapla(v, tahmin=True)
    s0, s1 = z.sahneler
    assert s0.p["konuk"][0]["yon"] == "alt" and Path(s0.p["konuk"][0]["gorsel"]).is_absolute()
    assert 0.4 in vuruslar(s0) and 2.0 in vuruslar(s0) and 1.5 in vuruslar(s1)
    ef = ses.otomatik_efektler(z)
    on = 0.1 - ses.WHOOSH_TEPE    # 7. tur: whoosh tepesi girişin en hızlı karelerine (girişten 0,1 sn sonra)
    assert any(ad == "whoosh_kisa" and abs(t - (0.4 + on)) < 1e-6 for t, ad, _ in ef)
    assert any(ad == "whoosh_kisa" and abs(t - (z.sahne_basi(s1) + 1.5 + on)) < 1e-6 for t, ad, _ in ef)
    W, H = 320, 180
    ku = render.KareUretici(v, z, 0, W, H)
    once, sonra = np.asarray(ku.kare(3), np.float32), np.asarray(ku.kare(60), np.float32)
    # konuk sağ altta: girişten sonra o köşede beyaz kafa görünür
    assert sonra[110:, 250:, :].mean() > once[110:, 250:, :].mean() + 20
    # hata: wojak sahnesinde konuk yok; olmayan konuğa yüz olayı
    _hata_bekle(lambda: _video([{"baslik": "a", "sahneler": [
        {"tip": "wojak", "arka": "uzun/demo/img/contergan_kutu.jpg", "konuk": {"gorsel": kl + "sakin.png"}}]}]), "konuk")
    _hata_bekle(lambda: _video([{"baslik": "a", "sahneler": [
        {"tip": "sayac", "deger": 1, "olaylar": [{"tip": "yuz", "karakter": "q", "gorsel": kl + "terli.png"}]}]}]),
        "yalnız")


def test_pano_damga_gorselli_kartta_gorselin_ortasina():
    """Görselli kartta damga başlığın üstüne değil görselin ortasına iner; kart_y elle verilebilir (4. tur)."""
    from wojak.uzun import bilgi
    from wojak.uzun.sahneler import Baglam
    v = _video([{"baslik": "a", "sahneler": [{
        "tip": "pano", "sure": 4,
        "kartlar": [{"id": "b", "metin": "ANMA YAZILARI, 1994", "alt": "x", "gorsel": "uzun/demo/img/contergan_kutu.jpg"},
                    {"id": "m", "metin": "BAKANLIK"}],
        "olaylar": [{"tip": "damga", "kart": "b", "metin": "YOK", "t": 0.5},
                    {"tip": "damga", "kart": "m", "metin": "YOK", "t": 0.5},
                    {"tip": "damga", "kart": "b", "metin": "Z", "t": 0.5, "kart_y": 0.3}]}]}])
    z = zaman.hesapla(v, tahmin=True)
    cz = bilgi.PanoCizici(z.sahneler[0], Baglam(v, 480, 270))
    ky = [k for _, _, k in cz.damgalar]
    assert ky[0] < -0.05            # görselli kart: görselin ortası, kart merkezinin üstünde
    assert abs(ky[1] - 0.2) < 1e-6  # görselsiz kart: eski yer
    assert abs(ky[2] - 0.3) < 1e-6  # elle


def test_tepe_siniri_ve_anlatim_izi_seviyesi():
    """Altlığın 100 ms tepesi medyan konuşmanın en çok TEPE_PAYI_DB üstünde; konuşma yoksa dokunulmaz (4. tur)."""
    from wojak.uzun import ses
    sr = ses.SR
    n = sr * 6
    t = np.arange(n) / sr
    an = np.zeros(n, np.float32)
    an[: 3 * sr] = 0.18 * np.sin(2 * np.pi * 180 * t[: 3 * sr])          # konuşma ~ -18 dBFS
    alt = np.zeros((n, 2), np.float32)
    alt[4 * sr: 4 * sr + sr // 2] = 0.9 * np.sin(2 * np.pi * 60 * t[: sr // 2])[:, None]   # boom ~ -4 dBFS
    g, bilgi = ses.tepe_siniri(an, alt)
    y = alt * g[:, None]
    def db100(x):
        h = int(0.1 * sr)
        k = len(x) // h
        e = (x[: k * h].reshape(k, h, *x.shape[1:]) ** 2).mean(axis=1)
        e = e.mean(axis=1) if e.ndim > 1 else e
        return 10 * np.log10(e + 1e-12)
    ref = np.median(db100(an)[db100(an) > -40])
    assert db100(y).max() <= ref + ses.TEPE_PAYI_DB + 0.6, (db100(y).max(), ref)
    assert g[: 3 * sr].min() > 0.999                                    # sessiz altlık kısılmaz
    assert bilgi["altlik_en_yuksek_ustu_db"] > 10
    g2, b2 = ses.tepe_siniri(np.zeros(n, np.float32), alt)
    assert g2.min() == 1.0 and b2 == {}


def test_bes_tur_motor_ekleri():
    """5. tur: yıl göstergesinde yüzyıl sabit, kartsız bölüm damgası aşağı, Türkçe kırma cezaları, iç içe telif
    notu, sahne `sfx_db`, damga `kontur`, metinde süs tırnağı yalnız alıntıda."""
    import tempfile
    from wojak.uzun import ses
    from wojak.uzun.sahneler import Baglam, MetinCizici
    from wojak.uzun.ust import KoseGostergesi, damga_sprite, kose_olaylari
    # yıl karışımı: "19??" / "20??", gelecek yıl yok
    v = _yeni_tipler_video()
    z = zaman.hesapla(v, tahmin=True)
    c = Baglam(v, 480, 270)
    s = z.sahneler[5]
    # 9. tur (izlenme S1): takılı yıl geriye gitmez: eski yıldan ileri akar, sonra takılır; titreşimde de eski yıldan
    # önceki bir yıl görünmez
    kg = KoseGostergesi(s, c, kose_olaylari(s))
    t_e, eski = [(d[0], d[2]) for d in kg.durumlar if d[5]][0]
    onceki = int(eski)
    for k in range(80):
        t_ = t_e + k * 0.02
        m = kg._metin(t_)[0]
        if m == "????":
            continue
        assert m.isdigit() and int(m) >= int(eski), m
        if t_ < t_e + 0.8:
            assert int(m) >= onceki, (m, onceki)
            onceki = int(m)
    s.olaylar = [o for o in s.olaylar if o.tip != "kose"] + [
        spec.Olay(tip="kose", p={"deger": "20??", "takili": True}, zaman=0.4)]
    kg = KoseGostergesi(s, c, kose_olaylari(s))
    onceki = 0
    for k in range(60):
        m = kg._metin(0.4 + k * 0.02)[0]
        assert m == "20??" or (m.isdigit() and int(m) <= 2019), m
        if m != "20??" and 0.4 + k * 0.02 < 1.2:
            assert int(m) >= onceki, (m, onceki)
            onceki = int(m)
    # kartsız bölüm: aşağı yuvarlanır (ilk kelime kesilmesin); kartlı: yukarı
    v = _video([
        {"baslik": "Giriş", "kart": False, "sahneler": [{"tip": "metin", "metin": "x", "sure": 41.7}]},
        {"baslik": "İki", "sahneler": [{"tip": "metin", "metin": "x", "sure": 30}]},
        {"baslik": "Kapanış", "kart": False, "sahneler": [{"tip": "metin", "metin": "x", "sure": 20}]}])
    z = zaman.hesapla(v)
    d = paket.bolum_damgalari(z)
    import math
    t3 = z.sahne_basi(v.bolumler[2].sahneler[0])
    assert d[1][0] == math.ceil(41.7 - 1e-6) and d[2][0] == math.floor(t3) and t3 % 1 > 0
    # Türkçe kırma cezaları
    ceza = altyazi.kirma_cezalari("yeterli miydi? her seferinde yetersiz olduğunu Grünenthal'in laboratuvarı".split())
    assert ceza[1] >= 60 and ceza[3] >= 50 and ceza[5] >= 30 and ceza[7] >= 25 and ceza[2] == 0
    assert altyazi.kirma_cezalari("1928'den beri".split())[1] >= 40
    # iç içe telif notu
    v = _video([{"baslik": "Giriş", "kart": False, "sahneler": [{"tip": "metin", "metin": "x", "sure": 20}]},
                {"baslik": "Bir", "sahneler": [{"tip": "metin", "metin": "y", "sure": 20}]},
                {"baslik": "İki", "sahneler": [{"tip": "metin", "metin": "z", "sure": 20}]}],
               paket={"telif_notu": ["Üst madde:", ["alt bir", "alt iki"], "Son madde."]})
    z = zaman.hesapla(v)
    with tempfile.TemporaryDirectory() as dd:
        md = paket.yaz(v, z, Path(dd), None, None, []).read_text(encoding="utf-8")
    assert "- Üst madde:\n  - alt bir\n  - alt iki\n- Son madde." in md
    # sfx_db: yalnız o sahnenin otomatik efektleri kayar
    v = _video([{"baslik": "a", "kart": False, "sahneler": [
        {"tip": "metin", "metin": "x", "sure": 3, "ceviri": "y"},
        {"tip": "metin", "metin": "x", "sure": 3, "ceviri": "y", "sfx_db": -6}]}])
    z = zaman.hesapla(v)
    ef = ses.otomatik_efektler(z)
    b2 = z.sahne_basi(z.sahneler[1])
    pop1 = [db for t, a, db in ef if a == "pop" and t < b2]
    pop2 = [db for t, a, db in ef if a == "pop" and t >= b2]
    assert pop1 and pop2 and abs(pop2[0] - (pop1[0] - 6)) < 1e-6
    _hata_bekle(lambda: _video([{"baslik": "a", "sahneler": [{"tip": "metin", "metin": "x", "sfx_db": 30}]}]),
                "sfx_db")
    # damga konturu: sprite büyür, kenarda beyaz piksel
    a = damga_sprite("RUHSAT", (0, 70, 30), 60, 0.5)
    b = damga_sprite("RUHSAT", (0, 70, 30), 60, 0.5, kontur=(255, 255, 255))
    assert b.width > a.width and np.asarray(b)[..., :3][np.asarray(b)[..., 3] > 200].max() == 255
    # süs tırnağı: alıntıda var, düz metinde yok
    for metin, beklenen in (("„völlig ungiftig“", True), ("Bir süre sonra", False)):
        v = _video([{"baslik": "a", "kart": False, "sahneler": [{"tip": "metin", "metin": metin, "sure": 2}]}])
        z = zaman.hesapla(v)
        mc = MetinCizici(z.sahneler[0], Baglam(v, 480, 270))
        mc.hazirla()
        assert (mc.tirnak is not None) == beklenen, metin


def test_alti_tur_motor_ekleri():
    """6. tur: teslim adı `<id>-uzun.*`, bindirme kartında tam saniyeye yakın damga aşağı, alıntı altyazısı italik,
    anlık sayaç değişiminde tık yok, wojak sahnesinde `vinyet`, fotoğraf etiketinde seyrek tuş sesi."""
    import tempfile
    from wojak.uzun import ses
    v = _video([{"baslik": "a", "kart": False, "sahneler": [{"tip": "metin", "metin": "x", "sure": 2}]}])
    assert paket.teslim_adi(v, ".mp4") == "test-uzun.mp4" and paket.teslim_adi(v, ".srt") == "test-uzun.srt"
    # bindirme kartı 30,03'te: 30 (dondurulan kare); 30,5'te: 31 (kartın içi); siyah kart her zaman yukarı
    for ilk, bind, beklenen in ((30.03, True, 30), (30.5, True, 31), (30.03, False, 31)):
        v = _video([{"baslik": "Giriş", "kart": False, "sahneler": [{"tip": "metin", "metin": "x", "sure": ilk}]},
                    {"baslik": "İki", "kart_bindirme": bind, "sahneler": [{"tip": "metin", "metin": "y", "sure": 20}]},
                    {"baslik": "Üç", "sahneler": [{"tip": "metin", "metin": "z", "sure": 20}]}])
        z = zaman.hesapla(v)
        t = z.sahne_basi(v.bolumler[1].sahneler[0])
        assert paket.bolum_damgalari(z)[1][0] == beklenen, (ilk, bind, t)
    # alıntı (anlatıcıdan başka ses) italik; satır uzunluğu etiketsiz metinle denetlenir
    v = _video([{"baslik": "a", "kart": False, "sahneler": [{"tip": "metin", "metin": "x", "satirlar": [
        "Reklamlarına göre bu ilaç…",
        {"ses": "aylin", "metin": "Distaval, hamile kadınlara ve emziren annelere tam bir güvenle verilebilir."}]}]}])
    _sureler(v, [1.5, 4.0])
    z = zaman.hesapla(v)
    ps = altyazi.parcalar(z)
    metin = altyazi.srt(ps)
    assert "<i>Reklam" not in metin and metin.count("<i>") == sum(p.alinti for p in ps) >= 1
    assert all(len(s) <= altyazi.MAX_SATIR for s in metin.splitlines()) and not altyazi.denetle(ps)
    assert not altyazi.kelime_farki(z, ps)
    # anlık değişim (deger olayı sure: 0): tık yok, vuruş var
    v = _video([{"baslik": "a", "kart": False, "sahneler": [{"tip": "sayac", "deger": 1267, "sure": 6, "olaylar": [
        {"tip": "deger", "deger": 17, "t": 3.0, "sure": 0}]}]}])
    z = zaman.hesapla(v)
    ef = ses.otomatik_efektler(z)
    assert not [t for t, a, _ in ef if a == "tik" and t >= 3.0] and [t for t, a, _ in ef if a == "hit" and t >= 3.0]
    # vinyet anahtarı wojak sahnesinde geçerli
    _video([{"baslik": "a", "kart": False, "sahneler": [{"tip": "wojak", "arka": "uzun/demo/img/contergan_kutu.jpg",
                                                          "vinyet": 0.7, "sure": 2, "karakterler": [
                                                              {"id": "a", "gorsel": "assets/kit/klasik/sakin.png"}]}]}])
    # fotoğraf etiketi: her 4 harfte bir tuş
    assert ses.ETIKET_TUS_ADIMI == 4 and ses.TUS_ADIMI == 2


# ---------------------------------------------------------------- 7. tur (animasyon: hata avı, hareket dili, kapanış)

KL = "assets/kit/klasik/"


def test_hareket_spec_ve_varsayilanlar():
    """`hareket` bloğu: varsayılanlar (bulanıklık, ikincil, canlı açık; paralaks 0, doku kapalı), aralık ve anahtar
    denetimi; yeni karakter yönleri (ust, pop) ve `canli: false`; sahne `doku` ve kamera `paralaks`."""
    v = _video([{"baslik": "a", "sahneler": [{"tip": "metin", "metin": "x"}]}])
    assert v.hareket == spec.HAREKET_VARSAYILAN
    v = _video([{"baslik": "a", "sahneler": [{"tip": "metin", "metin": "x"}]}],
               hareket={"paralaks": 0.4, "doku": True, "canli": False})
    assert v.hareket["paralaks"] == 0.4 and v.hareket["doku"] == {"gren": 0.035, "toz": 18} and not v.hareket["canli"]
    _hata_bekle(lambda: _video([{"baslik": "a", "sahneler": [{"tip": "metin", "metin": "x"}]}],
                               hareket={"titreme": 1}), "hareket")
    _hata_bekle(lambda: _video([{"baslik": "a", "sahneler": [{"tip": "metin", "metin": "x"}]}],
                               hareket={"paralaks": 2}), "paralaks")
    v = _video([{"baslik": "a", "sahneler": [{"tip": "wojak", "arka": KUTU, "doku": {"gren": 0.05},
                                              "kamera": {"paralaks": 0.3}, "karakterler": [
        {"id": "a", "gorsel": KL + "sakin.png", "yon": "pop"},
        {"id": "b", "gorsel": KL + "sakin.png", "yon": "ust", "canli": False}]}]}])
    s = v.sahneler[0]
    assert s.p["doku"] == {"gren": 0.05, "toz": 18} and s.p["kamera"]["paralaks"] == 0.3
    _hata_bekle(lambda: _video([{"baslik": "a", "sahneler": [{"tip": "wojak", "arka": KUTU, "karakterler": [
        {"id": "a", "gorsel": KL + "sakin.png", "yon": "zipla"}]}]}]), "yon")


def test_hareket_bulanikligi_ve_alt_piksel():
    from PIL import Image
    from wojak.uzun import cizim as C
    spr = Image.new("RGBA", (40, 30), (0, 0, 0, 0))
    spr.paste((255, 255, 255, 255), (10, 5, 30, 25))
    out, ox, oy = C.hareket_izi(spr, 60, 0)      # sağa 60 px/kare: sola 30 px iz (180° obtüratör)
    assert out.width - spr.width in (29, 30, 31) and ox < 0 and oy == 0
    # 8. tur: keskin katman ÜSTTE ve tam opak (yüz 'hayalet' olmaz), iz altta ve yarı saydam
    A = np.asarray(out.getchannel("A"), float)
    asil = A[5:25, -ox + 10:-ox + 30]
    assert asil.min() >= 254                               # sprite'ın kendi alanı tam opak
    iz = A[5:25, :-ox + 10]
    assert 0 < iz.max() <= 255 * C.IZ_OPAKLIK + 2          # iz yarı saydam, sprite'ın arkasında
    RGB = np.asarray(out.convert("RGB"), float)
    assert RGB[15, -ox + 20].min() >= 250                  # keskin beyaz bozulmadı
    # iz 40 px ile sınırlı (200 px/kare -> 100 px değil)
    uzun, ox2, _ = C.hareket_izi(spr, 200, 0)
    assert uzun.width - spr.width <= 41 and ox2 >= -41
    same, *_ = C.hareket_izi(spr, 1, 0)
    assert same is spr                                     # yavaşta dokunulmaz
    # alt piksel: 0,5 px kayan katman iki komşu sütuna yarı yarıya dağılır
    dst = Image.new("RGB", (20, 10), (0, 0, 0))
    nokta = Image.new("RGBA", (1, 10), (255, 255, 255, 255))
    C.bindir_alt(dst, nokta, 5.5, 0)
    satir = np.asarray(dst, float)[5, :, 0]
    assert 90 < satir[5] < 165 and 90 < satir[6] < 165
    # yatay bulanıklık: ortalama korunur
    im = Image.fromarray((np.random.default_rng(1).random((20, 60, 3)) * 255).astype(np.uint8))
    b = C.yatay_bulanik(im, 9)
    assert abs(np.asarray(b, float).mean() - np.asarray(im, float).mean()) < 2


def test_yay_egrisi_ve_karakter_ikincil_hareket():
    from wojak.uzun import render
    from wojak.uzun.sahneler import yay_egrisi
    us, y = yay_egrisi()
    assert abs(np.abs(y).max() - 1) < 1e-9 and abs(y[-1]) < 0.05     # en büyük 1, sonunda oturmuş
    v = _video([{"baslik": "a", "sahneler": [{"tip": "wojak", "arka": KUTU, "sure": 4, "karakterler": [
        {"id": "a", "gorsel": KL + "sakin.png", "taraf": "sol", "giris": 0.2},
        {"id": "b", "gorsel": KL + "sakin.png", "taraf": "sag", "yon": "pop", "giris": 1.0},
        {"id": "c", "gorsel": KL + "sakin.png", "x": 0.5, "yon": "alt", "giris": 0.5, "canli": False}]}]}])
    z = zaman.hesapla(v, tahmin=True)
    ku = render.KareUretici(v, z, 0, 320, 180)
    a, b, c = ku.cz.karakterler
    acilar = [a.poz(0.2 + 0.75 * u)["aci"] for u in np.linspace(0.05, 1.6, 30)]
    assert max(abs(x) for x in acilar) > 1.0                  # yandan girişte belirgin eğilme
    assert abs(a.poz(3.9)["aci"]) < 0.6                       # oturduktan sonra yalnız canlı salınım (<0,6°)
    assert b.poz(1.0)["sx"] < 0.05 and abs(b.poz(1.6)["sx"] - 1) < 0.03   # pop: sıfırdan büyür
    sy = [c.poz(0.5 + 0.75 * u)["sy"] for u in np.linspace(0.05, 1.5, 30)]
    assert max(sy) > 1.02                                     # alttan girişte esneme
    assert c.poz(3.9)["sy"] == 1.0 and c.poz(3.9)["aci"] == 0.0   # canli: false -> nefes/eğim yok
    for k in (6, 10, 40, 100):                                # kareler hatasız (bulanıklık + eğim yolları)
        assert ku.kare(k).size == (320, 180)
    # kapalı hareket dili: eski davranış (eğim yok)
    v2 = _video(v.raw["bolumler"], hareket={"ikincil": False, "canli": False, "bulaniklik": False})
    z2 = zaman.hesapla(v2, tahmin=True)
    a2 = render.KareUretici(v2, z2, 0, 320, 180).cz.karakterler[0]
    assert all(a2.poz(t)["aci"] == 0.0 for t in np.linspace(0, 4, 20))


def test_kesmede_yarim_kalmasin_ve_kose_sabit_genislik():
    from wojak.uzun.sahneler import Baglam, kesmede_yarim_kalmasin
    from wojak.uzun.ust import KoseGostergesi, kose_olaylari
    assert kesmede_yarim_kalmasin(1.0, 2.0, 0.3, 3.1, "kesme") == 3.1 - 1.0 + 1.0  # kesmede yarıda: sonuna dek tam
    assert kesmede_yarim_kalmasin(1.0, 2.0, 0.3, 3.1, None) == 2.0                  # çapraz geçişte söner
    assert kesmede_yarim_kalmasin(1.0, 1.0, 0.3, 5.0, "kesme") == 1.0               # erken biten: dokunulmaz
    d = kesmede_yarim_kalmasin(1.0, 5.0, 0.3, 3.1, "donuk")                        # donan karede yazı kalmasın
    assert abs(1.0 + d + 0.3 - (3.1 - 0.04)) < 1e-9
    v = _video([{"baslik": "a", "sahneler": [{"tip": "metin", "metin": "x", "sure": 4,
                 "kose": {"metin": "GÜN {} / 12", "deger": 0},
                 "olaylar": [{"tip": "kose", "deger": 11, "t": 0.5, "sure": 1.0},
                             {"tip": "kose", "deger": "????", "takili": True, "t": 2.5}]}]}])
    z = zaman.hesapla(v, tahmin=True)
    s = z.sahneler[0]
    k = KoseGostergesi(s, Baglam(v, 1920, 1080), kose_olaylari(s))
    boylar = {k._kutu(*k._metin(i / 30)[:2]).size for i in range(120)}
    assert len(boylar) == 1, boylar                          # sayarken/takılırken kutu boyu değişmez


def test_sayac_tekerlek_yuvarlanma():
    from wojak.uzun import render
    v = _video([{"baslik": "a", "sahneler": [{"tip": "sayac", "deger": 20000, "sure": 4}]}])
    z = zaman.hesapla(v, tahmin=True)
    cz = render.KareUretici(v, z, 0, 480, 270).cz
    b = cz.bolumler[0]
    # 8. tur: basamak sayısı baştan hedefinki (20.000 -> 5 tekerlek); öndekiler boş
    assert b["basamak"] == 5
    teker = [q for q in cz._yuvarlanan(19.5, 0.01, b) if not isinstance(q[0], str)]
    assert len(teker) == 5 and all(q[2] for q in teker[:3]) and not teker[3][2]
    # kilometre sayacı: 19,5'te onlar tekerleği 1,5'te (alttakiler 9'dan 0'a geçerken döner)
    assert abs(teker[3][0] - 1.5) < 1e-9 and abs(teker[4][0] - 9.5) < 1e-9
    # 9.999,5 -> öndeki boş tekerlek boştan 1'e yarı yolda (eskiden 4 basamak "0.000"a dönüyordu)
    t9 = [q for q in cz._yuvarlanan(9999.5, 0.01, b) if not isinstance(q[0], str)]
    assert t9[0][2] and abs(t9[0][0] - 0.5) < 1e-6
    ayrac = [q for q in cz._yuvarlanan(1234.0, 0.01, b) if q[0] == "."]
    assert ayrac and ayrac[0][1] == 1.0                     # binlik ayırıcı (solu dolu: görünür)
    # sayarken katman genişliği hiç değişmez (sayı yana kaymaz); görünen ortası yumuşakça kayar
    ws = {cz._say_katmani(b["t0"] + (b["t1"] - b["t0"]) * i / 40, b).width for i in range(41)}
    assert max(ws) - min(ws) <= 1, ws
    axs = [cz._say_katmani(b["t0"] + (b["t1"] - b["t0"]) * i / 120, b).info["ax"] for i in range(121)]
    assert max(abs(a_ - b_) for a_, b_ in zip(axs, axs[1:])) < cz.hucre * 0.25   # hiçbir karede yarım hücre sıçrama yok
    assert cz.kare(1.0).size == (480, 270)


def test_ses_senkronu_ve_sessizlikten_donus():
    """Efekt vuruşu görüntüdeki an ile aynı karede: damga kâğıda değdiğinde (INIS), deklanşör baskı değdiğinde,
    whoosh tepesi girişin en hızlı karelerinde; sessizlikten dönen müzik en az 1,6 sn'de açılır."""
    from wojak.uzun import ses
    from wojak.uzun.ust import Damga
    v = _video([{"baslik": "a", "sahneler": [
        {"tip": "foto", "gorsel": KUTU, "sure": 3, "olaylar": [{"tip": "damga", "metin": "X", "t": 1.0},
                                                             {"tip": "muzik", "db": -40, "t": 2.0}]},
        {"tip": "wojak", "arka": KUTU, "sure": 3, "karakterler": [{"id": "a", "gorsel": KL + "sakin.png",
                                                                    "giris": 0.5}]}]}])
    z = zaman.hesapla(v, tahmin=True)
    ef = ses.otomatik_efektler(z)
    assert any(a == "damga" and abs(t - (1.0 + Damga.INIS)) < 1e-6 for t, a, _ in ef)
    assert any(a == "shutter" and abs(t - 0.48) < 1e-6 for t, a, _ in ef)
    b = z.sahne_basi(z.sahneler[1])
    assert any(a == "whoosh_kisa" and abs(t - (b + 0.5 + 0.1 - ses.WHOOSH_TEPE)) < 1e-6 for t, a, _ in ef)
    eg = ses.muzik_egrisi(z)
    donus = [r for t, db, r in eg if db == 0.0]
    assert donus and donus[0] >= ses.SESSIZLIK_DONUS


def test_kapanis_sahnesi():
    from wojak.uzun import render, ses
    from wojak.uzun.kapanis import kapanis_zamanlari, varsayilan_yorum
    from wojak.uzun.sahneler import vuruslar
    sahne = {"tip": "kapanis", "arka": KUTU, "ust": "SON SORU", "soru": "Türkiye'yi ne korudu?",
             "secenekler": [{"metin": "A kişi", "gorsel": KL + "sakin.png"}, "B kişi",
                            {"metin": "Kural", "gorsel": KUTU}],
             "karakter": {"gorsel": KL + "sakin.png", "yuz": KL + "mutlu.png"},
             "satirlar": ["Bir sonraki hikâyede görüşmek üzere."],
             "olaylar": [{"tip": "tikla", "hedef": "zil", "t": 4.4}, {"tip": "secenek", "indeks": 2, "t": 8.0}]}
    v = _video([{"baslik": "a", "sahneler": [{"tip": "metin", "metin": "x", "sure": 2}, sahne]}])
    z = zaman.hesapla(v, tahmin=True)
    s = z.sahneler[1]
    assert abs(s.sure_hesap - 10.0) < 0.05                  # varsayılan en az 10 sn
    zt = kapanis_zamanlari(s)
    assert zt["tik"]["zil"] == 4.4 and zt["vurgu"] == [(8.0, 2)] and zt["tik"]["abone"] < zt["tik"]["zil"]
    assert varsayilan_yorum(3) == "A mı, B mi, yoksa C mi?\nCevabını yorumlara yaz"
    vu = vuruslar(s)
    assert 4.4 in vu and 8.0 in vu
    ef = [a for t, a, _ in ses.otomatik_efektler(z) if t >= z.sahne_basi(s)]
    assert "klik" in ef and "zil" in ef and "pop" in ef and "tus" in ef
    assert not paket.bitis_denetle(z)                       # son sahne, 5-20 sn: uyarı yok
    assert "video kutusu EKLEME" in paket.bitis_maddesi(z)
    ku = render.KareUretici(v, z, 1, 480, 270)
    kareler = [np.asarray(ku.kare(k), np.float32) for k in (3, 60, 100, 130, 200, 290)]
    for a, b in zip(kareler, kareler[1:]):
        assert np.abs(a - b).mean() > 0.3                   # sahne boyunca hareket var
    # bindirme: ilk karesi önceki sahnenin son karesi
    sahne2 = dict(sahne, bindirme=True)
    sahne2.pop("arka")
    v2 = _video([{"baslik": "a", "sahneler": [{"tip": "metin", "metin": "x", "sure": 2}, sahne2]}])
    z2 = zaman.hesapla(v2, tahmin=True)
    onceki = np.asarray(render.son_kare(v2, z2, 0, 320, 180), np.float32)
    ilk = np.asarray(render.KareUretici(v2, z2, 1, 320, 180).cz.kare(0.0), np.float32)
    assert np.abs(onceki - ilk).mean() < 8
    # hatalar
    _hata_bekle(lambda: _video([{"baslik": "a", "sahneler": [dict(sahne, secenekler=["a", "b", "c", "d"])]}]),
                "0-3")
    _hata_bekle(lambda: _video([{"baslik": "a", "sahneler": [dict(sahne, olaylar=[{"tip": "tikla", "hedef": "x"}])]}]),
                "tikla")
    _hata_bekle(lambda: _video([{"baslik": "a", "sahneler": [dict(sahne, dugmeler=["abone"], olaylar=[
        {"tip": "tikla", "hedef": "begen"}])]}]), "dugmeler")


def test_harita_rota_ve_belge_isaretleri():
    from wojak.uzun import render, ses
    v = _video([{"baslik": "a", "sahneler": [
        {"tip": "harita", "bolge": "avrupa", "ulkeler": ["DEU"], "sure": 4,
         "olaylar": [{"tip": "rota", "a": "DEU", "b": "TUR", "t": 1.0, "kesik": True, "etiket": "yol"},
                     {"tip": "rota", "a": [13.4, 52.5], "b": [32.9, 39.9], "t": 1.5, "sure": 0.8}]},
        {"tip": "manset", "gorsel": KUTU, "kutular": [[0.1, 0.1, 0.5, 0.3], [0.2, 0.5, 0.6, 0.6]], "sure": 3,
         "olaylar": [{"tip": "vurgula", "kutu": 1, "t": 0.5, "stil": "daire"},
                     {"tip": "vurgula", "kutu": 2, "t": 1.0, "stil": "alt_cizgi", "renk": "mavi"}]}]}])
    z = zaman.hesapla(v, tahmin=True)
    ef = ses.otomatik_efektler(z)
    assert any(a == "blip" and abs(t - 2.2) < 1e-6 for t, a, _ in ef)     # varışta blip
    ku = render.KareUretici(v, z, 0, 480, 270)
    once, sonra = np.asarray(ku.kare(25), np.float32), np.asarray(ku.kare(90), np.float32)
    assert np.abs(once - sonra).max() > 60                  # rota çizildi
    km = render.KareUretici(v, z, 1, 480, 270)
    assert np.abs(np.asarray(km.kare(10), np.float32) - np.asarray(km.kare(80), np.float32)).max() > 60
    _hata_bekle(lambda: _video([{"baslik": "a", "sahneler": [{"tip": "sayac", "deger": 1, "olaylar": [
        {"tip": "rota", "a": "DEU", "b": "TUR"}]}]}]), "yalnız")
    _hata_bekle(lambda: _video([{"baslik": "a", "sahneler": [{"tip": "manset", "gorsel": KUTU, "kutular": [[0, 0, 1, 1]],
                                                              "olaylar": [{"tip": "vurgula", "kutu": 1, "stil": "x"}]}]}]),
                "stil")


def test_metin_kelimeleri_ortak_taban():
    """Kelime kelime dizilen yazıda her kelime satır yüksekliğinde: çıkıntısız kelime ('ne') yukarı kaymaz."""
    from wojak.uzun import cizim as C
    a = C.yazi("Türkiye'yi", C.FONT_DIALOG, 80, C.BEYAZ, dikey_kirp=False)
    b = C.yazi("ne", C.FONT_DIALOG, 80, C.BEYAZ, dikey_kirp=False)
    assert a.height == b.height
    assert C.yazi("ne", C.FONT_DIALOG, 80, C.BEYAZ).height < b.height


def test_tur8_animasyon_duzeltmeleri():
    """8. tur: sıkışmasız yüz geçişi (kapı ara kareleri), kamera sarsıntısı, havadaki nesneye gölge, aynı karakterli
    çapraz geçiş uyarısı, kapanışta nötr bitiş, sayaçta bir anda gelen değer."""
    from wojak.uzun import render
    from wojak.uzun.cli import gecis_denetimi, karakter_ailesi
    from wojak.uzun.kapanis import KapanisCizici, kapanis_zamanlari
    from wojak.uzun.sahneler import Baglam, Karakter, karakter_zamanlari
    AN = "uzun/talidomit-turkiye/chars/anlatici_v2_sakin.png"
    sah = {"tip": "wojak", "arka": KUTU, "sure": 2.0,
           "karakterler": [{"id": "a", "gorsel": KL + "sakin.png", "x": 0.3, "giris": False},
                           {"id": "k", "gorsel": KL + "sakin.png", "x": 0.7, "alt": -0.3, "bakis": "on",
                            "giris": False, "canli": False, "golge": True}],
           "olaylar": [{"tip": "yuz", "karakter": "a", "gorsel": KL + "mutlu.png", "sik": False, "t": 0.5},
                       {"tip": "yuz", "karakter": "a", "gorsel": KL + "sakin.png", "t": 1.0},
                       {"tip": "sarsinti", "t": 1.5, "guc": 10, "sure": 0.2}]}
    v = _video([{"baslik": "a", "sahneler": [sah]}])
    z = zaman.hesapla(v, tahmin=True)
    s = z.sahneler[0]
    zam = karakter_zamanlari(s)
    assert zam["a"]["sik"] == [1.0] and len(zam["a"]["yuz"]) == 2     # sik: false sıkışma listesine girmez
    k = Karakter(s.p["karakterler"][0], zam["a"], Baglam(v, 480, 270), 0)
    assert k.poz(0.5)["sy"] == k.poz(0.5)["sx"] or abs(k.poz(0.5)["sy"] - 1) < 0.02   # 0,5'te sıkışma yok
    assert k.poz(1.0)["sy"] < 0.95                                    # 1,0'da var
    ku = render.KareUretici(v, z, 0, 480, 270)
    a0 = np.asarray(ku.cz.kare(1.45), np.float32)
    a1 = np.asarray(ku.cz.kare(1.52), np.float32)                    # sarsıntı: kare kayar
    a2 = np.asarray(ku.cz.kare(1.8), np.float32)                     # sarsıntı bitti
    assert np.abs(a1 - a0).mean() > np.abs(a2 - a0).mean() + 0.5
    # gölge: aynı nesne gölgesiz çizilince sağ altı daha açık
    sah2 = dict(sah, karakterler=[sah["karakterler"][0], dict(sah["karakterler"][1], golge=False)])
    v2 = _video([{"baslik": "a", "sahneler": [sah2]}])
    z2 = zaman.hesapla(v2, tahmin=True)
    b0 = np.asarray(render.KareUretici(v2, z2, 0, 480, 270).cz.kare(0.2), np.float32)
    g0 = np.asarray(ku.cz.kare(0.2), np.float32)
    assert (b0 - g0).mean() > 0.2                                     # gölge kareyi koyulaştırır
    # aynı karakter ailesi çapraz geçişte uyarı verir (chars/ dışındaki nesne aile sayılmaz)
    assert karakter_ailesi(AN) == "anlatici_v2" and karakter_ailesi(KL + "sakin.png") is None
    w = lambda g: {"tip": "wojak", "arka": KUTU, "sure": 2.0, "gecis": g,
                   "karakterler": [{"id": "z", "gorsel": AN.replace("sakin", "fark")}]}
    for g, n in (("gecis", 1), ("kesme", 0), ("kaydir", 0)):
        v3 = _video([{"baslik": "a", "sahneler": [{"tip": "wojak", "arka": KUTU, "sure": 2.0,
                                                     "karakterler": [{"id": "z", "gorsel": AN}]}, w(g)]}])
        assert len(gecis_denetimi(zaman.hesapla(v3, tahmin=True))) == n
    # kapanış: son karede hiçbir seçenek tek başına vurgulu değil (üçü eşit)
    kap = {"tip": "kapanis", "arka": KUTU, "soru": "Ne korudu?", "secenekler": ["A", "B", "C"], "sure": 9.5,
           "satirlar": ["Sizce hangisi?"]}
    v4 = _video([{"baslik": "a", "sahneler": [kap]}])
    z4 = zaman.hesapla(v4, tahmin=True)
    zt = kapanis_zamanlari(z4.sahneler[0])
    assert zt["hepsi"] is not None and zt["hepsi"] <= 9.5 - 0.4
    kc = KapanisCizici(z4.sahneler[0], Baglam(v4, 480, 270))
    son = [kc._vurgu(9.45, i) for i in range(3)]
    assert max(son) - min(son) < 1e-6 and son[0] < 0.6
    # sayaç: bir anda gelen değer (sure: 0) bulanık dönmez, yumruk gibi büyükten iner
    say = {"tip": "sayac", "deger": 20000, "sure": 4, "sure_say": 1.0,
           "olaylar": [{"tip": "deger", "deger": 17, "onek": "en az ", "renk": "kirmizi", "t": 2.0, "sure": 0}]}
    v5 = _video([{"baslik": "a", "sahneler": [say]}])
    cz = render.KareUretici(v5, zaman.hesapla(v5, tahmin=True), 0, 480, 270).cz
    b = cz.bolumler[1]
    assert b["ani"] and cz._deger(2.0, b) == 17 and b["basamak"] == 2
    tek = [q for q in cz._yuvarlanan(17, 0.0, b) if not isinstance(q[0], str)]
    assert [round(q[0]) for q in tek] == [1, 7]


def test_dokuz_tur_motor_ekleri():
    """9. tur: karanlıktan geçiş, kâğıt zemin karartması, panelde sayan sayılar (sabit genişlik), log sayaç ve boş
    tekerlek, `it` olayı (kamera vurgu itmesi), `yuz {buyu}`, balon `agiz`, SRT bölmesinin sessizliğe oturması,
    sure: 0'dan önce eski etiketin sönmesi, daktilonun geçişten sonra başlaması."""
    from PIL import Image
    from wojak.uzun import render
    from wojak.uzun.bilgi import _Panel, _hizali_sayi
    from wojak.uzun.sahneler import Baglam, cizici, metin_zamanlari
    # karart geçişi: ortada koyu, iki görüntü üst üste binmez
    a = Image.new("RGB", (64, 36), (240, 240, 240))
    b = Image.new("RGB", (64, 36), (200, 40, 40))
    orta = np.asarray(render.gecis_uygula("karart", a, b, 4, 10), np.float32).mean()
    assert orta < 60
    assert np.asarray(render.gecis_uygula("karart", a, b, 9, 10), np.float32)[..., 1].mean() < 80   # sonda yeni kare
    assert spec.GECIS_KARE["karart"] == 10
    # panel sayısı: sağdan hizalı, sayarken genişlik sabit
    assert _hizali_sayi("1.267", 999) == "  999"
    assert _hizali_sayi("20.000", 1500) == " 1.500"
    v = _yeni_tipler_video()
    c = Baglam(v, 480, 270)
    pn = _Panel({"metin": "1.267 doktor\n≈20.000 hasta", "zemin": "kagit", "say": True, "zoom": 1.12}, c, 1)
    ws = {pn.metin_katmani(u).size for u in (0.0, 0.4, 0.9, 1.3, 3.0)}
    assert len(ws) == 1 and pn.metin_zoom == 1.12
    # kâğıt zemin karartması
    from wojak.uzun import zemin as Z
    acik = np.asarray(Z.Zemin(c, {"zemin": "kagit"}).taban, np.float32).mean()
    koyu = np.asarray(Z.Zemin(c, {"zemin": "kagit", "karart": 0.2}).taban, np.float32).mean()
    assert koyu < acik * 0.85
    # log sayaç + boş tekerlek
    say = {"tip": "sayac", "deger": 300000000, "olcek": "log", "sure": 4, "sure_say": 3.0, "satirlar": []}
    v5 = _video([{"baslik": "a", "sahneler": [say]}])
    cz = render.KareUretici(v5, zaman.hesapla(v5, tahmin=True), 0, 480, 270).cz
    b0 = cz.bolumler[0]
    vs = [cz._deger(b0["t0"] + k * 0.3, b0) for k in range(11)]
    assert all(y >= x for x, y in zip(vs, vs[1:])) and vs[-1] == 300000000
    assert 1 <= vs[1] <= 1e5 and vs[5] < 1e6                          # ilk anlarda küçük sayılar (8 basamak sıçraması yok)
    parca = cz._yuvarlanan(1500000, 3e6, b0)
    tek = [q for q in parca if not isinstance(q[0], str)]
    assert tek[0] == (0.0, 0.0, True) and tek[1] == (0.0, 0.0, True)    # öndeki iki tekerlek boş ("01.500.000" yok)
    # `it` olayı ve yuz `buyu`, balon `agiz`
    AN = "uzun/talidomit-turkiye/chars/anlatici_v2_sakin.png"
    ACIK = "uzun/talidomit-turkiye/chars/anlatici_v2_saskin.png"
    KUTU = "uzun/talidomit-turkiye/img/doku_kagit.jpg"
    DOZ = "uzun/talidomit-turkiye/img/kompozit/doz_"
    sah = {"tip": "wojak", "arka": KUTU, "sure": 4.0, "kamera": {"zoom": [1.0, 1.0], "it": 0},
           "karakterler": [{"id": "z", "gorsel": AN, "x": 0.7}, {"id": "s", "gorsel": DOZ + "1.png", "x": 0.3,
                                                                  "bakis": "on", "canli": False}],
           "olaylar": [{"tip": "it", "t": 1.0, "guc": 0.1, "sure": 0.5, "x": 0.7},
                       {"tip": "yuz", "karakter": "s", "gorsel": DOZ + "3.png", "t": 2.0, "buyu": True},
                       {"tip": "balon", "karakter": "z", "metin": "Evet!", "t": 2.5, "sure": 1.0, "agiz": ACIK}]}
    v6 = _video([{"baslik": "a", "sahneler": [sah]}])
    z6 = zaman.hesapla(v6, tahmin=True)
    cw = cizici(z6.sahneler[0], Baglam(v6, 480, 270))
    assert abs(cw.kam(0.5).z - 1.0) < 1e-6 and abs(cw.kam(2.0).z - 1.1) < 1e-3 and cw.kam(2.0).cx > 0.5
    ks = cw.karakterler[1]
    assert ks.buyu and ks.buyu[0][1] < 1.0
    assert ks.poz(2.02)["sx"] < 0.95 and abs(ks.poz(2.6)["sx"] - 1.0) < 0.02
    kz = cw.karakterler[0]
    acik = {kz.poz(2.5 + i / 30)["vi"] for i in range(30)}
    assert kz.agiz and kz.agiz[0][2][0] in acik and 0 in acik          # hecelerde açık / kapalı ağız
    # 11. tur: [yarık, açık] ağız: kapalıdan açığa atlamaz, her durum en az 4 kare
    sah["olaylar"][-1]["agiz"] = [AN.replace("sakin", "dusunceli"), ACIK]
    v6b = _video([{"baslik": "a", "sahneler": [sah]}])
    kz2 = cizici(zaman.hesapla(v6b, tahmin=True).sahneler[0], Baglam(v6b, 480, 270)).karakterler[0]
    yar, ac = kz2.agiz[0][2]
    dz = [{0: 0, yar: 1, ac: 2}[kz2.poz(2.5 + i / 30)["vi"]] for i in range(48)]
    assert 2 in dz and all(abs(x - y) <= 1 for x, y in zip(dz, dz[1:]))
    kosu = [len(list(g)) for _, g in __import__("itertools").groupby(dz)]
    assert min(kosu[:-1]) >= 4
    # daktilo çapraz geçiş bitince başlar
    dk = {"tip": "metin", "metin": "ANNE KARNINDA.", "yazim": "daktilo", "gecis": "gecis", "sure": 2.0,
          "olaylar": [{"tip": "basla", "t": 0.0}]}
    v7 = _video([{"baslik": "a", "sahneler": [{"tip": "metin", "metin": "x", "sure": 2.0}, dk]}])
    s7 = zaman.hesapla(v7, tahmin=True).sahneler[1]
    assert metin_zamanlari(s7)["daktilo"][0] >= 8 / 30
    # SRT: tahmini sınır en yakın iç sessizliğe oturur
    assert altyazi.sessizlige_otur([3.6], ((4.3, 5.1),), 6.2) == [5.1 - 0.08]
    assert altyazi.sessizlige_otur([2.0], ((5.0, 5.3),), 6.2) == [2.0]       # uzak sessizlik: tahmin kalır
    # sure: 0'dan önce eski etiket söner
    say2 = {"tip": "sayac", "deger": 20000, "etiket": "hasta", "sure": 4, "sure_say": 1.0,
            "olaylar": [{"tip": "deger", "deger": 17, "etiket": "bebek", "t": 2.0, "sure": 0}]}
    v8 = _video([{"baslik": "a", "sahneler": [say2]}])
    k8 = render.KareUretici(v8, zaman.hesapla(v8, tahmin=True), 0, 480, 270).cz
    once = np.asarray(k8.kare(1.5), np.float32)
    hemen = np.asarray(k8.kare(1.99), np.float32)
    assert np.abs(once - hemen)[int(270 * 0.62):].mean() > 0.3        # etiket bandı değişti (söndü)


# ---------------------------------------------------------------- 10. tur (hakem 9: sayaç, yerleşim, altyazı)

def _okuma(parcalar) -> int:
    """Tekerleklerin okunan değeri: her tekerlek en yakın rakamı gösterir (boş = 0)."""
    tek = [q for q in parcalar if not isinstance(q[0], str)]
    n = 0
    for konum, _, bos in tek:
        n = n * 10 + (0 if bos and konum < 0.5 else int(round(konum)) % 10)
    return n


def _sayac_cizici(say: dict, W: int = 480):
    from wojak.uzun import render
    v = _video([{"baslik": "a", "kart": False, "sahneler": [say]}])
    z = zaman.hesapla(v, tahmin=True)
    return render.KareUretici(v, z, 0, W, W * 9 // 16).cz, z


def test_sayac_tekerlek_hic_geri_okunmaz():
    """Animasyon hakemi S1: taşıma geriye okunmamalı ("38 -> 30 -> 40", "292,9 M -> 202,0 M", "≈6.318 -> ≈0.310").
    Her karede tekerleklerin okunuşu tekdüze; öndeki sıfır hiç görünmez; boş tekerlek ancak boştan 1'e döner."""
    durumlar = [
        {"tip": "sayac", "deger": 61, "sonek": "", "sure_say": 4.2, "sure": 5.2},
        {"tip": "sayac", "deger": 20000, "sure": 4},
        {"tip": "sayac", "deger": 300000000, "olcek": "log", "sure_say": 3.0, "sure": 4},
        {"tip": "sayac", "deger": [60, 0], "sure_say": 3.0, "sure": 4},
        {"tip": "sayac", "deger": 1267, "sonek": "", "sure": 5,
         "olaylar": [{"tip": "deger", "deger": 20000, "onek": "≈", "t": 2.2, "sure": 1.2}]},
    ]
    for say in durumlar:
        cz, z = _sayac_cizici(say)
        dt = 1 / 30
        onceki = None
        for k in range(z.sahneler[0].n_kare):
            t = k * dt
            _, b = cz._bolum(t)
            v, vo = cz._deger(t, b), cz._deger(t - dt, b)
            p = cz._yuvarlanan(v, abs(v - vo), b, vo)
            n = _okuma(p)
            artan = b["b"] >= b["a"]
            if onceki is not None and onceki[0] is b:
                assert (n >= onceki[1]) if artan else (n <= onceki[1]), (say, t, onceki[1], n)
            onceki = (b, n)
            tek = [q for q in p if not isinstance(q[0], str)]
            for konum, iz, bos in tek:
                if bos:
                    assert konum < 1.0 and (konum < 1e-9 or iz < 0.5)   # boş tekerlek yalnız boştan 1'e döner
            dolu = [q for q in tek if not q[2]]
            if dolu and n > 0 and len(dolu) > 1:
                assert int(round(dolu[0][0])) % 10 != 0, (say, t, p)   # öndeki sıfır yok
        # son değer yerleşir
        son = cz.bolumler[-1]
        assert _okuma(cz._yuvarlanan(son["b"], 0.0, son)) == int(son["b"])


def test_sayac_tekerlek_keskin_rakam_ve_hizli_sayi():
    """Hızlı sayımda her kare round(v) (sayısal), iz keskin rakamın ALTINDA (rakam bulanıp "0" okunmaz); duran
    tekerlekte iz yok (eskiden sayının hızıyla duran 9 da bulanıyordu)."""
    cz, _ = _sayac_cizici({"tip": "sayac", "deger": 20000, "sure": 4}, 960)
    b = cz.bolumler[0]
    p = cz._yuvarlanan(9775.84, 1078.4, b, 8697.4)
    assert _okuma(p) == 9776
    tek = [q for q in p if not isinstance(q[0], str)]
    assert tek[0][2] and tek[2][1] > 0 and tek[-1][1] > 0          # yüzler döner (iz var), on binler boş
    assert tek[1][1] == 0.0                                          # 12. tur: binler ~1 hücre/kare: keskin
    # yavaş: hiçbir tekerlekte iz yok (12. tur: adım adım geçiş; bulanık kopya rakamın üstünde gri bant gibiydi)
    p = cz._yuvarlanan(1262.4, 0.3, b, 1262.1)
    tek = [q for q in p if not isinstance(q[0], str)]
    assert all(q[1] == 0.0 for q in tek)
    # izli tekerlekte rakamın kendi pikselleri keskin olanla aynı
    renk = (240, 240, 240)
    keskin = np.asarray(cz._teker(renk, 8.0, 0.0), np.float32)
    izli = np.asarray(cz._teker(renk, 8.0, 0.75), np.float32)
    opak = keskin[..., 3] >= 250
    assert opak.sum() > 50 and np.abs(izli[opak] - keskin[opak]).max() <= 2
    assert izli[..., 3][~opak].mean() > keskin[..., 3][~opak].mean()   # iz rakamın çevresinde
    # 12. tur (animasyon hakemi M1): orta hızda (birler kare başına 0,5-2,5) iz yok; iz yalnız rakamın kendi dikey
    # izi (komşu rakamların parçası yok: rakamın hiç pikseli olmayan sütunlarda iz de yok)
    p = cz._yuvarlanan(35.2, 1.2, b, 34.0)
    assert _okuma(p) == 35 and all(q[1] == 0.0 for q in p if not isinstance(q[0], str))
    for d in (1, 5, 7):
        kes = np.asarray(cz._rakam(str(d), renk))[..., 3]
        iz1 = cz._rakam_izi(renk, d, 0.75)[..., 3]
        bos_sutun = kes.max(axis=0) == 0
        assert bos_sutun.any() and iz1[:, bos_sutun].max() < 1e-3
    # önek ilk görünen rakamın solunda kalır (9.999 -> 10.000 geçişinde "≈" yeni "1"in üstüne binmez)
    cz2, _ = _sayac_cizici({"tip": "sayac", "deger": 1267, "sonek": "", "sure": 5, "olaylar": [
        {"tip": "deger", "deger": 20000, "onek": "≈", "t": 2.2, "sure": 1.2}]}, 960)
    b2 = cz2.bolumler[1]
    for k in range(int(b2["t0"] * 30), int(b2["t1"] * 30) + 2):
        lay = cz2._say_katmani(k / 30, b2)
        assert lay.info["onek_sag"] <= lay.info["rakam_sol"] + 1.0, (k, lay.info)


def test_sayac_yavas_adim_adim_yirtik_rakam_yok():
    """12. tur (animasyon hakemi M1): 0 -> 61 sayımının yavaş kuyruğunda adım ~2,75 karede bir geliyordu ve neredeyse
    her kare yarım dönmüş iki rakamdı (yırtık rakam, gri bulanıklık bandı, pencerenin altında gelen rakamın tepesi).
    Artık gösterilen değer round(v): yeni tam sayı 2 karede geçer (%87,5, %100), sonra durur; geçişteki tekerlek
    şeritten kesilmez (eski rakam yukarı kayıp söner, yenisi aşağıdan belirir; pencere kenarında sert kesik yok)."""
    cz, _ = _sayac_cizici({"tip": "sayac", "deger": 61, "sonek": "", "sure_say": 4.2, "sure": 6}, 960)
    b = cz.bolumler[0]
    dt = 1 / 30
    ks = range(int(b["t0"] * 30), int(b["t1"] * 30) + 15)
    gos = [cz._gosterilen(k * dt, b) for k in ks]
    hiz = [abs(cz._deger(k * dt, b) - cz._deger(k * dt - dt, b)) for k in ks]
    yavas = [g for g, h in zip(gos, hiz) if h <= cz.HIZLI]
    assert len(yavas) > 20
    kesirli = [g for g in yavas if abs(g - round(g)) > 1e-6]
    tam = [g for g in yavas if abs(g - round(g)) <= 1e-6]
    assert len(kesirli) < len(tam)                                    # çoğu kare tam bir sayı
    assert all(abs(g - round(g)) >= 0.1 for g in kesirli)            # geçiş karesi yeniye yakın (%87,5)
    assert all(b_ >= a_ - 1e-9 for a_, b_ in zip(gos, gos[1:]))      # hiç geri gitmez
    assert abs(gos[-1] - 61) < 1e-9
    renk = (240, 240, 240)
    ara = np.asarray(cz._teker(renk, 1.875, 0.0), np.float32)[..., 3]
    tam1 = np.asarray(cz._teker(renk, 2.0, 0.0), np.float32)[..., 3]
    assert ara[0].max() < 30 and ara[-1].max() < 30                  # kenarda kesik parça yok
    assert ara.sum() > 0.8 * tam1.sum()                               # yeni rakam neredeyse tam


def test_sayac_yerlesip_okunur_ve_basla_sure():
    """Animasyon hakemi M2: 1.267 sayımı bitmeden 20.000 geliyordu. Değer yeni değişimden en az `tut` (0,6) önce
    yerleşir: sayım kısalır (en az 0,6 sn), yetmezse sonraki değer ertelenir; `basla {sure}` sayım süresi; son
    sayım sahne bitmeden; kontrol bildirir."""
    from wojak.uzun.cli import sayac_denetimi
    from wojak.uzun.sahneler import SAYAC_EN_AZ, SAYAC_TUT, sayac_bolumleri
    say = {"tip": "sayac", "deger": 1267, "sonek": "", "sure": 7, "olaylar": [
        {"tip": "basla", "t": 0.3}, {"tip": "deger", "deger": 20000, "t": 2.21, "sure": 1.2}]}
    v = _video([{"baslik": "a", "kart": False, "sahneler": [say]}])
    z = zaman.hesapla(v, tahmin=True)
    b = sayac_bolumleri(z.sahneler[0])
    assert b[0]["t1"] <= b[1]["t0"] - SAYAC_TUT + 1e-6 and b[0]["kisaldi"] > 0.8
    assert any("kısaltıldı" in x for x in sayac_denetimi(z))
    # basla sure
    say2 = dict(say, olaylar=[{"tip": "basla", "t": 0.3, "sure": 1.0},
                              {"tip": "deger", "deger": 20000, "t": 2.21, "sure": 1.2}])
    v = _video([{"baslik": "a", "kart": False, "sahneler": [say2]}])
    b = sayac_bolumleri(zaman.hesapla(v, tahmin=True).sahneler[0])
    assert abs(b[0]["t1"] - 1.3) < 1e-9 and not b[0].get("kisaldi")
    # çok yakın değişim: sayım en az 0,6 sn, sonraki değer ertelenir
    say3 = dict(say, olaylar=[{"tip": "basla", "t": 0.3}, {"tip": "deger", "deger": 17, "t": 0.6, "sure": 0}])
    v = _video([{"baslik": "a", "kart": False, "sahneler": [say3]}])
    z = zaman.hesapla(v, tahmin=True)
    b = sayac_bolumleri(z.sahneler[0])
    assert abs(b[0]["t1"] - (0.3 + SAYAC_EN_AZ)) < 1e-9 and b[1]["ertelendi"] > 0
    assert b[1]["t0"] - b[0]["t1"] >= 0.3 - 1e-9
    assert any("ertelendi" in x for x in sayac_denetimi(z))
    # son sayım sahne sonundan tut kadar önce biter
    v = _video([{"baslik": "a", "kart": False, "sahneler": [{"tip": "sayac", "deger": 50, "sure": 2.0,
                                                               "sure_say": 3.0}]}])
    b = sayac_bolumleri(zaman.hesapla(v, tahmin=True).sahneler[0])
    assert b[0]["t1"] <= 2.0 - SAYAC_TUT + 1e-6
    _video([{"baslik": "a", "sahneler": [{"tip": "sayac", "deger": 5, "tut": 0.8}]}])   # `tut` geçerli anahtar


def test_sayac_anlik_deger_yuvarlanarak_gelir():
    """Animasyon hakemi S2: "≈20.000" -> "en az 17" tek karede değişiyordu. Şimdi 0,26 sn'de tekerlek gibi
    yuvarlanır: değişim birkaç kareye yayılır; vuruş efekti yeni sayı oturduğunda."""
    from wojak.uzun import ses
    from wojak.uzun.sahneler import SAYAC_GECIS
    say = {"tip": "sayac", "deger": 20000, "onek": "≈", "sonek": "", "sure": 4, "sure_say": 1.0, "olaylar": [
        {"tip": "deger", "deger": 17, "onek": "en az ", "renk": "kirmizi", "t": 2.5, "sure": 0}]}
    cz, z = _sayac_cizici(say)
    H = 270
    t0 = cz.bolumler[1]["t0"]
    kareler = [np.asarray(cz.kare(t0 + (k - 2) / 30), np.float32)[int(H * 0.25):int(H * 0.65)]
               for k in range(int(SAYAC_GECIS * 30) + 6)]
    farklar = [np.abs(b_ - a_).mean() for a_, b_ in zip(kareler, kareler[1:])]
    assert sum(1 for f in farklar if f > 0.5) >= 3, farklar          # birkaç karede ilerler
    assert max(farklar) < 0.7 * sum(farklar), farklar                 # tek karede değil
    vurus = [t for t, a, _ in ses.otomatik_efektler(z) if a == "hit" and t > t0]
    assert vurus and abs(vurus[0] - cz.bolumler[1]["varis"]) < 1e-6 and vurus[0] > t0


def test_yuz_kutusu_ve_geometri():
    from PIL import Image
    from wojak.uzun import yerlesim as Y
    im = Image.open(KOK / "uzun/talidomit-turkiye/chars/anlatici_v2_sakin.png").convert("RGBA")
    ab, yb = Y.alfa_kutusu(im), Y.yuz_kutusu(im)
    h = ab[3] - ab[1]
    assert yb[1] == ab[1] and 0.4 * h <= yb[3] - yb[1] <= 0.9 * h and yb[0] >= ab[0] and yb[2] <= ab[2]
    kare = Y.dikdortgen(0, 0, 10, 10)
    assert Y.derinlik(kare, Y.dikdortgen(5, 5, 20, 20)) == 5
    assert Y.derinlik(kare, Y.dikdortgen(13, 0, 20, 10)) < 0
    don = Y.donuk_dikdortgen(0, 0, 10, 10, 45)
    assert abs(max(x for x, _ in don) - 5 * math.sqrt(2)) < 1e-6
    assert Y.ikiye_bol("farmakolog (1923–1984) · kaynak: meslektaş tanıklıkları") == \
        "farmakolog (1923–1984)\nkaynak: meslektaş tanıklıkları"
    assert Y.ikiye_bol("Ord. Prof. Süreyya Tahsin Aygün").count("\n") == 1 and Y.ikiye_bol("Tek") is None


def test_isim_karakterlerden_40px_uzak():
    """Animasyon hakemi M1: isim etiketi çeneye/ağza biniyordu. Etiket her karakterin alfa kutusundan en az 40 px
    uzakta: uzun unvan kırılır/küçülür ya da boş tarafa geçer; `karakter` verilince karakterin yanına."""
    from wojak.uzun import yerlesim as Y
    from wojak.uzun.sahneler import Baglam, cizici
    AN = "uzun/talidomit-turkiye/chars/kaymakcalan_v2_sakin.png"
    for kon, x, ek in (("sol", 0.72, {}), ("sag", 0.5, {"karakter": "s"}), ("sol", 0.25, {})):
        sah = {"tip": "wojak", "arka": "uzun/talidomit-turkiye/img/doku_kagit.jpg", "sure": 6.0,
               "kamera": {"zoom": [1.0, 1.0], "it": 0},
               "karakterler": [{"id": "s", "gorsel": AN, "x": x, "boy": 0.7, "giris": False}],
               "olaylar": [dict({"tip": "isim", "ad": "Şükrü Kaymakçalan", "t": 0.5, "sure": 4.0, "konum": kon,
                                 "unvan": "farmakolog (1923–1984) · kaynak: meslektaş tanıklıkları"}, **ek)]}
        v = _video([{"baslik": "a", "sahneler": [sah]}])
        z = zaman.hesapla(v, tahmin=True)
        c = Baglam(v, 960, 540, 30)
        cz = cizici(z.sahneler[0], c)
        uk = cz.katman
        it = uk.isimler[0]
        assert it["ihlal"] == 0.0, (kon, x, it)
        for t in (1.0, 2.5, 4.4):
            (ad, poli), = uk.kutular(t)
            kb = cz.karakterler[0].ekran_kutulari(t, cz.kam(t))[0]
            px0, py0, px1, py1 = Y.kutu_icin(poli)
            bosluk = max(kb[0] - px1, px0 - kb[2], kb[1] - py1)
            assert bosluk >= Y.BOSLUK * c.S - 1.5, (kon, x, t, bosluk)
    # hiçbir yere sığmıyorsa en az çakışan yer (önce yüz, sonra gövde) seçilir ve kontrol uyarır
    sah = {"tip": "wojak", "arka": "uzun/talidomit-turkiye/img/doku_kagit.jpg", "sure": 6.0,
           "karakterler": [{"id": "a", "gorsel": AN, "x": 0.25, "boy": 0.75, "giris": False},
                           {"id": "b", "gorsel": AN, "x": 0.75, "boy": 0.75, "giris": False}],
           "olaylar": [{"tip": "isim", "ad": "Çok Uzun Bir Ad Soyad Unvanı", "unvan": "uzun bir açıklama satırı",
                        "t": 0.5, "sure": 4.0}]}
    v = _video([{"baslik": "a", "sahneler": [sah]}])
    z = zaman.hesapla(v, tahmin=True)
    uk = cizici(z.sahneler[0], Baglam(v, 960, 540, 30)).katman
    assert uk.isimler[0]["ihlal"] == 1.0
    assert any("40 px" in x for x in Y.denetle(v, z))


def test_kontrol_ust_katman_cakismalari():
    """kontrol: üst katman yüze ya da başka üst katmana binerse (damgalar köşeden değerse dahil) ve pano kartları
    üst üste binerse uyarır; ayrık olanlar temiz."""
    from wojak.uzun import yerlesim as Y
    AN = "uzun/talidomit-turkiye/chars/anlatici_v2_sakin.png"
    KG = "uzun/talidomit-turkiye/img/doku_kagit.jpg"
    def uyarilar(olaylar, kar=True):
        sah = {"tip": "wojak", "arka": KG, "sure": 4.0, "kamera": {"zoom": [1.0, 1.0], "it": 0},
               "karakterler": [{"id": "z", "gorsel": AN, "x": 0.75, "boy": 0.8, "giris": False}] if kar else [],
               "olaylar": olaylar}
        v = _video([{"baslik": "a", "sahneler": [sah]}])
        return Y.denetle(v, zaman.hesapla(v, tahmin=True))
    d1 = {"tip": "damga", "metin": "BİR", "x": 0.3, "y": 0.3, "aci": 0, "t": 0.3}
    assert not uyarilar([d1])
    yakin = {"tip": "damga", "metin": "İKİ", "x": 0.37, "y": 0.3, "aci": 0, "t": 0.5}
    assert any("damga 'BİR' ile damga 'İKİ'" in x for x in uyarilar([d1, yakin]))
    yuz = {"tip": "kelime", "metin": "YÜZÜN ÜSTÜNDE", "konum": "orta", "t": 0.5}
    assert any("yüzüne biniyor" in x for x in uyarilar([yuz]))
    pano = {"tip": "pano", "sure": 3.0, "kartlar": [{"id": "a", "metin": "A", "x": 0.4, "y": 0.5},
                                                    {"id": "b", "metin": "B", "x": 0.45, "y": 0.52},
                                                    {"id": "c", "metin": "C", "x": 0.85, "y": 0.2}]}
    v = _video([{"baslik": "a", "sahneler": [pano]}])
    u = Y.denetle(v, zaman.hesapla(v, tahmin=True))
    assert any("'a' ile 'b'" in x for x in u) and not any("'c'" in x for x in u)


def test_pano_ipi_kartin_yazisindan_gecmez():
    """Animasyon hakemi S6: alttaki karta giden ip üst raptiyeden kartın kendi yazısının üstünden iniyordu; şimdi
    alt kenardaki raptiyeye bağlanır. Aradaki kartlar ipin üstünde (ip altlarından geçer)."""
    from wojak.uzun.sahneler import Baglam, cizici
    pano = {"tip": "pano", "sure": 4.0, "ipler": [["k", "b"], ["k", "r"]],
            "kartlar": [{"id": "k", "metin": "ÜST", "alt": "uzun bir açıklama", "x": 0.2, "y": 0.35, "egim": 0},
                        {"id": "b", "metin": "ALT", "x": 0.2, "y": 0.75, "egim": 0},
                        {"id": "m", "metin": "ORTA", "x": 0.5, "y": 0.35, "egim": 0},
                        {"id": "r", "metin": "SAĞ", "x": 0.8, "y": 0.35, "egim": 0}]}
    v = _video([{"baslik": "a", "sahneler": [pano]}])
    z = zaman.hesapla(v, tahmin=True)
    cz = cizici(z.sahneler[0], Baglam(v, 960, 540, 30))
    (ka, alt_a), (kb, alt_b) = cz.ip_uclari[("k", "b")]
    assert alt_a and not alt_b and ka[1] > cz.kartlar["k"]["cy"]       # üst kartın alt raptiyesinden
    (ra, alt_ra), _ = cz.ip_uclari[("k", "r")]
    assert not alt_ra                                                   # yan kart: üst raptiye
    # ip ortadaki kartın gövdesinde görünmez: kartın ortası ipli ve ipsiz çizimde aynı
    from PIL import Image
    tuval = Image.new("RGB", (cz.CW, cz.CH), (200, 180, 150))
    m = cz.kartlar["m"]
    gx0, gy0, gx1, gy1 = m["govde"]
    once = np.asarray(tuval, np.float32)[int(gy0):int(gy1), int(gx0):int(gx1)].copy()
    cz._ip_ciz(tuval, "k", "r", cz.kartlar["k"]["pin"], cz.kartlar["r"]["pin"], 1.0, 10.0)
    sonra = np.asarray(tuval, np.float32)[int(gy0):int(gy1), int(gx0):int(gx1)]
    assert np.abs(sonra - once).max() == 0
    assert np.abs(np.asarray(tuval, np.float32) - 200).sum() > 0     # ip başka yerde çizildi


def test_kapanis_kartlari_karakterden_kacar():
    """Animasyon hakemi S8: anlatıcının başı A kartının köşesine biniyordu; kart sırası karakterin kutusundan uzak."""
    from wojak.uzun.kapanis import KapanisCizici
    from wojak.uzun.sahneler import Baglam
    kap = {"tip": "kapanis", "arka": KUTU, "soru": "Ne korudu?", "secenekler": ["A", "B", "C"], "sure": 9.5,
           "karakter": {"gorsel": "uzun/talidomit-turkiye/chars/anlatici_v2_sakin.png", "boy": 0.37},
           "bos_alan": True, "satirlar": ["Sizce hangisi?"]}
    v = _video([{"baslik": "a", "sahneler": [kap]}])
    kc = KapanisCizici(zaman.hesapla(v, tahmin=True).sahneler[0], Baglam(v, 1920, 1080))
    kx0, ky0, kx1, ky1 = kc.kar["kutu"]
    for k in kc.kartlar:
        ust_uste = k["x"] < kx1 + 20 and k["x"] + k["w"] > kx0 and k["y"] + k["h"] > ky0
        assert not ust_uste, (k["x"], k["y"], kc.kar["kutu"])
    assert max(k["x"] + k["w"] for k in kc.kartlar) <= 1920 - 50


def test_altyazi_sinirlari_metne_gore_oturur():
    """Teknik hakem S1: tahmini sınır en yakın sessizliğe değil, bölme noktasındaki noktalamanın sessizliğine
    oturur ("1957. | Batı Almanya." hatası); rakamlar okunuşuyla tartılır; noktalamasız bölmede uzak sessizlik
    alınmaz, çapalar arasında doğrusal."""
    assert altyazi.sayi_okunusu(1954) == "bin dokuz yüz elli dört"
    assert altyazi.sayi_okunusu(20000) == "yirmi bin" and altyazi.sayi_okunusu(1267) == "bin iki yüz altmış yedi"
    assert altyazi.soylenis("1954'te") == "bin dokuz yüz elli dört'te"
    ps = ["1957. Batı Almanya.", "Reçetesiz satılan yeni bir uyku ilacı."]
    # sessizlikler: "1957."den sonra (0,9-1,2) ve "Almanya."dan sonra (2,1-2,4); sınır ikincisine
    s = altyazi.sinirlari_hizala(ps, ((0.9, 1.2), (2.1, 2.4)), 5.0)
    assert s is not None and abs(s[0] - (2.4 - 0.08)) < 1e-9
    # noktalamasız bölme noktası: 1,1 sn uzaktaki sessizlik alınmaz (rakam okunuşu tahmini öne çeker)
    ps = ["1954'te Alman ilaç firması", "Grünenthal'in laboratuvarında yeni bir molekül sentezleniyor."]
    s = altyazi.sinirlari_hizala(ps, ((1.24, 1.38),), 5.59)
    assert s is not None and 2.0 < s[0] < 2.9, s
    # bölme noktasındaki nefes duraklaması (noktalamasız) alınır, öndeki virgüle eşlenmez
    ps = ["O yıllardan bir belge, bir gazete haberi", "ya da ailenizden dinlediğiniz bir anı varsa yorumlara yazın."]
    s = altyazi.sinirlari_hizala(ps, ((2.42, 2.6),), 5.55)
    assert s is not None and abs(s[0] - 2.52) < 1e-9


def test_short_youtube_aciklamasi_en_cok_uc_hashtag():
    """Hesap sahibi: YouTube'da 2-3 hashtag (Short açıklamasında 8 + #shorts vardı)."""
    import re
    from wojak import pack
    from wojak.episode import load
    ep = load(KOK / "episodes/talidomit-turkiye")
    t = pack.texts(ep)
    n = len(re.findall(r"(?<!\w)#\w+", t["youtube_aciklama"]))
    assert 2 <= n <= 3 and "#shorts" in t["youtube_aciklama"]
    assert "#" not in t["instagram_aciklama"]
    assert not [w for w in pack.warnings(t, ep) if "hashtag" in w]


def test_on_uc_tur_motor_ekleri():
    """13. tur: (a) kontrol, aynı yerde öncekinin sönmesi bitmeden beliren vurgu kelimesini bildirir; `y` ile ayrılır;
    (b) kamera itmesinde kadrajdan çıkan yüzü ve sonra çizilen görselin örttüğü yüzü bildirir; (c) harita lejantı
    `aciklama_en` ile iki satıra kırılır, sabit kutudur ve konuğa binince bildirilir; (d) itme geçişinin bulanıklığı
    yumuşak uçlu (tek kutu çekirdeğinin sert uçları basamaklı hayalet kopya yapıyordu); (e) bakış kaydı olmayan karakter
    görseli bildirilir; (f) kapanıştaki belge damgası kartın içine sığar; (g) konturlu damganın mürekkep boşlukları
    beyaz değil."""
    import tempfile
    from PIL import Image
    from wojak.uzun import cli, yerlesim as Y
    from wojak.uzun import cizim as C
    from wojak.uzun.kapanis import KapanisCizici
    from wojak.uzun.sahneler import Baglam, cizici
    from wojak.uzun.ust import damga_sprite
    AN = "uzun/talidomit-turkiye/chars/anlatici_v2_sakin.png"
    KG = "uzun/talidomit-turkiye/img/doku_kagit.jpg"
    MAK = "uzun/talidomit-turkiye/img/cizim/makale_behcet_1998_cizim.png"
    # (a) kelime sırası
    def kel(o2):
        sah = {"tip": "metin", "metin": "x", "sure": 5.0,
               "olaylar": [{"tip": "kelime", "metin": "BİR", "konum": "ust", "t": 0.2, "sure": 1.5}, o2]}
        v = _video([{"baslik": "a", "sahneler": [sah]}])
        return [x for x in Y.denetle(v, zaman.hesapla(v, tahmin=True)) if "kelime" in x]
    assert any("sönmesi bitmeden" in x for x in kel({"tip": "kelime", "metin": "İKİ", "konum": "ust", "t": 1.8}))
    assert not kel({"tip": "kelime", "metin": "İKİ", "konum": "ust", "t": 2.4})
    assert not kel({"tip": "kelime", "metin": "İKİ", "konum": "ust", "t": 1.8, "y": 0.6})
    # (b) yüz kadraj dışında / örtülü
    def kar(karakterler, olaylar=()):
        sah = {"tip": "wojak", "arka": KG, "sure": 4.0, "kamera": {"zoom": [1.0, 1.0], "it": 0},
               "karakterler": karakterler, "olaylar": list(olaylar)}
        v = _video([{"baslik": "a", "sahneler": [sah]}])
        return Y.denetle(v, zaman.hesapla(v, tahmin=True))
    z_ = {"id": "z", "gorsel": AN, "x": 0.86, "boy": 0.5, "giris": False}
    assert not kar([z_])
    it = {"tip": "it", "t": 0.5, "guc": 0.2, "sure": 0.6, "x": 0.3, "y": 0.5}
    assert any("kadraj dışında" in x for x in kar([z_], [it]))
    m_ = {"id": "m", "gorsel": MAK, "x": 0.8, "boy": 0.8, "giris": False, "canli": False}
    assert any("örtüyor" in x for x in kar([z_, m_]))          # makale sonra çiziliyor: yüzü örter
    assert not any("örtüyor" in x for x in kar([m_, z_]))      # anlatıcı önde
    # (c) lejant
    har = {"tip": "harita", "bolge": "avrupa", "ulkeler": ["DEU"], "sure": 3.0,
           "aciklama": "kırmızı: satıldığı belgelenen ülkelerden bazıları"}
    v = _video([{"baslik": "a", "sahneler": [har]}])
    cz = cizici(zaman.hesapla(v, tahmin=True).sahneler[0], Baglam(v, 960, 540))
    tek = cz.aciklama.size
    assert len(cz.sabit_engeller()) == 1
    v2 = _video([{"baslik": "a", "sahneler": [dict(har, aciklama_en=520)]}])
    cz2 = cizici(zaman.hesapla(v2, tahmin=True).sahneler[0], Baglam(v2, 960, 540))
    assert cz2.aciklama.width <= 520 / 2 + 2 and cz2.aciklama.height > tek[1] * 1.5    # 960 px'te yarı ölçek
    v3 = _video([{"baslik": "a", "sahneler": [dict(har, konuk=[{"id": "z", "gorsel": AN, "x": 0.45, "boy": 0.4,
                                                                 "giris": False}])]}])
    assert any("lejant" in x for x in Y.denetle(v3, zaman.hesapla(v3, tahmin=True)))
    # (d) bulanıklık: tek parlak sütunun izi uçlara doğru yumuşak azalır (düz kutu değil), ortalama korunur
    im = Image.new("RGB", (400, 4), (0, 0, 0))
    im.paste((255, 255, 255), (200, 0, 202, 4))
    b = np.asarray(C.yatay_bulanik(im, 120), np.float32)[2, :, 0]
    tepe = int(np.argmax(b))
    assert abs(float((b * np.arange(400)).sum() / b.sum()) - 200.5) <= 120 / 20 + 1   # yerel kayma <= L/20
    assert b[tepe] > 1.6 * b[tepe + 40] > 0 and b[tepe + 40] > b[tepe + 70]     # uçlar yumuşak söner
    assert abs(b.sum() - 2 * 255) < 0.08 * 2 * 255
    # (e) kayıtsız bakış
    with tempfile.TemporaryDirectory(dir=str(KOK / "out")) as td:
        kopya = Path(td) / "chars" / "yeni_yuz.png"
        kopya.parent.mkdir()
        a = Image.open(KOK / AN).convert("RGBA")
        a.putpixel((0, 0), (1, 2, 3, 4))                         # içerik (sha1) farklı: kayıtsız
        a.save(kopya)
        sah = {"tip": "wojak", "arka": KG, "sure": 2.0, "karakterler": [{"id": "z", "gorsel": str(kopya), "x": 0.8}]}
        assert any("bakış kaydı yok" in x for x in cli.bakis_denetimi(_video([{"baslik": "a", "sahneler": [sah]}])))
        sah["karakterler"][0]["bakis"] = "sol"
        assert not cli.bakis_denetimi(_video([{"baslik": "a", "sahneler": [sah]}]))
    # (f) kapanış: belge kartındaki damga kartın iç enine sığar
    kap = {"tip": "kapanis", "arka": KUTU, "soru": "?", "sure": 9.5, "satirlar": ["Sizce hangisi?"],
           "secenekler": [{"metin": "A"}, {"metin": "B", "gorsel": KUTU, "damga": "ÇOK UZUN BİR DAMGA YAZISI"},
                          {"metin": "C"}]}
    v = _video([{"baslik": "a", "sahneler": [kap]}])
    kc = KapanisCizici(zaman.hesapla(v, tahmin=True).sahneler[0], Baglam(v, 960, 540))
    k = kc.kartlar[1]
    th = math.radians(7)
    assert k["damga"].width * math.cos(th) + k["damga"].height * math.sin(th) <= 0.881 * (k["w"] - 2 * k["pad"])
    # (g) konturlu damga: harf izinin içinde beyaz benek yok (mürekkep rengi altta)
    from PIL import ImageFilter
    iz = np.asarray(damga_sprite("HAYIR", (196, 16, 28), 80, 1.0, 3).getchannel("A")
                    .filter(ImageFilter.MinFilter(3))) > 10              # harf + çerçeve izi (boşluklar dahil)
    d = np.asarray(damga_sprite("HAYIR", (196, 16, 28), 80, 1.0, 3, kontur=(255, 255, 255)), np.float32)
    pay = max(3, int(round(0.07 * 80)) | 1)
    d = d[pay:pay + iz.shape[0], pay:pay + iz.shape[1]]
    assert d[..., 1][iz].mean() < 50, d[..., 1][iz].mean()   # 12. turdaki gibi beyaz dolgu üstünde: ~75 (pembe)


def test_on_dort_tur_motor_ekleri():
    """14. tur: (a) anlatım klibinin sonu söndürülür ve patlamayla biten klip bildirilir; (b) yakın panoda kadrajdan
    taşan kart bildirilir, çerçeveleyen kamera kartı güvenli alanda tutar; (c) köşe göstergesinde şablon değişince
    değer aynı karede değişir; (d) vurgu kelimesi baskının üst kenarına binince bildirilir; (e) altyazıda "ise"
    öznesinde kalır, "¦" blok içi satır ipucu, 0,1 sn'den kısa boşluk kapanır; (f) kapanışta yorum gönderme tıkı
    yazımı geciktirmez."""
    import tempfile
    from wojak.uzun import altyazi, ses, tts, yerlesim as Y
    from wojak.uzun.kapanis import kapanis_zamanlari
    from wojak.uzun.sahneler import Baglam, cizici
    from wojak.uzun.ust import KoseGostergesi, kose_olaylari
    KG = "uzun/talidomit-turkiye/img/doku_kagit.jpg"
    # (a) söndürme ve kuyruk ölçüsü
    sr = 48000
    t_ = np.arange(sr) / sr
    x = (0.3 * np.sin(2 * np.pi * 220 * t_) * np.clip(1 - t_ / 0.8, 0, 1)).astype(np.float32)
    x[-int(0.006 * sr):] = 0.8 * np.sign(np.sin(np.arange(int(0.006 * sr))))     # sondaki patlama
    assert ses.kuyruk_farki(x)[0] > 20
    y = ses.klip_sondur(np.ones(1000, np.float32))
    assert y[-1] == 0 and y[0] == 1 and y[-500] == 1 and 0 < y[-200] < 1
    with tempfile.TemporaryDirectory() as d:
        w = Path(d) / "k.wav"
        tts.wav_yaz(w, x, sr)
        v = _video([{"baslik": "a", "sahneler": [{"tip": "metin", "metin": "x", "satirlar": ["Bir."]}]}])
        st = v.sahneler[0].satirlar[0]
        st.wav, st.sure, st.tahmini = w, 1.0, False
        z = zaman.hesapla(v)
        assert any("patlamayla bitiyor" in u for u in ses.klip_denetimi(z))
        x2 = x.copy()
        x2[-int(0.006 * sr):] = 0
        tts.wav_yaz(w, x2, sr)
        assert not ses.klip_denetimi(zaman.hesapla(v))
    # (a2) klip içindeki sıfır aralığının (Cartesia break) iki kenarı da yumuşar; boy aynı; kısa sıfırlar dokunulmaz
    c = np.full(4800, 0.5, np.float32)
    c[2000:2600] = 0                       # 12,5 ms tam sıfır: sönümsüz kesme + sönümsüz başlangıç
    c[3500:3550] = 0                       # ~1 ms: aralık sayılmaz
    y2, k = ses.ic_kenar_yumusat(c)
    assert len(y2) == len(c) and k == 3    # kesme, başlangıç, sıfırsız klip başı
    assert y2[0] == 0 and y2[1999] < 0.01 and y2[2600] < 0.01 and abs(y2[2600 + 240] - 0.5) < 1e-6
    assert y2[1500] == 0.5 and np.all(y2[3500:3550] == 0) and y2[3600] == 0.5
    assert ses.ic_kenar_yumusat(np.zeros(1000, np.float32))[1] == 0
    # (b) yakın pano: alttaki uzun kart
    kartlar = [{"id": "a", "metin": "ÜST", "x": 0.3, "y": 0.3}, {"id": "b", "metin": "ALT KART", "alt": "alt satır",
               "gorsel": KG, "x": 0.3, "y": 0.78, "en": 320}]
    def pano(**ek):
        sah = {"tip": "pano", "zoom": 1.25, "yakin": 1.25, "sure": 6.0, "kartlar": kartlar,
               "olaylar": [{"tip": "kart", "id": "a", "t": 0.0}, {"tip": "kart", "id": "b", "t": 1.0}], **ek}
        v = _video([{"baslik": "a", "sahneler": [sah]}])
        return [u for u in Y.denetle(v, zaman.hesapla(v, tahmin=True)) if "kadraj" in u]
    assert any("pano kartı 'b'" in u for u in pano(cercevele=False))
    assert not pano()
    # (c) köşe: "GÜN {}" 0 -> "{}" "1961": ara karede çıplak "0" yok
    sah = {"tip": "metin", "metin": "x", "sure": 3.0, "kose": {"metin": "GÜN {}", "deger": 0},
           "olaylar": [{"tip": "kose", "metin": "{}", "deger": "1961", "t": 1.0}]}
    v = _video([{"baslik": "a", "sahneler": [sah]}])
    s0 = zaman.hesapla(v, tahmin=True).sahneler[0]
    kg = KoseGostergesi(s0, Baglam(v, 960, 540), kose_olaylari(s0))
    assert [kg._metin(t)[0] for t in (0.9, 1.01, 1.2)] == ["GÜN 0", "1961", "1961"]
    # (d) kenar bandı: kelime baskının üst kenarında / üstünde
    def foto(y_):
        sah = {"tip": "foto", "gorsel": KG, "boy": 0.7, "sure": 4.0,
               "olaylar": [{"tip": "kelime", "metin": "SORU?", "t": 1.5, "konum": "ust", "y": y_}]}
        v = _video([{"baslik": "a", "sahneler": [sah]}])
        return [u for u in Y.denetle(v, zaman.hesapla(v, tahmin=True)) if "kenarının" in u]
    assert foto(0.13) and not foto(0.5)
    # (e) altyazı
    assert altyazi.iki_satir("İngiltere'deki bir reklam ise daha da ileri gidiyor:").split("\n")[0].endswith("ise")
    sah = {"tip": "metin", "metin": "x", "satirlar": ["Bugün bir kanser ilacı olarak¦kullanılıyor.", "İkinci satır."]}
    v = _video([{"baslik": "a", "sahneler": [sah]}])
    assert v.transkript(v.sahneler[0].satirlar[0]) == "Bugün bir kanser ilacı olarak kullanılıyor."
    _sureler(v, [3.0, 2.0])
    ps = altyazi.parcalar(zaman.hesapla(v))
    assert ps[0].metin == "Bugün bir kanser ilacı olarak\nkullanılıyor."
    assert all(not (0 < ps[i + 1].bas - ps[i].son < altyazi.BOSLUK_BIRLES) for i in range(len(ps) - 1))
    # (f) kapanış: yorum tıkı yazım başlangıcını değiştirmez
    kap = {"tip": "kapanis", "arka": KG, "soru": "?", "sure": 11.0, "satirlar": ["Sizce?"],
           "olaylar": [{"tip": "tikla", "hedef": "yorum", "t": 9.0}]}
    v = _video([{"baslik": "a", "sahneler": [kap]}])
    z = kapanis_zamanlari(zaman.hesapla(v, tahmin=True).sahneler[0])
    assert z["tik"]["yorum"] == 9.0 and z["yorum"] < 6.0


if __name__ == "__main__":
    import inspect
    import time
    testler = [(n, f) for n, f in sorted(globals().items()) if n.startswith("test_") and inspect.isfunction(f)]
    hata = 0
    for n, f in testler:
        t0 = time.time()
        try:
            f()
            print(f"  ok    {n} ({time.time() - t0:.1f} sn)")
        except Exception as e:  # noqa: BLE001
            hata += 1
            print(f"  HATA  {n}: {type(e).__name__}: {e}")
    print(f"{len(testler) - hata}/{len(testler)} geçti")
    sys.exit(1 if hata else 0)


def test_on_bir_tur_motor_ekleri():
    """11. tur: kapanış kartlarının tepkisi (vurgu_gorsel, damga, yuvarlan) ve 34 px alt yazı, kartsız bölüm damgası
    ilk sesten önceki tam saniyeye yukarı, kesmede zıplayan karakter denetimi, inik + sure damgası söner, fotoğraf
    atıfı isim etiketine engel."""
    from wojak.uzun import cli
    from wojak.uzun.kapanis import KapanisCizici, efektler
    from wojak.uzun.sahneler import Baglam, cizici
    from wojak.uzun.ust import Damga
    AN = "uzun/talidomit-turkiye/chars/anlatici_v2_sakin.png"
    KAY = "uzun/talidomit-turkiye/chars/kaymakcalan_v2_"
    kap = {"tip": "kapanis", "arka": KUTU, "soru": "Ne korudu?", "sure": 9.5, "satirlar": ["Sizce hangisi?"],
           "secenekler": [{"metin": "A", "alt": "bir uzmanın ‘hayır’ı", "gorsel": KAY + "sakin.png",
                           "vurgu_gorsel": KAY + "kararli.png", "damga": "HAYIR"},
                          {"metin": "B", "gorsel": KUTU, "damga": {"metin": "ŞART", "renk": [20, 128, 62]}},
                          {"metin": "C", "gorsel": "uzun/talidomit-turkiye/img/cizim/zarlar.png", "hareket": "yuvarlan"}]}
    v = _video([{"baslik": "a", "sahneler": [kap]}])
    s = zaman.hesapla(v, tahmin=True).sahneler[0]
    kc = KapanisCizici(s, Baglam(v, 960, 540))
    a, b, c = kc.kartlar
    assert a["kar2_pm"] is not None and a["damga"] is not None and b["damga"] is not None and c["hareket"] == "yuvarlan"
    ilk = {i: t for t, i in reversed(kc.z["vurgu"])}
    im0 = kc.kare(ilk[1] - 0.05)
    im1 = kc.kare(ilk[1] + 0.6)
    assert np.abs(np.asarray(im0, np.int16) - np.asarray(im1, np.int16)).mean() > 0.5   # yüz + damga değişti
    adlar = [ad for _, ad, _ in efektler(s, 0.0)]
    assert adlar.count("damga") == 2
    _hata_bekle(lambda: _video([{"baslik": "a", "sahneler": [dict(kap, secenekler=[{"metin": "A", "hareket": "uc"}])]}]),
                "yuvarlan")
    # kartsız bölüm: ilk ses yukarıdaki saniyeden >= 0,1 sn sonra -> yukarı; değilse aşağı
    v2 = _video([
        {"baslik": "Giriş", "kart": False, "sahneler": [{"tip": "metin", "metin": "x", "sure": 41.5}]},
        {"baslik": "İki", "sahneler": [{"tip": "metin", "metin": "x", "sure": 30}]},
        {"baslik": "Kapanış", "kart": False, "sahneler": [{"tip": "metin", "metin": "x", "bas": 0.6,
                                                            "satirlar": ["Peki?"]}]}])
    _sureler(v2, [1.0])
    z2 = zaman.hesapla(v2)
    s3 = v2.bolumler[2].sahneler[0]
    t3 = z2.sahne_basi(s3)
    assert t3 % 1 > 0.05
    s3.bas = math.ceil(t3) - t3 + 0.3                       # ilk ses yukarıdaki saniyeden 0,3 sn sonra
    assert paket.bolum_damgalari(zaman.hesapla(v2))[2][0] == math.ceil(t3)
    s3.bas = math.ceil(t3) - t3 + 0.02                      # ilk ses saniyeye çok yakın: aşağı (kelime kesilmesin)
    assert paket.bolum_damgalari(zaman.hesapla(v2))[2][0] == math.floor(t3)
    # kesmede zıplama: aynı anlatıcı köşede boy değiştirirse uyarı; aynıysa yok; karart geçişinde yok
    def iki(b2, gecis="kesme"):
        sa = {"tip": "sayac", "deger": 10, "sure": 2.0, "konuk": [{"id": "z", "gorsel": AN, "x": 0.87, "boy": 0.5,
                                                                    "giris": False}]}
        sb = {"tip": "sayac", "deger": 20, "sure": 2.0, "gecis": gecis,
              "konuk": [{"id": "z", "gorsel": AN, "x": 0.87, "boy": b2, "giris": False}]}
        vv = _video([{"baslik": "a", "sahneler": [sa, sb]}])
        return cli.ziplama_denetimi(vv, zaman.hesapla(vv, tahmin=True))
    assert iki(0.42) and "zıplıyor" in iki(0.42)[0]
    assert not iki(0.5) and not iki(0.42, "karart")
    # inik + sure: sahne başında basılı, sure sonunda söner
    sah = {"tip": "metin", "metin": "x", "sure": 2.0,
           "olaylar": [{"tip": "damga", "metin": "ONAY", "t": 0.0, "inik": True, "sure": 0.4}]}
    v3 = _video([{"baslik": "a", "sahneler": [sah]}])
    s3 = zaman.hesapla(v3, tahmin=True).sahneler[0]
    d = Damga(s3.olaylar[0], Baglam(v3, 480, 270))
    bos = Image_bos = __import__("PIL.Image", fromlist=["Image"]).new("RGB", (480, 270))
    im = bos.copy(); d.ciz(im, 0.0)
    assert np.asarray(im).max() > 0
    im = bos.copy(); d.ciz(im, 1.0)
    assert np.asarray(im).max() == 0
    # fotoğraf atıfı isim etiketine engel (sabit kutu)
    foto = {"tip": "foto", "gorsel": KUTU, "atif": "Fotoğraf: test (kamu malı)", "x": 0.4, "sure": 4.0}
    v4 = _video([{"baslik": "a", "sahneler": [foto]}])
    cz = cizici(zaman.hesapla(v4, tahmin=True).sahneler[0], Baglam(v4, 960, 540))
    assert len(cz.sabit_engeller()) == 1 and cz.katman.sabit == cz.sabit_engeller()


def test_short_youtube_aciklamasi_hikayeyi_tasir():
    """Hesap sahibi (22.10): YouTube açıklaması = başlık + hikâyenin tamamı + atıf + hashtag; 'sabit yorumda' satırı yok."""
    from wojak import pack
    from wojak.episode import load
    ep = load(KOK / "episodes/kiz-kulesi-efsanesi")
    t = pack.texts(ep)
    d = t["youtube_aciklama"]
    assert d.startswith(t["youtube_baslik"]) and t["youtube_sabit_yorum"] in d
    assert "sabit yorumda" not in d
    assert d.index(t["youtube_sabit_yorum"]) < d.index("Görseller:") < d.index("#shorts")
    assert len(d) <= pack.LIMITS["youtube_desc"]
    uzun = dict(t, youtube_aciklama="x" * 5001)
    assert [w for w in pack.warnings(uzun) if "5000" in w]


def _gemini_video(**satir):
    from wojak.uzun.spec import yukle_sozluk
    from wojak import config
    st = {"metin": "Bu molekülün adı: <break time=\"350ms\"/> talidomit."}
    st.update(satir)
    return yukle_sozluk({"id": "g", "baslik": "g", "model": "gemini-2.5-pro-tts",
                         "sesler": {"charon": {"gemini": "Charon", "hiz": 1.25, "tarz": "Belgesel anlatıcısı."},
                                    "kore": {"gemini": "Kore"}},
                         "anlatici": {"ses": "charon", "hiz": 1.0},
                         "bolumler": [{"baslik": "a", "sahneler": [{"tip": "bolum_karti", "baslik": "x",
                                                                    "satirlar": [st]}]}]}, config.ROOT)


def test_gemini_ses_tablosu_ve_anahtar():
    """Gemini (UZUN_FORMAT §1.1): ses tablosu taban hız × satır hızı = atempo; tarz/hız/metin anahtarı değiştirir;
    <break> noktalamaya çevrilir; duygu tarza eklenir."""
    from wojak.uzun import tts
    v = _gemini_video()
    st = v.sahneler[0].satirlar[0]
    assert v.saglayici == "gemini" and v.ses_id("charon") == "Charon"
    ay = tts.gemini_ayari(v, st)
    assert ay["tempo"] == 1.25 and ay["tarz"] == "Belgesel anlatıcısı." and "<break" not in ay["metin"]
    assert ay["metin"] == "Bu molekülün adı: ... talidomit."
    k = tts.satir_anahtari(v, st)
    v1 = _gemini_video()
    assert k.startswith("g") and k == tts.satir_anahtari(v1, v1.sahneler[0].satirlar[0])
    for kw in ({"hiz": 0.9}, {"tarz": "Fısılda."}, {"metin": "Başka."}):
        vx = _gemini_video(**kw)
        assert tts.satir_anahtari(vx, vx.sahneler[0].satirlar[0]) != k
    assert tts.satir_anahtari(v, st, deneme=1) != k
    v2 = _gemini_video(hiz=0.9, ses="kore", duygu="content")
    ay2 = tts.gemini_ayari(v2, v2.sahneler[0].satirlar[0])
    assert ay2["tempo"] == 0.9 and ay2["ses"] == "Kore" and "kendinden emin" in ay2["tarz"]


def test_gemini_ses_tablosu_zorunlu():
    import pytest
    from wojak.uzun.spec import SpecHatasi
    with pytest.raises(SpecHatasi):
        _gemini_video(ses="murat")   # model gemini ama Cartesia sesi


def test_tempo_uygula_sureyi_kisaltir():
    import numpy as np
    from wojak.uzun import tts
    x = (0.3 * np.sin(np.arange(48000) * 2 * np.pi * 220 / 48000)).astype(np.float32)
    y = tts.tempo_uygula(x, 48000, 1.25)
    assert abs(len(y) / 48000 - 0.8) < 0.03 and tts.tempo_uygula(x, 48000, 1.0) is x


def test_gemini_sayilar_yaziyla():
    """UZUN_FORMAT §1.1: Gemini metninde sayılar yazıyla; kesme işaretli ek bitişir."""
    from wojak.uzun.tts import gemini_metni, sayi_yazi
    assert gemini_metni("1 Ekim 1957'de ilaç") == "bir Ekim bin dokuz yüz elli yedide ilaç"
    assert gemini_metni("10.000'den fazla bebek, %40'ı") == "on binden fazla bebek, yüzde kırkı"
    assert sayi_yazi(2018) == "iki bin on sekiz" and sayi_yazi(1100) == "bin yüz" and sayi_yazi(300000000) == "üç yüz milyon"
    assert gemini_metni("SALL4 proteini") == "SALL4 proteini"
