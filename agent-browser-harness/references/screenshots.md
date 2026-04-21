# Screenshots

Use screenshots both for discovery and for verification.

## Discovery

When layout, overlays, geometry, or visual blockers matter:

```bash
agent-browser screenshot /tmp/discovery.png
```

Use the image to answer:
- is the control actually visible?
- is it covered by a modal, sticky header, or tooltip?
- did a new panel or picker open?
- is the page in the expected state at all?

## Verification

After every meaningful action, use a screenshot if textual checks are insufficient:

```bash
agent-browser screenshot /tmp/after-action.png
```

This is especially useful for:
- uploads
- media scheduling
- dropdowns and date/time pickers
- tab switches
- error banners and disabled buttons

## Rules That Hold Up

- Take the screenshot after the action and after a short settle period if the UI animates.
- Use screenshots early, not only after the flow is already lost.
- Pair screenshots with `snapshot -i` when you need both visual truth and refs.
