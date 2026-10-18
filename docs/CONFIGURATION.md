# Zelport Integration configuration

Edit `$XDG_CONFIG_HOME/zelport/omarchy.json`, or
`~/.config/zelport/omarchy.json` when `XDG_CONFIG_HOME` is unset or relative. See
[config.example.json](../config.example.json) for the defaults. Zelport
Integration reads this file at each poll, including Refresh, and never rewrites
it. The file itself is optional: when it does not exist, the integration uses
the defaults in memory and does not create it. Optional sections and fields use
defaults.

`version: 1` is required when a file exists. Unknown fields, wrong types, other
versions, and malformed JSON disable launching with a configuration error. This
16-KiB token-free schema is independent of Zelport App configuration schema v1;
no credentials belong in it, and it must be a regular file.

| Field | Default | Accepted values |
| --- | --- | --- |
| `services.source_types` | `[]` | Source IDs, for example `["remote_http", "local_ports"]`; empty means all |
| `services.sort_by` | `"domain"` | `"domain"`, `"source_type"`, `"state"` |
| `panel.remember_selection` | `true` | Boolean |
| `panel.clear_search_on_open` | `true` | Boolean |

`version` identifies this configuration schema, not the integration or Zelport
App version. Values in `services.source_types` are matched exactly against the
source IDs returned by the integration API. A valid but unknown source ID simply
matches no services.

Sorting is ascending and textual, with domain and ID as stable tie-breakers.
Source type sorting uses the displayed source name. State sorting is
alphabetical, not a health ranking. Filtering does not alter Zelport App routes.

When `panel.remember_selection` is `true`, reopening the panel keeps the
selected service if its stable route ID is still present. When it is `false`,
each open resets selection to the first visible service. When
`panel.clear_search_on_open` is `true`, each open clears the search field; when
it is `false`, reopening the panel retains the current search text. Selection
and search text exist only in the running Omarchy shell: neither survives a
shell restart, logout, or reboot, and neither is written to this file.

## Endpoint selection

Zelport Integration reads `$XDG_STATE_HOME/zelport/endpoint.json`, falling back
to `~/.local/state/zelport/endpoint.json` when the variable is missing or
relative. It uses the recorded port and tries 8080 once if that endpoint fails.
With a missing or invalid hint, it tries only 8080. It rereads the hint on every
poll. There is no scan, instance selector, or token. The helper connects directly
to IPv4 loopback with the exact localhost authority, ignoring proxy variables
and redirects.

Unknown and obsolete configuration fields are rejected. Listener selection
belongs to Zelport App and is not configurable through Zelport Integration.
