#!/usr/bin/env python3
from __future__ import annotations

import argparse
import mimetypes
import os
import subprocess
import time
from pathlib import Path
from urllib.parse import urlparse

from google import genai
from google.genai import types
from yt_dlp import YoutubeDL


DEFAULT_MODEL = "gemini-flash-lite-latest"
MAX_DURATION_SECONDS = 180.0
POLL_INTERVAL_SECONDS = 2.0
MAX_POLL_SECONDS = 120.0
DEFAULT_ANALYSIS_PROMPT = """You are an expert Video Analysis AI specialized in extracting comprehensive, structured information from video content.

Analyze this video and return a detailed analysis in markdown format:

## Metadata
- **Title**: Descriptive title of the video content
- **Duration**: Estimated duration (MM:SS format)
- **Aspect Ratio**: e.g., 16:9, 9:16, 1:1
- **Resolution**: e.g., 1080p, 4K, 720p
- **Video Type**: e.g., live-action, animation, motion graphics

## Transcript
- **Has Speech**: yes/no/unknown
- **Spoken Dialogue**: All spoken lines with timestamps, speaker/source type (dialogue/voiceover/lyrics), and tone
- **On-Screen Text**: All visible text with timestamps and positioning/style

## Hook & Call to Action
- **Hook**: The opening hook or attention grabber
- **Call to Action**: Any explicit CTA
- **Hashtags**: Any hashtags visible or mentioned

## Key Topics
Main topics and themes covered in the video (semicolon-separated list)

## Summary
Concise 2-4 sentence summary of the video content

## Characters
All characters with:
- Name/identifier and role
- Appearance description
- Key actions and emotions observed

## Props & Objects
Notable props/objects including:
- Description
- How they are used in the video

## Environment
- **Primary Setting**: Setting type, location description, lighting, color tone
- **Background Elements**: Notable background elements and their context

## Scenes
Scene-by-scene breakdown with:
- Time range (start-end)
- Setting and location
- Key actions occurring
- Notable props/objects

## Visual & Cinematographic Analysis
- **Camera Work**: Angles, movement, framing, focus techniques
- **Lighting Design**: Style, mood, direction
- **Color Grading**: Dominant colors, overall tone, contrast
- **Visual Effects**: Effects, overlays, filters, compositing
- **Graphics & Text**: Any graphics/text overlays and their style
- **Editing Style**: Pacing, transitions, rhythm

## Audio Analysis
- **Music**: Presence, genre, mood, tempo, instrumentation, prominence
- **Sound Effects**: Types and usage
- **Voice & Dialogue**: Voice characteristics, recording quality
- **Overall Mix**: Balance and quality assessment

## Content & Themes
- **Primary Subject**: Main subject of the video
- **Themes**: Key themes explored
- **Tone**: Overall tone (e.g., humorous, serious, inspirational)
- **Mood**: Emotional atmosphere
- **Genre/Category**: Content category
- **Target Audience**: Intended viewers
- **Purpose**: Goal of the video
- **Key Messages**: Main takeaways
- **Branding**: Brand mentions, logos, product placements

## Technical Quality
- **Video Quality**: Resolution, sharpness, exposure notes
- **Production Values**: Equipment level, post-production quality

## Overall Assessment
- **Summary**: 1-3 sentence overall assessment
- **Visual Style**: Description of the visual style
- **Emotional Impact**: Effect on the viewer
- **Memorability**: Rating (low/medium/high)
- **Strengths**: What works well
- **Areas for Improvement**: What could be better
- **Comparable References**: Similar content or styles

## Timeline
- **Intro**: Timestamp + description
- **Key Moments**: List with timestamps + descriptions
- **Climax**: Timestamp + description
- **Conclusion**: Timestamp + description

Output ONLY the markdown analysis, starting with ## Metadata."""


def load_prompt(prompt_file: str | None) -> str:
    if not prompt_file:
        return DEFAULT_ANALYSIS_PROMPT

    prompt_path = Path(prompt_file).expanduser().resolve()
    prompt = prompt_path.read_text(encoding="utf-8").strip()
    if not prompt:
        raise RuntimeError(f"Prompt file is empty: {prompt_path}")
    return prompt


def is_youtube_url(source: str) -> bool:
    hostname = (urlparse(source).hostname or "").lower()
    return any(domain in hostname for domain in ("youtube.com", "youtu.be"))


def get_local_duration_seconds(path: Path) -> float:
    result = subprocess.run(
        ["mdls", "-raw", "-name", "kMDItemDurationSeconds", str(path)],
        check=True,
        capture_output=True,
        text=True,
    )
    raw_value = result.stdout.strip()
    if not raw_value or raw_value == "(null)":
        raise RuntimeError(f"Could not determine duration for local video: {path}")
    return float(raw_value)


def get_youtube_duration_seconds(url: str) -> float:
    options = {
        "quiet": True,
        "no_warnings": True,
        "skip_download": True,
    }
    with YoutubeDL(options) as ydl:
        info = ydl.extract_info(url, download=False)
    duration = info.get("duration")
    if duration is None:
        raise RuntimeError(f"Could not determine YouTube duration for: {url}")
    return float(duration)


def validate_duration(source: str) -> float:
    if is_youtube_url(source):
        duration_seconds = get_youtube_duration_seconds(source)
    else:
        source_path = Path(source).expanduser().resolve()
        if not source_path.is_file():
            raise RuntimeError(f"Video file not found: {source_path}")
        duration_seconds = get_local_duration_seconds(source_path)

    if duration_seconds > MAX_DURATION_SECONDS:
        raise RuntimeError(
            f"Video is too long: {duration_seconds:.1f}s. Maximum supported duration is {MAX_DURATION_SECONDS:.0f}s."
        )

    return duration_seconds


def guess_mime_type(path: Path) -> str:
    mime_type, _ = mimetypes.guess_type(str(path))
    return mime_type or "video/mp4"


def wait_for_active_file(client: genai.Client, uploaded) -> object:
    deadline = time.time() + MAX_POLL_SECONDS
    current = uploaded

    while time.time() < deadline:
        state = getattr(current, "state", None)
        state_name = getattr(state, "name", str(state)) if state is not None else ""

        if state_name == "ACTIVE":
            return current
        if state_name == "FAILED":
            raise RuntimeError(f"Gemini file processing failed for {uploaded.name}.")

        time.sleep(POLL_INTERVAL_SECONDS)
        current = client.files.get(name=uploaded.name)

    raise RuntimeError(f"Timed out waiting for Gemini file {uploaded.name} to become ACTIVE.")


def analyze_youtube(source: str, prompt: str, model: str, client: genai.Client) -> str:
    response = client.models.generate_content(
        model=model,
        contents=types.Content(
            parts=[
                types.Part(file_data=types.FileData(file_uri=source)),
                types.Part(text=prompt),
            ]
        ),
    )
    if not response.text:
        raise RuntimeError("Gemini returned an empty response for the YouTube URL.")
    return response.text.strip() + "\n"


def analyze_local_file(source_path: Path, prompt: str, model: str, client: genai.Client) -> str:
    uploaded = client.files.upload(file=str(source_path), config={"mime_type": guess_mime_type(source_path)})
    uploaded = wait_for_active_file(client, uploaded)
    try:
        response = client.models.generate_content(
            model=model,
            contents=[uploaded, prompt],
        )
        if not response.text:
            raise RuntimeError("Gemini returned an empty response for the local video.")
        return response.text.strip() + "\n"
    finally:
        try:
            client.files.delete(name=uploaded.name)
        except Exception:
            pass


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Analyze a local video or public YouTube URL with Gemini and write markdown output.",
    )
    parser.add_argument("source", help="Local video path or public YouTube URL")
    parser.add_argument("output", help="Markdown output path")
    parser.add_argument("--prompt-file")
    parser.add_argument("--model", default=DEFAULT_MODEL)
    parser.add_argument("--api-key", default=os.environ.get("GEMINI_API_KEY"))
    return parser


def main() -> int:
    args = build_parser().parse_args()

    if not args.api_key:
        raise RuntimeError("Missing Gemini API key. Set GEMINI_API_KEY or pass --api-key.")

    output_path = Path(args.output).expanduser().resolve()
    output_path.parent.mkdir(parents=True, exist_ok=True)

    validate_duration(args.source)
    prompt = load_prompt(args.prompt_file)
    client = genai.Client(api_key=args.api_key)

    if is_youtube_url(args.source):
        markdown = analyze_youtube(args.source, prompt, args.model, client)
    else:
        markdown = analyze_local_file(Path(args.source).expanduser().resolve(), prompt, args.model, client)

    output_path.write_text(markdown, encoding="utf-8")
    print(str(output_path))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
