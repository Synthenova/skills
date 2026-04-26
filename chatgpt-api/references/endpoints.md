# ChatGPT web backend endpoints

## Preferred mode

Run requests from an authenticated ChatGPT browser tab whenever possible. Browser-originated `fetch` calls are less fragile than external replay because the page already holds the active auth/session state and any sentinel/client requirements.

## Attachment controls

The web app exposes hidden file inputs:

- `#upload-photos` for image uploads
- `#upload-files` for general file uploads
- `#upload-camera` for camera capture on supported devices

## Upload sequence

Confirmed upload flow for a local image:

1. `POST https://chatgpt.com/backend-api/files/library`
2. `POST https://chatgpt.com/backend-api/files`
3. `PUT https://sdmntpr...oaiusercontent.com/files/<uuid>/raw?...`
4. `GET https://chatgpt.com/backend-api/files/process_upload_stream`
5. `GET https://chatgpt.com/backend-api/files/download/file_<id>`
6. `GET https://chatgpt.com/backend-api/estuary/content?id=file_<id>...`

Notes:

- The signed `oaiusercontent.com` URL is an upload target returned by ChatGPT, not a reusable API contract.
- The stable object identifier for downstream prompts is the resulting `file_<id>`.

## Send prompt

Primary send endpoint:

- `POST https://chatgpt.com/backend-api/f/conversation`

Preparation endpoint seen immediately before sends:

- `GET https://chatgpt.com/backend-api/f/conversation/prepare`

Safety/session traffic commonly adjacent to sends:

- `POST /backend-api/sentinel/chat-requirements/prepare`
- `POST /backend-api/sentinel/chat-requirements/finalize`
- `POST /backend-api/sentinel/ping`
- `POST /backend-api/sentinel/req`

## Response status

Use these status endpoints:

- `GET /backend-api/conversation/{chat_id}/stream_status`
  - Plain text chat
  - Upload + ask
  - Upload + reference-image generation
  - Some image generation flows

- `POST /backend-api/conversation/{chat_id}/async-status`
  - Seen in some longer-running image edit flows

## Generated files

Generated or uploaded file retrieval endpoints:

- `GET /backend-api/files/download/file_<id>`
- `GET /backend-api/files/download/file_<id>?post_id=&inline=false`
- `GET /backend-api/estuary/content?id=file_<id>&...`

## Conversation IDs observed during capture

These were captured live and are useful examples only:

- Text chat: `69ee9525-38b0-83a8-bfbe-db1998f0672b`
- Upload + edit intent: `69ee98a6-b590-83a5-af82-1a8f8910845b`
- Upload + reference-generation intent: `69ee98db-5fa4-83a7-b666-1a720c7fb966`
