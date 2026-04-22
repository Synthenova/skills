# Iframes

Use this reference when the target UI is embedded inside an iframe or when controls are visible but missing from the top-level page refs.

## Start With a Fresh Snapshot

`agent-browser` can inline iframe content in snapshots. Do this before switching frame context:

```bash
agent-browser snapshot -i
```

If the target appears as a normal `@eN` ref under an iframe node, interact with that ref directly first.

## When To Switch Frame Context

Use `frame ...` only when:
- the target is not exposed in the top-level snapshot
- the page has multiple embedded browsing contexts and you need a scoped snapshot
- repeated top-level interaction is hitting the wrong embedded surface

Examples:

```bash
agent-browser frame @e3
agent-browser snapshot -i
agent-browser frame main
```

## Cross-Origin Friction

If the widget is clearly present but frame-local discovery is inconsistent:
- use screenshots to confirm what is visibly present
- re-snapshot after the embedded UI fully loads
- prefer stable visible refs and scoped frame snapshots over brittle deep selectors

## Rules That Hold Up

- Re-snapshot after switching into or out of a frame.
- Treat iframe interactions like a separate page state.
- Debug frame ownership before debugging the control itself.
