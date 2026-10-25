"""Kısa reel bakış yönü: karakter her zaman kadrajın içine bakar; kayıt 'faces'ten önce gelir.

Ajanlar 'faces'e görselin kendi yönü yerine olması gereken yönü yazdı (solda 'sag', sağda 'sol'); kayıt ezilince
Lady Be Good ve Ayasofya'da sağdaki karakter dışarı baktı (hesap sahibinin geri bildirimi, 2026-10-25).

    python -m pytest tests/test_bakis.py -q
"""

from __future__ import annotations

import dataclasses
import sys
from pathlib import Path

import numpy as np
import pytest
from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from wojak import cli, compose, config, facing  # noqa: E402
from wojak.episode import Character, load  # noqa: E402

ORNEK = config.ROOT / "episodes/talidomit-turkiye"


@pytest.fixture
def kayit(tmp_path, monkeypatch):
    """Gerçek data/karakter_yon.json'a dokunmadan boş kayıt ve sağa bakan (sağ yarısı işaretli) bir PNG."""
    monkeypatch.setattr(facing, "REGISTRY", tmp_path / "karakter_yon.json")
    a = np.zeros((200, 100, 4), np.uint8)
    a[..., 3] = 255
    a[:, 50:, 0] = 255   # sağ yarı kırmızı: aynalanınca sola geçer
    png = tmp_path / "sagdaki.png"
    Image.fromarray(a).save(png)
    return png


def _sahne(png, side, faces=None):
    ep = load(ORNEK)
    s = next(s for s in ep.scenes if s.type == "dialog")
    s = dataclasses.replace(s, chars=[Character(img=png, side=side, faces=faces)])
    return dataclasses.replace(ep, scenes=[s]), s


def _aynalandi(s) -> bool:
    im = np.asarray(compose._char_layers(s, 400)[0].image)
    return im[:, : im.shape[1] // 2, 0].mean() > im[:, im.shape[1] // 2:, 0].mean()


def test_kayit_faces_ten_once_gelir(kayit):
    facing.register(kayit, "sag")
    _, s = _sahne(kayit, "right", faces="sol")   # yanlış 'faces' (olması gereken yön yazılmış)
    assert _aynalandi(s), "sağdaki, sağa bakan görsel sola dönmeli"
    _, s = _sahne(kayit, "left", faces="sol")
    assert not _aynalandi(s)


def test_kayitsiz_ya_da_celiskili_bakis_uyarilir(kayit):
    ep, _ = _sahne(kayit, "right", faces="sol")
    assert any("kayıtlı değil" in u for u in cli.bakis_sorunlari(ep))
    facing.register(kayit, "sag")
    assert any("çelişiyor" in u for u in cli.bakis_sorunlari(ep))
    ep, _ = _sahne(kayit, "right")
    assert cli.bakis_sorunlari(ep) == []


@pytest.mark.parametrize("bolum", ["en-lady-be-good", "ayasofya-viking-yazisi", "kanuni-gizlenen-olum",
                                   "midas-mezari-altin", "hezarfen-galata-ucusu", "kasikci-elmasi",
                                   "gobeklitepe-mezar-tasi", "karun-hazinesi-bros"])
def test_yayinlanan_bolumlerde_bakis_sorunu_yok(bolum):
    assert cli.bakis_sorunlari(load(config.ROOT / "episodes" / bolum)) == []
