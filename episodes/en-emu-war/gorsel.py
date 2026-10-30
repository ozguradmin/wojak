"""en-emu-war görselleri (kaynaklardan yeniden üretir):  python episodes/en-emu-war/gorsel.py

bg.jpg      : 'Wheat fields in Brookton, Western Australia 03.jpg' (Ronnievonjohnson, 2026, CC BY-SA 4.0; 1920 px sürüm). Alt-orta kare kırpım
              (960 px -> 1080), renk 0.42, parlaklık 1.12.
kanit_1.jpg : 'Australian soldiers resting during Emu War.jpg' (1932, PD), 1080 genişliğe büyütüldü, hafif keskinleştirildi, autocontrast.
kanit_2_kupur.jpg: kupur.py
"""
from pathlib import Path
from PIL import Image, ImageEnhance, ImageFilter, ImageOps

HERE = Path(__file__).resolve().parent
RAW = Path("/tmp/arastirma/emu-war/raw")
SRC = HERE / "img" / "src"


def main():
    im = Image.open(SRC / "brookton03.jpg").convert("RGB")
    w, h = im.size
    im = im.crop((330, h - 960, 1290, h)).resize((1080, 1080), Image.LANCZOS)
    im = ImageEnhance.Color(im).enhance(0.42)
    im = ImageEnhance.Brightness(im).enhance(1.12)
    im.save(HERE / "img" / "bg.jpg", quality=93)
    k = Image.open(SRC / "soldiers_resting.jpg").convert("RGB")
    k = k.resize((1080, round(k.height * 1080 / k.width)), Image.LANCZOS)
    k = ImageOps.autocontrast(k, cutoff=0.05).filter(ImageFilter.UnsharpMask(1.2, 40, 2))
    k.save(HERE / "img" / "kanit_1.jpg", quality=93)
    print("bg", im.size, "kanit_1", k.size)


if __name__ == "__main__":
    main()
