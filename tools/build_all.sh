#!/usr/bin/env bash
# Rebuild every piece from palette.py, then check nothing picked up a tint.
#   bash tools/build_all.sh && bash apply.sh
# (SDDM's Main.qml and the KSplash QML hard-code their greys; ACCENT_STEP doesn't reach them.)
set -euo pipefail
R=$(cd "$(dirname "$0")/.." && pwd)
cd "$R"
for g in colors kvantum plasma aurorae icons wallpaper plymouth; do
    python3 "tools/build_$g.py"
done
bash tools/build_scene.sh
cp assets/wallpaper.png plasma/image-wallpaper/Redacted/contents/images/1920x1080.png
cp assets/wallpaper-2560x1440.png plasma/image-wallpaper/Redacted/contents/images/2560x1440.png
cp assets/wallpaper-3840x2160.png plasma/image-wallpaper/Redacted/contents/images/3840x2160.png
python3 tools/check_tint.py
