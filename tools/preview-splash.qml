// nested-grab.sh tools/preview-splash.qml out.png <ms> <stage>
import QtQuick
import QtQuick.Window
Window {
    id: win; visible: true; width: 1920; height: 1080
    readonly property var args: Qt.application.arguments.slice(Qt.application.arguments.indexOf("--") + 1)
    Loader {
        anchors.fill: parent
        source: Qt.resolvedUrl("../plasma/look-and-feel/scorn.redacted/contents/splash/Splash.qml")
        onLoaded: item.stage = parseInt(win.args[0])
    }
}
