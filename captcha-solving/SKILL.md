---
name: captcha-solving
description: Use when solving or integrating captchas in browser automation or scraping workflows. Covers TikTok captchas via SadCaptcha and reCAPTCHA v2, reCAPTCHA v3, and Cloudflare Turnstile via 2Captcha. Uses SADCAPTCHA_API_KEY and TWOCAPTCHA_API_KEY.
version: 1.0.0
---

# Captcha Solving

Use this skill when the task involves one of these captcha families:

- TikTok captcha: route to SadCaptcha
- reCAPTCHA v2: route to 2Captcha
- reCAPTCHA v3: route to 2Captcha
- Cloudflare Turnstile: route to 2Captcha

## Provider Routing

- SadCaptcha:
  Read [references/sadcaptcha.md](references/sadcaptcha.md) when the captcha is TikTok-native: puzzle, rotate, 3D shapes, icon/video-upload, or image-semantics challenges.
- 2Captcha:
  Read [references/2captcha.md](references/2captcha.md) when the captcha is reCAPTCHA v2, reCAPTCHA v3, or Cloudflare Turnstile.

## Required Env Vars

- `SADCAPTCHA_API_KEY`
- `TWOCAPTCHA_API_KEY`

Never hardcode either key. Read them from the environment and fail clearly if missing.

## Workflow

1. Identify the captcha family from the page or automation context.
2. Extract the required solve inputs before writing code:
   - TikTok puzzle: puzzle image + piece image
   - TikTok rotate: outer ring image + inner image
   - TikTok shapes/icon: challenge image, and text challenge for icon when present
   - TikTok image-semantics: challenge text + image (English only)
   - reCAPTCHA v2: `websiteURL`, `websiteKey`, and optional `data-s`, invisibility, cookies, user agent, proxy
   - reCAPTCHA v3: `websiteURL`, `websiteKey`, `minScore`, optional `pageAction`
   - Turnstile standalone: `websiteURL`, `websiteKey`
   - Turnstile challenge page: `websiteURL`, `websiteKey`, `cData`, `chlPageData`, `action`, page user agent, callback handle
3. Use the matching provider and response format from the relevant reference file.
4. Return or inject the solved token/coordinates in the form the target expects.
5. Add bounded retry and surface provider error codes instead of hiding them.

## Fast Detection

Use these fingerprints before deciding which provider/task type to use:

- reCAPTCHA v2:
  look for `.g-recaptcha`, `iframe[src*="google.com/recaptcha"]`, or any element with `data-sitekey` that is tied to a visible checkbox/challenge widget.
- reCAPTCHA v3:
  look for `grecaptcha.execute(...)`, `grecaptcha.ready(...)`, `g-recaptcha-response`, and an action value passed as `{ action: "..." }`. There is usually no visible checkbox.
- Cloudflare Turnstile:
  look for `.cf-turnstile`, `iframe[src*="challenges.cloudflare.com"]`, `name="cf-turnstile-response"`, or `turnstile.render(...)`.
- TikTok native captcha:
  look for TikTok-specific image/slider challenges rather than token widgets. Key CSS selectors: `.captcha-verify-image` (main image), `.captcha_verify_slide--slidebar` (slider bar), `.secsdk-captcha-drag-icon` (drag handle). These route to SadCaptcha, not 2Captcha.

  **Critical: distinguish the TikTok sub-type before calling the API:**
  - **Rotate** (most common): two overlaid images where the inner image is circular/rotatable. **The page text is misleading** — it may say "Drag the puzzle piece" even for rotate captchas. The key indicator is the image structure (outer bg + inner circle), not the text. Call `/rotate`.
  - **Puzzle**: two images where the second is a **jigsaw-shaped piece** with a visible cutout in the background. Call `/puzzle`.
  - **3D Shapes**: single image with 3D objects to click. Call `/shapes`.
  - **Icon / Video Upload**: image + text challenge ("Which object has a brim?"). Call `/icon`.
  - **Image Semantics**: text challenge + image, "click in order" or "find the unique object". English only. Call `/image-semantics`.
  - **Default to `/rotate` if unsure between rotate vs puzzle** — rotate is far more common on TikTok and the puzzle endpoint returns constant wrong results when given rotate images.

When the target is reCAPTCHA or Turnstile, read [references/2captcha.md](references/2captcha.md) for exact extraction patterns and demo-page fingerprints.

## Implementation Rules

- Prefer direct REST calls unless the repo already uses an official SDK.
- For 2Captcha, submit with `createTask` and poll `getTaskResult` no faster than every 5 seconds.
- For SadCaptcha, send images as base64 strings and include `licenseKey` in the query string.
- Keep provider-specific code isolated so switching services later is easy.
- Log the captcha type and provider, but never log API keys or full solution tokens.

## Output Conventions

- reCAPTCHA v2/v3:
  inject the returned token into `g-recaptcha-response` or pass it to the site callback.
- Turnstile standalone:
  inject the token into `cf-turnstile-response` or `g-recaptcha-response`, or call the widget callback.
- Turnstile challenge page:
  call the intercepted callback with the returned token and use the returned `userAgent` if the provider requires it.
- TikTok SadCaptcha responses:
  convert returned ratios/angles into screen coordinates or slider distances using the formulas in the reference.
