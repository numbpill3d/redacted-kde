#!/usr/bin/env python3
"""Render the real redacted_censor fragment shader offline (Qt OpenGL) onto a
captured window, composite over a desktop capture, and write frames + a GIF.
   render-unfurl.py window.png bg.png out.gif [x y]"""
import sys, math
from pathlib import Path
import numpy as np
from PIL import Image
from PyQt6.QtGui import QGuiApplication, QOpenGLContext, QOffscreenSurface, QSurfaceFormat
from PyQt6.QtOpenGL import (QOpenGLShaderProgram, QOpenGLShader, QOpenGLFramebufferObject, QOpenGLTexture,
                            QOpenGLFramebufferObjectFormat, QOpenGLBuffer, QOpenGLVertexArrayObject)
R = Path(__file__).resolve().parent.parent
app = QGuiApplication(sys.argv)
win_p, bg_p, out_p = sys.argv[1], sys.argv[2], sys.argv[3]
X, Y = (int(sys.argv[4]), int(sys.argv[5])) if len(sys.argv) > 5 else (480, 250)
CROP = tuple(map(int, sys.argv[6].split(","))) if len(sys.argv) > 6 else None   # x0,y0,x1,y1 of the output view

fmt = QSurfaceFormat(); fmt.setVersion(3, 3); fmt.setProfile(QSurfaceFormat.OpenGLContextProfile.CoreProfile)
ctx = QOpenGLContext(); ctx.setFormat(fmt); assert ctx.create(), "no GL context"
surf = QOffscreenSurface(); surf.setFormat(ctx.format()); surf.create()
assert ctx.makeCurrent(surf)
from OpenGL import GL as gl  # raw calls: PyQt6 has no QOpenGLFunctions

src = (R / "kwin/redacted_censor/contents/shaders/redacted-censor_core.frag").read_text()
src = "\n".join(l for l in src.splitlines() if not l.startswith("#define KWIN") and not l.startswith("#define PLASMA6")
                and not l.startswith("#version"))
frag = "#version 330 core\n#define KWIN\n#define texture2D texture\n" + src
vert = """#version 330 core
in vec2 pos; out vec2 texcoord0;
void main(){ texcoord0 = vec2(pos.x*0.5+0.5, 0.5-pos.y*0.5); gl_Position = vec4(pos,0.0,1.0); }"""
prog = QOpenGLShaderProgram()
assert prog.addShaderFromSourceCode(QOpenGLShader.ShaderTypeBit.Vertex, vert), prog.log()
if not prog.addShaderFromSourceCode(QOpenGLShader.ShaderTypeBit.Fragment, frag):
    sys.exit(prog.log())
prog.bindAttributeLocation("pos", 0)
assert prog.link(), prog.log()

win = Image.open(win_p).convert("RGBA")
W, H = win.size
from PyQt6.QtGui import QImage
tex = QOpenGLTexture(QImage(win_p).convertToFormat(QImage.Format.Format_RGBA8888_Premultiplied))
tex.setMinMagFilters(QOpenGLTexture.Filter.Linear, QOpenGLTexture.Filter.Linear)
ff = QOpenGLFramebufferObjectFormat(); ff.setInternalTextureFormat(0x8058)  # GL_RGBA8
fbo = QOpenGLFramebufferObject(W, H, ff)

# fullscreen quad
quad = np.array([-1, -1, 1, -1, -1, 1, 1, 1], dtype=np.float32)
vao = QOpenGLVertexArrayObject(); vao.create(); vao.bind()
vbo = QOpenGLBuffer(QOpenGLBuffer.Type.VertexBuffer); vbo.create(); vbo.bind()
vbo.allocate(quad.tobytes(), quad.nbytes)
prog.bind(); prog.enableAttributeArray(0); prog.setAttributeBuffer(0, 0x1406, 0, 2)  # GL_FLOAT
GL_COLOR_BUFFER_BIT, GL_TRIANGLE_STRIP, GL_TEXTURE0 = 0x4000, 0x0005, 0x84C0


def render(progress, opening, seed=0.37):
    fbo.bind()
    gl.glViewport(0, 0, W, H); gl.glClearColor(0, 0, 0, 0); gl.glClear(GL_COLOR_BUFFER_BIT)
    prog.bind()
    gl.glActiveTexture(GL_TEXTURE0); tex.bind()
    prog.setUniformValue("sampler", 0)
    prog.setUniformValue("textureWidth", W); prog.setUniformValue("textureHeight", H)
    prog.setUniformValue("uProgress", float(progress)); prog.setUniformValue("uDuration", 0.38)
    prog.setUniformValue("uForOpening", bool(opening)); prog.setUniformValue("uIsFullscreen", False)
    prog.setUniformValue("uSeed", float(seed))
    from PyQt6.QtGui import QVector4D
    prog.setUniformValue("uColor", QVector4D(0.6, 0.6, 0.6, 1.0))
    prog.setUniformValue("uInk", QVector4D(0.0, 0.0, 0.0, 1.0))
    vao.bind(); gl.glDrawArrays(GL_TRIANGLE_STRIP, 0, 4)
    img = fbo.toImage(True).convertToFormat(QImage.Format.Format_RGBA8888)
    fbo.release()
    ptr = img.constBits(); ptr.setsize(img.sizeInBytes())
    a = np.frombuffer(ptr, np.uint8).reshape(img.height(), img.bytesPerLine() // 4, 4)[:, :W].copy()
    return Image.fromarray(a, "RGBA")


bg = Image.open(bg_p).convert("RGBA")
def view(im):
    im = im.convert("RGB")
    return im.crop(CROP) if CROP else im.resize((im.width // 2, im.height // 2), Image.LANCZOS)


def out_cubic(t): return 1 - (1 - t) ** 3
def in_cubic(t): return t ** 3

frames, durs = [], []
def frame(progress, opening, ms):
    layer = render(progress, opening)
    s = (0.965 + 0.035 * out_cubic(progress)) if opening else (1.0 - 0.035 * in_cubic(progress))
    if s != 1.0:
        layer = layer.resize((round(W * s), round(H * s)), Image.LANCZOS)
    c = bg.copy()
    c.alpha_composite(layer, (X + (W - layer.width) // 2, Y + (H - layer.height) // 2))
    frames.append(view(c)); durs.append(ms)

frames.append(view(bg)); durs.append(700)
N = 22
for i in range(1, N + 1):
    frame(i / N, True, 45)
durs[-1] = 1600
for i in range(1, 16 + 1):
    frame(i / 16, False, 40)
frames.append(frames[0]); durs.append(600)
outd = Path(out_p).with_suffix("")
outd.mkdir(exist_ok=True)
for i, f in enumerate(frames):
    f.save(outd / f"f{i:03d}.png")
frames[0].save(out_p, save_all=True, append_images=frames[1:], duration=durs, loop=0, optimize=True)
print("gif ->", out_p, len(frames), "frames")
