#!/usr/bin/env bash
# Redacted — user-level install + apply (no sudo).
#   bash ~/redacted/apply.sh            install everything and switch to it
#   bash ~/redacted/apply.sh --install  copy files only, change nothing
#   bash ~/redacted/apply.sh --revert   restore the configs saved by the first apply
# SDDM + Plymouth need root: sudo bash ~/redacted/install.sh
set -euo pipefail
HERE=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
C=${XDG_CONFIG_HOME:-$HOME/.config}
D=${XDG_DATA_HOME:-$HOME/.local/share}
BK=$HERE/backup
FILES=(kdeglobals kwinrc plasmarc ksplashrc kscreenlockerrc konsolerc Kvantum/kvantum.kvconfig kitty/kitty.conf
       plasma-org.kde.plasma.desktop-appletsrc plasmashellrc gtk-3.0/settings.ini gtk-4.0/settings.ini)
FONT_DIR=$D/fonts/DepartureMono
UI_FONT="DepartureMono Nerd Font,-1,11,5,400,0,0,0,0,0,0,0,0,0,0,1"
MONO_FONT="DepartureMono Nerd Font Mono,-1,11,5,400,0,0,0,0,0,0,0,0,0,0,1"
TITLE_FONT="DepartureMono Nerd Font,11,-1,5,400,0,0,0,0,0,0,0,0,0,0,1"

reconfigure() { qdbus6 org.kde.KWin /KWin reconfigure >/dev/null 2>&1 || true; }
shell_js() { qdbus6 org.kde.plasmashell /PlasmaShell org.kde.PlasmaShell.evaluateScript "$1" >/dev/null; }

if [[ ${1:-} == --revert ]]; then
    last=$(ls -1d "$BK"/* 2>/dev/null | head -1) || true   # oldest = pre-Redacted
    [[ -n ${last:-} ]] || { echo "no backup in $BK" >&2; exit 1; }
    echo "==> Restoring configs from $last"
    for f in "${FILES[@]}"; do
        if [[ -f $last/$f ]]; then install -Dm644 "$last/$f" "$C/$f"
        elif [[ -f $last/.absent/$f ]]; then rm -f "$C/$f"; fi
    done
    qdbus6 org.kde.KWin /Scripting org.kde.kwin.Scripting.unloadScript redacted_static >/dev/null 2>&1 || true
    qdbus6 org.kde.KWin /Effects org.kde.kwin.Effects.unloadEffect redacted_censor >/dev/null 2>&1 || true
    [[ -s $last/gtk-theme ]] && qdbus6 org.kde.GtkConfig /GtkConfig org.kde.GtkConfig.setGtkTheme "$(cat "$last/gtk-theme")" >/dev/null 2>&1 || true
    scheme=$(kreadconfig6 --file kdeglobals --group General --key ColorScheme)
    theme=$(kreadconfig6 --file plasmarc --group Theme --key name)
    icons=$(kreadconfig6 --file kdeglobals --group Icons --key Theme)
    plasma-apply-colorscheme Redacted >/dev/null 2>&1 || true
    plasma-apply-colorscheme "$scheme" || true
    plasma-apply-desktoptheme "$theme" || true
    /usr/lib/plasma-changeicons "$icons" || true
    reconfigure
    # effects listed in the restored kwinrc (e.g. the previous open/close animation)
    for e in $(sed -n '/^\[Plugins\]/,/^\[/p' "$C/kwinrc" | grep -oP '^\K[a-z0-9_]+(?=Enabled=true)'); do
        qdbus6 org.kde.KWin /Effects org.kde.kwin.Effects.loadEffect "$e" >/dev/null 2>&1 || true
    done
    qdbus6 org.kde.KWin /Scripting org.kde.kwin.Scripting.start >/dev/null 2>&1 || true
    # the panel + wallpaper live in plasmashell's own config: restart it to reread them
    systemctl --user restart plasma-plasmashell
    echo "Reverted. Theme files stay installed; log out and back in for every app to follow."
    exit 0
fi

echo "==> Installing Redacted files"
install -Dm644 "$HERE/colors/Redacted.colors" "$D/color-schemes/Redacted.colors"
rm -rf "$C/Kvantum/Redacted" "$D/plasma/desktoptheme/Redacted" "$D/aurorae/themes/Redacted" "$D/icons/Redacted" \
       "$D/plasma/look-and-feel/scorn.redacted" "$D/plasma/wallpapers/scorn.redacted" "$D/wallpapers/Redacted" \
       "$D/plasma/plasmoids/scorn.redacted.clock" "$D/kwin/effects/redacted_censor" "$D/kwin/scripts/redacted_static"
mkdir -p "$C/Kvantum" "$D/plasma/desktoptheme" "$D/aurorae/themes" "$D/icons" "$D/plasma/look-and-feel" "$D/wallpapers" \
         "$D/plasma/wallpapers" "$D/plasma/plasmoids" "$D/kwin/effects" "$D/kwin/scripts" "$D/konsole" "$C/kitty"
cp -r "$HERE/kvantum/Redacted" "$C/Kvantum/"
cp -r "$HERE/plasma/desktoptheme/Redacted" "$D/plasma/desktoptheme/"
cp -r "$HERE/aurorae/Redacted" "$D/aurorae/themes/"
cp -r "$HERE/icons/Redacted" "$D/icons/"
cp -r "$HERE/plasma/look-and-feel/scorn.redacted" "$D/plasma/look-and-feel/"
cp -r "$HERE/plasma/wallpapers/scorn.redacted" "$D/plasma/wallpapers/"
cp -r "$HERE/plasma/image-wallpaper/Redacted" "$D/wallpapers/"          # still version: zero GPU
cp -r "$HERE/plasma/plasmoids/scorn.redacted.clock" "$D/plasma/plasmoids/"
cp -r "$HERE/kwin/redacted_censor" "$D/kwin/effects/"
cp -r "$HERE/kwin/redacted_static" "$D/kwin/scripts/"
cp "$HERE/terminal/Redacted.colorscheme" "$HERE/terminal/Redacted.profile" "$D/konsole/"
cp "$HERE/terminal/redacted-kitty.conf" "$C/kitty/redacted.conf"
[[ -d $FONT_DIR ]] || echo "!! Departure Mono Nerd Font not found in $FONT_DIR (UI font falls back)"
gtk-update-icon-cache -q -f -t "$D/icons/Redacted" 2>/dev/null || true

[[ ${1:-} == --install ]] && { echo "Files installed; nothing switched."; exit 0; }

# back up only the pre-Redacted state, so --revert always returns to it
if [[ $(kreadconfig6 --file kdeglobals --group General --key ColorScheme) != Redacted ]]; then
    stamp=$BK/$(date +%Y%m%d-%H%M%S)
    echo "==> Backing up current configs to $stamp"
    for f in "${FILES[@]}"; do
        if [[ -f $C/$f ]]; then install -Dm644 "$C/$f" "$stamp/$f"
        else install -Dm644 /dev/null "$stamp/.absent/$f"; fi
    done
    gsettings get org.gnome.desktop.interface gtk-theme 2>/dev/null | tr -d "'" > "$stamp/gtk-theme" || true
else
    echo "==> Redacted already active; keeping the existing backup in $BK"
fi

echo "==> Applying"
# a custom or wallpaper-derived accent would override the near-black accent
kwriteconfig6 --file kdeglobals --group General --key AccentColor --delete
kwriteconfig6 --file kdeglobals --group General --key accentColorFromWallpaper false
plasma-apply-colorscheme Redacted
plasma-apply-desktoptheme Redacted
/usr/lib/plasma-changeicons Redacted
kwriteconfig6 --file kdeglobals --group KDE --key widgetStyle kvantum
qdbus6 org.kde.GtkConfig /GtkConfig org.kde.GtkConfig.setGtkTheme Breeze >/dev/null 2>&1 || true
kwriteconfig6 --file kdeglobals --group KDE --key LookAndFeelPackage scorn.redacted
kwriteconfig6 --file Kvantum/kvantum.kvconfig --group General --key theme Redacted
# fonts: the small pixel font everywhere, window titles included
for k in font menuFont toolBarFont smallestReadableFont; do
    kwriteconfig6 --file kdeglobals --group General --key $k "$UI_FONT"
done
kwriteconfig6 --file kdeglobals --group General --key fixed "$MONO_FONT"
kwriteconfig6 --file kdeglobals --group WM --key activeFont "$TITLE_FONT"
# decoration (switch away and back so KWin rereads the Aurorae theme)
kwriteconfig6 --file kwinrc --group org.kde.kdecoration2 --key library org.kde.breeze
kwriteconfig6 --file kwinrc --group org.kde.kdecoration2 --key theme Breeze
reconfigure
kwriteconfig6 --file kwinrc --group org.kde.kdecoration2 --key library org.kde.kwin.aurorae
kwriteconfig6 --file kwinrc --group org.kde.kdecoration2 --key theme __aurorae__svg__Redacted
# window open/close: the censor effect replaces every other open/close animation
for e in fade scale glide kwin6_effect_glide kinetic_scale arterial_incision xenoglyph_unfurl; do
    kwriteconfig6 --file kwinrc --group Plugins --key ${e}Enabled false
done
kwriteconfig6 --file kwinrc --group Plugins --key redacted_censorEnabled true
# the active window comes loose (a KWin script); Xenoglyph's runes go
kwriteconfig6 --file kwinrc --group Plugins --key xenoglyph_runesEnabled false
kwriteconfig6 --file kwinrc --group Plugins --key redacted_staticEnabled true
# splash + lock screen
kwriteconfig6 --file ksplashrc --group KSplash --key Theme scorn.redacted
kwriteconfig6 --file ksplashrc --group KSplash --key Engine KSplashQML
kwriteconfig6 --file kscreenlockerrc --group Greeter --key WallpaperPlugin scorn.redacted
# terminals: Konsole default profile + kitty include (previous include is commented, not deleted)
kwriteconfig6 --file konsolerc --group "Desktop Entry" --key DefaultProfile Redacted.profile
if [[ -f $C/kitty/kitty.conf ]] && ! grep -q '^include redacted.conf' "$C/kitty/kitty.conf"; then
    sed -i 's/^include \(.*\)$/# include \1/' "$C/kitty/kitty.conf"
    printf '\n# Redacted theme\ninclude redacted.conf\n' >> "$C/kitty/kitty.conf"
fi
reconfigure
qdbus6 org.kde.KWin /Effects org.kde.kwin.Effects.unloadEffect xenoglyph_unfurl >/dev/null 2>&1 || true
# KWin only rescans effects at startup; load the freshly installed one now
qdbus6 org.kde.KWin /Effects org.kde.kwin.Effects.loadEffect redacted_censor >/dev/null 2>&1 || true
qdbus6 org.kde.KWin /Scripting org.kde.kwin.Scripting.unloadScript xenoglyph_runes >/dev/null 2>&1 || true
qdbus6 org.kde.KWin /Scripting org.kde.kwin.Scripting.unloadScript redacted_static >/dev/null 2>&1 || true
qdbus6 org.kde.KWin /Scripting org.kde.kwin.Scripting.start >/dev/null 2>&1 || true

# desktop wallpaper; swap the Xenoglyph sigil in the panel for the redacted clock
shell_js 'var ds = desktops();
for (var i = 0; i < ds.length; i++) { ds[i].wallpaperPlugin = "scorn.redacted"; }
var ps = panels();
for (var p = 0; p < ps.length; p++) {
    var ws = ps[p].widgets();
    for (var j = 0; j < ws.length; j++) if (ws[j].type == "scorn.xenoglyph.sigil") ws[j].remove();
}
if (ps.length > 0) {
    var has = false, ws2 = ps[0].widgets();
    for (var k = 0; k < ws2.length; k++) if (ws2[k].type == "scorn.redacted.clock") has = true;
    if (!has) ps[0].addWidget("scorn.redacted.clock");
}' || echo "!! could not reach plasmashell; set the wallpaper by hand (Redacted (animated))"

# file pickers are long-lived services that keep the style they started with
systemctl --user restart plasma-xdg-desktop-portal-kde.service xdg-desktop-portal-gtk.service >/dev/null 2>&1 || true

echo
echo "Redacted applied. Close and reopen apps (or log out and back in once) so every app picks up Kvantum, the fonts and the new splash."
echo "Login screen + boot splash:  sudo bash $HERE/install.sh"
echo "Undo:                        bash $HERE/apply.sh --revert"
