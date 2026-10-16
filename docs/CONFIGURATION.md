# Plugin configuration

Edit `$XDG_CONFIG_HOME/zelport/omarchy.json`, or `~/.config/zelport/omarchy.json`
when XDG_CONFIG_HOME is unset. See [config.example.json](../config.example.json)
for the defaults. The plugin reads this file at each poll, including Refresh.
Polling backs off to 30 seconds on failure; Refresh applies corrections immediately.
The plugin does not rewrite the file. Optional sections and fields use defaults.
`version: 1` is required when a file exists. Unknown fields, wrong types, unsupported
versions and malformed JSON disable launching with a configuration error. No tokens
belong in this file. Its maximum size is 16 KiB; it must be a regular file.

| Field | Default | Accepted values |
| --- | --- | --- |
| `services.source_types` | `[]` | Module IDs, e.g. `["remote_http", "local_ports"]`; empty means all |
| `services.sort_by` | `"domain"` | `"domain"`, `"source_type"`, `"state"` |
| `panel.remember_selection` | `true` | Boolean |
| `panel.clear_search_on_open` | `true` | Boolean |

Sorting is ascending and textual, with domain and ID as stable tie-breakers. Source
type sorting uses the displayed source name. State sorting is alphabetical, not a
health ranking. Filtering does not alter gateway routes. Panel options apply when
opening the panel. Selection follows stable route IDs across reconnects.

## Endpoint selection

The plugin reads `$XDG_STATE_HOME/zelport/endpoint.json`, falling back to
`~/.local/state/zelport/endpoint.json` when the variable is missing or relative.
It uses the recorded port and tries 8080 if that endpoint fails. With a missing or
invalid hint it tries only 8080. It rereads the hint each poll. There is no scan or
instance selector and no token. The helper connects directly to IPv4 loopback
with the exact localhost Host header, ignoring proxy variables and redirects.

The retired `gateway` configuration section is ignored to preserve existing
presentation preferences. It can be removed. ZELPORT_INTEGRATION_PORT and
OMAPORT_PORT are no longer used. Port changes belong to the gateway.
