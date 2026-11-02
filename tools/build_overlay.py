#!/usr/bin/env python3
"""Sprites for the redacted_static KWin script: mosaic chunks, censor bars, speck clusters."""
import random, sys
from pathlib import Path
from PIL import Image, ImageDraw
R = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(R))
import palette as P

OUT = R / "kwin/redacted_static/contents/ui/sprites"
OUT.mkdir(parents=True, exist_ok=True)
rnd = random.Random(404)

# mosaic chunks: ragged clusters of 4 px grey blocks
for i in range(6):
    w, h = rnd.choice(((40, 12), (56, 16), (32, 20), (64, 8), (24, 24), (48, 12)))
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    for y in range(0, h, 4):
        for x in range(0, w, 4):
            edge = min(x, w - 4 - x) / w + min(y, h - 4 - y) / h
            if rnd.random() < 0.35 + edge * 2.2:
                v = rnd.choice((14, 20, 26, 34, 44, 58))
                d.rectangle([x, y, x + 3, y + 3], fill=(v, v, v, 255))
    im.save(OUT / f"mosaic_{i}.png")

# censor bars: black with one lit edge
for i, (w, h) in enumerate(((36, 7), (58, 8), (84, 9), (22, 6))):
    im = Image.new("RGBA", (w, h), (0, 0, 0, 255))
    ImageDraw.Draw(im).line([(0, 0), (w - 1, 0)], fill=P.rgb(P.ACCENT_GLOW) + (255,))
    im.save(OUT / f"bar_{i}.png")

# speck clusters: a few bright-ish grey pixels
for i in range(4):
    im = Image.new("RGBA", (16, 16), (0, 0, 0, 0)); px = im.load()
    for _ in range(rnd.randint(3, 7)):
        v = rnd.randint(60, 150)
        px[rnd.randrange(16), rnd.randrange(16)] = (v, v, v, rnd.randint(140, 255))
    im.save(OUT / f"speck_{i}.png")
print("overlay sprites ->", OUT)
