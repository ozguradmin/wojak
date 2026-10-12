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
    assert d[1] == (41, "İkinci bölüm")              # kart dahil bölüm başı, aşağı yuvarlanır
    assert d[2][0] == int(41.7 + v.zamanlama["kart"] + 100)   # 3. bölümün kartı kendi başında
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
    od = config.OUT / v.id
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
