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

From the `posthog-mcp` skill directory, use the wrapper like this:

```bash
bash scripts/posthog-mcp --list
```

## Core workflow

1. Discover tools:

```bash
bash scripts/posthog-mcp --list
bash scripts/posthog-mcp --search feature
```

2. Inspect parameters before calling a tool:

```bash
bash scripts/posthog-mcp event-definitions-list --help
bash scripts/posthog-mcp docs-search --help
bash scripts/posthog-mcp query-run --help
```

3. Start with a read call or a documentation search:

```bash
bash scripts/posthog-mcp event-definitions-list --limit 5
bash scripts/posthog-mcp docs-search --query "feature flags"
```

4. Use `--jq` for JSON-shaped outputs, but expect some tools to return text content:

```bash
bash scripts/posthog-mcp --jq '.[].name' event-definitions-list --limit 5
```

## Available tools

### Documentation and general discovery

- `docs-search`: search PostHog docs and return guidance with links.
- `entity-search`: search across PostHog entities by name or description.
- `query-run`: run a custom analytics query payload directly.
- `projects-get`: list projects accessible in the current organization context.
- `organizations-get`: list accessible organizations.
- `organization-details-get`: fetch details for the active organization.
- `switch-organization`: change the active organization.
- `switch-project`: change the active project.
- `debug-mcp-ui-apps`: return sample data for MCP Apps SDK debugging.

### Events, properties, and actions

- `event-definitions-list`: list event definitions in the current project.
- `event-definition-update`: update event definition metadata.
- `properties-list`: list known event or person properties.
- `actions-get-all`: list reusable actions.
- `action-get`: fetch one action by action ID.

### Insights and dashboards

- `insights-get-all`: list insights with optional filtering.
- `insight-get`: fetch one insight by insight ID.
- `insight-query`: run an existing insight and return results.
- `insight-update`: update an insight definition.
- `insight-delete`: soft-delete an insight.
- `insight-create-from-query`: create an insight from a query payload that has already been tested.
- `dashboards-get-all`: list dashboards.
- `dashboard-get`: fetch one dashboard with tiles.
- `dashboard-create`: create a dashboard.
- `dashboard-update`: update a dashboard.
- `dashboard-delete`: soft-delete a dashboard.
- `dashboard-reorder-tiles`: reorder tiles within a dashboard.

### Experiments and feature flags

- `experiment-get-all`: list experiments.
- `experiment-get`: fetch one experiment by experiment ID.
- `experiment-create`: create a new experiment.
- `experiment-update`: update an experiment.
- `experiment-delete`: delete an experiment.
- `experiment-results-get`: fetch experiment result metrics.
- `feature-flag-get-all`: list feature flags.
- `feature-flag-get-definition`: fetch one feature flag by flag ID.
- `create-feature-flag`: create a feature flag.
- `update-feature-flag`: update a feature flag.
- `delete-feature-flag`: soft-delete a feature flag.
- `feature-flags-activity-retrieve`: fetch a feature flag audit trail.
- `feature-flags-dependent-flags-retrieve`: list flags that depend on another flag.
- `feature-flags-status-retrieve`: fetch health and evaluation status for a flag.
- `feature-flags-evaluation-reasons-retrieve`: debug why a flag evaluates the way it does for a user.
- `feature-flags-user-blast-radius-create`: estimate the impact of a release condition before applying it.
- `feature-flags-copy-flags-create`: copy a feature flag to other projects.
- `scheduled-changes-list`: list scheduled future changes to feature flags.
- `scheduled-changes-get`: fetch one scheduled change by ID.
- `scheduled-changes-create`: create a scheduled change.
- `scheduled-changes-update`: update a scheduled change.
- `scheduled-changes-delete`: delete a scheduled change.
- `early-access-feature-list`: list early-access features.
- `early-access-feature-retrieve`: fetch one early-access feature.

### Surveys, annotations, alerts, and activity

- `survey-create`: create a survey.
- `survey-get`: fetch one survey by survey ID.
- `surveys-get-all`: list surveys.
- `survey-update`: update a survey.
- `survey-delete`: archive a survey.
- `surveys-global-stats`: fetch aggregated survey response stats.
- `survey-stats`: fetch detailed stats for one survey.
- `annotations-list`: list annotations in the current project.
- `annotation-retrieve`: fetch one annotation by annotation ID.
- `alerts-list`: list insight alerts.
- `alert-get`: fetch one alert by alert ID.
- `alert-simulate`: run anomaly detection on an insight without creating a persistent alert.
- `activity-logs-list`: list recent project activity logs.

### Logs and error tracking

- `logs-query`: search project logs with filters.
- `logs-list-attributes`: list available log attributes.
- `logs-list-attribute-values`: list observed values for a log attribute.
- `error-tracking-issues-list`: list error tracking issues.
- `error-tracking-issues-retrieve`: fetch one error tracking issue by ID.
- `query-error-tracking-issues`: query and filter error tracking issues.

### Persons, cohorts, and user analysis

- `persons-list`: list persons in the project.
- `persons-retrieve`: fetch one person by numeric ID or UUID.
- `persons-cohorts-retrieve`: list cohorts that contain a specific person.
- `persons-values-retrieve`: list distinct values for a person property.
- `cohorts-list`: list cohorts.
- `cohorts-retrieve`: fetch one cohort by cohort ID.

### Data warehouse, endpoints, notebooks, proxies, and workflows

- `view-list`: list saved data warehouse queries or views.
- `view-get`: fetch one saved view by ID.
- `view-run-history`: list recent materialization runs for a view.
- `endpoints-get-all`: list saved query endpoints.
- `endpoint-get`: fetch one endpoint by name.
- `endpoint-run`: execute an endpoint query.
- `endpoint-versions`: list endpoint versions.
- `endpoint-materialization-status`: fetch endpoint materialization status.
- `notebooks-list`: list notebooks.
- `notebooks-retrieve`: fetch one notebook by short ID.
- `proxy-list`: list managed reverse proxies.
- `proxy-get`: fetch one reverse proxy by ID.
- `workflows-list`: list workflows.
- `workflows-get`: fetch one workflow by workflow ID.

### CDP functions

- `cdp-function-templates-list`: list function templates.
- `cdp-function-templates-retrieve`: fetch one function template by template ID.
- `cdp-functions-list`: list configured functions such as destinations, transformations, site apps, and sources.
- `cdp-functions-retrieve`: fetch one function by function ID.

### Prompts and LLM observability

- `prompt-list`: list stored LLM prompts.
- `prompt-get`: fetch one LLM prompt by name.
- `query-llm-traces-list`: list LLM traces in PostHog.
- `query-llm-trace`: fetch one LLM trace by trace ID.
- `get-llm-total-costs-for-project`: fetch daily LLM costs by model.

### Standard product analytics queries

- `query-trends`: run a trends query.
- `query-funnel`: run a funnel query.
- `query-retention`: run a retention query.
- `query-stickiness`: run a stickiness query.
- `query-paths`: run a paths query.
- `query-lifecycle`: run a lifecycle query.

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
bash scripts/posthog-mcp --head 2 docs-search --query "feature flags"
```

- Not every tool supports `--limit`. Check `--help` before assuming pagination flags exist.
- Some outputs are text-heavy rather than plain JSON arrays. `docs-search` is useful for guidance, but its output is not shaped like the event listing endpoints.
- `query-run` is flexible but low-level. Prefer a narrower read tool first if the user only needs event names, dashboards, persons, or flags.
- Some API failures are returned as `Error: ...` text while the wrapper still exits with status `0`. For permission-sensitive checks such as `organizations-get`, inspect the output text itself instead of trusting exit status alone.

## Examples

Search docs for a product concept:

```bash
bash scripts/posthog-mcp docs-search --query "feature flags"
```

List a few event definitions:

```bash
bash scripts/posthog-mcp event-definitions-list --limit 5
```

Inspect available feature-flag tools:

```bash
bash scripts/posthog-mcp --search flag
```
