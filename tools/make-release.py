#!/usr/bin/env python3
"""Assemble the publishable Redacted pieces.

For each piece this writes
  repos/<repo>/   a self-contained git working tree: theme files at the root,
                  README.md (screenshots, description, tags), LICENSE, install.sh, screenshots/
  <docs>/<repo>/  the KDE Store upload: <repo>.tar.gz, screenshots/, STORE-LISTING.txt

    bash tools/make-shots.sh && python3 tools/make-release.py [docs-dir]
"""
import shutil, subprocess, sys, tarfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SHOTS = ROOT / "screenshots"
DOCS = Path(sys.argv[1]) if len(sys.argv) > 1 else Path.home() / "Documents" / "Redacted Release"
REPOS = ROOT / "repos"
GPL = Path("/usr/share/licenses/spdx/GPL-3.0-or-later.txt")
GH = "https://github.com/numbpill3d"
VERSION = "1.0"
HUB = "redacted-kde"   # numbpill3d/redacted is an older, unrelated (archived) repo

BLURB = ("Redacted is a monochrome-black look for KDE Plasma 6 about obfuscation and censorship. Every colour is a neutral grey, "
         "and the accents sit only a few levels above black: almost imperceptible, but just perceptible. The motifs are static, "
         "mosaic pixelation, black censor bars and a dissociated double.")
BASE_TAGS = ["redacted", "kde", "plasma6", "dark", "black", "monochrome", "grayscale", "minimal", "censored", "glitch", "static", "pixel"]
CONFIRM = "  (check this name against the store's category list when uploading)"

PIECES = {}


def piece(repo, **kw):
    kw.setdefault("files", None); kw.setdefault("config", ""); kw.setdefault("credit_extra", "")
    kw.setdefault("category_note", "")
    PIECES[repo] = kw


DEPARTURE = "\nPixel font: Departure Mono by Helena Zhang (SIL OFL 1.1)."
TERMINESS = "\nLogin font: Terminess Nerd Font (Terminus, SIL OFL 1.1), bundled with its licence."
SHADER = "\nShader preamble from Burn-My-Windows by Simon Schneegans (GPL-3.0-or-later)."

# ---- pieces -------------------------------------------------------------------
piece("redacted-global",
      short="Global theme + splash screen", title="Redacted — Global Theme (Plasma 6)", category="Global Themes (Plasma 6)",
      src=ROOT / "plasma/look-and-feel/scorn.redacted", tar_top="scorn.redacted",
      shots={"desktop.jpg": "desktop.png", "splash.jpg": "splash.png", "splash-resolved.jpg": "splash-resolved.png"},
      tags=["global-theme", "look-and-feel", "splash-screen", "ksplash", "plasma-6"],
      summary="The Redacted global theme. It switches Plasma to the whole monochrome-black suite at once and ships the censored-face splash screen.",
      features="""- **Splash screen:** a grey face under a coarse mosaic that resolves one stage at a time as Plasma starts. The name unscrambles out of glyph noise, and a strip of censor blocks shows progress. A censor bar stays across the eyes.
- **Defaults:** sets the colour scheme, Plasma style, icons, Kvantum widget style, Aurorae window decoration, splash and wallpaper to Redacted.
- **No panel layout:** it ships none, so applying it never rearranges your panels or widgets.""",
      requires="Plasma 6. Install the other Redacted pieces first (colour scheme, Plasma style, Aurorae, icons, Kvantum). The global theme falls back to Breeze for anything missing. Kvantum needs `kvantum` installed.",
      install_store="System Settings → Colors & Themes → Global Theme → Install from File, or extract it to `~/.local/share/plasma/look-and-feel/`. To use only the splash, pick it under Colors & Themes → Splash Screen.",
      install_sh="""DST=${XDG_DATA_HOME:-$HOME/.local/share}/plasma/look-and-feel/scorn.redacted
rm -rf "$DST"; mkdir -p "$DST"
cp -r "$HERE"/{metadata.json,contents} "$DST"/
echo "Installed. Apply: plasma-apply-lookandfeel -a scorn.redacted   (splash only: kwriteconfig6 --file ksplashrc --group KSplash --key Theme scorn.redacted)" """,
      credit_extra=SHADER)

piece("redacted-plasma",
      short="Plasma style (panel, popups)", title="Redacted — Plasma Style", category="Plasma Themes",
      src=ROOT / "plasma/desktoptheme/Redacted", tar_top="Redacted",
      shots={"panel.jpg": "panel.png", "desktop.jpg": "desktop.png"},
      tags=["plasma-style", "desktoptheme", "panel", "plasma-theme", "translucent"],
      summary="Black for the Plasma panel, popups and tooltips: faint grain, a censor-pixel mosaic and a stepped seam a few levels above black.",
      features="""- Panel, popups and dialogs, tooltips and widget backgrounds in near-black.
- Faint grain and a sparse censor-pixel mosaic, tiled 1:1 so they never smear at any panel size.
- A stepped seam along the edge, a breath lighter than black.
- Translucent variants with blur, plus solid variants for when compositing is off.
- Buttons, sliders and task highlights follow your colour scheme, so pair it with the Redacted colours.""",
      requires="Plasma 6.",
      install_store="System Settings → Colors & Themes → Plasma Style → Install from File, or extract it to `~/.local/share/plasma/desktoptheme/`.",
      install_sh="""DST=${XDG_DATA_HOME:-$HOME/.local/share}/plasma/desktoptheme/Redacted
rm -rf "$DST"; mkdir -p "$DST"
cp -r "$HERE"/{metadata.json,plasmarc,widgets,dialogs,solid,translucent} "$DST"/
plasma-apply-desktoptheme Redacted""")

piece("redacted-aurorae",
      short="Aurorae window decoration", title="Redacted — Aurorae Window Decoration", category="Aurorae Themes",
      src=ROOT / "aurorae/Redacted", tar_top="Redacted",
      shots={"decoration.jpg": "decoration.png", "buttons.jpg": "buttons.png", "desktop.jpg": "desktop.png"},
      tags=["aurorae", "window-decoration", "kwin", "titlebar", "pixel-art"],
      summary="A black window frame like a censored file: a scanlined title bar over a dithered seam of censor pixels, measurement ticks, crop marks at the corners. Unfocused windows get a censor bar through the title.",
      features="""- **Title bar:** faint grain and scanlines. The seam under it is made of 2 px censor pixels, ordered-dithered from dense to sparse.
- **Ruler:** measurement ticks hang off the top hairline, long every 48 px and short every 12.
- **Crop marks:** print crop marks sit in the shadow just outside each corner, as if the window had been cut out of a file. The active window adds a registration pip.
- **Unfocused windows:** a black censor bar runs through the title bar, and the title text sits on it.
- **Buttons:** pixel-stepped plates that light up with a dithered mosaic rim. On hover, the close ✕ gets struck out by a censor bar. The window-menu button is a censor block.
- **Tiled borders:** every border tiles at its natural size, so no detail stretches or smears at any window size.
- Centred title, 3 px borders, square corners.""",
      requires="KWin (Plasma 6) with Aurorae.",
      install_store="System Settings → Colors & Themes → Window Decorations → Install from File, or extract it to `~/.local/share/aurorae/themes/`.",
      install_sh="""DST=${XDG_DATA_HOME:-$HOME/.local/share}/aurorae/themes/Redacted
rm -rf "$DST"; mkdir -p "$DST"
cp "$HERE"/*.svg "$HERE"/Redactedrc "$HERE"/metadata.desktop "$DST"/
kwriteconfig6 --file kwinrc --group org.kde.kdecoration2 --key library org.kde.kwin.aurorae
kwriteconfig6 --file kwinrc --group org.kde.kdecoration2 --key theme __aurorae__svg__Redacted
qdbus6 org.kde.KWin /KWin reconfigure 2>/dev/null || true""")

piece("redacted-colors",
      short="Colour scheme", title="Redacted — Colour Scheme", category="Plasma Color Schemes",
      src=ROOT / "colors", tar_top="redacted-colors", files=["Redacted.colors"],
      shots={"palette.jpg": "colors.png", "desktop.jpg": "desktop.png"},
      tags=["color-scheme", "colour-scheme", "dark-theme", "kdeglobals", "black-theme"],
      summary="A monochrome-black KDE colour scheme. Every role is a neutral grey, the accent sits seven levels above the surface, and a selection reads by its text brightening.",
      features="""- Surfaces between `#020202` and `#0f0f0f`. Window `#0a0a0a`, views `#080808`, headers `#0c0c0c`.
- The focus and hover accent is `#131313`: almost imperceptible, but just perceptible.
- Text is `#969696`. Selected and hovered text brightens to `#d6d6d6`, and that is how a selection reads.
- Negative, neutral and positive are brightness steps, not hues, so nothing ever picks up a tint.
- Titlebar colours are set too, for Breeze decorations.""",
      requires="Plasma 5 or 6.",
      install_store="System Settings → Colors & Themes → Colors → Install from File, or copy it to `~/.local/share/color-schemes/`.",
      install_sh="""install -Dm644 "$HERE/Redacted.colors" "${XDG_DATA_HOME:-$HOME/.local/share}/color-schemes/Redacted.colors"
plasma-apply-colorscheme Redacted""")

piece("redacted-kvantum",
      short="Kvantum widget style", title="Redacted — Kvantum Theme", category="Kvantum",
      src=ROOT / "kvantum/Redacted", tar_top="Redacted",
      shots={"widgets.jpg": "gallery.png", "desktop.jpg": "desktop.png"},
      tags=["kvantum", "qt-style", "widget-style", "qt6", "qt5"],
      summary="A Kvantum widget style in monochrome black: recessed fields, grey sliders and checks, and selections that read by brightness rather than colour.",
      features="""- Built on KvArcDark's engine map. The greys are remapped onto a near-black ramp, and Arc's blue becomes grey.
- Text fields sit recessed, darker than the buttons.
- Sliders, checks, progress bars and focus rings are a few grey levels above their surface.
- Blurred popups. Matches the Redacted colour scheme.""",
      requires="Kvantum (`kvantum` package), with the widget style set to kvantum.",
      install_store="Extract it to `~/.config/Kvantum/`, select **Redacted** in Kvantum Manager, then set the Application Style to kvantum.",
      install_sh="""DST=${XDG_CONFIG_HOME:-$HOME/.config}/Kvantum/Redacted
rm -rf "$DST"; mkdir -p "$DST"
cp "$HERE"/Redacted.kvconfig "$HERE"/Redacted.svg "$DST"/
kwriteconfig6 --file Kvantum/kvantum.kvconfig --group General --key theme Redacted
kwriteconfig6 --file kdeglobals --group KDE --key widgetStyle kvantum
echo "Restart apps to see it." """,
      credit_extra="\nEngine map adapted from KvArcDark by Tsu Jan (Kvantum, GPL-3.0).")

piece("redacted-icons",
      short="Icon theme", title="Redacted — Icons", category="Full Icon Themes",
      src=ROOT / "icons/Redacted", tar_top="Redacted",
      shots={"icons.jpg": "icons.png", "desktop.jpg": "desktop.png"},
      tags=["icon-theme", "icons", "folders", "tela", "grey-folders"],
      summary="Charcoal folder and places icons and a censored-face launcher icon, layered over Tela circle dark.",
      features="""- Every folder and places icon (home, downloads, music, git, trash and the rest) is recoloured to charcoal with pale grey glyphs.
- The app-launcher icon is a static-filled disc under a censor bar, used for every `start-here` and `distributor-logo` name, symbolic ones included.
- Every other icon is inherited from **Tela circle dark**, then breeze-dark.""",
      requires="[Tela circle icon theme](https://github.com/vinceliuice/Tela-circle-icon-theme), dark variant (`Tela-circle-dark`), installed alongside.",
      install_store="Install Tela-circle-dark first. Then extract this to `~/.local/share/icons/` and pick **Redacted** in System Settings → Colors & Themes → Icons.",
      install_sh="""DST=${XDG_DATA_HOME:-$HOME/.local/share}/icons/Redacted
rm -rf "$DST"; mkdir -p "$DST"
cp -a "$HERE"/index.theme "$HERE"/scalable "$HERE"/scalable@2x "$HERE"/16 "$HERE"/16@2x "$HERE"/22 "$HERE"/22@2x "$HERE"/24 "$HERE"/24@2x "$HERE"/symbolic "$DST"/
/usr/lib/plasma-changeicons Redacted 2>/dev/null || echo "Pick Redacted in System Settings > Icons." """,
      credit_extra="\nFolder artwork recoloured from Tela circle icon theme by Vince Liuice (GPL-3.0).")

piece("redacted-konsole",
      short="Konsole + kitty colours", title="Redacted — Konsole & kitty Colours", category="Konsole color schemes",
      src=ROOT / "terminal", tar_top="redacted-konsole",
      files=["Redacted.colorscheme", "Redacted.profile", "redacted-kitty.conf"],
      shots={"terminal.jpg": "terminal.png", "desktop.jpg": "desktop.png"},
      tags=["konsole", "kitty", "terminal", "colorscheme", "terminal-theme"],
      summary="Monochrome-black terminal colours for Konsole and kitty: 16 colours that are all greys, tuned so ls, git and prompts still separate.",
      features="""- Near-black background, grey text, and a grey I-beam cursor.
- All 16 colours are neutral greys at distinct brightness steps, so ls colours, git diffs and prompts still read.
- A Konsole profile with Terminess, a slight translucency and blur, and roomy margins.
- A kitty theme with matching tab and border colours.""",
      requires="Konsole and/or kitty. The profile uses Terminess Nerd Font if it is installed.",
      install_store="Copy `Redacted.colorscheme` and `Redacted.profile` to `~/.local/share/konsole/`, then pick the profile in Konsole. For kitty, add `include redacted-kitty.conf` to kitty.conf.",
      install_sh="""K=${XDG_DATA_HOME:-$HOME/.local/share}/konsole; mkdir -p "$K"
cp "$HERE"/Redacted.colorscheme "$HERE"/Redacted.profile "$K"/
C=${XDG_CONFIG_HOME:-$HOME/.config}/kitty; mkdir -p "$C"; cp "$HERE"/redacted-kitty.conf "$C"/
echo "Konsole: Settings > Switch Profile > Redacted.   kitty: add 'include redacted-kitty.conf' to kitty.conf" """)

piece("redacted-sddm",
      short="SDDM login", title="Redacted — SDDM Login", category="SDDM Login Themes",
      src=ROOT / "sddm/redacted", tar_top="redacted",
      shots={"login.jpg": "sddm.png", "login-error.jpg": "sddm-error.png"},
      tags=["sddm", "sddm-theme", "login-screen", "qt6", "qml", "shader"],
      summary="An SDDM (Qt6) login like a censored file: the face under drifting mosaic and static behind a black panel. A wrong password knocks the censor bar off the eyes.",
      features="""- The animated Redacted scene runs behind the login: drifting mosaic, a censor bar that slips during glitch bursts, a dissociated double, torn rows and rolling static. It is one GPU shader at 12 fps.
- A `[REDACTED]` header with a file number, and the time and date top right.
- A black login panel. The password shows as censor blocks.
- A wrong password flips the header to `DENIED`, knocks the bar off the eyes for a moment and shakes the panel.
- Transport-style power controls.""",
      requires="SDDM with the Qt6 greeter (`sddm-greeter-qt6`) and a GPU with OpenGL. The fonts are bundled.",
      install_store="Extract it to `/usr/share/sddm/themes/` and pick **Redacted** in System Settings → Colors & Themes → Login Screen (SDDM).",
      install_sh="""DST=/usr/share/sddm/themes/redacted
[[ $EUID -eq 0 ]] || { echo "run with sudo: sudo ./install.sh" >&2; exit 1; }
rm -rf "$DST"; mkdir -p "$DST"
cp -r "$HERE"/{Main.qml,RedactedScene.qml,metadata.desktop,theme.conf,assets,art,fonts,preview.jpg} "$DST"/
chmod -R a+rX "$DST"
found=0
for f in /etc/sddm.conf /etc/sddm.conf.d/*.conf; do
    if [[ -f $f ]] && grep -q '^Current=' "$f"; then sed -i 's/^Current=.*/Current=redacted/' "$f"; found=1; fi
done
(( found )) || { mkdir -p /etc/sddm.conf.d; printf '[Theme]\\nCurrent=redacted\\n' > /etc/sddm.conf.d/redacted.conf; }
echo "Installed. Test without logging out: sddm-greeter-qt6 --test-mode --theme $DST" """,
      credit_extra=TERMINESS + SHADER)

piece("redacted-plymouth",
      short="Plymouth boot splash", title="Redacted — Plymouth Boot Splash", category="Plymouth Themes",
      src=ROOT / "plymouth/redacted", tar_top="redacted",
      shots={"boot.jpg": "plymouth.png", "password.jpg": "plymouth-password.png", "shutdown.jpg": "plymouth-shutdown.png"},
      tags=["plymouth", "plymouth-theme", "boot-splash", "bootscreen", "luks"],
      summary="A boot splash of the censored face under live static, with censor-block progress and a redacted disk-unlock prompt.",
      features="""- The face behind a censor bar, live static, and a tracking band that rolls down the screen.
- A `[REDACTED]` header with a file number, and an elapsed-time counter that ticks every second.
- Boot progress fills a strip of censor blocks under **REDACTED**.
- Separate shutdown and reboot captions.
- A disk-unlock prompt (LUKS) with censor-block bullets.
- Every word is pre-rendered, so the initramfs needs no fonts. Scales by screen height.""",
      requires="Plymouth with the `script` plugin (standard).",
      install_store="Extract it to `/usr/share/plymouth/themes/`, then run `sudo plymouth-set-default-theme -R redacted` (on dracut systems: `sudo plymouth-set-default-theme redacted && sudo dracut -f`).",
      install_sh="""DST=/usr/share/plymouth/themes/redacted
[[ $EUID -eq 0 ]] || { echo "run with sudo: sudo ./install.sh" >&2; exit 1; }
rm -rf "$DST"; mkdir -p "$DST"
cp "$HERE"/*.png "$HERE"/redacted.plymouth "$HERE"/redacted.script "$DST"/
chmod -R a+rX "$DST"
if command -v dracut >/dev/null && ! command -v mkinitcpio >/dev/null; then
    plymouth-set-default-theme redacted
    if command -v dracut-rebuild >/dev/null; then dracut-rebuild; else dracut -f; fi
else
    plymouth-set-default-theme -R redacted
fi
echo "Installed; you will see it at next boot." """,
      config="Make sure `splash` is on the kernel command line.")

piece("redacted-wallpaper",
      short="Animated wallpaper (desktop + lock)", title="Redacted — Animated Wallpaper", category="Wallpaper Plugins" + CONFIRM,
      src=ROOT / "plasma/wallpapers/scorn.redacted", tar_top="scorn.redacted",
      shots={"wallpaper.jpg": "wallpaper.png", "desktop.jpg": "desktop.png"},
      tags=["wallpaper-plugin", "animated-wallpaper", "live-wallpaper", "shader", "lock-screen"],
      summary="A live wallpaper for the desktop and lock screen: a grey face under drifting mosaic, a censor bar that slips during glitch bursts, a dissociated double, and a document whose lines draw back and re-redact.",
      features="""- One GPU fragment shader, capped at 12 fps; it stops whenever Plasma hides the wallpaper (screen off or locked away).
- **Face:** a grey face under mosaic blocks that drift and resolve. A censor bar across the eyes slips during glitch bursts.
- **Double:** a faint, offset copy of the face that comes and goes.
- **Signal:** torn rows and rolling static.
- **Document:** a page of text on the right whose censor bars draw back, show a line for a moment, and redact it again.
- Works as the lock screen wallpaper too.""",
      requires="Plasma 6 and a GPU with OpenGL. If you want zero GPU use, take the still version, **redacted-image-wallpaper**.",
      install_store="Extract it to `~/.local/share/plasma/wallpapers/`. Then right-click the desktop → Desktop and Wallpaper → Wallpaper type → **Redacted (animated)**.",
      install_sh="""DST=${XDG_DATA_HOME:-$HOME/.local/share}/plasma/wallpapers/scorn.redacted
rm -rf "$DST"; mkdir -p "$DST"
cp -r "$HERE"/{metadata.json,contents} "$DST"/
qdbus6 org.kde.plasmashell /PlasmaShell org.kde.PlasmaShell.evaluateScript 'var d=desktops(); for (var i=0;i<d.length;i++) d[i].wallpaperPlugin="scorn.redacted";' 2>/dev/null \\
  || echo "Pick Redacted (animated) under Desktop and Wallpaper > Wallpaper type." """,
      credit_extra=SHADER + DEPARTURE + "\nThe face is the author's own artwork.")

piece("redacted-image-wallpaper",
      short="Still wallpaper (1080p–4K)", title="Redacted — Wallpaper (still)", category="Wallpapers KDE Plasma" + CONFIRM,
      src=ROOT / "plasma/image-wallpaper/Redacted", tar_top="Redacted",
      shots={"wallpaper.jpg": "wallpaper.png"},
      tags=["wallpaper", "4k", "black-wallpaper", "face", "dark-wallpaper"],
      summary="The still Redacted wallpaper: a grey face behind a censor bar on black, in 1920×1080, 2560×1440 and 3840×2160.",
      features="""- A grey face behind a censor bar and a scatter of mosaic, on black.
- Three sizes: 1920×1080, 2560×1440 and 3840×2160.
- Uses no GPU at all. This is the still counterpart to the animated **redacted-wallpaper**.""",
      requires="Any Plasma version.",
      install_store="Extract it to `~/.local/share/wallpapers/`, then pick **Redacted** under Desktop and Wallpaper.",
      install_sh="""DST=${XDG_DATA_HOME:-$HOME/.local/share}/wallpapers/Redacted
rm -rf "$DST"; mkdir -p "$DST"
cp -r "$HERE"/{metadata.json,contents} "$DST"/
plasma-apply-wallpaperimage "$DST" 2>/dev/null || echo "Pick Redacted under Desktop and Wallpaper." """,
      credit_extra="\nThe face is the author's own artwork.")

piece("redacted-censor",
      short="KWin open/close effect", title="Redacted — Censor (KWin open/close effect)", category="KWin Effects" + CONFIRM,
      src=ROOT / "kwin/redacted_censor", tar_top="redacted_censor",
      shots={"censor.gif": "censor.gif"},
      tags=["kwin-effect", "kwin", "window-animation", "open-close", "shader"],
      summary="A window open/close animation. Windows arrive as a grey mosaic full of static under sliding censor bars and resolve into focus. On close they pixelate, are censored and vanish.",
      features="""- **Open:** power-of-two mosaic blocks shrink away, 24 px cells pop in out of order, torn rows slide sideways early on, and three black censor bars slide off alternately left and right.
- **Close:** the same, in reverse.
- The window is drained to grey while it is still mostly mosaic, so colour arrives last.
- A GLSL fragment shader on KWin's scripted-effect API. Durations and colours are configurable.""",
      requires="KWin 6 (Plasma 6) with OpenGL compositing.",
      install_store="Extract it to `~/.local/share/kwin/effects/`, then enable **Redacted Censor** in System Settings → Window Management → Desktop Effects. Turn off any other open/close animation first.",
      install_sh="""DST=${XDG_DATA_HOME:-$HOME/.local/share}/kwin/effects/redacted_censor
rm -rf "$DST"; mkdir -p "$DST"
cp -r "$HERE"/{metadata.json,contents} "$DST"/
for e in fade scale glide; do kwriteconfig6 --file kwinrc --group Plugins --key ${e}Enabled false; done
kwriteconfig6 --file kwinrc --group Plugins --key redacted_censorEnabled true
qdbus6 org.kde.KWin /KWin reconfigure 2>/dev/null || true
qdbus6 org.kde.KWin /Effects org.kde.kwin.Effects.loadEffect redacted_censor 2>/dev/null || true""",
      config="System Settings → Desktop Effects → Redacted Censor → configure: `OpenDuration` (380 ms), `CloseDuration` (300 ms), `Color` (static grey), `Ink` (bar black).",
      credit_extra=SHADER)

piece("redacted-static",
      short="KWin script: active window under review", title="Redacted — Static (KWin script)", category="KWin Scripts" + CONFIRM,
      src=ROOT / "kwin/redacted_static", tar_top="redacted_static",
      shots={"overlay.gif": "overlay.gif", "overlay.jpg": "overlay.png"},
      tags=["kwin-script", "kwin", "overlay", "focus-indicator", "qml"],
      summary="Puts the active window under review. Corner brackets lock onto it when it takes focus, a write head crawls its edge stamping censor bars that decay into mosaic, and a case-file tag censors its title.",
      features="""- **Lock-on:** when a window takes focus, four corner brackets snap onto it in hard steps, like a camera acquiring a subject. They blink once and cut out, then re-acquire every 24 s.
- **Sweep:** a write head crawls clockwise round the frame edge. Behind it, black censor bars are stamped onto the hairline. Each bar breaks into a few 3 px censor pixels and then disappears.
- **Case file:** above the top-left corner sits `FILE 0x....`, a hex number derived from the app. It scrambles while the brackets acquire, then settles. Next to it, the window title appears as censor bars, one per word.
- **Light:** one click-through overlay that redraws at most 10 times a second, and only while visible. It hides for maximised, fullscreen and non-normal windows.""",
      requires="KWin 6 (Plasma 6). The tag uses Departure Mono Nerd Font if it is installed; otherwise it falls back to the default mono font.",
      install_store="Extract it to `~/.local/share/kwin/scripts/`, then enable **Redacted Static** in System Settings → Window Management → KWin Scripts.",
      install_sh="""DST=${XDG_DATA_HOME:-$HOME/.local/share}/kwin/scripts/redacted_static
rm -rf "$DST"; mkdir -p "$DST"
cp -r "$HERE"/{metadata.json,contents} "$DST"/
kwriteconfig6 --file kwinrc --group Plugins --key redacted_staticEnabled true
qdbus6 org.kde.KWin /Scripting org.kde.kwin.Scripting.unloadScript redacted_static >/dev/null 2>&1 || true
qdbus6 org.kde.KWin /Scripting org.kde.kwin.Scripting.start >/dev/null 2>&1 || true""")

piece("redacted-clock",
      short="Clock plasmoid", title="Redacted — Clock (Plasma 6 widget)", category="Plasma 6 Applets" + CONFIRM,
      src=ROOT / "plasma/plasmoids/scorn.redacted.clock", tar_top="scorn.redacted.clock",
      shots={"clock.jpg": "clock.png", "panel.jpg": "panel.png"},
      tags=["plasmoid", "plasma-widget", "clock", "panel-widget", "shader"],
      summary="A redacted panel clock: the time sits under censor bars beside a square of live static. Hover to read it.",
      features="""- The time and date sit under two black bars that slide back while you hover.
- Beside them is a square of live static (a small GPU shader) with a censor bar across it.
- Every so often the signal slips and the bars jerk open for a moment on their own.
- The pixel font is bundled.""",
      requires="Plasma 6 and a GPU with OpenGL.",
      install_store="Install it from the widget explorer (Add Widgets → Get New Widgets → Install from local file), or extract it to `~/.local/share/plasma/plasmoids/`. Then add **Redacted Clock** to a panel.",
      install_sh="""kpackagetool6 -t Plasma/Applet -u "$HERE" 2>/dev/null || kpackagetool6 -t Plasma/Applet -i "$HERE"
echo "Add 'Redacted Clock' to a panel (right-click panel > Add Widgets)." """,
      credit_extra=DEPARTURE)


# ---- build --------------------------------------------------------------------
def shot(src, dst):
    if src.suffix == ".gif" or dst.suffix == ".gif":
        shutil.copy(src, dst)
    else:
        subprocess.run(["magick", str(src), "-quality", "90", str(dst)], check=True)


def suite_table(skip):
    rows = [f"| {p['short']} | [{r}]({GH}/{r}) |" for r, p in PIECES.items() if r != skip]
    return "## The rest of the suite\n\n| piece | repo |\n|---|---|\n" + "\n".join(rows) + \
           f"\n\nEverything at once, with the generators: [{HUB}]({GH}/{HUB}).\n"


def readme(repo, p):
    names = list(p["shots"])
    more = "\n\n".join(f"![{n.rsplit('.', 1)[0]}](screenshots/{n})" for n in names[1:])
    tags = " ".join(f"`{t}`" for t in BASE_TAGS + p["tags"])
    cfg = f"\n## Configuration\n\n{p['config']}\n" if p["config"] else ""
    sudo = "sudo " if "EUID" in p["install_sh"] else ""
    return f"""# {p['title']}

{p['summary']}

![{names[0].rsplit('.', 1)[0]}](screenshots/{names[0]})

{BLURB}

## Features

{p['features']}

{more}

## Requirements

{p['requires']}

## Install

```bash
git clone {GH}/{repo}
cd {repo} && {sudo}./install.sh
```

Or from the KDE Store: {p['install_store']}
{cfg}
{suite_table(repo)}
## Tags

{tags}

## Credits and licence

By splicer scorn (voidrane). GPL-3.0-or-later.{p['credit_extra']}
"""


def store_listing(repo, p):
    return f"""NAME: {p['title']}
CATEGORY: {p['category']}
VERSION: {VERSION}
LICENSE: GPL-3.0-or-later
SOURCE: {GH}/{repo}
UPLOAD: {repo}.tar.gz
SCREENSHOTS (in order): {", ".join("screenshots/" + n for n in p["shots"])}
TAGS: {", ".join(BASE_TAGS + p["tags"])}

SUMMARY:
{p['summary']}

DESCRIPTION:
{p['summary']}

{BLURB}

{p['features']}

Requirements: {p['requires']}

Install: {p['install_store']}

Part of the Redacted suite: global theme + splash, Plasma style, Aurorae, colours, Kvantum, icons, Konsole/kitty, SDDM, Plymouth, animated and still wallpaper, the Censor open/close effect, the Static KWin script and the Redacted Clock. Source for every piece: {GH}/{HUB}
"""


def main():
    REPOS.mkdir(exist_ok=True)
    DOCS.mkdir(parents=True, exist_ok=True)
    for repo, p in PIECES.items():
        d = REPOS / repo
        if d.exists():
            for c in d.iterdir():
                if c.name != ".git":
                    shutil.rmtree(c) if c.is_dir() and not c.is_symlink() else c.unlink()
        d.mkdir(exist_ok=True)
        if p["files"]:
            for f in p["files"]:
                shutil.copy2(p["src"] / f, d / f)
        else:
            for c in p["src"].iterdir():
                if c.name == "__pycache__":
                    continue
                if c.is_dir() and not c.is_symlink():
                    shutil.copytree(c, d / c.name, symlinks=True)
                else:
                    shutil.copy2(c, d / c.name, follow_symlinks=False)
        (d / "screenshots").mkdir(exist_ok=True)
        for n, s in p["shots"].items():
            shot(SHOTS / s, d / "screenshots" / n)
        (d / "README.md").write_text(readme(repo, p))
        shutil.copy(GPL, d / "LICENSE")
        sh = d / "install.sh"
        sh.write_text(f"#!/usr/bin/env bash\n# {p['title']} — install.  ./install.sh\nset -euo pipefail\n"
                      f"HERE=$(cd \"$(dirname \"${{BASH_SOURCE[0]}}\")\" && pwd)\n{p['install_sh'].strip()}\n")
        sh.chmod(0o755)

        k = DOCS / repo
        if k.exists():
            shutil.rmtree(k)
        (k / "screenshots").mkdir(parents=True)
        for n in p["shots"]:
            shutil.copy(d / "screenshots" / n, k / "screenshots" / n)
        with tarfile.open(k / f"{repo}.tar.gz", "w:gz") as t:
            if p["files"]:
                for f in p["files"]:
                    t.add(p["src"] / f, arcname=f"{p['tar_top']}/{f}")
            else:
                t.add(p["src"], arcname=p["tar_top"], filter=lambda i: None if "__pycache__" in i.name else i)
        (k / "STORE-LISTING.txt").write_text(store_listing(repo, p))
        print(f"{repo:26s} -> repos/{repo}, {k}")

    (DOCS / "README.txt").write_text(
        "Redacted — KDE Store upload kit\n\nOne folder per component. Each folder holds three things:\n"
        "  - the upload tarball\n  - screenshots/ (upload them in the order listed)\n"
        "  - STORE-LISTING.txt (name, category, tags and description, ready to paste)\n\n"
        "Categories marked 'check this name' are the closest store category I know of; confirm them in the store's list.\n\n"
        + "\n".join(f"  {r:26s} {p['category'].replace(CONFIRM, ' *'):30s} {r}.tar.gz" for r, p in PIECES.items())
        + f"\n\nSource repos: {GH}/<folder name>   (hub with everything: {GH}/{HUB})\n")
    shutil.copy(SHOTS / "desktop.png", DOCS / "redacted-desktop.png")


if __name__ == "__main__":
    main()
