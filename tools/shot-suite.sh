#!/usr/bin/env bash
# Raw screenshots in a headless nested Plasma session on a scratch copy of the
# configs, with a clean default panel (no personal widgets):  shot-suite.sh
#   screenshots/raw/desk.png       Dolphin + Konsole on the animated wallpaper
#   screenshots/raw/static/f*.png  a burst for the active-window overlay GIF
set -u
R=$(cd "$(dirname "$0")/.." && pwd)
RAW=$R/screenshots/raw; mkdir -p "$RAW"
T=$R/build/suite; mkdir -p "$T/config" "$T/run"; chmod 700 "$T/run"
for f in kdeglobals kwinrc plasmarc ksplashrc kscreenlockerrc konsolerc kcminputrc gtk-3.0 gtk-4.0 Kvantum; do
    [[ -e ~/.config/$f ]] && cp -r ~/.config/$f "$T/config/"
done
rm -f "$T/config/plasma-org.kde.plasma.desktop-appletsrc" "$T/config/plasmashellrc"
cat > "$T/session.sh" <<IN
cd $R
plasmashell >/dev/null 2>&1 & PS=\$!
sleep 32
qdbus6 org.kde.plasmashell /PlasmaShell org.kde.PlasmaShell.evaluateScript 'var ds=desktops(); for (var i=0;i<ds.length;i++) ds[i].wallpaperPlugin="scorn.redacted"; var ps=panels(); if (ps.length) ps[0].addWidget("scorn.redacted.clock");'
sleep 8
python3 tools/kwin-capture.py $RAW/desk-empty.png
dolphin --new-window $R/build/demo >/dev/null 2>&1 & DO=\$!
sleep 7
konsole --separate --hold -e bash $R/tools/term-demo.sh >/dev/null 2>&1 & KO=\$!
sleep 7
python3 tools/kwin-capture.py $RAW/desk.png
rm -rf $RAW/static; python3 tools/kwin-burst.py $RAW/static 16
# only what this session started: never pkill by name (it reaches the real desktop)
kill \$KO \$DO \$PS 2>/dev/null
IN
env -u WAYLAND_DISPLAY -u DISPLAY XDG_CONFIG_HOME="$T/config" XDG_RUNTIME_DIR="$T/run" KWIN_SCREENSHOT_NO_PERMISSION_CHECKS=1 \
    dbus-run-session -- kwin_wayland --virtual --width 1920 --height 1080 --no-lockscreen --xwayland --exit-with-session "bash $T/session.sh" >"$T/log" 2>&1
ls "$RAW"
