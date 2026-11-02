/*
 * Redacted scene: the shared animated backdrop (wallpaper, lock screen,
 * splash, login). Authored in 1920x1080 scene pixels and scaled to cover.
 *
 *   art      folder holding face.png, scene.frag.qsb and DepartureMono.otf
 *   running  false pauses every timer (Plasma hides the item when covered)
 *   resolve  1 normal; lower = whole frame mosaicked (the splash animates it)
 *   bright   overall gain
 *   doc      show the redacted document lines on the right
 */
import QtQuick

Item {
    id: root
    property url art: Qt.resolvedUrl("art/")
    property bool running: true
    property int fps: 12
    property real resolve: 1
    property real bright: 1
    property bool doc: true
    readonly property alias monoFont: mono.name
    readonly property real sceneScale: Math.max(width / 1920, height / 1080)

    property real time: 0
    property int frame: 0
    property real glitch: 0
    property real barSlip: 0
    clip: true

    FontLoader { id: mono; source: root.art + "DepartureMono.otf" }

    function hash(n) { const s = Math.sin(n * 12.9898 + 78.233) * 43758.5453; return s - Math.floor(s) }

    Rectangle { anchors.fill: parent; color: "#020202" }

    Timer {
        interval: Math.round(1000 / root.fps); repeat: true; running: root.running
        onTriggered: { root.frame += 1; root.time = root.frame / root.fps }
    }

    // glitch bursts: every 6-20 s the picture tears, and now and then the bar slips
    Timer {
        id: burstClock
        running: root.running; repeat: false
        interval: 6000 + Math.random() * 14000
        onTriggered: {
            burst.slip = Math.random() < 0.45 ? (Math.random() < 0.5 ? -1 : 1) * (14 + Math.random() * 26) : 0
            burst.restart()
            interval = 6000 + Math.random() * 14000
            restart()
        }
    }
    SequentialAnimation {
        id: burst
        property real slip: 0
        ParallelAnimation {
            NumberAnimation { target: root; property: "glitch"; to: 1; duration: 60 }
            NumberAnimation { target: root; property: "barSlip"; to: burst.slip; duration: 50 }
        }
        PauseAnimation { duration: 140 + Math.random() * 220 }
        ParallelAnimation {
            NumberAnimation { target: root; property: "glitch"; to: 0; duration: 380; easing.type: Easing.OutCubic }
            NumberAnimation { target: root; property: "barSlip"; to: 0; duration: 90 }
        }
    }

    Item {
        id: stage
        width: 1920; height: 1080
        scale: root.sceneScale
        transformOrigin: Item.TopLeft
        x: (root.width - width * scale) / 2
        y: (root.height - height * scale) / 2

        ShaderEffect {
            anchors.fill: parent
            property real time: root.time
            property real frame: root.frame
            property real resolve: root.resolve
            property real glitch: root.glitch
            property real barSlip: root.barSlip
            property real bright: root.bright
            property variant face: Image { source: root.art + "face.png"; visible: false; smooth: true }
            fragmentShader: root.art + "scene.frag.qsb"
        }

        // the redacted document: bars a few levels above black. Every so often one
        // bar draws back to show what it hid, then closes again.
        Item {
            visible: root.doc
            opacity: root.bright * Math.min(1, root.resolve * 1.5)
            x: 1260; y: 250
            readonly property var words: ["subject does not recall", "no record of the interval", "observer: unverified",
                "file 0x2133 // closed", "the room was not there", "memory withheld", "identity: [withheld]",
                "last seen: ——", "she watched from outside", "signal lost at 03:12", "do not attempt contact",
                "it was never me", "elapsed time unknown", "the mirror shows static"]
            Repeater {
                id: lines
                model: 22
                delegate: Item {
                    id: line
                    readonly property real seed: root.hash(index + 3.1)
                    readonly property bool gap: seed < 0.12
                    readonly property real w: 140 + 330 * root.hash(index * 7.7)
                    readonly property int lvl: 14 + 2 * Math.floor(3 * root.hash(index * 2.3))
                    property real open: 0          // 0 covered .. 1 drawn back
                    y: index * 26
                    visible: !gap
                    Text {
                        x: 2; y: -1
                        text: parent.parent.words[Math.floor(root.hash(index * 5.3) * parent.parent.words.length)]
                        font.family: root.monoFont; font.pixelSize: 12
                        color: "#3a3a3a"
                        opacity: line.open
                    }
                    Rectangle {
                        x: line.w * line.open; width: line.w * (1 - line.open); height: 14
                        color: Qt.rgba(line.lvl / 255, line.lvl / 255, line.lvl / 255, 1)
                    }
                }
            }
            Timer {
                running: root.running && root.doc; repeat: true
                interval: 4200
                onTriggered: {
                    const it = lines.itemAt(Math.floor(Math.random() * 22))
                    if (it && it.visible && !reveal.running) { reveal.target = it; reveal.restart() }
                }
            }
            SequentialAnimation {
                id: reveal
                property Item target
                NumberAnimation { target: reveal.target; property: "open"; to: 1; duration: 420; easing.type: Easing.OutCubic }
                PauseAnimation { duration: 1400 }
                NumberAnimation { target: reveal.target; property: "open"; to: 0; duration: 120; easing.type: Easing.InQuad }
            }
        }
    }
}
