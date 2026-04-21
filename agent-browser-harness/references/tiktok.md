# TikTok Studio — Upload Video

URL: `https://www.tiktok.com/tiktokstudio/upload?from=upload&lang=en`

Always keep `&lang=en` so visible labels and text-based finders remain stable.

## Prerequisites

- Logged into TikTok in the browser profile or saved state used by `agent-browser`
- Video file on local disk
- Upload task does not require bypassing captcha or human-only approval

If login is missing, use the packaged `agent-browser` authentication guidance first.

## Start State

Open the upload page, then inspect before acting:

```bash
agent-browser open "https://www.tiktok.com/tiktokstudio/upload?from=upload&lang=en"
agent-browser wait --load networkidle
agent-browser snapshot -i
agent-browser screenshot /tmp/tiktok-upload-start.png
```

## Stale Draft Banner

TikTok may show a stale draft warning like "A video you were editing wasn't saved".

Recovery pattern:

1. Use `snapshot -i` and `find text` or `find role button` to locate a visible discard action.
2. Click the first discard control.
3. Re-snapshot for the confirmation modal.
4. Click the confirmation discard button.
5. Repeat if stacked drafts remain.

Example:

```bash
agent-browser find text "Discard" click
agent-browser snapshot -i
agent-browser find text "Discard" click
agent-browser screenshot /tmp/tiktok-after-discard.png
```

Verify that the banner is gone before uploading.

## Attach File

Prefer a real file input if TikTok exposes one:

```bash
agent-browser snapshot -i
agent-browser upload @eN /absolute/path/to/video.mp4
```

Then verify processing started:

```bash
agent-browser network requests --clear
agent-browser wait 2000
agent-browser screenshot /tmp/tiktok-upload-processing.png
agent-browser snapshot -i
agent-browser network requests
```

Processing often takes several seconds before caption and schedule controls stabilize.

## Caption

TikTok pre-fills caption content with the filename. Clear the field before typing.

Preferred pattern:

1. `snapshot -i`
2. focus the contenteditable caption ref
3. clear with keyboard commands
4. type caption
5. dismiss suggestion overlays if they appear
6. verify caption text

Example:

```bash
agent-browser snapshot -i
agent-browser focus @eN
agent-browser press Control+a
agent-browser press Backspace
agent-browser keyboard type "your caption here #hashtag1 #hashtag2"
agent-browser press Escape
```

Verification:

```bash
agent-browser get text @eN
agent-browser screenshot /tmp/tiktok-caption.png
```

If TikTok ignores `Control+a`, move to the end and backspace through the filename instead of mutating DOM with JavaScript.

## Schedule

When scheduling instead of immediate posting:

1. Select the visible `Schedule` control.
2. Re-snapshot after the scheduling UI appears.
3. Handle time and date pickers as virtualized controls, not native selects.

Example start:

```bash
agent-browser find text "Schedule" click
agent-browser snapshot -i
agent-browser screenshot /tmp/tiktok-schedule-open.png
```

### Time Picker

TikTok's time picker behaves like a wheel-based list. Treat it as a scrolling control.

Pattern:

1. Open the time picker.
2. Take a screenshot to confirm which columns are visible.
3. Place the mouse over the correct hour or minute column.
4. Use small `mouse wheel` steps.
5. Verify the resulting displayed time after each adjustment batch.

Example:

```bash
agent-browser mouse move 350 540
agent-browser mouse wheel 160
agent-browser screenshot /tmp/tiktok-hour-wheel.png
```

Then repeat over the minute column if needed.

Do not assume JavaScript `.click()` or ordinary page scroll will change the value.

### Date Picker

Open the date picker, re-snapshot, then click the visible day button or day cell ref. Verify the chosen date in the input or summary field.

## AI-Generated Content Disclosure

This setting lives under expanded controls and may appear only after clicking `Show more`.

Pattern:

1. Expand `Show more` if present.
2. Re-snapshot.
3. Locate the `AI-generated content` row or toggle.
4. Read current state before toggling.
5. If a confirmation dialog appears, handle it explicitly.

Use:
- `snapshot -i`
- `get text ...`
- `dialog status`
- `dialog accept`

## Submit

Once caption and schedule settings are correct:

1. Re-snapshot for the final button state.
2. Confirm the action button text is what you intend, usually `Schedule` after the schedule option is enabled.
3. Clear network log.
4. Click the final button.
5. Verify both network activity and resulting page state.

Example:

```bash
agent-browser network requests --clear
agent-browser snapshot -i
agent-browser click @eN
agent-browser wait 3000
agent-browser get url
agent-browser network requests
agent-browser screenshot /tmp/tiktok-post-submit.png
```

Successful completion usually redirects to TikTok Studio content management rather than leaving you on the upload form.

## Gotchas

- Always keep `lang=en` in the URL.
- Re-snapshot after opening scheduling controls, expanding `Show more`, dismissing stale drafts, or submitting.
- TikTok pickers often behave like wheel-based or virtualized controls rather than native inputs.
- Caption fields are contenteditable and should be cleared through user-like keyboard input, not DOM mutation.
- `beforeunload` can appear if you leave the upload page mid-edit; handle it explicitly.
- Use screenshots often. TikTok moves controls, overlays panels, and changes visible affordances after upload processing starts.
