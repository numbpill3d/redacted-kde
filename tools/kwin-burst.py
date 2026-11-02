#!/usr/bin/env python3
"""Grab a burst of workspace frames through KWin's ScreenShot2 D-Bus API
(KWin started with KWIN_SCREENSHOT_NO_PERMISSION_CHECKS=1).
   kwin-burst.py out-dir frames [launch-cmd]
If launch-cmd is given it is started right after the first frame, so the
burst covers the window's open animation."""
import os, sys, threading, time, subprocess
from PyQt6.QtCore import QCoreApplication
from PyQt6.QtDBus import QDBusConnection, QDBusInterface, QDBusUnixFileDescriptor, QDBusMessage
from PyQt6.QtGui import QImage
app = QCoreApplication(sys.argv)
out, n = sys.argv[1], int(sys.argv[2])
cmd = sys.argv[3] if len(sys.argv) > 3 else None
os.makedirs(out, exist_ok=True)
iface = QDBusInterface("org.kde.KWin", "/org/kde/KWin/ScreenShot2", "org.kde.KWin.ScreenShot2", QDBusConnection.sessionBus())


def grab(path):
    r, w = os.pipe()
    chunks = []
    t = threading.Thread(target=lambda: chunks.append(os.fdopen(r, "rb").read())); t.start()
    msg = iface.call("CaptureWorkspace", {"include-cursor": False}, QDBusUnixFileDescriptor(w))
    os.close(w); t.join(15)
    if msg.type() == QDBusMessage.MessageType.ErrorMessage:
        sys.exit("dbus error: " + msg.errorMessage())
    m = msg.arguments()[0]
    QImage(chunks[0], int(m["width"]), int(m["height"]), int(m["stride"]), QImage.Format(int(m["format"]))).copy().save(path)


t0 = time.time()
for i in range(n):
    grab(f"{out}/f{i:03d}.png")
    if i == 0 and cmd:
        subprocess.Popen(cmd, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    with open(f"{out}/times.txt", "a") as f:
        f.write(f"{i} {time.time() - t0:.3f}\n")
print("frames", n, "in", round(time.time() - t0, 2), "s")
