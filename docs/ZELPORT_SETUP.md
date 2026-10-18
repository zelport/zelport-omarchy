# Zelport App setup

Zelport Integration `2026.10.0` is a read-only Linux consumer of the local
integration API provided by Zelport App `0.10.0`. Install and start Zelport App
separately. The integration does not install, start, stop, update, or configure
the App.

The Arch package runs Zelport App as the logged-in user:

```sh
systemctl --user enable --now zelport.service
systemctl --user status zelport.service
```

A manually managed App can instead be started with its chosen `--port` and
`--config` arguments. No integration flag, additional listener, or runtime
directory is required.

## Endpoint discovery

After startup, Zelport App records its listener port in
`$XDG_STATE_HOME/zelport/endpoint.json`, or
`~/.local/state/zelport/endpoint.json` when `XDG_STATE_HOME` is unset, empty, or
relative. Zelport Integration rereads this hint on every poll. A missing or
invalid hint selects port 8080; a failed nondefault endpoint is followed by one
attempt on port 8080. The integration never scans ports or processes.

The client calls `GET /api/integration/v1/state` and requires
`product: "zelport"`, `api_version: 1`, and the expected response structure.
Requests connect directly to IPv4 loopback, use the exact localhost authority,
ignore proxy environment variables, and do not follow redirects. Service launch
URLs must use HTTP `.localhost` names on the selected port. Administration must
use exact localhost.

The App repository owns the complete normative contract in
[`docs/LOCAL_INTEGRATION_API.md`](https://github.com/zelport/zelport/blob/main/docs/LOCAL_INTEGRATION_API.md).

## Lifecycle boundary

Zelport Integration only reads projected service and relay status. Installing,
updating, disabling, or removing it must not change the Zelport App process,
configuration, routes, traffic, or service state. Manage Zelport App and its
optional user service independently.
