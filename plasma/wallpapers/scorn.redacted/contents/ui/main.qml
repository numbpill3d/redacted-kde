/*
 * Redacted — animated Plasma wallpaper (desktop and lock screen).
 */
import QtQuick
import org.kde.plasma.plasmoid

WallpaperItem {
    id: root
    RedactedScene {
        anchors.fill: parent
        art: Qt.resolvedUrl("art/")
        // pause while the screen is covered/locked away: Plasma hides the item
        running: root.visible
    }
}
