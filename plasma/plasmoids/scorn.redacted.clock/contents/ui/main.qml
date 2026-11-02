/*
 * Redacted Clock — a square of live static with a censor bar, and the time
 * under two black bars. Hover and the bars slide back. Every so often the
 * signal slips and the bars jerk open for a moment on their own.
 */
import QtQuick
import QtQuick.Layouts
import org.kde.plasma.plasmoid
import org.kde.plasma.core as PlasmaCore

PlasmoidItem {
    id: root
    preferredRepresentation: fullRepresentation
    Plasmoid.backgroundHints: PlasmaCore.Types.NoBackground

    property date now: new Date()
    property int frame: 0
    property real slip: 0
    toolTipMainText: Qt.formatTime(now, "hh:mm")
    toolTipSubText: Qt.formatDate(now, "dddd d MMMM yyyy")

    Timer { interval: 1000; running: true; repeat: true; onTriggered: root.now = new Date() }
    // static at 10 fps while the panel is on screen
    Timer { interval: 100; running: root.expanded || root.visible; repeat: true; onTriggered: root.frame++ }
    Timer {
        interval: 9000 + Math.random() * 14000; running: true; repeat: true
        onTriggered: { glitch.restart(); interval = 9000 + Math.random() * 14000 }
    }
    SequentialAnimation {
        id: glitch
        NumberAnimation { target: root; property: "slip"; to: Math.random() < 0.5 ? -1 : 1; duration: 40 }
        PauseAnimation { duration: 160 }
        NumberAnimation { target: root; property: "slip"; to: 0; duration: 70 }
    }
    FontLoader { id: mono; source: Qt.resolvedUrl("../art/DepartureMono.otf") }

    fullRepresentation: MouseArea {
        id: area
        hoverEnabled: true
        readonly property bool vertical: Plasmoid.formFactor === PlasmaCore.Types.Vertical
        readonly property real thick: vertical ? width : height
        property real open: area.containsMouse ? 1 : Math.abs(root.slip) * 0.6
        Layout.preferredWidth: vertical ? -1 : row.implicitWidth + 8
        Layout.preferredHeight: vertical ? row.implicitHeight + 8 : -1
        Layout.minimumWidth: vertical ? -1 : tv.width

        Behavior on open { NumberAnimation { duration: area.containsMouse ? 260 : 120; easing.type: Easing.OutCubic } }

        Row {
            id: row
            anchors.centerIn: parent
            spacing: 6

            ShaderEffect {
                id: tv
                width: Math.round(Math.max(14, area.thick * 0.56)); height: width
                anchors.verticalCenter: parent.verticalCenter
                property real frame: root.frame
                property real px: width
                property real slip: root.slip
                fragmentShader: Qt.resolvedUrl("../art/static.frag.qsb")
            }

            Row {
                visible: !area.vertical
                anchors.verticalCenter: parent.verticalCenter
                spacing: 0
                Repeater {
                    model: [Qt.formatTime(root.now, "hh"), ":", Qt.formatTime(root.now, "mm")]
                    Item {
                        readonly property bool digits: modelData !== ":"
                        width: txt.implicitWidth; height: txt.implicitHeight
                        Text {
                            id: txt
                            text: modelData
                            font.family: mono.name; font.pixelSize: Math.max(11, Math.round(area.thick * 0.42))
                            color: digits ? "#9a9a9a" : "#3a3a3a"
                        }
                        // the censor bar: slides right to uncover
                        Rectangle {
                            visible: parent.digits
                            x: parent.width * area.open; y: txt.height * 0.18
                            width: (parent.width + 2) * (1 - area.open); height: txt.height * 0.66
                            color: "#000000"
                            Rectangle { width: parent.width; height: 1; color: "#212121" }
                        }
                    }
                }
            }
        }
    }
}
