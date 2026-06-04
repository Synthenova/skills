# Artifact Contract

The bootstrap scanner creates a `.harness/` operating surface for agents.

## Primary Files

- `INDEX.md`: entrypoint and routing map for agents.
- `READINESS.md`: current status, ready gates, failed gates, next actions.
- `FRESH_SESSION_TEST.md`: questions a cold agent must answer.
- `ENVIRONMENT.md`: runtime versions, install/start commands, env vars.
- `TOOLING.md`: CLIs, MCPs, skills, package managers.
- `TESTING.md`: test/check/build commands and baseline status.
- `DEPLOYMENT.md`: CI/CD, hosting, release commands, deployment unknowns.
- `OBSERVABILITY.md`: logs, telemetry, metrics, traces, error reporting.
- `DESIGN_LANGUAGE.md`: frontend stack, UI libraries, design system clues.
- `SECURITY.md`: secret handling, auth/security config clues.
- `QUALITY.md`: quality risks, stale docs, weak gates.
- `KNOWLEDGE.md`: repo-map and Understand Anything graph status.
- `RUNBOOKS.md`: local dev, debugging, release, incident paths.

## Generated Files

- `generated/repo-map.md`: deterministic file and stack map.
- `generated/env-scan.md`: env var names and references only.
- `generated/test-scan.md`: scripts and test framework evidence.
- `generated/ci-cd-scan.md`: CI/CD and deployment files.
- `generated/observability-scan.md`: logging and telemetry clues.
- `generated/readiness-report.json`: machine-readable gate report.

## State Files

- `state/questions.md`: unresolved questions for the user.
- `state/validation-history.md`: append-only readiness scan history.

Generated files may be replaced by the scanner. Human-curated sections should be edited after generated summaries or in the primary files.
