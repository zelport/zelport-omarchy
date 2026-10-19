# Working on zelport-omarchy

Read README.md before making changes. Write documentation, code comments,
errors and UI text in English.

The canonical Integration release identifier is `vYYYY.MM.MICRO`. Use it in
documentation, operator inputs, tags, GitHub Releases and reports. The manifest
stores the derived `YYYY.MM.MICRO` payload because its format omits the prefix.
`MICRO` starts at `0` each month and increments for every additional Integration
release in that month.

Zelport App releases remain independent and use canonical
`vMAJOR.MINOR.PATCH`. The latest Integration follows the latest App through
Integration API v1 compatibility; do not publish or pin a new Integration
release solely because the App version changed.

## Commit messages

Use [Conventional Commits 1.0.0](https://www.conventionalcommits.org/en/v1.0.0/)
for all new commits. Write commit messages in English.

Format: `<type>[optional scope][!]: <description>`.

Use `feat` for new features and `fix` for bug fixes. Use `docs`, `build`, `ci`,
`test`, `refactor`, `perf`, `style`, or `chore` where appropriate. Use lowercase
types and short, meaningful scopes. Keep each commit focused on one logical
change and write a concise description of what it does.

Mark breaking changes with `!` before the colon or a `BREAKING CHANGE:` footer.
Explain the impact and migration steps in the body when needed. Squash commit
titles must follow the same convention.

Examples:

- `feat(homebrew): support user services`
- `fix(relay): preserve client identities on reconnect`
- `docs: clarify installation instructions`
- `feat(integration): publish zelport v2026.10.0`

Do not rewrite existing shared history merely to change commit message format.

## Preparing changes for publication

Keep source repositories independent of the frozen source container. Do not
commit binaries, generated release archives, local staging caches, credentials,
or user runtime configuration. Review staged changes and run the repository's
relevant checks before committing. Preparation for a push does not authorize
changing repository visibility or publishing releases.

## Privacy in published material

Use synthetic examples in documentation, tests, screenshots and verification
reports. Use reserved example domains such as `desktop.example.test`, generic
paths such as `~/.config/zelport/`, and temporary test data. Never publish real
internal hostnames, personal home-directory paths, private email addresses,
credentials or user configuration. Check tracked files and staged diffs before
publication, including generated source bundles.

Preserve the existing repository-local Git author and committer configuration
unless the user explicitly requests a change.
