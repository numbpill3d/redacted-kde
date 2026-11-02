/*
 * Redacted — KSplash. The face starts as one coarse mosaic and resolves as
 * Plasma's six startup stages arrive; the name unscrambles letter by letter;
 * the progress bar is a row of censor blocks closing one by one.
 */
import QtQuick

Rectangle {
    id: root
    color: "#020202"
    property int stage
    readonly property real u: height / 1080
    readonly property real progress: Math.min(1, stage / 6)

    RedactedScene {
        id: scene
        anchors.fill: parent
        art: Qt.resolvedUrl("art/")
        fps: 15
        resolve: 0.04 + root.progress * 0.96
        Behavior on resolve { NumberAnimation { duration: 900; easing.type: Easing.OutCubic } }
        bright: 0.75 + 0.25 * root.progress
        doc: false
    }

    Item {
        id: block
        x: root.width * 0.70 - width / 2
        anchors.verticalCenter: parent.verticalCenter
        width: 600 * root.u; height: 240 * root.u

        // R E D A C T E D: each letter flickers through block glyphs until its turn comes
        Row {
            id: title
            anchors.horizontalCenter: parent.horizontalCenter
            spacing: 6 * root.u
            readonly property string word: "REDACTED"
            readonly property string noise: "█▓▒░#%&$@"
            property int tick: 0
            Timer { interval: 70; running: true; repeat: true; onTriggered: title.tick++ }
            Repeater {
                model: 8
                Text {
                    readonly property bool settled: index < Math.round(root.progress * 8)
                    text: settled ? title.word.charAt(index)
                                  : title.noise.charAt((title.tick * 7 + index * 13) % title.noise.length)
                    font.family: scene.monoFont
                    font.pixelSize: 58 * root.u
                    color: settled ? "#bdbdbd" : "#3a3a3a"
                }
            }
        }

        Text {
            id: tag
            anchors.horizontalCenter: parent.horizontalCenter
            anchors.top: title.bottom; anchors.topMargin: 14 * root.u
            readonly property var words: ["signal acquired", "identity withheld", "memory partial", "observer detached",
                                          "redacting", "record sealed", "present"]
            text: words[Math.min(root.stage, 6)]
            font.family: scene.monoFont; font.pixelSize: 15 * root.u; font.letterSpacing: 4 * root.u
            color: "#5c5c5c"
        }

        // censor-block progress
        Row {
            anchors.horizontalCenter: parent.horizontalCenter
            anchors.top: tag.bottom; anchors.topMargin: 40 * root.u
            spacing: 6 * root.u
            Repeater {
                model: 6
                Rectangle {
                    readonly property bool shut: index < root.stage
                    width: 64 * root.u; height: 14 * root.u
                    color: shut ? "#000000" : "#111111"
                    border.width: 1; border.color: shut ? "#262626" : "#161616"
                    Behavior on color { ColorAnimation { duration: 260 } }
                }
            }
        }
        Text {
            anchors.right: parent.right; anchors.rightMargin: 18 * root.u
            anchors.bottom: parent.bottom
            text: "0" + Math.min(root.stage, 6) + " / 06"
            font.family: scene.monoFont; font.pixelSize: 11 * root.u
            color: "#3c3c3c"
        }
    }

    OpacityAnimator on opacity { from: 0; to: 1; duration: 300; running: true }
}
