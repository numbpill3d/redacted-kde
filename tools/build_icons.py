#!/usr/bin/env python3
"""Redacted icon theme: grey-black places/folders over Tela-circle-dark.

Copies only the places/ dirs (symlinks kept), swaps Tela's blue for the
monochrome greys, adds a censored-mosaic launcher icon. Everything else inherits.
"""
import re, shutil, sys
from pathlib import Path
R = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(R))
import palette as P

SRC = Path.home() / ".local/share/icons/Tela-circle-dark"
OUT = R / "icons/Redacted"
if OUT.exists():
    shutil.rmtree(OUT)
OUT.mkdir(parents=True)

SWAP = {"#5294e2": P.grey(44), "#4877b1": P.grey(30), "#ffffff": P.grey(118)}
dirs = []
for d in sorted(SRC.glob("*/places")):
    rel = d.relative_to(SRC)
    dst = OUT / rel
    shutil.copytree(d, dst, symlinks=True)
    dirs.append(str(rel))
    for f in dst.iterdir():
        if f.is_symlink() or f.suffix != ".svg":
            continue
        t = f.read_text()
        t = re.sub(r"#[0-9a-fA-F]{6}\b", lambda m: SWAP.get(m.group(0).lower(), m.group(0)), t)
        f.write_text(t)

# drop links into dirs we don't copy (devices/, actions/): Tela supplies those via Inherits
for f in OUT.rglob('*'):
    if f.is_symlink() and not f.exists():
        f.unlink()

# launcher: a mosaic square under a censor bar
_rnd = __import__("random").Random(9)
_px = "".join(f'<rect x="{16 + 4 * i}" y="{16 + 4 * j}" width="4" height="4" fill="{P.grey(_rnd.choice((14, 20, 28, 40, 58)))}"/>'
              for i in range(8) for j in range(8))
launcher = f'''<svg xmlns="http://www.w3.org/2000/svg" width="64" height="64" viewBox="0 0 64 64">
 <circle cx="32" cy="32" r="29" fill="{P.VOID}" stroke="{P.EDGE_HI}" stroke-width="2"/>
 {_px}
 <rect x="11" y="27" width="42" height="9" fill="#000"/>
 <rect x="11" y="27" width="42" height="1" fill="{P.ACCENT_GLOW}"/>
</svg>
'''
for d in ("scalable/places", "scalable/apps"):
    (OUT / d).mkdir(parents=True, exist_ok=True)
    for n in ("start-here", "start-here-kde", "start-here-kde-plasma", "start-here-archlinux", "distributor-logo", "kde", "plasma",
              "start-here-symbolic", "start-here-kde-symbolic", "start-here-kde-plasma-symbolic", "distributor-logo-symbolic"):
        p = OUT / d / f"{n}.svg"
        if p.is_symlink() or p.exists():
            p.unlink()
        p.write_text(launcher)
for p in (OUT / "16/places").glob("start-here*.svg"):
    p.unlink()   # let the scalable one win at every size
if "scalable/apps" not in dirs:
    dirs.append("scalable/apps")

src_index = (SRC / "index.theme").read_text()
sections = []
for d in dirs:
    m = re.search(r"^\[" + re.escape(d) + r"\]\n(.*?)(?=^\[|\Z)", src_index, re.S | re.M)
    body = m.group(1).strip() if m else "Size=64\nMinSize=16\nMaxSize=512\nType=Scalable"
    if d == "scalable/apps" and not m:
        body = "Context=Applications\nSize=64\nMinSize=16\nMaxSize=512\nType=Scalable"
    sections.append(f"[{d}]\n{body}\n")
head = f"""[Icon Theme]
Name=Redacted
Comment=Grey-black folders over Tela circle dark; a censored launcher
Inherits=Tela-circle-dark,breeze-dark,hicolor
Example=folder
FollowsColorScheme=false
DisplayDepth=32
LinkOverlay=link_overlay
LockOverlay=lock_overlay
ZipOverlay=zip_overlay
DesktopDefault=48
DesktopSizes=16,22,32,48,64,96,128,256
ToolbarDefault=22
ToolbarSizes=16,22,32,48
MainToolbarDefault=22
MainToolbarSizes=16,22,32,48
SmallDefault=16
SmallSizes=16,22,32,48
PanelDefault=48
PanelSizes=16,22,32,48,64,128,256
DialogDefault=32
DialogSizes=16,22,32,48,64,128,256
Directories={",".join(dirs)}

"""
(OUT / "index.theme").write_text(head + "\n".join(sections))
print("icons ->", OUT, len(dirs), "dirs")
