#!/usr/bin/env python3
"""Redacted wallpaper: the Nightfeed face, drained to grey and nearly to black,
then censored: a mosaic over the face, a black bar over the eyes, a faint
dissociated double of the face drifting off to one side, torn scan rows,
static, and a column of redacted "document" lines in the empty dark.

Outputs (assets/):
  face.png        1920x1080 clean grey face (input for the animated shaders)
  wallpaper.png   1920x1080 still composite (image wallpaper, lock fallback)
  wallpaper-<WxH>.png  extra sizes for the image wallpaper package
The source file is only read.
"""
import math, random, sys
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
R = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(R))
import palette as P

A = R / "assets"
A.mkdir(exist_ok=True)
W, H = 1920, 1080
rnd = random.Random(2133)

# eye centres in the 1080-high face (measured on the source), used for the bar
EYE_L, EYE_R = (298, 343), (679, 552)

# 1. grey face, max brightness = PALE, padded east with black
src = Image.open(P.SOURCE_WALLPAPER).convert("RGB")
src = src.resize((round(src.width * H / src.height), H), Image.LANCZOS)
a = np.asarray(src).astype(np.float32) / 255
v = a.max(axis=2)                                    # the face is blue: use the max channel
v = np.clip((v - 0.03) / 0.97, 0, 1) ** 1.25 * P.lv(P.PALE)
face = np.zeros((H, W), np.float32)
face[:, :v.shape[1]] = v
Image.fromarray(face.astype(np.uint8), "L").save(A / "face.png", optimize=True)

# 2. still composite
out = face.copy()

# dissociated double: a fainter copy, shifted right/up, with torn rows
ghost = np.roll(np.roll(face, 46, axis=1), -10, axis=0) * 0.42
out = np.maximum(out, ghost)

# mosaic over the face's middle (block grid), stronger toward the eyes
def mosaic(img, x0, y0, x1, y1, b):
    sub = img[y0:y1, x0:x1]
    h, w = sub.shape
    hb, wb = h // b, w // b
    m = sub[:hb * b, :wb * b].reshape(hb, b, wb, b).mean(axis=(1, 3))
    img[y0:y0 + hb * b, x0:x0 + wb * b] = np.repeat(np.repeat(m, b, 0), b, 1)

mosaic(out, 456, 312, 936, 768, 24)     # the right cheek dissolves into blocks
mosaic(out, 168, 744, 552, 1008, 12)    # mouth and chin, finer
mosaic(out, 96, 480, 264, 744, 6)       # a fine seam where the face turns

# torn scan rows: random horizontal slices slid sideways
for _ in range(38):
    y = rnd.randrange(120, H - 120); h = rnd.choice((2, 3, 3, 6, 9)); dx = rnd.randint(-90, 90)
    out[y:y + h] = np.roll(out[y:y + h], dx, axis=1)

# scanlines: every third row a touch darker
out[2::3] *= 0.72

img = Image.fromarray(np.clip(out, 0, 255).astype(np.uint8), "L").convert("RGB")
d = ImageDraw.Draw(img)

# censor bar over both eyes (rotated rectangle), pure black, with a hairline lift
cx, cy = (EYE_L[0] + EYE_R[0]) / 2, (EYE_L[1] + EYE_R[1]) / 2
ang = math.atan2(EYE_R[1] - EYE_L[1], EYE_R[0] - EYE_L[0])
L = math.dist(EYE_L, EYE_R) + 300
T = 120
ux, uy = math.cos(ang), math.sin(ang)
nx, ny = -uy, ux
def quad(l, t):
    return [(cx + ux * sx * l / 2 + nx * sy * t / 2, cy + uy * sx * l / 2 + ny * sy * t / 2)
            for sx, sy in ((-1, -1), (1, -1), (1, 1), (-1, 1))]
d.polygon(quad(L, T), fill=(0, 0, 0))
d.line(quad(L, T)[:2], fill=P.rgb(P.ACCENT_GLOW), width=1)

# the empty dark: a redacted document, bars only a few levels above black
x0, y = 1260, 250
for i in range(22):
    if rnd.random() < 0.12:
        y += 26; continue
    w = rnd.randint(140, 470)
    lvl = P.lv(P.SURFACE) + rnd.choice((2, 4, 6))
    d.rectangle([x0, y, x0 + w, y + 13], fill=P.rgb(P.grey(lvl)))
    if rnd.random() < 0.35:        # a few lines keep a short unredacted stub
        d.rectangle([x0 + w + 10, y + 5, x0 + w + 10 + rnd.randint(20, 60), y + 8], fill=P.rgb(P.grey(lvl + 10)))
    y += 26

# static: sparse grey grain + a few dropout streaks
px = img.load()
for _ in range(int(W * H * 0.012)):
    x, yy = rnd.randrange(W), rnd.randrange(H)
    g = rnd.randint(18, 70)
    o = px[x, yy][0]
    px[x, yy] = (max(o, g),) * 3
for _ in range(14):
    yy = rnd.randrange(H); x = rnd.randrange(W); l = rnd.randint(60, 420)
    d.line([(x, yy), (min(W - 1, x + l), yy)], fill=P.rgb(P.grey(rnd.randint(24, 44))))

img.save(A / "wallpaper.png", optimize=True)
for w, h in ((2560, 1440), (3840, 2160)):
    img.resize((w, h), Image.NEAREST).save(A / f"wallpaper-{w}x{h}.png", optimize=True)

# a dimmer copy for behind login / lock UI
Image.fromarray((np.asarray(img).astype(np.float32) * 0.6).astype(np.uint8)).save(A / "wallpaper-dim.png", optimize=True)
print("wallpaper ->", A / "wallpaper.png")
