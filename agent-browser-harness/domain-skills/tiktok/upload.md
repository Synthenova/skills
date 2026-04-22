# TikTok Studio — Upload And Schedule From Disk

URL: `https://www.tiktok.com/tiktokstudio/upload?from=upload&lang=en`

Always keep `&lang=en` in the URL so labels stay stable for refs and text finders.

## Scope

Use this flow when you already have a local video file on disk and need to upload it in TikTok Studio, set caption/schedule options, and confirm the resulting Studio content entry.

This guide starts from the local file path. It does not cover external storage systems.

## Prerequisites

- Logged into TikTok in the browser session used by `agent-browser`
- Local video file path available
- TikTok Studio is reachable in the current browser session

## Starting Pattern

Open Studio upload first, then inspect before acting:

```bash
agent-browser open "https://www.tiktok.com/tiktokstudio/upload?from=upload&lang=en"
agent-browser snapshot -i
```

If TikTok is slow, prefer short waits and re-checks over large one-shot commands:

```bash
agent-browser wait 2000
agent-browser get url
agent-browser snapshot -i
```

## Stale Draft Recovery

TikTok often restores an abandoned draft with:

- `A video you were editing wasn’t saved`
- `Discard`
- `Continue`

If you want to keep the prior edit, click `Continue`.
If you need a clean upload, click `Discard`.

For ongoing work, prefer `Continue` unless the draft state is clearly wrong.

Example:

```bash
agent-browser snapshot -i
agent-browser click @eN   # Continue
```

## Upload From Local Disk

TikTok exposes a hidden file input on the upload page. The visible `Select video` button may not itself be the file input, so inspect first:

```bash
agent-browser eval "JSON.stringify(Array.from(document.querySelectorAll('input[type=file]')).map((i,idx)=>({idx, accept:i.accept, outer:i.outerHTML.slice(0,200)})))"
```

Then upload directly to the actual file input:

```bash
agent-browser upload "input[type=file]" /absolute/path/to/video.mp4
```

Wait for the composer to render:

```bash
agent-browser wait 12000
agent-browser snapshot -i
```

Good signs:

- filename is shown at top of the editor
- `Uploaded` status is visible
- caption/editor controls appear
- `Schedule` and `Post` controls appear lower in the form

## Caption

TikTok pre-fills the caption/editor with the filename. Clear it before typing.

The caption field is a contenteditable combobox. User-like key input is more reliable than DOM mutation.

Example:

```bash
agent-browser snapshot -i
agent-browser focus @eN
agent-browser press Control+a
agent-browser press Backspace
agent-browser keyboard type "Your caption here #tag1 #tag2"
agent-browser press Escape
```

Verify:

```bash
agent-browser get text @eN
```

## Scheduling

### 1. Enable schedule mode

Use the actual schedule radio, not only the label, if the label click does not commit:

```bash
agent-browser snapshot -i
agent-browser check @eN
agent-browser snapshot -i
```

After success, the action button text changes to `Schedule`, and the time/date controls appear.

### 2. Set the date

TikTok renders the date field as a readonly text input behind a picker. If the visible date is already correct, leave it alone.

Otherwise open the date picker, re-snapshot, and click the target day.

Verify the visible field after closing the picker.

### 3. Set the time

TikTok’s time control is a custom picker, not a native input.

Observed working pattern:

1. Open the time picker by clicking the visible time field.
2. Inspect the picker DOM if ref-based actions are not enough.
3. The picker contains hour and minute option lists under classes like:
   - `.tiktok-timepicker-time-scroll-container`
   - `.tiktok-timepicker-option-text`
   - `.tiktok-timepicker-is-active`
4. The selected hour and minute can be verified from the active option classes.
5. Close the picker and confirm the visible time field now shows the chosen value.

Useful inspection command:

```bash
agent-browser eval "(()=>{const root=document.querySelector('.scheduled-picker'); return root ? [...root.querySelectorAll('.tiktok-timepicker-is-active')].map(el=>el.textContent.trim()) : [];})()"
```

Useful field verification:

```bash
agent-browser eval "(()=>Array.from(document.querySelectorAll('input.TUXTextInputCore-input')).map(i=>i.getAttribute('value')))()"
```

Do not rely on ordinary `fill` for the time field. The displayed control is readonly and the picker owns the real state.

## Content Check Lite

`Content check lite` appears lower in the form near `View details`.

If you need it off:

1. Scroll the checks section into view.
2. Re-snapshot.
3. Toggle the specific `Content check lite` row control.
4. Re-verify before scheduling.

This control may not expose a clean label-bound ref. In that case:

- use `snapshot -i` to identify the row adjacent to `View details`
- or use a direct mouse click on the row once it is in view

## Final Submit

The final `Schedule` button may exist outside the visible viewport even though it has a valid ref. If a semantic click appears to do nothing:

1. `scrollintoview` the button ref
2. fetch its box
3. click the real coordinates

Example:

```bash
agent-browser scrollintoview @eN
agent-browser --json get box @eN
agent-browser batch --bail "mouse move X Y" "mouse down left" "mouse up left"
```

Success signal:

- URL changes to `https://www.tiktok.com/tiktokstudio/content`

Verify:

```bash
agent-browser get url
agent-browser snapshot -i
```

## Capture The Real Platform ID

After redirect to Studio content:

1. find the newest row matching the uploaded caption
2. extract the TikTok video URL from the row link
3. store the numeric ID from `/video/<id>`

Example inspection:

```bash
agent-browser snapshot -i
agent-browser eval "(()=>({links:[...document.querySelectorAll('a[href]')].map(a=>a.href).filter(h=>h.includes('/video/')).slice(0,20), text:document.body.innerText.slice(0,5000)}))()"
```

The newest scheduled item typically appears at the top of the content list with its scheduled time label.

## Working Recovery Notes

- If a page-level command hangs, do not immediately discard the draft. Re-open the current page state first.
- On refresh, TikTok often restores the draft and offers `Continue` or `Discard`. Use `Continue` to preserve the in-progress edit.
- Semantic ref clicks may succeed visually but fail to trigger the real submit if the control is offscreen. In that case, scroll it into view and click by coordinates.
- TikTok Studio can be responsive for profile and content pages while still being sluggish inside the upload editor. Short, verifiable commands work better than large compound reads.
- `snapshot -i` is usually safe on the content page and lighter-weight than large `eval` payloads.
