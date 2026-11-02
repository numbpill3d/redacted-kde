#!/usr/bin/env python3
"""Stills for the README / KDE Store, composed from the raw desktop captures and
rendered with QtSvg (the renderer KDE uses). Called by tools/make-shots.sh:
    QT_QPA_PLATFORM=offscreen python3 tools/make-stills.py <screenshots> <scratch>"""
import shutil, sys
from pathlib import Path
from PIL import Image
from PyQt6.QtGui import QGuiApplication, QImage, QPainter, QColor, QFont, QFontDatabase
from PyQt6.QtSvg import QSvgRenderer
from PyQt6.QtCore import QRectF, Qt

R = Path(__file__).resolve().parent.parent
S, T = Path(sys.argv[1]), Path(sys.argv[2])
RAW = S / "raw"
app = QGuiApplication(sys.argv[:1])
FONT = "DepartureMono Nerd Font"
A = R / "aurorae/Redacted"
P, B, TT, C = 20, 3, 36, 48

shutil.copy(RAW / "desk.png", S / "desktop.png")
shutil.copy(RAW / "desk-empty.png", S / "wallpaper.png")

# panel: the bottom strip, both halves stacked, at 2x
d = Image.open(RAW / "desk.png").convert("RGB")
strip = d.crop((0, 1036, 1920, 1080))
l, r = strip.crop((0, 0, 700, 44)), strip.crop((1220, 0, 1920, 44))
pan = Image.new("RGB", (700, 96), (0, 0, 0)); pan.paste(l, (0, 0)); pan.paste(r, (0, 52))
pan.resize((1400, 192), Image.NEAREST).save(S / "panel.png")

# terminal: the Konsole window
d.crop((370, 95, 1920, 1036)).save(S / "terminal.png")

# the active-window overlay, as a GIF
fr = sorted((RAW / "static").glob("f*.png"))
gif = [Image.open(f).convert("RGB").crop((300, 60, 1920, 1060)).resize((810, 500), Image.LANCZOS) for f in fr]
gif[0].save(S / "overlay.gif", save_all=True, append_images=gif[1:], duration=330, loop=0, optimize=True)
gif[len(gif) // 2].save(S / "overlay.png")


def qimg(w, h, bg=(5, 5, 5)):
    im = QImage(w, h, QImage.Format.Format_ARGB32); im.fill(QColor(*bg)); return im


# window decoration: active over inactive, on the wallpaper
def window(p, r, x, y, w, h, pre, title):
    def part(n, rx, ry, rw, rh, clip=None):
        p.save()
        if clip: p.setClipRect(QRectF(*clip))
        r.render(p, f"{pre}-{n}", QRectF(rx, ry, rw, rh)); p.restore()
    part("topleft", x - P, y - P, P + B, P + TT)
    part("topright", x + w - B, y - P, B + P, P + TT)
    part("bottomleft", x - P, y + h - B, P + B, B + P)
    part("bottomright", x + w - B, y + h - B, B + P, B + P)
    for tx in range(x + B, x + w - B, C):        # borders tile at natural size, as KSvg does
        cw = min(C, x + w - B - tx)
        part("top", tx, y - P, C, P + TT, (tx, y - P, cw, P + TT))
        part("bottom", tx, y + h - B, C, B + P, (tx, y + h - B, cw, B + P))
    for ty in range(y + TT, y + h - B, C):
        ch = min(C, y + h - B - ty)
        part("left", x - P, ty, P + B, C, (x - P, ty, P + B, ch))
        part("right", x + w - B, ty, B + P, C, (x + w - B, ty, B + P, ch))
    p.fillRect(x + B, y + TT, w - 2 * B, h - TT - B, QColor(10, 10, 10))
    p.setFont(QFont(FONT, 11)); p.setPen(QColor(150, 150, 150) if pre == "decoration" else QColor(56, 56, 56))
    p.drawText(QRectF(x, y + 3, w, 30), Qt.AlignmentFlag.AlignCenter, title)
    st = "active-center" if pre == "decoration" else "inactive-center"
    for i, n in enumerate(["close", "maximize", "minimize"]):
        QSvgRenderer(str(A / f"{n}.svg")).render(p, st, QRectF(x + w - 11 - 26 * (i + 1), y + 6, 24, 24))
    QSvgRenderer(str(A / "menu.svg")).render(p, st, QRectF(x + 11, y + 6, 24, 24))


bgw = Image.open(RAW / "desk-empty.png").convert("RGB").crop((120, 160, 1080, 760))
bgw.save(T / "decobg.png")
im = QImage(str(T / "decobg.png")).convertToFormat(QImage.Format.Format_ARGB32)
p = QPainter(im); dr = QSvgRenderer(str(A / "decoration.svg"))
window(p, dr, 120, 330, 720, 220, "decoration-inactive", "notes.md — Kate")
window(p, dr, 60, 70, 720, 220, "decoration", "subject_0x2133.txt — Kate")
p.end(); im.save(str(S / "decoration.png"))

# buttons: every state, 4x
names = ["close", "maximize", "minimize", "menu", "keepabove", "alldesktops"]
states = ["active-center", "hover-center", "pressed-center", "inactive-center", "hover-inactive-center"]
im = qimg(130 + 112 * len(states), 40 + 112 * len(names)); p = QPainter(im)
p.setFont(QFont(FONT, 11)); p.setPen(QColor(92, 92, 92))
for c, s in enumerate(states):
    p.drawText(QRectF(130 + 112 * c, 8, 104, 24), Qt.AlignmentFlag.AlignCenter, s.replace("-center", ""))
for rr, n in enumerate(names):
    p.drawText(QRectF(8, 40 + 112 * rr, 116, 96), Qt.AlignmentFlag.AlignVCenter, n)
    for c, s in enumerate(states):
        QSvgRenderer(str(A / f"{n}.svg")).render(p, s, QRectF(134 + 112 * c, 40 + 112 * rr, 96, 96))
p.end(); im.save(str(S / "buttons.png"))

# clock widget, 3x
if (T / "clock.png").exists():
    c = Image.open(T / "clock.png"); c.resize((c.width * 3, c.height * 3), Image.NEAREST).save(S / "clock.png")

# icons
IC = R / "icons/Redacted/scalable"
picks = [("places", "blue-folder"), ("places", "blue-user-home"), ("places", "blue-folder-documents"),
         ("places", "blue-folder-download"), ("places", "blue-folder-music"), ("places", "blue-folder-pictures"),
         ("places", "blue-folder-video"), ("places", "blue-folder-git"), ("places", "blue-folder-templates"),
         ("places", "blue-network"), ("apps", "start-here"), ("apps", "distributor-logo")]
im = qimg(6 * 150, 2 * 170); p = QPainter(im); p.setFont(QFont(FONT, 10)); p.setPen(QColor(92, 92, 92))
for i, (sub, n) in enumerate(picks):
    x, y = (i % 6) * 150, (i // 6) * 170
    f = IC / sub / f"{n}.svg"
    if f.exists():
        QSvgRenderer(str(f.resolve())).render(p, QRectF(x + 27, y + 18, 96, 96))
    p.drawText(QRectF(x, y + 124, 150, 30), Qt.AlignmentFlag.AlignCenter, n.replace("blue-", ""))
p.end(); im.save(str(S / "icons.png"))

# colour scheme: the roles as swatches
cs = {}; grp = None
for line in (R / "colors/Redacted.colors").read_text().splitlines():
    if line.startswith("["): grp = line.strip("[]")
    elif "=" in line and grp and grp.startswith("Colors:") and "][" not in grp:
        k, v = line.split("=", 1)
        if v.count(",") == 2: cs[f"{grp[7:]}.{k}"] = tuple(map(int, v.split(",")))
keys = [k for k in ("Window.BackgroundNormal", "View.BackgroundNormal", "Header.BackgroundNormal", "Button.BackgroundNormal",
                    "Window.DecorationFocus", "Selection.BackgroundNormal", "Tooltip.BackgroundNormal", "Window.ForegroundInactive",
                    "Window.ForegroundNormal", "Selection.ForegroundNormal", "Window.ForegroundLink", "Window.ForegroundNegative") if k in cs]
im = qimg(4 * 230, ((len(keys) + 3) // 4) * 150); p = QPainter(im); p.setFont(QFont(FONT, 10))
for i, k in enumerate(keys):
    x, y = (i % 4) * 230, (i // 4) * 150
    p.fillRect(x + 15, y + 15, 200, 90, QColor(*cs[k])); p.setPen(QColor(40, 40, 40)); p.drawRect(x + 15, y + 15, 200, 90)
    p.setPen(QColor(120, 120, 120)); p.drawText(QRectF(x, y + 108, 230, 18), Qt.AlignmentFlag.AlignCenter, k)
    p.setPen(QColor(70, 70, 70)); p.drawText(QRectF(x, y + 124, 230, 18), Qt.AlignmentFlag.AlignCenter, "#%02x%02x%02x" % cs[k])
p.end(); im.save(str(S / "colors.png"))
print("stills ->", S)
