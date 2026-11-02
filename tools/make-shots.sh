#!/usr/bin/env bash
# Every README / KDE Store screenshot, into screenshots/.
#   bash tools/shot-suite.sh      # first: raw desktop + overlay burst (nested Plasma)
#   bash tools/make-shots.sh
# GPU pieces (splash, SDDM, clock) render in one headless nested KWin; the rest
# is offscreen Qt or composed from the raw desktop captures by make-stills.py.
set -u
R=$(cd "$(dirname "$0")/.." && pwd)
S=$R/screenshots; RAW=$S/raw; mkdir -p "$S"
T=$R/build/shots; rm -rf "$T"; mkdir -p "$T/run"; chmod 700 "$T/run"
cd "$R"

# ---- nested KWin: shader renders ------------------------------------------------
cat > "$T/inner.sh" <<IN
cd '$R'
export QT_QPA_PLATFORM=wayland
python3 -u tools/grab.py tools/preview-splash.qml '$S/splash.png' 2600 -- 2
python3 -u tools/grab.py tools/preview-splash.qml '$S/splash-resolved.png' 2600 -- 6
python3 -u tools/grab.py tools/preview-clock.qml '$T/clock.png' 1500
timeout 20 qml6 tools/preview-harness.qml -- '$R/sddm/redacted' '$S/sddm.png' scorn
timeout 20 qml6 tools/preview-harness.qml -- '$R/sddm/redacted' '$S/sddm-error.png' scorn hunter2 fail
IN
env -u WAYLAND_DISPLAY -u DISPLAY XDG_RUNTIME_DIR="$T/run" dbus-run-session -- kwin_wayland --virtual \
    --width 1920 --height 1080 --no-lockscreen --exit-with-session "bash $T/inner.sh" >"$T/kwin.log" 2>&1

# ---- offscreen ------------------------------------------------------------------
QT_QPA_PLATFORM=offscreen QT_STYLE_OVERRIDE=kvantum timeout 30 python3 tools/gallery.py "$S/gallery.png"
python3 tools/plymouth-preview.py "$S"
# open/close effect, rendered with the real shader onto the captured Konsole window
magick "$RAW/desk.png" -crop 1100x640+384+110 +repage "$T/win.png"
build/venv/bin/python tools/render-censor.py "$T/win.png" "$RAW/desk-empty.png" "$S/censor.gif" 410 220

QT_QPA_PLATFORM=offscreen python3 tools/make-stills.py "$S" "$T"
ls -1 "$S"
