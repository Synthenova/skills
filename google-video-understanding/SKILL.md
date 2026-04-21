---
name: google-video-understanding
description: Analyze local video files or public YouTube URLs with the Gemini API and write a markdown report to disk. Use when Codex needs video-plus-audio understanding from Google Gemini, must accept either a file path or YouTube URL, must enforce a hard maximum duration of 3 minutes, and should run from a skill-local virtualenv instead of depending on another project environment.
---

# Google Video Understanding

Use the bundled runner for all execution:

```bash
scripts/run_video_analysis.sh SOURCE OUTPUT.md [--prompt-file PATH] [--model MODEL] [--api-key KEY]
```

Inputs:
- `SOURCE`: local video path or public YouTube URL
- `OUTPUT.md`: markdown destination path

Defaults:
- model: `gemini-flash-lite-latest`
- prompt: bundled default analysis prompt inside `scripts/video_analysis.py`
- max duration: 180 seconds

Authentication:
- Prefer `GEMINI_API_KEY` in the environment
- Or pass `--api-key`
- Do not hardcode API keys into the skill files

## Workflow

1. Run `scripts/run_video_analysis.sh`, not the Python file directly.
2. Let the runner create `./.venv` inside this skill with Python 3.13 using `uv`.
3. Let the runner install only the required packages for this skill:
   - `google-genai`
   - `yt-dlp`
4. Let `scripts/video_analysis.py`:
   - use its bundled default analysis prompt
   - reject any input longer than 3 minutes
   - send the source to Gemini
   - write markdown to the requested output path

## Rules

- Keep this skill self-contained. Its runtime lives in `google-video-understanding/.venv`.
- Use `yt-dlp` only for YouTube metadata checks, not for downloading unless the skill is explicitly changed later.
- Use Gemini directly through the `google-genai` SDK.
- Write plain markdown only.
- Fail fast on missing API key, unsupported duration, empty custom prompt file, or missing local file.

## Commands

Basic usage:

```bash
scripts/run_video_analysis.sh "/abs/path/video.mp4" "/abs/path/output.md"
```

With API key flag:

```bash
scripts/run_video_analysis.sh "https://www.youtube.com/watch?v=..." "/abs/path/output.md" --api-key "$GEMINI_API_KEY"
```

With a custom prompt file:

```bash
scripts/run_video_analysis.sh "/abs/path/video.mp4" "/abs/path/output.md" --prompt-file /abs/path/prompt.py
```

## Files

- `scripts/run_video_analysis.sh`: bootstrap local Python 3.13 env and dependencies
- `scripts/video_analysis.py`: duration gate, Gemini call, markdown output
- `.gitignore`: ignore the skill-local `.venv`
