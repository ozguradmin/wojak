"""Kanal profili testleri: tr (Tarihsel Wojak) değişmeden kalır, en (Wojak Past Files) İngilizce çıktı verir.

    python -m pytest tests/test_kanal.py -q
"""

from __future__ import annotations

import argparse
import dataclasses
import shutil
import sys
import tempfile
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from wojak import censor, cli, config, denetim, pack  # noqa: E402
from wojak.episode import EpisodeError, load  # noqa: E402

KOK = config.ROOT
ORNEK = KOK / "episodes/talidomit-turkiye"   # yolları göreli; her makinede yüklenir


def _en(ep, **ek):
    alan = dict(kanal="en", title="The princess locked in a tower on her 18th birthday",
                pinned_comment="Legend has it a prophet warned the emperor. He killed nobody, yet the story ends in death.",
                credits="Jane Doe, CC BY-SA 4.0", hashtags=["#istanbul"], uzun_video="")
    alan.update(ek)
    return dataclasses.replace(ep, **alan)


def test_tr_profili_degismedi():
    ep = load(ORNEK)
    assert ep.kanal == "tr" and ep.watermark == "tarihselwojak"
    t = pack.texts(ep)
    assert "Görseller:" in t["youtube_aciklama"] and "#tarihselwojak" in pack.instagram_tags(ep)
    assert pack.DEFAULT_TAGS == config.KANALLAR["tr"]["default_tags"]


def test_en_paylasim_metinleri():
    t = pack.texts(_en(load(ORNEK), uzun_video="https://youtu.be/x"))
    d = t["youtube_aciklama"]
    assert "Images: Jane Doe, CC BY-SA 4.0" in d and "Görseller" not in d
    assert "▶ Full version: https://youtu.be/x" in d and "Uzun hali" not in d
    assert "#shorts" in d and "#keşfet" not in d and "#tarihselwojak" not in d
    assert "k*lled" in t["youtube_sabit_yorum"] and "d*ath" in t["youtube_sabit_yorum"]
    tags = pack.instagram_tags(_en(load(ORNEK)))
    assert tags.endswith("#wojakpastfiles #wojak") and "#tarihselwojak" not in tags


def test_en_basliktaki_yorum_eki_atilir():
    t = pack.texts(_en(load(ORNEK), title="The missing battalion (story in the comments)"))
    assert t["instagram_aciklama"].startswith("The missing battalion\n")


def test_en_sansur_kelime_basi_ve_sonu():
    assert censor.metin("He killed a man; the killer used a gun.", "en") == "He k*lled a man; the k*ller used a g*n."
    assert censor.metin("Murder at dawn", "en") == "M*rder at dawn"
    for temiz in ("skill", "deadline", "diet", "Gunther", "bloodhound", "dyed", "gunpowder"):
        assert censor.metin(temiz, "en") == temiz, temiz
    assert censor.metin("cinayet", "en") == "cinayet"          # tr kuralları en'e karışmaz
    assert censor.metin("killed") == "killed"                  # varsayılan tr


def test_en_denetim():
    ep = _en(load(ORNEK), gundem=True, kesin_hukum=False, title="The killer next door")
    u = denetim.check(ep)
    assert any("[masumiyet] 'killer'" in x for x in u)
    cocuk = _en(load(ORNEK), pinned_comment="A 15-year-old boy saw it.")
    assert any("[çocuk]" in x for x in denetim.check(cocuk))


def test_en_kart_metni():
    ep = load(ORNEK)
    kart = next((s for s in ep.scenes if s.type == "card"), None)
    if kart is None:
        pytest.skip("örnek bölümde kart yok")
    en = _en(ep, scenes=[dataclasses.replace(s, text="A few hours later") if s is kart else s for s in ep.scenes])
    assert not [x for x in denetim.stil(en) if "kart yalnız" in x]


def test_yaml_kanal_ve_filigran():
    with tempfile.TemporaryDirectory() as d:
        hedef = Path(d) / "en-deneme"
        shutil.copytree(ORNEK, hedef)
        yml = hedef / "episode.yaml"
        metin = "\n".join(s for s in yml.read_text(encoding="utf-8").splitlines() if not s.startswith("watermark:"))
        yml.write_text("kanal: en\n" + metin + "\n", encoding="utf-8")
        ep = load(hedef)
        assert ep.kanal == "en" and ep.watermark == "wojakpastfiles"
        yml.write_text("kanal: de\n" + metin + "\n", encoding="utf-8")
        with pytest.raises(EpisodeError):
            load(hedef)


def test_new_en_id_on_eki():
    with pytest.raises(SystemExit):
        cli.cmd_new(argparse.Namespace(id="karun-en", kanal="en"))
