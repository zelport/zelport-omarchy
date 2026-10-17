import QtQuick
import QtQuick.Effects
import Quickshell.Widgets
import qs.Ui
import qs.Commons

BarWidget {
    id: root
    readonly property var shell: bar ? bar.shell : null
    moduleName: "zelport.integration"
    readonly property var service: shell ? shell.serviceFor(moduleName) : null
    readonly property string status: service ? service.status + (service.connectionsText ? '\n' + service.connectionsText : '') : 'Zelport Integration requires the standard Omarchy bar'
    readonly property color foreground: bar ? bar.barForeground : Color.menu.text
    readonly property bool ready: !!service && service.snapshot.ready
    implicitWidth: vertical ? barSize : Style.bar.iconSlot
    implicitHeight: vertical ? Style.bar.iconSlot : barSize
    IconImage {
        anchors.centerIn: parent
        // Optical correction for the solid SVG compared with neighboring glyphs.
        implicitSize: Style.bar.iconFont * 0.95
        layer.enabled: true
        layer.effect: MultiEffect { colorization: 1; colorizationColor: root.foreground }
        source: Qt.resolvedUrl("assets/zelport-symbol.svg")
        opacity: root.ready ? 1 : 0.45
    }
    MouseArea {
        anchors.fill: parent
        hoverEnabled: true
        onClicked: if (root.shell) root.shell.toggle('zelport.integration','{}')
        onEntered: if (root.bar) root.bar.showTooltip(root,root.status)
        onExited: if (root.bar) root.bar.hideTooltip(root)
    }
}
