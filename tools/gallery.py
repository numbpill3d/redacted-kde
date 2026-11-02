#!/usr/bin/env python3
"""Kvantum widget gallery, grabbed offscreen:
    QT_QPA_PLATFORM=offscreen QT_STYLE_OVERRIDE=kvantum python3 tools/gallery.py <out.png>"""
import sys
from PyQt6.QtWidgets import (QApplication, QWidget, QGridLayout, QVBoxLayout, QHBoxLayout, QPushButton, QCheckBox,
                             QRadioButton, QLineEdit, QComboBox, QSlider, QProgressBar, QSpinBox, QTabWidget,
                             QGroupBox, QListWidget, QTreeWidget, QTreeWidgetItem, QLabel, QTextEdit)
from PyQt6.QtCore import Qt, QTimer

app = QApplication(sys.argv)
w = QWidget(); w.resize(900, 520)
root = QHBoxLayout(w)
left = QVBoxLayout(); root.addLayout(left, 1)
g = QGroupBox("Subject"); gl = QGridLayout(g); left.addWidget(g)
b1 = QPushButton("Redact"); b1.setDefault(True); gl.addWidget(b1, 0, 0)
gl.addWidget(QPushButton("Restore"), 0, 1)
d = QPushButton("Release"); d.setEnabled(False); gl.addWidget(d, 0, 2)
c1 = QCheckBox("Withhold name"); c1.setChecked(True); gl.addWidget(c1, 1, 0)
gl.addWidget(QCheckBox("Blur face"), 1, 1)
r1 = QRadioButton("Mosaic"); r1.setChecked(True); gl.addWidget(r1, 2, 0)
gl.addWidget(QRadioButton("Bar"), 2, 1); gl.addWidget(QRadioButton("Static"), 2, 2)
e = QLineEdit(); e.setPlaceholderText("file reference…"); gl.addWidget(e, 3, 0, 1, 3)
cb = QComboBox(); cb.addItems(["FILE 0x2133", "FILE 0x2134", "[withheld]"]); gl.addWidget(cb, 4, 0)
sp = QSpinBox(); sp.setValue(66); gl.addWidget(sp, 4, 1)
s = QSlider(Qt.Orientation.Horizontal); s.setValue(64); gl.addWidget(s, 5, 0, 1, 3)
pb = QProgressBar(); pb.setValue(72); gl.addWidget(pb, 6, 0, 1, 3)
t = QTextEdit(); t.setPlainText("Subject does not recall the interval.\nThe record is sealed."); left.addWidget(t)
tabs = QTabWidget(); root.addWidget(tabs, 1)
lw = QListWidget(); lw.addItems(["record_01.txt", "record_02.txt", "████████.txt", "static.wav", "do_not_open.txt", "untitled"])
lw.setCurrentRow(2)
tw = QTreeWidget(); tw.setHeaderLabels(["File", "Kind"])
for a, b in (("~/redacted", "hub"), ("aurorae", "frame"), ("plasma", "style"), ("kvantum", "widgets")):
    it = QTreeWidgetItem([a, b]); tw.addTopLevelItem(it); QTreeWidgetItem(it, [f"{a}/README.md", "doc"])
tw.expandAll()
tabs.addTab(lw, "Records"); tabs.addTab(tw, "Archive"); tabs.addTab(QLabel("…"), "Sealed")
w.show()
if len(sys.argv) > 1:
    QTimer.singleShot(400, lambda: (w.grab().save(sys.argv[1]), app.quit()))
w.setWindowTitle("Redacted widgets")
app.exec()
