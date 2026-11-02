#!/usr/bin/env python3
"""Fail if any shipped colour is not a neutral grey (r == g == b, within `tol`).
Scans hex/rgb colours in text files and pixels in PNG/JPG under the shipped dirs."""
import re, sys
from pathlib import Path
import numpy as np
from PIL import Image
R = Path(__file__).resolve().parent.parent
DIRS = ["colors", "plasma", "aurorae", "kvantum", "terminal", "sddm", "plymouth", "kwin", "qml", "shaders"]
SKIP_ICON = R / "icons"            # inherited Tela icons keep their own colours (only folders are recoloured)
tol = 3
bad = []
HEX = re.compile(r"#([0-9a-fA-F]{6})(?:[0-9a-fA-F]{2})?\b")
RGBCSV = re.compile(r"=(\d{1,3}),(\d{1,3}),(\d{1,3})\b")
for d in DIRS:
    for f in (R / d).rglob("*"):
        if not f.is_file():
            continue
        if f.suffix in (".png", ".jpg"):
            a = np.asarray(Image.open(f).convert("RGBA")).astype(int)
            vis = a[..., 3] > 8
            spread = (a[..., :3].max(axis=2) - a[..., :3].min(axis=2))[vis]
            if spread.size and spread.max() > tol + 4:      # jpeg/AA slack
                bad.append(f"{f.relative_to(R)}: pixel spread {spread.max()}")
            continue
        if f.suffix in (".otf", ".ttf", ".qsb") or f.name.startswith("UPSTREAM"):
            continue
        try:
            t = f.read_text()
        except UnicodeDecodeError:
            continue
        for m in HEX.finditer(t):
            r, g, b = (int(m.group(1)[i:i + 2], 16) for i in (0, 2, 4))
            if max(r, g, b) - min(r, g, b) > tol:
                bad.append(f"{f.relative_to(R)}: {m.group(0)}")
        if f.suffix in (".colors", ".colorscheme", ".profile") or f.name.endswith("rc"):
            for m in RGBCSV.finditer(t):
                r, g, b = map(int, m.groups())
                if max(r, g, b) - min(r, g, b) > tol:
                    bad.append(f"{f.relative_to(R)}: {m.group(0)}")
# folder icons we generate
for f in (R / "icons/Redacted").rglob("*.svg"):
    if f.is_symlink():
        continue
    for m in HEX.finditer(f.read_text()):
        r, g, b = (int(m.group(1)[i:i + 2], 16) for i in (0, 2, 4))
        if max(r, g, b) - min(r, g, b) > tol:
            bad.append(f"{f.relative_to(R)}: {m.group(0)}"); break
for b in sorted(set(bad))[:60]:
    print("TINT", b)
print(f"{len(set(bad))} tinted colour(s)" if bad else "all grey")
sys.exit(1 if bad else 0)
