#!/usr/bin/env python3
from __future__ import annotations

import argparse
import importlib.util
import mimetypes
import os
import subprocess
import time
from pathlib import Path
from urllib.parse import urlparse

from google import genai
from google.genai import types
from yt_dlp import YoutubeDL


DEFAULT_PROMPT_FILE = Path("/Users/nirmal/Desktop/conthunt/backend/app/prompts/video_analysis.py")
DEFAULT_MODEL = "gemini-flash-lite-latest"
MAX_DURATION_SECONDS = 180.0
POLL_INTERVAL_SECONDS = 2.0
MAX_POLL_SECONDS = 120.0


def load_default_prompt(prompt_file: Path) -> str:
    spec = importlib.util.spec_from_file_location("video_analysis_prompt", prompt_file)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to load prompt file: {prompt_file}")

    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    prompt = getattr(module, "DEFAULT_ANALYSIS_PROMPT", None)
    if not isinstance(prompt, str) or not prompt.strip():
        raise RuntimeError(f"DEFAULT_ANALYSIS_PROMPT missing in {prompt_file}")
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
    parser.add_argument("--prompt-file", default=str(DEFAULT_PROMPT_FILE))
    parser.add_argument("--model", default=DEFAULT_MODEL)
    parser.add_argument("--api-key", default=os.environ.get("GEMINI_API_KEY"))
    return parser


def main() -> int:
    args = build_parser().parse_args()

    if not args.api_key:
        raise RuntimeError("Missing Gemini API key. Set GEMINI_API_KEY or pass --api-key.")

    prompt_file = Path(args.prompt_file).expanduser().resolve()
    output_path = Path(args.output).expanduser().resolve()
    output_path.parent.mkdir(parents=True, exist_ok=True)

    validate_duration(args.source)
    prompt = load_default_prompt(prompt_file)
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
