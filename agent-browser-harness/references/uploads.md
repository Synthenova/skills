# Uploads

Use this reference for file inputs, drag-and-drop upload zones, and upload flows that reveal extra controls only after processing starts.

## Preferred Path

If a real file input exists, use:

```bash
agent-browser upload @e3 /absolute/path/to/file.mp4
```

Find the input via:

```bash
agent-browser snapshot -i
agent-browser find label "Upload" click
agent-browser snapshot -i
```

## Verification

Uploading is not complete just because the command succeeded. Verify:
- file name appears
- progress UI appears or disappears as expected
- downstream controls become enabled
- network activity starts or settles

Useful checks:

```bash
agent-browser screenshot /tmp/upload.png
agent-browser snapshot -i
agent-browser network requests
```

## Hidden Inputs

Many upload UIs hide the actual file input behind a visible button. The reliable pattern is:

1. Trigger the upload UI if needed.
2. Re-snapshot.
3. Upload to the actual file input ref.
4. Verify processing state before continuing.

## Drag And Drop

If the site truly requires drag-and-drop rather than a file input:
- verify there is no workable input first
- use drag mechanics only when the visible flow proves it is necessary
- re-check whether the dropped asset appeared before attempting later steps
