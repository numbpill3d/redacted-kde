#!/usr/bin/env python3
"""Capture the workspace through KWin's ScreenShot2 D-Bus API (needs a KWin
started with KWIN_SCREENSHOT_NO_PERMISSION_CHECKS=1).  kwin-capture.py out.png"""
import os, sys, threading
from PyQt6.QtCore import QCoreApplication, QByteArray
from PyQt6.QtDBus import QDBusConnection, QDBusInterface, QDBusUnixFileDescriptor, QDBusMessage
from PyQt6.QtGui import QImage
app = QCoreApplication(sys.argv)
r, w = os.pipe()
chunks = []
def reader():
    with os.fdopen(r, "rb") as f:
        chunks.append(f.read())
t = threading.Thread(target=reader); t.start()
iface = QDBusInterface("org.kde.KWin", "/org/kde/KWin/ScreenShot2", "org.kde.KWin.ScreenShot2", QDBusConnection.sessionBus())
msg = iface.call("CaptureWorkspace", {"include-cursor": False}, QDBusUnixFileDescriptor(w))
os.close(w)
t.join(15)
if msg.type() == QDBusMessage.MessageType.ErrorMessage:
    sys.exit("dbus error: " + msg.errorMessage())
meta = msg.arguments()[0]
W, H, stride, fmt = int(meta["width"]), int(meta["height"]), int(meta["stride"]), int(meta["format"])
data = chunks[0]
img = QImage(data, W, H, stride, QImage.Format(fmt))
img.copy().save(sys.argv[1]); print("saved", sys.argv[1], W, H)
