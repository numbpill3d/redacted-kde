# Redacted

A monochrome-black KDE Plasma 6 suite. Every colour is a neutral grey, and the
accents sit only a few levels above black (`ACCENT_STEP` in `palette.py`).
The panel, splash, lock screen, login and boot splash carry the overtone:
static, pixelation, censor bars, obfuscation and dissociation.

## Pieces

| piece | what it does |
|---|---|
| colour scheme, Kvantum, Plasma style, Aurorae, icons, Konsole/kitty | monochrome black; the panel has grain, a censor-pixel mosaic and a stepped seam |
| `scorn.redacted` wallpaper (desktop + lock) | GPU shader at 12 fps: a grey face under drifting mosaic, a censor bar that slips during glitch bursts, a dissociated double, torn rows, rolling static; a document whose lines draw back and re-redact |
| `Redacted` image wallpaper | the still version, zero GPU |
| KSplash | the mosaic resolves stage by stage, the name unscrambles, censor-block progress |
| `redacted_censor` KWin effect | windows open as grey mosaic and static under sliding censor bars; close in reverse |
| `redacted_static` KWin script | the active window comes loose: a drifting 1 px double of its frame, censor bars, mosaic chunks and specks on its edge |
| `scorn.redacted.clock` plasmoid | the time under censor bars beside a square of live static; hover to read |
| SDDM `redacted` | the same scene behind a black panel; a wrong password knocks the bar off the eyes |
| Plymouth `redacted` | the censored face, censor-block progress |

## Use

    bash apply.sh            # install + switch (user level)
    bash apply.sh --revert   # back to the configs saved by the first apply
    sudo bash install.sh     # SDDM + Plymouth (dracut rebuild)

## Rebuild

    bash tools/build_all.sh && bash apply.sh    # every generator, scene staging, grey check

Accent strength is one knob, `ACCENT_STEP` in `palette.py` (levels above the surface):

    sed -i 's/^ACCENT_STEP = .*/ACCENT_STEP = 10/' palette.py && bash tools/build_all.sh && bash apply.sh

The SDDM and KSplash QML hard-code their greys, so the knob doesn't reach them.

Previews with real GPU shaders: `tools/nested-grab.sh` (headless nested KWin).
The KWin effect renders offline with `build/venv/bin/python tools/render-censor.py`.
Shader preamble from Burn-My-Windows (GPL-3.0-or-later). Wallpaper face: scorn's own.
