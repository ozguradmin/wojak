#!/usr/bin/env bash
# Bulut oturumu kurulumu, tek komut ve kısa çıktı (her adım bir satır OK/FAIL; ayrıntı $LOG'da).
#
#   bash tools/hazirla.sh /workspace/wojak-ozel        # tr kanalı
#   bash tools/hazirla.sh /workspace/wojak-en-ozel     # en kanalı (font yine wojak-ozel'den gelir)
#
# Her oturum aynı tuzaklara düşüyordu (docs/OGRENILENLER.md, 23-28.10.2026): /home/user yokken `ln -sfn` sessizce
# başarısız ve bir test düşüyor; iki depo da ayrık HEAD'de açılıyor (commit kayboluyor, `git pull` duruyor); font ve
# referans elle kuruluyor. Sert hata (çıkış kodu 1): font, referans, testler. Diğerleri uyarı.
set -u

OZEL="${1:-/workspace/wojak-ozel}"
WOJAK="${WOJAK:-/workspace/wojak}"
FONT_DEPO="${FONT_DEPO:-/workspace/wojak-ozel}"   # lisanslı font en kanalında da wojak-ozel'de
FONT=AvenirLTStd-BoldItalic-TR.otf
LOG="${LOG:-/tmp/hazirla.log}"
: > "$LOG"
SERT=0

ok()   { printf 'OK    %s\n' "$*"; }
fail() { printf 'FAIL  %s  (ayrıntı: %s)\n' "$*" "$LOG"; }
sert() { fail "$@"; SERT=1; }

# 1. Sembolik bağ: testler ve eski yaml'lar /home/user/wojak yolunu kullanıyor
if mkdir -p /home/user >>"$LOG" 2>&1 && ln -sfn "$WOJAK" /home/user/wojak >>"$LOG" 2>&1 && [ -d /home/user/wojak/wojak ]; then
  ok "bağ: /home/user/wojak -> $WOJAK"
else
  fail "bağ: /home/user/wojak kurulamadı"
fi

# 2. Depolar: ayrık HEAD ise varsayılan dala geç, sonra çek
varsayilan_dal() {
  local d="$1" dal
  dal=$(git -C "$d" symbolic-ref -q --short refs/remotes/origin/HEAD 2>/dev/null | sed 's#^origin/##')
  [ -n "$dal" ] || dal=$(git -C "$d" ls-remote --symref origin HEAD 2>>"$LOG" | awk '/^ref:/ {sub("refs/heads/", "", $2); print $2; exit}')
  [ -n "$dal" ] || dal=$(git -C "$d" remote show origin 2>>"$LOG" | sed -n 's/.*HEAD branch: //p')
  printf '%s' "$dal"
}
for d in "$WOJAK" "$OZEL"; do
  if [ ! -d "$d/.git" ]; then fail "depo yok: $d"; continue; fi
  not=""
  if ! git -C "$d" symbolic-ref -q HEAD >/dev/null; then
    git -C "$d" fetch -q origin >>"$LOG" 2>&1
    dal=$(varsayilan_dal "$d")
    if [ -n "$dal" ] && git -C "$d" checkout -q "$dal" >>"$LOG" 2>&1; then
      not=" (ayrık HEAD -> $dal)"
    else
      fail "$d: ayrık HEAD, varsayılan dal ('$dal') açılamadı; yerel değişiklik varsa: git stash -u && git checkout <dal>"
      continue
    fi
  fi
  dal=$(git -C "$d" rev-parse --abbrev-ref HEAD)
  if git -C "$d" pull -q --rebase origin "$dal" >>"$LOG" 2>&1; then
    ok "git: $d [$dal]$not"
  else
    fail "git: $d [$dal]$not pull --rebase olmadı (ağ ya da yerel değişiklik)"
  fi
done

cd "$WOJAK" || { sert "cd $WOJAK"; exit 1; }

# 3. Python paketleri (sessiz)
if python -m pip install -q -r requirements.txt pytest faster-whisper py7zr multivolumefile >>"$LOG" 2>&1; then
  ok "pip: requirements + pytest faster-whisper py7zr multivolumefile"
else
  fail "pip install"
fi

# 4. Lisanslı font (repoya girmez; yoksa Poppins'e düşer ve reel "kanal değil" görünür)
mkdir -p assets/fonts/ozel
if [ -f "assets/fonts/ozel/$FONT" ] || cp "$FONT_DEPO/$FONT" assets/fonts/ozel/ >>"$LOG" 2>&1; then
  ok "font: assets/fonts/ozel/$FONT"
else
  sert "font: $FONT_DEPO/$FONT yok"
fi

# 5. Referans reel'ler (hakemlerin kıyas kaynağı): yalnız referans/ yoksa aç
if ls referans/*.mp4 >/dev/null 2>&1; then
  ok "referans: zaten var ($(ls referans/*.mp4 | wc -l) mp4)"
elif python - "$FONT_DEPO/referans.7z" "$WOJAK" >>"$LOG" 2>&1 <<'PY'
import glob, sys
import py7zr
taban, hedef = sys.argv[1], sys.argv[2]
if glob.glob(taban + ".[0-9]*"):          # referans.7z.001, .002 ... (parçalı)
    import multivolumefile
    with multivolumefile.open(taban, mode="rb") as mv, py7zr.SevenZipFile(mv, "r") as z:
        z.extractall(hedef)
else:
    with py7zr.SevenZipFile(taban, "r") as z:
        z.extractall(hedef)
PY
then
  n=$(ls referans/*.mp4 2>/dev/null | wc -l)
  if [ "$n" -gt 0 ]; then ok "referans: açıldı ($n mp4)"; else sert "referans: arşiv açıldı ama referans/*.mp4 yok"; fi
else
  sert "referans: $FONT_DEPO/referans.7z açılamadı"
fi

# 6. İmza müziği (config.MUSIC_IMZA) yerinde mi
if m=$(python -c "from wojak import config; p = config.MUSIC_IMZA; print(p.relative_to(config.ROOT)); raise SystemExit(0 if p.exists() else 1)" 2>>"$LOG"); then
  ok "müzik: $m"
else
  fail "müzik: config.MUSIC_IMZA yok ($m); music: kanal yedek sese düşer"
fi

# 7. Testler: yalnız özet satırı
ozet=$(python -m pytest tests -q -p no:cacheprovider 2>&1 | tee -a "$LOG" | tail -n 1)
if printf '%s' "$ozet" | grep -q "passed" && ! printf '%s' "$ozet" | grep -qE "failed|error"; then
  ok "testler: $ozet"
else
  sert "testler: $ozet"
  grep -E "^(FAILED|ERROR) " "$LOG" | head -n 5 | sed 's/^/      /'
fi

exit $SERT
