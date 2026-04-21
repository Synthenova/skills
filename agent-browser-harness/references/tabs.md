# Tabs

Use this reference when the session is attached to the wrong page, the visible Chrome tab does not match the controlled page, or new tabs open during the flow.

## First Checks

```bash
agent-browser tab
agent-browser get url
agent-browser get title
agent-browser screenshot /tmp/tab-check.png
```

`agent-browser` can control a tab that is not the one the user expects. Always verify both tab listing and current page state.

## Common Recovery

```bash
agent-browser tab
agent-browser tab 2
agent-browser wait 500
agent-browser get url
agent-browser screenshot /tmp/tab-2.png
```

Use tab indices only after confirming the list output. Re-snapshot after switching:

```bash
agent-browser snapshot -i
```

## New Tabs

If an action opens a new tab:

1. List tabs again.
2. Switch to the new tab.
3. Verify URL/title.
4. Re-snapshot for new refs.

## Rules That Hold Up

- Treat every tab switch as a ref invalidation boundary.
- If the user means visible order, do not assume automation order and human-visible order are identical.
- If screenshots show the wrong page, switch tabs first and debug selectors second.
