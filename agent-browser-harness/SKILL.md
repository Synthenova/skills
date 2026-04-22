---
name: agent-browser-harness
description: Use agent-browser with browser-harness-style self-healing, interaction recovery, and domain-first browser automation. Trigger this skill when browser work needs durable recovery after failed clicks, ref invalidation, tab or iframe confusion, upload flows, ambiguous submit state, or site-specific tactics such as TikTok Studio publishing. Use it to layer browser-harness operating doctrine and exported domain references on top of the current agent-browser CLI.
---

# Agent Browser Harness

Load the current `agent-browser` skill first, then use this skill for operating doctrine and repo-derived references.

## Quick Start

Before running any browser command, load the current CLI skill:

```bash
agent-browser skills get agent-browser
```

`agent-browser` owns command syntax, flags, refs, sessions, dialogs, frames, screenshots, and browser execution.

This skill owns:
- self-healing workflow
- interaction recovery guidance
- exported domain tactics

## Workflow

1. Load `agent-browser`.
2. Read [references/self-healing.md](references/self-healing.md).
3. If the work is site-specific, check `domain-skills/` first before inventing a new approach.
4. If the work gets stuck on browser mechanics, load the relevant interaction reference.
5. Verify after every meaningful action with `snapshot`, `get ...`, `screenshot`, URL checks, or network checks.

## Interaction Skills

Read these only when the current failure mode matches:

- [interaction-skills/dialogs.md](interaction-skills/dialogs.md) for `alert`, `confirm`, `prompt`, and `beforeunload`
- [interaction-skills/tabs.md](interaction-skills/tabs.md) for wrong-tab, hidden-tab, or tab-order confusion
- [interaction-skills/iframes.md](interaction-skills/iframes.md) for iframe, nested browsing context, or cross-origin widget issues
- [interaction-skills/uploads.md](interaction-skills/uploads.md) for file chooser and upload controls
- [interaction-skills/network-requests.md](interaction-skills/network-requests.md) when submit state is ambiguous
- [interaction-skills/scrolling.md](interaction-skills/scrolling.md) when the wrong scroll container is consuming input
- [interaction-skills/screenshots.md](interaction-skills/screenshots.md) when you need visual discovery or post-action verification

## Domain Skills

- [domain-skills/tiktok/upload.md](domain-skills/tiktok/upload.md) for TikTok Studio upload and scheduling from a local video file
- [domain-skills/instagram/upload.md](domain-skills/instagram/upload.md) for Instagram reel upload from a local video file

## Rules That Hold Up

- Re-snapshot after any UI change that can invalidate refs.
- Prefer the least brittle tactic that can be verified quickly.
- Prefer refs and semantic finders before raw JavaScript.
- Use screenshots to discover and to verify, not just to debug after failure.
- If browser work is proving unnecessary, switch to the site's HTTP or API path when the domain reference says it is safe.
- If you hit an auth wall or human-only checkpoint, stop and ask the user instead of guessing.
