// QT_QPA_PLATFORM=offscreen qml6 tools/preview-scene.qml -- <out.png> <ms> [resolve] [glitch]
import QtQuick
import QtQuick.Window
Window {
    id: win; visible: true; width: 1920; height: 1080
    readonly property var args: Qt.application.arguments.slice(Qt.application.arguments.indexOf("--") + 1)
    Loader {
        id: l; anchors.fill: parent
        source: Qt.resolvedUrl("../build/preview/RedactedScene.qml")
        onLoaded: {
            item.art = Qt.resolvedUrl("../build/preview/art/")
            if (win.args.length > 2) item.resolve = parseFloat(win.args[2])
            if (win.args.length > 3) { item.glitch = parseFloat(win.args[3]); item.barSlip = 30 * item.glitch }
        }
    }
    Timer { interval: parseInt(win.args[1]); running: true; onTriggered: l.item.grabToImage(function (r) { r.saveToFile(win.args[0]); Qt.quit() }) }
}
