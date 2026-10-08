#!/usr/bin/env python3
"""Yapay zekâ ile karakter / arka plan üretimi.

Önce kütüphanede ara (python tools/wojak_lib.py search ...). Uygun karakter
yoksa üret. Stil tutarlılığı için --ref ile 1-3 mevcut wojak PNG'si ver.

Örnekler:
  python tools/gorsel_uret.py karakter "a Turkish taxi driver in his 40s, short black hair, \
      mustache, grey jacket over a checkered shirt" --duygu "kind, tired smile" \
      -o assets/characters/taksici_erkek.png --ref assets/characters/sovyet_asker_kis.png

  python tools/gorsel_uret.py arkaplan "the inside of a small 1990s Turkish kebab restaurant, \
      empty tables, fluorescent lights" --zaman "Night" -o episodes/x/img/lokanta.jpg

  python tools/gorsel_uret.py prompt karakter "an old village imam with white beard"   # sadece promptu yaz
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from wojak import imagegen  # noqa: E402


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sp = ap.add_subparsers(dest="cmd", required=True)
    k = sp.add_parser("karakter")
    k.add_argument("tarif", help="karakter tarifi (İngilizce daha iyi sonuç verir)")
    k.add_argument("--duygu", default="worried")
    k.add_argument("--yon", default="slightly to the left", help="bakış yönü")
    k.add_argument("--ref", action="append", default=[], help="stil referansı PNG (tekrarlanabilir)")
    k.add_argument("-o", "--out", required=True)
    b = sp.add_parser("arkaplan")
    b.add_argument("yer")
    b.add_argument("--zaman", default="Evening")
    b.add_argument("--hava", default="Quiet, slightly eerie atmosphere")
    b.add_argument("-o", "--out", required=True)
    p = sp.add_parser("prompt")
    p.add_argument("tur", choices=["karakter", "arkaplan"])
    p.add_argument("tarif")
    a = ap.parse_args()

    if a.cmd == "prompt":
        print(imagegen.character_prompt(a.tarif) if a.tur == "karakter" else imagegen.background_prompt(a.tarif))
    elif a.cmd == "karakter":
        out = imagegen.generate_character(a.tarif, Path(a.out), emotion=a.duygu, facing=a.yon,
                                          refs=[Path(r) for r in a.ref])
        print(f"-> {out}")
    else:
        out = imagegen.generate_background(a.yer, Path(a.out), time=a.zaman, mood=a.hava)
        print(f"-> {out}")


if __name__ == "__main__":
    main()
