# Redacted

A blood-dubbed VHS look for KDE Plasma 6, built around a crimson-lit face on near-black:
blood-black surfaces, faint scanlines and tape grain, and a slight crimson glow on whatever has focus.
It is the whole desktop, from the boot splash and login screen down to the terminal colours,
all generated from one palette.

![Redacted desktop](screenshots/desktop.png)

| | |
|---|---|
| ![login](screenshots/sddm.png) | ![boot](screenshots/plymouth.png) |
| SDDM login: VCR on-screen display, tracking band, tape tears | Plymouth boot: tape-block progress, tape counter |
| ![splash](screenshots/splash.png) | ![decoration](screenshots/decoration.png) |
| Plasma splash: rewind → play | Aurorae decoration: scanline title, crimson glow |

## Components

| piece | repo | KDE Store category |
|---|---|---|
| SDDM login | [redacted-sddm](https://github.com/numbpill3d/redacted-sddm) | SDDM Login Themes |
| Plymouth boot splash | [redacted-plymouth](https://github.com/numbpill3d/redacted-plymouth) | Plymouth Themes |
| Global theme + splash screen | [redacted-global](https://github.com/numbpill3d/redacted-global) | Global Themes (Plasma 6) |
| Plasma style (panel, popups) | [redacted-plasma](https://github.com/numbpill3d/redacted-plasma) | Plasma Themes |
| Aurorae window decoration | [redacted-aurorae](https://github.com/numbpill3d/redacted-aurorae) | Aurorae Themes |
| Colour scheme | [redacted-colors](https://github.com/numbpill3d/redacted-colors) | Plasma Color Schemes |
| Kvantum widget style | [redacted-kvantum](https://github.com/numbpill3d/redacted-kvantum) | Kvantum |
| Icons (over Tela circle dark) | [redacted-icons](https://github.com/numbpill3d/redacted-icons) | Full Icon Themes |
| Konsole + kitty colours | [redacted-konsole](https://github.com/numbpill3d/redacted-konsole) | Konsole color schemes |

This repo holds the sources and the generators (`tools/build_*.py`). The piece repos are
assembled from it by `tools/make-release.py`.

## Use
    bash ~/redacted/apply.sh            # install + switch (backs up configs to backup/)
    bash ~/redacted/apply.sh --revert   # restore the last backup
    sudo bash ~/redacted/install.sh     # SDDM + Plymouth (dracut-rebuild)
    sudo bash ~/redacted/install.sh --revert

## Rebuild after editing palette.py
    cd ~/redacted
    python3 tools/build_textures.py && python3 tools/build_colors.py && python3 tools/build_kvantum.py
    python3 tools/build_plasma.py && python3 tools/build_aurorae.py && python3 tools/build_icons.py
    python3 tools/build_plymouth.py
    QT_QPA_PLATFORM=offscreen python3 tools/make-shots.py screenshots && python3 tools/make-release.py
    # SDDM/KSplash QML hard-code the palette at the top of each file

## Preview without installing
    QT_QPA_PLATFORM=offscreen qml6 tools/preview-harness.qml -- ~/redacted/sddm/redacted out.png scorn pass [fail]
    QT_QPA_PLATFORM=offscreen qml6 tools/preview-splash.qml -- plasma/look-and-feel/scorn.redacted/contents/splash/Splash.qml out.png 4
    sddm-greeter-qt6 --test-mode --theme ~/redacted/sddm/redacted

SDDM `theme.conf`: `glitches=false` stops the random tape tears; `tagline`, `channel` are editable.
Font: Terminess Nerd Font (OFL), bundled. Kvantum engine map from KvArcDark (Tsu Jan, GPL).

## Tags

`redacted` `kde` `plasma6` `dark` `vhs` `scanlines` `crimson` `red` `blood` `horror` `retro` `analog-horror` `glow` `sddm` `plymouth` `aurorae` `kvantum` `global-theme` `icon-theme` `konsole`

## Credits and licence

By splicer scorn (voidrane). GPL-3.0-or-later. The wallpaper is the author's own.
Credits for the bundled and adapted work:
- Terminess Nerd Font (SIL OFL 1.1), bundled.
- The Kvantum engine map is adapted from KvArcDark by Tsu Jan (GPL-3.0).
- The folder icons are recoloured from the Tela circle icon theme by Vince Liuice (GPL-3.0).
