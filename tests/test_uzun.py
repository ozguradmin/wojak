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
    assert any(ad == "whoosh_kisa" and abs(t - 0.4) < 1e-6 for t, ad, _ in ef)
    assert any(ad == "whoosh_kisa" and abs(t - (z.sahne_basi(s1) + 1.5)) < 1e-6 for t, ad, _ in ef)
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
    kg = KoseGostergesi(s, c, kose_olaylari(s))
    for k in range(40):
        m = kg._metin(0.4 + k * 0.02)[0]
        assert m == "????" or m.startswith("19"), m
    s.olaylar = [o for o in s.olaylar if o.tip != "kose"] + [
        spec.Olay(tip="kose", p={"deger": "20??", "takili": True}, zaman=0.4)]
    kg = KoseGostergesi(s, c, kose_olaylari(s))
    for k in range(60):
        m = kg._metin(0.4 + k * 0.02)[0]
        assert m[:2] in ("19", "20") and (m[:2] == "19" or m == "20??" or int(m) <= 2019), m
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
