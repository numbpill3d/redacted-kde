/*
 * redacted — SDDM theme (Qt6 greeter, pure QtQuick, no shaders)
 * A tape dubbed in blood, on playback: the wallpaper face under scanlines, grain,
 * a rolling tracking band and the odd tape tear; a VCR on-screen display; a
 * blood-black glass panel with a crimson glow seam. All motion is image swaps and
 * transforms, cheap on the UHD 620.
 */

import QtQuick
import QtQuick.Window

Item {
    id: root
    width:  Screen.width
    height: Screen.height

    // shared with ~/redacted/palette.py
    readonly property color cVoid:    "#0a0304"
    readonly property color cAbyss:   "#0e0506"
    readonly property color cBase:    "#150809"
    readonly property color cSurface: "#1d0a0d"
    readonly property color cRaised:  "#290e12"
    readonly property color cEdge:    "#45141b"
    readonly property color cEdgeHi:  "#641c25"
    readonly property color cOxblood:  "#98182b"
    readonly property color cFlesh:    "#e88a90"
    readonly property color cCrimDeep: "#3a0911"
    readonly property color cCrimLo:   "#8c1024"
    readonly property color cCrim:     "#dc1f3c"
    readonly property color cCrimHi:   "#ff5368"
    readonly property color cCrimGlow: "#ffa3ad"
    readonly property color cText:    "#e8d2d0"
    readonly property color cTextHi:  "#fff1ef"
    readonly property color cDim:     "#a87e80"
    readonly property color cMute:    "#6b4549"
    readonly property color cRec:     "#ff6a2b"

    readonly property real   u:     height / 1080
    readonly property string mono:  osdFont.status === FontLoader.Ready ? osdFont.font.family : "monospace"
    readonly property bool   glitchy: (config.glitches || "true").toString() !== "false"

    property bool   loginPending: false
    property string errorMsg:     ""
    property var    sessionNames: []
    property int    sessionIdx:   sessionModel.lastIndex >= 0 ? sessionModel.lastIndex : 0
    property string sessionLabel: sessionNames.length > sessionIdx ? sessionNames[sessionIdx] : "default session"
    property date   now:          new Date()
    property int    counter:      0
    property int    noiseFrame:   0
    property real   jitter:       0
    property alias  nameField:    nameBox.input
    property alias  passField:    passBox.input

    FontLoader { id: osdFont;  source: "fonts/TerminessNerdFontMono-Regular.ttf" }
    FontLoader { id: osdBold;  source: "fonts/TerminessNerdFontMono-Bold.ttf" }

    Timer { interval: 1000; running: true; repeat: true; onTriggered: { root.now = new Date(); root.counter++ } }
    Timer { interval: 70;   running: true; repeat: true; onTriggered: root.noiseFrame = (root.noiseFrame + 1 + Math.floor(Math.random() * 4)) % 6 }

    // sessionModel exposes names only through delegates
    Repeater {
        model: sessionModel
        Item {
            visible: false
            Component.onCompleted: {
                var a = root.sessionNames.slice()
                while (a.length <= index) a.push("")
                a[index] = model.name; root.sessionNames = a
            }
        }
    }

    function cycleSession(d) {
        if (sessionNames.length === 0) return
        sessionIdx = (sessionIdx + d + sessionNames.length) % sessionNames.length
    }

    function doLogin() {
        if (loginPending) return
        if (nameField.text.length === 0) { nameField.forceActiveFocus(); return }
        if (passField.text.length === 0) { passField.forceActiveFocus(); return }
        loginPending = true; errorMsg = ""
        sddm.login(nameField.text, passField.text, sessionIdx)
    }

    function pad(n) { return n < 10 ? "0" + n : "" + n }
    function tapeCounter(s) { return Math.floor(s / 3600) + ":" + pad(Math.floor(s / 60) % 60) + ":" + pad(s % 60) }
    function osdDate(d) {
        var m = ["JAN", "FEB", "MAR", "APR", "MAY", "JUN", "JUL", "AUG", "SEP", "OCT", "NOV", "DEC"]
        return m[d.getMonth()] + ". " + pad(d.getDate()) + " " + d.getFullYear()
    }
    function osdTime(d) {
        var h = d.getHours(), ap = h < 12 ? "AM" : "PM"
        h = h % 12; if (h === 0) h = 12
        return ap + " " + h + ":" + pad(d.getMinutes())
    }

    Connections {
        target: sddm
        function onLoginFailed() {
            root.loginPending = false
            root.errorMsg = "TRACKING ERROR  //  ACCESS DENIED"
            passField.text = ""; passField.forceActiveFocus()
            shake.restart(); glitch.restart()
        }
        function onLoginSucceeded() { powerOff.start() }
    }

    Component.onCompleted: {
        nameField.text = userModel.lastUser
        var first = nameField.text.length > 0 ? passField : nameField
        first.forceActiveFocus()
        powerOn.start()
    }

    // ---- the tape ------------------------------------------------------------
    Rectangle { anchors.fill: parent; color: root.cVoid }

    Item {
        id: screen
        anchors.fill: parent
        transformOrigin: Item.Center

        Item {
            id: picture
            anchors.fill: parent
            transform: Translate { x: root.jitter }
            Image {
                id: bg
                anchors.fill: parent
                source: config.background || "assets/background.png"
                fillMode: Image.PreserveAspectCrop
                horizontalAlignment: Image.AlignLeft
                // slow drift, like a tape that never quite settles
                SequentialAnimation on scale {
                    loops: Animation.Infinite
                    NumberAnimation { from: 1.0;   to: 1.018; duration: 16000; easing.type: Easing.InOutSine }
                    NumberAnimation { from: 1.018; to: 1.0;   duration: 16000; easing.type: Easing.InOutSine }
                }
            }
            // chroma bleed: a faint copy riding a few px to the right
            Image {
                anchors.fill: bg
                transform: Translate { x: 3 * root.u }
                source: bg.source; fillMode: bg.fillMode; horizontalAlignment: bg.horizontalAlignment
                scale: bg.scale; opacity: 0.10
            }
        }

        // tape tear: a slice of the picture shoved sideways during a glitch
        Item {
            id: tear
            visible: false
            width: parent.width; height: 46 * root.u
            clip: true
            Image {
                y: -tear.y; x: 28 * root.u
                width: root.width; height: root.height
                source: bg.source; fillMode: bg.fillMode; horizontalAlignment: bg.horizontalAlignment
                scale: bg.scale
            }
            Rectangle { anchors.fill: parent; color: root.cFlesh; opacity: 0.06 }
        }

        Image { anchors.fill: parent; source: "assets/scanlines-1080.png"; smooth: false }
        Image {
            anchors.fill: parent; smooth: false; opacity: 0.55
            source: "assets/noise_" + root.noiseFrame + ".png"
        }
        // rolling tracking band
        Image {
            id: band
            width: parent.width; height: 90 * root.u
            source: "assets/tracking.png"
            opacity: 0.8
            NumberAnimation on y { from: -120 * root.u; to: root.height + 40 * root.u; duration: 11000; loops: Animation.Infinite }
        }
        Image { anchors.fill: parent; source: "assets/vignette.png" }
    }

    // ---- glitch --------------------------------------------------------------
    SequentialAnimation {
        id: glitch
        ScriptAction { script: { tear.y = (0.15 + Math.random() * 0.7) * root.height; tear.visible = true } }
        NumberAnimation { target: root; property: "jitter"; to: -9 * root.u; duration: 40 }
        NumberAnimation { target: root; property: "jitter"; to:  6 * root.u; duration: 50 }
        ScriptAction { script: tear.y = (0.15 + Math.random() * 0.7) * root.height }
        NumberAnimation { target: root; property: "jitter"; to: -3 * root.u; duration: 40 }
        NumberAnimation { target: root; property: "jitter"; to:  0;          duration: 60 }
        ScriptAction { script: tear.visible = false }
    }
    Timer {
        id: glitchClock
        running: root.glitchy; repeat: true
        interval: 9000
        onTriggered: { glitch.restart(); interval = 7000 + Math.random() * 9000 }
    }

    // ---- on-screen display ---------------------------------------------------
    // OSD text: hard bone-white core over two soft crimson copies
    component Osd: Item {
        id: osd
        property alias text: core.text
        property real  size: 30
        property color ink: root.cTextHi
        property color glow: root.cCrim
        property bool  bold: true
        implicitWidth: core.implicitWidth; implicitHeight: core.implicitHeight
        Text { x: -1.5 * root.u; y: 0; text: core.text; font: core.font; color: osd.glow; opacity: 0.45 }
        Text { x:  1.5 * root.u; y: 1 * root.u; text: core.text; font: core.font; color: osd.glow; opacity: 0.30 }
        Text {
            id: core
            font.family: root.mono; font.pixelSize: osd.size * root.u
            font.bold: osd.bold; font.letterSpacing: 2 * root.u
            color: osd.ink
        }
    }

    Item {
        id: hud
        anchors.fill: parent
        anchors.margins: 56 * root.u

        Osd {
            id: mode
            size: 46
            text: root.errorMsg.length ? "STOP ■" : (root.loginPending ? "FF ▶▶" : "PLAY ▶")
            ink: root.errorMsg.length ? "#ffc2a3" : root.cTextHi
            glow: root.errorMsg.length ? root.cRec : root.cCrim
            // PLAY flashes for a while, like a deck that just engaged
            SequentialAnimation on opacity {
                running: !root.loginPending
                loops: 6
                NumberAnimation { to: 0.15; duration: 1 }
                PauseAnimation { duration: 500 }
                NumberAnimation { to: 1; duration: 1 }
                PauseAnimation { duration: 500 }
            }
        }
        Osd { anchors.top: mode.bottom; anchors.topMargin: 6 * root.u; size: 22; bold: false; ink: root.cText
              text: (config.channel || "CH 03") + "   SP" }

        Column {
            anchors.right: parent.right
            spacing: 4 * root.u
            Osd { anchors.right: parent.right; size: 46; text: root.osdTime(root.now) }
            Osd { anchors.right: parent.right; size: 22; bold: false; ink: root.cText; text: root.osdDate(root.now) }
        }

        Row {
            anchors.left: parent.left; anchors.bottom: parent.bottom
            spacing: 22 * root.u
            Osd { size: 22; text: "CNT " + root.tapeCounter(root.counter) }
            Osd { size: 22; bold: false; ink: root.cDim; glow: root.cCrimDeep; text: "@ " + (sddm.hostName || "localhost").toUpperCase() }
        }
    }

    // ---- glass panel ---------------------------------------------------------
    component Field: Item {
        id: field
        property alias input: input
        property string label: ""
        property bool secret: false
        signal accepted()
        width: parent.width; height: 74 * root.u
        Text {
            text: field.label
            font.family: root.mono; font.pixelSize: 15 * root.u; font.letterSpacing: 3 * root.u
            color: input.activeFocus ? root.cCrimHi : root.cDim
        }
        // glow halo when focused
        Rectangle {
            x: -3 * root.u; y: 22 * root.u - 3 * root.u
            width: well.width + 6 * root.u; height: well.height + 6 * root.u
            color: "transparent"; radius: 5 * root.u
            border.width: 3 * root.u; border.color: root.cCrim
            opacity: input.activeFocus ? 0.22 : 0
            Behavior on opacity { NumberAnimation { duration: 180 } }
        }
        Rectangle {
            id: well
            y: 22 * root.u; width: parent.width; height: 46 * root.u
            radius: 3 * root.u
            color: root.cAbyss
            border.width: 1; border.color: input.activeFocus ? root.cCrim : root.cEdge
            TextInput {
                id: input
                anchors.fill: parent; anchors.leftMargin: 14 * root.u; anchors.rightMargin: 14 * root.u
                verticalAlignment: TextInput.AlignVCenter
                clip: true
                font.family: root.mono; font.pixelSize: 22 * root.u
                color: field.secret ? "transparent" : root.cTextHi
                selectionColor: root.cCrimDeep; selectedTextColor: root.cTextHi
                echoMode: field.secret ? TextInput.Password : TextInput.Normal
                cursorDelegate: Item {}
                activeFocusOnTab: true
                enabled: !root.loginPending
                Keys.onReturnPressed: field.accepted()
                Keys.onEnterPressed: field.accepted()
            }
            // password shown as a strip of tape blocks
            Row {
                id: blocks
                visible: field.secret
                anchors.verticalCenter: parent.verticalCenter
                x: 14 * root.u
                spacing: 4 * root.u
                Repeater {
                    model: field.secret ? Math.min(input.length, 24) : 0
                    Rectangle {
                        width: 9 * root.u; height: 18 * root.u
                        color: index === input.length - 1 ? root.cCrimGlow : root.cCrim
                        opacity: 0.55 + 0.45 * ((index * 7) % 5) / 4
                    }
                }
            }
            Rectangle {
                visible: input.activeFocus
                width: 10 * root.u; height: 3 * root.u
                y: parent.height / 2 + 9 * root.u
                x: 14 * root.u + (field.secret ? blocks.width + (input.length > 0 ? 4 * root.u : 0)
                                               : Math.min(input.cursorRectangle.x + 2 * root.u, well.width - 30 * root.u))
                color: root.cCrimGlow
                SequentialAnimation on opacity {
                    loops: Animation.Infinite
                    NumberAnimation { to: 0.1; duration: 1 }
                    PauseAnimation { duration: 480 }
                    NumberAnimation { to: 1; duration: 1 }
                    PauseAnimation { duration: 480 }
                }
            }
        }
        MouseArea { anchors.fill: parent; onClicked: input.forceActiveFocus() }
    }

    component Transport: Item {
        id: btn
        property string glyph: ""
        property string text: ""
        property bool   primary: false
        signal clicked()
        activeFocusOnTab: true
        readonly property bool hot: area.containsMouse || btn.activeFocus
        width: label.implicitWidth + 36 * root.u; height: (primary ? 48 : 36) * root.u
        Rectangle {
            anchors.fill: parent; radius: 3 * root.u
            color: btn.primary ? (btn.hot ? root.cCrimLo : root.cCrimDeep) : (btn.hot ? root.cRaised : Qt.rgba(0.09, 0.03, 0.04, 0.55))
            border.width: 1; border.color: btn.hot ? root.cCrimHi : (btn.primary ? root.cCrim : root.cEdge)
            Behavior on color { ColorAnimation { duration: 140 } }
        }
        Rectangle {
            anchors.fill: parent; anchors.margins: -4 * root.u; radius: 6 * root.u
            color: "transparent"; border.width: 3 * root.u; border.color: root.cCrim
            opacity: btn.hot ? 0.25 : 0
            Behavior on opacity { NumberAnimation { duration: 140 } }
        }
        Text {
            id: label
            anchors.centerIn: parent
            text: btn.glyph + "  " + btn.text
            font.family: root.mono; font.bold: true
            font.pixelSize: (btn.primary ? 19 : 15) * root.u; font.letterSpacing: 3 * root.u
            color: btn.hot || btn.primary ? root.cTextHi : root.cDim
        }
        MouseArea { id: area; anchors.fill: parent; hoverEnabled: true; cursorShape: Qt.PointingHandCursor; onClicked: btn.clicked() }
        Keys.onReturnPressed: clicked()
        Keys.onEnterPressed: clicked()
        Keys.onSpacePressed: clicked()
    }

    Item {
        id: panel
        width: 560 * root.u; height: inner.implicitHeight + 76 * root.u
        x: root.width * 0.705 - width / 2
        anchors.verticalCenter: parent.verticalCenter
        anchors.verticalCenterOffset: 10 * root.u

        // crimson bloom behind the glass
        Image {
            source: "assets/glow.png"
            anchors.centerIn: parent
            width: parent.width * 1.9; height: parent.height * 1.5
            opacity: 0.13
        }
        Rectangle {
            id: glass
            anchors.fill: parent
            radius: 6 * root.u
            color: Qt.rgba(0.082, 0.031, 0.035, 0.78)
            border.width: 1; border.color: root.cEdgeHi
            clip: true
            // scanlines inside the glass too
            Image { anchors.fill: parent; source: "assets/scanlines-1080.png"; fillMode: Image.Tile; opacity: 0.8; smooth: false }
            // glow seam along the top
            Rectangle { x: 8 * root.u; width: parent.width - 16 * root.u; y: 1; height: 2; color: root.cCrim }
            Rectangle {
                x: 8 * root.u; width: parent.width - 16 * root.u; y: 3; height: 28 * root.u
                gradient: Gradient {
                    GradientStop { position: 0; color: Qt.rgba(0.86, 0.12, 0.24, 0.20) }
                    GradientStop { position: 1; color: Qt.rgba(0.86, 0.12, 0.24, 0) }
                }
            }
        }

        Column {
            id: inner
            x: 40 * root.u; y: 40 * root.u
            width: panel.width - 80 * root.u
            spacing: 14 * root.u

            Row {
                spacing: 12 * root.u
                Rectangle { width: 6 * root.u; height: 30 * root.u; color: root.cCrim; anchors.verticalCenter: parent.verticalCenter }
                Osd { size: 32; text: "REDACTED"; anchors.verticalCenter: parent.verticalCenter }
            }
            Text {
                text: config.tagline || "SIGNAL ACQUIRED  //  IDENTIFY"
                font.family: root.mono; font.pixelSize: 15 * root.u; font.letterSpacing: 3 * root.u
                color: root.cDim
            }
            Item { width: 1; height: 8 * root.u }

            Field {
                id: nameBox
                label: "USER"
                onAccepted: passField.forceActiveFocus()
            }
            Field {
                id: passBox
                label: "PASSWORD"
                secret: true
                onAccepted: root.doLogin()
            }

            // session + caps
            Item {
                width: parent.width; height: 30 * root.u
                Row {
                    anchors.verticalCenter: parent.verticalCenter
                    spacing: 10 * root.u
                    Text { text: "◀"; font.family: root.mono; font.pixelSize: 16 * root.u; color: prevArea.containsMouse ? root.cCrimGlow : root.cCrim
                           MouseArea { id: prevArea; anchors.fill: parent; anchors.margins: -8; hoverEnabled: true; onClicked: root.cycleSession(-1) } }
                    Text { text: root.sessionLabel.toUpperCase(); font.family: root.mono; font.pixelSize: 15 * root.u; font.letterSpacing: 2 * root.u; color: root.cText }
                    Text { text: "▶"; font.family: root.mono; font.pixelSize: 16 * root.u; color: nextArea.containsMouse ? root.cCrimGlow : root.cCrim
                           MouseArea { id: nextArea; anchors.fill: parent; anchors.margins: -8; hoverEnabled: true; onClicked: root.cycleSession(1) } }
                }
                Text {
                    anchors.right: parent.right; anchors.verticalCenter: parent.verticalCenter
                    visible: typeof keyboard !== "undefined" && keyboard.capsLock
                    text: "CAPS"; font.family: root.mono; font.bold: true; font.pixelSize: 15 * root.u; color: root.cRec
                }
            }

            Item {
                width: parent.width; height: 52 * root.u
                Transport {
                    id: play
                    primary: true
                    glyph: root.loginPending ? "▶▶" : "▶"
                    text: root.loginPending ? "LOADING" : "PLAY"
                    anchors.right: parent.right; anchors.verticalCenter: parent.verticalCenter
                    onClicked: root.doLogin()
                }
                Text {
                    id: err
                    anchors.left: parent.left; anchors.verticalCenter: parent.verticalCenter
                    width: parent.width - play.width - 16 * root.u
                    wrapMode: Text.WordWrap
                    text: root.errorMsg
                    font.family: root.mono; font.bold: true; font.pixelSize: 15 * root.u; font.letterSpacing: 1 * root.u
                    color: root.cRec
                }
            }
        }

        transform: Translate { id: shakeT }
        SequentialAnimation {
            id: shake
            NumberAnimation { target: shakeT; property: "x"; to: -12 * root.u; duration: 45 }
            NumberAnimation { target: shakeT; property: "x"; to:  10 * root.u; duration: 60 }
            NumberAnimation { target: shakeT; property: "x"; to:  -6 * root.u; duration: 60 }
            NumberAnimation { target: shakeT; property: "x"; to:   0;          duration: 60 }
        }
    }

    // ---- transport controls = power ------------------------------------------
    Row {
        anchors.right: parent.right; anchors.bottom: parent.bottom
        anchors.margins: 52 * root.u
        spacing: 12 * root.u
        Transport { glyph: "❚❚"; text: "PAUSE";  visible: sddm.canSuspend;  onClicked: sddm.suspend() }
        Transport { glyph: "◀◀"; text: "REWIND"; visible: sddm.canReboot;   onClicked: sddm.reboot() }
        Transport { glyph: "■";       text: "STOP";   visible: sddm.canPowerOff; onClicked: sddm.powerOff() }
    }

    // ---- CRT on / off --------------------------------------------------------
    Rectangle {
        id: beam
        anchors.centerIn: parent
        width: parent.width; height: 2
        color: root.cCrimGlow
        opacity: 0
    }
    Rectangle { id: blackout; anchors.fill: parent; color: root.cVoid; opacity: 0 }

    SequentialAnimation {
        id: powerOn
        PropertyAction { target: screen; property: "scale"; value: 1 }
        PropertyAction { target: blackout; property: "opacity"; value: 1 }
        PropertyAction { target: beam; property: "opacity"; value: 1 }
        PropertyAction { target: beam; property: "width"; value: 0 }
        NumberAnimation { target: beam; property: "width"; to: root.width; duration: 220; easing.type: Easing.OutQuad }
        ParallelAnimation {
            NumberAnimation { target: beam; property: "height"; to: root.height * 0.25; duration: 240; easing.type: Easing.InQuad }
            NumberAnimation { target: beam; property: "opacity"; to: 0; duration: 260 }
            NumberAnimation { target: blackout; property: "opacity"; to: 0; duration: 420 }
        }
        PropertyAction { target: beam; property: "height"; value: 2 }
    }
    SequentialAnimation {
        id: powerOff
        ScriptAction { script: glitch.restart() }
        PauseAnimation { duration: 150 }
        ParallelAnimation {
            NumberAnimation { target: blackout; property: "opacity"; to: 0.85; duration: 260 }
            NumberAnimation { target: beam; property: "opacity"; to: 1; duration: 200 }
        }
        NumberAnimation { target: beam; property: "width"; to: 0; duration: 220; easing.type: Easing.InQuad }
        NumberAnimation { target: blackout; property: "opacity"; to: 1; duration: 120 }
    }
}
