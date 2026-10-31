"""Oturum araçları ve hakem öncesi ön kontrol testleri (ağsız): tools/commons.py, denetim.hakem_oncesi, yön kaydı,
teslim klasörünün korunan dosyaları, ses normalizasyonu.

Hepsi docs/OGRENILENLER.md "Ek dersler"deki tekrar eden kusurlardan (23-28.10.2026).

    python -m pytest tests/test_araclar.py -q
"""

from __future__ import annotations

import argparse
import dataclasses
import importlib.util
import json
import sys
from pathlib import Path

import numpy as np
import pytest
from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from wojak import audio, cli, config, denetim, facing  # noqa: E402
from wojak.episode import load  # noqa: E402

KOK = config.ROOT


def _commons():
    spec = importlib.util.spec_from_file_location("commons_araci", KOK / "tools" / "commons.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture
def commons(monkeypatch):
    c = _commons()
    monkeypatch.setattr(c, "_bekle", lambda s: None)
    return c


# --- tools/commons.py --------------------------------------------------------------------------------------------

@pytest.mark.parametrize("kisa, kullanim, kabul", [
    ("Public domain", "", True), ("PD-old-100", "", True), ("CC0", "", True), ("CC BY 4.0", "", True),
    ("CC BY-SA 3.0", "Creative Commons Attribution-Share Alike 3.0", True), ("cc-by-sa-4.0", "", True),
    ("CC BY-NC 2.0", "", False), ("CC BY-NC-SA 4.0", "", False), ("CC BY-ND 4.0", "", False),
    ("Fair use", "", False), ("", "", False), ("GFDL", "", False), ("Copyrighted", "All rights reserved", False),
])
def test_commons_lisans_sinifi(commons, kisa, kullanim, kabul):
    assert commons.lisans_sinifi(kisa, kullanim)[0] is kabul


def test_commons_yalniz_standart_genislik(commons):
    """Standart dışı ya da özgünden büyük/eşit genişlik `thumbnail_unscaled` özgün yolu döndürüp 429'da kalıyordu."""
    assert commons.genislik_sec(1280, 4928) == 1280
    assert commons.genislik_sec(1000, 4928) == 1280
    assert commons.genislik_sec(1920, 1500) == 1280      # özgünden küçük olmalı
    assert commons.genislik_sec(1280, 1280) == 960       # eşit = özgün yol
    assert commons.genislik_sec(1280, 905) is None       # küçük dosya: md5 özgün yolundan
    with pytest.raises(ValueError):
        commons.thumb_url("File:X.jpg", 1800)
    assert not commons.gecerli_thumb("https://upload.wikimedia.org/wikipedia/commons/1/12/X.jpg"
                                     "?utm_content=thumbnail_unscaled")
    assert commons.gecerli_thumb("https://upload.wikimedia.org/wikipedia/commons/thumb/1/12/X.jpg/1280px-X.jpg")


def test_commons_url_kurma(commons):
    """md5 yolu Commons'un verdiği özgün adresle aynı (Harbor in Moudros, API'den 29.10)."""
    ad = "File:Harbor in Moudros, Lemnos Greece.jpg"
    assert commons.dosya_adi(ad) == "Harbor_in_Moudros,_Lemnos_Greece.jpg"
    assert commons.dosya_adi("https://commons.wikimedia.org/wiki/File:Harbor_in_Moudros,_Lemnos_Greece.jpg") == \
        "Harbor_in_Moudros,_Lemnos_Greece.jpg"
    assert commons.md5_url(ad) == ("https://upload.wikimedia.org/wikipedia/commons/1/12/"
                                   "Harbor_in_Moudros%2C_Lemnos_Greece.jpg")
    assert commons.thumb_url(ad, 1280) == ("https://upload.wikimedia.org/wikipedia/commons/thumb/1/12/"
                                           "Harbor_in_Moudros%2C_Lemnos_Greece.jpg/"
                                           "1280px-Harbor_in_Moudros%2C_Lemnos_Greece.jpg")
    assert commons.thumb_url("File:a.svg", 960).endswith("/960px-A.svg.png")


class _Yanit:
    def __init__(self, kod, icerik=b"", basliklar=None, js=None):
        self.status_code, self.content, self.headers, self._js = kod, icerik, basliklar or {}, js
        self.text = icerik.decode("latin-1")

    def json(self):
        return self._js


class _Oturum:
    def __init__(self, yanitlar):
        self.yanitlar, self.istekler, self.headers = list(yanitlar), [], {}

    def get(self, url, params=None, timeout=None):
        self.istekler.append(url)
        return self.yanitlar.pop(0)


def test_commons_429_geri_cekilme(commons, monkeypatch):
    bekleme = []
    monkeypatch.setattr(commons, "_bekle", bekleme.append)
    monkeypatch.setattr(commons, "ARALIK", 0)
    o = _Oturum([_Yanit(429, basliklar={"Retry-After": "7"}), _Yanit(429), _Yanit(200, b"ok")])
    monkeypatch.setattr(commons, "_oturum", o)
    assert commons._get("https://x").content == b"ok"
    assert bekleme == [7.0, 30.0]                 # Retry-After'a uyar, yoksa üstel (15 * 2**k)
    o = _Oturum([_Yanit(429)] * 4)
    monkeypatch.setattr(commons, "_oturum", o)
    with pytest.raises(commons.CommonsHatasi):
        commons._get("https://x")
    assert len(o.istekler) == commons.DENEME == 4
    o = _Oturum([_Yanit(404)])
    monkeypatch.setattr(commons, "_oturum", o)
    with pytest.raises(commons.CommonsHatasi):
        commons._get("https://x")
    assert len(o.istekler) == 1                   # 404 yeniden denenmez
    assert "@" not in commons.UA                  # kişisel tanımlayıcı yok (§3.10)


def test_commons_kucuk_resim_olmazsa_md5_yolu(commons, monkeypatch, tmp_path):
    import io
    buf = io.BytesIO()
    Image.new("RGB", (2400, 1200), "gray").save(buf, "JPEG")
    istekler = []

    def sahte_get(url, params=None, timeout=60):
        istekler.append(url)
        if "/thumb/" in url:
            raise commons.CommonsHatasi("4 denemede olmadı (HTTP 429)")
        return _Yanit(200, buf.getvalue())

    monkeypatch.setattr(commons, "_get", sahte_get)
    b = {"genislik": 2400, "yukseklik": 1200}
    yol, url = commons.indir("File:Ornek dosya.jpg", tmp_path / "k.jpg", 1280, b)
    assert istekler == [commons.thumb_url("File:Ornek dosya.jpg", 1280), commons.md5_url("File:Ornek dosya.jpg")]
    assert url == commons.md5_url("File:Ornek dosya.jpg")
    assert Image.open(yol).size == (1280, 640)    # özgün iner, standart genişliğe küçültülür


def test_commons_atif_satiri(commons):
    b = {"ad": "Harbor_in_Moudros,_Lemnos_Greece.jpg", "yazar": "Jane Doe", "yil": "2013", "lisans": "CC BY-SA 3.0",
         "lisans_url": "https://creativecommons.org/licenses/by-sa/3.0", "neden": "CC BY-SA",
         "sayfa": "https://commons.wikimedia.org/wiki/File:Harbor_in_Moudros,_Lemnos_Greece.jpg"}
    a = commons.atif(b)
    assert a["en"].startswith("Harbor in Moudros, Lemnos Greece, by Jane Doe, 2013, CC BY-SA 3.0 (https://")
    assert a["en"].endswith("via Wikimedia Commons (https://commons.wikimedia.org/wiki/File:Harbor_in_Moudros,"
                            "_Lemnos_Greece.jpg)")
    assert a["tr"] == "Jane Doe (Harbor in Moudros, Lemnos Greece, 2013, CC BY-SA 3.0), Wikimedia Commons"
    assert "kamu malı" in commons.atif(dict(b, lisans="Public domain", neden="kamu malı / CC0"))["tr"]
    assert commons._ozet({"title": "File:A.jpg", "imageinfo": [{"extmetadata": {
        "LicenseShortName": {"value": "CC BY-NC 2.0"}, "Artist": {"value": "<a href='x'>Ali</a>"}}}]})["kabul"] is False


# --- Hakem öncesi ön kontrol (denetim.hakem_oncesi) --------------------------------------------------------------

def _diyalog(ep, metin, i=0):
    """i. diyalog sahnesinin yazısını değiştirir."""
    sahneler = list(ep.scenes)
    j = [k for k, s in enumerate(sahneler) if s.type == "dialog"][i]
    sahneler[j] = dataclasses.replace(sahneler[j], text=metin)
    return dataclasses.replace(ep, scenes=sahneler)


def _yetimli_metin(son: str, onek: str = "aaa") -> str:
    """Rendererın fontu ve kırımıyla son satırında yalnız `son` kalan metin (font makineye göre değişir)."""
    from wojak.episode import Scene
    for n in range(1, 40):
        t = " ".join([onek] * n + [son])
        lines = denetim._satirlar(Scene(type="dialog", duration=2.5, text=t))
        if lines and len(lines) == 2 and lines[-1] == son:
            return t
    raise AssertionError("yetimli metin kurulamadı")


def test_yetim_kelime():
    ep = load(KOK / "episodes/kasikci-elmasi")
    assert denetim.yetim(ep) == []                       # elle kırılmış replikler
    t = _yetimli_metin("görüşürüz")
    assert any("tek kelime" in u and "görüşürüz" in u for u in denetim.yetim(_diyalog(ep, t)))
    assert denetim.yetim(_diyalog(ep, t.replace(" görüşürüz", "\ngörüşürüz"))) == []   # elle kırım bilinçli


def test_ozel_ad_bolunmesi():
    """'Türk Hava / Yolları' okunmadı (Tahran, 26.10); kesme işaretli ad ('Kulesi'nden / Üsküdar'a') bölünmüş sayılmaz."""
    from wojak.episode import Scene
    ep = load(KOK / "episodes/kasikci-elmasi")
    for n in range(1, 40):
        t = " ".join(["aaa"] * n + ["Türk", "Hava", "Yolları", "geldi"])
        lines = denetim._satirlar(Scene(type="dialog", duration=2.5, text=t))
        if lines and len(lines) == 2 and lines[1].startswith("Yolları"):
            break
    else:
        raise AssertionError("bölünen ad kurulamadı")
    assert any("özel ad" in u and "Hava / Yolları" in u for u in denetim.yetim(_diyalog(ep, t)))
    assert denetim.yetim(load(KOK / "episodes/hezarfen-galata-ucusu")) == []


def test_sansur_izi_en_ve_tr():
    en = load(KOK / "episodes/en-violet-jessop")
    assert denetim.sansur_izi(en) == []
    u = denetim.sansur_izi(dataclasses.replace(en, pinned_comment="Hundreds died that day. She lived until 1971."))
    assert any("died -> d*ed" in x and "hikâye" in x for x in u)
    u = denetim.sansur_izi(_diyalog(en, "Wait, they all d*ed?"))
    assert any("ekranda" in x and "d*ed" in x for x in u)
    assert denetim.sansur_izi(_diyalog(en, "Stop! Wait, is that the ship?!")) == []    # ünlem kelime içinde değil
    tr = load(KOK / "episodes/kanuni-gizlenen-olum")
    assert denetim.sansur_izi(tr) == []
    u = denetim.sansur_izi(dataclasses.replace(tr, pinned_comment="Silahdar Feridun Bey ölümü sakladı."))
    assert any("Silahdar -> S!lahdar" in x for x in u) and any("ölümü -> *lümü" in x for x in u)


def _kanit(ep, tmp_path, w, h):
    p = tmp_path / f"kanit_{w}x{h}.jpg"
    Image.new("RGB", (w, h), "gray").save(p)
    sahneler = [dataclasses.replace(s, images=[p]) if s.type == "evidence" else s for s in ep.scenes]
    return dataclasses.replace(ep, scenes=sahneler)


def test_kanit_boyu(tmp_path):
    """537-816 px (STIL §8); 482 px'lik kırpım MUST (Lady Be Good); 560 -> 1080 büyütme bulanık."""
    ep = load(KOK / "episodes/kasikci-elmasi")
    assert denetim.kanit_boyu(ep) == []
    assert denetim.kanit_boyu(_kanit(ep, tmp_path, 1080, 700)) == []
    assert any("537 px altı" in u for u in denetim.kanit_boyu(_kanit(ep, tmp_path, 1080, 482)))
    assert any("816 px" in u for u in denetim.kanit_boyu(_kanit(ep, tmp_path, 1080, 900)))
    assert any("büyütülüyor" in u for u in denetim.kanit_boyu(_kanit(ep, tmp_path, 560, 380)))
    assert denetim.kanit_boyu(_kanit(ep, tmp_path, 1600, 1100)) == []      # 1080x743, küçültme
    assert denetim.kanit_boyu(_kanit(ep, tmp_path, 960, 1513)) == []       # dikey portre kareyi doldurabilir (685 px)


def test_arka_plan_doygunluk_ve_netlik(tmp_path):
    ep = load(KOK / "episodes/kasikci-elmasi")
    assert denetim.arka_plan(ep) == []
    rng = np.random.default_rng(0)

    def bg(arr):
        p = tmp_path / f"bg_{len(list(tmp_path.iterdir()))}.png"
        Image.fromarray(arr.astype(np.uint8)).save(p)
        return dataclasses.replace(ep, scenes=[dataclasses.replace(s, bg=p, blur=0) if s.type == "dialog" else s
                                               for s in ep.scenes])

    duz = np.full((800, 800, 3), 120)
    assert any("düz/çok yumuşak" in u for u in denetim.arka_plan(bg(duz)))
    doygun = np.stack([rng.integers(150, 255, (800, 800)), rng.integers(0, 40, (800, 800)),
                       rng.integers(0, 40, (800, 800))], -1)
    u = denetim.arka_plan(bg(doygun))
    assert any("çok doygun" in x for x in u) and any("çok keskin" in x for x in u)


def test_baslik_ters_koseyi_soyluyor():
    """Midas'ın ilk başlığı son repliği cevaplıyordu (25.10, MUST); Orban'daki 'dev top' kurulumdur, uyarılmaz."""
    midas = load(KOK / "episodes/midas-mezari-altin")
    assert denetim.baslik_ters_kose(midas) == []
    eski = dataclasses.replace(midas, title="Midas'ın mezarını açtılar, içinden tek bir altın çıkmadı")
    assert any("altın" in u for u in denetim.baslik_ters_kose(eski))
    assert denetim.baslik_ters_kose(load(KOK / "episodes/orban-topu-bizans")) == []
    en = load(KOK / "episodes/en-mona-lisa")
    assert denetim.baslik_ters_kose(en) == []
    ifsa = dataclasses.replace(en, title="Why the Mona Lisa buyer had to call the police")
    assert any("call, police" in u for u in denetim.baslik_ters_kose(ifsa))


@pytest.mark.parametrize("bolum", ["kasikci-elmasi", "midas-mezari-altin", "tahran-1985-ertugrul",
                                   "yerebatan-bodrum-balik", "goeben-fes-1914", "pera-palas-anahtar-1979"])
def test_yayinlanan_bolumlerde_on_kontrol_sessiz(bolum):
    """Eşik yanlışsa yayınlanmış her bölümde öter; iki hakemden 8/8 alan bu bölümlerde uyarı çıkmamalı. Başlık uzunluğu
    31.10'da eklenen bir politika: goeben ve pera-palas başlıkları (65, 88 karakter) bilerek uyarı alır, burada sayılmaz."""
    uyarilar = denetim.hakem_oncesi(load(KOK / "episodes" / bolum))
    assert [u for u in uyarilar if "karakter (en çok" not in u] == []


def test_baslik_uzunlugu():
    """En çok izlenen başlıklar 43-57 karakter, en az izlenenler 69-88 (31.10)."""
    pera = load(KOK / "episodes/pera-palas-anahtar-1979")
    assert any("karakter (en çok 60)" in u for u in denetim.baslik_uzun(pera))
    assert denetim.baslik_uzun(load(KOK / "episodes/kasikci-elmasi")) == []
    assert denetim.baslik_uzun(dataclasses.replace(pera, title="Pera Palas'ın 411 numaralı odasındaki anahtar")) == []


# --- Yön kaydı: yalnız kendi girdisi -----------------------------------------------------------------------------

def test_yon_baska_bolumun_girdisine_dokunmaz(tmp_path, monkeypatch):
    """Aynı baytlı PNG başka bölümde kayıtlıysa 'file' alanı yeni bölüme çevrilmez (Violet Jessop / Mincemeat, 27.10)."""
    monkeypatch.setattr(config, "ROOT", tmp_path)
    monkeypatch.setattr(facing, "REGISTRY", tmp_path / "karakter_yon.json")
    a = np.zeros((40, 20, 4), np.uint8)
    a[..., 3] = 255
    (tmp_path / "eski").mkdir()
    (tmp_path / "yeni").mkdir()
    Image.fromarray(a).save(tmp_path / "eski" / "k.png")
    (tmp_path / "yeni" / "k.png").write_bytes((tmp_path / "eski" / "k.png").read_bytes())
    b = a.copy()
    b[0, 0, 0] = 9
    Image.fromarray(b).save(tmp_path / "yeni" / "baska.png")
    facing.register(tmp_path / "eski" / "k.png", "sag")
    reg = {"0" * 40: {"faces": "left", "file": "silinmis/bolum.png"}}
    reg.update(json.loads(facing.REGISTRY.read_text(encoding="utf-8")))
    facing.REGISTRY.write_text(json.dumps(reg, ensure_ascii=False, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    once = facing.REGISTRY.read_bytes()
    facing.register(tmp_path / "yeni" / "k.png", "sag")                 # aynı bayt, aynı yön: dosyaya dokunma
    assert facing.REGISTRY.read_bytes() == once
    facing.register(tmp_path / "yeni" / "k.png", "sol")                 # yön düzeltmesi: file eski bölümde kalır
    yeni = json.loads(facing.REGISTRY.read_text(encoding="utf-8"))
    anahtar = facing._sha1(tmp_path / "eski" / "k.png")
    assert yeni[anahtar] == {"faces": "left", "file": "eski/k.png"}
    assert yeni["0" * 40] == reg["0" * 40]
    facing.register(tmp_path / "yeni" / "baska.png", "on")
    assert set(json.loads(facing.REGISTRY.read_text(encoding="utf-8"))) == set(yeni) | {facing._sha1(
        tmp_path / "yeni" / "baska.png")}
    facing.REGISTRY.write_text("{ bozuk", encoding="utf-8")            # çakışmalı dosya: üzerine yazılmaz
    with pytest.raises(SystemExit):
        facing.register(tmp_path / "yeni" / "k.png", "sag")
    assert facing.REGISTRY.read_text(encoding="utf-8") == "{ bozuk"


# --- Teslim: RAPOR.md ve BEKLET korunur ---------------------------------------------------------------------------

def test_teslim_rapor_ve_beklet_korunur(tmp_path, monkeypatch):
    """`teslim` teslim/<id>/ klasörünü yeniden kurarken RAPOR.md siliniyordu (en-great-moon-hoax, 26.10)."""
    ep = load(KOK / "episodes/kasikci-elmasi")
    monkeypatch.setattr(config, "ROOT", tmp_path)
    monkeypatch.setattr(config, "OUT", tmp_path / "out")
    monkeypatch.setattr(denetim, "hakem_oncesi", lambda ep: [])
    src = tmp_path / "out" / ep.id
    src.mkdir(parents=True)
    (src / f"{ep.id}.mp4").write_bytes(b"video")
    Image.new("RGB", (8, 8)).save(src / "kapak.jpg")
    dst = tmp_path / "teslim" / ep.id
    dst.mkdir(parents=True)
    (dst / "RAPOR.md").write_text("# rapor\n", encoding="utf-8")
    (dst / "BEKLET").write_bytes(b"")
    (dst / "eski_dolgu.mp4").write_bytes(b"x")
    cli.cmd_teslim(argparse.Namespace(episode=str(ep.dir), zorla=True))
    assert (dst / "RAPOR.md").read_text(encoding="utf-8") == "# rapor\n"
    assert (dst / "BEKLET").exists()
    assert not (dst / "eski_dolgu.mp4").exists()                      # eski üretim çıktısı yine temizlenir
    assert (dst / f"{ep.id}.mp4").read_bytes() == b"video" and (dst / "metinler").is_dir()


# --- Ses: loudnorm sessiz 'anull' düşüşü ---------------------------------------------------------------------------

def test_ses_dogrusal_kazanc_ve_gorunur_uyari(tmp_path, monkeypatch, capsys):
    """TP=-17 ffmpeg'in -9..0 aralığı dışında: filtre hata veriyor, kod sessizce anull'a düşüp -15,5 LUFS
    çıkarıyordu (kanuni-gizlenen-olum, 23.10). Şimdi ölçüm + volume=dB; ölçülemezse uyarı basılır."""
    cagri = []
    olcum = {"input_i": "-15.71", "input_tp": "-2.90", "input_lra": "3.1", "input_thresh": "-26", "target_offset": "0"}

    class R:
        def __init__(self, err=""):
            self.stderr, self.returncode = err, 0

    def sahte(cmd, **kw):
        cagri.append(cmd)
        if "null" in cmd:
            return R("...\n" + json.dumps(olcum))
        return R()

    monkeypatch.setattr(audio.subprocess, "run", sahte)
    audio._loudnorm(tmp_path / "a.wav", tmp_path / "b.wav")
    olc_af = cagri[0][cagri[0].index("-af") + 1]
    tp = float(olc_af.split("TP=")[1].split(":")[0])
    assert -9 <= tp <= 0                                              # ffmpeg'in kabul ettiği aralık
    af = cagri[1][cagri[1].index("-af") + 1]
    assert af == "volume=1.40dB"                                      # -14 LUFS'a +1,71 dB yerine tepe -1,5'e göre
    assert "⚠" not in capsys.readouterr().out                          # hedefin 1 LU içinde: sessiz
    cagri.clear()
    olcum = {"bozuk": 1}
    audio._loudnorm(tmp_path / "a.wav", tmp_path / "b.wav")
    assert cagri[1][cagri[1].index("-af") + 1] == "anull"
    assert "normalize EDİLEMEDİ" in capsys.readouterr().out
