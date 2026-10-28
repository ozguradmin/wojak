"""en-mechanical-turk görselleri: ham dosyalardan (img/ham_*) üretir. python episodes/en-mechanical-turk/gorsel.py"""
from pathlib import Path
from PIL import Image, ImageEnhance, ImageOps, ImageFilter
import numpy as np, colorsys

H = Path(__file__).resolve().parent / "img"


def olc(im):
    a = np.array(im.convert("RGB")).astype(float) / 255
    mx, mn = a.max(-1), a.min(-1)
    sat = np.where(mx > 0, (mx - mn) / np.maximum(mx, 1e-6), 0).mean()
    g = np.array(im.convert("L").resize((720, 720)), dtype=float)
    lap = (np.roll(g, 1, 0) + np.roll(g, -1, 0) + np.roll(g, 1, 1) + np.roll(g, -1, 1) - 4 * g)[1:-1, 1:-1]
    return round(float(np.array(im.convert("L")).mean()), 1), round(float(sat), 3), round(float(lap.var()), 1)


def bg():
    im = Image.open(H / "arka_plan_meytens_1763.jpg").convert("RGB")  # 1280x1619
    w, h = im.size
    im = im.crop((0, 120, 1280, 120 + 1280)).resize((1080, 1080), Image.LANCZOS)
    im = ImageEnhance.Color(im).enhance(0.42)
    im = ImageEnhance.Brightness(im).enhance(1.12)
    im.save(H / "bg_court.jpg", quality=93)
    print("bg", olc(im))


def kanit(src, out, top, scale_w=1080):
    im = Image.open(H / src).convert("RGB")
    w, h = im.size
    nh = round(h * scale_w / w)
    im = im.resize((scale_w, nh), Image.LANCZOS)
    im = im.crop((0, top, scale_w, top + 816))
    im.save(H / out, quality=94)
    print(out, im.size)


if __name__ == "__main__":
    bg()
    kanit("kanit_1_racknitz_tab1_makine.jpg", "ev_1_turk_kapaklar.jpg", 60)
    kanit("kanit_3_racknitz_tab3_operator.jpg", "ev_2_turk_ici.jpg", 100)
