#!/usr/bin/env python3
"""Uzun video müzik altlığı (kendi sentezimiz; telifsiz, Content ID riski yok).

    python tools/uzun_muzik.py --sure 540 --tohum 1957          # -> out/muzik/uzun_belgesel_1957_540s.mp3
    python tools/uzun_muzik.py --sure 120 --cikti /tmp/x.wav

Motor (wojak/uzun/ses.py) videonun süresi kadar altlığı kendisi üretir (`muzik: {uret: true, tohum: N}`);
bu araç dinlemek / başka yerde kullanmak içindir. Ayrıntı: wojak/uzun/muzik.py.
"""

from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from wojak import config  # noqa: E402
from wojak.uzun import muzik  # noqa: E402


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--sure", type=float, default=540.0, help="saniye (varsayılan 540 = 9 dk)")
    ap.add_argument("--tohum", type=int, default=1957, help="aynı tohum = aynı parça")
    ap.add_argument("--cikti", type=Path)
    a = ap.parse_args()
    out = a.cikti or config.OUT / "muzik" / f"uzun_belgesel_{a.tohum}_{int(a.sure)}s.mp3"
    t0 = time.time()
    x = muzik.uret(a.sure, a.tohum)
    muzik.kaydet(x, out)
    print(f"-> {out} ({a.sure:.0f} sn, {time.time() - t0:.1f} sn'de üretildi)")


if __name__ == "__main__":
    main()
