#!/usr/bin/env python3
"""Redacted Plymouth assets. Every word is pre-rendered (no fonts in initramfs)."""
import shutil, sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter
R = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(R))
import palette as P

A = R / "assets"
OUT = R / "plymouth/redacted"
OUT.mkdir(parents=True, exist_ok=True)
for f in OUT.glob("*.png"):
    f.unlink()
FB = FR = str(R / "sddm/redacted/art/DepartureMono.otf")

def osd(text, size, ink=P.TEXT_HI, glow=P.ACCENT, bold=True, spacing=2, glow_a=150):
    f = ImageFont.truetype(FB if bold else FR, size)
    # letter-spaced layout
    widths = [f.getlength(ch) for ch in text]
    w = int(sum(widths) + spacing * len(text)) + 24
    asc, desc = f.getmetrics()
    h = asc + desc + 24
    def draw(fill):
        im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        d = ImageDraw.Draw(im); x = 12
        for ch, cw in zip(text, widths):
            d.text((x, 12), ch, font=f, fill=fill); x += cw + spacing
        return im
    g = draw(P.rgb(glow) + (glow_a,)).filter(ImageFilter.GaussianBlur(size / 9))
    out = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    out.alpha_composite(g)
    out.alpha_composite(draw(P.rgb(glow) + (110,)), (-2, 0))     # chroma split
    out.alpha_composite(draw(P.rgb(ink) + (255,)), (1, 0))
    return out

def save(im, name):
    im.save(OUT / name, optimize=True)

# background: the still wallpaper, dimmed (it already carries scanlines + static)
Image.open(A / "wallpaper-dim.png").convert("RGB").save(OUT / "bg.png", optimize=True)

# grey static frames, a soft rolling band, a faint grey glow
import random
rnd = random.Random(77)
for i in range(4):
    im = Image.new("RGBA", (480, 270), (0, 0, 0, 0)); px = im.load()
    for _ in range(int(480 * 270 * 0.03)):
        v = rnd.randint(60, 170)
        px[rnd.randrange(480), rnd.randrange(270)] = (v, v, v, rnd.randint(12, 46))
    im.resize((1920, 1080), Image.NEAREST).save(OUT / f"noise_{i}.png", optimize=True)
band = Image.new("RGBA", (1920, 90), (0, 0, 0, 0)); d = ImageDraw.Draw(band)
for y in range(90):
    a = 1 - abs(y - 45) / 45
    d.line([(0, y), (1919, y)], fill=(160, 160, 160, int(16 * a * a)))
band.save(OUT / "tracking.png", optimize=True)
g = Image.new("RGBA", (256, 256), (0, 0, 0, 0)); gp = g.load()
for y in range(256):
    for x in range(256):
        dd = ((x - 128) ** 2 + (y - 128) ** 2) ** .5 / 128
        if dd < 1:
            gp[x, y] = (34, 34, 34, int(255 * (1 - dd) ** 2.2))
g.save(OUT / "glow.png")

GLOW = P.grey(40)
save(osd("[REDACTED]", 46, glow=GLOW), "osd_play.png")
save(osd("WITHDRAWN ■", 46, glow=GLOW), "osd_stop.png")
save(osd("RESTARTING", 46, glow=GLOW), "osd_rew.png")
save(osd("FILE 0x2133", 22, ink=P.TEXT, glow=GLOW, bold=False), "osd_ch.png")
save(osd("ELAPSED", 22, glow=GLOW), "osd_cnt.png")
for ch, name in list(zip("0123456789", [f"d{i}" for i in range(10)])) + [(":", "dcolon")]:
    save(osd(ch, 22, glow=GLOW, spacing=0), f"{name}.png")

save(osd("REDACTED", 64, glow=GLOW, glow_a=190, spacing=6), "logo.png")
save(osd("RESTORING SUBJECT", 18, ink=P.TEXT_DIM, glow=P.ACCENT_DEEP, bold=False, spacing=5, glow_a=90), "cap_boot.png")
save(osd("WITHDRAWING SUBJECT", 18, ink=P.TEXT_DIM, glow=P.ACCENT_DEEP, bold=False, spacing=5, glow_a=90), "cap_halt.png")
save(osd("PASSWORD", 18, ink=P.TEXT_DIM, glow=P.ACCENT_DEEP, bold=False, spacing=5, glow_a=90), "cap_pw.png")

# tape-block progress bar: 32 blocks
N, BW, BH, GAP = 32, 11, 20, 5
W = N * BW + (N - 1) * GAP + 16
def blocks(lit):
    im = Image.new("RGBA", (W, BH + 16), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    for i in range(N):
        x = 8 + i * (BW + GAP)
        c = P.rgb(P.grey(58) if lit else P.grey(18)) + (255 if lit else 200,)
        d.rectangle([x, 8, x + BW - 1, 8 + BH - 1], fill=c)
    if lit:
        g = im.filter(ImageFilter.GaussianBlur(4))
        out = Image.new("RGBA", im.size, (0, 0, 0, 0)); out.alpha_composite(g); out.alpha_composite(g); out.alpha_composite(im)
        d2 = ImageDraw.Draw(out)
        for i in range(N):   # hot top edge on every block
            x = 8 + i * (BW + GAP)
            d2.line([x, 8, x + BW - 1, 8], fill=P.rgb(P.grey(120)) + (255,))
        return out
    return im
save(blocks(False), "bar_dim.png")
save(blocks(True), "bar_lit.png")

# password plate + block bullet
pw = Image.new("RGBA", (520, 58), (0, 0, 0, 0))
d = ImageDraw.Draw(pw)
d.rounded_rectangle([4, 4, 515, 53], 4, fill=P.rgb(P.ABYSS) + (235,), outline=P.rgb(P.grey(40)) + (255,))
g = pw.filter(ImageFilter.GaussianBlur(3)); plate = Image.new("RGBA", pw.size, (0, 0, 0, 0)); plate.alpha_composite(g); plate.alpha_composite(pw)
save(plate, "pw_plate.png")
b = Image.new("RGBA", (13, 22), (0, 0, 0, 0)); ImageDraw.Draw(b).rectangle([2, 2, 10, 19], fill=P.rgb(P.TEXT) + (255,))
save(b, "bullet.png")
print("plymouth assets ->", OUT)
