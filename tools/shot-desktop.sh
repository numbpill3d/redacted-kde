#!/usr/bin/env bash
# Screenshot the whole themed desktop in a headless nested session that runs on
# a scratch copy of the configs:  shot-desktop.sh out.png ["app command"] [delay]
set -u
HERE=$(cd "$(dirname "$0")/.." && pwd)
OUT=$1; APP=${2:-konsole}; DELAY=${3:-6}
T=$HERE/build/shot; mkdir -p "$T"
mkdir -p "$T/config" "$T/run"; chmod 700 "$T/run"
for f in kdeglobals kwinrc plasmarc ksplashrc kscreenlockerrc konsolerc plasma-org.kde.plasma.desktop-appletsrc plasmashellrc kcminputrc kactivitymanagerdrc kactivitymanagerd-statsrc gtk-3.0 gtk-4.0; do
    [[ -e ~/.config/$f ]] && cp -r ~/.config/$f "$T/config/"
done
cp -r ~/.config/Kvantum "$T/config/" 2>/dev/null
[[ -n ${KWINRC_EXTRA:-} ]] && printf "%b" "$KWINRC_EXTRA" >> "$T/config/kwinrc"
export XDG_CONFIG_HOME=$T/config XDG_RUNTIME_DIR=$T/run
unset WAYLAND_DISPLAY DISPLAY
KWIN_SCREENSHOT_NO_PERMISSION_CHECKS=1 dbus-run-session -- kwin_wayland --virtual --width 1920 --height 1080 --no-lockscreen --xwayland --exit-with-session \
    "bash -c 'plasmashell >/dev/null 2>&1 & sleep ${WAIT:-34}; $APP >/dev/null 2>&1 & sleep $DELAY; timeout 25 python3 $HERE/tools/kwin-capture.py $OUT; sleep 1'" >"$T/log" 2>&1
[[ -s $OUT ]] && echo "saved $OUT" || { echo "no shot"; tail -15 "$T/log"; }

