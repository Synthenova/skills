---
name: chatgpt-api
description: Reverse-engineered ChatGPT web backend (`chatgpt.com/backend-api`) for sending prompts, uploading local files, attaching images, reference-image generation, and image-edit flows. Use when Codex needs the exact request bodies, endpoint sequence, or browser-driven automation for an already authenticated ChatGPT session, including future agents that must chat or generate images through ChatGPT without rediscovering the upload and `f/conversation` schema.
---

# Chatgpt Api

## Overview

Use this skill to operate against the authenticated ChatGPT web app backend, not the public OpenAI API. Prefer this skill when a task specifically depends on `chatgpt.com` web behavior, existing ChatGPT browser auth, hidden upload controls, or the exact `backend-api/f/conversation` payload shape.

The safest execution mode is browser-first: run requests from an already logged-in ChatGPT tab with `agent-browser` or equivalent browser automation. Direct HTTP replay is possible only when you already have the browser-derived auth/session material and you accept that the web app's auth layer may change.

## Quick Start

1. Reuse an authenticated ChatGPT browser session.
2. For uploads, use the hidden file input `#upload-photos` for images or `#upload-files` for general files.
3. Build the `f/conversation` payload with `scripts/build_conversation_payload.py` when you need a raw JSON body.
4. Send the request to `https://chatgpt.com/backend-api/f/conversation`.
5. Poll `conversation/{chat_id}/stream_status` for normal text/reference-image generation flows.
6. Poll `conversation/{chat_id}/async-status` for some longer-running image edit flows.
7. Fetch rendered files with `/backend-api/files/download/{file_id}` or signed `/backend-api/estuary/content?...`.

## Browser-First Workflow

Use this workflow when you want the least fragile path.

1. Attach to an already logged-in browser, for example with `agent-browser --cdp 9222`.
2. Open or stay on `https://chatgpt.com/`.
3. Upload the local image through `#upload-photos`.
4. Wait until ChatGPT shows the image chip in the composer.
5. Send the prompt through the composer or by issuing an in-page `fetch` from the authenticated tab.
6. Inspect request details from browser network logs or by patching `window.fetch`/`XMLHttpRequest` in the page before sending.

Use this mode for:

- Plain chat through ChatGPT web
- Upload + ask
- Upload + edit image
- Upload + use-as-reference generation
- Fetching generated image file IDs from the conversation lifecycle

## Confirmed Schemas

For an uploaded image plus prompt, the confirmed request shape is:

```json
{
  "action": "next",
  "messages": [
    {
      "author": { "role": "user" },
      "content": {
        "content_type": "multimodal_text",
        "parts": [
          {
            "content_type": "image_asset_pointer",
            "asset_pointer": "sediment://file_<id>",
            "size_bytes": 52866,
            "width": 1914,
            "height": 1012
          },
          "Use this uploaded image as a reference and generate a high-contrast editorial poster version."
        ]
      },
      "metadata": {
        "attachments": [
          {
            "id": "file_<id>",
            "size": 52866,
            "name": "upload-valid.png",
            "mime_type": "image/png",
            "width": 1914,
            "height": 1012,
            "source": "local",
            "is_big_paste": false
          }
        ]
      }
    }
  ]
}
```

Key points:

- `content.parts[0]` is the uploaded image pointer.
- `content.parts[1]` is the human prompt text.
- `metadata.attachments` duplicates the file metadata ChatGPT needs around the same uploaded file.
- The image pointer scheme is `sediment://file_<id>`.

For the full captured body and endpoint notes, read:

- `references/request-bodies.md`
- `references/endpoints.md`

## Payload Builder

Use `scripts/build_conversation_payload.py` to generate a replayable payload skeleton.

Examples:

```bash
python scripts/build_conversation_payload.py \
  --prompt "Use this uploaded image as a reference and generate a stylized poster version." \
  --file-id file_000000003980720bb63e604b34691383 \
  --file-name upload-valid.png \
  --mime-type image/png \
  --file-size 52866 \
  --width 1914 \
  --height 1012
```

```bash
python scripts/build_conversation_payload.py \
  --prompt "Reply with exactly OK." \
  --content-type text
```

Notes:

- The attached-image shape is confirmed.
- The plain-text `content_type: "text"` path is included for convenience; if the live web app rejects it, capture a fresh browser-originated text send and mirror that shape.

## Upload Sequence

For local image uploads, the confirmed sequence is:

1. `POST /backend-api/files`
2. `PUT https://sdmntpr...oaiusercontent.com/files/.../raw?...`
3. `GET /backend-api/files/process_upload_stream`
4. `GET /backend-api/files/download/file_<id>`
5. `GET /backend-api/estuary/content?id=file_<id>...`

ChatGPT also uses `POST /backend-api/files/library` when the attachment menu opens.

## Response Handling

Use these rules:

- Plain text send or reference-image generation: watch `GET /backend-api/conversation/{chat_id}/stream_status`
- Some image edit flows: watch `POST /backend-api/conversation/{chat_id}/async-status`
- Generated image retrieval: watch for new `file_<id>` values, then fetch `/backend-api/files/download/{file_id}` and `/backend-api/estuary/content?...`

## Guardrails

- Re-snapshot after every DOM-changing browser action.
- Prefer in-page authenticated requests over external `curl` unless the user explicitly wants raw replay.
- Expect ChatGPT web auth and sentinel requirements to evolve.
- Treat signed `oaiusercontent.com` upload URLs as one-time upload targets, not stable API endpoints.
- If a file uploads successfully but ChatGPT says the image is unsupported, retry with a conventional PNG, JPEG, or WebP file.
