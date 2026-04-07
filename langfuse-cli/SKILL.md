name: langfuse-cli
description: Access Langfuse through a local stdio `langfuse-mcp` process wrapped by `mcp2cli`. Use this whenever the user wants to inspect Langfuse traces, observations, prompts, sessions, scores, datasets, or exceptions from the terminal and should talk to the MCP over stdio instead of a long-lived HTTP bridge.
compatibility: Requires `uvx` with `mcp2cli` access, `uvx --python 3.11 langfuse-mcp`, and `LANGFUSE_PUBLIC_KEY`, `LANGFUSE_SECRET_KEY`, and `LANGFUSE_HOST` in the environment.
---

# Langfuse CLI

This skill uses a skill-local `mcp2cli` baked config plus the wrapper in `scripts/`, but it connects to Langfuse over stdio rather than an HTTP MCP bridge.

From the `langfuse-cli` skill directory, use the wrapper instead of repeating the stdio command and env setup:

```bash
bash scripts/langfuse-cli --list
```

The wrapper sets `MCP2CLI_CONFIG_DIR` to the skill's own `config/` directory, so this skill does not depend on global `~/.config/mcp2cli` state. The wrapper expects `LANGFUSE_PUBLIC_KEY`, `LANGFUSE_SECRET_KEY`, and `LANGFUSE_HOST` to already be exported in the shell.

Before using it:

```bash
export LANGFUSE_PUBLIC_KEY=...
export LANGFUSE_SECRET_KEY=...
export LANGFUSE_HOST=https://cloud.langfuse.com
```

If `/tmp/langfuse_mcp.log` exists but is not writable by the current user, the stdio server can fail at startup. Clear or chown that file before retrying.

## Core workflow

1. Discover tools:

```bash
bash scripts/langfuse-cli --list
bash scripts/langfuse-cli --search trace
```

2. Inspect parameters before calling a tool:

```bash
bash scripts/langfuse-cli fetch-traces --help
bash scripts/langfuse-cli list-prompts --help
```

3. Run the smallest useful query first:

```bash
bash scripts/langfuse-cli fetch-traces --limit 1
bash scripts/langfuse-cli list-prompts --limit 5
bash scripts/langfuse-cli list-datasets --limit 5
```

4. Use `--jq` for follow-up filtering instead of ad hoc scripts:

```bash
bash scripts/langfuse-cli --jq '.data | length' list-datasets
bash scripts/langfuse-cli --jq '.data[]?.id' fetch-traces --limit 5
```

## Available tools

### Prompts

- `list-prompts`: list prompt definitions and filter by prompt metadata such as name, label, or tag.
- `get-prompt`: fetch a prompt by name with dependencies resolved.
- `get-prompt-unresolved`: fetch the raw prompt definition without resolving dependencies.
- `create-text-prompt`: create a new text prompt version.
- `create-chat-prompt`: create a new chat prompt version.
- `update-prompt-labels`: update labels for a specific prompt version.

### Traces and observations

- `fetch-traces`: search traces with optional filters such as age, name, user, session, tags, or metadata.
- `fetch-trace`: fetch one trace by trace ID with full details.
- `fetch-observations`: list observations filtered by type and related criteria.
- `fetch-observation`: fetch one observation by observation ID.
- `get-data-schema`: return the Langfuse trace, observation, event, and score schema reference.

### Sessions

- `fetch-sessions`: list sessions in the current project.
- `get-session-details`: fetch one session with detailed session information.
- `get-user-sessions`: list sessions for a specific user in a time range.

### Scores

- `list-scores-v2`: list scores with optional filters.
- `get-score-v2`: fetch one score by score ID.

### Datasets

- `list-datasets`: list datasets in the current project.
- `get-dataset`: fetch one dataset by dataset name.
- `create-dataset`: create a new dataset.
- `list-dataset-items`: list items inside a dataset with pagination and filtering.
- `get-dataset-item`: fetch one dataset item by item ID.
- `create-dataset-item`: create or upsert a dataset item.
- `delete-dataset-item`: permanently delete a dataset item.

### Annotation queues

- `list-annotation-queues`: list annotation queues.
- `create-annotation-queue`: create a new annotation queue.
- `get-annotation-queue`: fetch one annotation queue by queue ID.
- `list-annotation-queue-items`: list items inside an annotation queue.
- `get-annotation-queue-item`: fetch one queue item by queue ID and item ID.
- `create-annotation-queue-item`: add an item to an annotation queue.
- `update-annotation-queue-item`: update the status of a queue item.
- `delete-annotation-queue-item`: remove an item from an annotation queue.
- `create-annotation-queue-assignment`: assign a user to a queue.
- `delete-annotation-queue-assignment`: remove a user assignment from a queue.

### Exceptions and errors

- `find-exceptions`: aggregate exceptions by file path, function, or type.
- `find-exceptions-in-file`: inspect exceptions for a specific file.
- `get-exception-details`: fetch detailed exception data for a trace or span.
- `get-error-count`: return the number of traces with exceptions in a recent time window.

## Tested behaviors

These were verified against the stdio server before packaging this skill:

- `--list` works over stdio when `LANGFUSE_PUBLIC_KEY`, `LANGFUSE_SECRET_KEY`, and `LANGFUSE_HOST` are set.
- `list-prompts --limit 1` returned a valid empty paginated result:

```json
{"data":[],"metadata":{"page":1,"limit":1,"item_count":0,"total":null}}
```

- `list-datasets --limit 1` also returned a valid empty paginated result. Empty collections are normal and should not be treated as transport failures.
- `get-data-schema` returns a Markdown-style schema document, not JSON. Do not assume every tool returns machine-shaped JSON.
- `fetch-traces --help` shows `--include-observations` and `--output-mode`. Those materially affect response size and latency.
- If `/tmp/langfuse_mcp.log` is root-owned from an earlier privileged run, the stdio server can fail with `PermissionError`. Remove that file before retrying.

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
bash scripts/langfuse-cli fetch-traces --age 60 --limit 5
```

Recent traces with only IDs:

```bash
bash scripts/langfuse-cli --jq '.data[]?.id' fetch-traces --age 60 --limit 5
```

Prompt inventory:

```bash
bash scripts/langfuse-cli list-prompts --limit 20
```

Inspect the data model before querying:

```bash
bash scripts/langfuse-cli get-data-schema
```
