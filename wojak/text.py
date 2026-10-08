"""Yazı yerleşimi ve çizimi (Türkçe karakter destekli, dengeli satır kırma)."""

from __future__ import annotations

from functools import lru_cache
from itertools import combinations

from PIL import Image, ImageDraw, ImageFilter, ImageFont

from . import config


@lru_cache(maxsize=64)
def font(path: str, size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(str(path), size)


def _width(text: str, f: ImageFont.FreeTypeFont, stroke: int = 0) -> int:
    l, _, r, _ = f.getbbox(text, stroke_width=stroke)
    return r - l


def balanced_wrap(text: str, f: ImageFont.FreeTypeFont, max_w: int, max_lines: int = 4,
                  stroke: int = 0) -> list[str] | None:
    """Satırları olabildiğince eşit uzunlukta kırar (orijinal videolardaki gibi).

    Elle kırmak için metinde '\\n' kullanılabilir; o zaman metne dokunulmaz.
    Sığmazsa None döner.
    """
    if "\n" in text:
        lines = [ln.strip() for ln in text.split("\n")]
        return lines if all(_width(ln, f, stroke) <= max_w for ln in lines) else None
    words = text.split()
    if not words:
        return []
    best = None
    for n in range(1, min(max_lines, len(words)) + 1):
        for cuts in combinations(range(1, len(words)), n - 1):
            idx = (0, *cuts, len(words))
            lines = [" ".join(words[idx[i]:idx[i + 1]]) for i in range(n)]
            widths = [_width(ln, f, stroke) for ln in lines]
            if max(widths) > max_w:
                continue
            # Az satır + dengeli genişlik; üst satırın biraz uzun olması tercih edilir.
            score = (n, max(widths) - min(widths), -widths[0])
            if best is None or score < best[0]:
                best = (score, lines)
        if best is not None:
            return best[1]
    return None


def fit_text(text: str, font_path, size: int, max_w: int, max_lines: int = 3,
             stroke_ratio: float = 0.05, min_size: int = 36):
    """Metni max_w içine sığdıracak en büyük punto ve satırları bulur."""
    while size >= min_size:
        f = font(str(font_path), size)
        stroke = max(1, round(size * stroke_ratio))
        lines = balanced_wrap(text, f, max_w, max_lines, stroke)
        if lines is not None:
            return f, lines, stroke
        size -= 2
    f = font(str(font_path), min_size)
    stroke = max(1, round(min_size * stroke_ratio))
    return f, balanced_wrap(text, f, max_w, 8, stroke) or [text], stroke


def text_block(text: str, *, font_path=config.FONT_DIALOG, size: int = 76, max_w: int = 820,
               max_lines: int = 3, fill=config.WHITE, stroke_fill=config.BLACK,
               stroke_ratio: float = 0.055, line_gap: float = 0.98, shadow: bool = True,
               align: str = "center") -> Image.Image:
    """Konturlu (beyaz dolgu + siyah kenar) yazıyı şeffaf bir RGBA katman olarak döndürür."""
    f, lines, stroke = fit_text(text, font_path, size, max_w, max_lines, stroke_ratio)
    asc, desc = f.getmetrics()
    lh = round((asc + desc) * line_gap)
    widths = [_width(ln, f, stroke) for ln in lines]
    pad = stroke * 2 + 12
    w = max(widths) + pad * 2
    h = lh * len(lines) + pad * 2
    layer = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    for i, ln in enumerate(lines):
        if align == "center":
            x = (w - widths[i]) / 2
        elif align == "left":
            x = pad
        else:
            x = w - pad - widths[i]
        y = pad + i * lh
        d.text((x, y), ln, font=f, fill=fill, stroke_width=stroke, stroke_fill=stroke_fill)
    if shadow:
        sh = Image.new("RGBA", layer.size, (0, 0, 0, 0))
        alpha = layer.getchannel("A").filter(ImageFilter.GaussianBlur(stroke * 1.5))
        sh.putalpha(alpha.point(lambda a: int(a * 0.55)))
        out = Image.new("RGBA", layer.size, (0, 0, 0, 0))
        out.alpha_composite(sh, (0, 3))
        out.alpha_composite(layer)
        layer = out
    return layer


def bubble_block(text: str, *, dark: bool = False, font_path=config.FONT_DIALOG, size: int = 60,
                 max_w: int = 820, max_lines: int = 3, radius: int = 34) -> Image.Image:
    """Yuvarlatılmış kutu içinde yazı (Instagram 'arka planlı yazı' stili)."""
    f, lines, _ = fit_text(text, font_path, size, max_w - 80, max_lines, 0)
    asc, desc = f.getmetrics()
    lh = round((asc + desc) * 0.98)
    widths = [_width(ln, f) for ln in lines]
    px, py = 40, 26
    w = max(widths) + px * 2
    h = lh * len(lines) + py * 2
    bg = (0, 0, 0, 235) if dark else (255, 255, 255, 245)
    fg = (255, 255, 255, 255) if dark else (0, 0, 0, 255)
    layer = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    d.rounded_rectangle((0, 0, w - 1, h - 1), radius=radius, fill=bg)
    for i, ln in enumerate(lines):
        d.text(((w - widths[i]) / 2, py + i * lh - 2), ln, font=f, fill=fg)
    return layer


def card_block(text: str, *, size: int = 150, max_w: int = 960, color=config.WHITE) -> Image.Image:
    """'Bir süre sonra' tarzı ara kart yazısı (Anton)."""
    f, lines, _ = fit_text(text, config.FONT_CARD, size, max_w, 3, 0, min_size=60)
    asc, desc = f.getmetrics()
    lh = round((asc + desc) * 0.92)
    widths = [_width(ln, f) for ln in lines]
    w = max(widths) + 20
    h = lh * len(lines) + 20
    layer = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    for i, ln in enumerate(lines):
        d.text(((w - widths[i]) / 2, 10 + i * lh), ln, font=f, fill=color)
    return layer


def banner_block(text: str, *, width: int = config.BOX, size: int = 44,
                 color=(200, 16, 30, 240)) -> Image.Image:
    """Haber bandı (kırmızı alt şerit) — kanıt sahnelerinde kullanılır."""
    f, lines, _ = fit_text(text, config.FONT_BOLD, size, width - 80, 2, 0, min_size=28)
    asc, desc = f.getmetrics()
    lh = asc + desc
    h = lh * len(lines) + 36
    layer = Image.new("RGBA", (width, h), color)
    d = ImageDraw.Draw(layer)
    for i, ln in enumerate(lines):
        d.text((40, 18 + i * lh), ln, font=f, fill=(255, 255, 255, 255))
    return layer
