# 2Captcha Reference

Sources:
- https://2captcha.com/api-docs
- https://2captcha.com/api-docs/create-task
- https://2captcha.com/api-docs/get-task-result
- https://2captcha.com/api-docs/recaptcha-v2
- https://2captcha.com/api-docs/recaptcha-v3
- https://2captcha.com/api-docs/cloudflare-turnstile
- Demo pages inspected on April 21, 2026:
  - https://2captcha.com/demo/recaptcha-v2
  - https://2captcha.com/demo/recaptcha-v3
  - https://2captcha.com/demo/cloudflare-turnstile
- Live-verified solve results from April 21, 2026 (TWOCAPTCHA_API_KEY balance $14.04)

Base API:
- `POST https://api.2captcha.com/createTask`
- `POST https://api.2captcha.com/getTaskResult`

Auth:
- JSON field: `clientKey: process.env.TWOCAPTCHA_API_KEY`

Polling:
- Submit a task with `createTask`.
- Poll `getTaskResult` with the returned `taskId`.
- When status is `processing`, wait at least 5 seconds before polling again.

## Common Request Shell

Create task:
```json
{
  "clientKey": "TWOCAPTCHA_API_KEY",
  "task": {}
}
```

Poll result:
```json
{
  "clientKey": "TWOCAPTCHA_API_KEY",
  "taskId": 123456789
}
```

Ready result shape (verified live):
```json
{
  "errorId": 0,
  "status": "ready",
  "solution": { /* see per-type below */ },
  "cost": "0.00299",
  "ip": "72.61.251.227",
  "createTime": 1776787314,
  "endTime": 1776787367,
  "solveCount": 2
}
```

Metadata fields (present on all responses):
- `cost`: price per solve in USD (v2/v3 ~$0.003, Turnstile ~$0.0015)
- `createTime` / `endTime`: unix timestamps for timing diagnostics
- `solveCount`: number of worker attempts (v2 often needs 2)
- `ip`: solver worker IP

## Detection Heuristics

Use this order:

1. Check for Turnstile first:
   `.cf-turnstile`, `turnstile.render(`, `name="cf-turnstile-response"`, or iframes/scripts on `challenges.cloudflare.com`.
2. Then check for reCAPTCHA v3:
   `grecaptcha.execute(` or `grecaptcha.enterprise.execute(`, plus an action passed in code. Usually no visible checkbox widget.
3. Then check for reCAPTCHA v2:
   `.g-recaptcha`, visible checkbox/challenge iframe, or a `data-sitekey` attached to a rendered widget.

Fallback hints:

- `enterprise.js` or `grecaptcha.enterprise.execute` implies Enterprise.
- `data-size="invisible"` or an invisible callback flow implies invisible v2.
- If both `g-recaptcha-response` and `cf-turnstile-response` exist, prefer Turnstile if `.cf-turnstile` or `turnstile.render` is present.

## Testing-Ground Fingerprints

These values were extracted from the official 2Captcha demo pages and are useful as known-good examples.

### reCAPTCHA v2 demo

Page:
- `https://2captcha.com/demo/recaptcha-v2`

Observed markers:
- `div.g-recaptcha`
- `data-sitekey="6LfD3PIbAAAAAJs_eEHvoOl75_83eXSqpPSRFJ_u"`
- Visible checkbox/widget flow

Minimal task:
```json
{
  "type": "RecaptchaV2TaskProxyless",
  "websiteURL": "https://2captcha.com/demo/recaptcha-v2",
  "websiteKey": "6LfD3PIbAAAAAJs_eEHvoOl75_83eXSqpPSRFJ_u"
}
```

Detection hint:
- If you can locate a visible widget container with `data-sitekey` and there is no `grecaptcha.execute(...)` action flow, assume reCAPTCHA v2.

## reCAPTCHA v2

Task types:
- `RecaptchaV2TaskProxyless`
- `RecaptchaV2Task`

Required fields:
```json
{
  "type": "RecaptchaV2TaskProxyless",
  "websiteURL": "https://target.example",
  "websiteKey": "sitekey"
}
```

Optional fields:
- `recaptchaDataSValue`
- `isInvisible`
- `userAgent`
- `cookies`
- `apiDomain`

Proxy variant extra fields:
- `proxyType`
- `proxyAddress`
- `proxyPort`
- `proxyLogin`
- `proxyPassword`

Solution fields (verified live):
```json
{
  "gRecaptchaResponse": "token",
  "token": "identical-copy-of-gRecaptchaResponse",
  "cookies": "optional-cookie-string"
}
```

Live observations:
- `gRecaptchaResponse` and `token` are always identical; use either.
- `cookies` is returned for v2 but not always for v3.
- Token length ~1166 chars. Solve time ~53s, solveCount often 2.

Use:
- Set `g-recaptcha-response` to the token or pass it into the page callback.

Demo-ground note:
- On the 2Captcha demo page, the sitekey is `6LfD3PIbAAAAAJs_eEHvoOl75_83eXSqpPSRFJ_u`.

## reCAPTCHA v3

### Demo fingerprint

Page:
- `https://2captcha.com/demo/recaptcha-v3`

Observed markers:
- `grecaptcha.ready(function() { ... })`
- `grecaptcha.execute('6LfB5_IbAAAAAMCtsjEHEHKqcB9iQocwwxTiihJu', { action: 'demo_action' })`
- callback handoff through `window.verifyRecaptcha(token)`
- recommended score in the demo docs: `0.9`

Detection hint:
- Search page source and bundled JS for `grecaptcha.execute(`. Extract:
  - first argument: sitekey
  - `action` object property: page action
  - token consumer in `.then(...)`: callback or submission path

Task type:
- `RecaptchaV3TaskProxyless`

Required fields:
```json
{
  "type": "RecaptchaV3TaskProxyless",
  "websiteURL": "https://target.example",
  "websiteKey": "sitekey",
  "minScore": 0.9
}
```

Optional fields:
- `pageAction`
- `isEnterprise`
- `apiDomain`

Solution fields (verified live):
```json
{
  "gRecaptchaResponse": "token",
  "token": "identical-copy-of-gRecaptchaResponse"
}
```

Live observations:
- `gRecaptchaResponse` and `token` are always identical.
- Token length ~1060 chars. Solve time ~6s, solveCount 1.

Use:
- Inject token into `g-recaptcha-response` or pass to the callback used by the target page.

Demo-ground note:
- The 2Captcha demo page uses:
  - `websiteKey = 6LfB5_IbAAAAAMCtsjEHEHKqcB9iQocwwxTiihJu`
  - `pageAction = demo_action`
  - `minScore = 0.9`
  - token handler pattern: `window.verifyRecaptcha(token)`

## Cloudflare Turnstile

Task types:
- `TurnstileTaskProxyless`
- `TurnstileTask`

### Demo fingerprint

Page:
- `https://2captcha.com/demo/cloudflare-turnstile`

Observed markers:
- `div.cf-turnstile`
- `data-sitekey="3x00000000000000000000FF"`
- token sink is `name="cf-turnstile-response"`
- docs also mention compatibility with `g-recaptcha-response`

Detection hint:
- If `.cf-turnstile` exists, or the page uses `turnstile.render(...)`, classify as Turnstile even if there is also a `g-recaptcha-response` field for compatibility.

### Standalone widget

Required fields:
```json
{
  "type": "TurnstileTaskProxyless",
  "websiteURL": "https://target.example",
  "websiteKey": "sitekey"
}
```

Use:
- Insert the token into `cf-turnstile-response` or `g-recaptcha-response`, or invoke the widget callback.

Demo-ground note:
- The 2Captcha demo page uses:
  - `websiteKey = 3x00000000000000000000FF`
  - token field: `cf-turnstile-response`

### Cloudflare challenge page

The docs require intercepting `turnstile.render` before the widget loads and extracting:
- `cData`
- `chlPageData`
- `action`
- callback handle
- current page user agent

The 2Captcha docs provide this interception pattern:
```js
const i = setInterval(() => {
  if (window.turnstile) {
    clearInterval(i);
    window.turnstile.render = (a, b) => {
      const p = {
        type: "TurnstileTaskProxyless",
        websiteKey: b.sitekey,
        websiteURL: window.location.href,
        data: b.cData,
        pagedata: b.chlPageData,
        action: b.action,
        userAgent: navigator.userAgent
      };
      console.log(JSON.stringify(p));
      window.tsCallback = b.callback;
      return "foo";
    };
  }
}, 10);
```

Challenge-page task body:
```json
{
  "type": "TurnstileTaskProxyless",
  "websiteURL": "https://target.example",
  "websiteKey": "sitekey",
  "action": "managed",
  "data": "cData value",
  "pagedata": "chlPageData value",
  "userAgent": "browser UA"
}
```

Solution fields (verified live):
```json
{
  "token": "turnstile-token",
  "userAgent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/145.0.0.0 Safari/537.36"
}
```

Live observations:
- NO `gRecaptchaResponse` field — only `token` and `userAgent`.
- Test sitekey `3x00000000000000000000FF` returns dummy token `XXXX.DUMMY.TOKEN.XXXX`. This is expected — real sitekeys return real tokens.
- Solve time ~6s, cost $0.00145.
- The returned `userAgent` is the worker's browser UA. If the target page checks UA consistency, override the browser UA to match.

Use:
- For standalone widgets, inject the token into the expected field or callback.
- For challenge pages, call the intercepted callback with the returned token and align the browser user agent with the one returned by 2Captcha when required by the page flow.

## Error Handling

- `errorId: 0` means the request itself succeeded.
- `status: processing` means keep polling.
- Errors such as `ERROR_CAPTCHA_UNSOLVABLE` should be surfaced to the caller with context.

## Practical Integration Notes

- Prefer proxyless tasks first unless the target explicitly requires IP matching.
- reCAPTCHA v2 on Google properties may require `recaptchaDataSValue`, cookies, and a matching user agent.
- reCAPTCHA v3 quality depends on the correct `minScore` and `pageAction`; extract both from the target if possible.

## Live Test Summary (April 21, 2026)

All three captcha types were submitted and solved against the 2Captcha demo pages:

| Type | Task ID | Solve Time | Cost | Token Len | solveCount |
|------|---------|-----------|------|-----------|------------|
| reCAPTCHA v2 | 82483492103 | ~53s | $0.00299 | 1166 | 2 |
| reCAPTCHA v3 | 82483498162 | ~6s | $0.00299 | 1060 | 1 |
| Turnstile | 82483500080 | ~6s | $0.00145 | 21 (dummy) | 1 |

Key takeaways:
- v2 is the slowest (often needs 2 attempts). Budget ~60s polling timeout.
- v3 and Turnstile solve in one pass (~6s). Budget ~20s.
- Turnstile test sitekey `3x00000000000000000000FF` returns a dummy token. Real sitekeys return real tokens.
- Always use the `token` field from `solution` — for reCAPTCHA it equals `gRecaptchaResponse`.
