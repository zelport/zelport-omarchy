# Publishing Zelport Integration for Omarchy

Zelport Integration releases independently from Zelport App. The integration
never downloads, installs, starts, stops, or updates the App. Python 3 and the
standard Omarchy shell and bar are required. Native acceptance targets Omarchy
4.0.4-1; do not claim wider compatibility without testing. The supported local
integration API is v1.

## Release identity

- Repository: `https://github.com/zelport/zelport-omarchy`
- Name: Zelport Integration
- ID: `zelport.integration`
- Canonical release: `v2026.10.0`
- Derived manifest version: `2026.10.0`
- Author: Zelport
- Description: Unofficial Zelport integration for Omarchy.
- Suggested category: Network
- Suggested tags: zelport, localhost, services, development, networking
- License: MIT

The root manifest is authoritative for the integration version, entry points,
and bar widget metadata. A prepared archive is an alternative for manual
installation; it is not itself a Git repository accepted by
`omarchy plugin add`.

Canonical Integration release identifiers use `vYYYY.MM.MICRO`. `MICRO` starts
at `0` each month and increments for every additional release in that month. The
manifest derives its prefix-free payload from that identifier. Zelport App uses
independent canonical `vMAJOR.MINOR.PATCH` releases. The latest Integration
follows the latest App through Integration API v1 compatibility; an App release
alone does not require an Integration release.

## Reproducible release procedure

1. Confirm the latest stable Zelport App release is public and still provides
   the supported Integration API v1.
2. Confirm the working tree contains the reviewed runtime files, root manifest,
   README, LICENSE, assets, tests, and current documentation. Exclude `bin/`,
   Python caches, captured results, and historical design material.
3. Confirm canonical release `v2026.10.0` derives the `manifest.json` value
   `2026.10.0` and the release commit will receive that exact tag.
4. Run `python3 -m unittest discover -s tests -v`.
5. Run `node --test tests/model.test.cjs` in an isolated Node.js environment.
6. Run `omarchy plugin validate .` and complete
   [native acceptance](../NATIVE_ACCEPTANCE.md) on Omarchy 4.0.4-1 with the
   latest stable Zelport App release and Integration `v2026.10.0`. Exercise only
   clean schema-v1 configuration.
7. Run `python3 scripts/bundle.py` twice and require identical archive SHA-256
   values. Inspect the archive allowlist and checksum manifest.
8. Verify installation, update, and removal on a clean test account. Preserve
   `~/.config/zelport/omarchy.json`, Zelport App configuration, and existing
   shortcuts.
9. Tag the exact verified commit as `v2026.10.0`, create the GitHub release, and
   attach the exact verified `zelport-omarchy.tar.gz` plus its checksum file.

Executed results belong to release verification and are not stored as a
completed checklist in this repository. Any screenshot must use synthetic data
and contain no private domains, endpoints, or settings.

## Catalog submission

Catalog submission is a separate external action and requires explicit approval.
Submit the repository URL, category, and tags through the catalog publishing
form only after the GitHub release is verified. Listing approval does not make
the integration an official Omarchy project and does not validate its security.

## Installation from GitHub

Install and start the latest stable Zelport App release, then add the
integration:

```sh
omarchy plugin add https://github.com/zelport/zelport-omarchy.git --enable
```

The manifest defaults the widget to the right bar section. No global shortcut is
installed automatically. The optional Super + Alt + Z binding and the
Zelport Integration configuration are documented in the root README. Removing
the integration must not stop Zelport App, remove its package, or delete either
configuration file.
