"""Yumuşatma (easing) eğrileri. Hepsi t'yi [0, 1]'e kırpar ve f(0)=0, f(1)=1 sağlar."""

from __future__ import annotations

import math


def kirp(t: float, lo: float = 0.0, hi: float = 1.0) -> float:
    return lo if t < lo else hi if t > hi else t


def ilerleme(t: float, t0: float, sure: float) -> float:
    """t0'da başlayıp `sure` saniyede biten animasyonun [0,1] ilerlemesi."""
    if sure <= 0:
        return 1.0 if t >= t0 else 0.0
    return kirp((t - t0) / sure)


def lineer(t: float) -> float:
    return kirp(t)


def out_cubic(t: float) -> float:
    t = kirp(t)
    return 1 - (1 - t) ** 3


def in_cubic(t: float) -> float:
    t = kirp(t)
    return t ** 3


def in_out_cubic(t: float) -> float:
    t = kirp(t)
    return 4 * t ** 3 if t < 0.5 else 1 - (-2 * t + 2) ** 3 / 2


def in_out_sine(t: float) -> float:
    t = kirp(t)
    return 0.5 - 0.5 * math.cos(math.pi * t)


def out_back(t: float, k: float = 1.2) -> float:
    """Hedefi küçük bir taşmayla geçip geri oturur. k=1.2 -> ~%6, k=1.70158 -> ~%10 taşma."""
    t = kirp(t) - 1
    return 1 + (k + 1) * t ** 3 + k * t ** 2


def back_tasma(k: float) -> float:
    """out_back(k) eğrisinin en yüksek değeri - 1 (taşma oranı)."""
    # türev sıfır: 3(k+1)u^2 + 2ku = 0 -> u = -2k / (3(k+1)), t = 1 + u
    u = -2 * k / (3 * (k + 1))
    return (k + 1) * u ** 3 + k * u ** 2


def tumsek(t: float) -> float:
    """0 -> 1 -> 0 yumuşak tümsek (sıkışma/vurgu darbesi için)."""
    t = kirp(t)
    return math.sin(math.pi * t) ** 2


def karistir(a: float, b: float, p: float) -> float:
    return a + (b - a) * p


EGRILER = {
    "lineer": lineer,
    "out_cubic": out_cubic,
    "in_cubic": in_cubic,
    "in_out_cubic": in_out_cubic,
    "in_out_sine": in_out_sine,
    "out_back": out_back,
}
