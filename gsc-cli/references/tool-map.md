# GSC Command Map

Use this file when you need the local `gsc-cli` command inventory without rediscovering the interface from scratch.

## Runtime

- Backing source: `uvx --from "${GSC_SOURCE:-git+https://github.com/AminForou/mcp-gsc}" mcp-gsc`
- Canonical wrapper: [`scripts/gsc-cli`](/home/lamrin/skills/gsc-cli/scripts/gsc-cli)
- Default auth mode in this skill: service account via `GSC_CREDENTIALS_PATH`
- Default data freshness: `GSC_DATA_STATE=all`
- Optional default property: `GSC_SITE_URL`

## Available commands

### Properties

- `list-properties`: list accessible Search Console properties and permission levels.
- `get-site-details`: fetch detailed metadata for one property.
- `add-site`: add a property. Requires `GSC_ALLOW_DESTRUCTIVE=true`.
- `delete-site`: remove a property. Requires `GSC_ALLOW_DESTRUCTIVE=true`.

### Search analytics

- `get-search-analytics`: basic analytics by dimension and date window.
- `get-performance-overview`: summary metrics for one property.
- `get-advanced-search-analytics`: broader analytics with sorting and filtering.
- `compare-search-periods`: compare two date windows.
- `get-search-by-page-query`: break one page down by queries.

### URL inspection

- `inspect-url-enhanced`: inspect one URL in detail.
- `batch-url-inspection`: inspect multiple URLs in one call.
- `check-indexing-issues`: summarize indexing problems across a URL set.

### Sitemaps

- `get-sitemaps`: basic sitemap list.
- `list-sitemaps-enhanced`: sitemap list with richer status detail.
- `get-sitemap-details`: fetch one sitemap.
- `submit-sitemap`: submit or resubmit a sitemap.
- `delete-sitemap`: unsubmit a sitemap. Requires `GSC_ALLOW_DESTRUCTIVE=true`.
- `manage-sitemaps`: combined list/get/submit/delete entrypoint.

### Miscellaneous

- `get-creator-info`: return project author information.
- `reauthenticate`: clear auth state and try to start a new login flow. This is not useful from non-interactive stdio unless OAuth was prepared manually first.

## Examples

List properties:

```bash
bash scripts/gsc-cli list-properties
```

Inspect a property summary:

```bash
bash scripts/gsc-cli get-performance-overview --site-url sc-domain:example.com --days 28
```

Inspect one URL:

```bash
bash scripts/gsc-cli inspect-url-enhanced \
  --site-url sc-domain:conthunt.app \
  --page-url https://conthunt.app/
```

Find tool details before a call:

```bash
bash scripts/gsc-cli get-advanced-search-analytics --help
```

## Gotchas

- Property strings must match GSC exactly. Run `list-properties` first if there is any doubt.
- Domain properties use `sc-domain:example.com`, not `https://example.com`.
- `GSC_DATA_STATE=all` includes fresh data and matches the GSC dashboard more closely than `final`.
- Some responses are formatted text. Do not assume machine-shaped JSON for every tool.
- If `GSC_SITE_URL` is set, the wrapper injects `--site-url` automatically for commands that require it unless you pass `--site-url` explicitly.
- The wrapper installs and runs the backing CLI through `uvx`, so users do not need a separate checkout on disk.
