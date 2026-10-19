# Native acceptance — Omarchy 4.0.4-1

Run this mandatory release checklist on the target Linux desktop with the
latest stable Zelport App release and Zelport Integration `v2026.10.0`. A macOS
unit-test or cross-build result does not count as QML/runtime acceptance. Use
temporary schema-v1 configuration and synthetic services for route mutation
checks.

- [ ] `omarchy-version` reports the intended 4.0.4 series,
  `omarchy-shell shell ping` succeeds, and the standard `omarchy.bar` is active.
- [ ] `omarchy plugin validate ~/.config/omarchy/plugins/zelport.integration`
  succeeds.
- [ ] Enabling loads one widget and one service without QML warnings in shell
  logs.
- [ ] With no running Zelport App, the widget has an unavailable state and the
  panel gives setup guidance without starting the App.
- [ ] Start Zelport App normally with the chosen port and no `XDG_RUNTIME_DIR`.
  Verify `endpoint.json` under `XDG_STATE_HOME` records that port with mode 0600.
- [ ] The widget becomes available and services match Dashboard, including stale
  states. Relay connectivity is labeled separately from service health.
- [ ] Pointer click and `omarchy-shell shell toggle zelport.integration '{}'`
  open the same panel. Search focuses immediately. Up/Down, Enter, and Escape
  work.
- [ ] Search matches domain and source label. Enter opens only the selected
  `.localhost` service at the configured port. Administration opens exact
  localhost.
- [ ] Unchanged polls preserve selection, search, scroll, and delegates. A real
  addition or removal updates the list and retains the selected stable ID when
  present.
- [ ] Restart Zelport App. Stale entries remain visible but cannot launch;
  reconnect rereads the endpoint hint and resumes automatically.
- [ ] A malformed response or incompatible API produces a concise message
  without a raw exception or private settings.
- [ ] Dark and light theme changes update widget and panel colors. Narrow display
  and vertical bar placement remain usable. Replacement bars explain a missing
  service capability.
- [ ] Remove, disable, and reload the integration. The Zelport App PID,
  configuration, and service traffic remain unchanged, and no helper process is
  left running.
- [ ] Stop Zelport App cleanly. `endpoint.json` remains, while the widget becomes
  unavailable.
- [ ] Remove or corrupt the hint and verify selection of port 8080. A failed
  nondefault port produces one attempt on 8080 and no scan of other ports.
- [ ] A different application returning HTTP 200 is rejected as incompatible.

Record the exact Omarchy version and canonical `v…` release identifiers for
Zelport App and Zelport Integration, plus each result and sanitized shell errors,
in release verification. Do not mark this checklist passed from manifest
validation alone.
