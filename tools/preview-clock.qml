// nested-grab.sh tools/preview-clock.qml out.png 1500 : the clock widget body on a panel strip
import QtQuick
import QtQuick.Window
Window {
    visible: true; width: 260; height: 44; color: "#0c0c0c"
    Loader { anchors.fill: parent; source: Qt.resolvedUrl("clock-harness.qml") }
}
