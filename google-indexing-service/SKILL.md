---
name: google-indexing-service
description: Explain and use the `gis` Google Indexing CLI in a simple way. Trigger this skill when Codex needs to show how `gis` works, validate its credentials setup, or run a small indexing request with a service account JSON file supplied through `GIS_CREDENTIALS_PATH`.
---

# Google Indexing Service

This skill is only a usage guide for the installed `gis` CLI.

Use `GIS_CREDENTIALS_PATH` as the credential environment variable and call `gis` directly.

## Quick Start

Set the credential path:

```bash
export GIS_CREDENTIALS_PATH=/full/path/to/service_account_credentials.json
```

Inspect usage:

```bash
gis --help
gis --version
```

Run a one-URL request:

```bash
gis conthunt.app --path "$GIS_CREDENTIALS_PATH" --urls https://conthunt.app/
```

## Core Workflow

1. Inspect usage first:

```bash
gis --help
gis --version
```

2. Validate that the credentials file is readable and the service account can reach Search Console:

```bash
gis example.com --path "$GIS_CREDENTIALS_PATH"
```

If the service account does not have access, the CLI fails during the site access check.

3. Prefer an explicit one-URL request instead of a whole-domain run:

```bash
gis conthunt.app --path "$GIS_CREDENTIALS_PATH" --urls https://conthunt.app/
```

4. Only omit `--urls` when the user explicitly wants the CLI to pull pages from submitted sitemaps:

```bash
gis conthunt.app --path "$GIS_CREDENTIALS_PATH"
```

## Environment Contract

- `GIS_CREDENTIALS_PATH`
  Required. Absolute path to the Google service account JSON file.

## Behavior Notes

- `gis` is single-purpose. Beyond `--help` and `--version`, a real run proceeds toward indexing checks and may eventually call the Indexing API publish endpoint.
- If you pass `--urls`, keep the list small unless the user explicitly wants a broader run.
- Prefer a one-URL request over a whole-domain run when validating behavior.
- The CLI requires the service account to have access to the target site in Search Console and the relevant Google APIs enabled.
- `gis example.com --path "$GIS_CREDENTIALS_PATH"` is a safe validation pattern when the service account does not have access to `example.com`, because it fails before any indexing request.

## Main Options

- `--path <path>`
  Path to the service account JSON file.
- `--urls <urls>`
  Comma-separated explicit URL list to process.
- `--rpm-retry`
  Retry when rate-limited on read requests.
- `--client-email <email>`
  Service account client email if not using `--path`.
- `--private-key <key>`
  Service account private key if not using `--path`.

## Tested Behavior

- `gis --help` works.
- `gis --version` works.
- `gis example.com --path /home/lamrin/paperclip/service_account_credentials.json` fails with a Search Console access error before any indexing request.
