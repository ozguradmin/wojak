"""Hava müzikleri: besteler (özgün; Claude, 12.11.2026). İşleyen: tools/hava_muzik.py.

Her beste 14,0 sn'lik bir döngüdür. Çoğu imza valsi gibi iki vuruşluk bir "ön çekiş"le başlar ve sondaki yarım ölçü
döngüde bu ön çekişe bağlanır. Kanal tanınırlığı: imza valsinin (Gölge) düşen "5-4 | 3" iç çekişi her parçada bir
yerde geçer (gizemde başta ve sonda, merakta ön çekişte, ironikte fagot/klarnet ön çekişinde, masallarda başta; Lidya
renkli masalda 5-#4 | 3). Bilinen bir ezgiden alıntı yok; armoniler türün genel kalıpları (i-VI-III-VII, inen bas,
Napoli ♭II, Lidya II).

Birim: `vurus` beste birimidir (4/4 ve 3/4'te dörtlük, 6/8'de sekizlik). Tempo, toplam vuruşun 14 sn'ye sığmasından
çıkar (Beste.bpm).
"""

from __future__ import annotations

from hava_muzik import Beste, Parca, ezgi, m

# GM programları (MuseScore General)
PIYANO, YUMUSAK_PIYANO = 0, (0, 8)
CELESTA, GLOCK, MUZIK_KUTUSU, VIBRAFON, MARIMBA, KSILOFON, CAN = 8, 9, 10, 11, 12, 13, 14
KEMAN, VIYOLA, CELLO, KONTRBAS, TREMOLO, PIZZ, ARP, TIMPANI = 40, 41, 42, 43, 44, 45, 46, 47
YAYLI_HIZLI, YAYLI_YAVAS = 48, 49
KORO_AA, KORO_UU = 52, 53
TROMPET, TROMBON, TUBA, KORNO, BAKIR = 56, 57, 58, 60, 61
OBUA, FAGOT, KLARNET, FLUT = 68, 70, 71, 73
TAIKO = 116


def P(ad, program, banka=0, **kw) -> Parca:
    return Parca(ad=ad, program=program, banka=banka, **kw)


def akor_deseni(p: Parca, bolumler, desen, birim, hizlar=(70,), kesik=0.6, kaydir=0.0):
    """bolumler: [(bas, sure, ["A4","D5","F5"]), ...]; her `birim` vuruşta desenden bir indeks çalınır (sıralı,
    döngülü; indeks akordaki notalardan biri ya da liste: aynı anda birkaç nota). hizlar: vuruş içindeki sıraya göre
    döngülü hız deseni."""
    k = 0
    for bas, sure, notalar in bolumler:
        n = [m(x) if isinstance(x, str) else x for x in notalar]
        t = bas + kaydir
        while t < bas + sure - 1e-9:
            i = desen[k % len(desen)]
            secim = i if isinstance(i, (list, tuple)) else [i]
            for j in secim:
                if j is None:
                    continue
                p.ekle(t, birim * kesik, n[j % len(n)], hizlar[k % len(hizlar)])
            k += 1
            t += birim


def tut(p: Parca, bolumler, hiz=60, kisalt=0.0):
    """Uzun akorlar: [(bas, sure, [notalar]), ...]."""
    for bas, sure, notalar in bolumler:
        for x in notalar:
            p.ekle(bas, sure - kisalt, x, hiz)


def bas_cizgisi(p: Parca, metin: str, bas=0.0, hiz=78, oktav=False, oktav_hiz=-14, kesik=True):
    """'D2:1 A1:1 ...' bas çizgisi; oktav=True üst oktavı da çalar (pizzicato kalınlığı)."""
    t = bas
    for tok in metin.split():
        if tok == "|":
            continue
        ad, _, s = tok.partition(":")
        sure = float(s)
        if ad != "r":
            gercek = sure * (0.55 if kesik else 0.95)
            p.ekle(t, gercek, ad, hiz)
            if oktav:
                p.ekle(t, gercek, m(ad) + 12, hiz + oktav_hiz)
        t += sure
    return t


def timpani_tremolo(p: Parca, nota, bas, sure, hiz0=30, hiz1=90, adim=0.25):
    t, n = bas, int(round(sure / adim))
    for i in range(n):
        p.ekle(t + i * adim, adim * 0.9, nota, int(hiz0 + (hiz1 - hiz0) * i / max(1, n - 1)))


def _kontrol(b: Beste, *parcalar):
    """Döngü sonunu aşan nota kısaltılır (kesimden sonrası zaten çalmaz); döngüden sonra başlayan nota hatadır."""
    for p in parcalar:
        for n in p.notalar:
            assert n.bas < b.vurus - 1e-6, f"{b.ad}/{p.ad}: nota döngü bittikten sonra başlıyor ({n.bas})"
            n.sure = min(n.sure, b.vurus - n.bas)
    return b


# ===================================================================================================== GİZEM
def gizem_a() -> Beste:
    """Saat: Re minör, 4/4, 137 bpm (yarım tempo hissi). Çelesta kutu-müziği ostinatosu, kesik pizzicato bas, alçak
    klarnet; inen bas (Re-Do-Si♭-La), sonra iv - Napoli ♭II - V(b9). Tremolo kemanlar ve timpani son iki ölçüde gerilir.
    İç çekiş: klarnet La-Sol | Fa (baştaki ön çekiş ve sondaki dönüş aynı)."""
    akorlar = [(0, 2, "A7"), (2, 4, "Dm"), (6, 4, "Dm/C"), (10, 4, "Bbmaj7"), (14, 2, "A7sus4"), (16, 2, "A7"),
               (18, 4, "Gmadd9"), (22, 4, "Ebmaj7#11"), (26, 4, "A7b9"), (30, 2, "Dm")]
    cel = P("celesta", CELESTA, db=-0.5, pan=0.25, yanki=0.45, eq=[("hp", 300)])
    yaz = [(0, 2, ["C#5", "E5", "G5"]), (2, 4, ["A4", "D5", "F5"]), (6, 4, ["A4", "D5", "F5"]),
           (10, 4, ["A4", "D5", "F5"]), (14, 2, ["D5", "E5", "A5"]), (16, 2, ["C#5", "E5", "A5"]),
           (18, 4, ["A4", "Bb4", "D5"]), (22, 4, ["G4", "Bb4", "D5"])]
    akor_deseni(cel, yaz, [0, 2, 1, 2], 0.5, hizlar=(64, 46, 54, 46), kesik=1.4)
    akor_deseni(cel, [(26, 4, ["C#5", "E5", "G5", "Bb5"])], [0, 1, 2, 3], 0.5, hizlar=(58, 60, 64, 68, 66, 70, 74, 78),
                kesik=1.4)
    akor_deseni(cel, [(30, 2, ["A4", "D5", "F5"])], [0, 2, 1, 2], 0.5, hizlar=(66, 48, 54, 46), kesik=1.4)
    kl = P("klarnet", KLARNET, db=0, pan=-0.15, yanki=0.32, eq=[("hp", 120), ("tepe", 2800, 1.5, 1.0)],
           ifade=[(0, 92), (18, 92), (26, 112), (30, 96)])
    son = ezgi(kl, "A4:1 G4:1 | F4:3 E4:1 | D4:3 E4:1 | F4:2 G4:1 A4:1 | Bb4:2 A4:2 | G4:2 A4:1 Bb4:1 | "
                   "D5:2 C5:1 Bb4:1 | E5:1 C#5:1 A4:1 G4:1 | F4:2", hiz=74)
    assert abs(son - 32) < 1e-9, son
    pz = P("pizz bas", PIZZ, db=-1, yanki=0.15, eq=[("hp", 35)])
    bas_cizgisi(pz, "A1:1 A2:1 | D2:2 A2:2 | C2:2 A2:2 | Bb1:2 F2:2 | A1:2 E2:2 | G1:2 D2:2 | Eb2:2 Bb2:2 | "
                    "A1:2 E2:1 A2:1 | D2:2", hiz=86, oktav=True)
    pad = P("yaylı", YAYLI_YAVAS, db=-7, yanki=0.42, eq=[("hp", 120), ("lp", 7000)],
            ifade=[(0, 58), (2, 62), (17, 64), (26, 96), (29, 104), (30, 70), (32, 60)])
    tut(pad, [(0, 2, ["E3", "G3", "C#4"]), (2, 12, ["D3", "F3", "A3"]), (14, 2, ["D3", "E3", "A3"]),
              (16, 2, ["C#3", "E3", "A3"]), (18, 8, ["D3", "G3", "Bb3"]), (26, 4, ["C#3", "E3", "G3", "Bb3"]),
              (30, 2, ["D3", "F3", "A3"])], hiz=70, kisalt=0.02)
    trem = P("tremolo", TREMOLO, db=-11, pan=0.3, yanki=0.45, eq=[("hp", 400)],
             ifade=[(18, 20), (26, 82), (29.5, 110)])
    trem.ekle(18, 12, "A5", 70)
    tim = P("timpani", TIMPANI, db=-4, yanki=0.32, eq=[("hp", 40)])
    tim.ekle(2, 1.5, "D2", 58)
    timpani_tremolo(tim, "A2", 26, 4, 22, 84)
    tim.ekle(30, 1.5, "D2", 72)
    b = Beste("gizem_a", "gizem", "Saat", "4/4", 32, [cel, kl, pz, pad, trem, tim], akorlar,
              "Re minör; çelesta ostinatosu, klarnet, inen bas, Napoli ♭II", yanki_rt60=1.9)
    return _kontrol(b, cel, kl, pz, pad, trem, tim)


def gizem_b() -> Beste:
    """Dehliz: Mi minör, 6/8 (noktalı dörtlük 69), 8 ölçü. Yumuşak kuyruklu piyanonun dalgalanan arpejleri; içteki ses
    Mi-Re#-Re-Do# iner (klişe çizgi), sonra Do maj7 - Fa (♭II) - Si7 - Mi minör(add9). Yüksek keman yalnız ve uzun;
    dibinde konser davulu ve uzak bir çan. İç çekiş: keman Si-La | Sol (son iki ölçü)."""
    akorlar = [(0, 6, "Em"), (6, 6, "Emmaj7/D#"), (12, 6, "Em7/D"), (18, 6, "Em6/C#"), (24, 6, "Cmaj7"),
               (30, 6, "Fmaj7"), (36, 6, "B7"), (42, 6, "Emadd9")]
    pi = P("piyano", 0, banka=8, db=-2, pan=-0.1, yanki=0.42, eq=[("hp", 45)],
           pedal=[(0, 127), (5.9, 0), (6, 127), (11.9, 0), (12, 127), (17.9, 0), (18, 127), (23.9, 0), (24, 127),
                  (29.9, 0), (30, 127), (35.9, 0), (36, 127), (41.9, 0), (42, 127), (47.95, 0)])
    sag = [(0, 6, ["G3", "B3", "E4"]), (6, 6, ["G3", "B3", "D#4"]), (12, 6, ["G3", "B3", "D4"]),
           (18, 6, ["G3", "B3", "C#4"]), (24, 6, ["G3", "B3", "E4"]), (30, 6, ["A3", "C4", "E4"]),
           (36, 6, ["A3", "D#4", "F#4"]), (42, 6, ["G3", "B3", "F#4"])]
    akor_deseni(pi, sag, [0, 1, 2, 1, 2, 1], 1, hizlar=(48, 40, 52, 38, 46, 36), kesik=0.9)
    for bas, nota in [(0, "E2"), (6, "D#2"), (12, "D2"), (18, "C#2"), (24, "C2"), (30, "F2"), (36, "B1"), (42, "E2")]:
        pi.ekle(bas, 5.8, nota, 62)
    pi.ekle(0, 5.8, "E1", 50)
    pi.ekle(42, 5.8, "E1", 50)
    vl = P("keman", KEMAN, banka=8, db=-1, pan=0.2, yanki=0.48, eq=[("hp", 250), ("tepe", 3500, -2, 1.2)],
           ifade=[(0, 70), (6, 96), (11, 84), (24, 92), (33, 108), (40, 100), (46, 84), (48, 70)])
    son = ezgi(vl, "r:3 B4:2 E5:1 | G5:5 F#5:1 | E5:3 D5:3 | C#5:5 B4:1 | C5:3 E5:2 G5:1 | A5:4 G5:1 F5:1 | "
                   "F#5:3 B5:2 A5:1 | G5:4 F#5:2", hiz=72)
    assert abs(son - 48) < 1e-9, son
    trem = P("tremolo", TREMOLO, db=-8, yanki=0.42, eq=[("hp", 90), ("lp", 6000)],
             ifade=[(0, 30), (5, 70), (12, 40), (22, 76), (24, 44), (34, 90), (41, 96), (42, 46), (48, 30)])
    tut(trem, [(0, 24, ["E3", "B3"]), (24, 6, ["C3", "G3"]), (30, 6, ["F3", "C4"]), (36, 6, ["B2", "F#3"]),
               (42, 6, ["E3", "B3"])], hiz=64, kisalt=0.05)
    dav = P("konser davulu", 116, banka=8, db=-7, yanki=0.35, eq=[("lp", 3000)])
    dav.ekle(0, 3, "E2", 76)
    dav.ekle(24, 3, "C2", 64)
    tim = P("timpani", TIMPANI, db=-6, yanki=0.35)
    timpani_tremolo(tim, "B2", 36, 6, 20, 70, adim=0.5)
    can = P("çan", CAN, db=-9, pan=-0.35, yanki=0.6, eq=[("hp", 300)])
    can.ekle(0, 6, "E5", 46)
    can.ekle(24, 6, "C5", 40)
    b = Beste("gizem_b", "gizem", "Dehliz", "6/8", 48, [pi, vl, trem, dav, tim, can], akorlar,
              "Mi minör; piyano arpeji ve inen iç ses, yalnız keman, Fa (♭II) ve Si7", yanki_rt60=2.4,
              yanki_on=0.03)
    return _kontrol(b, pi, vl, trem, dav, tim, can)


# ===================================================================================================== MERAK
def merak_a() -> Beste:
    """Keşif: Sol majör, 4/4, 120 bpm. Marimba ezgisi + glockenspiel pırıltısı, zıplayan pizzicato (bas vuruşta,
    akor vuruş arasında), Lidya II (La/Sol) "vay" rengi, hafif shaker. İç çekiş: ön çekiş Re-Do | Si."""
    akorlar = [(0, 2, "D7"), (2, 4, "G"), (6, 4, "A/G"), (10, 4, "Em7"), (14, 4, "Cadd9"), (18, 4, "G/B"),
               (22, 2, "Am7"), (24, 2, "D7"), (26, 1, "G"), (27, 1, "D/F#")]
    mel = "D5:1 C5:1 | B4:1.5 D5:0.5 G5:1 F#5:0.5 E5:0.5 | C#5:1 E5:1 A5:1.5 G5:0.5 | F#5:1 E5:1 D5:1 B4:1 | " \
          "C5:0.5 D5:0.5 E5:0.5 G5:0.5 D5:2 | B4:0.5 D5:0.5 G5:0.5 B5:0.5 A5:1 G5:1 | E5:1 C5:1 F#5:1 A5:1 | G5:2"
    mar = P("marimba", MARIMBA, db=0, pan=-0.1, yanki=0.25, eq=[("hp", 150)])
    son = ezgi(mar, mel, hiz=84)
    assert abs(son - 28) < 1e-9, son
    gl = P("glockenspiel", GLOCK, db=-1, pan=0.25, yanki=0.35, eq=[("hp", 800)])
    ezgi(gl, " ".join(t if t == "|" else _oktav(t, 1) for t in mel.split()), hiz=56)
    pz = P("pizz akor", PIZZ, db=-2.5, pan=0.18, yanki=0.25, eq=[("hp", 160)])
    akor_deseni(pz, [(0, 2, ["F#3", "A3", "C4"]), (2, 4, ["G3", "B3", "D4"]), (6, 4, ["A3", "C#4", "E4"]),
                     (10, 4, ["G3", "B3", "E4"]), (14, 4, ["G3", "C4", "D4", "E4"]), (18, 4, ["G3", "B3", "D4"]),
                     (22, 2, ["A3", "C4", "E4"]), (24, 2, ["F#3", "A3", "C4"]), (26, 1, ["G3", "B3", "D4"]),
                     (27, 1, ["F#3", "A3", "D4"])],
                [None, [0, 1, 2]], 0.5, hizlar=(0, 58), kesik=0.55)
    bs = P("pizz bas", PIZZ, db=-2, yanki=0.12, eq=[("hp", 35)])
    bas_cizgisi(bs, "D2:1 F#2:1 | G2:1 D2:1 G2:1 D2:1 | G2:1 E2:1 G2:1 A2:1 | E2:1 B1:1 E2:1 D2:1 | "
                    "C2:1 G2:1 C2:1 G2:1 | B1:1 D2:1 G2:1 B2:1 | A1:1 E2:1 D2:1 F#2:1 | G2:1 F#2:1", hiz=80, oktav=True)
    pad = P("yaylı", YAYLI_YAVAS, db=-9, yanki=0.4, eq=[("hp", 200), ("lp", 7000)], ifade=[(0, 70), (28, 70)])
    tut(pad, [(0, 2, ["A3", "C4", "F#4"]), (2, 4, ["B3", "D4", "G4"]), (6, 4, ["C#4", "E4", "A4"]),
              (10, 4, ["B3", "E4", "G4"]), (14, 4, ["C4", "E4", "G4"]), (18, 4, ["B3", "D4", "G4"]),
              (22, 2, ["C4", "E4", "A4"]), (24, 2, ["C4", "F#4", "A4"]), (26, 2, ["B3", "D4", "G4"])], hiz=60,
        kisalt=0.03)
    pe = P("shaker", 48, davul=True, db=-5, pan=0.4, yanki=0.15)
    for i in range(56):
        pe.ekle(i * 0.5, 0.25, 82, 44 if i % 2 else 30)
    pe.ekle(2, 1, 81, 40)    # açık üçgen
    pe.ekle(18, 1, 81, 34)
    b = Beste("merak_a", "merak", "Keşif", "4/4", 28, [mar, gl, pz, bs, pad, pe], akorlar,
              "Sol majör; marimba + glockenspiel, zıplayan pizzicato, Lidya La/Sol", yanki_rt60=1.4)
    return _kontrol(b, mar, gl, pz, bs, pad, pe)


def _oktav(tok: str, n: int) -> str:
    ad, _, gerisi = tok.partition(":")
    if ad == "r":
        return tok
    import re
    r = re.fullmatch(r"([A-G][#b]*)(-?\d)", ad)
    return f"{r.group(1)}{int(r.group(2)) + n}:{gerisi}"


def merak_b() -> Beste:
    """Buluş: Re majör, 6/8 (noktalı dörtlük 86), 10 ölçü. Flüt ezgisi sıçrayarak yükselir ("buldum!"), arp 6/8
    arpejleri, klarnet kılavuz sesler, pizzicato bas, glockenspiel parıltıları, hafif tef. Mi7 (V/V) aydınlığı.
    İç çekiş: ön çekiş La-Sol | Fa#."""
    akorlar = [(0, 3, "A7"), (3, 6, "D"), (9, 6, "Gmaj7"), (15, 6, "D/F#"), (21, 6, "Em7"), (27, 6, "D"),
               (33, 6, "Bm"), (39, 6, "G"), (45, 6, "E7"), (51, 6, "A7"), (57, 3, "D")]
    fl = P("flüt", FLUT, db=0, pan=0.1, yanki=0.3, eq=[("hp", 250)], ifade=[(0, 96), (27, 108), (45, 112), (57, 96)])
    son = ezgi(fl, "r:1 A5:1 G5:1 | F#5:2 E5:1 D5:2 F#5:1 | B5:2 A5:1 G5:2 F#5:1 | A5:3 F#5:2 D5:1 | "
                   "E5:2 F#5:1 G5:2 B5:1 | A5:2 F#5:1 D6:2 A5:1 | B5:2 A5:1 F#5:2 D5:1 | G5:2 B5:1 D6:2 B5:1 | "
                   "G#5:2 B5:1 E6:2 D6:1 | E5:2 F#5:1 G5:2 C#5:1 | D5:3", hiz=76)
    assert abs(son - 60) < 1e-9, son
    kl = P("klarnet", KLARNET, db=-2, pan=-0.2, yanki=0.3, eq=[("hp", 140)])
    ezgi(kl, "G4:3 | F#4:6 | F#4:6 | A4:6 | G4:6 | F#4:6 | F#4:3 B4:3 | B4:6 | G#4:6 | A4:3 G4:3 | F#4:3", hiz=58)
    ar = P("arp", ARP, db=-1, pan=-0.25, yanki=0.38, eq=[("hp", 80)])
    kok = [(0, 3, "A2", "7"), (3, 6, "D3", ""), (9, 6, "G2", "maj7"), (15, 6, "F#2", "D/F#"), (21, 6, "E2", "m7"),
           (27, 6, "D3", ""), (33, 6, "B2", "m"), (39, 6, "G2", ""), (45, 6, "E2", "7"), (51, 6, "A2", "7"),
           (57, 3, "D3", "")]
    for bas, sure, r, tur in kok:
        notalar = _arp_notalari(r, tur)
        for i in range(int(sure)):
            ar.ekle(bas + i, 1.6, notalar[i % len(notalar)], 62 if i % 3 == 0 else 50)
    bs = P("pizz bas", PIZZ, db=0, yanki=0.15, eq=[("hp", 35)])
    bas_cizgisi(bs, "A1:3 | D2:3 A1:3 | G1:3 D2:3 | F#1:3 A1:3 | E2:3 B1:3 | D2:3 A1:3 | B1:3 F#2:3 | G1:3 D2:3 | "
                    "E2:3 B1:3 | A1:3 E2:3 | D2:3", hiz=76, oktav=True)
    gl = P("glockenspiel", GLOCK, db=2, pan=0.3, yanki=0.42, eq=[("hp", 900)])
    for t, n in [(27, "D6"), (30, "A6"), (45, "E6"), (48, "B6"), (57, "D6")]:
        gl.ekle(t, 1.5, n, 58)
    tef = P("tef", 48, davul=True, db=-4, pan=0.45, yanki=0.15)
    for t in range(3, 57, 3):
        tef.ekle(t, 0.5, 54, 40 if (t - 3) % 6 == 0 else 28)
    b = Beste("merak_b", "merak", "Buluş", "6/8", 60, [fl, kl, ar, bs, gl, tef], akorlar,
              "Re majör; flüt, arp, klarnet, pizzicato, glockenspiel; Mi7 aydınlığı", yanki_rt60=1.5)
    return _kontrol(b, fl, kl, ar, bs, gl, tef)


def _arp_notalari(kok: str, tur: str) -> list[int]:
    r = m(kok)
    if tur == "D/F#":           # Re/Fa#: Fa# - La - Re - Fa# - La - Re
        return [r, r + 3, r + 8, r + 12, r + 15, r + 8]
    aralik = {"": (0, 7, 12, 16, 19, 12), "m": (0, 7, 12, 15, 19, 12), "7": (0, 7, 10, 16, 19, 10),
              "maj7": (0, 7, 11, 16, 19, 11), "m7": (0, 7, 10, 15, 19, 10)}[tur]
    return [r + a for a in aralik]


# ===================================================================================================== İRONİK
def ironik_a() -> Beste:
    """Sinsi: Re minör, 4/4, 120 bpm, parmak ucu. Kesik fagot ezgisi (kromatik iniş, telaşlı merdiven), her vuruşta
    pizzicato bas, vuruş aralarında kuru akorlar, hafif tahta blok; sonda Si♭7 -> La7 yan basamağı ve bir glockenspiel
    "göz kırpması". İç çekiş: fagot ön çekişi La | Sol kesik, ardından Fa."""
    akorlar = [(0, 2, "A7"), (2, 4, "Dm"), (6, 4, "Dm"), (10, 4, "Gm6"), (14, 4, "A7"), (18, 4, "Dm"), (22, 2, "Bb7"),
               (24, 2, "A7"), (26, 2, "Dm")]
    fg = P("fagot", FAGOT, db=0, pan=-0.12, yanki=0.2, eq=[("hp", 70), ("tepe", 1800, 2, 1.0)])
    son = ezgi(fg, "A3:0.5. r:0.5 G3:0.5. r:0.5 | F3:0.5. r:0.5 A3:0.5. D4:0.5. C#4:0.5 D4:0.5. r:1 | "
                   "F4:0.5. E4:0.5. Eb4:0.5. D4:0.5. A3:1. r:1 | G3:0.5. Bb3:0.5. E4:1 D4:0.5. Bb3:0.5. G3:1. | "
                   "A3:0.5. C#4:0.5. E4:0.5. G4:0.5. F4:0.5. E4:0.5. D4:0.5. C#4:0.5. | "
                   "D4:1. r:0.5 A3:0.5. D4:0.5. F4:0.5. A4:1 | Ab4:0.5. F4:0.5. D4:0.5. Bb3:0.5. C#4:0.5. E4:0.5. G4:1_ | "
                   "F4:0.5. r:0.5 D4:0.5. r:0.5", hiz=82)
    assert abs(son - 28) < 1e-9, son
    bs = P("pizz bas", PIZZ, db=-2, yanki=0.12, eq=[("hp", 35)])
    bas_cizgisi(bs, "A1:1 C#2:1 | D2:1 A1:1 D2:1 A1:1 | D2:1 A1:1 D2:1 C#2:1 | G1:1 D2:1 G1:1 D2:1 | "
                    "A1:1 E2:1 A1:1 C#2:1 | D2:1 A1:1 D2:1 F2:1 | Bb1:1 F2:1 A1:1 E2:1 | D2:1 A1:1", hiz=80, oktav=True)
    pz = P("pizz akor", PIZZ, db=-2, pan=0.22, yanki=0.18, eq=[("hp", 180)])
    akor_deseni(pz, [(0, 2, ["G3", "C#4", "E4"]), (2, 8, ["F3", "A3", "D4"]), (10, 4, ["G3", "Bb3", "E4"]),
                     (14, 4, ["G3", "C#4", "E4"]), (18, 4, ["F3", "A3", "D4"]), (22, 2, ["Ab3", "D4", "F4"]),
                     (24, 2, ["G3", "C#4", "E4"]), (26, 2, ["F3", "A3", "D4"])],
                [None, [0, 1, 2]], 0.5, hizlar=(0, 56), kesik=0.5)
    gl = P("glockenspiel", GLOCK, db=1, pan=0.3, yanki=0.35, eq=[("hp", 900)])
    gl.ekle(9.5, 0.5, "A6", 50)
    gl.ekle(27.5, 0.5, "D7", 54)
    tb = P("tahta blok", 48, davul=True, db=-3, pan=0.35, yanki=0.12)
    for t in range(1, 28, 2):
        tb.ekle(t, 0.25, 76, 34)
    b = Beste("ironik_a", "ironik", "Sinsi", "4/4", 28, [fg, bs, pz, gl, tb], akorlar,
              "Re minör; kesik fagot, parmak ucu pizzicato, Si♭7-La7 yan basamağı", yanki_rt60=1.2)
    return _kontrol(b, fg, bs, pz, gl, tb)


def ironik_b() -> Beste:
    """Ters Köşe: Fa majör, 3/4, 154 bpm (imza valsinin temposu; onun alaycı kuzeni). Klarnet ezgisi, tuba "um",
    pizzicato "pa-pa", Fa7'nin mi♭ "mavi" notası ve Si♭m6 (minör iv) iç çekişi; sonda glockenspiel motifi yankılar.
    İç çekiş: ön çekiş Do-Si♭ | La."""
    akorlar = [(0, 2, "C7"), (2, 3, "F"), (5, 3, "F/A"), (8, 3, "Gm7"), (11, 3, "C7"), (14, 3, "C7"), (17, 3, "F"),
               (20, 3, "F7"), (23, 3, "Bb"), (26, 3, "Bbm6"), (29, 3, "C7"), (32, 3, "F"), (35, 1, "F")]
    kl = P("klarnet", KLARNET, db=0, pan=-0.1, yanki=0.25, eq=[("hp", 150)],
           ifade=[(0, 100), (20, 112), (26, 96), (36, 100)])
    son = ezgi(kl, "C5:1 Bb4:1 | A4:2 C5:1 | F5:2 E5:1 | D5:1 E5:1 F5:1 | G5:2 E5:1 | Bb4:1 A4:1 G4:1 | "
                   "A4:1 C5:1 F5:1 | Eb5:2 D5:1 | D5:2 Bb4:1 | Db5:2 C5:1 | Bb4:1 G4:1 E4:1 | F4:2 r:1 | r:1", hiz=78)
    assert abs(son - 36) < 1e-9, son
    tb = P("tuba", TUBA, db=-6, yanki=0.14, eq=[("hp", 30), ("lp", 4000)])
    for t, n in [(2, "F2"), (5, "A2"), (8, "G2"), (11, "C2"), (14, "G2"), (17, "F2"), (20, "A2"), (23, "Bb1"),
                 (26, "Db2"), (29, "C2"), (32, "F2"), (35, "F2")]:
        tb.ekle(t, 0.8, n, 80)
    pz = P("pizz", PIZZ, db=-1, pan=0.2, yanki=0.2, eq=[("hp", 170)])
    yer = [(0, 2, ["G3", "Bb3", "E4"]), (2, 6, ["A3", "C4", "F4"]), (8, 3, ["G3", "Bb3", "D4"]),
           (11, 6, ["G3", "Bb3", "E4"]), (17, 3, ["A3", "C4", "F4"]), (20, 3, ["A3", "C4", "Eb4"]),
           (23, 3, ["Bb3", "D4", "F4"]), (26, 3, ["Db4", "F4", "G4"]), (29, 3, ["G3", "Bb3", "E4"]),
           (32, 3, ["A3", "C4", "F4"])]
    for bas, sure, notalar in yer:
        for v in range(int(sure)):
            t = bas + v
            if bas == 0 or (t - 2) % 3 != 0:          # ön çekiş: iki pa; ölçü içinde 2. ve 3. vuruşlar
                for x in notalar:
                    pz.ekle(t, 0.45, x, 60)
    gl = P("glockenspiel", GLOCK, db=0, pan=0.3, yanki=0.38, eq=[("hp", 900)])
    ezgi(gl, "C7:1 Bb6:1 A6:1.5.", bas=30, hiz=50)
    b = Beste("ironik_b", "ironik", "Ters Köşe", "3/4", 36, [kl, tb, pz, gl], akorlar,
              "Fa majör vals; klarnet, tuba, pizzicato; Fa7 ve Si♭m6", yanki_rt60=1.3)
    return _kontrol(b, kl, tb, pz, gl)


# ===================================================================================================== DESTANSI
def destansi_a() -> Beste:
    """Zafer: Re minör, 4/4, 137 bpm (yarım tempo hissi). i-VI-III-VII; alçak yaylılarda 3+3+2 vurgulu sekizlik
    ostinato, kornolar kahraman ezgi (ikinci yarıda trompetler oktav üstte), bakır vurgular, timpani ve konser davulu,
    sonda La majör (Pikardi dominant) -> Re. Ezginin doruğu Do# - Re."""
    akorlar = [(0, 2, "A"), (2, 4, "Dm"), (6, 4, "Bb"), (10, 4, "F"), (14, 4, "C"), (18, 4, "Dm"), (22, 4, "Bb"),
               (26, 2, "C"), (28, 2, "A"), (30, 2, "Dm")]
    ko = P("korno", KORNO, db=0, pan=-0.15, yanki=0.45, eq=[("hp", 90), ("tepe", 2500, 1.5, 1)],
           ifade=[(0, 92), (18, 100), (28, 120), (32, 116)])
    mel = "A3:1 C#4:1 | D4:3 A3:1 | D4:1.5 E4:0.5 F4:2 | C5:3 A4:1 | G4:2 E4:1 C4:1 | D4:2 F4:1 A4:1 | " \
          "Bb4:2 A4:1 G4:1 | G4:1 A4:1 C#5:2 | D5:2"
    son = ezgi(ko, mel, hiz=84)
    assert abs(son - 32) < 1e-9, son
    ezgi(ko, " ".join(_oktav(t, -1) if t != "|" else t for t in mel.split()), hiz=70)   # oktav altı: kalın kornolar
    tr = P("trompet", TROMPET, db=-6, pan=0.2, yanki=0.45, eq=[("hp", 200), ("lp", 9000)])
    ezgi(tr, "D5:2 F5:1 A5:1 | Bb5:2 A5:1 G5:1 | G5:1 A5:1 C#6:2 | D6:2", bas=18, hiz=74)
    yo = P("yaylı ostinato", YAYLI_HIZLI, db=1, yanki=0.3, eq=[("hp", 45), ("tepe", 250, -2, 1)])
    kokler = [(0, 2, "A2"), (2, 4, "D2"), (6, 4, "Bb1"), (10, 4, "F2"), (14, 4, "C2"), (18, 4, "D2"), (22, 4, "Bb1"),
              (26, 2, "C2"), (28, 2, "A1"), (30, 2, "D2")]
    k = 0
    for bas, sure, r in kokler:
        t = bas
        while t < bas + sure - 1e-9:
            vurgu = k % 8 in (0, 3, 6)
            yo.ekle(t, 0.42, m(r) + 12, 104 if vurgu else 66)
            yo.ekle(t, 0.42, m(r), 96 if vurgu else 58)
            k += 1
            t += 0.5
    pad = P("yaylı", YAYLI_YAVAS, db=-6, yanki=0.5, eq=[("hp", 200)],
            ifade=[(0, 70), (18, 80), (28, 118), (32, 110)])
    tut(pad, [(0, 2, ["A4", "C#5", "E5"]), (2, 4, ["A4", "D5", "F5"]), (6, 4, ["Bb4", "D5", "F5"]),
              (10, 4, ["A4", "C5", "F5"]), (14, 4, ["G4", "C5", "E5"]), (18, 4, ["A4", "D5", "F5"]),
              (22, 4, ["Bb4", "D5", "F5"]), (26, 2, ["G4", "C5", "E5"]), (28, 2, ["A4", "C#5", "E5"]),
              (30, 2, ["A4", "D5", "F5"])], hiz=74, kisalt=0.03)
    ba = P("bakır", BAKIR, db=-7, pan=0.05, yanki=0.42, eq=[("hp", 120)])
    for t, notalar, s in [(2, ["D3", "A3", "D4", "F4"], 1.2), (10, ["F3", "C4", "F4", "A4"], 1.2),
                          (18, ["D3", "A3", "D4", "F4"], 1.2), (22, ["Bb2", "F3", "Bb3", "D4"], 1.2),
                          (26, ["C3", "G3", "C4", "E4"], 1.6), (28, ["A2", "E3", "A3", "C#4"], 1.8),
                          (30, ["D3", "A3", "D4", "F4"], 1.6)]:
        for x in notalar:
            ba.ekle(t, s, x, 84)
    ti = P("timpani", TIMPANI, db=-3, yanki=0.35)
    timpani_tremolo(ti, "A2", 0, 2, 26, 78)
    for t, n, v in [(2, "D2", 96), (6, "Bb2", 70), (10, "F2", 84), (14, "C3", 74), (18, "D2", 100), (22, "Bb2", 80)]:
        ti.ekle(t, 1, n, v)
    timpani_tremolo(ti, "A2", 26, 4, 40, 104)
    ti.ekle(30, 1.5, "D2", 108)
    bd = P("konser davulu", 116, banka=8, db=-1, yanki=0.3, eq=[("lp", 2500)])
    for t in (2, 18, 30):
        bd.ekle(t, 2, "C2", 92)
    ta = P("taiko", TAIKO, db=-4, yanki=0.3, eq=[("lp", 3000)])
    for bar in (18, 22, 26):
        for o, v in ((0, 92), (1.5, 70), (2, 88)):
            ta.ekle(bar + o, 0.5, "C3", v)
    cy = P("zil", 48, davul=True, db=-8, pan=0.3, yanki=0.4)
    cy.ekle(18, 2, 49, 80)
    b = Beste("destansi_a", "destansi", "Zafer", "4/4", 32, [ko, tr, yo, pad, ba, ti, bd, ta, cy], akorlar,
              "Re minör; i-VI-III-VII, 3+3+2 ostinato, korno + trompet, timpani", yanki_rt60=2.2)
    return _kontrol(b, ko, tr, yo, pad, ba, ti, bd, ta, cy)


def destansi_b() -> Beste:
    """Onur: Sol minör, 4/4, 69 bpm. Ağır, onurlu: yalnız korno, yaylılar, alçak yaylı kökler, uzak trampet trileri,
    timpani. Ezgide imza iç çekişi Re-Do | Si♭ ikinci ölçüde. Çanakkale gibi fedakârlık hikâyeleri için."""
    akorlar = [(0, 1, "D"), (1, 2, "Gm"), (3, 2, "Eb"), (5, 2, "Bb"), (7, 2, "F"), (9, 2, "Gm"), (11, 1, "Cm"),
               (12, 1, "D"), (13, 3, "Gm")]
    ko = P("korno", KORNO, db=0, pan=-0.1, yanki=0.52, eq=[("hp", 90)], ifade=[(0, 86), (5, 104), (9, 110), (16, 92)])
    son = ezgi(ko, "D4:1 | G4:1.5 A4:0.5 Bb4:1 G4:1 | D5:2 C5:1 Bb4:1 | Bb4:1 A4:1 G4:1 F#4:1 | G4:3", hiz=80)
    assert abs(son - 16) < 1e-9, son
    yy = P("yaylı", YAYLI_YAVAS, db=-3, yanki=0.52, eq=[("hp", 110)],
           ifade=[(0, 70), (5, 92), (9, 108), (13, 96), (16, 80)])
    tut(yy, [(0, 1, ["F#3", "A3", "D4"]), (1, 2, ["G3", "Bb3", "D4"]), (3, 2, ["G3", "Bb3", "Eb4"]),
             (5, 2, ["F3", "Bb3", "D4"]), (7, 2, ["F3", "A3", "C4"]), (9, 2, ["G3", "Bb3", "D4"]),
             (11, 1, ["G3", "C4", "Eb4"]), (12, 1, ["F#3", "A3", "D4"]), (13, 3, ["G3", "Bb3", "D4"])], hiz=72,
        kisalt=0.02)
    kb = P("alçak yaylılar", KONTRBAS, db=-6, yanki=0.4, eq=[("hp", 35)])
    for t, s, n in [(0, 1, "D2"), (1, 2, "G1"), (3, 2, "Eb2"), (5, 2, "Bb1"), (7, 2, "F2"), (9, 2, "G1"),
                    (11, 1, "C2"), (12, 1, "D2"), (13, 3, "G1")]:
        kb.ekle(t, s - 0.02, n, 74)
        kb.ekle(t, s - 0.02, m(n) + 12, 60)
    tr = P("trampet", 48, davul=True, db=-6, pan=0.12, yanki=0.3)
    for bas, sure in ((0, 1), (4, 1), (8, 1), (12, 1)):
        n = int(sure / 0.125)
        for i in range(n):
            tr.ekle(bas + i * 0.125, 0.1, 38, int(18 + 34 * i / n))
    ti = P("timpani", TIMPANI, db=-4, yanki=0.4)
    for t, n, v in [(1, "G2", 70), (5, "Bb2", 60), (9, "G2", 74), (13, "G2", 66)]:
        ti.ekle(t, 1, n, v)
    timpani_tremolo(ti, "D2", 12, 1, 30, 70, adim=0.125)
    ba = P("bakır", BAKIR, db=-8, yanki=0.5, eq=[("hp", 120)], ifade=[(5, 40), (9, 96), (13, 80)])
    tut(ba, [(5, 2, ["D3", "F3", "Bb3"]), (7, 2, ["C3", "F3", "A3"]), (9, 2, ["D3", "G3", "Bb3"]),
             (11, 1, ["Eb3", "G3", "C4"]), (12, 1, ["D3", "F#3", "A3"]), (13, 3, ["D3", "G3", "Bb3"])], hiz=66,
        kisalt=0.03)
    b = Beste("destansi_b", "destansi", "Onur", "4/4", 16, [ko, yy, kb, tr, ti, ba], akorlar,
              "Sol minör; yalnız korno, yaylılar, uzak trampet; onurlu, ağır", yanki_rt60=2.5, yanki_on=0.03)
    return _kontrol(b, ko, yy, kb, tr, ti, ba)


# ===================================================================================================== MASAL
def masal_a() -> Beste:
    """Kule: Mi minör (Dor renkli La/Mi), 3/4, 116 bpm, ninni-vals. Flüt ezgisi (çelesta aynı sesle ışıltı katar),
    arp vals arpejleri, yumuşak yaylı yatak. İç çekiş: ön çekiş Si-La | Sol."""
    akorlar = [(0, 2, "B7"), (2, 3, "Em"), (5, 3, "A/E"), (8, 3, "Em"), (11, 3, "D"), (14, 3, "Cmaj7"), (17, 3, "Am6"),
               (20, 3, "B7sus4"), (23, 3, "B7"), (26, 1, "Em")]
    mel = "B5:1 A5:1 | G5:2 E5:1 | E5:1 F#5:1 A5:1 | B5:2 A5:1 | F#5:2 D5:1 | E5:1 G5:1 B5:1 | C6:2 B5:1 | " \
          "A5:1 F#5:1 E5:1 | D#5:2 F#5:1 | E5:1"
    fl = P("flüt", FLUT, db=0, yanki=0.42, eq=[("hp", 250)], ifade=[(0, 94), (14, 110), (20, 104), (27, 92)])
    son = ezgi(fl, mel, hiz=74)
    assert abs(son - 27) < 1e-9, son
    ce = P("çelesta", CELESTA, db=-2, pan=0.3, yanki=0.5, eq=[("hp", 400)])
    ezgi(ce, mel, hiz=58)
    ar = P("arp", ARP, db=-2, pan=-0.2, yanki=0.42, eq=[("hp", 70)])
    for bas, sure, notalar in [(0, 2, ["B2", "F#3", "A3", "D#4"]), (2, 3, ["E2", "B2", "E3", "G3"]),
                               (5, 3, ["E2", "A2", "C#3", "E3"]), (8, 3, ["E2", "B2", "E3", "G3"]),
                               (11, 3, ["D2", "A2", "D3", "F#3"]), (14, 3, ["C2", "G2", "B2", "E3"]),
                               (17, 3, ["A1", "E2", "C3", "F#3"]), (20, 3, ["B1", "F#2", "A2", "E3"]),
                               (23, 3, ["B1", "F#2", "A2", "D#3"]), (26, 1, ["E2", "B2", "E3", "G3"])]:
        # ilk vuruş kök, sonra sekizliklerle yukarı-aşağı: 1 . 2 3 4 3 (3/4'te 6 sekizlik)
        sira = [0, 1, 2, 3, 2, 1]
        for i in range(int(sure * 2)):
            ar.ekle(bas + i * 0.5, 1.8 if i == 0 else 1.0, notalar[sira[i % 6]], 66 if i == 0 else 50)
    pad = P("yaylı", YAYLI_YAVAS, db=-6, yanki=0.5, eq=[("hp", 180), ("lp", 7000)], ifade=[(0, 70), (14, 86), (27, 70)])
    tut(pad, [(0, 2, ["A3", "D#4", "F#4"]), (2, 3, ["B3", "E4", "G4"]), (5, 3, ["C#4", "E4", "A4"]),
              (8, 3, ["B3", "E4", "G4"]), (11, 3, ["A3", "D4", "F#4"]), (14, 3, ["B3", "E4", "G4"]),
              (17, 3, ["C4", "E4", "F#4"]), (20, 3, ["A3", "E4", "F#4"]), (23, 3, ["A3", "D#4", "F#4"]),
              (26, 1, ["B3", "E4", "G4"])], hiz=60, kisalt=0.03)
    b = Beste("masal_a", "masal", "Kule", "3/4", 27, [fl, ce, ar, pad], akorlar,
              "Mi minör ninni-vals; flüt + çelesta, arp, yaylı yatak", yanki_rt60=2.1)
    return _kontrol(b, fl, ce, ar, pad)


def masal_b() -> Beste:
    """Rüya: Fa Lidya, 6/8 (noktalı dörtlük 69). Çelesta ezgisi (glockenspiel motifte parlar), akan arp, çok yumuşak
    "uu" korosu ve viyolonsel kökler. İç çekiş Lidya renkli: Do-Si | La (Si natürel)."""
    akorlar = [(0, 6, "Fmaj7"), (6, 6, "G/F"), (12, 6, "Am7"), (18, 6, "Bbmaj7"), (24, 6, "F/A"), (30, 6, "G/B"),
               (36, 6, "Bbmaj7"), (42, 6, "C7sus4")]
    mel = "C6:2 B5:1 A5:3 | B5:2 A5:1 G5:3 | E5:2 G5:1 C6:3 | D6:2 C6:1 A5:3 | C6:2 B5:1 A5:2 G5:1 | B5:3 D6:3 | " \
          "A5:2 F5:1 D5:3 | G5:3 F5:2 E5:1"
    ce = P("çelesta", CELESTA, db=0, pan=0.1, yanki=0.55, eq=[("hp", 300)])
    son = ezgi(ce, mel, hiz=76)
    assert abs(son - 48) < 1e-9, son
    gl = P("glockenspiel", GLOCK, db=-8, pan=0.3, yanki=0.6, eq=[("hp", 900)])
    ezgi(gl, "C7:2 B6:1 A6:3", bas=0, hiz=50)
    ezgi(gl, "C7:2 B6:1 A6:2", bas=24, hiz=46)
    ar = P("arp", ARP, db=-4, pan=-0.25, yanki=0.5, eq=[("hp", 70)])
    for bas, notalar in [(0, ["F2", "C3", "E3", "A3"]), (6, ["F2", "D3", "G3", "B3"]), (12, ["A2", "E3", "G3", "C4"]),
                         (18, ["Bb2", "F3", "A3", "D4"]), (24, ["A2", "F3", "A3", "C4"]), (30, ["B2", "D3", "G3", "B3"]),
                         (36, ["Bb2", "F3", "A3", "D4"]), (42, ["C3", "F3", "G3", "Bb3"])]:
        sira = [0, 1, 2, 3, 2, 1]
        for i in range(6):
            ar.ekle(bas + i, 2.2, notalar[sira[i]], 58 if i == 0 else 44)
    ko = P("koro uu", KORO_UU, db=-9, yanki=0.65, eq=[("hp", 220), ("lp", 6000)],
           ifade=[(0, 40), (12, 80), (24, 70), (36, 86), (48, 50)])
    tut(ko, [(0, 6, ["A3", "C4", "E4"]), (6, 6, ["B3", "D4", "G4"]), (12, 6, ["A3", "C4", "E4"]),
             (18, 6, ["A3", "D4", "F4"]), (24, 6, ["A3", "C4", "F4"]), (30, 6, ["B3", "D4", "G4"]),
             (36, 6, ["A3", "D4", "F4"]), (42, 6, ["Bb3", "F4", "G4"])], hiz=58, kisalt=0.05)
    ve = P("viyolonsel", CELLO, db=-11, yanki=0.45, eq=[("hp", 40)], ifade=[(0, 80), (48, 80)])
    for t, n in [(0, "F2"), (6, "F2"), (12, "A2"), (18, "Bb2"), (24, "A2"), (30, "B2"), (36, "Bb2"), (42, "C3")]:
        ve.ekle(t, 5.9, n, 62)
    b = Beste("masal_b", "masal", "Rüya", "6/8", 48, [ce, gl, ar, ko, ve], akorlar,
              "Fa Lidya; çelesta + glockenspiel, arp, uu korosu", yanki_rt60=2.6, yanki_on=0.03)
    return _kontrol(b, ce, gl, ar, ko, ve)


BESTELER = {f.__name__: f for f in (gizem_a, gizem_b, merak_a, merak_b, ironik_a, ironik_b, destansi_a, destansi_b,
                                    masal_a, masal_b)}
