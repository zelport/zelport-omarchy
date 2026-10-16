# Zelport Integration

Zelport Integration is an independent community project and is not affiliated with or endorsed
by Omarchy.

Zelport Integration connects the standard Omarchy bar and a keyboard search panel to an
existing Zelport gateway. It never starts, stops, installs, or configures Zelport.
Target: Omarchy **4.0.4-1** (upstream shell tag v4.0.4), Linux x86_64, Python 3.9+
and Zelport 0.1.0-preview.5 or newer with the automatic local integration API.
This is a preview. Earlier native loading checks are recorded in docs/NATIVE_RESULTS.md.
Full visual and interaction acceptance remains pending;
see [the acceptance checklist](docs/NATIVE_ACCEPTANCE.md).

## Gateway installed with the Arch package

The current Arch unit runs Zelport as the logged-in user. No integration flag is
needed. Older preview gateways and plugins must be upgraded together. See
[the API and migration guide](docs/GATEWAY_SETUP.md).

```sh
systemctl --user status zelport.service
```

## Install from GitHub

Install the preview from GitHub:

```sh
omarchy plugin add https://github.com/zelport/zelport-omarchy.git --enable
```

If a hand-installed `zelport.integration` already exists, back up its directory
before replacing it and follow Omarchy's plugin management prompts. Preserve
`~/.config/zelport/omarchy.json` and existing keyboard bindings. Do not create a
second bar widget if Zelport Integration is already present.

## Manually managed gateway

Start the gateway with its existing port and configuration. The plugin never
starts a second gateway. Python uses only its standard library.

The plugin reads the last-used port from `$XDG_STATE_HOME/zelport/endpoint.json`
or `~/.local/state/zelport/endpoint.json`. A missing or invalid hint defaults to
8080. A failed nondefault endpoint also falls back to 8080. Responses must match
the local integration API contract before the widget becomes available.
There is no token, port scan, process scan, instance selector or runtime-directory
dependency. Presentation preferences remain in
[`~/.config/zelport/omarchy.json`](docs/CONFIGURATION.md).

## Hand-install the local preview

Omarchy v4.0.4's `omarchy plugin add` accepts Git URLs, not local archives.
For an offline preview installation, use the following manual lifecycle. Extract
the prepared source bundle into a temporary directory and inspect it first. Copy
the plugin directory to `~/.config/omarchy/plugins/zelport.integration/` so that
`manifest.json` is directly inside that directory. If an earlier copy exists,
back it up before replacing it; do not merge stale runtime files into an update.

From that installed directory run:

```sh
omarchy plugin validate .
omarchy-shell shell rescanPlugins
omarchy plugin enable zelport.integration
```

Use Omarchy's bar configuration to add the **Zelport Integration** widget to the standard bar.
Do not modify Omarchy's built-in QML files. The monochrome logo uses full opacity
when the gateway is available and 45% opacity otherwise, without additional badges.
An explicit unsupported tooltip explains replacement bars that withhold services.

The panel can be opened without the widget:

```sh
omarchy-shell shell toggle zelport.integration '{}'
```

The optional shortcut **Super + Alt + Z** toggles Zelport Integration. Check for conflicts
before adding this to `~/.config/hypr/bindings.lua` on Omarchy with Lua configuration:

```lua
o.bind("SUPER + ALT + Z", "Zelport Integration", "omarchy-shell shell toggle zelport.integration '{}'")
```

Reload Hyprland configuration after saving. Opening the panel focuses search.
Installing Zelport Integration does not change keyboard configuration. This shortcut is a
project choice, not an Omarchy reserved convention. Use Alt, not Ctrl: Omarchy
binds Super + Ctrl + Z to zoom. Dual-label keyboard keys depend on the keyboard's
hardware mode; verify which keys send Super and Alt.

## Use

The service table shows Domain, Source type, Data flow and State. Narrow panels
stack these values. Data flow is display-only and comes from the gateway; older
servers without the optional field show a dash.

Type a domain or source name, use Up/Down to select, Enter to open, and Escape to
close. Click a row to open it with the configured URL handler. Administration opens
the existing gateway web interface. Refresh requests an immediate poll.

Availability means the validated integration API responded, **not** that an
application is healthy. Individual route and relay states retain Zelport's meaning.
On failure the last list stays visible as stale and all launch actions are disabled.
The endpoint hint is reread on each poll, including after a gateway restart.
Search, selection by route ID, scroll position, and unchanged row objects survive
refresh. The panel and widget share one service and one outstanding poll.

Polling runs every five seconds while closed and two seconds while open, backing
off failures to thirty seconds. Opening the panel requests an immediate refresh.
Each helper process has a two-second total deadline and each HTTP attempt is
limited to 900 ms. Responses are limited to 1 MiB and 4096 services. An invalid
response never enables launch actions.

## Local API boundary

The helper connects directly to IPv4 loopback with the exact localhost Host
header. It ignores proxy environment variables and does not follow redirects.
It validates product, API version and response structure. Launch URLs must use
HTTP and the selected port, with `.localhost` service names or exact localhost
for administration. QML opens validated URLs with `Qt.openUrlExternally`.

The API follows the existing local dashboard trust model. It is read-only but
not isolated from other local users. Requests with Origin are rejected and no
CORS access is granted. The plugin never changes gateway settings.

## Update and remove

Disable the plugin with `omarchy plugin disable zelport.integration` before replacing
its installed files. Validate, rescan, and enable again. The manifest uses
`keepLoaded`; service code changes require a shell restart under the v4.0.4
lifecycle. For removal, disable it and use `omarchy plugin remove zelport.integration`.
Removing Zelport Integration leaves Zelport, its configuration, routes, relay and sessions alone.
An optional gateway user service is independently managed by its owner.

## Development checks

For desktop development, keep a separate checkout at
`~/src/zelport-omarchy-dev` and link
`~/.config/omarchy/plugins/zelport.integration` to it. Before replacing an
existing installation, move it outside the plugin discovery directory, for
example into `~/.local/share/zelport/plugin-backups/`. Preserve presentation
preferences, keyboard bindings and the existing bar widget placement.

Update the development checkout directly, run `omarchy plugin validate
~/src/zelport-omarchy-dev`, then `omarchy restart shell` to reload service code.
No gateway restart or release upgrade is needed. The panel header displays the
manifest version. Development builds use a `-dev` suffix. Do not run the normal
plugin updater against a checkout with unpublished edits.

To roll back, remove only the plugin symlink, restore the backed-up directory
at the original plugin path, and restart the shell.

```sh
python3 -m unittest discover -s tests -v
node --test tests/model.test.cjs
python3 scripts/bundle.py
```

Tests use temporary runtime directories and a controlled ephemeral loopback HTTP
fixture. They do not inspect user descriptors or routes. The JavaScript tests exercise
model behavior; they are not a native QML rendering test. The bundle script packages
only an explicit runtime/documentation/test allowlist with deterministic metadata.

The icon is copied from the existing Zelport identity kit; no separate identity is
introduced. The UI uses Omarchy's live menu, font, spacing and bar theme tokens.

Services whose Zelport module is absent from the build appear as `unsupported`.
They remain visible but cannot be opened. This does not make Zelport unavailable
or dim the bar icon. Preserved services become usable when the module returns.

Omarchy catalog and release preparation: [publishing guide](docs/distribution/PUBLISHING.md).

Licensed under the [MIT License](LICENSE).
