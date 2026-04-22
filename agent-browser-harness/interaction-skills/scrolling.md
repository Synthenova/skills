# Scrolling

Use this reference when content is offscreen, inside a nested scroller, or inside a virtualized list or picker.

## Start Simple

```bash
agent-browser scrollintoview @e5
agent-browser snapshot -i
agent-browser screenshot /tmp/after-scroll.png
```

## When Page Scroll Is Not The Right Scroll

Symptoms:
- page scrolls but the target list does not move
- dropdown or time picker remains unchanged
- wheel input is consumed by a nested container

Recovery:
- click or focus the container first
- use `mouse wheel` while the pointer is over the actual scroller
- re-check the visible options after each movement

Example:

```bash
agent-browser mouse move 400 500
agent-browser mouse wheel 160
agent-browser screenshot /tmp/wheel.png
```

## Rules That Hold Up

- Re-measure after opening dropdowns, modals, or pickers.
- Virtualized controls often need repeated small wheel steps, not one large scroll.
- Do not assume the page itself owns the scroll just because the viewport moved.
