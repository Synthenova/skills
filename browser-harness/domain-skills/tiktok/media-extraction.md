# TikTok — Video Media Extraction

Use this when the current tab is already on a TikTok watch page and you need the actual video file, not screenshots or captions.

## Canonical URL

Prefer the canonical watch URL:

- `https://www.tiktok.com/@<handle>/video/<id>`

If the current tab includes search params like `?q=...&t=...`, keep them for the live tab if needed, but for extraction the durable identifier is the canonical `@handle/video/id` path.

## Best Source Of Truth

Do not start from the visible player element or the first media-looking network request.

Use the page hydration payload:

```python
item = js("""(() => {
  const s = document.getElementById('__UNIVERSAL_DATA_FOR_REHYDRATION__');
  if (!s) return null;
  const data = JSON.parse(s.textContent);
  return data?.__DEFAULT_SCOPE__?.['webapp.video-detail']?.itemInfo?.itemStruct || null;
})()""")
```

Then read:

- `item["video"]["downloadAddr"]` first
- `item["video"]["playAddr"]` second
- `item["video"]["PlayAddrStruct"]["UrlList"]` as fallback mirrors
- `item["video"]["bitrateInfo"][...]["PlayAddr"]["UrlList"]` for alternate encodes

`downloadAddr` and `playAddr` are the durable fields. The network log may rotate between `v16-webapp-prime` and `v19-webapp-prime`, but the hydration payload keeps the stable structure.

## Trap: Subtitle URLs Look Like Video

TikTok subtitle and caption URLs can also include `mime_type=video_mp4` in the query string.

The tell:

- subtitle payloads download as `WEBVTT`
- hydration exposes them under `item["video"]["subtitleInfos"][...]` or `item["video"]["claInfo"]["captionInfos"][...]`

Do not trust the first `performance` or network entry that contains `mime_type=video_mp4`.
Check whether the URL came from:

- `video.downloadAddr` or `video.playAddr` → real video
- `subtitleInfos` or `captionInfos` → captions, not video

## Browser-Harness Extraction Pattern

Use the live tab attached through `BU_CDP_WS`.

Minimal extraction:

```python
print(page_info())

item = js("""(() => {
  const s = document.getElementById('__UNIVERSAL_DATA_FOR_REHYDRATION__');
  if (!s) return null;
  const data = JSON.parse(s.textContent);
  return data?.__DEFAULT_SCOPE__?.['webapp.video-detail']?.itemInfo?.itemStruct || null;
})()""")

video = item["video"]
print(video["downloadAddr"])
print(video["playAddr"])
```

If you want to sanity-check against the live player:

```python
print(js("""(() =>
  performance.getEntriesByType('resource')
    .map(e => e.name)
    .filter(u => /video\\/tos|mime_type=video_mp4/.test(u))
)()"""))
```

But hydration remains the primary source of truth.

## Download Requirements

Direct `curl` to `downloadAddr` can return `403` even when the URL is fresh.

What worked from a live Penny browser session:

- the active browser's residential proxy
- the active browser cookies from CDP, not `document.cookie`
- browser user agent
- TikTok watch-page referer

Important:

- `document.cookie` misses `HttpOnly` cookies like `sessionid`, `sid_tt`, and `ttwid`
- use raw CDP cookies instead:

```python
cookies = cdp("Network.getCookies", urls=["https://www.tiktok.com/"])["cookies"]
```

Cookie names that mattered in the successful fetch:

- `sessionid`
- `sessionid_ss`
- `sid_tt`
- `ttwid`
- `msToken`
- `tt_chain_token`
- `d_ticket`

If the attached Chrome profile is running behind a proxy, reuse that proxy for the final HTTP request. In one verified run, bare `curl` returned `403`, while the same request succeeded once it matched the profile proxy plus cookies.

## Verified Download Pattern

This pattern worked against a live Penny session:

1. Extract `downloadAddr` from hydration.
2. Read `navigator.userAgent`.
3. Read cookies via `cdp("Network.getCookies", urls=["https://www.tiktok.com/"])`.
4. Reuse the Chrome profile proxy from the browser config when present.
5. Download with:
   - `Referer: <current TikTok watch URL>`
   - browser `User-Agent`
   - cookie header built from CDP cookies
   - profile proxy if configured
6. Verify with `file` and size checks.

Example verification target:

- expected file type: `ISO Media, MP4 Base Media`
- not `WEBVTT`
- non-trivial byte size

## Fallbacks

If `downloadAddr` fails:

1. retry with the same proxy + cookies
2. try `playAddr`
3. try the first `PlayAddrStruct.UrlList` entry
4. try the first `bitrateInfo[*].PlayAddr.UrlList` entry

If all media URLs fail but the page is visibly playing:

- re-read hydration after a reload
- re-read cookies from CDP
- confirm you are still on the intended watch page with `page_info()`

## Things Not To Do

- Do not scrape pixel coordinates for a download button.
- Do not rely on `document.cookie` alone.
- Do not assume the first network media-looking URL is the MP4.
- Do not assume a public unauthenticated `curl` will work outside the live browser context.
