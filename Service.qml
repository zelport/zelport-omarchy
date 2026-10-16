import QtQuick
import Quickshell
import Quickshell.Io
import "Model.js" as Model

Item {
    id: root
    property var shell: null
    property bool panelOpen: false
    property var snapshot: Model.initial()
    property int failures: 0
    property bool busy: false
    property bool received: false
    readonly property string status: Model.message(snapshot)
    readonly property string connectionsText: snapshot.connections.map(function(c) { return c.label + ': ' + c.state; }).join(' · ')
    function refresh() {
        if (!Model.canPoll(busy)) return
        pollTimer.stop()
        busy = true
        received = false
        fetch.running = true
    }
    function receive(raw) {
        var result
        try { result = JSON.parse(raw) } catch (e) { result = {ok:false,error:'unavailable'} }
        snapshot = Model.receive(snapshot,result)
        failures = snapshot.ready ? 0 : Math.min(failures+1,10)
        received = true
    }
    function openUrl(url) {
        if (!snapshot.ready) return
        if (Model.canOpen(snapshot,url)) Qt.openUrlExternally(url)
    }
    onPanelOpenChanged: { if (panelOpen) refresh(); else if (!busy) pollTimer.restart() }
    Component.onCompleted: refresh()
    Timer { id: pollTimer; interval: Model.delay(root.failures,root.panelOpen); onTriggered: root.refresh() }
    Process {
        id: fetch
        command: ["python3", decodeURIComponent(Qt.resolvedUrl("helper.py").toString().replace(/^file:\/\//,""))]
        stdout: StdioCollector { onStreamFinished: root.receive(text) }
        // stderr is deliberately not forwarded to the shell log.
        stderr: StdioCollector {}
        onExited: {
            if (!root.received) root.receive('{"ok":false,"error":"unavailable"}')
            root.busy = false
            pollTimer.restart()
        }
    }
}
