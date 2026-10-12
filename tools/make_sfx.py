#!/usr/bin/env python3
"""Telifsiz ses efektlerini ffmpeg ile sentezler -> assets/sfx/*.wav

    python tools/make_sfx.py              # hepsi
    python tools/make_sfx.py pop tus      # yalnız adı verilenler (var olanlara dokunmaz)

Hepsi matematiksel olarak üretildiği için telif sorunu yoktur. Daha kaliteli
efekt/müzik için assets/music/README.md'ye bakın.
"""

import subprocess
from pathlib import Path

OUT = Path(__file__).resolve().parent.parent / "assets" / "sfx"

SFX = {
    # sinematik "boom": düşen frekanslı sinüs + gürültü darbesi
    "boom": ("aevalsrc='0.9*sin(2*PI*(60-30*t)*t)*exp(-3.2*t)+0.25*(random(0)-0.5)*exp(-18*t)':d=2.2:s=48000",
             "lowpass=f=900,volume=1.4"),
    # kısa sert vuruş (kesme anları için)
    "hit": ("aevalsrc='0.8*sin(2*PI*90*t)*exp(-9*t)+0.5*(random(0)-0.5)*exp(-30*t)':d=0.9:s=48000",
            "lowpass=f=2500,volume=1.3"),
    # geçiş "whoosh"u
    "whoosh": ("anoisesrc=c=pink:d=0.8:a=0.6:r=48000",
               "bandpass=f=900:w=1.4,afade=t=in:d=0.45:curve=exp,afade=t=out:st=0.45:d=0.35,volume=9"),
    # gerilim yükselişi
    "riser": ("aevalsrc='0.35*sin(2*PI*(180+500*t*t/2.5)*t)*(t/2.5)+0.25*(random(0)-0.5)*(t/2.5)':d=2.5:s=48000",
              "highpass=f=120,afade=t=out:st=2.35:d=0.15"),
    # kalp atışı (2 vuruş)
    "heartbeat": ("aevalsrc='0.9*sin(2*PI*50*t)*exp(-25*t)+0.7*sin(2*PI*45*(t-0.28))*exp(-25*(t-0.28))*gte(t,0.28)':d=1.0:s=48000",
                  "lowpass=f=400,volume=1.6"),
    # cızırtı / statik
    "static": ("anoisesrc=c=white:d=0.6:a=0.4:r=48000", "bandpass=f=3000:w=1.2,afade=t=out:st=0.45:d=0.15,volume=3.5"),
    # fotoğraf makinesi deklanşörü (kanıt fotoğrafları için)
    "shutter": ("aevalsrc='(random(0)-0.5)*(exp(-120*t)+0.7*exp(-120*(t-0.07))*gte(t,0.07))':d=0.25:s=48000",
                "highpass=f=1500,volume=2.5"),
    # --- uzun format (wojak/uzun) için ---
    # balon/ikon "pop"u: perdesi hızla düşen kısa ton
    "pop": ("aevalsrc='0.7*sin(2*PI*(420+900*exp(-35*t))*t)*exp(-26*t)+0.15*(random(0)-0.5)*exp(-300*t)':d=0.2:s=48000",
            "highpass=f=180,afade=t=out:st=0.15:d=0.05,volume=1.2"),
    # daktilo tuşu (etiket yazılırken harf başına)
    "tus": ("aevalsrc='(random(0)-0.5)*exp(-170*t)+0.35*sin(2*PI*1700*t)*exp(-110*t)+0.2*sin(2*PI*230*t)*exp(-60*t)':d=0.07:s=48000",
            "highpass=f=400,volume=1.6"),
    # fosforlu kalem sürtünmesi
    "kalem": ("aevalsrc='(random(0)-0.5)*(0.55+0.45*sin(2*PI*19*t))':d=0.6:s=48000",
              "bandpass=f=2600:w=1.3,afade=t=in:d=0.06,afade=t=out:st=0.45:d=0.15,volume=2.2"),
    # sayaç tıkı
    "tik": ("aevalsrc='0.8*sin(2*PI*2400*t)*exp(-280*t)+0.3*(random(0)-0.5)*exp(-500*t)':d=0.04:s=48000",
            "highpass=f=800,volume=1.0"),
    # haritada ülke yanarken yumuşak ton
    "blip": ("aevalsrc='0.45*sin(2*PI*660*t)*exp(-12*t)+0.2*sin(2*PI*990*t)*exp(-18*t)':d=0.4:s=48000",
             "afade=t=in:d=0.004,volume=1.0"),
    # kısa geçiş hışırtısı (itme geçişi, isim etiketi)
    "whoosh_kisa": ("anoisesrc=c=pink:d=0.45:a=0.6:r=48000",
                    "bandpass=f=1300:w=1.2,afade=t=in:d=0.2:curve=exp,afade=t=out:st=0.2:d=0.25,volume=8"),
    # karanlık ambiyans altlığı (müzik yoksa kullanılabilir, 30 sn, döngüye uygun)
    "drone": ("aevalsrc='0.22*sin(2*PI*55*t)*(0.75+0.25*sin(2*PI*0.2*t))+0.12*sin(2*PI*82.4*t)+0.07*sin(2*PI*110.3*t)*(0.5+0.5*sin(2*PI*0.13*t))':d=30:s=48000",
              "lowpass=f=600,aecho=0.8:0.7:120|300:0.3|0.2,volume=1.3"),
}


def main() -> None:
    import sys
    OUT.mkdir(parents=True, exist_ok=True)
    secili = sys.argv[1:] or list(SFX)
    for name in secili:
        if name not in SFX:
            sys.exit(f"bilinmeyen efekt: {name} ({', '.join(SFX)})")
    for name, (src, flt) in ((n, SFX[n]) for n in secili):
        out = OUT / f"{name}.wav"
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "lavfi", "-i", src, "-af", flt,
                        "-ac", "2", "-ar", "48000", str(out)], check=True)
        print(f"-> {out.name}")


if __name__ == "__main__":
    main()
