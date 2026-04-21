# Network Requests

Use this reference when page state is ambiguous after submit, upload, scheduling, save, or SPA actions.

## Core Pattern

```bash
agent-browser network requests --clear
# perform the action
agent-browser network requests
```

Use network activity to answer:
- did the submit actually fire?
- did an upload request begin?
- did the page save silently without navigation?
- is the UI still waiting on backend processing?

## When To Reach For It

- button click has no obvious visible effect
- the page uses SPA mutations instead of full loads
- success state is delayed or hidden behind background processing
- you need to distinguish "click failed" from "request sent but UI lagged"

## Verification Strategy

Combine network checks with one visible check:

```bash
agent-browser screenshot /tmp/post-submit.png
agent-browser get url
agent-browser snapshot -i
agent-browser network requests
```

Do not infer success from network alone if the user-facing state matters.
