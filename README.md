# Zelport Integration

Zelport Integration brings Zelport services to the standard Omarchy bar and a
keyboard-driven search panel. It connects to a running Zelport App through its
read-only local integration API. It never installs, starts, stops, updates, or
configures Zelport App.

## Requirements

Install Zelport App and start it as the logged-in user. The Arch package provides
a user service:

```sh
systemctl --user status zelport.service
```

No integration flag or additional listener is required. See
[Zelport setup](docs/ZELPORT_SETUP.md) for the API and lifecycle boundary.

Zelport Integration and Zelport App release independently. The latest
Integration is expected to work with the latest App through Integration API v1;
an App release does not require a matching Integration version.

## Install from GitHub

```sh
omarchy plugin add https://github.com/zelport/zelport-omarchy.git --enable
```

If replacing a hand-installed copy, preserve
`~/.config/zelport/omarchy.json`, keyboard bindings, and the existing bar widget.

Add the **Zelport Integration** widget through Omarchy's bar configuration. Open
the panel directly with:

```sh
omarchy-shell shell toggle zelport.integration '{}'
```

See [installation details](docs/INSTALLATION.md) for offline setup and the
optional keyboard shortcut.

## Use

The service table shows Domain, Source type, Data flow, and State. Type a domain
or source name, use Up/Down to select, Enter to open, and Escape to close. Click
a row to open its validated URL. Administration opens the existing Zelport App
web interface. Refresh requests an immediate poll.

Availability confirms the local API, not individual application health. On
failure, the last verified list remains visible as stale and launch actions are
disabled. Refreshes preserve search and selection; polling backs off after
failures.

## Configuration

Configuration is optional. When no configuration file exists, the integration
uses the following defaults in memory and does not create a file:

```json
{
  "version": 1,
  "services": {
    "source_types": [],
    "sort_by": "domain"
  },
  "panel": {
    "remember_selection": true,
    "clear_search_on_open": true
  }
}
```

To customize it, create `$XDG_CONFIG_HOME/zelport/omarchy.json`, or
`~/.config/zelport/omarchy.json` when `XDG_CONFIG_HOME` is unset or relative.
The integration rereads but never rewrites the file. See
[configuration](docs/CONFIGURATION.md) for field semantics and validation.

## Local API boundary

The helper reads the listener from `$XDG_STATE_HOME/zelport/endpoint.json` (or
`~/.local/state/zelport/endpoint.json`) and falls back to port 8080. It connects
directly to IPv4 loopback, validates responses and launch URLs, and performs no
port or process scan. The read-only API follows the local dashboard trust model
and does not isolate users on the same machine. See
[Zelport setup](docs/ZELPORT_SETUP.md) for the complete boundary.

## Remove

```sh
omarchy plugin remove zelport.integration
```

Removing the integration does not remove Zelport App or its configuration.

## Development checks

Run the Python suite on a host that permits controlled loopback fixtures. Run the
JavaScript suite in an isolated Node.js environment, then build the deterministic
bundle:

```sh
python3 -m unittest discover -s tests -v
node --test tests/model.test.cjs
python3 scripts/bundle.py
```

Before release, complete the
[native acceptance checklist](docs/NATIVE_ACCEPTANCE.md) and follow the
[publishing guide](docs/distribution/PUBLISHING.md).

Licensed under the [MIT License](LICENSE).
