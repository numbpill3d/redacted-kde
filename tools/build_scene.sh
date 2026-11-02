#!/usr/bin/env bash
# Compile the shaders and copy the shared scene (QML + art) into every package
# that shows it. Run after build_wallpaper.py or any change in qml/ or shaders/.
set -euo pipefail
R=$(cd "$(dirname "$0")/.." && pwd)
QSB=/usr/lib/qt6/bin/qsb
for f in "$R"/shaders/*.frag; do
    "$QSB" --glsl "100 es,120,150" --hlsl 50 --msl 12 -o "$f.qsb" "$f"
done
FONT=$HOME/.local/share/fonts/DepartureMono/DepartureMonoNerdFont-Regular.otf
stage() {   # stage <ui dir> <art dir>
    mkdir -p "$1" "$2"
    cp "$R/qml/RedactedScene.qml" "$1/"
    cp "$R/assets/face.png" "$R/shaders/scene.frag.qsb" "$2/"
    cp "$FONT" "$2/DepartureMono.otf"
}
stage "$R/build/preview" "$R/build/preview/art"
for d in "$@"; do stage "$d" "$d/art"; done
# packages (created by their own steps; staged only if present)
P=$R/plasma
[[ -d $P/wallpapers/scorn.redacted ]] && stage "$P/wallpapers/scorn.redacted/contents/ui" "$P/wallpapers/scorn.redacted/contents/ui/art"
[[ -d $P/look-and-feel/scorn.redacted/contents/splash ]] && stage "$P/look-and-feel/scorn.redacted/contents/splash" "$P/look-and-feel/scorn.redacted/contents/splash/art"
PW=$P/plasmoids/scorn.redacted.clock/contents/art
[[ -d $PW ]] && { cp "$R/shaders/static.frag.qsb" "$PW/"; cp "$FONT" "$PW/DepartureMono.otf"; }
[[ -d $R/sddm/redacted ]] && stage "$R/sddm/redacted" "$R/sddm/redacted/art"
echo "scene staged"
