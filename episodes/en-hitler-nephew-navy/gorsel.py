"""en-hitler-nephew-navy: img/ dosyalarini indirilen kaynaklardan uretir (python episodes/en-hitler-nephew-navy/gorsel.py).

arka.jpg   : U.S.S. Iowa (BB61) in the New York Navy Yard (1943, US Navy / NARA, kamu malı), kare kırpım, hafif karartma
ev_1.jpg   : William-Patrick-Hitler.jpg (US Navy fotoğrafı, kamu malı, 190x222) — yüz + 'Target Berlin' afişi kırpımı, büyütüldü
ev_2.jpg   : KENDİ ÜRETİMİZ — 3 Mart 1942 mektup sayfasının yazı makinesi canlandırması; satırların hepsi gerçek mektup metni (IBTimes/Letters of Note tam metin), uydurma satır yok
"""
from pathlib import Path
import random
import numpy as np
from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont

HERE = Path(__file__).resolve().parent
IMG = HERE / "img"

# ---- Arka plan
bg = Image.open(IMG / "arka_aday4.jpg").convert("RGB")
bg = bg.crop((560, 130, 1829, 1399)).resize((1080, 1080), Image.LANCZOS)
a_ = np.array(bg).astype(float)
knee = a_ > 150
a_[knee] = 150 + (a_[knee] - 150) * 0.5     # patlayan gökyüzünü sıkıştır (karartma değil, yalnız parlak uç)
bg = Image.fromarray(np.clip(a_, 0, 255).astype("uint8"))
bg.save(IMG / "arka.jpg", quality=93)

# ---- Kanıt 1: Donanma fotoğrafı (190x222 kaynak): GELENEKSEL büyütme (bicubic + hafif bulanıklık/keskinleştirme + film gürültüsü).
#      Yapay zekâ ölçekleyici yok (kanal kuralı). Alternatif ev_1_edsr_alt.jpg: EDSR yalnız yüz/gövde (x<540), sağ taraf bicubic;
#      hesap sahibi isterse ev_1.jpg yerine koyabilir (sinir ağı kullanır; kuralla çelişebilir).
import cv2
im0 = cv2.imread(str(IMG / "wph_orig.jpg"))
c0 = im0[30:174, 0:190]
b_ = np.array(Image.fromarray(cv2.cvtColor(c0, cv2.COLOR_BGR2GRAY)).resize((1080, 816), Image.BICUBIC)
              .filter(ImageFilter.GaussianBlur(0.9)).filter(ImageFilter.UnsharpMask(2, 60, 2))).astype(float)
noise = np.random.default_rng(3).normal(0, 4, b_.shape)
Image.fromarray(np.clip(b_ + noise, 0, 255).astype("uint8")).convert("RGB").save(IMG / "ev_1.jpg", quality=93)
import os
if os.path.exists("/tmp/EDSR_x4.pb"):
    sr = cv2.dnn_superres.DnnSuperResImpl_create()
    sr.readModel("/tmp/EDSR_x4.pb"); sr.setModel("edsr", 4)
    up = cv2.resize(sr.upsample(c0), (1080, 816), interpolation=cv2.INTER_LANCZOS4)
    e_ = cv2.cvtColor(up, cv2.COLOR_BGR2GRAY).astype(float)
    m_ = np.zeros((816, 1080), float); m_[:, 540:] = 1
    m_ = cv2.GaussianBlur(m_, (0, 0), 14)
    o_ = e_ * (1 - m_) + b_ * m_ + noise
    Image.fromarray(np.clip(o_, 0, 255).astype("uint8")).convert("RGB").save(IMG / "ev_1_edsr_alt.jpg", quality=93)

# ---- Kanıt 2: mektup sayfası canlandırması (gerçek mektup metni, yazı makinesi, sayfadan bir kesit)
W, H = 1080, 816
PW, PH = 1260, 980          # döndürülmeden önceki sayfa tuvali
FR = "/usr/share/fonts/truetype/liberation/LiberationMono-Regular.ttf"
rng = np.random.default_rng(11)
FS, LH, CH = 39, 58, 40      # yazı, satır aralığı, satır başına karakter
paras = [
    ("Permit me to outline as briefly as possible the circumstances of my position, the solution of which I feel could so easily be achieved should you feel moved to give your kind intercession and decision.", True),
    ("I am the nephew and only descendant of the ill-famed Chancellor and Leader of Germany who today so despotically seeks to enslave the free and Christian peoples of the globe.", True),
    ("Under your masterful leadership men of all creeds and nationalities are waging desperate war to determine, in the last analysis, whether they shall finally serve and live an ethical society under God or become enslaved by a devilish and pagan regime.", True),
]
import textwrap
lines = []
for k, (p, indent) in enumerate(paras):
    wrapped = textwrap.wrap("     " + p, 39 if k == 1 else CH)
    wrapped[0] = wrapped[0] if k else wrapped[0]
    if k == 0:
        wrapped = wrapped[-2:]     # sayfa kesiti: ilk paragrafın son 2 satırı (tam satırda kesilir)
    if k == 2:
        wrapped = wrapped[:3]      # alt kesit: tam satırda biter
    lines += wrapped
    if k < len(paras) - 1:
        lines.append("")

paper = np.zeros((PH, PW, 3), float)
paper[:] = (232, 224, 205)
yy, xx = np.mgrid[0:PH, 0:PW]
vig = 1 - 0.16 * (((xx - PW / 2) / (PW / 2)) ** 2 + ((yy - PH / 2) / (PH / 2)) ** 2)
paper *= vig[..., None]
paper += rng.normal(0, 2.6, (PH, PW, 1))
blot = np.array(Image.fromarray(rng.integers(0, 255, (PH // 60, PW // 60), dtype=np.uint8)).resize((PW, PH), Image.BICUBIC)).astype(float)
paper += ((blot - 128) / 128 * 5)[..., None]
# yatay katlanma izleri (açık+koyu çizgi)
for fy in (int(PH * 0.34), int(PH * 0.69)):
    paper[fy - 3:fy, :, :] *= 0.91
    paper[fy:fy + 4, :, :] *= 1.04
page = Image.fromarray(np.clip(paper, 0, 255).astype("uint8"))
ink = Image.new("RGB", (PW, PH), (24, 22, 22))
mask = Image.new("L", (PW, PH), 0)
md = ImageDraw.Draw(mask)
f = ImageFont.truetype(FR, FS)
cw = md.textlength("M", font=f)
y = 112
for ln in lines:
    x = 170
    for chh in ln:
        if chh != " ":
            a_ = int(np.clip(rng.normal(205, 28), 120, 255))
            md.text((x + float(rng.normal(0, 0.5)), y + float(rng.normal(0, 0.9))), chh, font=f, fill=a_)
        x += cw
    y += LH
mask = mask.filter(ImageFilter.GaussianBlur(0.55))
page.paste(ink, (0, 0), mask)
# hafif eğim, kesit
page = page.rotate(0.45, resample=Image.BICUBIC, fillcolor=(222, 214, 196))
ox, oy = (PW - W) // 2, 54
out = page.crop((ox, oy, ox + W, oy + H))
a2 = np.array(out).astype(float)
# sol kenar gölgesi (ciltten) ve alt kenar kararması
sh = np.clip((90 - np.arange(W)) / 90, 0, 1) ** 2
a2 *= (1 - 0.16 * sh)[None, :, None]
edge = np.clip((20 - np.arange(W)) / 20, 0, 1)   # sayfanın sol kenarı: masa gölgesi
a2 = a2 * (1 - 0.6 * edge)[None, :, None]
out = Image.fromarray(np.clip(a2, 0, 255).astype("uint8")).filter(ImageFilter.GaussianBlur(0.25))
out.save(IMG / "ev_2.jpg", quality=93)
print("satir:", len(lines))
