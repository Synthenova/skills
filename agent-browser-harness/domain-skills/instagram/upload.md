# Instagram Reel Upload From Disk

Use this when posting a reel from a local video file through Instagram web with `agent-browser`.

## Preconditions

- `agent-browser` is already running with the intended profile and proxy.
- The Instagram account is already logged in.
- The video file exists on disk and is ready to upload.
- The final caption text is already decided before opening the composer.

## Reliable Flow

1. Open the target account or profile surface.
2. Open `New post`.
3. Choose `Post`.
4. In `Create new post`, upload the local file with `agent-browser upload 'input[type=file]' /absolute/path/to/video.mp4`.
5. Wait for the crop step to render.
6. Click `Next`.
7. Wait for the edit step to render.
8. Click `Next`.
9. Wait for the final `New reel` composer.
10. Fill the caption in `Write a caption...`.
11. Verify the exact caption text before sharing.
12. Click `Share`.
13. Wait through Instagram's `Sharing` modal instead of clicking again.
14. After publish completes, go to the profile reels grid and capture the latest reel URL from the page.

## Verification

Verify each step with `snapshot -i`:

- `Create new post`
- `Crop`
- `Edit`
- `New reel`
- post-share completion state

Do not assume the share succeeded just because the click returned `Done`.

## Recoveries

### Share spinner stays up

- Wait first. Instagram can spend a long time processing server-side.
- Do not dismiss the modal while the upload is still processing.
- If the modal eventually clears, re-open the profile reels page and capture the latest reel URL.

### Draft recovery prompt

- Prefer `Continue` rather than discarding the draft if Instagram surfaces a recovery prompt after an interruption.

### Latest reel ID capture

Once the profile reels page is loaded, extract reel links directly from the page:

```bash
agent-browser eval 'Array.from(document.querySelectorAll("a[href*=\"/reel/\"]")).map(a => a.href).slice(0,10)'
```

Use the newest reel URL as the platform source of truth.

If the database stores Instagram's numeric media ID instead of the shortcode, convert the shortcode from the captured URL before writing the row.
