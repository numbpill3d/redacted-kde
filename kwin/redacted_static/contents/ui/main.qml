/*
 * Redacted Static: the active window is under review.
 *
 * One transparent, click-through overlay follows the active window's frame:
 *   lock    when a window takes focus, four corner brackets snap in on it in
 *           hard steps (a camera acquiring a subject), then cut out; they
 *           re-acquire every 24 s
 *   sweep   a write head crawls the frame edge, stamping black censor bars
 *           behind it; each bar decays to a few mosaic pixels, then nothing
 *   tag     above the top-left corner, the case file: a hex number that
 *           scrambles and settles on focus, and the window title as censor bars
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
    property real lockT: 0          // clock time of the last focus change
    readonly property real speed: 220   // sweep, px per second
    readonly property int cell: 16      // one censor stamp per 16 px of edge
    readonly property int trail: 26     // stamps alive behind the head (~1.9 s)

    onWantedChanged: wanted ? overlay.show() : overlay.hide()
    onTargetChanged: lockT = t
    Component.onCompleted: if (wanted) overlay.show()

    Timer {
        interval: 100; repeat: true; running: overlay.visible
        onTriggered: root.t += 0.1
    }

    function hash(n) { const s = Math.sin(n * 12.9898 + 78.233) * 43758.5453; return s - Math.floor(s) }

    // seconds since the brackets last acquired (focus change, then every 24 s)
    readonly property real lockAge: (t - lockT) % 24

    Window {
        id: overlay
        readonly property real gx: root.target ? root.target.frameGeometry.x : 0
        readonly property real gy: root.target ? root.target.frameGeometry.y : 0
        readonly property real gw: root.target ? root.target.frameGeometry.width : 0
        readonly property real gh: root.target ? root.target.frameGeometry.height : 0
        readonly property real perim: 2 * (gw + gh)
        readonly property real head: perim > 0 ? (root.t * root.speed) % perim : 0
        x: gx - root.margin
        y: gy - root.margin
        width: Math.max(1, gw + 2 * root.margin)
        height: Math.max(1, gh + 2 * root.margin)
        visible: false
        color: "transparent"
        flags: Qt.FramelessWindowHint | Qt.WindowTransparentForInput | Qt.WindowDoesNotAcceptFocus
               | Qt.WindowStaysOnTopHint | Qt.BypassWindowManagerHint | Qt.Tool

        // a point d px clockwise round the frame from its top-left, and whether that edge is horizontal
        function along(d) {
            const m = root.margin, w = gw, h = gh
            d = ((d % perim) + perim) % perim
            if (d < w) return [m + d, m, true]
            d -= w; if (d < h) return [m + w, m + d, false]
            d -= h; if (d < w) return [m + w - d, m + h, true]
            d -= w; return [m, m + h - d, false]
        }

        // ---- lock-on brackets ------------------------------------------------
        Repeater {
            model: 4
            delegate: Item {
                readonly property int sx: index % 2 ? 1 : -1
                readonly property int sy: index > 1 ? 1 : -1
                // four hard steps inward over 0.4 s, hold, cut at 1.1 s
                readonly property int step: Math.min(4, Math.floor(root.lockAge / 0.1))
                readonly property real off: [30, 20, 12, 7, 4][step]
                readonly property real cx: root.margin + (sx > 0 ? overlay.gw : 0) + sx * off
                readonly property real cy: root.margin + (sy > 0 ? overlay.gh : 0) + sy * off
                visible: root.lockAge < 1.1 && !(root.lockAge > 0.5 && root.lockAge < 0.6)   // one blink as it settles
                Rectangle {   // horizontal arm, pointing back along the edge
                    x: sx > 0 ? parent.cx - 18 : parent.cx; y: parent.cy - (sy > 0 ? 1 : 0)
                    width: 19; height: 2; color: step < 4 ? "#3a3a3a" : "#5a5a5a"
                }
                Rectangle {   // vertical arm
                    x: parent.cx - (sx > 0 ? 1 : 0); y: sy > 0 ? parent.cy - 18 : parent.cy
                    width: 2; height: 19; color: step < 4 ? "#3a3a3a" : "#5a5a5a"
                }
            }
        }

        // ---- the sweep: censor stamps behind a crawling write head -------------
        Repeater {
            model: root.trail
            delegate: Item {
                readonly property int c0: Math.floor(overlay.head / root.cell)
                readonly property int ci: c0 - index                      // this stamp's cell on the edge
                readonly property real dist: ci * root.cell
                readonly property real age: (overlay.head - dist) / root.speed   // seconds since stamped
                readonly property var p: overlay.along(dist)
                readonly property bool horiz: p[2]
                // straddle the frame edge: bar centred on the 1 px hairline
                x: horiz ? p[0] : p[0] - 3
                y: horiz ? p[1] - 3 : p[1]
                width: horiz ? root.cell - 2 : 6
                height: horiz ? 6 : root.cell - 2
                visible: overlay.perim > 0

                // fresh: a solid black bar with one lit edge
                Rectangle {
                    anchors.fill: parent
                    visible: age < 0.75
                    color: "#000000"
                    Rectangle {
                        width: horiz ? parent.width : 1; height: horiz ? 1 : parent.height
                        color: "#2e2e2e"
                    }
                }
                // decaying: the bar breaks into a few 3 px censor pixels, fewer as it ages
                Repeater {
                    model: 4
                    delegate: Rectangle {
                        readonly property real h1: root.hash(ci * 4.17 + index * 1.31)
                        readonly property real h2: root.hash(ci * 2.71 + index * 3.07)
                        visible: age >= 0.75 && age < 1.9 && h1 > (age - 0.75) / 1.15
                        width: 3; height: 3
                        x: horiz ? h2 * (root.cell - 5) : (h1 > 0.5 ? 0 : 3)
                        y: horiz ? (h1 > 0.5 ? 0 : 3) : h2 * (root.cell - 5)
                        color: ["#141414", "#1e1e1e", "#2a2a2a", "#363636"][Math.floor(h2 * 4)]
                    }
                }
            }
        }
        // the write head
        Rectangle {
            readonly property var p: overlay.along(overlay.head)
            x: p[2] ? p[0] - 3 : p[0] - 4
            y: p[2] ? p[1] - 4 : p[1] - 3
            width: p[2] ? 6 : 8; height: p[2] ? 8 : 6
            visible: overlay.perim > 0
            color: Math.floor(root.t * 10) % 3 === 0 ? "#4a4a4a" : "#8a8a8a"
        }

        // ---- the case-file tag ------------------------------------------------
        Row {
            x: root.margin + 12; y: root.margin - 17
            spacing: 6
            Text {
                readonly property string hex: {
                    const caption = root.target ? String(root.target.resourceClass) : ""
                    let h = 0
                    for (let i = 0; i < caption.length; i++) h = (h * 31 + caption.charCodeAt(i)) & 0xffff
                    if (root.lockAge < 0.6) {
                        h = Math.floor(root.hash(root.t * 7.1) * 0xffff)   // scrambling while it acquires
                    }
                    return "FILE 0x" + ("000" + h.toString(16).toUpperCase()).slice(-4)
                }
                text: hex
                color: "#3c3c3c"
                font.family: "DepartureMono Nerd Font"
                font.pixelSize: 11
                renderType: Text.NativeRendering
            }
            // the window title, as censor bars (one per word, a few px per letter)
            Repeater {
                model: {
                    const c = root.target ? String(root.target.caption) : ""
                    return c.split(/\s+/).filter(w => w.length).slice(0, 6).map(w => Math.min(64, 4 + w.length * 4))
                }
                delegate: Rectangle {
                    y: 3; width: modelData; height: 7
                    color: "#161616"
                    Rectangle { width: parent.width; height: 1; color: "#2a2a2a" }
                }
            }
        }
    }
}
