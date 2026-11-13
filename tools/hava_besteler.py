#!/usr/bin/env python3
"""Hava müzikleri v2 (13.11.2026): eski klasik sesin iskeleti üzerine beş kardeş vals. Ev sesi motoru için melodi-JSON.

Neden v2: ilk 10 parça (temiz "orkestra" MIDI'si, döngü) hesap sahibinden "oyun arka plan müziği gibi, wojak
videolarına uymaz" yanıtını aldı; ölçü eski klasik ses oldu. Klasik ses ölçüldü (arastirma/hava_muzik/NOTLAR.md):
3/4, 152 BPM, iki vuruşluk "pa pa" ile başlar; tek bir iki ölçülük akor sarkacı baştan sona sürer; ilk 4 ölçü yalnız
kamışlı um-pa-pa (yorumlardaki "u a a"); ezgi 4. ölçüde girer, iki ölçülük hücre yinelenir; 7. ölçüde "çığlık"
(videoda ters köşe sahnesi, ~8-9 sn); son nota kesmeye kadar tutulur (kanıt görselleri, 11,4 sn'den sonra).

Beş parça bu iskelette ve Gölge'yi yapan motorla (tools/ev_sesi/render.py) kurulur; hava şunlarla değişir: ton ve
makam, sarkacın iki akoru, hücrenin ritmi ve yönü, çığlığın türü, bitiş, çalgı rengi ve GİRİŞİN dokusu (eşlik).
Kullanılmayanlar: klasik sesin hücresi (inen üçlemeler, Fa Fa Re), çığlığı (La♭5 iki vuruş -> Sol5), i <-> vii°6
sarkacı; Gölge'nin hücresi. İki bağımsız hakemin (besteci, izleyici) düzeltmeleri işlendi.

    python tools/hava_muzik.py --hepsi        # JSON -> ev sesi -> assets/music/hava/<ad>.m4a
"""
from __future__ import annotations

R1 = [{"prog": 22}, {"prog": 22, "gain_db": -3, "detune": 20}]                 # tremolo armonika (parlak)
R3 = [{"prog": 71}, {"prog": 71, "detune": 20}]                                # klarnet-müzet (koyu, odunsu)
KUTU_REED = [{"prog": 10, "kind": "struck", "ring_s": 1.2, "oct": 1, "gain_db": -2}, {"prog": 23, "gain_db": -3},
             {"prog": 22, "gain_db": -7, "detune": 14}]                        # müzik kutusu + hafif kamış
ST = {"art": "stacc"}
# Eşliğin "u a a" parlaklık karşıtlığı parçaya göre ayarlanır: hedef klasik sesin ölçüsü (karşıtlık 3,76 dB).
ESLIK = {
    "B": {"oom_bright_db": -3, "pah_bright_db": [2, 3]},
    "CD": {"oom_bright_db": 0, "pah_bright_db": [0.5, 1.5], "pah_low_db": [-2.5, -4.5]},
    "D": {"oom_bright_db": 1, "pah_bright_db": [0, 1], "pah_low_db": [-2, -4]},
}


def N(bar, beat, dur, midi, vel=88, **kw):
    d = {"bar": bar, "beat": beat, "dur_beats": dur, "midi": midi, "vel": vel}
    d.update(kw)
    return d


def CH(bar, midi, bass, beat=1, dur=None, **kw):
    d = {"bar": bar, "beat": beat, "midi": midi, "bass": bass}
    if dur is not None:
        d["dur_beats"] = dur
    d.update(kw)
    return d


def sarkac(a, b, son=11, ozel=None):
    """Ölçü 0 (auftakt: 2. vuruştan) .. son; çift ölçüler a, tekler b. ozel = {ölçü: (midi, bas) ya da akor listesi}."""
    out = []
    for br in range(0, son + 1):
        x = (ozel or {}).get(br, a if br % 2 == 0 else b)
        if isinstance(x, list):
            out += x
            continue
        m, bs = x
        out.append(CH(br, m, bs, beat=2, dur=2) if br == 0 else CH(br, m, bs))
    return out


def parca(ad, baslik, ton, notes, chords, eslik, lead=None, engine=None, accomp=None, perc=None, tempo=152, not_=""):
    e = {"profile": "m3", "accomp": dict(ESLIK[eslik])}
    if lead:
        e["lead"] = {"layers": lead}
    for k, v in (engine or {}).items():
        if k == "accomp":
            e["accomp"].update(v)
        else:
            e[k] = v
    J = {"id": ad, "title": baslik, "key": ton, "meter": "3/4", "tempo_bpm": tempo, "beats_per_bar": 3,
         "pickup_beats": 2, "notes": notes, "chords": chords, "accomp": accomp or {"pattern": "B C C"}, "engine": e,
         "notes_text": " ".join((not_ or "").split())}
    if perc:
        J["perc"] = perc
    return J


def gizem_a():
    """Fısıltı. La minör, 152. Sarkaç i <-> ♭vi (La m <-> Fa m/La♭): bas yarım ses iner; eşlik üç sesli, tepesi La->La♭
    kayar (karanlığı giriş söyler). Hücre: Do-Si-Do yoklaması, sonra dörtlü sıçrayış Fa— ve asılı Re♭. Çığlık: Fa'dan
    La♭'ye ÇIKAN ve asılı kalan soru (klasik sesin inen iç çekişinin tersi). Son: Do— Re ve tutulan Mi5: beşlide açık
    kalır, kesmede Fa m üstünde sürtünür. Klarnet-müzet."""
    ch = sarkac(([60, 64, 69], 57), ([60, 65, 68], 56))
    a = lambda b, v: [N(b, 2, 1, 72, v), N(b, 3, .5, 71, v - 4), N(b, 3.5, .5, 72, v - 2)]
    n = a(4, 84) + [N(5, 1, 2, 77, 88), N(5, 3, 1, 73, 84)] + a(6, 88) \
        + [N(7, 1, 1, 77, 94), N(7, 2, 2, 80, 102)] + a(8, 86) \
        + [N(9, 1, 2, 72, 86), N(9, 3, 1, 74, 88), N(10, 1, 6.5, 76, 86)]
    return parca("gizem_a", "Fısıltı", "A minor", n, ch, "B", lead=R3, engine={"accomp": {"pah_voices": 3}},
                 not_=gizem_a.__doc__)


def merak_a():
    """Acaba. Sol majör, 152. Lidya renkli sarkaç I <-> II (Sol <-> La majör), eşlik üç sesli ve hafif. Hücre: kesik
    Re-Mi ile Sol'e çıkar, sonra soru tonlamasıyla Mi-Do♯-Mi (Lidya dördüncüsü açıkta). "Buldum" anı aynı soru şeklinin
    dörtlü yukarısı: La-Fa♯-La. Son: Do♯-Mi-Fa♯ ile Sol5'e çıkar; son akor Sol majör (cevap). Tremolo armonika."""
    G, A = ([62, 67, 71], 55), ([61, 64, 69], 57)
    ch = sarkac(G, A, ozel={11: ([62, 67, 71], 50)})
    a = lambda b, v: [N(b, 2, .5, 74, v, **ST), N(b, 2.5, .5, 76, v, **ST), N(b, 3, 1, 79, v + 2)]
    q = lambda b, v, x, y: [N(b, 1, 1, x, v), N(b, 2, 1, y, v - 3), N(b, 3, 1, x, v)]
    n = a(4, 84) + q(5, 86, 76, 73) + a(6, 88) + q(7, 100, 81, 78) + a(8, 88) \
        + [N(9, 1, 1, 73, 86), N(9, 2, 1, 76, 88), N(9, 3, 1, 78, 90), N(10, 1, 6.5, 79, 90)]
    return parca("merak_a", "Acaba", "G major (Lydian II)", n, ch, "D", lead=R1, engine={"accomp": {"pah_voices": 3}},
                 not_=merak_a.__doc__)


def ironik_a():
    """Hınzır. Fa majör, 160 (biraz hızlı). Palyaço sarkacı I <-> V7 (Fa <-> Do7/Sol), eşlik kuru ve kesik. Hücre
    topallar: notalar 3. ve 1. vuruşta, 2. vuruş boş (La | Fa · Sol | Mi · La): inen üçlüler ölçü çizgisini aşar.
    Çığlık yerine şaka: beklenen Mi yerine Fa♯ basılır, yukarı kayıp Sol'e oturur. Sonra üçlüler merdivenden yuvarlanır
    (La-Fa, Sol-Mi), uzun bir Do'ya düşer ve kısa bir "tak" (Fa) ile biter."""
    F, C7 = ([60, 65, 69], 53), ([60, 64, 67, 70], 55)
    ch = sarkac(F, C7, son=12)
    ch[12]["pattern"] = "B C. R"
    n = [N(3, 3, 1, 81, 86, **ST), N(4, 1, 1, 77, 84, **ST), N(4, 3, 1, 79, 86, **ST),
         N(5, 1, 1, 76, 84, **ST), N(5, 3, 1, 81, 88, **ST), N(6, 1, 1, 77, 86, **ST), N(6, 3, 1, 79, 88, **ST),
         N(7, 1, 2, 78, 100, art="accent", bend=[[0, 0], [1.2, 0], [1.9, 45]]), N(7, 3, 1, 79, 90),
         N(8, 1, 1, 81, 92, **ST), N(8, 2, 1, 77, 90, **ST), N(9, 1, 1, 79, 90, **ST), N(9, 2, 1, 76, 88, **ST),
         N(10, 1, 6, 72, 88), N(12, 2, 1, 77, 100, **ST)]
    return parca("ironik_a", "Hınzır", "F major", n, ch, "B", tempo=160, accomp={"pattern": "B C. C."},
                 not_=ironik_a.__doc__)


def destansi_a():
    """Yemin. Fa minör -> Fa majör, 152. Sarkaç i <-> ♭VII ama ÜÇLÜSÜZ, açık beşlilerle (Fa-Do <-> Mi♭-Si♭): davul-zurna
    dem sesi gibi; 1. vuruşta hafif davul. Hücre borazan gibi: Do. Do Fa | Mi♭— Do (noktalı, dörtlü sıçrayış). Çığlık:
    bütün ölçü tutulan Sol5 (♭VII'nin parlak üçlüsü). Kapanış ♭VI - ♭VII - I: bas Re♭-Mi♭-Fa çıkar, ezgi Fa-Sol-La
    çıkar; ilk tam akor Fa MAJÖR, ezgi La5'te kalır."""
    F5, E5 = ([60, 65], 53), ([58, 63], 51)
    kad = [CH(9, [61, 65, 68], 49, beat=1, dur=2), CH(9, [58, 63, 67], 51, beat=3, dur=1)]
    ch = sarkac(F5, E5, ozel={9: kad, 10: ([60, 65, 69], 53), 11: ([60, 65, 69], 48)})
    a = lambda b, v: [N(b, 1, 1.5, 72, v), N(b, 2.5, .5, 72, v - 2), N(b, 3, 1, 77, v + 2)]
    n = a(4, 88) + [N(5, 1, 2, 75, 90), N(5, 3, 1, 72, 84)] + a(6, 92) + [N(7, 1, 3, 79, 104)] + a(8, 92) \
        + [N(9, 1, 2, 77, 94), N(9, 3, 1, 79, 98), N(10, 1, 6.5, 81, 96)]
    return parca("destansi_a", "Yemin", "F minor -> F major", n, ch, "D",
                 engine={"accomp": {"pah_voices": 3}, "perc": {"level_db": -9.0}}, perc={"pattern": "D . x"},
                 not_=destansi_a.__doc__)


def masal_a():
    """Bir Varmış. Mi majör, 144 (ninni gibi, biraz yavaş). Masal sarkacı I <-> iv (Mi <-> La minör): aydınlık akor,
    ardından gölgesi. Hücre beşik gibi sallanır: Mi— Sol♯ | Do— Mi (ezgi önce majör üçlüyü söyler, sonra gölgeye
    düşer). Çığlık: o majör üçlünün bemolü, Sol5 (gülümseme söner). Kapanış Hicaz basamağı: Do-Si-Re♯ -> tutulan Mi5.
    Müzik kutusu + hafif kamış. Yavaş olduğu için hücre iki kez söylenir."""
    E, Am, B7 = ([64, 68, 71], 52), ([60, 64, 69], 57), ([59, 63, 66, 69], 59)
    ch = sarkac(E, Am, ozel={8: B7, 9: E, 10: Am, 11: E})
    a = lambda b, v: [N(b, 1, 2, 76, v), N(b, 3, 1, 80, v)]
    n = a(4, 84) + [N(5, 1, 2, 72, 84), N(5, 3, 1, 76, 84)] + a(6, 88) + [N(7, 1, 2, 79, 98), N(7, 3, 1, 76, 90)] \
        + [N(8, 1, 1, 72, 86), N(8, 2, 1, 71, 86), N(8, 3, 1, 75, 90), N(9, 1, 8.5, 76, 88)]
    return parca("masal_a", "Bir Varmış", "E major (harmonic major)", n, ch, "CD", lead=KUTU_REED, tempo=144,
                 not_=masal_a.__doc__)


BESTELER = {"gizem_a": gizem_a, "merak_a": merak_a, "ironik_a": ironik_a, "destansi_a": destansi_a, "masal_a": masal_a}
HAVA_ADI = {"gizem": "Gizem / gerilim", "merak": "Merak / keşif", "ironik": "İronik / hafif komik",
            "destansi": "Destansı / kahramanlık", "masal": "Masalsı / efsane"}
KONU = {
    "gizem_a": "çözülmemiş gizem, kaybolma, söylenti, lanet, ürkütücü yer",
    "merak_a": "buluş, keşif, şaşırtıcı bilgi, arkeoloji, bilim",
    "ironik_a": "tuhaf olay, kimsenin ölmediği aksilik, kandırmaca, kurnazlık",
    "destansi_a": "kurtarma, direniş, cesaret, zafer",
    "masal_a": "efsane, kehanet, tılsım, halk hikâyesi",
}
