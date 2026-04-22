# Dialogs

Browser dialogs can block progress even when the DOM looks unchanged.

Use this reference for:
- `alert`
- `confirm`
- `prompt`
- `beforeunload`

## Detect First

```bash
agent-browser dialog status
```

Also suspect a dialog when:
- a navigation hangs unexpectedly
- the page stops responding after submit or leave-page actions
- screenshots stop changing while the workflow should have progressed

## Default Recovery

Use explicit dialog handling instead of guessing:

```bash
agent-browser dialog accept
agent-browser dialog dismiss
```

Use `accept` when leaving a page is intended. Use `dismiss` when preserving unsaved state is intended.

## beforeunload

Common on editors, upload flows, and schedule forms.

Typical sequence:

```bash
agent-browser open https://example.com/next-page
agent-browser dialog status
agent-browser dialog accept
agent-browser wait --load networkidle
```

If the dialog appears repeatedly, verify that the original page state actually changed and that a background upload or draft-save flow is not still running.

## Verification

After handling the dialog, verify with:
- `agent-browser get url`
- `agent-browser screenshot /tmp/post-dialog.png`
- `agent-browser snapshot -i`
