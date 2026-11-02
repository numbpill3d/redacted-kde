#!/usr/bin/env bash
# Render a QML file with real GPU shaders inside a headless nested KWin:
#   nested-grab.sh file.qml out.png [ms] [args for the qml...]
# Scratch files live in build/nested (reused each run).
set -u
R=$(cd "$(dirname "$0")/.." && pwd)
T=$R/build/nested
mkdir -p "$T/run"; chmod 700 "$T/run"
QMLF=$(realpath "$1"); OUT=$(realpath -m "$2"); MS=${3:-2500}; shift 3 || true
{ echo "cd '$R'"
  printf 'QT_QPA_PLATFORM=wayland python3 -u tools/grab.py %q %q %q --' "$QMLF" "$OUT" "$MS"
  printf ' %q' "$@"; echo " > '$T/client.log' 2>&1"; } > "$T/inner.sh"
: > "$T/client.log"
env -u WAYLAND_DISPLAY -u DISPLAY XDG_RUNTIME_DIR="$T/run" dbus-run-session -- kwin_wayland --virtual \
    --width 1920 --height 1080 --no-lockscreen --exit-with-session "bash $T/inner.sh" >"$T/kwin.log" 2>&1
cat "$T/client.log"
