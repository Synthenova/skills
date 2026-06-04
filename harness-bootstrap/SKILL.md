---
name: harness-bootstrap
description: Bootstrap a repository into an agent-ready codebase before feature implementation. Use when the user wants Codex to scan a repo, create or update .harness artifacts, document environment variables, CLI/MCP/skill requirements, test and deployment commands, observability/logging, design language, codebase knowledge sources, and report READY / PARTIALLY READY / NOT READY with missing items.
---

# Harness Bootstrap

Use this skill to initialize or audit a codebase so a fresh coding agent can understand, operate, verify, and debug the repository without relying on chat history. This skill is for readiness setup, not feature implementation.

## Core Rule

Create target-repo artifacts under `.harness/`. Do not dump large deterministic scaffolds into the repository root. A root `AGENTS.md` or `CLAUDE.md` router is optional and should be created only when the user asks or the agent platform needs it.

## Workflow

1. Run the bootstrap scanner:

```bash
python3 <skill-dir>/scripts/bootstrap_harness.py --target <repo>
```

Use `--with-root-router` only after user approval.

2. Read `.harness/generated/readiness-report.json` and `.harness/READINESS.md`.
3. Inspect missing items and any failed commands.
4. Ask targeted questions only for facts that cannot be inferred from the repo.
5. If the user answers, update the relevant `.harness/` files and rerun the scanner if needed.
6. Report the readiness status exactly as `READY`, `PARTIALLY READY`, or `NOT READY`.

## Readiness Gates

The repo is `READY` only when all core gates are satisfied:

- Instruction surface: `.harness/INDEX.md` routes agents to current repo facts.
- Environment: install/start commands and required env vars are documented.
- Verification: base check/test command is known and runnable, or a clear failing baseline is recorded.
- Architecture: system shape and important boundaries are documented.
- Tooling: required CLIs, MCP servers, and skills are documented.
- Deployment: deploy target or release path is documented.
- Observability: logs, errors, metrics, traces, or the absence of telemetry is documented.
- Knowledge: repo map exists; Understand Anything graph status is recorded when present.
- Fresh-session test: a cold agent can answer what the repo is, how it is organized, how to run, how to verify, and what is not ready.

If any gate is missing, the repo is not ready; do not soften the result.

## Understand Anything Integration

If `.understand-anything/knowledge-graph.json` exists, treat it as a codebase knowledge source and record graph freshness by comparing `.understand-anything/meta.json` with `git rev-parse HEAD`.

If Understand Anything is not present, list it as optional. Recommend it when the repo is large, hard to navigate, or needs incremental knowledge maintenance. If enabled and graph files are large, note that Git LFS is acceptable for `.understand-anything/*.json`.

Do not install external plugins or modify git hooks without explicit user approval.

## Env And Secrets

Never copy secret values into `.harness`. Scan names and references only. Prefer placeholders, sources, and scope:

- local/dev/test/prod
- required/optional
- source file where referenced
- owner or unknown

If a required variable is found in code but not documented by `.env.example`, mark it as missing.

## Generated Artifacts

The scanner writes or updates:

```text
.harness/
├── INDEX.md
├── READINESS.md
├── FRESH_SESSION_TEST.md
├── ENVIRONMENT.md
├── TOOLING.md
├── TESTING.md
├── DEPLOYMENT.md
├── OBSERVABILITY.md
├── DESIGN_LANGUAGE.md
├── SECURITY.md
├── QUALITY.md
├── KNOWLEDGE.md
├── RUNBOOKS.md
├── generated/
│   ├── repo-map.md
│   ├── env-scan.md
│   ├── test-scan.md
│   ├── ci-cd-scan.md
│   ├── observability-scan.md
│   └── readiness-report.json
└── state/
    ├── questions.md
    └── validation-history.md
```

The scanner may overwrite these `.harness/` generated files because they are harness-owned. It must not overwrite app source files.

## When To Read References

- For readiness philosophy and pass/fail policy, read `references/readiness-model.md`.
- For target artifact meanings, read `references/artifact-contract.md`.

## Final Response Shape

After running the skill, summarize:

```text
Harness status: <READY|PARTIALLY READY|NOT READY>

Ready:
- ...

Not ready:
- ...

Questions:
- ...

Artifacts:
- .harness/READINESS.md
- .harness/generated/readiness-report.json
```

Keep this about codebase readiness. Do not start implementing product features.
