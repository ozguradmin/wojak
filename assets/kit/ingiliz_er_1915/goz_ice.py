"""2. sahne yüzü (terli) için gözbebeklerini iç köşeye (yüzün baktığı +x yönüne) kaydırır: B, A'ya bakarak sorar
(STIL §4); ters köşede (kaygili) Nervous Wojak'ın kendi dışa kaçan bakışı kalır. Böylece S2 -> S5 arasında göz de
değişir (C2fa B S2 -> S5, C2kk S1 -> S2 gibi).

    python assets/kit/ingiliz_er_1915/goz_ice.py
    python assets/kit/ingiliz_er_1915/kostum.py assets/kit/ingiliz_er_1915/taban/nervous_temiz_ice.png assets/kit/ingiliz_er_1915/taban/kostumlu_nervous_temiz_ice.png
    python tools/kit_varyant.py assets/kit/ingiliz_er_1915/taban/kostumlu_nervous_temiz_ice.png --kit ingiliz_er_1915

Yöntem (taban koordinatı 899x1022, her göz kendi kutusunda, SS kat süper örnekleme):
1. Siyah maske B; gözün tam şekli R = B'nin delikleri doldurulmuş hâli (kontur + gözbebeği + göz akı).
2. Gözün içi I = R'nin LW yarıçaplı diskle aşındırılması; kontur halkası = R - I (gözbebeğinin taşıdığı dış kenar
   da böylece düz bir kontur olur).
3. Eski gözbebeği silinir (I beyaz), yeni gözbebeği = I ∩ (gözün +x ucundaki elips): Nervous Wojak'ın gözbebeği
   gibi gözün bir ucunu dolduran düz siyah leke, bu kez iç köşede.
"""
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

K = Path(__file__).resolve().parent
SS = 3
LW = 8.5                    # kontur kalınlığı (taban px)
# göz kutusu (taban px) ve yeni gözbebeğinin genişliği (iç köşeden, taban px)
EYES = [((430, 385, 595, 475), 64), ((705, 395, 835, 490), 44)]


def _fill_holes(m):
    """m: bool (True = siyah). Kenardan ulaşılamayan beyaz bölgeleri doldurur."""
    h, w = m.shape
    pad = Image.new("L", (w + 2, h + 2), 0)
    pad.paste(Image.fromarray(m.astype(np.uint8) * 255), (1, 1))
    ImageDraw.floodfill(pad, (0, 0), 128)
    return np.asarray(pad)[1:-1, 1:-1] != 128


def _erode_disk(m, r):
    out = m.copy()
    h, w = m.shape
    ri = int(np.ceil(r))
    pad = np.zeros((h + 2 * ri, w + 2 * ri), bool)
    pad[ri:ri + h, ri:ri + w] = m
    for dy in range(-ri, ri + 1):
        for dx in range(-ri, ri + 1):
            if dx * dx + dy * dy <= r * r:
                out &= pad[ri + dy:ri + dy + h, ri + dx:ri + dx + w]
    return out


def shift_eye(rgba, box, pw):
    x0, y0, x1, y1 = box
    crop = rgba.crop(box)
    w, h = crop.size
    a = np.asarray(crop, np.float32)
    lum = a[..., :3].mean(-1)
    black = Image.fromarray((((a[..., 3] > 128) & (lum < 128)) * 255).astype(np.uint8))
    B = np.asarray(black.resize((w * SS, h * SS), Image.BICUBIC)) > 127
    R = _fill_holes(B)
    I = _erode_disk(R, LW * SS)
    ring = R & ~I
    ys, xs = np.nonzero(I)
    xr = xs.max()
    yc = ys[xs >= xr - pw * SS * 0.5].mean()
    yy, xx = np.mgrid[0:h * SS, 0:w * SS]
    # elips: merkez iç köşenin biraz dışında, sol kenarı gözün içine doğru kavisli (eski gözbebeğinin ayna görüntüsü)
    ell = ((xx - (xr + pw * SS * 0.2)) / (pw * SS * 1.2)) ** 2 + ((yy - yc) / (h * SS * 0.55)) ** 2 <= 1.0
    pupil = I & ell
    new_black = (B & ~I) | ring | pupil
    nb = np.asarray(Image.fromarray((new_black * 255).astype(np.uint8)).resize((w, h), Image.LANCZOS), np.float32) / 255
    Rm = np.asarray(Image.fromarray((R * 255).astype(np.uint8)).resize((w, h), Image.LANCZOS), np.float32) / 255
    out = a.copy()
    region = Rm > 0
    for c in range(3):
        out[..., c] = np.where(region, 255.0 * (1 - nb) * Rm + a[..., c] * (1 - Rm), a[..., c])
    out[..., 3] = np.where(region, np.maximum(a[..., 3], 255 * Rm), a[..., 3])
    rgba.paste(Image.fromarray(np.clip(out, 0, 255).astype(np.uint8), "RGBA"), (x0, y0))


def main():
    base = Image.open(K / "taban" / "nervous_temiz.png").convert("RGBA")
    for box, pw in EYES:
        shift_eye(base, box, pw)
    out = K / "taban" / "nervous_temiz_ice.png"
    base.save(out, optimize=True)
    print(out)


if __name__ == "__main__":
    main()
