---
name: gsc-cli
description: Use a local `gsc-cli` wrapper to inspect Google Search Console properties, search analytics, indexing status, URL inspection results, and sitemap data from the terminal. Trigger this skill for SEO investigations that should be handled through the existing CLI instead of custom Python or direct API code.
---

# GSC CLI

This skill uses the local `gsc-cli` wrapper so you can discover commands, inspect arguments, and run Search Console queries from the shell.

Use the wrapper in [`scripts/gsc-cli`](/home/lamrin/skills/gsc-cli/scripts/gsc-cli) instead of repeating the install and environment setup by hand.

## Quick Start

Run the wrapper from the skill directory:

```bash
bash scripts/gsc-cli --list
```

The wrapper defaults to:

- `GSC_SOURCE=git+https://github.com/AminForou/mcp-gsc`
- `GSC_CREDENTIALS_PATH` must point to a service account JSON file unless the local default path exists
- `GSC_SKIP_OAUTH=true`
- `GSC_DATA_STATE=all`

Override any of those with environment variables before invoking the wrapper.

For a public installation, expect to set at least:

```bash
export GSC_CREDENTIALS_PATH=/full/path/to/service_account_credentials.json
```

Optionally set these for convenience:

```bash
export GSC_SOURCE=git+https://github.com/AminForou/mcp-gsc
export GSC_DATA_STATE=all
export GSC_SKIP_OAUTH=true
```

## Core Workflow

1. Discover tools:

```bash
bash scripts/gsc-cli --list
bash scripts/gsc-cli --search analytics
```

2. Inspect parameters before calling a tool:

```bash
bash scripts/gsc-cli get-search-analytics --help
bash scripts/gsc-cli inspect-url-enhanced --help
bash scripts/gsc-cli list-sitemaps-enhanced --help
```

3. Start with low-risk read calls:

```bash
bash scripts/gsc-cli list-properties
bash scripts/gsc-cli get-performance-overview --site-url sc-domain:example.com --days 28
```

4. Use `--jq` only after confirming the output shape:

```bash
bash scripts/gsc-cli --jq '.[]?' list-properties
```

Some tools return formatted text rather than clean JSON arrays, so do not assume `--jq` will always help.

## What To Use First

- `list-properties`
  Use first to get the exact property string. Domain properties use `sc-domain:example.com`.
- `get-performance-overview`
  Use for a fast summary before running broader analytics pulls.
- `get-search-analytics`
  Use for top queries, pages, countries, devices, or dates. Check `--help` for the `dimensions` syntax.
- `inspect-url-enhanced`
  Use when the user already has one URL and needs crawl/indexing detail.
- `check-indexing-issues`
  Use when the user has a short list of URLs and wants to find indexing problems across them.
- `list-sitemaps-enhanced`
  Use to inventory sitemap coverage and warning counts before submitting or deleting anything.

## Auth And Safety

- The wrapper is configured for service-account auth by default because interactive OAuth is not reliable for this non-interactive CLI flow.
- If OAuth is required, prepare the auth flow separately first, then switch `GSC_SKIP_OAUTH=false` only after token setup is complete.
- Destructive tools such as `add-site`, `delete-site`, `submit-sitemap`, and `delete-sitemap` exist, but the server blocks the dangerous ones unless `GSC_ALLOW_DESTRUCTIVE=true` is set.
- Do not enable destructive mode unless the user explicitly asks for a state-changing action.

## Environment Contract

- `GSC_CREDENTIALS_PATH`
  Preferred. Absolute path to the Google service account JSON file.
- `GSC_SOURCE`
  Optional. Package source passed to `uvx --from ...`. Leave it at the default unless you need a fork or pinned revision.
- `GSC_DATA_STATE`
  Optional. `all` by default. Set `final` only when you explicitly want confirmed-only data.
- `GSC_SKIP_OAUTH`
  Optional. `true` by default for non-interactive usage.
- `GSC_ALLOW_DESTRUCTIVE`
  Optional. Leave unset unless you explicitly need state-changing commands.

## Usage Discipline

- Ask the user for the exact property string or run `list-properties` first.
- Pass `--site-url` explicitly for property-specific commands. Do not assume a default domain.
- Keep example property strings neutral in explanations unless the user provides a real target.

## References

Read [`references/tool-map.md`](/home/lamrin/skills/gsc-cli/references/tool-map.md) when you need the full command inventory, argument guidance, or example commands by task.
