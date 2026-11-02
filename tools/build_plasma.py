#!/usr/bin/env python3
"""Redacted Plasma style: panel, dialogs, tooltips, widget backgrounds.

Every frame is authored at 1:1. The centre and side edges tile (scanline phase
is a multiple of 3px everywhere), so the VHS lines never smear. Glows are
gradients in the shadow-* elements, no SVG filters. Missing elements fall back
to Breeze and follow the Redacted colour scheme.
"""
import base64, io, json, random, shutil, sys
from pathlib import Path
from PIL import Image
R = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(R))
import palette as P

OUT = R / "plasma/desktoptheme/Redacted"
TILE = 96
random.seed(7)

def noise_png(n, alpha, blocks=0, density=0.06):
    """grey grain; `blocks` adds a sparse mosaic of censor-pixel squares (multiples of 3px)."""
    im = Image.new("RGBA", (n, n), (0, 0, 0, 0))
    px = im.load()
    for _ in range(blocks):
        s = random.choice((3, 6, 6, 9, 12))
        x0, y0 = random.randrange(0, n, 3), random.randrange(0, n, 3)
        v = random.randint(30, 90); a = random.randint(6, 16)
        for y in range(y0, min(n, y0 + s)):
            for x in range(x0, min(n, x0 + s)):
                px[x, y] = (v, v, v, a)
    for _ in range(int(n * n * density)):
        v = random.randint(110, 220)
        px[random.randrange(n), random.randrange(n)] = (v, v, v, random.randint(alpha // 3, alpha))
    b = io.BytesIO(); im.save(b, "PNG")
    return "data:image/png;base64," + base64.b64encode(b.getvalue()).decode()

NOISE = noise_png(TILE, 26)
STATIC = noise_png(TILE, 34, blocks=26, density=0.09)   # panel: heavier static + pixel mosaic

def stops(*s):
    return "".join(f'<stop offset="{o}" stop-color="{c}" stop-opacity="{a}"/>' for o, c, a in s)

def scan(x, y, w, h, op=0.30):
    """horizontal scanlines on rows where (row % 3 == 2), phase anchored to y."""
    return "".join(f'<rect x="{x}" y="{y + r}" width="{w}" height="1" fill="#000" opacity="{op}"/>'
                   for r in range(2, h, 3))

def frame_svg(cs, fill, fill_op, edge, glow_top, shadow, S, radius, margins, scan_op=0.30, noise=True, inset=0, tex=None):
    T = TILE
    W, H = cs * 2 + T, cs * 2 + T
    sx = W + 40              # shadows live to the right of the frame
    o = [f'<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="{sx + S * 2 + T + 10}" height="{max(H, S * 2 + T) + 10}">',
         "<defs>",
         f'<linearGradient id="gT" x1="0" y1="0" x2="0" y2="1">{stops((0, glow_top, 0.55), (1, glow_top, 0))}</linearGradient>']
    sh = ((0, shadow, 0.34), (0.35, "#000", 0.30), (0.7, "#000", 0.10), (1, "#000", 0))
    for d, (x1, y1, x2, y2) in {"T": (0, 1, 0, 0), "B": (0, 0, 0, 1), "L": (1, 0, 0, 0), "R": (0, 0, 1, 0)}.items():
        o.append(f'<linearGradient id="s{d}" x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}">{stops(*sh)}</linearGradient>')
    for k, (cx, cy) in {"TL": (S, S), "TR": (0, S), "BL": (S, 0), "BR": (0, 0)}.items():
        o.append(f'<radialGradient id="s{k}" gradientUnits="objectBoundingBox" cx="{cx / S}" cy="{cy / S}" r="1">{stops(*sh)}</radialGradient>')
    o.append("</defs>")

    def body(x, y, w, h):
        g = f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{fill}" opacity="{fill_op}"/>'
        g += scan(x, y, w, h, scan_op)
        return g

    # centre: tiled at natural size
    c = body(cs, cs, T, T)
    if noise:
        c += f'<image x="{cs}" y="{cs}" width="{T}" height="{T}" xlink:href="{tex or NOISE}"/>'
    o.append(f'<g id="center">{c}</g>')
    # edges (phase matches centre: edges start at y=cs as well)
    o.append(f'<g id="left">{body(0, cs, cs, T)}<rect x="0" y="{cs}" width="1" height="{T}" fill="{edge}"/></g>')
    o.append(f'<g id="right">{body(cs + T, cs, cs, T)}<rect x="{W - 1}" y="{cs}" width="1" height="{T}" fill="{edge}"/></g>')
    # top/bottom: rows authored relative to their own origin, so they match any centre phase
    top = (body(cs, 0, T, cs) + f'<rect x="{cs}" y="0" width="{T}" height="1" fill="{edge}"/>'
           + f'<rect x="{cs}" y="1" width="{T}" height="1" fill="{glow_top}" opacity="0.85"/>'
           + f'<rect x="{cs}" y="2" width="{T}" height="{cs - 2}" fill="url(#gT)" opacity="0.5"/>')
    if tex:   # pixel-stepped seam: a broken row of censor pixels under the hairline
        rnd = random.Random(31)
        for bx in range(cs, cs + T, 3):
            if rnd.random() < 0.45:
                top += f'<rect x="{bx}" y="2" width="3" height="3" fill="{glow_top}" opacity="{rnd.choice((0.5, 0.8, 1))}"/>'
    o.append(f'<g id="top">{top}</g>')
    o.append(f'<g id="bottom">{body(cs, cs + T, T, cs)}<rect x="{cs}" y="{H - 1}" width="{T}" height="1" fill="{edge}"/></g>')

    r = radius
    def corner(name, x, y, fx, fy):
        # quarter-rounded corner, flipped into place
        tf = f'transform="translate({x + (cs if fx else 0)},{y + (cs if fy else 0)}) scale({-1 if fx else 1},{-1 if fy else 1})"'
        outer = f"M{cs},0 L{cs},{cs} L0,{cs} L0,{r} A{r},{r} 0 0 1 {r},0 Z"
        ri = r - 1
        inner = f"M{cs},1 L{cs},{cs} L1,{cs} L1,{1 + ri} A{ri},{ri} 0 0 1 {1 + ri},1 Z"
        g = [f'<rect x="{x}" y="{y}" width="{cs}" height="{cs}" fill="#000" opacity="0"/>',
             f'<g {tf}><path d="{outer}" fill="{edge}"/>'
             f'<path d="{inner}" fill="{fill}" opacity="{fill_op}"/>']
        if not fy:  # top corners carry the accent hairline + seam glow, matching the top edge
            g.append(f'<rect x="{r - 1}" y="1" width="{cs - r + 1}" height="1" fill="{glow_top}" opacity="0.85"/>')
            g.append(f'<rect x="2" y="2" width="{cs - 2}" height="{cs - 2}" fill="url(#gT)" opacity="0.5"/>')
        g.append("</g>")
        return f'<g id="{name}">' + "".join(g) + "</g>"
    o += [corner("topleft", 0, 0, 0, 0), corner("topright", cs + T, 0, 1, 0),
          corner("bottomleft", 0, cs + T, 0, 1), corner("bottomright", cs + T, cs + T, 1, 1)]

    # masks (for blur behind translucent frames) — same footprint, opaque
    for n, (x, y, w, h) in {"center": (cs, cs, T, T), "top": (cs, 0, T, cs), "bottom": (cs, cs + T, T, cs),
                            "left": (0, cs, cs, T), "right": (cs + T, cs, cs, T), "topleft": (0, 0, cs, cs),
                            "topright": (cs + T, 0, cs, cs), "bottomleft": (0, cs + T, cs, cs),
                            "bottomright": (cs + T, cs + T, cs, cs)}.items():
        o.append(f'<rect id="mask-{n}" x="{x}" y="{y}" width="{w}" height="{h}" fill="#000"/>')

    # shadows with a faint bleed nearest the frame = the glow
    X, Y = sx, 0
    o += [f'<rect id="shadow-topleft" x="{X}" y="{Y}" width="{S}" height="{S}" fill="url(#sTL)"/>',
          f'<rect id="shadow-top" x="{X + S}" y="{Y}" width="{T}" height="{S}" fill="url(#sT)"/>',
          f'<rect id="shadow-topright" x="{X + S + T}" y="{Y}" width="{S}" height="{S}" fill="url(#sTR)"/>',
          f'<rect id="shadow-left" x="{X}" y="{Y + S}" width="{S}" height="{T}" fill="url(#sL)"/>',
          f'<rect id="shadow-center" x="{X + S}" y="{Y + S}" width="{T}" height="{T}" fill="none"/>',
          f'<rect id="shadow-right" x="{X + S + T}" y="{Y + S}" width="{S}" height="{T}" fill="url(#sR)"/>',
          f'<rect id="shadow-bottomleft" x="{X}" y="{Y + S + T}" width="{S}" height="{S}" fill="url(#sBL)"/>',
          f'<rect id="shadow-bottom" x="{X + S}" y="{Y + S + T}" width="{T}" height="{S}" fill="url(#sB)"/>',
          f'<rect id="shadow-bottomright" x="{X + S + T}" y="{Y + S + T}" width="{S}" height="{S}" fill="url(#sBR)"/>']
    for side in ("top", "bottom", "left", "right"):
        o.append(f'<rect id="shadow-hint-{side}-margin" x="0" y="0" width="{S}" height="{S}" fill="none"/>')
    m = margins
    for side in ("top", "bottom", "left", "right"):
        o.append(f'<rect id="hint-{side}-margin" x="0" y="0" width="{m}" height="{m}" fill="none"/>')
        if inset:
            o.append(f'<rect id="hint-{side}-inset" x="0" y="0" width="{inset}" height="{inset}" fill="none"/>')
    o.append('<rect id="hint-tile-center" x="0" y="0" width="1" height="1" fill="none"/>')
    o.append("</svg>")
    return "\n".join(o)

OUT.mkdir(parents=True, exist_ok=True)
files = {
    "widgets/panel-background.svg": frame_svg(6, P.SURFACE, 0.97, P.EDGE, P.ACCENT_HI, "#000000", 12, 2, 3, tex=STATIC),
    "dialogs/background.svg":       frame_svg(8, P.BASE, 0.97, P.EDGE_HI, P.ACCENT, "#000000", 18, 3, 8),
    "widgets/tooltip.svg":          frame_svg(6, P.VOID, 0.97, P.EDGE_HI, P.ACCENT_HI, "#000000", 12, 2, 6),
    "widgets/background.svg":       frame_svg(8, P.BASE, 0.92, P.EDGE, P.ACCENT_LO, "#000000", 14, 3, 8),
    "solid/widgets/panel-background.svg": frame_svg(6, P.SURFACE, 1.0, P.EDGE, P.ACCENT_HI, "#000000", 12, 2, 3, tex=STATIC),
    "solid/dialogs/background.svg":       frame_svg(8, P.BASE, 1.0, P.EDGE_HI, P.ACCENT, "#000000", 18, 3, 8),
    "translucent/widgets/panel-background.svg": frame_svg(6, P.SURFACE, 0.94, P.EDGE, P.ACCENT_HI, "#000000", 12, 2, 3, tex=STATIC),
    "translucent/dialogs/background.svg":       frame_svg(8, P.BASE, 0.94, P.EDGE_HI, P.ACCENT, "#000000", 18, 3, 8),
    "translucent/widgets/tooltip.svg":          frame_svg(6, P.VOID, 0.94, P.EDGE_HI, P.ACCENT_HI, "#000000", 12, 2, 6),
}
if OUT.exists():
    for p in OUT.rglob("*.svg*"):
        p.unlink()
for rel, svg in files.items():
    p = OUT / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(svg)

meta = {"KPlugin": {"Authors": [{"Name": "splicer scorn (voidrane)"}], "Category": "",
                    "Description": "Redacted: monochrome black with static, censor pixels and a seam only just lighter than black",
                    "EnabledByDefault": True, "Id": "Redacted", "License": "GPL-3.0-or-later",
                    "Name": "Redacted", "Version": "1.0"},
        "X-Plasma-API": "5.0"}
(OUT / "metadata.json").write_text(json.dumps(meta, indent=4))
# blur + contrast behind translucent frames
(OUT / "plasmarc").write_text("[ContrastEffect]\nenabled=true\ncontrast=0.2\nintensity=0.5\nsaturation=0\n\n[BlurBehindEffect]\nenabled=true\n\n[AdaptiveTransparency]\nenabled=true\n")
print("plasma style ->", OUT)
