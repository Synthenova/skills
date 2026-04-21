---
name: pinchtab-tiktok-media-extraction
description: Extract and download TikTok video media using the PinchTab HTTP API. Use when you have a PINCHTAB_SERVER_URL and a TikTok URL, and need the exact current video downloaded with PinchTab session data such as cookies, user agent, referer, and profile proxy.
---

# PINCHTAB TikTok Media Extraction

Use this skill when:
- `PINCHTAB_SERVER_URL` points to a running PinchTab server or instance
- `tiktok_url` is a TikTok video URL or a TikTok search/result URL
- you need to download the current TikTok video using PinchTab session state

Available inputs:
- `PINCHTAB_SERVER_URL`
- `tiktok_url`

Required environment:
- `PINCHTAB_TOKEN`

Optional:
- `TAB_ID`
- `OUT`

## Rule

Use PinchTab for all browser-state extraction steps.

That means:
- navigate with PinchTab
- inspect page state with PinchTab
- extract hydration payload with PinchTab
- read cookies with PinchTab
- read profile proxy from PinchTab

The final media file is still downloaded with normal HTTPS, but every prerequisite value comes from PinchTab.

## TikTok-Specific Facts

### 1. The DOM `video` tag is not the download source

TikTok often renders the visible player as a `blob:` URL. Do not use `video.currentSrc` as the download URL.

### 2. The correct source of truth is the hydration payload

Use:

- `#__UNIVERSAL_DATA_FOR_REHYDRATION__`

Preferred extraction path:

- `__DEFAULT_SCOPE__["webapp.video-detail"].itemInfo.itemStruct.video`

Important fields:
- `downloadAddr`
- `playAddr`
- `PlayAddrStruct.UrlList`
- `bitrateInfo[].PlayAddr.UrlList`

### 3. If PinchTab profile proxy exists, always use it

Proxy rule:
- if the active PinchTab profile has a proxy, use it in the final HTTPS media request
- if that proxy is residential, that is preferred
- if the proxy is empty, skip the proxy and continue

Do not ignore a non-empty profile proxy. Use it.

## Workflow

1. Find or create the active PinchTab tab.
2. Navigate the tab to `tiktok_url`.
3. Confirm the current page state.
4. Extract the browser `User-Agent` using PinchTab.
5. Extract live TikTok cookies using PinchTab.
6. Extract the active profile proxy using PinchTab.
7. Extract the signed media URL from the TikTok hydration payload using PinchTab.
8. Download the media over HTTPS using:
   - profile proxy if present
   - browser UA
   - live cookies
   - TikTok referer
9. Verify the downloaded file is a real MP4.

## Step 1: Find or Create a PinchTab Tab

List tabs:

```bash
curl -s "$PINCHTAB_SERVER_URL/tabs" \
  -H "Authorization: Bearer $PINCHTAB_TOKEN"
```

If no tab exists, create one:

```bash
curl -s -X POST "$PINCHTAB_SERVER_URL/navigate" \
  -H "Authorization: Bearer $PINCHTAB_TOKEN" \
  -H "Content-Type: application/json" \
  -d "{\"url\":\"$tiktok_url\"}"
```

This returns `tabId`. Save it to `TAB_ID`.

If `TAB_ID` is already known, reuse it.

## Step 2: Navigate the PinchTab Tab

Always navigate directly to `tiktok_url` first:

```bash
curl -s -X POST "$PINCHTAB_SERVER_URL/tabs/$TAB_ID/navigate" \
  -H "Authorization: Bearer $PINCHTAB_TOKEN" \
  -H "Content-Type: application/json" \
  -d "{\"url\":\"$tiktok_url\"}"
```

Then wait:

```bash
sleep 3
```

Why:
- TikTok search pages can leave the session in mixed search/detail state
- a direct navigate to the exact URL is more reliable before extraction

## Step 3: Confirm Page State with PinchTab

```bash
expr='({href: location.href, title: document.title, ready: document.readyState, text: document.body ? document.body.innerText.slice(0,1500) : ""})'
jq -n --arg expr "$expr" '{expression:$expr}' | \
curl -s -X POST "$PINCHTAB_SERVER_URL/tabs/$TAB_ID/evaluate" \
  -H "Authorization: Bearer $PINCHTAB_TOKEN" \
  -H "Content-Type: application/json" \
  -d @-
```

What you want:
- `ready` is `complete`
- `href` is the intended TikTok video page

If the URL is correct but the title or text still look like search results:
- navigate again to the exact TikTok video URL
- wait 2 to 4 seconds
- retry

## Step 4: Extract Browser User-Agent with PinchTab

```bash
expr='navigator.userAgent'
jq -n --arg expr "$expr" '{expression:$expr}' | \
curl -s -X POST "$PINCHTAB_SERVER_URL/tabs/$TAB_ID/evaluate" \
  -H "Authorization: Bearer $PINCHTAB_TOKEN" \
  -H "Content-Type: application/json" \
  -d @-
```

Use that exact `User-Agent` value in the final HTTPS download request.

## Step 5: Extract TikTok Cookies with PinchTab

```bash
curl -s "$PINCHTAB_SERVER_URL/tabs/$TAB_ID/cookies?url=https%3A%2F%2Fwww.tiktok.com%2F" \
  -H "Authorization: Bearer $PINCHTAB_TOKEN"
```

Build a standard `Cookie:` header from the returned cookie list.

Cookies that commonly matter:
- `sid_tt`
- `sessionid`
- `sessionid_ss`
- `ttwid`
- `msToken`
- `odin_tt`
- `tt_chain_token`
- `d_ticket`

Refresh cookies from PinchTab if the final media request fails.

## Step 6: Extract the Profile Proxy with PinchTab

Get instances:

```bash
curl -s "$PINCHTAB_SERVER_URL/instances" \
  -H "Authorization: Bearer $PINCHTAB_TOKEN"
```

Identify the active instance for the tab or profile you are using.

Then get profiles:

```bash
curl -s "$PINCHTAB_SERVER_URL/profiles" \
  -H "Authorization: Bearer $PINCHTAB_TOKEN"
```

Read the active profile’s proxy from:

- `backend.steel.proxyUrl`

Proxy logic:
- if proxy is non-empty, use it
- if proxy is empty, skip proxy usage

If the proxy is residential, prefer it.

## Step 7: Extract the Signed Media URL with PinchTab

Preferred structured extraction:

```bash
expr='(() => {
  const raw = document.getElementById("__UNIVERSAL_DATA_FOR_REHYDRATION__")?.textContent;
  if (!raw) return { error: "no hydration script" };
  const data = JSON.parse(raw);
  const item = data?.__DEFAULT_SCOPE?.["webapp.video-detail"]?.itemInfo?.itemStruct;
  return item ? {
    id: item.id,
    author: item.author?.uniqueId,
    desc: item.desc,
    video: {
      downloadAddr: item.video?.downloadAddr,
      playAddr: item.video?.playAddr,
      format: item.video?.format,
      size: item.video?.size
    }
  } : { error: "video-detail missing" };
})()'

jq -n --arg expr "$expr" '{expression:$expr}' | \
curl -s -X POST "$PINCHTAB_SERVER_URL/tabs/$TAB_ID/evaluate" \
  -H "Authorization: Bearer $PINCHTAB_TOKEN" \
  -H "Content-Type: application/json" \
  -d @-
```

Use:
- `downloadAddr` first
- `playAddr` second

## Step 8: Fallback When `video-detail` Is Empty

Sometimes PinchTab shows:
- correct video URL
- valid page text
- but empty `webapp.video-detail`

That is usually TikTok mixed page state.

Fallback using PinchTab:

Dump the raw hydration script:

```bash
expr='(() => document.getElementById("__UNIVERSAL_DATA_FOR_REHYDRATION__")?.textContent || "")()'
jq -n --arg expr "$expr" '{expression:$expr}' | \
curl -s -X POST "$PINCHTAB_SERVER_URL/tabs/$TAB_ID/evaluate" \
  -H "Authorization: Bearer $PINCHTAB_TOKEN" \
  -H "Content-Type: application/json" \
  -d @- > /tmp/tiktok_hydration.json
```

Parse locally:

```bash
python3 - <<'PY'
import json
obj = json.loads(open('/tmp/tiktok_hydration.json').read())
raw = obj['result']
data = json.loads(raw)
item = data['__DEFAULT_SCOPE__']['webapp.video-detail']['itemInfo']['itemStruct']
video = item['video']
print(json.dumps({
    'id': item['id'],
    'author': item['author']['uniqueId'],
    'desc': item['desc'],
    'downloadAddr': video.get('downloadAddr'),
    'playAddr': video.get('playAddr'),
    'format': video.get('format'),
    'size': video.get('size')
}, ensure_ascii=False, indent=2))
PY
```

If this still fails:
- navigate again with PinchTab to the exact TikTok video URL
- wait
- repeat the hydration dump

## Step 9: Download the Media

Build the final HTTPS request from PinchTab-derived values:
- `downloadAddr` or `playAddr`
- browser UA from PinchTab
- cookies from PinchTab
- profile proxy from PinchTab if present
- page URL as `Referer`

Without proxy:

```bash
curl -L --http1.1 --fail --show-error --silent \
  -A "$BROWSER_UA" \
  -H "Referer: $CURRENT_TIKTOK_PAGE" \
  -H "Origin: https://www.tiktok.com" \
  -H "Cookie: $COOKIE_HEADER" \
  "$SIGNED_DOWNLOAD_ADDR" \
  -o "${OUT:-/tmp/tiktok_video.mp4}"
```

With proxy:

```bash
curl -L --http1.1 --fail --show-error --silent \
  --proxy "$PROFILE_PROXY" \
  -A "$BROWSER_UA" \
  -H "Referer: $CURRENT_TIKTOK_PAGE" \
  -H "Origin: https://www.tiktok.com" \
  -H "Cookie: $COOKIE_HEADER" \
  "$SIGNED_DOWNLOAD_ADDR" \
  -o "${OUT:-/tmp/tiktok_video.mp4}"
```

Use the proxy variant whenever the PinchTab profile proxy is non-empty.

## Step 10: Verify the Output

```bash
ls -lh "${OUT:-/tmp/tiktok_video.mp4}"
file "${OUT:-/tmp/tiktok_video.mp4}"
xxd -l 16 "${OUT:-/tmp/tiktok_video.mp4}"
```

Expected:
- file type is MP4 or ISO Media
- header contains `ftypisom` or another valid MP4 signature

Failure signs:
- HTML output
- tiny file
- header starts with `<!DOCTYPE` or `<html`

## Full PinchTab Example

This example assumes:
- `PINCHTAB_SERVER_URL`
- `PINCHTAB_TOKEN`
- `TAB_ID`
- `tiktok_url`

```bash
curl -s -X POST "$PINCHTAB_SERVER_URL/tabs/$TAB_ID/navigate" \
  -H "Authorization: Bearer $PINCHTAB_TOKEN" \
  -H "Content-Type: application/json" \
  -d "{\"url\":\"$tiktok_url\"}"

sleep 3

expr='navigator.userAgent'
jq -n --arg expr "$expr" '{expression:$expr}' | \
curl -s -X POST "$PINCHTAB_SERVER_URL/tabs/$TAB_ID/evaluate" \
  -H "Authorization: Bearer $PINCHTAB_TOKEN" \
  -H "Content-Type: application/json" \
  -d @- > /tmp/ua.json

BROWSER_UA=$(jq -r '.result' /tmp/ua.json)

curl -s "$PINCHTAB_SERVER_URL/tabs/$TAB_ID/cookies?url=https%3A%2F%2Fwww.tiktok.com%2F" \
  -H "Authorization: Bearer $PINCHTAB_TOKEN" > /tmp/cookies.json

COOKIE_HEADER=$(python3 - <<'PY'
import json
obj = json.loads(open('/tmp/cookies.json').read())
print('; '.join(f"{c['name']}={c['value']}" for c in obj['cookies']))
PY
)

PROFILE_PROXY=$(curl -s "$PINCHTAB_SERVER_URL/profiles" \
  -H "Authorization: Bearer $PINCHTAB_TOKEN" | \
python3 - <<'PY'
import json,sys
profiles=json.load(sys.stdin)
for p in profiles:
    proxy=((p.get('backend') or {}).get('steel') or {}).get('proxyUrl') if (p.get('backend') or {}).get('kind')=='steel' else None
    if proxy:
        print(proxy)
        break
PY
)

expr='(() => document.getElementById("__UNIVERSAL_DATA_FOR_REHYDRATION__")?.textContent || "")()'
jq -n --arg expr "$expr" '{expression:$expr}' | \
curl -s -X POST "$PINCHTAB_SERVER_URL/tabs/$TAB_ID/evaluate" \
  -H "Authorization: Bearer $PINCHTAB_TOKEN" \
  -H "Content-Type: application/json" \
  -d @- > /tmp/tiktok_hydration.json

SIGNED_DOWNLOAD_ADDR=$(python3 - <<'PY'
import json
obj = json.loads(open('/tmp/tiktok_hydration.json').read())
raw = obj['result']
data = json.loads(raw)
item = data['__DEFAULT_SCOPE__']['webapp.video-detail']['itemInfo']['itemStruct']
video = item['video']
print(video.get('downloadAddr') or video.get('playAddr'))
PY
)

CURRENT_TIKTOK_PAGE="$tiktok_url"
OUT="${OUT:-/tmp/tiktok_video.mp4}"

if [ -n "$PROFILE_PROXY" ]; then
  curl -L --http1.1 --fail --show-error --silent \
    --proxy "$PROFILE_PROXY" \
    -A "$BROWSER_UA" \
    -H "Referer: $CURRENT_TIKTOK_PAGE" \
    -H "Origin: https://www.tiktok.com" \
    -H "Cookie: $COOKIE_HEADER" \
    "$SIGNED_DOWNLOAD_ADDR" \
    -o "$OUT"
else
  curl -L --http1.1 --fail --show-error --silent \
    -A "$BROWSER_UA" \
    -H "Referer: $CURRENT_TIKTOK_PAGE" \
    -H "Origin: https://www.tiktok.com" \
    -H "Cookie: $COOKIE_HEADER" \
    "$SIGNED_DOWNLOAD_ADDR" \
    -o "$OUT"
fi

ls -lh "$OUT"
file "$OUT"
xxd -l 16 "$OUT"
```

## Error Cases

### `403` on final media fetch

Fix:
- refresh cookies from PinchTab
- re-extract signed media URL from PinchTab
- confirm profile proxy is being used if non-empty
- confirm `Referer` matches the video page

### HTML instead of video

Fix:
- verify output with `file` and `xxd`
- re-extract from current PinchTab page state
- do not reuse an old media URL

### `video-detail` is empty

Fix:
- re-navigate with PinchTab to the exact video URL
- wait
- dump raw hydration with PinchTab
- parse locally

### Proxy is empty

Fix:
- skip the proxy
- continue the download
- expect a higher chance of `403`

## Success Criteria

The workflow is complete only when:
- PinchTab is on the intended TikTok video page
- the media URL came from the current PinchTab page state
- the final HTTPS request used PinchTab-derived cookies and UA
- the profile proxy was used if it was non-empty
- the saved file verifies as a real MP4
