"""uzun/talidomit-turkiye arşiv görselleri: indirilen kaynaklardan hazır kırpımlar (img/) ve telifli/izin bekleyen
kırpımlar (img/telifli/, git'e girmez). Ayrıca yazı kartı yedekleri (img/cizim/) ve fosforlu kalem kutuları
(img/kutular.json: motorun `manset.kutular` alanı için piksel kutuları).

    python uzun/talidomit-turkiye/img/arsiv_uret.py <kaynak_klasoru>

<kaynak_klasoru>: tam boy indirmeler (repo dışı). Adresler, yazarlar ve lisanslar: uzun/talidomit-turkiye/VARLIKLAR.md.
PDF sayfaları pdftoppm (poppler) ile 220 dpi çizilir.
"""
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
TEL = HERE / "telifli"
CIZ = HERE / "cizim"
KUTU: dict[str, dict] = {}
MAXW = 2560


def kaydet(im: Image.Image, yol: Path, q: int = 92) -> Image.Image:
    yol.parent.mkdir(parents=True, exist_ok=True)
    if im.width > MAXW:
        im = im.resize((MAXW, round(im.height * MAXW / im.width)), Image.LANCZOS)
    if yol.suffix == ".png":
        im.save(yol, optimize=True)
    else:
        im.convert("RGB").save(yol, quality=q, optimize=True)
    print(f"{yol.relative_to(HERE)} {im.size}")
    return im


def kenar_kirp(im: Image.Image, esik: int = 236, pay: int = 4) -> Image.Image:
    """Taramadaki beyaz/açık kenar boşluğunu kırpar (kartpostal, panorama)."""
    g = np.asarray(im.convert("L"))
    rows = np.where((g < esik).mean(1) > 0.5)[0]
    cols = np.where((g < esik).mean(0) > 0.5)[0]
    if len(rows) and len(cols):
        return im.crop((cols[0] + pay, rows[0] + pay, cols[-1] - pay, rows[-1] - pay))
    return im


def kirp169(im: Image.Image, x0: int, y0: int, w: int) -> Image.Image:
    return im.crop((x0, y0, x0 + w, y0 + round(w * 9 / 16)))


def pdf_sayfa(pdf: Path, sayfa: int, dpi: int = 220) -> Image.Image:
    with tempfile.TemporaryDirectory() as d:
        subprocess.run(["pdftoppm", "-r", str(dpi), "-f", str(sayfa), "-l", str(sayfa), "-png", str(pdf), f"{d}/s"],
                       check=True)
        return Image.open(next(Path(d).glob("s*.png"))).convert("RGB")


def serbest(K: Path) -> None:
    o = lambda ad: Image.open(K / ad).convert("RGB")  # noqa: E731
    im = o("contergan_teneke_oesterreich_ccbysa3.jpg")
    kaydet(im, HERE / "foto_contergan_teneke.jpg")
    kaydet(kirp169(im, 0, 230, 2832), HERE / "foto_contergan_teneke_169.jpg")
    kaydet(o("contergan_forte_kutu_tobitoaster_ccbysa4.jpg").crop((0, 60, 2785, 1720)), HERE / "foto_contergan_forte.jpg")
    kaydet(kirp169(o("kupferhof_grunenthal_stolberg_ccby3.jpg"), 0, 70, 1920), HERE / "foto_kupferhof_grunenthal_169.jpg")
    kaydet(kirp169(o("stolberg_grunenthal_merkez_2006_ccbysa3.jpg"), 0, 230, 2048), HERE / "foto_stolberg_grunenthal_169.jpg")
    kaydet(kirp169(o("giessen_marktplatz_1957_ccbysa4.jpg"), 0, 120, 1920), HERE / "foto_giessen_1957_169.jpg")
    kaydet(o("koln_alisveris_caddesi_1960_bundesarchiv_ccbysa3de.jpg"), HERE / "foto_koln_1960.jpg")
    # Bundesarchiv künye şeridi alttan kırpılır (atıf VARLIKLAR.md ve açıklamada)
    kaydet(o("ddr_ilac_kacakciligi_1961_0002_contergan_bundesarchiv_ccbysa3de.jpg").crop((0, 0, 800, 574)),
           HERE / "foto_dogu_berlin_kacak_ilac_1961.jpg")
    kaydet(o("protez_kollar_roehampton_sciencemuseum_ccbysa2.jpg"), HERE / "foto_protez_kollar.jpg")
    kaydet(o("kelsey_portre_1960lar_pd.jpg"), HERE / "foto_kelsey_masa.jpg")
    kaydet(o("kelsey_jfk_1962_pd.jpg"), HERE / "foto_kelsey_kennedy_1962.jpg")
    kaydet(o("jfk_imza_1962_ilac_yasasi_pd.jpg"), HERE / "foto_kennedy_imza_1962.jpg")
    pano = kenar_kirp(o("ankara_kaleden_panorama_salt_kisitsiz.jpg"))
    pano.save(HERE / "foto_ankara_panorama_tam.jpg", quality=92, optimize=True)
    print(f"foto_ankara_panorama_tam.jpg {pano.size}")
    kaydet(kenar_kirp(o("ankara_bankalar_caddesi_salt_kisitsiz.jpg")), HERE / "foto_ankara_bankalar_caddesi.jpg")
    cift = o("ankara_sergievi_bankalar_salt_kisitsiz.jpg")               # ÜST = Bankalar Caddesi, ALT = Sergi Evi
    W, H = cift.size
    kaydet(kenar_kirp(cift.crop((0, 0, W, H // 2))), HERE / "foto_ankara_bankalar_kartpostal_ust.jpg")
    kaydet(kenar_kirp(cift.crop((0, H // 2, W, H))), HERE / "foto_ankara_sergievi_kartpostal_alt.jpg")
    kaydet(o("saglik_bakanligi_bina_2014_ccbysa3.jpg").crop((0, 0, 1280, 1230)), HERE / "foto_saglik_bakanligi.jpg")
    kaydet(o("tavuk_embriyosu_11gun_cdc_pd.jpg"), HERE / "foto_tavuk_embriyosu.jpg")
    br = o("brezilya_talidomid_kutusu_2009_ccbysa4.jpg")
    kaydet(br, HERE / "foto_brezilya_kutu.jpg")
    kaydet(br.crop((380, 860, 920, 1400)), HERE / "foto_brezilya_piktogram.jpg")
    KUTU["foto_brezilya_kutu.jpg"] = {"piktogram": [431, 914, 863, 1345]}


def telifli(K: Path) -> None:
    """Hesap sahibinin lisans kararını bekleyenler: img/telifli/ (repo dışı)."""
    o = lambda ad: Image.open(K / ad).convert("RGB")  # noqa: E731
    kaydet(o("kevadon_1960_fda_pd_belirsiz.jpg"), TEL / "kevadon_1960_fda.jpg")
    kaydet(o("distaval_reklam_1958_wellcome_InC.jpg"), TEL / "distaval_reklam_wellcome.jpg")
    # Wellcome broşüründe 'complete safety ... pregnant women' cümlesi YOK; vurgulanabilecek satır 'no known toxicity'
    KUTU["telifli/distaval_reklam_wellcome.jpg"] = {"Safe Sedation": [146, 304, 692, 388],
                                                     "no known toxicity": [174, 886, 436, 922],
                                                     "untoward side-effects": [174, 914, 448, 944]}
    # TFD Bülteni 26 (Temmuz 1994): kapak + s. 2 (Kayaalp'in anma yazısı); s. 2 gövdesi kırpılır
    kapak = pdf_sayfa(K / "tfd_bulten26_1994.pdf", 1)
    kaydet(kapak.crop((60, 40, kapak.width - 40, kapak.height - 40)), TEL / "tfd_bulten26_1994_kapak.jpg")
    s2 = pdf_sayfa(K / "tfd_bulten26_1994.pdf", 2).crop((140, 120, 1760, 2300))
    kaydet(s2, TEL / "tfd_bulten26_1994_s2.jpg")
    KUTU["telifli/tfd_bulten26_1994_s2.jpg"] = {
        "baslik": [191, 89, 1220, 182],
        "Sağlık Bakanlığına başta İlaç ve Eczacılık": [772, 1188, 1460, 1232],
        "Genel Müdürlüğü olmak üzere danışman ve yol gösterici olarak yaptığı": [190, 1229, 1460, 1275],
        "katkıdır.": [190, 1272, 330, 1312]}
    if (K / "tfd_akcasu.png").exists():                                  # demo'daki TFD 2012 kırpımı (aynı kaynak)
        kaydet(Image.open(K / "tfd_akcasu.png").convert("RGB"), TEL / "tfd_bulten114_2012_kirpim.png")
    # TİTCK KÜB (THALIDOMIDE CELGENE 50 mg): s. 5 bölüm 4.4 kesiti + s. 21 ilk ruhsat tarihi
    pt = 220 / 72
    p5 = pdf_sayfa(K / "titck_thalidomide_kub.pdf", 5)
    x0, y0 = round(60 * pt), round(476 * pt)
    kes = p5.crop((x0, y0, round(545 * pt), round(592 * pt)))
    kaydet(kes, TEL / "kub_bolum44_kesit.png")
    b = lambda X0, Y0, X1, Y1: [round(X0 * pt) - x0 - 4, round(Y0 * pt) - y0 - 4, round(X1 * pt) - x0 + 4,  # noqa: E731
                                round(Y1 * pt) - y0 + 4]
    KUTU["telifli/kub_bolum44_kesit.png"] = {
        "Talidomid, gebe kadınlar": b(325, 549, 454, 563),
        "tarafından kesinlikle kullanılmamalıdır.": b(289, 577, 484, 590),
        "atlanan_1 (veya …)": b(461, 549, 540, 563), "atlanan_2": b(71, 563, 540, 576), "atlanan_3": b(71, 577, 283, 590)}
    # atlanan kısım gri (senaryo B6.7: 'atlanan veya … gebe kalabilecek kadınlar kısmı gri')
    gri = kes.copy().convert("RGBA")
    lay = Image.new("RGBA", gri.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    for k in ("atlanan_1 (veya …)", "atlanan_2", "atlanan_3"):
        d.rectangle(KUTU["telifli/kub_bolum44_kesit.png"][k], fill=(255, 255, 255, 170))
    gri.alpha_composite(lay)
    kaydet(gri.convert("RGB"), TEL / "kub_bolum44_kesit_gri.png")
    KUTU["telifli/kub_bolum44_kesit_gri.png"] = KUTU["telifli/kub_bolum44_kesit.png"]
    p21 = pdf_sayfa(K / "titck_thalidomide_kub.pdf", 21)
    x0, y0 = round(60 * pt), round(380 * pt)
    kaydet(p21.crop((x0, y0, round(400 * pt), round(430 * pt))), TEL / "kub_ilk_ruhsat_2004.png")
    KUTU["telifli/kub_ilk_ruhsat_2004.png"] = {"31/05/2004": [round(151 * pt) - x0 - 4, round(409 * pt) - y0 - 4,
                                                               round(206 * pt) - x0 + 4, round(422 * pt) - y0 + 4]}


def _font(ad, size):
    for p in {"mono": [ROOT / "assets/fonts/LiberationMono-Bold.ttf"],
              "serif": [Path("/usr/share/fonts/truetype/liberation/LiberationSerif-Regular.ttf"),
                        Path("/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf"), ROOT / "assets/fonts/Poppins-Bold.ttf"],
              "poppins": [ROOT / "assets/fonts/Poppins-Bold.ttf"]}[ad]:
        if Path(p).exists():
            return ImageFont.truetype(str(p), size)
    raise FileNotFoundError(ad)


def _kart(satirlar, W=1800, H=1000, zemin=None):
    """Eski kâğıt dokulu yazı kartı. satirlar: [(metin, font, boyut, renk, y)] -> (im, {metin: kutu})."""
    base = Image.open(zemin).convert("RGB").resize((W, H)) if zemin and Path(zemin).exists() else \
        Image.new("RGB", (W, H), (238, 230, 210))
    d = ImageDraw.Draw(base)
    kutular = {}
    for metin, f, s, renk, x, y in satirlar:
        fnt = _font(f, s)
        d.text((x, y), metin, font=fnt, fill=renk)
        kutular[metin] = list(d.textbbox((x, y), metin, font=fnt))
    return base, kutular


def kartlar() -> None:
    zemin = HERE / "doku_kagit.jpg"
    ink = (32, 30, 28)
    # Distaval yedeği: belgeli İngilizce reklam cümlesi (araştırma D11/W4) daktiloyla + kaynak satırı
    satir = [("Distaval can be given with complete safety", "mono", 64, ink, 120, 260),
             ("to pregnant women and nursing mothers", "mono", 64, ink, 120, 360),
             ("without adverse effect on mother or child.", "mono", 64, ink, 120, 460),
             ("İngiltere'deki Distaval reklamından (1958-61)", "serif", 40, (110, 100, 90), 120, 640)]
    im, k = _kart(satir, zemin=zemin)
    d = ImageDraw.Draw(im)
    fnt = _font("mono", 64)
    pre = d.textlength("Distaval can be given with ", font=fnt)
    cs = d.textlength("complete safety", font=fnt)
    pw = d.textlength("pregnant women and nursing mothers", font=fnt)
    tw = d.textlength("to ", font=fnt)
    kutu = {"complete safety": [round(120 + pre) - 6, 252, round(120 + pre + cs) + 6, 340],
            "pregnant women and nursing mothers": [round(120 + tw) - 6, 352, round(120 + tw + pw) + 6, 440]}
    kaydet(im, CIZ / "distaval_yedek_kart.jpg")
    KUTU["cizim/distaval_yedek_kart.jpg"] = kutu
    # KÜB 4.4 yedeği: tam cümle, atlanan kısım gri
    gri = (165, 160, 152)
    satir = [("THALIDOMIDE CELGENE · Kısa Ürün Bilgisi · Bölüm 4.4", "serif", 40, (110, 100, 90), 120, 120),
             ("Talidomid, gebe kadınlar", "mono", 58, ink, 120, 260),
             ("veya THALIDOMIDE CELGENE Gebelik Önleme", "mono", 58, gri, 120, 345),
             ("Programının bütün koşulları yerine", "mono", 58, gri, 120, 430),
             ("getirilmediğinde gebe kalabilecek kadınlar", "mono", 58, gri, 120, 515),
             ("tarafından kesinlikle kullanılmamalıdır.", "mono", 58, ink, 120, 620)]
    im, k = _kart(satir, zemin=zemin)
    kaydet(im, CIZ / "kub_bolum44_yedek_kart.jpg")
    d = ImageDraw.Draw(im)
    fnt = _font("mono", 58)
    tal = d.textlength("Talidomid, ", font=fnt)
    gk = d.textlength("gebe kadınlar", font=fnt)
    tf = d.textlength("tarafından ", font=fnt)
    kk = d.textlength("kesinlikle kullanılmamalıdır.", font=fnt)
    KUTU["cizim/kub_bolum44_yedek_kart.jpg"] = {
        "gebe kadınlar": [round(120 + tal) - 6, 252, round(120 + tal + gk) + 6, 335],
        "kesinlikle kullanılmamalıdır.": [round(120 + tf) - 6, 612, round(120 + tf + kk) + 6, 695]}


if __name__ == "__main__":
    K = Path(sys.argv[1])
    serbest(K)
    telifli(K)
    kartlar()
    old = json.loads((HERE / "kutular.json").read_text()) if (HERE / "kutular.json").exists() else {}
    old.update(KUTU)
    old.setdefault("cizim/gazete_1961_canlandirma.png", {"CONTERGAN": [134, 368, 1277, 505]})
    (HERE / "kutular.json").write_text(json.dumps(old, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print("kutular.json", len(old))
