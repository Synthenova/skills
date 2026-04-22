# SadCaptcha Reference

Source:
- https://www.sadcaptcha.com/api/v1/swagger-ui/index.html
- OpenAPI discovered at `https://www.sadcaptcha.com/api/v1/v3/api-docs`
- API version: 1.1.0 (verified April 21, 2026)

Base URL:
- `https://www.sadcaptcha.com/api/v1`

Auth:
- Query parameter: `licenseKey=$SADCAPTCHA_API_KEY`

General rules:
- Request bodies are JSON.
- Images are sent as base64-encoded strings. Either download from the `<img>` `src` URL and encode, or extract the base64 payload from `data:` URIs directly.
- SadCaptcha returns ratios or angles instead of device-specific pixels.
- If images come as `data:image/webp;base64,...` data URIs (common on TikTok), strip the prefix and send the raw base64 part.

## TikTok CSS Selectors (for extracting images from the DOM)

These selectors are documented by SadCaptcha and used in their Python client:
- `.captcha-verify-image` — the main captcha puzzle/image element
- `.captcha_verify_slide--slidebar` — the slider bar for puzzle/rotate
- `.secsdk-captcha-drag-icon` — the draggable icon on the slider

## TikTok Puzzle

Endpoint:
- `POST /puzzle?licenseKey=...`

Request body:
```json
{
  "puzzleImageB64": "<base64>",
  "pieceImageB64": "<base64>"
}
```

Response:
```json
{
  "slideXProportion": 0.42
}
```

Use:
- `distance = slideXProportion * puzzleImageWidth`
- Where `puzzleImageWidth` is the width of the `.captcha-verify-image` element.

## TikTok Rotate

**This is the most common TikTok captcha type.** Even when the page text says "Drag the puzzle piece", if there are two overlaid images (outer background + inner rotatable circle), use the rotate endpoint, NOT puzzle.

Live-verified April 22, 2026:
- Solved successfully against live TikTok captcha on the Penny profile
- The page text read "Drag the puzzle piece into place" but the captcha was actually a rotate type
- Puzzle endpoint returned constant 0.196 (wrong), rotate endpoint returned correct angles

Endpoint:
- `POST /rotate?licenseKey=...`

Request body:
```json
{
  "outerImageB64": "<base64>",
  "innerImageB64": "<base64>"
}
```

Where:
- `outerImageB64` = the larger background image (210x210 rendered, ~347px natural)
- `innerImageB64` = the smaller overlaid circle image (128x128 rendered, ~211px natural)

Response:
```json
{
  "angle": 312.0
}
```

Distance formula (verified live):
```
distance = ((trackWidth - dragWidth) * angle) / 360
```

Where:
- `trackWidth` = width of the slider track container (class `cap-w-full cap-h-40 cap-rounded-full cap-bg-UISheetGrouped3`), typically 348px
- `dragWidth` = width of the drag handle (class `secsdk-captcha-drag-icon`), typically 64px
- `angle` = the angle returned by SadCaptcha

Live test results:
| Angle | Distance | TrackW | DragW | Result |
|-------|----------|--------|-------|--------|
| 312.0 | 246px | 348 | 64 | User confirmed correct position |
| 142.0 | 112px | 348 | 64 | Captcha solved successfully |

Drag implementation:
- Use CDP mouse events via agent-browser batch command
- ~15-20 steps with 20-35ms waits between steps for smooth human-like motion
- Hold mouse down during entire drag, only release at final position
- Do NOT use synthetic JS events — TikTok doesn't register them

Use:
- `distance = ((slideBarLength - dragIconLength) * angle) / 360`
- Where `slideBarLength` = width of `.captcha_verify_slide--slidebar`, `dragIconLength` = width of `.secsdk-captcha-drag-icon`.

## TikTok 3D Shapes

Endpoint:
- `POST /shapes?licenseKey=...`

Request body:
```json
{
  "imageB64": "<base64>"
}
```

Note: The OpenAPI schema defines `image_b64` (snake_case) but the documented Python example uses `imageB64` (camelCase). The API accepts **both** — use whichever matches your convention.

Response:
```json
{
  "pointOneProportionX": 0.25,
  "pointOneProportionY": 0.35,
  "pointTwoProportionX": 0.68,
  "pointTwoProportionY": 0.54
}
```

Use:
- `x = proportionX * imageWidth`, `y = proportionY * imageWidth`
- Both axes use image **width** for scaling (documented convention).
- Click both points on the image.

## TikTok Icon / Video Upload

Endpoint:
- `POST /icon?licenseKey=...`

Request body:
```json
{
  "challenge": "Which of these objects has a brim?",
  "imageB64": "<base64>"
}
```

Response:
```json
{
  "proportionalPoints": [
    { "proportionX": 0.31, "proportionY": 0.47 }
  ]
}
```

Use:
- `x = proportionX * imageWidth`, `y = proportionY * imageWidth`
- Click each returned point.

## Image Semantics (shapes, items, click-in-order)

Endpoint:
- `POST /image-semantics?licenseKey=...`

Description:
- Solves any captcha with a text challenge + image. Includes semantic shapes, items, and "click in order" challenges.
- English only.

Request body:
```json
{
  "challenge": "Please click the unique object.",
  "image_b64": "<base64>"
}
```

Note: This endpoint uses `image_b64` (snake_case) in both schema and example.

Response:
```json
{
  "proportionalPoints": [
    { "proportionX": 0.31, "proportionY": 0.47 }
  ]
}
```

Use:
- `x = proportionX * imageWidth`, `y = proportionY * imageWidth`
- Click each returned point.

## Health / Credits Check

Endpoint:
- `GET /license/credits?licenseKey=...`

Response:
```json
{
  "credits": 25
}
```

## Practical Integration Notes

- TikTok challenge images usually come from `<img>` `src` attributes in the captcha UI. They may be full URLs or `data:` URIs. For data URIs, strip the `data:image/...;base64,` prefix and send the raw base64 payload.
- The solve and browser action need to stay in the same live challenge session. Do not fetch a solve result and wait too long before dragging/clicking. TikTok captchas expire quickly.
- SadCaptcha also offers a Python client (`pip install tiktok-captcha-solver`) and a Chrome extension for non-programmatic use.
- SadCaptcha is only the TikTok/Shopee-side provider in this skill. Do not use it for reCAPTCHA or Turnstile.

