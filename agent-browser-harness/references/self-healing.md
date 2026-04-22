# Self-Healing Browser Workflow

Use this loop whenever browser automation is not trivially linear.

## Core Loop

1. Inspect the current state.
2. Choose the simplest viable action.
3. Verify the result immediately.
4. Classify the failure if verification fails.
5. Recover with the next tactic.
6. Re-check whether browser automation is still the right path.

## Inspect First

Start with whichever signal is cheapest and most trustworthy for the current page:

```bash
agent-browser snapshot -i
agent-browser get url
agent-browser get title
agent-browser screenshot /tmp/current.png
```

Use:
- `snapshot -i` to find actionable refs
- `snapshot` to read broader structure
- `screenshot` when layout, overlays, or visual blockers matter
- `network requests` when DOM state is ambiguous

## Action Order

Default action order:

1. Ref-based interaction from `snapshot -i`
2. Semantic `find ...`
3. `scrollintoview`
4. `frame ...` if the target lives in an iframe
5. `eval ...` only when the DOM state must be inspected or a stable value must be read
6. `mouse ...` only when the control is visually present but standard interaction is failing

Avoid jumping straight to JavaScript mutation or brittle selector guessing.

## Verify Every Meaningful Action

After clicking, typing, selecting, uploading, scheduling, or submitting, verify with at least one of:

- `agent-browser snapshot -i`
- `agent-browser get url`
- `agent-browser get title`
- `agent-browser get text ...`
- `agent-browser screenshot ...`
- `agent-browser network requests`
- `agent-browser dialog status`

Do not chain multiple unverified actions through a fragile UI state.

## Failure Classes

### Agent Browser is completely wedged

Symptoms:
- `agent-browser` commands hang with no output
- `get url`, `tab list`, `snapshot`, and `screenshot` all stall
- one stuck command causes later commands to stall too
- the browser window may still be visibly alive even though the CLI is not

Recovery:

1. Kill only the stuck `agent-browser` client commands first.
2. If new commands are still blocked, restart the `agent-browser` daemon.
3. Preserve the browser process if the page state matters.
4. Reconnect and verify the session before resuming the workflow.

Preferred recovery sequence:

```bash
pkill -f '/usr/lib/node_modules/agent-browser/bin/agent-browser-linux-x64' || true
agent-browser session
agent-browser tab list
agent-browser get url
```

If the browser process is still alive, this often restores control without losing the page state.

If the daemon restart comes back on a blank tab, assume you lost the daemon session, not necessarily the browser process. Re-open the target page or recover via the site's draft/continue flow.

If you need to confirm whether the underlying Chrome process survived:

```bash
ps -ef | rg '/chrome --remote-debugging-port=0'
```

If the browser process is gone too, relaunch the configured `agent-browser` profile cleanly and resume from the last durable checkpoint.

Rules:
- Do not keep stacking new `agent-browser` commands on top of a known hung session.
- Kill the stuck client processes before deciding the whole browser is dead.
- Prefer preserving the browser window when the page contains a draft, upload, or partially completed editor state.
- After recovery, treat the session as freshly attached: re-check tabs, URL, and refs.
- In this setup, if the CLI is wedged, assume raw CDP is likely wedged too. Do not burn time on CDP fallback probing; restart the configured session cleanly instead.

### Refs went stale

Symptoms:
- `@eN` no longer exists
- click targets the wrong thing
- the page changed after an earlier action

Recovery:

```bash
agent-browser snapshot -i
```

Always get fresh refs after navigation, modal open/close, dropdown expansion, tab switch, major rerender, or submit.

### Wrong tab or wrong visible page

Symptoms:
- URL/title does not match what the user sees
- commands work but Chrome is visibly on another tab
- screenshots show a different page than expected

Recovery:
- read [../interaction-skills/tabs.md](../interaction-skills/tabs.md)
- use `agent-browser tab`
- switch tabs, then re-check URL/title/screenshot

### Iframe or embedded context

Symptoms:
- target is visible but missing from top-level refs
- payment/editor/widget UI appears embedded
- interaction works on parent page but not the target control

Recovery:
- read [../interaction-skills/iframes.md](../interaction-skills/iframes.md)
- re-snapshot first because `agent-browser` may already inline iframe refs
- use `frame ...` only when necessary

### Hidden, covered, or offscreen target

Symptoms:
- ref exists but click has no effect
- sticky headers, drawers, or modals cover the element
- wrong scroll container consumed input

Recovery:
- read [../interaction-skills/scrolling.md](../interaction-skills/scrolling.md)
- use `scrollintoview`
- take a screenshot
- re-measure with a new snapshot after opening overlays

### Async state has not settled

Symptoms:
- submit button exists but result state has not appeared
- SPA updates happen after the click with no navigation
- upload processing or schedule controls lag behind the file attach

Recovery:

```bash
agent-browser wait 1000
agent-browser wait --load networkidle
agent-browser network requests
agent-browser snapshot -i
```

Prefer waiting on a concrete URL, text, or load condition instead of arbitrary long sleeps.

### Dialog interrupted the flow

Symptoms:
- page stops responding
- navigation hangs
- beforeunload blocks leaving an editor or upload page

Recovery:
- read [../interaction-skills/dialogs.md](../interaction-skills/dialogs.md)
- use `agent-browser dialog status`
- accept or dismiss explicitly

### Browser is unnecessary

Symptoms:
- the domain reference exposes a stable API or HTTP path
- DOM interaction is slower and less reliable than direct retrieval

Recovery:
- switch to the domain's non-browser path
- keep the browser only if login state or JS execution is actually required

### Auth wall or human checkpoint

Symptoms:
- login redirect
- OTP, captcha, passkey, or approval prompt

Recovery:
- stop and ask the user
- do not fabricate credentials or pretend the checkpoint succeeded

## Durable Habits

- Re-snapshot after any UI state change.
- Prefer `find role`, `find text`, `find label`, and refs over opaque selectors.
- Use screenshots to notice blockers earlier.
- Verify the post-action state, not just the action call.
- If a tactic fails twice for the same reason, change tactic instead of repeating it.
