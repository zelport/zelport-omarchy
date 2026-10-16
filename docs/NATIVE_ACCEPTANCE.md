# Omarchy 4.0.4-1 native acceptance

Run these checks on the target Linux desktop. A macOS unit-test or cross-build
result does not count as QML/runtime acceptance. Use temporary gateway configuration
and a controlled test HTTP service for route mutation checks.

- [ ] `omarchy-version` reports the intended 4.0.4 series; `omarchy-shell shell ping`
  succeeds; the standard `omarchy.bar` is active.
- [ ] `omarchy plugin validate ~/.config/omarchy/plugins/zelport.integration` succeeds.
- [ ] Enabling loads one widget and one service without QML warnings in shell logs.
- [ ] With no running gateway, the widget has an unavailable state and
  the panel gives setup guidance without launching another gateway.
- [ ] Start Zelport normally with the chosen port and no XDG_RUNTIME_DIR. Verify
  endpoint.json under XDG_STATE_HOME records that port with mode 0600.
- [ ] Widget becomes available. Services match Dashboard, including stale states.
  Relay connectivity is labeled separately from service/application health.
- [ ] Pointer click and `omarchy-shell shell toggle zelport.integration '{}'` open
  the same panel. Search focuses immediately. Up/Down, Enter and Escape work.
- [ ] Search matches domain and source label; Enter opens only the selected
  `.localhost` service at the configured port. Administration opens exact localhost.
- [ ] Unchanged polls preserve selection, search, scroll and delegates. A real
  addition/removal updates the list and retains the selected stable ID if present.
- [ ] Restart gateway: stale entries remain visible but cannot launch; reconnect
  rereads the endpoint hint and resumes automatically.
- [ ] A malformed response or incompatible API gives
  a concise message without a raw exception, private settings.
- [ ] Dark/light theme changes update widget/panel colors. Narrow display and
  vertical bar placement remain usable. Unsupported replacement bars explain the
  missing service capability.
- [ ] Remove/disable/reload plugin: gateway PID, configuration and service traffic
  remain unchanged. Plugin leaves no background helper running.
- [ ] Stop gateway cleanly: endpoint.json remains, but the widget becomes unavailable.
- [ ] Remove or corrupt the hint and verify fallback to 8080. A failed nondefault
  port falls back once to 8080, never scanning other ports.
- [ ] A different application returning HTTP 200 is rejected as incompatible.

Record Omarchy version, gateway build version, plugin version, results and any
shell errors with secrets removed. Do not mark the whole checklist passed from
manifest validation alone.
