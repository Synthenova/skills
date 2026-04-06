---
name: steel-orchestrator-remote-control
description: Manage Steel profiles over HTTP and attach agent-browser to a running profile WS/CDP endpoint. Use when listing profiles, creating profiles, starting or stopping profiles, retrieving connection info, or controlling a browser running on the Mac from a remote VPS.
---

# Steel Orchestrator Remote Control

Use this skill when a Steel orchestrator is running on the Mac and a remote machine needs to manage profiles or attach browser automation to a running profile.

This skill covers profile lifecycle over HTTP and browser attachment over the profile WebSocket/CDP endpoint. For actual page automation after attaching, continue with the `agent-browser` skill.

Use the injected environment variable `STEEL_ORCHESTRATOR_HOST` for the orchestrator host. Do not hardcode a hostname or IP in examples or commands.

## Profile lifecycle over HTTP

Use the orchestrator API to list, create, start, stop, and inspect profiles.

```bash
curl "http://${STEEL_ORCHESTRATOR_HOST}/profiles"
curl "http://${STEEL_ORCHESTRATOR_HOST}/profiles/<profile-id>"
curl "http://${STEEL_ORCHESTRATOR_HOST}/profiles/<profile-id>/connection"
curl -X POST "http://${STEEL_ORCHESTRATOR_HOST}/profiles/<profile-id>/start"
curl -X POST "http://${STEEL_ORCHESTRATOR_HOST}/profiles/<profile-id>/stop"
```

Treat profile creation, proxy config, and runtime state as HTTP-managed concerns.

## Attach agent-browser to the running profile

When a profile is running, use the `wsEndpoint` from `/connection` and pass it to `agent-browser --cdp`. The agent environment will already have `STEEL_ORCHESTRATOR_HOST` injected, so use that same variable when constructing the WebSocket URL.

```bash
agent-browser --cdp "ws://${STEEL_ORCHESTRATOR_HOST}/profiles/<profile-id>/ws" snapshot
agent-browser --cdp "ws://${STEEL_ORCHESTRATOR_HOST}/profiles/<profile-id>/ws" open https://example.com
agent-browser --cdp "ws://${STEEL_ORCHESTRATOR_HOST}/profiles/<profile-id>/ws" eval 'document.body.innerText'
```

If the profile is already running, reuse its reported `wsEndpoint` instead of starting a second instance.

## Continue browser automation with agent-browser

This skill only handles profile lifecycle and attaching to the browser endpoint.
Once attached, use the `agent-browser` skill for the browser workflow:

- navigation
- clicking
- filling forms
- screenshots
- snapshots
- extraction
