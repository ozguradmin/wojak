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


def test_her_havanin_en_az_iki_parcasi_var():
    for hava in config.HAVALAR:
        assert len(list(config.MUSIC_HAVA.glob(f"{hava}_*.m4a"))) >= 2, hava


def test_kisa_adlar():
    assert muzik_dosyasi("kanal", "x") == muzik_dosyasi("huzun", "x") == config.MUSIC_IMZA
    assert muzik_dosyasi("gizem_b", "x") == config.MUSIC_HAVA / "gizem_b.m4a"
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
def test_bolumde_hava_adi(tmp_path, yazilan, ad):
    ep = load(_bolum(tmp_path, yazilan))
    assert ep.music.ad == ad
    assert not [u for u in denetim.stil(ep) if "müzik" in u]


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
        assert 13.95 <= float(bilgi["format"]["duration"]) <= 14.1, p.name
        assert bilgi["streams"][0]["channels"] == 2, p.name


def test_klasik_en_kanalinda_uyarir(tmp_path, monkeypatch):
    sahte = tmp_path / "kanal_orijinal_ses.m4a"
    shutil.copy(config.MUSIC_IMZA, sahte)
    monkeypatch.setattr(config, "MUSIC_CHANNEL", sahte)
    d = _bolum(tmp_path, "klasik")
    yol = d / "episode.yaml"
    yol.write_text("kanal: en\n" + yol.read_text(encoding="utf-8"), encoding="utf-8")
    assert any("yalnız tr kanalında" in u for u in denetim.stil(load(d)))
