#!/usr/bin/env python3
"""Generate the Redacted Aurorae window decoration (forked from DaedricMorrowind).

    python3 decoration/build-decoration.py [out-dir] [theme-name]

Geometry is authored 1:1 in pixels. Each frame element is as big as the area
Aurorae gives it (shadow padding + border), so nothing is squeezed or tiled:
the whole title bar is the "top" element and the soft shadow lives in the
padding. Edges only use gradients that run across them, so they stretch clean.
No SVG filters: glows are layered translucent strokes and radial gradients.
"""
import base64, io, random, sys
from pathlib import Path
from PIL import Image
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import palette as PAL

OUT = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).resolve().parent.parent / "aurorae/Redacted"
NAME = sys.argv[2] if len(sys.argv) > 2 else OUT.name

P = 20          # shadow padding on every side
B = 3           # side and bottom border
ET, TH, EB = 3, 30, 3   # title edge top, title height, title edge bottom
T = ET + TH + EB        # title bar height
C = 48          # border tile period: every pattern below repeats every 48 px
BTN = 24

W = P + B + C + B + P
H = P + T + C + B + P
X0, X1 = P, W - P            # window left / right edge
Y0, Y1 = P, H - P            # window top / bottom edge
XL, XR = P + B, W - P - B    # centre left / right
YT, YB = P + T, H - P - B    # centre top / bottom

VOID, BASALT = PAL.VOID, PAL.BASE
BRASS, BRASS_HI, BRASS_LO = PAL.EDGE, PAL.EDGE_HI, PAL.SHADE_LO       # hairlines
BONE, PEACH, EMBER, FLAME, BLOOD = PAL.TEXT, PAL.TEXT_HI, PAL.ACCENT_GLOW, PAL.ACCENT_HI, PAL.ACCENT_DEEP
ASH, ASH_LO = PAL.grey(17), PAL.grey(12)
REC = PAL.grey(64)      # close-button hover: the one place a step more light is allowed

random.seed(1993)
_im = Image.new("RGBA", (C, TH + ET + EB), (0, 0, 0, 0))
_px = _im.load()
for _ in range(int(C * (TH + ET + EB) * 0.07)):
    v = random.randint(120, 220)
    _px[random.randrange(C), random.randrange(TH + ET + EB)] = (v, v, v, random.randint(6, 20))
_b = io.BytesIO(); _im.save(_b, "PNG")
NOISE = "data:image/png;base64," + base64.b64encode(_b.getvalue()).decode()


def stops(*s):
    return "".join(f'<stop offset="{o}" stop-color="{c}" stop-opacity="{a}"/>' for o, c, a in s)


def defs():
    sh = lambda tint: ((0, tint, 0.30 if tint != "#000" else 0.5), (0.22, tint if tint != "#000" else "#000", 0.13), (0.5, "#000", 0.14), (0.8, "#000", 0.04), (1, "#000", 0))
    out = ["<defs>"]
    for key, tint in (("a", PAL.ACCENT), ("i", "#000")):
        s = stops(*sh(tint))
        out += [
            f'<linearGradient id="sh{key}L" x1="1" y1="0" x2="0" y2="0">{s}</linearGradient>',
            f'<linearGradient id="sh{key}R" x1="0" y1="0" x2="1" y2="0">{s}</linearGradient>',
            f'<linearGradient id="sh{key}T" x1="0" y1="1" x2="0" y2="0">{s}</linearGradient>',
            f'<linearGradient id="sh{key}B" x1="0" y1="0" x2="0" y2="1">{s}</linearGradient>',
        ]
        for corner, cx, cy in (("TL", X0, Y0), ("TR", X1, Y0), ("BL", X0, Y1), ("BR", X1, Y1)):
            out.append(f'<radialGradient id="sh{key}{corner}" gradientUnits="userSpaceOnUse" cx="{cx}" cy="{cy}" r="{P}">{s}</radialGradient>')
    out += [
        # title bar stone, top to bottom
        f'<linearGradient id="barA" x1="0" y1="0" x2="0" y2="1">{stops((0, PAL.grey(17), 1), (0.55, PAL.SURFACE, 1), (1, PAL.BASE, 1))}</linearGradient>',
        f'<linearGradient id="barI" x1="0" y1="0" x2="0" y2="1">{stops((0, PAL.grey(12), 1), (1, PAL.BASE, 1))}</linearGradient>',
        # ember seam under the title: a soft bloom with a thin hot core
        f'<linearGradient id="seam" x1="0" y1="0" x2="0" y2="1">{stops((0, FLAME, 0), (0.55, FLAME, 0.10), (0.85, FLAME, 0.30), (1, FLAME, 0.55))}</linearGradient>',
        f'<linearGradient id="seamI" x1="0" y1="0" x2="0" y2="1">{stops((0, "#000", 0), (1, "#000", 0.25))}</linearGradient>',
        f'<linearGradient id="stud" x1="0" y1="0" x2="1" y2="1">{stops((0, BONE, 1), (0.5, BRASS, 1), (1, BRASS_LO, 1))}</linearGradient>',
        "</defs>",
    ]
    return "\n".join(out)


def rect(x, y, w, h, fill, extra=""):
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{fill}" {extra}/>'


def bayer(n=4):
    m = [[0]]
    while len(m) < n:
        k = len(m)
        m = [[4 * v + o for v in row] + [4 * v + o2 for v in row] for row, (o, o2) in
             [(r, (0, 2)) for r in m] + [(r, (3, 1)) for r in m]]
    return m


BAYER = bayer(4)


def mosaic_seam(x, w, ybot, active):
    """The seam under the title as censor pixels: 2 px blocks, ordered-dithered,
    dense at the seam and thinning upward. A pure function of (x mod C), so the
    tiled border repeats seamlessly."""
    o = []
    if w < 8:
        return o
    rows = (0.78, 0.52, 0.30, 0.14, 0.06)
    lv = (38, 32, 27, 23, 20) if active else (16, 14, 12, 11, 10)
    for r, dens in enumerate(rows):
        y = ybot - 2 * (r + 1)
        for bx in range(0, w, 2):
            gx = (x + bx) % C
            th = (BAYER[(gx // 2) % 4][r % 4] + 0.5) / 16
            jitter = ((gx * 7 + r * 13) % 11) / 11 * 0.18 - 0.09
            if th + jitter < dens:
                v = lv[r] + ((gx * 5 + r * 3) % 3) * 2
                o.append(rect(x + bx, y, 2, 2, PAL.grey(v)))
    return o


def ruler(x, w, y, active):
    """Measurement ticks hanging off the top hairline: long every 48, short every 12."""
    if w < 12:
        return []
    o = []
    for t in range(0, w, 12):
        gx = (x + t) % C
        n = 4 if gx == 0 else 2 if gx == 24 else 1
        o.append(rect(x + t, y + 1, 1, n, PAL.grey((44 if n > 1 else 32) if active else 17)))
    return o


def title_strip(x, w, active, left_edge=False, right_edge=False, Y0=Y0):
    """A slice of the title bar from window top to the centre."""
    YT = Y0 + T
    bar, hair = ("barA", BRASS_HI) if active else ("barI", ASH)
    o = [rect(x, Y0, w, T, f"url(#{bar})")]
    o.append(f'<image x="{x}" y="{Y0}" width="{w}" height="{T}" preserveAspectRatio="none" xlink:href="{NOISE}" opacity="{1 if active else 0.5}"/>')
    # scanlines: a faint darker row every 3 px
    for yy in range(Y0 + 2, YT - 2, 3):
        o.append(rect(x, yy, w, 1, "#000", f'opacity="{0.22 if active else 0.12}"'))
    if not active:
        # unfocused windows are redacted: a censor band through the title (the text sits on top)
        mid = Y0 + ET + TH // 2
        o += [rect(x, mid - 7, w, 14, "#000", 'opacity="0.62"'),
              rect(x, mid - 8, w, 1, PAL.grey(15)),
              rect(x, mid + 7, w, 1, "#000", 'opacity="0.8"')]
    o.append(rect(x, Y0, w, 1, hair))
    o += ruler(x, w, Y0, active)
    o += mosaic_seam(x, w, YT - 1, active)
    o.append(rect(x, YT - 1, w, 1, FLAME if active else ASH, '' if active else 'opacity="0.8"'))
    if left_edge:
        o.append(rect(x, Y0, 1, T, hair))
    if right_edge:
        o.append(rect(x + w - 1, Y0, 1, T, hair))
    return o


def side_strip(x, y, h, active, outer_left):
    hair = BRASS if active else ASH
    o = [rect(x, y, B, h, BASALT if active else PAL.grey(9))]
    ox = x if outer_left else x + B - 1
    o.append(rect(ox, y, 1, h, hair))
    o.append(rect(x + B - 1 if outer_left else x, y, 1, h, PAL.VOID))
    if h >= C:
        o.append(rect(ox, y + 22, 1, 4, PAL.grey(40 if active else 18)))
    return o


def bottom_strip(x, w, active):
    hair = BRASS if active else ASH
    o = [rect(x, YB, w, B, BASALT if active else PAL.grey(9)),
         rect(x, YB, w, 1, PAL.VOID),
         rect(x, Y1 - 1, w, 1, hair)]
    if w >= C:
        o.append(rect(x + 22, Y1 - 1, 4, 1, PAL.grey(40 if active else 18)))
    return o


def stud(cx, cy, active):
    """Print crop marks in the shadow padding: the window's two edges carried on
    outward past the corner, after a gap, as if it had been cut from a file."""
    sx = -1 if cx < W / 2 else 1
    sy = -1 if cy < H / 2 else 1
    ex = X0 if sx < 0 else X1 - 1          # edge column
    ey = Y0 if sy < 0 else Y1 - 1          # edge row
    g, L, gap = PAL.grey(44 if active else 20), 12, 4
    hx = ex - gap - L if sx < 0 else ex + 1 + gap      # horizontal mark, on the edge row
    vy = ey - gap - L if sy < 0 else ey + 1 + gap      # vertical mark, on the edge column
    o = [rect(hx, ey, L, 1, g), rect(ex, vy, 1, L, g)]
    if active:   # registration pip where the marks would meet
        o.append(rect(ex + sx * (gap + 2), ey + sy * (gap + 2), 1, 1, PAL.grey(34)))
    return o


def frame(prefix, active):
    k = "a" if active else "i"
    g = {}
    g["center"] = [rect(XL, YT, C, C, PAL.BASE)]
    g["top"] = [rect(XL, 0, C, P, f"url(#sh{k}T)")] + title_strip(XL, C, active)
    g["bottom"] = [rect(XL, Y1, C, P, f"url(#sh{k}B)")] + bottom_strip(XL, C, active)
    g["left"] = [rect(0, YT, P, C, f"url(#sh{k}L)")] + side_strip(X0, YT, C, active, True)
    g["right"] = [rect(X1, YT, P, C, f"url(#sh{k}R)")] + side_strip(XL + C, YT, C, active, False)
    g["topleft"] = ([rect(0, 0, P, P, f"url(#sh{k}TL)"), rect(P, 0, B, P, f"url(#sh{k}T)"), rect(0, P, P, T, f"url(#sh{k}L)")]
                    + title_strip(X0, B, active, left_edge=True) + stud(X0 + 0.5, Y0 + 0.5, active))
    g["topright"] = ([rect(X1, 0, P, P, f"url(#sh{k}TR)"), rect(XR, 0, B, P, f"url(#sh{k}T)"), rect(X1, P, P, T, f"url(#sh{k}R)")]
                     + title_strip(XR, B, active, right_edge=True) + stud(X1 - 0.5, Y0 + 0.5, active))
    g["bottomleft"] = ([rect(0, Y1, P, P, f"url(#sh{k}BL)"), rect(P, Y1, B, P, f"url(#sh{k}B)"), rect(0, YB, P, B, f"url(#sh{k}L)")]
                       + side_strip(X0, YB, B, active, True) + [rect(X0, Y1 - 1, B, 1, BRASS if active else ASH)]
                       + stud(X0 + 0.5, Y1 - 0.5, active))
    g["bottomright"] = ([rect(X1, Y1, P, P, f"url(#sh{k}BR)"), rect(XR, Y1, B, P, f"url(#sh{k}B)"), rect(X1, YB, P, B, f"url(#sh{k}R)")]
                        + side_strip(XR, YB, B, active, False) + [rect(XR, Y1 - 1, B, 1, BRASS if active else ASH)]
                        + stud(X1 - 0.5, Y1 - 0.5, active))
    return "\n".join(f'<g id="{prefix}-{n}">\n' + "\n".join(v) + "\n</g>" for n, v in g.items())


def masks():
    boxes = {"center": (XL, YT, C, C), "top": (XL, Y0, C, T), "bottom": (XL, YB, C, B), "left": (X0, YT, B, C),
             "right": (XR, YT, B, C), "topleft": (X0, Y0, B, T), "topright": (XR, Y0, B, T),
             "bottomleft": (X0, YB, B, B), "bottomright": (XR, YB, B, B)}
    # each mask element keeps the full element size; only the window part is opaque
    full = {"center": (XL, YT, C, C), "top": (XL, 0, C, P + T), "bottom": (XL, YB, C, B + P), "left": (0, YT, P + B, C),
            "right": (XR, YT, B + P, C), "topleft": (0, 0, P + B, P + T), "topright": (XR, 0, B + P, P + T),
            "bottomleft": (0, YB, P + B, B + P), "bottomright": (XR, YB, B + P, B + P)}
    out = []
    for n in boxes:
        hidden = 'opacity="0"'
        out.append(f'<g id="mask-{n}">{rect(*full[n], "#000", hidden)}{rect(*boxes[n], "#fff")}</g>')
    return "\n".join(out)


def maximized(prefix, active):
    # centre-only frame stretched over the title bar; authored at title-bar height
    return f'<g id="{prefix}-center">' + "".join(title_strip(0, C, active, Y0=0)) + "</g>"


def decoration_svg():
    return "\n".join([
        f'<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="{W}" height="{H}" viewBox="0 0 {W} {H}">',
        defs(), frame("decoration", True), frame("decoration-inactive", False), masks(),
        # Aurorae stretches the maximized centre over the whole window height; tiling it
        # at its natural size instead keeps the title bar art 1:1 in the visible strip
        '<rect id="decoration-maximized-hint-tile-center" x="0" y="0" width="1" height="1" fill="none"/>',
        '<rect id="decoration-maximized-inactive-hint-tile-center" x="0" y="0" width="1" height="1" fill="none"/>',
        "</svg>"])


def maximized_svg_groups():
    # kept in the same file but outside the frame's coordinate system
    return maximized("decoration-maximized", True) + "\n" + maximized("decoration-maximized-inactive", False)


# ---- buttons -----------------------------------------------------------------
M = BTN / 2
GLYPHS = {
    "close":       f"M{M-3.5},{M-3.5} L{M+3.5},{M+3.5} M{M+3.5},{M-3.5} L{M-3.5},{M+3.5}",
    "minimize":    f"M{M-4},{M+3} L{M+4},{M+3}",
    "maximize":    f"M{M-3.5},{M-3.5} L{M+3.5},{M-3.5} L{M+3.5},{M+3.5} L{M-3.5},{M+3.5} Z",
    "restore":     f"M{M-4},{M-1.5} L{M+1.5},{M-1.5} L{M+1.5},{M+4} L{M-4},{M+4} Z M{M-1.5},{M-4} L{M+4},{M-4} L{M+4},{M+1.5}",
    "keepabove":   f"M{M-4},{M+1.5} L{M},{M-2.5} L{M+4},{M+1.5}",
    "keepbelow":   f"M{M-4},{M-1.5} L{M},{M+2.5} L{M+4},{M-1.5}",
    "shade":       f"M{M-4},{M-3} L{M+4},{M-3} M{M-4},{M} L{M+4},{M}",
    "alldesktops": f"M{M-3},{M-3} L{M-1},{M-3} L{M-1},{M-1} L{M-3},{M-1} Z M{M+1},{M+1} L{M+3},{M+1} L{M+3},{M+3} L{M+1},{M+3} Z",
    # a censor block
    "menu":        f"M{M-4.5},{M-2} L{M+4.5},{M-2} L{M+4.5},{M+2} L{M-4.5},{M+2} Z",
}
# plate with pixel-stepped corners (two 1 px steps), no curves
_a, _b = 3.5, BTN - 3.5
PLATE = (f"M{_a+2},{_a} L{_b-2},{_a} L{_b-2},{_a+1} L{_b-1},{_a+1} L{_b-1},{_a+2} L{_b},{_a+2} "
         f"L{_b},{_b-2} L{_b-1},{_b-2} L{_b-1},{_b-1} L{_b-2},{_b-1} L{_b-2},{_b} L{_a+2},{_b} "
         f"L{_a+2},{_b-1} L{_a+1},{_b-1} L{_a+1},{_b-2} L{_a},{_b-2} L{_a},{_a+2} L{_a+1},{_a+2} "
         f"L{_a+1},{_a+1} L{_a+2},{_a+1} Z")


def mosaic_rim(density, lit):
    """2 px censor pixels scattered just inside the plate rim."""
    o = []
    for i, (x, y) in enumerate([(x, y) for y in range(5, BTN - 5, 2) for x in range(5, BTN - 5, 2)]):
        edge = min(x - 5, BTN - 7 - x, y - 5, BTN - 7 - y)
        if edge > 2:
            continue
        th = (BAYER[(x // 2) % 4][(y // 2) % 4] + 0.5) / 16
        if th < density * (1.0 - edge * 0.3):
            o.append(rect(x, y, 2, 2, PAL.grey(lit - 4 * ((x * 3 + y) % 3))))
    return o


def button_state(ident, glyph, rim, fill, ink, glow=None, halo=0.0, filled=False, plate=True,
                 mosaic=0.0, lit=30, censor=False):
    o = [f'<g id="{ident}">', rect(0, 0, BTN, BTN, "#000", 'opacity="0"')]
    if halo:
        o.append(f'<circle cx="{M}" cy="{M}" r="{M}" fill="url(#halo)" opacity="{halo}"/>')
    if plate:
        o.append(f'<path d="{PLATE}" fill="{fill}" stroke="{rim}" stroke-width="1"/>')
    if mosaic:
        o += mosaic_rim(mosaic, lit)
    common = 'stroke-linecap="square" stroke-linejoin="miter"'
    paint = f'fill="{ink}"' if filled else 'fill="none"'
    if glow:
        o.append(f'<path d="{glyph}" fill="none" {common} stroke="{glow}" stroke-width="4" opacity="0.20"/>')
        o.append(f'<path d="{glyph}" fill="none" {common} stroke="{glow}" stroke-width="2.6" opacity="0.35"/>')
    o.append(f'<path d="{glyph}" {paint} {common} stroke="{ink}" stroke-width="1.4"/>')
    if censor:   # the close glyph gets struck out by a censor bar
        o += [rect(M - 7, M - 2, 14, 4, "#000"), rect(M - 7, M - 2, 14, 1, PAL.grey(lit + 14))]
    o.append("</g>")
    return "\n".join(o)


def button_svg(name):
    g = GLYPHS[name]
    hot = name == "close"
    filled = name == "menu"
    accent = REC if hot else FLAME
    d = ("<defs>"
         f'<linearGradient id="well" x1="0" y1="0" x2="0" y2="1">{stops((0, PAL.grey(18), 1), (1, PAL.grey(10), 1))}</linearGradient>'
         f'<linearGradient id="wellHot" x1="0" y1="0" x2="0" y2="1">{stops((0, PAL.grey(24 if not hot else 30), 1), (1, PAL.grey(12), 1))}</linearGradient>'
         f'<radialGradient id="halo" cx="0.5" cy="0.5" r="0.5">{stops((0, accent, 0.75), (0.6, accent, 0.25), (1, accent, 0))}</radialGradient>'
         "</defs>")
    states = [
        button_state("active-center", g, BRASS, "url(#well)", PAL.TEXT_DIM if not filled else FLAME, plate=False, filled=filled, glow=FLAME if filled else None),
        button_state("hover-center", g, accent, "url(#wellHot)", PAL.TEXT_HI, glow=accent, halo=0.45, filled=filled,
                     mosaic=0.55, lit=44 if hot else 34, censor=hot),
        button_state("pressed-center", g, accent, PAL.VOID, PEACH, glow=accent, halo=0.85, filled=filled,
                     mosaic=0.9, lit=52 if hot else 40, censor=hot),
        button_state("inactive-center", g, ASH, PAL.grey(11), PAL.TEXT_MUTE, plate=False, filled=filled),
        button_state("hover-inactive-center", g, BRASS_HI, "url(#well)", PAL.TEXT, glow=accent, halo=0.3, filled=filled,
                     mosaic=0.35, lit=28),
        button_state("pressed-inactive-center", g, accent, PAL.VOID, PEACH, halo=0.6, filled=filled, mosaic=0.7, lit=34),
        button_state("deactivated-center", g, ASH_LO, PAL.grey(11), ASH, plate=False, filled=filled),
        button_state("deactivated-inactive-center", g, ASH_LO, PAL.grey(11), ASH_LO, plate=False, filled=filled),
    ]
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{BTN}" height="{BTN}" viewBox="0 0 {BTN} {BTN}">\n'
            + d + "\n" + "\n".join(states) + "\n</svg>\n")


RC = f"""[General]
ActiveTextColor={PAL.csv(PAL.TEXT)},255
InactiveTextColor={PAL.csv(PAL.TEXT_MUTE)},255
TitleAlignment=Center
TitleVerticalAlignment=Center
Animation=160
Shadow=true
TitleShadow=false
UseTextShadow=false

[Layout]
TitleHeight={TH}
TitleEdgeTop={ET}
TitleEdgeBottom={EB}
TitleEdgeLeft=9
TitleEdgeRight=9
TitleEdgeTopMaximized={ET}
TitleEdgeBottomMaximized={EB}
TitleEdgeLeftMaximized=9
TitleEdgeRightMaximized=9
TitleBorderLeft=8
TitleBorderRight=8
ButtonWidth={BTN}
ButtonHeight={BTN}
ButtonSpacing=2
ButtonMarginTop={(TH - BTN) // 2}
ButtonMarginTopMaximized={(TH - BTN) // 2}
ExplicitButtonSpacer=8
PaddingLeft={P}
PaddingRight={P}
PaddingTop={P}
PaddingBottom={P}
BorderLeft={B}
BorderRight={B}
BorderBottom={B}
CornerRadius=0
BorderRadius=0
"""

META = f"""[Desktop Entry]
Name={NAME}
Comment=Monochrome black frame: scanlined title bar over a dithered censor-pixel seam, measurement ticks, crop marks at the corners, unfocused windows censored, close struck out by a censor bar.
Type=Service
X-KDE-ServiceTypes=AuroraeTheme
X-KDE-Library=aurorae
X-KDE-Aurorae-Corner-Radius=0
X-KDE-PluginInfo-Author=splicer scorn (voidrane)
X-KDE-PluginInfo-Version=1.0
X-KDE-PluginInfo-License=GPL-3.0-or-later
"""

if __name__ == "__main__":
    OUT.mkdir(parents=True, exist_ok=True)
    svg = decoration_svg().replace("</svg>", maximized_svg_groups() + "\n</svg>")
    (OUT / "decoration.svg").write_text(svg)
    for name in GLYPHS:
        (OUT / f"{name}.svg").write_text(button_svg(name))
    (OUT / f"{NAME}rc").write_text(RC)
    (OUT / "metadata.desktop").write_text(META)
    stale = OUT / "masks.svg"
    if stale.exists():
        stale.unlink()   # masks now live in decoration.svg, where Aurorae reads them
    print("wrote", OUT)
