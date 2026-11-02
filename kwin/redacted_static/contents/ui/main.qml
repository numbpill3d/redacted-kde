/*
 * Redacted Static: the active window comes loose.
 *
 * One transparent, click-through overlay follows the active window's frame:
 *   ghost   a 1 px double of the frame that drifts a few px off and fades in
 *           and out (dissociation)
 *   bars    black censor bars straddling the frame edge, jumping elsewhere
 *   mosaic  ragged chunks of grey pixel blocks that flicker on the edge
 *   specks  static that flashes in place
 * Everything is a pure function of one 10 fps clock, so the overlay redraws at
 * most 10 times a second and only while visible. Hidden for maximised,
 * fullscreen and non-normal windows.
 */
import QtQuick
import QtQuick.Window
import org.kde.kwin

Item {
    id: root
    readonly property var target: Workspace.activeWindow
    readonly property int margin: 40
    readonly property bool wanted: {
        if (!target || !target.normalWindow || target.fullScreen || target.minimized) return false
        const g = target.frameGeometry, o = target.output ? target.output.geometry : null
        if (o && g.width >= o.width - 4 && g.height >= o.height - 64) return false   // maximised
        return g.width > 140 && g.height > 90
    }
    property real t: 0
    onWantedChanged: wanted ? overlay.show() : overlay.hide()
    Component.onCompleted: if (wanted) overlay.show()

    Timer {
        interval: 100; repeat: true; running: overlay.visible
        onTriggered: root.t += 0.1
    }

    function hash(n) { const s = Math.sin(n * 12.9898 + 78.233) * 43758.5453; return s - Math.floor(s) }

    // motes: kind 0 bar, 1 mosaic, 2 speck
    readonly property var motes: [0, 0, 0, 1, 1, 1, 1, 2, 2, 2, 2, 2, 2]

    Window {
        id: overlay
        readonly property real gx: root.target ? root.target.frameGeometry.x : 0
        readonly property real gy: root.target ? root.target.frameGeometry.y : 0
        readonly property real gw: root.target ? root.target.frameGeometry.width : 0
        readonly property real gh: root.target ? root.target.frameGeometry.height : 0
        x: gx - root.margin
        y: gy - root.margin
        width: Math.max(1, gw + 2 * root.margin)
        height: Math.max(1, gh + 2 * root.margin)
        visible: false
        color: "transparent"
        flags: Qt.FramelessWindowHint | Qt.WindowTransparentForInput | Qt.WindowDoesNotAcceptFocus
               | Qt.WindowStaysOnTopHint | Qt.BypassWindowManagerHint | Qt.Tool

        // a point on the frame edge (perimeter walk), plus whether that edge is horizontal
        function along(p) {
            const m = root.margin, w = width - 2 * m, h = height - 2 * m
            let d = ((p % 1) + 1) % 1 * 2 * (w + h)
            if (d < w) return [m + d, m, true]
            d -= w; if (d < h) return [m + w, m + d, false]
            d -= h; if (d < w) return [m + w - d, m + h, true]
            d -= w; return [m, m + h - d, false]
        }

        // the dissociated double
        Rectangle {
            readonly property real dx: 4 + 3 * Math.sin(root.t * 0.23)
            readonly property real dy: -3 + 2 * Math.sin(root.t * 0.17 + 1.3)
            x: root.margin + dx; y: root.margin + dy
            width: overlay.gw; height: overlay.gh
            color: "transparent"
            border.width: 1; border.color: "#2a2a2a"
            opacity: Math.max(0, Math.sin(root.t * 0.31)) * 0.85
        }

        Repeater {
            model: root.motes.length
            delegate: Image {
                readonly property int kind: root.motes[index]
                readonly property real seed: root.hash(index + 0.37)
                readonly property real period: kind === 0 ? 2.6 + 3 * seed : kind === 1 ? 1.4 + 2 * seed : 0.6 + 0.8 * seed
                readonly property real clock: root.t + seed * period
                readonly property int cycle: Math.floor(clock / period)
                readonly property real life: clock / period - cycle
                readonly property real spot: root.hash(index * 31 + cycle * 7.13)
                readonly property var p: overlay.along(spot)
                // on for the middle of each cycle, hard cut in and out like a bad signal
                readonly property bool on: kind === 2 ? life < 0.35 : (life > 0.12 && life < (kind === 0 ? 0.8 : 0.6))
                readonly property int pick: Math.floor(root.hash(index * 9 + cycle) * (kind === 0 ? 4 : kind === 1 ? 6 : 4))
                source: "sprites/" + ["bar_", "mosaic_", "speck_"][kind] + pick + ".png"
                smooth: false
                // bars lie along their edge; on vertical edges they turn
                rotation: kind !== 2 && !p[2] ? 90 : 0
                x: p[0] - width / 2 + (kind === 2 ? (root.hash(cycle + index) - 0.5) * 20 : 0)
                y: p[1] - height / 2 + (kind === 2 ? (root.hash(cycle * 3 + index) - 0.5) * 20 : 0)
                visible: on
                opacity: kind === 1 ? 0.85 : 1
            }
        }
    }
}
