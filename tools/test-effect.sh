#!/usr/bin/env bash
# Record the censor open/close animation in a headless nested KWin (no plasmashell):
#   test-effect.sh out-dir [ms]
# The effect must be installed in ~/.local/share/kwin/effects (apply.sh --install).
set -u
HERE=$(cd "$(dirname "$0")/.." && pwd)
OUTD=$(realpath -m "$1"); MS=${2:-2400}
T=$HERE/build/effect-test
mkdir -p "$T/config" "$T/run" "$OUTD"; chmod 700 "$T/run"
cp ~/.config/kdeglobals "$T/config/" 2>/dev/null
printf '[Effect-redacted_censor]\nOpenDuration=%s\nCloseDuration=%s\n\n[Plugins]\nredacted_censorEnabled=true\nxenoglyph_unfurlEnabled=false\nxenoglyph_runesEnabled=false\n' "$MS" "$MS" > "$T/config/kwinrc"
cat > "$T/session.sh" <<IN
sleep 3
python3 $HERE/tools/kwin-burst.py $OUTD/open 30 "kwrite $HERE/README.md"
sleep 2
python3 $HERE/tools/kwin-burst.py $OUTD/close 1
( sleep 0.2; pkill -f "^kwrite $HERE/README.md\$" ) &   # only the test window, never every kwrite
python3 $HERE/tools/kwin-burst.py $OUTD/close 30
IN
env -u WAYLAND_DISPLAY -u DISPLAY XDG_CONFIG_HOME="$T/config" XDG_RUNTIME_DIR="$T/run" KWIN_SCREENSHOT_NO_PERMISSION_CHECKS=1 \
    dbus-run-session -- kwin_wayland --virtual --width 1920 --height 1080 --no-lockscreen --xwayland --exit-with-session "bash $T/session.sh" >"$T/log" 2>&1
grep -iE "redacted|shader|glsl|compile" "$T/log" | head -12
tail -1 "$OUTD/open/times.txt" 2>/dev/null
