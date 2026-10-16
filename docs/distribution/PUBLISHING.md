# Publishing Zelport Integration for Omarchy

Status: GitHub preview distribution. The plugin is not submitted to the catalog.

The gateway and plugin have independent releases. The plugin never downloads,
installs, starts or updates a gateway implicitly. It discovers a running gateway
through its automatic local API. Python 3 and the standard Omarchy shell/bar are
required. Native testing targets Omarchy 4.0.4-1; do not claim wider compatibility
without testing. The supported desktop API is v1.

## Catalog metadata

- Repository: https://github.com/zelport/zelport-omarchy
- Name: Zelport Integration
- ID: `zelport.integration`
- Author: Zelport
- Description: Unofficial Zelport integration for Omarchy.
- Suggested category: Network (choose the matching category offered by the form).
- Suggested tags: zelport, localhost, services, development, networking.
- License: MIT; see the root LICENSE.

The manifest at the repository root is authoritative for the plugin version,
entry points and bar widget metadata. Keep that layout in the published repository.
A prepared archive is an alternative for manual preview installation; it is not
itself a Git repository accepted by `omarchy plugin add`.

## Release checklist

- Publish a standalone repository with runtime files, root manifest, README,
  LICENSE, assets, tests and documentation. Exclude `bin/`, Python caches and
  historical design drafts; review the complete Git tree before publishing.
- Review third-party asset attribution. Take an optional preview screenshot on
  Omarchy with synthetic services and no private domains or endpoints.
- Set the intended version in manifest.json and tag that exact revision.
- Run `python3 -m unittest discover -s tests` and `node --test tests/model.test.cjs`.
- Run `omarchy plugin validate .` on the supported Omarchy version. Complete
  [native acceptance](../NATIVE_ACCEPTANCE.md), including keyboard navigation,
  endpoint changes, config changes and unavailable gateways.
- Run `python3 scripts/bundle.py`; the archive includes LICENSE and a SHA-256 file.
- Verify installation, upgrade and removal on a clean test account. Preserve
  `~/.config/zelport/omarchy.json`, gateway config and existing shortcuts.
- Submit the repository URL, category and tags through the
  [catalog publishing form](https://plugins.omarchy.org/publish.html).
  Listing approval is separate from manifest validation. Do not describe the
  plugin as an official Omarchy project or imply listing validates its security.

## Installation from GitHub

Install Zelport 0.1.0-preview.5 or newer through its Arch package and enable its user service first;
see the gateway's `contrib/distribution/README.md`. Then:

```sh
omarchy plugin add https://github.com/zelport/zelport-omarchy.git --enable
```

The manifest defaults the widget to the right bar section. Follow placement prompts
and choose the standard bar. No global shortcut is installed automatically. The
optional Super + Alt + Z binding and JSON configuration are documented in README.
When absent, the config file uses auto-discovery defaults; users can copy
`config.example.json` to `~/.config/zelport/omarchy.json` before editing.

Use Omarchy's supported plugin update/remove workflow. Removing this plugin must
not stop Zelport, remove its package or delete either configuration file.
