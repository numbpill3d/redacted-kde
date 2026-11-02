#!/usr/bin/env python3
"""Render a QML file and save a PNG after N ms:  grab.py file.qml out.png [ms] [-- args for the qml]

Uses the offscreen platform unless QT_QPA_PLATFORM is set. Shaders need a GPU:
run it through tools/nested-grab.sh (headless nested KWin) for that.
The QML sees everything after "--" via Qt.application.arguments.
"""
import os, sys
from PyQt6.QtGui import QGuiApplication
from PyQt6.QtQml import QQmlApplicationEngine
from PyQt6.QtCore import QTimer, QUrl
from PyQt6.QtQuick import QQuickWindow
from PyQt6 import sip

extra = sys.argv[sys.argv.index("--"):] if "--" in sys.argv else ["--"]
app = QGuiApplication(sys.argv[:1] + ([] if os.environ.get("QT_QPA_PLATFORM") else ["-platform", "offscreen"]) + extra)
eng = QQmlApplicationEngine()
eng.warnings.connect(lambda ws: [print("QML:", w.toString(), flush=True) for w in ws])
eng.load(QUrl.fromLocalFile(os.path.abspath(sys.argv[1])))
if not eng.rootObjects():
    sys.exit("load failed")
win = eng.rootObjects()[0]


def shot():
    try:
        sip.cast(win, QQuickWindow).grabWindow().save(sys.argv[2])
    except Exception as e:          # an exception escaping a slot aborts PyQt
        print("grab failed:", e, flush=True)
    print("saved", sys.argv[2], flush=True)
    app.quit()


QTimer.singleShot(int(sys.argv[3]) if len(sys.argv) > 3 else 1500, shot)
app.exec()
