"""Müzik kütüphanesi testleri (12.11.2026): `music:` kısa adları, hava parçaları, eski klasik ses.

    python -m pytest tests/test_muzik.py -q
"""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from wojak import config, denetim, episode  # noqa: E402
from wojak.episode import EpisodeError, load, muzik_dosyasi  # noqa: E402

ORNEK = config.ROOT / "episodes/talidomit-turkiye"
HAVA_DOSYALARI = sorted(config.MUSIC_HAVA.glob("*.m4a"))


def _bolum(tmp_path: Path, music: str, bolum_id: str = "deneme") -> Path:
    """Örnek bölümü (yolları kök-göreli) başka bir müzikle geçici klasöre kopyalar."""
    d = tmp_path / bolum_id
    d.mkdir()
    yaml = (ORNEK / "episode.yaml").read_text(encoding="utf-8").splitlines()
    yaml = [f"music: {music}" if s.startswith("music:") else s for s in yaml]
    if not any(s.startswith("music:") for s in yaml):
        yaml.append(f"music: {music}")
    (d / "episode.yaml").write_text("\n".join(yaml) + "\n", encoding="utf-8")
    for alt in ("img", "chars"):
        if (ORNEK / alt).is_dir():
            shutil.copytree(ORNEK / alt, d / alt)
    return d


def test_her_havanin_parcasi_var():
    for hava in config.HAVALAR:
        assert list(config.MUSIC_HAVA.glob(f"{hava}_*.m4a")), hava


def test_kisa_adlar():
    assert muzik_dosyasi("kanal", "x") == muzik_dosyasi("huzun", "x") == config.MUSIC_IMZA
    assert muzik_dosyasi("gizem_a", "x") == config.MUSIC_HAVA / "gizem_a.m4a"
    assert muzik_dosyasi("imza_v2_golge.m4a", "x") is None      # dosya adı: eskisi gibi yol olarak aranır
    assert muzik_dosyasi("hava/gizem_a.m4a", "x") is None


def test_hava_secimi_sabit_ve_cesitli():
    for hava in config.HAVALAR:
        secilen = {muzik_dosyasi(hava, f"bolum-{i}") for i in range(40)}
        assert secilen == set(config.MUSIC_HAVA.glob(f"{hava}_*.m4a")), hava    # her parça bir bölüme düşer
        assert muzik_dosyasi(hava, "kiz-kulesi") == muzik_dosyasi(hava, "kiz-kulesi")


def test_klasik_yoksa_imza_ve_uyari(tmp_path, monkeypatch):
    monkeypatch.setattr(config, "MUSIC_CHANNEL", tmp_path / "yok.m4a")
    assert muzik_dosyasi("klasik", "x") == config.MUSIC_IMZA
    ep = load(_bolum(tmp_path, "klasik"))
    assert ep.music.ad == "klasik" and ep.music.file == config.MUSIC_IMZA.resolve()
    assert any("music: klasik istendi" in u for u in denetim.stil(ep))


def test_klasik_varsa_eski_ses(tmp_path, monkeypatch):
    sahte = tmp_path / "kanal_orijinal_ses.m4a"
    shutil.copy(config.MUSIC_IMZA, sahte)
    monkeypatch.setattr(config, "MUSIC_CHANNEL", sahte)
    ep = load(_bolum(tmp_path, "{file: klasik, volume: 0.5}"))
    assert ep.music.file == sahte.resolve() and ep.music.volume == 0.5
    assert not [u for u in denetim.stil(ep) if "müzik" in u]


@pytest.mark.parametrize("yazilan,ad", [("gizem", "gizem"), ("destansı", "destansi"), ("Hüzün", "huzun")])
def test_bolumde_hava_adi(tmp_path, monkeypatch, yazilan, ad):
    monkeypatch.setattr(config, "HAVA_ONAYLI", True)
    ep = load(_bolum(tmp_path, yazilan))
    assert ep.music.ad == ad
    assert not [u for u in denetim.stil(ep) if "müzik" in u]


def test_onaysiz_hava_uyarir(tmp_path, monkeypatch):
    monkeypatch.setattr(config, "HAVA_ONAYLI", False)
    for yazilan in ("gizem", "merak_a", "{file: hava/masal_a.m4a}"):
        ep = load(_bolum(tmp_path, yazilan, bolum_id=f"b{abs(hash(yazilan)) % 9999}"))
        assert any("onayını bekliyor" in u for u in denetim.stil(ep)), yazilan
    assert not [u for u in denetim.stil(load(_bolum(tmp_path, "kanal", bolum_id="k"))) if "müzik" in u]


def test_kutuphane_disi_muzik_uyarir(tmp_path):
    ep = load(_bolum(tmp_path, "{file: assets/sfx/" + next(p.name for p in sorted(config.SFX.iterdir())
                                                           if p.suffix in (".wav", ".mp3")) + "}"))
    assert ep.music.ad is None
    assert any("kütüphane dışı müzik" in u for u in denetim.stil(ep))


def test_bilinmeyen_ad_dosya_hatasi(tmp_path):
    with pytest.raises(EpisodeError):
        load(_bolum(tmp_path, "gizem_z"))


@pytest.mark.skipif(not shutil.which("ffprobe"), reason="ffprobe yok")
def test_hava_parcalari_14_sn_ve_stereo():
    for p in HAVA_DOSYALARI:
        r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration:stream=channels,sample_rate",
                            "-of", "json", str(p)], capture_output=True, text=True, check=True)
        bilgi = json.loads(r.stdout)
        assert 13.7 <= float(bilgi["format"]["duration"]) <= 14.1, p.name
        assert bilgi["streams"][0]["channels"] == 2, p.name


def test_klasik_en_kanalinda_da_serbest(tmp_path, monkeypatch):
    """13.11: hesap sahibi klasiği iki kanalda da istedi ("türkçe/yabancı kanal için")."""
    sahte = tmp_path / "kanal_orijinal_ses.m4a"
    shutil.copy(config.MUSIC_IMZA, sahte)
    monkeypatch.setattr(config, "MUSIC_CHANNEL", sahte)
    monkeypatch.setattr(denetim, "onceki_bolum", lambda ep, kok=None: None)
    d = _bolum(tmp_path, "klasik")
    yol = d / "episode.yaml"
    yol.write_text("kanal: en\n" + yol.read_text(encoding="utf-8"), encoding="utf-8")
    assert not [u for u in denetim.stil(load(d)) if "müzik" in u or "music" in u]


@pytest.mark.parametrize("onceki, simdi, uyari", [
    ("kanal", "klasik", None),                       # önceki bölümün `music:` değeri (onceki_bolum'un verdiği)
    ("gizem", "klasik", None),
    ("hava/merak_a.m4a", "klasik", None),
    ("klasik", "gizem", None),
    ("ozel/kanal_orijinal_ses.m4a", "masal", None),
    ("klasik", "{file: kanal, volume: 0.197}", None),
    ("klasik", "klasik", "de klasikti"),
    ("orijinal", "{file: klasik, volume: 0.5}", "de klasikti"),
    ("kanal", "gizem", "sıra klasikte"),
    ("destansi", "{file: kanal, volume: 0.197}", "sıra klasikte"),
])
def test_muzik_sirasi(tmp_path, onceki, simdi, uyari):
    ep = load(_bolum(tmp_path, simdi))
    u = denetim.muzik_sirasi(ep, ("onceki-bolum", onceki))
    assert (uyari is None and u == []) or (uyari is not None and len(u) == 1 and uyari in u[0]), u
    assert denetim.muzik_sirasi(ep, None) == []      # git geçmişi yoksa kural denetlenmez


def test_onceki_bolum_git_gecmisinden(tmp_path):
    """Önceki bölüm, episode.yaml'ın depoya ilk girdiği commit'e göre ve yalnız aynı kanaldan bulunur."""
    kok = tmp_path / "depo"
    (kok / "episodes").mkdir(parents=True)

    def git(*a):
        subprocess.run(["git", "-C", str(kok), *a], check=True, capture_output=True)

    git("init", "-q")
    git("config", "user.email", "t@t")
    git("config", "user.name", "t")
    for bolum, govde in (("eski-tr", "music: klasik\n"), ("en-bir", "kanal: en\nmusic: gizem\n"),
                         ("yeni-tr", "music: {file: kanal, volume: 0.197}\n"), ("en-iki", "kanal: en\nmusic: klasik\n")):
        (kok / "episodes" / bolum).mkdir()
        (kok / "episodes" / bolum / "episode.yaml").write_text(f"id: {bolum}\n{govde}", encoding="utf-8")
        git("add", "-A")
        git("commit", "-q", "-m", bolum)
    (kok / "episodes/eski-tr/episode.yaml").write_text("id: eski-tr\nmusic: klasik\n# düzeltme\n", encoding="utf-8")
    git("commit", "-qam", "eski-tr düzeltme")   # düzeltme sırayı bozmaz

    tr = load(_bolum(tmp_path, "klasik", bolum_id="simdiki"))
    assert denetim.onceki_bolum(tr, kok) == ("yeni-tr", "kanal")
    en = load(_bolum(tmp_path, "klasik", bolum_id="en-simdiki"))
    en.kanal = "en"
    assert denetim.onceki_bolum(en, kok) == ("en-iki", "klasik")
    en.id = "en-iki"                           # kendisi sayılmaz (yeniden render)
    assert denetim.onceki_bolum(en, kok) == ("en-bir", "gizem")
    assert denetim.onceki_bolum(tr, tmp_path / "git-degil") is None


def test_besteler_iskelete_uyar():
    """Her parça klasik sesin iskeletinde: 3/4, iki vuruşluk auftakt, ezgi 3. ölçünün sonundan önce girmez."""
    sys.path.insert(0, str(config.ROOT / "tools"))
    import hava_besteler
    assert set(hava_besteler.BESTELER) == {p.stem for p in HAVA_DOSYALARI}
    for ad, f in hava_besteler.BESTELER.items():
        b = f()
        assert b["beats_per_bar"] == 3 and b["pickup_beats"] == 2 and 140 <= b["tempo_bpm"] <= 164, ad
        ilk = min(n["bar"] * 3 + n["beat"] for n in b["notes"])
        assert ilk >= 3 * 3 + 3, ad                              # en erken 3. ölçünün 3. vuruşu
        assert ad.split("_")[0] in config.HAVALAR, ad
