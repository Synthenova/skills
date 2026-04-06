---
name: langfuse-mcp
description: Access the Langfuse MCP at http://72.61.251.227:8789/mcp through a local mcp2cli wrapper. Use this whenever the user wants to inspect Langfuse traces, observations, prompts, sessions, scores, datasets, or exceptions from the terminal, especially when they mention Langfuse, traces, prompts, sessions, datasets, prompt versions, or observability data and need to query the MCP rather than write custom code.
compatibility: Requires `uvx` with `mcp2cli` access and network access to the Langfuse MCP endpoint.
---

# Langfuse MCP

This skill uses a skill-local `mcp2cli` baked config plus the wrapper in `scripts/`.

Use the wrapper instead of repeating the raw endpoint URL:

```bash
bash "${CLAUDE_SKILL_DIR}/scripts/langfuse-mcp" --list
```

The wrapper sets `MCP2CLI_CONFIG_DIR` to the skill's own `config/` directory, so this skill does not depend on global `~/.config/mcp2cli` state.

## Core workflow

1. Discover tools:

```bash
bash "${CLAUDE_SKILL_DIR}/scripts/langfuse-mcp" --list
bash "${CLAUDE_SKILL_DIR}/scripts/langfuse-mcp" --search trace
```

2. Inspect parameters before calling a tool:

```bash
bash "${CLAUDE_SKILL_DIR}/scripts/langfuse-mcp" fetch-traces --help
bash "${CLAUDE_SKILL_DIR}/scripts/langfuse-mcp" list-prompts --help
```

3. Run the smallest useful query first:

```bash
bash "${CLAUDE_SKILL_DIR}/scripts/langfuse-mcp" fetch-traces --limit 1
bash "${CLAUDE_SKILL_DIR}/scripts/langfuse-mcp" list-prompts --limit 5
bash "${CLAUDE_SKILL_DIR}/scripts/langfuse-mcp" list-datasets --limit 5
```

4. Use `--jq` for follow-up filtering instead of ad hoc scripts:

```bash
bash "${CLAUDE_SKILL_DIR}/scripts/langfuse-mcp" --jq '.data | length' list-datasets
bash "${CLAUDE_SKILL_DIR}/scripts/langfuse-mcp" --jq '.data[]?.id' fetch-traces --limit 5
```

## Tested behaviors

These were verified against the live endpoint before packaging this skill:

- `--list` works without an auth header on the supplied endpoint.
- `list-prompts --limit 1` returned a valid empty paginated result:

```json
{"data":[],"metadata":{"page":1,"limit":1,"item_count":0,"total":null}}
```

- `list-datasets --limit 1` also returned a valid empty paginated result. Empty collections are normal and should not be treated as transport failures.
- `get-data-schema` returns a Markdown-style schema document, not JSON. Do not assume every tool returns machine-shaped JSON.
- `fetch-traces --help` shows `--include-observations` and `--output-mode`. Those materially affect response size and latency.

## What to use first

Start with these tools for most requests:

- `get-data-schema`
  Use when you need to understand trace, observation, event, or score fields before querying.
- `fetch-traces`
  Use for recent traces, filtering by age, name, user, session, metadata, or tags.
- `fetch-trace`
  Use when you already have a trace ID and need full details.
- `list-prompts`
  Use to enumerate prompts and labels before fetching one by name.
- `get-prompt`
  Use when you know the prompt name and want the resolved prompt.
- `fetch-sessions`
  Use to inspect session activity.
- `find-exceptions`
  Use for error-oriented investigations.

## Response-size guidance

- Prefer `fetch-traces --limit N` before broader queries.
- Only add `--include-observations` when the task explicitly needs prompt bodies, model parameters, or embedded observation details.
- If the user needs raw complete output, switch `fetch-traces` to `--output-mode full_json_file` so the result is written to disk instead of forcing a huge inline payload.
- When a list call returns `{data, metadata}`, read `metadata` before deciding whether you need another page.

## Gotchas

- Some Langfuse tools return structured JSON, while `get-data-schema` returns documentation text. Inspect the output shape before piping it into `--jq`.
- Empty `data` arrays are valid. Do not invent missing-data errors when the transport succeeded.
- The safest first pass is always a low `--limit` or a narrow filter.
- Keep the user in control of scope. If they ask a broad observability question, identify whether they actually want traces, sessions, prompts, scores, or exceptions before running tools.

## Examples

Recent traces:

```bash
bash "${CLAUDE_SKILL_DIR}/scripts/langfuse-mcp" fetch-traces --age 60 --limit 5
```

Recent traces with only IDs:

```bash
bash "${CLAUDE_SKILL_DIR}/scripts/langfuse-mcp" --jq '.data[]?.id' fetch-traces --age 60 --limit 5
```

Prompt inventory:

```bash
bash "${CLAUDE_SKILL_DIR}/scripts/langfuse-mcp" list-prompts --limit 20
```

Inspect the data model before querying:

```bash
bash "${CLAUDE_SKILL_DIR}/scripts/langfuse-mcp" get-data-schema
```
