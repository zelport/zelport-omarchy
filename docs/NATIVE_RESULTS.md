# Native verification — 2026-10-14

## Data flow and table update

Zelport `dev-omaport-dataflow` adds the optional v1 `data_flow` display field.
The table uses Domain, Source type, Data flow and State, with stacked fields on
narrow panels. Both live services matched their Dashboard target summaries.
The new panel loaded without QML errors against both the previous gateway
(missing Data flow shown as a dash) and the updated gateway. The existing
configuration was retained and relay connectivity resumed after restart.

Validation: `make check`, `make check-modules`, `make build`, Linux amd64 build,
10 Python tests on macOS and native Linux, and 6 JavaScript model tests passed.
Visual column proportions, narrow layout and tooltip interaction still require
desktop review; successful QML loading is not visual acceptance.

## Initial native verification

Environment: Omarchy 4.0.4-1, Linux 7.2.5-3-omarchy x86_64,
Python 3.14.7, Zelport dev-omaport-v1, Omaport 0.1.0.

Verified over SSH on the target desktop:

- All four Go desktop test groups passed, including Linux filesystem cases.
- All nine bundled Python tests passed.
- Native `omarchy plugin validate` passed; plugin installed and enabled.
- The standard Omarchy bar is active. The panel loaded, accepted a method call,
  and appeared as the `omarchy-omaport` Hyprland layer without new QML errors.
- A temporary gateway on port 18888 authenticated successfully through the helper.
  Descriptor directories had mode 0700 and the descriptor had mode 0600.
- The existing gateway was backed up and replaced by a running preview process
  using the same configuration and port 8080, with desktop integration enabled.
  The helper returned both configured routes and the connected relay state.
- Stopping the temporary gateway removed its own descriptor and retained the
  gateway descriptor for port 8080.

Visual appearance, pointer interaction, keyboard navigation, theme changes and
selection retention still require desktop acceptance. IPC success and layer
presence are not evidence that those interactions passed. Autostart was not set up.

## Absent-module configuration (2026-10-14)

An isolated Linux core build on port 18888 started with a synthetic missing-module
route. The authenticated desktop helper returned `unsupported`, no relay
connections, and the configuration bytes were unchanged. The temporary process
was stopped after verification. Model tests verify that unsupported services
cannot be opened while the gateway remains available.

The full gateway and plugin were updated with backups. The live helper reported
both existing services (`configured` and `ready`); shell ping and plugin summon
succeeded. Local core UI verification was attempted but blocked by repeated
in-app browser/CDP timeouts; no visual verification is claimed for this change.

## Identity migration (2026-10-15)

Renamed the plugin to Zelport Integration (`zelport.integration`) and the local
project to `zelport-omarchy`. Migrated the native bar entry and Super + Alt + Z
binding; the old plugin directory is backed up outside discovery. Manifest
validation and configuration assertions passed. After unlocking, shell restart, ping and summon using `zelport.integration`
succeeded. The helper returned both existing services and the connected relay;
no new QML errors appeared in the shell log. Visual acceptance remains manual.
Historical results above retain the names used during those tests.

## Editable configuration and discovery (2026-10-15)

Created the default config at `~/.config/zelport/omarchy.json` with mode
0600. Updated plugin passed native manifest validation and 16 Python tests.
Local model tests passed 10 cases. An independent code review found no remaining
important issues after fixing stalled-probe budget distribution and preserving
an explicitly selected unavailable gateway.

An isolated native core gateway on port 8070 ran alongside the existing 8080
gateway. Auto-discovery returned both ports without choosing one; the helper's
session selection returned 8070. The panel was summoned while both existed and
produced no new QML errors. Stopping the temporary process restored sole-instance
auto-selection of 8080. Existing gateway configuration was not modified. Pointer
selection, keyboard navigation of the chooser and visual appearance still need
manual acceptance; IPC/log checks do not prove those interactions.

## Local endpoint redesign (2026-10-16)

The token-based discovery results above describe the retired preview protocol.
The new implementation uses an automatic read-only API and a last-used port hint
under XDG_STATE_HOME, with 8080 fallback. It removes instance selection and the
startup flag. Existing gateway configuration and processes were not changed.

Verified locally: 13 Python tests, 10 JavaScript model tests, deterministic bundle,
workspace race tests/vet, module combinations and builds. An isolated Linux arm64
container ran the full gateway and plugin helper as an unprivileged user without
XDG_RUNTIME_DIR. Startup, restart with changed port, missing/stale-hint fallback,
and a nonfatal endpoint-file write failure all passed.

Native Omarchy shell loading and visual interaction for this revision remain
pending. Earlier desktop results do not establish acceptance of the new revision.
