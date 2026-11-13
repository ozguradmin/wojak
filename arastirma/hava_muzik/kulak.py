#!/usr/bin/env python3
"""kulak.py: "ears" for the mood-music project. Scores audio the way a listener would LABEL it.

    python3 kulak.py a.wav [b.wav ...] [--json out.json] [--kisa] [--tablo]

For every file (any length / format that soundfile or ffmpeg reads; the first 14 s are analysed, mono, level-normalised
to -20 dBFS RMS so that loudness never changes a verdict) it prints one compact JSON object:

  ast / cnn14   AudioSet tag probabilities (527 real AudioSet labels) from two independent taggers:
                AST  = transformers "MIT/ast-finetuned-audioset-10-10-0.4593" (transformer, 16 kHz, Apache-2.0)
                CNN14= PANNs Cnn14 mAP 0.431 (CNN, 32 kHz, hub copy "nicofarr/panns_Cnn14", Apache-2.0)
                "ilk15" = top 15 tags, "ilgili" = the fixed list of tags that matter to us (ILGILI below).
  clap_genel / clap_buyuk
                CLAP audio embedding ("laion/clap-htsat-unfused" and "laion/larger_clap_general"):
                "benzerlik" = cosine similarity to the embeddings of bilinen/klasik.wav and bilinen/golge.wav,
                "gruplar"   = zero-shot scores for the prompt bank ISTEMLER: inside each group a softmax over the
                              concepts (each concept = mean of several paraphrases), temperature SICAKLIK.
  ozet          the composite indicators (the only thing printed with --kisa): KANAL_UYUMU 0-100, OYUN_MUZIGI 0-100,
                its ingredients, and the six mood indicators. Formulas: see ozet_hesapla() and KULAK.md.

Engineering: embeddings/tag vectors are cached by file hash in ./cache (a repeated call does not load torch at all);
CPU only, torch threads = 2; an fcntl lock (./.kulak.lock) is held around model loading + inference, so several agents
calling the tool at the same moment never load models in parallel. Models load once per process; pass many files per call.

Nobody listens: these are ML labels, not a human verdict. Calibration, limits and failure cases: KULAK.md.
"""
from __future__ import annotations

import argparse
import fcntl
import hashlib
import json
import math
import os
import subprocess
import sys
import tempfile
import warnings

import numpy as np

warnings.filterwarnings("ignore")
os.environ.setdefault("HF_HUB_DISABLE_TELEMETRY", "1")
os.environ.setdefault("TOKENIZERS_PARALLELISM", "false")
os.environ.setdefault("OMP_NUM_THREADS", "2")
os.environ.setdefault("TRANSFORMERS_VERBOSITY", "error")
os.environ.setdefault("HF_HUB_DISABLE_PROGRESS_BARS", "1")
_HUB = os.path.join(os.environ.get("HF_HOME", os.path.expanduser("~/.cache/huggingface")), "hub")
if all(os.path.isdir(os.path.join(_HUB, "models--" + m.replace("/", "--"))) for m in (
        "MIT/ast-finetuned-audioset-10-10-0.4593", "nicofarr/panns_Cnn14", "laion/larger_clap_general", "laion/clap-htsat-unfused")):
    os.environ.setdefault("HF_HUB_OFFLINE", "1")      # models already downloaded: no network call at all

HERE = os.path.dirname(os.path.abspath(__file__))
CACHE = os.path.join(HERE, "cache")
LOCK = os.path.join(HERE, ".kulak.lock")
BILINEN = os.path.abspath(os.path.join(HERE, "..", "bilinen"))
REFS = {"klasik": os.path.join(BILINEN, "klasik.wav"), "golge": os.path.join(BILINEN, "golge.wav")}

VERSION = "k3"            # bump when the audio front end changes (invalidates the audio cache)
SURE = 14.0               # seconds analysed from t = 0
RMS_DB = -20.0            # level normalisation target (dBFS RMS), peak capped at -1 dBFS
GURULTU_DB = -60.0        # white noise added at this level re the signal RMS (None = off). Log-mel models react to the
                          # floor of EMPTY bands / silent gaps ("digital black" vs 16-bit quantisation vs AAC): without it a
                          # -12 dB copy of the same file moved KANAL_UYUMU by up to 9 points; a listener hears no difference.
SICAKLIK = 25.0           # softmax temperature for the zero-shot groups (cosine * SICAKLIK)

AST_ID = "MIT/ast-finetuned-audioset-10-10-0.4593"
CNN_ID = "nicofarr/panns_Cnn14"
CLAP_IDS = {"clap_genel": "laion/clap-htsat-unfused", "clap_buyuk": "laion/larger_clap_general"}
# "laion/larger_clap_music" was tried first and dropped: with transformers 5.22 its hub checkpoint is collapsed (text-text cosine
# 0.999, audio-text cosine ~0.01, logit scale 1.03), so it cannot do zero-shot. See KULAK.md "Limits".

# ---------------------------------------------------------------------------------------------- AudioSet tags we watch
ILGILI = [
    "Music", "Video game music", "Background music", "Theme music", "Soundtrack music", "Jingle (music)",
    "Accordion", "Harmonica", "Organ", "Electronic organ", "Hammond organ", "Piano", "Electric piano", "Keyboard (musical)",
    "Synthesizer", "Sampler", "Harpsichord",
    "Mallet percussion", "Marimba, xylophone", "Glockenspiel", "Vibraphone", "Bell", "Chime", "Tubular bells", "Harp",
    "Orchestra", "Brass instrument", "French horn", "Trumpet", "String section", "Bowed string instrument", "Violin, fiddle",
    "Cello", "Pizzicato", "Plucked string instrument", "Wind instrument, woodwind instrument", "Flute", "Clarinet",
    "Percussion", "Drum", "Timpani", "Bagpipes", "Theremin",
    "Scary music", "Funny music", "Happy music", "Sad music", "Tender music", "Exciting music", "Angry music", "Lullaby",
    "Classical music", "Folk music", "Traditional music", "Music for children", "Christmas music", "New-age music",
    "Ambient music", "Electronic music", "Music of Latin America", "Middle Eastern music", "Music of Asia",
    "Independent music", "Dance music", "Wedding music", "Opera", "Jazz",
    "Musical instrument", "Speech", "Singing", "Synthetic singing", "Yodeling", "Whistling", "Humming",
    "Jingle, tinkle", "Ding", "Ding-dong", "Ringtone", "Sound effect", "Television", "Radio",
]

# ------------------------------------------------------------------------------------------------- CLAP prompt bank
# group -> concept -> paraphrases.  Scores: softmax inside the group over the concept means.
ISTEMLER = {
    "tur": {       # what kind of thing does a listener call this?
        "oyun": ["background music of a video game", "video game soundtrack music", "level music from a casual mobile game",
                 "looping background music from a role-playing game", "menu music of a computer game"],
        "gramofon_vals": ["an old gramophone record of an accordion waltz", "a scratchy vintage recording of a sad waltz",
                          "an old-time musette waltz from an antique record", "a melancholic harmonica waltz from an old radio",
                          "an old sad waltz played on a barrel organ or accordion"],
        "film": ["a cinematic orchestral film score", "an epic movie soundtrack with full orchestra", "hollywood film music"],
        "meme": ["music from an internet meme video", "a funny meme background song", "a sad meme song used in short videos",
                 "the background sound of a viral short video"],
        "stok": ["royalty free stock background music for videos", "corporate background music", "library music for a commercial"],
        "cizgi_film": ["music from a children's cartoon", "cartoon background music", "music for a kids tv show"],
    },
    "produksiyon": {
        "lofi_eski": ["a lo-fi old recording", "a low quality vintage recording with narrow bandwidth",
                      "music playing through an old telephone or AM radio", "an old 78 rpm record", "a muffled worn-out tape recording"],
        "temiz_modern": ["a clean modern studio production", "a high fidelity crisp modern recording",
                         "polished professional music production in wide stereo", "clear digital audio with full bass and bright highs"],
    },
    "kaynak": {
        "midi_sentetik": ["MIDI music with synthetic orchestra instruments", "computer music made with General MIDI instruments",
                          "a cheap synthesizer keyboard demo song", "virtual instruments sequenced on a computer",
                          "sampled orchestral instruments from a sound module"],
        "gercek_eski": ["a real vintage instrument played by a musician", "a live acoustic performance on a real instrument",
                        "a street musician playing an old accordion", "a musician playing a real harmonica"],
    },
    "doku": {
        "tek_calgi": ["a single solo instrument playing alone", "a simple tune on one instrument with sparse accompaniment",
                      "one instrument playing a melody and its own chords"],
        "katmanli": ["a full arrangement with many layered instruments", "a busy orchestral arrangement with percussion and many parts",
                     "an ensemble of many different instruments playing together"],
    },
    "calgi": {
        "akordeon": ["an accordion playing", "a musette accordion melody"],
        "armonika": ["a harmonica playing", "a tremolo harmonica melody"],
        "org": ["a reed organ or harmonium playing", "a barrel organ or fairground organ playing"],
        "piyano": ["a piano playing", "solo piano music"],
        "muzik_kutusu": ["a music box playing", "a celesta or glockenspiel melody"],
        "marimba": ["a marimba or xylophone playing", "mallet percussion melody"],
        "pizzicato": ["pizzicato strings", "plucked orchestral strings playing staccato"],
        "yayli": ["a string orchestra playing", "legato violins and cellos"],
        "bakir": ["brass instruments and french horns", "a trumpet fanfare"],
        "tahta_nefesli": ["a flute or clarinet melody", "woodwind instruments playing"],
        "synth": ["a synthesizer pad", "electronic synthesizer music"],
        "davul": ["drums and percussion", "timpani and orchestral percussion"],
        "chiptune": ["8-bit chiptune music", "retro game console sound chip music"],
    },
    "hava": {
        "gizem": ["mysterious tense music", "creepy suspenseful music", "eerie music for an unsolved mystery",
                  "dark ominous music full of suspense"],
        "merak": ["curious playful music of wonder", "inquisitive music for a discovery", "light music that sounds like wondering about something",
                  "quirky investigative music"],
        "ironik": ["comic ironic music", "mischievous funny music", "silly clumsy comedy music", "sarcastic tongue-in-cheek music"],
        "destansi": ["heroic epic music", "triumphant majestic music", "a proud heroic march", "glorious music for a victorious battle"],
        "masal": ["fairy tale music", "dreamy lullaby music", "magical music for an old legend", "gentle music for a bedtime story"],
        "huzun": ["sad melancholic music", "sorrowful mournful music", "a heartbreaking nostalgic tune", "tragic grieving music"],
    },
    "ton": {       # mood axis 1 (less tied to instrument stereotypes than the six mood names)
        "karanlik": ["dark ominous music in a minor key", "gloomy dark brooding music", "sinister unsettling music"],
        "aydinlik": ["bright cheerful music in a major key", "happy sunny uplifting music", "light-hearted joyful music"],
    },
    "enerji": {    # mood axis 2
        "sakin": ["slow calm gentle music", "quiet soft peaceful music", "a slow sparse tune with long notes"],
        "canli": ["fast lively bouncy music", "energetic upbeat rhythmic music", "a quick staccato tune with many short notes"],
    },
    "olcu": {
        "vals": ["a waltz in three-four time", "oom-pah-pah waltz accompaniment"],
        "mars": ["a march in four-four time", "a steady four-on-the-floor beat"],
        "serbest": ["ambient music without a beat", "slow drifting music with no rhythm"],
    },
}


def _istem_hash() -> str:
    return hashlib.sha1(json.dumps(ISTEMLER, sort_keys=True).encode()).hexdigest()[:10]


# ------------------------------------------------------------------------------------------------------------ audio
def ses_oku(path: str, sr: int = 48000) -> np.ndarray:
    """mono float32 at 48 kHz, first SURE seconds, level-normalised."""
    import soundfile as sf
    try:
        x, fs = sf.read(path, dtype="float32", always_2d=True)
    except Exception:
        with tempfile.NamedTemporaryFile(suffix=".wav") as tmp:
            subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", path, "-t", str(SURE + 1), "-ac", "2", tmp.name], check=True)
            x, fs = sf.read(tmp.name, dtype="float32", always_2d=True)
    x = x.mean(axis=1)[: int(SURE * fs)]
    if fs != sr:
        import scipy.signal as ss
        g = math.gcd(int(fs), sr)
        x = ss.resample_poly(x, sr // g, int(fs) // g).astype(np.float32)
    rms = float(np.sqrt(np.mean(x ** 2)) + 1e-12)
    x = x * (10 ** (RMS_DB / 20) / rms)
    pk = float(np.max(np.abs(x)) + 1e-12)
    if pk > 0.89:
        x = x * (0.89 / pk)
    if GURULTU_DB is not None:        # fixed inaudible noise floor: see GURULTU_DB
        g = np.random.default_rng(7).standard_normal(len(x)).astype(np.float32)
        x = x + g * (float(np.sqrt(np.mean(x ** 2))) * 10 ** (GURULTU_DB / 20))
    return x.astype(np.float32)


def _resample(x: np.ndarray, sr_in: int, sr_out: int) -> np.ndarray:
    import scipy.signal as ss
    g = math.gcd(sr_in, sr_out)
    return ss.resample_poly(x, sr_out // g, sr_in // g).astype(np.float32)


def _pencereler(x: np.ndarray, sr: int, win_s: float) -> list[np.ndarray]:
    """<= win_s: one window; longer: first and last win_s (their mean covers the whole 14 s)."""
    n = int(win_s * sr)
    if len(x) <= n:
        return [x]
    return [x[:n], x[-n:]]


def dosya_hash(path: str) -> str:
    h = hashlib.sha1()
    with open(path, "rb") as f:
        for blk in iter(lambda: f.read(1 << 20), b""):
            h.update(blk)
    h.update(f"{VERSION}|{SURE}|{RMS_DB}|{GURULTU_DB}".encode())
    return h.hexdigest()[:20]


# ----------------------------------------------------------------------------------------------------------- models
_M: dict = {}


def _torch():
    import torch
    if "torch" not in _M:
        torch.set_num_threads(2)
        try:
            torch.set_num_interop_threads(1)
        except Exception:
            pass
        _M["torch"] = torch
    return torch


def _ast():
    if "ast" not in _M:
        from transformers import ASTFeatureExtractor, ASTForAudioClassification
        fe = ASTFeatureExtractor.from_pretrained(AST_ID)
        m = ASTForAudioClassification.from_pretrained(AST_ID).eval()
        _M["ast"] = (fe, m)
    return _M["ast"]


def etiketler() -> list[str]:
    p = os.path.join(HERE, "audioset_labels.json")
    if os.path.exists(p):
        return json.load(open(p))
    from transformers import AutoConfig
    c = AutoConfig.from_pretrained(AST_ID)
    labs = [c.id2label[i] for i in range(len(c.id2label))]
    json.dump(labs, open(p, "w"))
    return labs


def ast_olasilik(x48: np.ndarray) -> np.ndarray:
    torch = _torch()
    fe, m = _ast()
    x = _resample(x48, 48000, 16000)
    out = []
    for w in _pencereler(x, 16000, 10.24):
        inp = fe(w, sampling_rate=16000, return_tensors="pt")
        with torch.no_grad():
            out.append(torch.sigmoid(m(**inp).logits)[0].numpy())
    return np.mean(out, axis=0).astype(np.float32)


def _cnn14():
    if "cnn" in _M:
        return _M["cnn"]
    torch = _torch()
    import torch.nn as nn
    import torch.nn.functional as F
    from huggingface_hub import hf_hub_download
    from safetensors.torch import load_file

    class ConvBlock(nn.Module):
        def __init__(self, i, o):
            super().__init__()
            self.conv1 = nn.Conv2d(i, o, 3, 1, 1, bias=False)
            self.conv2 = nn.Conv2d(o, o, 3, 1, 1, bias=False)
            self.bn1 = nn.BatchNorm2d(o)
            self.bn2 = nn.BatchNorm2d(o)

        def forward(self, x, pool=(2, 2)):
            x = F.relu_(self.bn1(self.conv1(x)))
            x = F.relu_(self.bn2(self.conv2(x)))
            return F.avg_pool2d(x, pool)

    class Cnn14(nn.Module):               # PANNs Cnn14 (Kong et al. 2020), 32 kHz, 64 mel, hop 320, window 1024
        def __init__(self):
            super().__init__()
            self.bn0 = nn.BatchNorm2d(64)
            ch = [1, 64, 128, 256, 512, 1024, 2048]
            for k in range(6):
                setattr(self, f"conv_block{k + 1}", ConvBlock(ch[k], ch[k + 1]))
            self.fc1 = nn.Linear(2048, 2048)
            self.fc_audioset = nn.Linear(2048, 527)
            self.register_buffer("melW", torch.zeros(513, 64))
            self.register_buffer("win", torch.hann_window(1024, periodic=True))

        def forward(self, wav):          # wav (B, N)
            s = torch.stft(wav, 1024, 320, 1024, self.win, center=True, pad_mode="reflect", return_complex=True)
            p = (s.real ** 2 + s.imag ** 2).transpose(1, 2)                 # (B, T, 513)
            x = 10.0 * torch.log10(torch.clamp(p @ self.melW, min=1e-10))   # (B, T, 64)
            x = x[:, None]                                                  # (B, 1, T, 64)
            x = self.bn0(x.transpose(1, 3)).transpose(1, 3)
            for k in range(1, 6):
                x = getattr(self, f"conv_block{k}")(x, (2, 2))
            x = self.conv_block6(x, (1, 1))
            x = x.mean(dim=3)
            x = x.max(dim=2)[0] + x.mean(dim=2)
            x = F.relu_(self.fc1(x))
            return torch.sigmoid(self.fc_audioset(x))

    sd = load_file(hf_hub_download(CNN_ID, "model.safetensors"))
    sd = {k.replace("backbone.", ""): v for k, v in sd.items()}
    sd["melW"] = sd.pop("logmel_extractor.melW")
    sd = {k: v for k, v in sd.items() if not k.startswith("spectrogram_extractor")}
    m = Cnn14()
    miss = m.load_state_dict(sd, strict=False)
    assert set(miss.missing_keys) <= {"win"} and not miss.unexpected_keys, miss
    _M["cnn"] = m.eval()
    return _M["cnn"]


def cnn_olasilik(x48: np.ndarray) -> np.ndarray:
    torch = _torch()
    m = _cnn14()
    x = _resample(x48, 48000, 32000)
    with torch.no_grad():
        return m(torch.from_numpy(x)[None])[0].numpy().astype(np.float32)


def _clap(key: str):
    if key not in _M:
        from transformers import ClapModel, ClapProcessor
        _M[key] = (ClapProcessor.from_pretrained(CLAP_IDS[key]), ClapModel.from_pretrained(CLAP_IDS[key]).eval())
    return _M[key]


def _vec(o):
    """transformers versions differ: tensor or an output object."""
    torch = _torch()
    if isinstance(o, torch.Tensor):
        return o
    for a in ("audio_embeds", "text_embeds", "pooler_output"):
        v = getattr(o, a, None)
        if v is not None:
            return v
    raise RuntimeError("unknown CLAP output")


def clap_ses(key: str, x48: np.ndarray) -> np.ndarray:
    torch = _torch()
    proc, m = _clap(key)
    embs = []
    for w in _pencereler(x48, 48000, 10.0):
        inp = proc.feature_extractor(w, sampling_rate=48000, return_tensors="pt")
        with torch.no_grad():
            e = _vec(m.get_audio_features(**inp))[0]
        embs.append((e / e.norm()).numpy())
    e = np.mean(embs, axis=0)
    return (e / np.linalg.norm(e)).astype(np.float32)


def clap_metin(key: str) -> dict:
    """{group: {concept: (n_paraphrase, 512) unit vectors}} cached by prompt-bank hash."""
    p = os.path.join(CACHE, f"metin_{key}_{_istem_hash()}.npz")
    flat = [(g, c, t) for g, cs in ISTEMLER.items() for c, ts in cs.items() for t in ts]
    if os.path.exists(p):
        E = np.load(p)["E"]
    else:
        torch = _torch()
        proc, m = _clap(key)
        tok = proc.tokenizer([t for _, _, t in flat], padding=True, return_tensors="pt")
        with torch.no_grad():
            e = _vec(m.get_text_features(**tok))
        E = (e / e.norm(dim=-1, keepdim=True)).numpy().astype(np.float32)
        os.makedirs(CACHE, exist_ok=True)
        np.savez(p, E=E)
    out: dict = {}
    for (g, c, _), v in zip(flat, E):
        out.setdefault(g, {}).setdefault(c, []).append(v)
    return {g: {c: np.stack(v) for c, v in cs.items()} for g, cs in out.items()}


# ------------------------------------------------------------------------------------------------------------ cache
def _cache_yolu(h: str) -> str:
    return os.path.join(CACHE, f"ses_{h}.npz")


def _eksik_metin() -> bool:
    return any(not os.path.exists(os.path.join(CACHE, f"metin_{k}_{_istem_hash()}.npz")) for k in CLAP_IDS)


def hazirla(paths: list[str]) -> dict:
    """returns {path: raw dict}; computes the missing ones under the lock."""
    os.makedirs(CACHE, exist_ok=True)
    hs = {p: dosya_hash(p) for p in paths}
    eksik = [p for p in paths if not os.path.exists(_cache_yolu(hs[p]))]
    if eksik or _eksik_metin():
        with open(LOCK, "w") as lk:
            fcntl.flock(lk, fcntl.LOCK_EX)
            try:
                for k in CLAP_IDS:
                    clap_metin(k)
                for p in eksik:
                    if os.path.exists(_cache_yolu(hs[p])):       # another process did it while we waited
                        continue
                    x = ses_oku(p)
                    d = {"sure": np.float32(len(x) / 48000), "ast": ast_olasilik(x), "cnn14": cnn_olasilik(x)}
                    for k in CLAP_IDS:
                        d[k] = clap_ses(k, x)
                    tmp = _cache_yolu(hs[p]) + f".{os.getpid()}.tmp.npz"
                    np.savez(tmp, **d)
                    os.replace(tmp, _cache_yolu(hs[p]))
            finally:
                fcntl.flock(lk, fcntl.LOCK_UN)
    return {p: dict(np.load(_cache_yolu(hs[p]))) for p in paths}


# ---------------------------------------------------------------------------------------------------------- scoring
def _softmax(v: np.ndarray) -> np.ndarray:
    v = v - v.max()
    e = np.exp(v)
    return e / e.sum()


def gruplar(emb: np.ndarray, metin: dict) -> tuple[dict, dict]:
    """(softmax per group, raw mean cosine per concept)"""
    sm, cos = {}, {}
    for g, cs in metin.items():
        names = list(cs)
        c = np.array([float((cs[n] @ emb).mean()) for n in names])
        p = _softmax(c * SICAKLIK)
        sm[g] = {n: round(float(v), 4) for n, v in zip(names, p)}
        cos[g] = {n: round(float(v), 4) for n, v in zip(names, c)}
    return sm, cos


# ------------------------------------------------------------------------------------- composite indicators (KULAK.md §3)
KU_AGIRLIK = {"gramofon": 0.35, "benzerlik": 0.30, "lofi": 0.20, "kamis": 0.15}
BENZ_TABAN, BENZ_TAVAN = 0.50, 0.90       # cosine of unrelated music .. of the house family, mapped to 0 .. 100
MEDYA_ETIKET = ("Background music", "Theme music", "Soundtrack music", "Video game music", "Music for children")
HAVA_ETIKET = ("Scary music", "Funny music", "Happy music", "Sad music", "Tender music", "Exciting music", "Lullaby")
HAVALAR = ("gizem", "merak", "ironik", "destansi", "masal", "huzun")
# house baseline = mean of the six accepted files (klasik, golge, ic_cekis, ic_cekis_b, ic_cekis_hohner, golge_sentez);
# "hava_ev_farki" = indicator minus this, i.e. "how much more <mood> than our signature waltz". Calibrated 13.11.2026.
EV_HAVA = {"gizem": 6.6, "merak": 1.9, "ironik": 32.5, "destansi": 6.2, "masal": 40.8, "huzun": 12.0}
EV_KARANLIK = 43.7


def _mm(r: dict, f) -> float:
    return float(np.mean([f(r[k]) for k in CLAP_IDS]))


def _etiket(r: dict, name: str) -> float:
    return 0.5 * (r["ast"]["ilgili"][name] + r["cnn14"]["ilgili"][name])


def ozet_hesapla(r: dict) -> dict:
    """Composite indicators, all 0-100. Every CLAP number is the mean of the two CLAP models; every tag number the mean
    of the two taggers.
      KANAL_UYUMU = 0.35 gramofon + 0.30 benzerlik + 0.20 lofi + 0.15 kamis
        gramofon   share of the "what kind of music" vote that goes to "old gramophone accordion/harmonica waltz"
                   (against video game / film score / meme / stock / cartoon)
        benzerlik  CLAP audio cosine to the references, the CLASSIC counted twice: s = (2 cos_klasik + cos_golge) / 3,
                   mapped linearly from 0.50 (unrelated music) to 0.90 (house family)
        lofi       "lo-fi old recording" against "clean modern production"
        kamis      share of the instrument vote for free reeds (accordion + harmonica + reed/barrel organ)
      OYUN_FON    share of the "kind" vote for video game + film score + stock + cartoon music ("functional media music",
                  what the owner called game background music); medya = its four parts; etiket_medya = sum of the
                  AudioSet tags Background / Theme / Soundtrack / Video game music / Music for children (capped at 100)
      katmanli    "many layered instruments" against "one instrument"
      hava        the six mood shares (softmax over the six moods); hava_ev_farki = minus the house baseline EV_HAVA
      karanlik    "dark ominous minor" against "bright cheerful major"; etiket_hava = AudioSet mood tags in %
    """
    g = lambda grp, c: 100.0 * _mm(r, lambda m: m["gruplar"][grp][c])
    gramofon = g("tur", "gramofon_vals")
    s = _mm(r, lambda m: (2 * m["benzerlik"]["klasik"] + m["benzerlik"]["golge"]) / 3) if r[next(iter(CLAP_IDS))]["benzerlik"] else 0.0
    benz = 100.0 * min(1.0, max(0.0, (s - BENZ_TABAN) / (BENZ_TAVAN - BENZ_TABAN)))
    lofi = g("produksiyon", "lofi_eski")
    kamis = g("calgi", "akordeon") + g("calgi", "armonika") + g("calgi", "org")
    bil = {"gramofon": gramofon, "benzerlik": benz, "lofi": lofi, "kamis": kamis}
    ku = sum(KU_AGIRLIK[k] * bil[k] for k in KU_AGIRLIK)
    medya = {c: g("tur", c) for c in ("oyun", "film", "stok", "cizgi_film")}
    hava = {h: g("hava", h) for h in HAVALAR}
    calgi = {c: g("calgi", c) for c in ISTEMLER["calgi"]}
    ilk_calgi = sorted(calgi, key=calgi.get, reverse=True)[:3]
    y = lambda v: round(float(v), 1)
    return {
        "KANAL_UYUMU": y(ku),
        "karar": "kanal sesi" if ku >= 65 else ("arada" if ku >= 30 else "kanal sesi degil"),
        "bilesenler": {k: y(v) for k, v in bil.items()},
        "kosinus_klasik_golge": [round(_mm(r, lambda m: m["benzerlik"].get("klasik", 0.0)), 3),
                                 round(_mm(r, lambda m: m["benzerlik"].get("golge", 0.0)), 3)],
        "OYUN_FON": y(sum(medya.values())),
        "medya": {k: y(v) for k, v in medya.items()},
        "meme": y(g("tur", "meme")),
        "etiket_medya": y(min(100.0, 100.0 * sum(_etiket(r, n) for n in MEDYA_ETIKET))),
        "etiket_oyun": y(100.0 * _etiket(r, "Video game music")),
        "katmanli": y(g("doku", "katmanli")),
        "midi_sentetik": y(g("kaynak", "midi_sentetik")),
        "calgi_ilk3": {c: y(calgi[c]) for c in ilk_calgi},
        "hava": {k: y(v) for k, v in hava.items()},
        "hava_ev_farki": {k: y(v - EV_HAVA[k]) for k, v in hava.items()},
        "karanlik": y(g("ton", "karanlik")),
        "karanlik_ev_farki": y(g("ton", "karanlik") - EV_KARANLIK),
        "canli": y(g("enerji", "canli")),
        "etiket_hava": {n.replace(" music", ""): y(100.0 * _etiket(r, n)) for n in HAVA_ETIKET},
    }


REF_EMB = os.path.join(HERE, "ref_emb.npz")     # CLAP embeddings of the two references (measurement only, no audio)


def _ref_emb(raw: dict) -> dict:
    """{name: {clap key: vector}}; refreshed from bilinen/ when the files are there, else read from ref_emb.npz."""
    if all(q in raw for q in REFS.values()):
        d = {f"{n}|{k}": raw[q][k] for n, q in REFS.items() for k in CLAP_IDS}
        old = dict(np.load(REF_EMB)) if os.path.exists(REF_EMB) else {}
        if set(old) != set(d) or any(not np.allclose(old[x], d[x]) for x in d):
            tmp = REF_EMB + f".{os.getpid()}.tmp.npz"
            np.savez(tmp, **d)
            os.replace(tmp, REF_EMB)
    elif os.path.exists(REF_EMB):
        d = dict(np.load(REF_EMB))
    else:
        return {}
    return {n: {k: d[f"{n}|{k}"] for k in CLAP_IDS} for n in REFS}


def skorla(paths: list[str]) -> list[dict]:
    refs = [p for p in REFS.values() if os.path.exists(p)]
    raw = hazirla(list(dict.fromkeys(paths + refs)))
    ref = _ref_emb(raw)
    labs = etiketler()
    metin = {k: clap_metin(k) for k in CLAP_IDS}
    out = []
    for p in paths:
        d = raw[p]
        r = {"dosya": p, "sure_s": round(float(d["sure"]), 2)}
        for t in ("ast", "cnn14"):
            pr = d[t]
            top = np.argsort(-pr)[:15]
            r[t] = {"ilk15": {labs[i]: round(float(pr[i]), 3) for i in top},
                    "ilgili": {n: round(float(pr[labs.index(n)]), 4) for n in ILGILI}}
        for k in CLAP_IDS:
            sm, cos = gruplar(d[k], metin[k])
            r[k] = {"benzerlik": {n: round(float(d[k] @ ref[n][k]), 4) for n in ref}, "gruplar": sm, "kosinus": cos}
        r["ozet"] = ozet_hesapla(r)
        out.append(r)
    return out


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("dosyalar", nargs="+")
    ap.add_argument("--json", help="write the full result list to this file")
    ap.add_argument("--kisa", action="store_true", help="print only the composite indicators")
    ap.add_argument("--etiketler", action="store_true", help="print the full AudioSet label set and exit")
    a = ap.parse_args()
    if a.etiketler:
        print(json.dumps(etiketler(), ensure_ascii=False))
        return
    res = skorla([os.path.abspath(p) for p in a.dosyalar])
    if a.json:
        json.dump(res, open(a.json, "w"), ensure_ascii=False, indent=1)
    for r in res:
        if a.kisa:
            print(json.dumps({"dosya": os.path.basename(r["dosya"]), **r["ozet"]}, ensure_ascii=False))
        else:
            r2 = {k: v for k, v in r.items()}
            for k in CLAP_IDS:
                r2[k] = {kk: vv for kk, vv in r[k].items() if kk != "kosinus"}
            print(json.dumps(r2, ensure_ascii=False, separators=(",", ":")))


if __name__ == "__main__":
    main()
