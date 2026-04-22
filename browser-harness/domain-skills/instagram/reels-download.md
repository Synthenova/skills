# Instagram — Reels Download

Use this when the current tab is already on an Instagram reel page and you need the actual video file, not the blob-backed player stream.

## Canonical URL

Prefer the canonical reel route:

- `https://www.instagram.com/reel/<code>/`

Instagram may also open on:

- `https://www.instagram.com/reels/<code>/`

Both point to the same reel. The durable identifier is the shortcode in the path.

## Trap: The Visible `<video>` Uses Blob URLs

Do not start from `document.querySelector("video").src`.

On the live reel page, Instagram commonly feeds the player through Media Source Extensions, so the DOM video elements expose:

- `blob:https://www.instagram.com/...`

Those blob URLs are not reusable for direct download.

## Best Source Of Truth

Use the Relay payload already embedded in page scripts.

On the reel page, a `ScheduledServerJS` script contains:

- `xdt_api__v1__clips__home__connection_v2`

That payload includes the current reel's media object keyed by the shortcode in the current URL.

The durable fields are:

- `video_versions[*].url` for direct progressive MP4 URLs
- `video_dash_manifest` for the DASH manifest
- `image_versions2.candidates[*].url` for posters

Prefer `video_versions[*].url` first because it is the simplest direct MP4 path.

## Browser-Harness Extraction Pattern

Use the live tab attached through `BU_CDP_WS`.

```python
print(page_info())

data = js(r"""(() => {
  const code = location.pathname.split('/').filter(Boolean).pop();
  const text = Array.from(document.scripts)
    .map(s => s.textContent || '')
    .find(t => t.includes('xdt_api__v1__clips__home__connection_v2') && t.includes(code));
  if (!text) return null;

  const idx = text.indexOf(`"code":"${code}"`);
  const vIdx = text.indexOf('"video_versions":', idx);
  const dIdx = text.indexOf('"video_dash_manifest":', idx);
  const chunk = text.slice(vIdx, vIdx + 6000);
  const versions = chunk.match(/"video_versions":([\s\S]*?),"has_audio"/);
  const dash = text.slice(dIdx, dIdx + 2500).match(/"video_dash_manifest":"([\s\S]*?)","video_duration"/);

  return {
    code,
    video_versions: versions ? JSON.parse(versions[1]) : null,
    video_dash_manifest: dash ? dash[1] : null,
  };
})()""")

print(data["code"])
print(data["video_versions"][0]["url"])
```

## Download Pattern

The extracted `video_versions[*].url` worked as a direct MP4 download with:

- browser user agent
- reel page as the `Referer`

Example:

```bash
curl -L --fail \
  -A 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36' \
  -H 'Referer: https://www.instagram.com/reel/<code>/' \
  '<video_versions_url>' \
  -o /tmp/instagram-reel.mp4
```

## Live Verification

Verified on:

- `https://www.instagram.com/reels/DUnxGL8Et7s/`

What worked:

- extracting `video_versions[*].url` from the embedded Relay payload
- downloading the first progressive URL directly

Result:

- `/tmp/instagram-reel.mp4`
- file type: `ISO Media, MP4 Base Media`

## Notes

- `video_versions` may contain repeated URLs with different `type` values. Reuse the URL itself as the true key.
- `video_dash_manifest` is present and can be parsed if you need representation-level control, but the progressive URLs are simpler when available.
- `document.querySelector("meta[property='og:video']")` was not populated on this live reel page, so the Relay payload was the reliable source.
