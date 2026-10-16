import QtQuick
import QtQuick.Effects
import Quickshell
import Quickshell.Widgets
import Quickshell.Wayland
import qs.Commons
import qs.Ui
import "Model.js" as Model

Item {
    id: root
    property var shell: null
    property var manifest: null
    property bool opened: false
    property string selectedId: ""
    property var service: shell ? shell.serviceFor('zelport.integration') : null
    function open(payload) {
        if (service && service.snapshot.config.panel.clear_search_on_open) search.text = ''
        if (service && !service.snapshot.config.panel.remember_selection) selectedId = ''
        opened = true
        if (service) service.panelOpen = true
        rebuild()
        Qt.callLater(function() { search.forceActiveFocus() })
    }
    function close() { opened = false; if (service) service.panelOpen = false }
    function toggle() { if (opened) close(); else open('{}') }
    function rebuild() {
        var rows = service ? Model.visibleServices(service.snapshot.services,search.text,service.snapshot.config.services) : []
        var scroll = list.contentY
        Model.sync(display,rows)
        list.currentIndex = Model.selection(rows,selectedId)
        selectedId = list.currentIndex >= 0 ? display.get(list.currentIndex).id : ''
        list.contentY = Math.max(0,Math.min(scroll,Math.max(0,list.contentHeight-list.height)))
    }
    function move(delta) {
        if (!display.count) return
        list.currentIndex = (list.currentIndex+delta+display.count)%display.count
        selectedId = display.get(list.currentIndex).id
        list.positionViewAtIndex(list.currentIndex,ListView.Contain)
    }
    function launch() { if (service && list.currentIndex >= 0 && Model.canOpen(service.snapshot,display.get(list.currentIndex).url)) { service.openUrl(display.get(list.currentIndex).url); close() } }
    Component.onDestruction: if (service) service.panelOpen = false
    onServiceChanged: if (service && opened) { service.panelOpen = true; rebuild() }
    Connections { target: root.service; function onSnapshotChanged() { root.rebuild() } }
    component TableCell: Text {
        id:cell
        textFormat:Text.PlainText
        elide:Text.ElideRight
        color:Color.menu.text
        font.family:Style.font.menuFamily
        font.pixelSize:Style.font.body
        HoverHandler { id:cellHover }
        PanelToolTip {
            visible: cell.truncated && cellHover.hovered
            text: cell.text
            fontFamily: Style.font.menuFamily
        }
    }
    ListModel { id: display }
    PanelWindow {
        id: panel
        visible: root.opened
        anchors { top:true; bottom:true; left:true; right:true }
        color: 'transparent'
        exclusionMode: ExclusionMode.Ignore
        WlrLayershell.namespace: 'zelport-integration'
        WlrLayershell.layer: WlrLayer.Overlay
        WlrLayershell.keyboardFocus: WlrKeyboardFocus.Exclusive
        Rectangle { anchors.fill: parent; color: Color.menu.scrim }
        MouseArea { anchors.fill: parent; onClicked: root.close() }
        BorderSurface {
            width: Math.min(Style.space(1000),panel.width-Style.gapsOut*2)
            height: Math.min(Style.space(600),panel.height-Style.gapsOut*2)
            anchors.centerIn: parent
            color: Color.menu.background
            radius: Style.cornerRadius
            borderSpec: Border.surfaceSpec('menu','border',Color.menu.border,Math.max(1,Style.space(2)))
            padding: Style.spacing.panelPadding
            Keys.onEscapePressed: root.close()
            MouseArea { anchors.fill: parent; onClicked: search.forceActiveFocus() }
            Column {
                anchors.fill: parent
                anchors.margins: Style.spacing.panelPadding
                spacing: Style.space(10)
                Row {
                    width:parent.width
                    spacing:Style.space(8)
                    IconImage {
                        id:headerIcon
                        implicitSize:Style.font.title
                        anchors.verticalCenter:headerText.verticalCenter
                        source:Qt.resolvedUrl('assets/zelport-symbol.svg')
                        layer.enabled:true
                        layer.effect:MultiEffect { colorization:1; colorizationColor:Color.menu.text }
                    }
                    Text {
                        id:headerText
                        width:Math.max(0,parent.width-headerVersion.width-headerIcon.width-parent.spacing*2)
                        text:'Zelport Integration for Omarchy'
                        textFormat:Text.PlainText; wrapMode:Text.Wrap
                        color:Color.menu.text; font.family:Style.font.menuFamily; font.pixelSize:Style.font.title
                    }
                    Text {
                        id:headerVersion
                        anchors.verticalCenter:headerText.verticalCenter
                        text:root.manifest && root.manifest.version ? 'v' + root.manifest.version : ''
                        textFormat:Text.PlainText
                        color:Color.menu.text
                        opacity:versionLink.containsMouse || activeFocus ? 1 : 0.65
                        font.family:Style.font.menuFamily
                        font.pixelSize:Style.font.caption
                        font.underline:versionLink.containsMouse || activeFocus
                        activeFocusOnTab:false
                        Accessible.role:Accessible.Link
                        Accessible.name:'Source on GitHub, ' + text
                        function openRepository() { Qt.openUrlExternally('https://github.com/zelport/zelport-omarchy') }
                        Accessible.onPressAction:openRepository()
                        Keys.onReturnPressed:openRepository()
                        Keys.onEnterPressed:openRepository()
                        Keys.onSpacePressed:openRepository()
                        PanelToolTip {
                            visible:versionLink.containsMouse || headerVersion.activeFocus
                            text:'Source on GitHub'
                            fontFamily:Style.font.menuFamily
                        }
                        MouseArea {
                            id:versionLink
                            anchors.fill:parent
                            hoverEnabled:true
                            cursorShape:Qt.PointingHandCursor
                            onClicked:headerVersion.openRepository()
                        }
                    }
                }
                Text {
                    width:parent.width; elide:Text.ElideRight; textFormat:Text.PlainText
                    text: !root.service ? 'Zelport Integration: unavailable'
                        : root.service.snapshot.ready
                            ? root.service.status + (root.service.connectionsText ? ' · ' + root.service.connectionsText : '')
                            : root.service.status
                    color:Color.menu.text; font.family:Style.font.menuFamily; font.pixelSize:Style.font.caption
                }
                Rectangle {
                    width:parent.width; height:Style.space(42); color:'transparent'; border.color:Color.menu.border; radius:Style.cornerRadius
                    border.width:search.activeFocus ? Math.max(1,Style.space(2)) : 1
                    TextInput {
                        id:search
                        activeFocusOnTab:true
                        anchors.fill:parent; anchors.margins:Style.space(10)
                        color:Color.menu.text; selectionColor:Color.menu.selectedBackground; selectedTextColor:Color.menu.selectedText
                        font.family:Style.font.menuFamily; font.pixelSize:Style.font.body
                        verticalAlignment:TextInput.AlignVCenter
                        clip:true; selectByMouse:true
                        onTextChanged:root.rebuild()
                        Keys.onDownPressed:root.move(1)
                        Keys.onUpPressed:root.move(-1)
                        Keys.onReturnPressed:root.launch()
                        Keys.onEnterPressed:root.launch()
                        Keys.onEscapePressed:root.close()
                        Text {
                            anchors.fill:parent
                            verticalAlignment:Text.AlignVCenter
                            visible:!search.text
                            text:'Search services'
                            textFormat:Text.PlainText
                            color:Color.menu.text
                            opacity:0.6
                            font:search.font
                        }
                    }
                }
                Row {
                    visible:!list.compact
                    width:parent.width
                    leftPadding:Style.space(8)
                    spacing:list.columnGap
                    TableCell { width:list.domainWidth; text:'Domain'; font.pixelSize:Style.font.caption; opacity:0.7 }
                    TableCell { width:list.sourceWidth; text:'Source type'; font.pixelSize:Style.font.caption; opacity:0.7 }
                    TableCell { width:list.flowWidth; text:'Data flow'; font.pixelSize:Style.font.caption; opacity:0.7 }
                    TableCell { width:list.stateWidth; text:'State'; font.pixelSize:Style.font.caption; opacity:0.7 }
                }
                ListView {
                    id:list
                    activeFocusOnTab:true
                    keyNavigationEnabled:false
                    Keys.onDownPressed:root.move(1)
                    Keys.onUpPressed:root.move(-1)
                    Keys.onReturnPressed:root.launch()
                    Keys.onEnterPressed:root.launch()
                    Keys.onEscapePressed:root.close()
                    readonly property bool compact: width<Style.space(720)
                    readonly property real columnGap: Style.space(12)
                    readonly property real usableWidth: Math.max(0,width-Style.space(16)-columnGap*3)
                    readonly property real domainWidth: usableWidth*0.28
                    readonly property real sourceWidth: usableWidth*0.21
                    readonly property real flowWidth: usableWidth*0.36
                    readonly property real stateWidth: usableWidth-domainWidth-sourceWidth-flowWidth
                    width:parent.width
                    height:Math.max(0,parent.height-y-bottomBar.height-parent.spacing)
                    clip:true
                    model:display
                    spacing:0
                    delegate:Item {
                        required property int index
                        required property var model
                        id:serviceRow
                        width:list.width
                        height:list.compact ? compactContent.implicitHeight+Style.space(12) : Math.max(Style.space(30),tableContent.implicitHeight+Style.space(8))
                        readonly property color ink: index===list.currentIndex ? Color.menu.selectedText : Color.menu.text
                        Rectangle {
                            anchors.fill:parent
                            anchors.margins:Math.max(1,Style.space(1))
                            color:serviceRow.ListView.isCurrentItem ? Color.menu.selectedBackground : 'transparent'
                            radius:Style.cornerRadius
                            border.width:list.activeFocus && serviceRow.index===list.currentIndex ? Math.max(1,Style.space(1)) : 0
                            border.color:serviceRow.ink
                        }
                        Row {
                            id:tableContent
                            visible:!list.compact
                            anchors.left:parent.left; anchors.leftMargin:Style.space(8)
                            anchors.verticalCenter:parent.verticalCenter
                            spacing:list.columnGap
                            TableCell { width:list.domainWidth; text:model.domain; color:serviceRow.ink; font.bold:true }
                            TableCell { width:list.sourceWidth; text:model.source_name; color:serviceRow.ink }
                            TableCell { width:list.flowWidth; text:model.data_flow || '—'; color:serviceRow.ink }
                            TableCell { width:list.stateWidth; text:model.state; color:serviceRow.ink }
                        }
                        Column {
                            id:compactContent
                            visible:list.compact
                            anchors.left:parent.left; anchors.right:parent.right; anchors.top:parent.top
                            anchors.leftMargin:Style.space(8)
                            anchors.rightMargin:Style.space(8)
                            anchors.topMargin:Style.space(6)
                            spacing:Style.space(3)
                            TableCell { width:parent.width; text:model.domain; color:serviceRow.ink; font.bold:true }
                            TableCell { width:parent.width; text:model.source_name+' · '+model.state; color:serviceRow.ink; font.pixelSize:Style.font.caption }
                            TableCell { width:parent.width; text:model.data_flow || '—'; color:serviceRow.ink; font.pixelSize:Style.font.caption }
                        }
                        MouseArea { anchors.fill:parent; enabled:root.service && root.service.snapshot.ready && model.state!=='unsupported'; onClicked:{ list.currentIndex=index; root.selectedId=display.get(index).id; root.launch() } }
                    }
                    Text { anchors.centerIn:parent; visible:display.count===0; text:'No matching services'; textFormat:Text.PlainText; color:Color.menu.text; font.family:Style.font.menuFamily }
                }
                Item {
                    id:bottomBar
                    width:parent.width
                    height:actions.implicitHeight
                    Flow {
                        id:actions
                        width:parent.width
                        anchors.left:parent.left
                        anchors.verticalCenter:parent.verticalCenter
                        spacing:Style.space(12)
                        Button { text:'Open administration'; foreground:Color.menu.text; enabled:root.service && root.service.snapshot.ready; focusable:true; onClicked:root.service.openUrl(root.service.snapshot.admin_url) }
                        Button { text:'Refresh'; foreground:Color.menu.text; enabled:root.service && !root.service.busy; focusable:true; onClicked:root.service.refresh() }
                        Button { text:'Close'; foreground:Color.menu.text; focusable:true; onClicked:root.close() }
                    }

                }
            }
        }
    }
}
