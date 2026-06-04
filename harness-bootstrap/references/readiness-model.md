# Readiness Model

Agent readiness is an initialization phase. It is complete only when a fresh agent can operate the repository without oral context and without first repairing basic setup.

## Fresh-Session Questions

A cold agent must answer from repo artifacts:

1. What is this system?
2. How is it organized?
3. How do I install and run it?
4. How do I verify it?
5. What tools, env vars, MCP servers, and skills are required?
6. Where are logs, telemetry, errors, and deployment signals?
7. What remains unknown or not ready?

## Status Rules

- `READY`: all core gates have evidence and no critical unknowns remain.
- `PARTIALLY READY`: the repo has a usable harness surface, but one or more gates are incomplete or unverified.
- `NOT READY`: install/run/test path is unknown, repo identity is unclear, or the harness cannot give a fresh agent a safe starting path.

## Core Gates

| Gate | Evidence |
|---|---|
| Instruction surface | `.harness/INDEX.md`, optional root router |
| Environment | install/start commands, runtime versions, env inventory |
| Verification | test/check/build commands, baseline result when run |
| Architecture | repo map, detected stack, boundaries or unknowns |
| Tooling | required CLIs, MCPs, skills |
| Deployment | CI/CD files, platform docs, release path |
| Observability | logs, telemetry, error reporting, dashboards |
| Knowledge | generated repo map or Understand Anything graph |
| Fresh session | explicit pass/fail answers to fresh-session questions |

## Harness Principles

- Write durable repo-local facts, not chat-only explanations.
- Prefer `.harness/` for operational docs and generated reports.
- Keep root agent files short and routing-oriented.
- Treat unknowns as readiness failures until explicitly resolved.
- Never hide secret values in generated artifacts.
- Promote repeated failures into checks or runbooks.
