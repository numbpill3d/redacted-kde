#!/usr/bin/env bash
# Redacted — user-level install + apply (no sudo).
#   bash ~/redacted/apply.sh            install everything and switch to it
#   bash ~/redacted/apply.sh --install  copy files only, change nothing
#   bash ~/redacted/apply.sh --revert   restore the configs saved by the last apply
# SDDM + Plymouth need root: sudo bash ~/redacted/install.sh
set -euo pipefail
HERE=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
C=${XDG_CONFIG_HOME:-$HOME/.config}
D=${XDG_DATA_HOME:-$HOME/.local/share}
BK=$HERE/backup
FILES=(kdeglobals kwinrc plasmarc ksplashrc kscreenlockerrc konsolerc Kvantum/kvantum.kvconfig kitty/kitty.conf)

reconfigure() {
    qdbus6 org.kde.KWin /KWin reconfigure >/dev/null 2>&1 || true
}

if [[ ${1:-} == --revert ]]; then
    last=$(ls -1d "$BK"/* 2>/dev/null | head -1) || true   # oldest = pre-Redacted
    [[ -n ${last:-} ]] || { echo "no backup in $BK" >&2; exit 1; }
    echo "==> Restoring configs from $last"
    for f in "${FILES[@]}"; do
        if [[ -f $last/$f ]]; then
            install -Dm644 "$last/$f" "$C/$f"
        elif [[ -f $last/.absent/$f ]]; then
            rm -f "$C/$f"
        fi
    done
    scheme=$(kreadconfig6 --file kdeglobals --group General --key ColorScheme)
    theme=$(kreadconfig6 --file plasmarc --group Theme --key name)
    icons=$(kreadconfig6 --file kdeglobals --group Icons --key Theme)
    # re-apply through the tools so running apps pick the old look back up
    plasma-apply-colorscheme Redacted >/dev/null 2>&1 || true
    plasma-apply-colorscheme "$scheme" || true
    plasma-apply-desktoptheme default >/dev/null 2>&1 || true
    plasma-apply-desktoptheme "$theme" || true
    /usr/lib/plasma-changeicons "$icons" || true
    reconfigure
    echo "Reverted. Theme files stay installed; log out and back in for every app to follow."
    exit 0
fi

echo "==> Installing Redacted files"
install -Dm644 "$HERE/colors/Redacted.colors" "$D/color-schemes/Redacted.colors"
rm -rf "$C/Kvantum/Redacted" "$D/plasma/desktoptheme/Redacted" "$D/aurorae/themes/Redacted" \
       "$D/icons/Redacted" "$D/plasma/look-and-feel/scorn.redacted"
mkdir -p "$C/Kvantum" "$D/plasma/desktoptheme" "$D/aurorae/themes" "$D/icons" "$D/plasma/look-and-feel" "$D/konsole" "$C/kitty"
cp -r "$HERE/kvantum/Redacted" "$C/Kvantum/"
cp -r "$HERE/plasma/desktoptheme/Redacted" "$D/plasma/desktoptheme/"
cp -r "$HERE/aurorae/Redacted" "$D/aurorae/themes/"
cp -r "$HERE/icons/Redacted" "$D/icons/"
cp -r "$HERE/plasma/look-and-feel/scorn.redacted" "$D/plasma/look-and-feel/"
install -Dm644 "$HERE/assets/lockscreen.png" "$D/wallpapers/redacted/lockscreen.png"
install -Dm644 "$HERE/assets/background.png" "$D/wallpapers/redacted/background.png"
cp "$HERE/terminal/Redacted.colorscheme" "$HERE/terminal/Redacted.profile" "$D/konsole/"
cp "$HERE/terminal/redacted-kitty.conf" "$C/kitty/redacted.conf"
gtk-update-icon-cache -q -f -t "$D/icons/Redacted" 2>/dev/null || true

[[ ${1:-} == --install ]] && { echo "Files installed; nothing switched."; exit 0; }

# back up only the pre-Redacted state, so --revert always returns to it
if [[ $(kreadconfig6 --file kdeglobals --group General --key ColorScheme) != Redacted ]]; then
    stamp=$BK/$(date +%Y%m%d-%H%M%S)
    echo "==> Backing up current configs to $stamp"
    for f in "${FILES[@]}"; do
        if [[ -f $C/$f ]]; then
            install -Dm644 "$C/$f" "$stamp/$f"
        else
            install -Dm644 /dev/null "$stamp/.absent/$f"
        fi
    done
else
    echo "==> Redacted already active; keeping the existing backup in $BK"
fi

echo "==> Applying"
plasma-apply-colorscheme Redacted
plasma-apply-desktoptheme default >/dev/null 2>&1 || true
plasma-apply-desktoptheme Redacted
/usr/lib/plasma-changeicons Redacted
kwriteconfig6 --file kdeglobals --group KDE --key widgetStyle kvantum
kwriteconfig6 --file Kvantum/kvantum.kvconfig --group General --key theme Redacted
kwriteconfig6 --file kwinrc --group org.kde.kdecoration2 --key library org.kde.breeze
kwriteconfig6 --file kwinrc --group org.kde.kdecoration2 --key theme Breeze
qdbus6 org.kde.KWin /KWin reconfigure >/dev/null 2>&1 || true
kwriteconfig6 --file kwinrc --group org.kde.kdecoration2 --key library org.kde.kwin.aurorae
kwriteconfig6 --file kwinrc --group org.kde.kdecoration2 --key theme __aurorae__svg__Redacted
kwriteconfig6 --file ksplashrc --group KSplash --key Theme scorn.redacted
kwriteconfig6 --file ksplashrc --group KSplash --key Engine KSplashQML
# lock screen: the face with scanlines baked in
kwriteconfig6 --file kscreenlockerrc --group Greeter --key WallpaperPlugin org.kde.image
kwriteconfig6 --file kscreenlockerrc --group Greeter --group Wallpaper --group org.kde.image --group General \
    --key Image "file://$D/wallpapers/redacted/lockscreen.png"
# terminals: Konsole default profile + kitty include (previous include is commented, not deleted)
kwriteconfig6 --file konsolerc --group "Desktop Entry" --key DefaultProfile Redacted.profile
if [[ -f $C/kitty/kitty.conf ]] && ! grep -q '^include redacted.conf' "$C/kitty/kitty.conf"; then
    sed -i 's/^include \(.*\)$/# include \1/' "$C/kitty/kitty.conf"
    printf '\n# Redacted theme\ninclude redacted.conf\n' >> "$C/kitty/kitty.conf"
fi
reconfigure
echo
echo "Redacted applied. Log out and back in once so every running app picks up Kvantum and the new splash."
echo "Login screen + boot splash:  sudo bash $HERE/install.sh"
echo "Undo:                        bash $HERE/apply.sh --revert"
