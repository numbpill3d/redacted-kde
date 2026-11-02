"""Redacted palette: one source of truth for every generator.

Monochrome black. Every colour is a neutral grey (r == g == b). Surfaces sit
just above the black that the X1C7's IPS backlight bleed crushes (~#080808),
and accents are only ACCENT_STEP levels lighter than the surface under them:
there, but only just. Text is a readable grey; it is not an accent.

The overtone (panel, splash, wallpaper, boot, login) is static, pixelation,
censor bars and dissociation, still in greys only.
"""
from pathlib import Path

# the face under the static (scorn's own Nightfeed wallpaper, only read)
SOURCE_WALLPAPER = "/home/scorn/Pictures/1b6c35a7-578c-4fb3-a811-1bed374eeaf5.png"
WALLPAPER = str(Path(__file__).resolve().parent / "assets/wallpaper.png")   # tools/build_wallpaper.py

# how much lighter than its surface an accent is (0-255 levels). Tune here.
ACCENT_STEP = 7


def grey(v):
    v = max(0, min(255, round(v)))
    return f"#{v:02x}{v:02x}{v:02x}"


def lv(h):
    return int(h.lstrip("#")[:2], 16)


# surfaces, darkest -> lightest
VOID    = grey(2)     # deepest: shadows, splash/boot base
ABYSS   = grey(8)     # view / text-field background
BASE    = grey(10)    # window background
SURFACE = grey(12)    # header / alt rows / panel
RAISED  = grey(15)    # buttons
EDGE    = grey(12 + ACCENT_STEP + 2)   # borders: barely there
EDGE_HI = grey(12 + ACCENT_STEP * 2)

# shade: the dim greys of the face under the static
SHADE_LO = grey(20)
SHADE    = grey(34)
SHADE_HI = grey(52)
PALE     = grey(96)   # brightest thing on the wallpaper (eye whites)

# accent: "only slightly less black"
ACCENT_DEEP = grey(lv(BASE) + 2)
ACCENT_LO   = grey(lv(BASE) + ACCENT_STEP - 2)
ACCENT      = grey(lv(SURFACE) + ACCENT_STEP)        # focus, hover, seams
ACCENT_HI   = grey(lv(SURFACE) + ACCENT_STEP * 2)    # pressed / active
ACCENT_GLOW = grey(lv(SURFACE) + ACCENT_STEP * 3)

# text: grey, readable
TEXT      = grey(150)
TEXT_HI   = grey(214)    # selected / hovered text brightens: that is how a selection reads
TEXT_DIM  = grey(92)
TEXT_MUTE = grey(56)

# states: told apart by brightness alone
NEGATIVE = grey(232)
NEUTRAL  = grey(176)
POSITIVE = grey(120)
LINK     = grey(190)
VISITED  = grey(120)

# selection: a faint lift, with the text going bright on top
SELECT    = grey(lv(SURFACE) + ACCENT_STEP + 4)
SELECT_HI = grey(lv(SURFACE) + ACCENT_STEP * 2 + 4)

FONT_UI = "DepartureMono Nerd Font"


def rgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def csv(h):
    return ",".join(map(str, rgb(h)))
