# Zelport Integration

Zelport Integration is an independent community project and is not affiliated
with or endorsed by Omarchy. Version `0.10.0` targets Omarchy **4.0.4-1**
(upstream shell tag `v4.0.4`), Linux x86_64, Python 3.9+, and Zelport App
`0.10.0`.

The integration connects the standard Omarchy bar and a keyboard search panel
to a running Zelport App through its read-only local integration API. It never
installs, starts, stops, updates, or configures Zelport App.

## Requirements

Install Zelport App `0.10.0` and start it as the logged-in user. The Arch package
provides a user service:

```sh
systemctl --user status zelport.service
```

No integration flag or additional listener is required. See
[Zelport setup](docs/ZELPORT_SETUP.md) for the API and lifecycle boundary.

## Install from GitHub

```sh
omarchy plugin add https://github.com/zelport/zelport-omarchy.git --enable
```

If a hand-installed `zelport.integration` directory already exists, back it up
before replacing it and follow Omarchy's plugin management prompts. Preserve
`~/.config/zelport/omarchy.json` and existing keyboard bindings. Do not create a
second bar widget when Zelport Integration is already present.

Omarchy `v4.0.4` accepts Git URLs rather than local archives. For an offline
installation, inspect and extract the prepared source bundle, then copy its
`zelport.integration` directory to
`~/.config/omarchy/plugins/zelport.integration/`. `manifest.json` must be
directly inside that directory. Validate and enable the installed copy:

```sh
omarchy plugin validate .
omarchy-shell shell rescanPlugins
omarchy plugin enable zelport.integration
```

Use Omarchy's bar configuration to add the **Zelport Integration** widget to the
standard bar. The panel can also be opened directly:

```sh
omarchy-shell shell toggle zelport.integration '{}'
```

The optional **Super + Alt + Z** shortcut can be added to
`~/.config/hypr/bindings.lua` on Omarchy installations that use Lua
configuration:

```lua
o.bind("SUPER + ALT + Z", "Zelport Integration", "omarchy-shell shell toggle zelport.integration '{}'")
```

Check for conflicts before adding the binding. Zelport Integration does not
change keyboard configuration automatically.

## Use

The service table shows Domain, Source type, Data flow, and State. Type a domain
or source name, use Up/Down to select, Enter to open, and Escape to close. Click
a row to open its validated URL. Administration opens the existing Zelport App
web interface. Refresh requests an immediate poll.

Availability means the validated local integration API responded; it does not
mean that an individual proxied application is healthy. On failure, the last
verified list remains visible as stale and all launch actions are disabled. The
endpoint hint is reread on each poll, including after a Zelport App restart.
Search, selection by stable route ID, scroll position, and unchanged row objects
survive refresh. The panel and widget share one service and one outstanding poll.

Polling runs every five seconds while closed and two seconds while open, backing
off failures to thirty seconds. Each helper process has a two-second total
deadline and each HTTP attempt is limited to 900 ms. Responses are limited to
1 MiB and 4096 services. An invalid response never enables launch actions.

## Local API boundary

The helper reads the last-used listener port from
`$XDG_STATE_HOME/zelport/endpoint.json` or
`~/.local/state/zelport/endpoint.json`. A missing or invalid hint selects port
8080. A failed nondefault endpoint is followed by one attempt on port 8080.
There is no token, port scan, process scan, instance selector, or runtime-directory
dependency. Presentation preferences are documented in
[Zelport Integration configuration](docs/CONFIGURATION.md).

Requests connect directly to IPv4 loopback with the exact localhost authority.
The helper ignores proxy environment variables, does not follow redirects, and
validates product, API version, and response structure. Launch URLs must use HTTP
and the selected port with `.localhost` service names, or exact localhost for
administration. QML opens validated URLs with `Qt.openUrlExternally`.

The API follows the local dashboard trust model. It is read-only but does not
isolate users on the same machine. Requests carrying `Origin` are rejected and
CORS is not enabled. Zelport Integration never changes Zelport App settings.

## Update and remove

Disable the integration before replacing its installed files:

```sh
omarchy plugin disable zelport.integration
```

Validate, rescan, and enable it again. The manifest uses `keepLoaded`, so service
code changes require an Omarchy shell restart under the `v4.0.4` lifecycle. To
remove the integration, disable it and run
`omarchy plugin remove zelport.integration`. Removal leaves Zelport App, its
configuration, services, relay state, and sessions unchanged.

## Development checks

Run the Python suite on a host that permits controlled loopback fixtures. Run the
JavaScript suite in an isolated Node.js environment, then build the deterministic
bundle:

```sh
python3 -m unittest discover -s tests -v
node --test tests/model.test.cjs
python3 scripts/bundle.py
```

The JavaScript suite exercises model behavior; it is not a native QML rendering
test. The bundle script packages only an explicit runtime, documentation, and
test allowlist with deterministic metadata. Complete the
[native acceptance checklist](docs/NATIVE_ACCEPTANCE.md) on the target Omarchy
desktop before release.

The icon comes from the Zelport identity kit. The UI uses Omarchy's live menu,
font, spacing, and bar theme tokens.

Release preparation is documented in the
[publishing guide](docs/distribution/PUBLISHING.md).

Licensed under the [MIT License](LICENSE).
