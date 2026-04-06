---
name: posthog-mcp
description: Access the PostHog MCP at https://mcp.posthog.com/mcp through a local mcp2cli wrapper. Use this whenever the user wants to inspect PostHog product analytics, feature flags, experiments, dashboards, persons, prompts, LLM traces, or documentation from the terminal, especially when they mention PostHog, feature flags, experiments, insights, events, logs, dashboards, or analytics queries and need to operate through the MCP instead of writing custom API code.
compatibility: Requires `uvx` with `mcp2cli`, network access to the PostHog MCP endpoint, and `POSTHOG_MCP_TOKEN` set in the environment.
---

# PostHog MCP

This skill uses a skill-local `mcp2cli` baked config plus the wrapper in `scripts/`.

Before using it, ensure the raw PostHog token is present in the environment:

```bash
export POSTHOG_MCP_TOKEN=...
```

The wrapper sets `MCP2CLI_CONFIG_DIR` to the skill's own `config/` directory, derives the required `Authorization: Bearer ...` header from `POSTHOG_MCP_TOKEN`, and then calls the baked tool.

Then use the wrapper:

```bash
bash "${CLAUDE_SKILL_DIR}/scripts/posthog-mcp" --list
```

## Core workflow

1. Discover tools:

```bash
bash "${CLAUDE_SKILL_DIR}/scripts/posthog-mcp" --list
bash "${CLAUDE_SKILL_DIR}/scripts/posthog-mcp" --search feature
```

2. Inspect parameters before calling a tool:

```bash
bash "${CLAUDE_SKILL_DIR}/scripts/posthog-mcp" event-definitions-list --help
bash "${CLAUDE_SKILL_DIR}/scripts/posthog-mcp" docs-search --help
bash "${CLAUDE_SKILL_DIR}/scripts/posthog-mcp" query-run --help
```

3. Start with a read call or a documentation search:

```bash
bash "${CLAUDE_SKILL_DIR}/scripts/posthog-mcp" event-definitions-list --limit 5
bash "${CLAUDE_SKILL_DIR}/scripts/posthog-mcp" docs-search --query "feature flags"
```

4. Use `--jq` for JSON-shaped outputs, but expect some tools to return text content:

```bash
bash "${CLAUDE_SKILL_DIR}/scripts/posthog-mcp" event-definitions-list --limit 5 --jq '.[].name'
```

## Tested behaviors

These were verified against the live endpoint before packaging this skill:

- `--list` works with the supplied bearer token.
- `event-definitions-list --limit 1` succeeded and returned event data.
- `docs-search --query "feature flags"` succeeded and returned documentation content with inline links and citations.
- `organizations-get` returned `403 Forbidden` with the provided token and the message that project-scoped keys only work on project-based endpoints.

That last point matters: treat the provided token as project-scoped unless the user supplies broader credentials.

## What to use first

Start with these tools for most requests:

- `docs-search`
  Use when the user asks how to do something in PostHog and you need product documentation first.
- `event-definitions-list`
  Use to confirm event names before building queries or insights.
- `query-run`
  Use for custom analytics queries when you already have the query payload. It takes a single `--query` argument or stdin JSON, not many small convenience flags.
- `feature-flag-get-all`
  Use to inspect feature flags.
- `experiment-get-all`
  Use to inspect experiments.
- `dashboards-get-all`
  Use to inspect dashboards.
- `query-llm-traces-list`
  Use for LLM observability data stored in PostHog.

## Scope and auth guidance

- Expect project-level access by default.
- If an org-level tool fails with `403`, do not keep retrying. Explain that the token is project-scoped and switch to project-based tools.
- Keep the secret out of command arguments. This wrapper is configured to read `POSTHOG_MCP_TOKEN` from the environment.

## CLI gotchas

- Global options such as `--head` belong before the subcommand:

```bash
bash "${CLAUDE_SKILL_DIR}/scripts/posthog-mcp" --head 2 docs-search --query "feature flags"
```

- Not every tool supports `--limit`. Check `--help` before assuming pagination flags exist.
- Some outputs are text-heavy rather than plain JSON arrays. `docs-search` is useful for guidance, but its output is not shaped like the event listing endpoints.
- `query-run` is flexible but low-level. Prefer a narrower read tool first if the user only needs event names, dashboards, persons, or flags.
- Some API failures are returned as `Error: ...` text while the wrapper still exits with status `0`. For permission-sensitive checks such as `organizations-get`, inspect the output text itself instead of trusting exit status alone.

## Examples

Search docs for a product concept:

```bash
bash "${CLAUDE_SKILL_DIR}/scripts/posthog-mcp" docs-search --query "feature flags"
```

List a few event definitions:

```bash
bash "${CLAUDE_SKILL_DIR}/scripts/posthog-mcp" event-definitions-list --limit 5
```

Inspect available feature-flag tools:

```bash
bash "${CLAUDE_SKILL_DIR}/scripts/posthog-mcp" --search flag
```
