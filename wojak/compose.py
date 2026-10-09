"""Sahne kompozisyonu: arka plan + karakter(ler) + yazı + filigran.

Her sahne için hareketsiz katmanlar bir kez hazırlanır (Layers), kare kare
animasyon render.py içinde bu katmanlar üzerinden yapılır.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from PIL import Image, ImageEnhance, ImageFilter, ImageOps

from . import config, facing, text
from .episode import Episode, Scene


def cover_fit(im: Image.Image, w: int, h: int, focus=(0.5, 0.5)) -> Image.Image:
    """Görseli kırparak w x h alanı tamamen doldurur (CSS object-fit: cover)."""
    return ImageOps.fit(im, (w, h), Image.LANCZOS, centering=focus)


def contain_fit(im: Image.Image, w: int, h: int) -> Image.Image:
    im = im.copy()
    im.thumbnail((w, h), Image.LANCZOS)
    if im.width < w and im.height < h:  # küçük görselleri büyüt
        r = min(w / im.width, h / im.height)
        im = im.resize((round(im.width * r), round(im.height * r)), Image.LANCZOS)
    return im


def load_rgba(path) -> Image.Image:
    im = Image.open(path)
    im = ImageOps.exif_transpose(im)
    return im.convert("RGBA")


def paste_rgba(dst: Image.Image, src: Image.Image, x: int, y: int) -> None:
    """src'yi dst üzerine alfa ile bindirir; taşan kısımları kırpar."""
    l, t = max(0, -x), max(0, -y)
    r, b = min(src.width, dst.width - x), min(src.height, dst.height - y)
    if r <= l or b <= t:
        return
    dst.alpha_composite(src.crop((l, t, r, b)) if (l, t, r, b) != (0, 0, src.width, src.height) else src,
                        (x + l, y + t))


def trim_alpha(im: Image.Image) -> Image.Image:
    """Şeffaf kenar boşluklarını kırpar (karakter PNG'leri için)."""
    bbox = im.getchannel("A").point(lambda a: 255 if a > 8 else 0).getbbox()
    return im.crop(bbox) if bbox else im


@dataclass
class CharLayer:
    image: Image.Image
    x: int          # kare içindeki sol üst
    y: int
    pop: bool


@dataclass
class Layers:
    """Bir sahnenin önceden hazırlanmış katmanları (kare: BOX x BOX)."""
    bg: Image.Image                     # zoom için biraz büyük tutulur (RGBA)
    chars: list[CharLayer] = field(default_factory=list)
    overlay: Image.Image | None = None  # yazı + filigran + bant (RGBA, BOX x BOX)


def _prep_bg(img: Image.Image, scene: Scene, box: int) -> Image.Image:
    bg = cover_fit(img.convert("RGB"), box, box, scene.focus)
    if scene.grayscale:
        bg = ImageOps.grayscale(bg).convert("RGB")
    if scene.blur:
        bg = bg.filter(ImageFilter.GaussianBlur(scene.blur))
    if scene.darken:
        bg = ImageEnhance.Brightness(bg).enhance(1 - scene.darken)
    return bg.convert("RGBA")


def _evidence_bg(scene: Scene, box: int) -> Image.Image:
    """Kanıt sahnesi: 1 görsel -> ortada sığdır; 2 -> yan yana; 3-4 -> ızgara."""
    canvas = Image.new("RGBA", (box, box), (0, 0, 0, 255))
    imgs = [load_rgba(p) for p in scene.images]
    n = len(imgs)
    if n == 1:
        im = contain_fit(imgs[0], box, box)
        canvas.alpha_composite(im, ((box - im.width) // 2, (box - im.height) // 2))
    elif n == 2:
        cw = box // 2
        for i, im in enumerate(imgs):
            im = cover_fit(im.convert("RGB"), cw - 4, round(box * 0.62)).convert("RGBA")
            canvas.alpha_composite(im, (i * cw + 2, (box - im.height) // 2))
    else:
        cw = box // 2
        for i, im in enumerate(imgs[:4]):
            im = cover_fit(im.convert("RGB"), cw - 4, cw - 4).convert("RGBA")
            x = (i % 2) * cw + 2
            if n == 3 and i == 2:  # 3 görsel: alttakini ortala
                x = (box - im.width) // 2
            canvas.alpha_composite(im, (x, (i // 2) * cw + 2))
    if scene.grayscale:
        canvas = ImageOps.grayscale(canvas.convert("RGB")).convert("RGBA")
    return canvas


def _char_layers(scene: Scene, box: int) -> list[CharLayer]:
    out = []
    for c in scene.chars:
        im = trim_alpha(load_rgba(c.img))
        # Karakter her zaman kadrajın içine baksın (solda -> sağa, sağda -> sola). Yön kayıtlıysa
        # (ya da sahnede faces: verildiyse) 'flip' yok sayılır ve otomatik karar verilir.
        cx = c.x if c.x is not None else {"left": 0.2, "right": 0.8}.get(c.side, 0.5)
        faces, known = facing.resolve(c.img, c.faces)
        flip = facing.needs_flip(faces, cx) if known and faces != "front" else c.flip
        if flip:
            im = ImageOps.mirror(im)
        h = round(box * c.height)
        w = round(im.width * h / im.height)
        if w > box * 0.95:  # çok geniş görselleri sınırla
            w = round(box * 0.95)
            h = round(im.height * w / im.width)
        im = im.resize((w, h), Image.LANCZOS)
        if c.x is not None:
            x = round(c.x * box - w / 2)
        elif c.side == "left":
            x = round(-w * 0.04)
        elif c.side == "center":
            x = (box - w) // 2
        else:
            x = round(box - w * 0.96)
        # Orijinallerde karakter alt kenardan kesilir (bel/göğüs planı).
        y = box - h + round(c.y_offset * box) + round(h * 0.02)
        out.append(CharLayer(im, x, y, c.pop))
    return out


def _overlay(ep: Episode, scene: Scene, box: int) -> Image.Image:
    ov = Image.new("RGBA", (box, box), (0, 0, 0, 0))
    if scene.type == "card":
        if scene.text:
            blk = text.card_block(scene.text)
            ov.alpha_composite(blk, ((box - blk.width) // 2, (box - blk.height) // 2))
    else:
        if scene.text and scene.text_style != "none":
            if scene.text_style == "outline":
                blk = text.text_block(scene.text, size=scene.text_size, max_w=round(box * 0.80))
            else:
                blk = text.bubble_block(scene.text, dark=scene.text_style == "bubble_dark",
                                        size=round(scene.text_size * 0.8), max_w=round(box * 0.86))
            cy = round(scene.text_y * box)
            y = max(10, min(box - blk.height - 10, cy - blk.height // 2))
            ov.alpha_composite(blk, ((box - blk.width) // 2, y))
        if scene.banner:
            bn = text.banner_block(scene.banner, width=box)
            ov.alpha_composite(bn, (0, box - bn.height - 70))
        if scene.label and config.SHOW_LABELS:
            lb = text.bubble_block(scene.label, dark=True, size=34, max_w=1000, max_lines=1, radius=18)
            ov.alpha_composite(lb, (24, 24))
    if ep.watermark and scene.type != "card":
        wm = text.text_block(ep.watermark, size=36, max_w=500, stroke_ratio=0.07, shadow=False)
        ov.alpha_composite(wm, (box - wm.width - 18, box - wm.height - 8))
    return ov


def build_layers(ep: Episode, scene: Scene, box: int = config.BOX) -> Layers:
    if scene.type == "card":
        bg = Image.new("RGBA", (box, box), (0, 0, 0, 255))
    elif scene.type == "evidence":
        bg = _evidence_bg(scene, box)
    else:
        bg = _prep_bg(load_rgba(scene.bg), scene, box)
    return Layers(bg=bg, chars=_char_layers(scene, box), overlay=_overlay(ep, scene, box))


def top_text_layer(msg: str) -> Image.Image:
    """Üst siyah banttaki kanca yazısı (isteğe bağlı)."""
    return text.text_block(msg, font_path=config.FONT_DIALOG, size=64, max_w=980,
                           max_lines=3, stroke_ratio=0.0, shadow=False)
