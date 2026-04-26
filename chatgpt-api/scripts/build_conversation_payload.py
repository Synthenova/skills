#!/usr/bin/env python3
"""Build ChatGPT web backend conversation payloads.

The attached-image schema is confirmed from live ChatGPT web traffic.
The plain-text shape is supported as a convenience path and may need
refreshing from live browser traffic if ChatGPT changes its frontend.
"""

from __future__ import annotations

import argparse
import json
import uuid
from datetime import datetime


def current_timezone() -> tuple[str, int]:
    now = datetime.now().astimezone()
    offset = now.utcoffset()
    if offset is None:
        return "UTC", 0
    # ChatGPT web used negative minutes for Asia/Calcutta (-330).
    return str(now.tzinfo or "UTC"), -int(offset.total_seconds() // 60)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Build ChatGPT web backend payload JSON.")
    parser.add_argument("--prompt", required=True, help="User prompt text.")
    parser.add_argument(
        "--content-type",
        choices=["multimodal_text", "text"],
        default="multimodal_text",
        help="Message content type. Use multimodal_text for confirmed attached-image sends.",
    )
    parser.add_argument("--file-id", help="Uploaded ChatGPT file id, e.g. file_000...")
    parser.add_argument("--file-name", default="upload.png", help="Original uploaded filename.")
    parser.add_argument("--mime-type", default="image/png", help="Uploaded file MIME type.")
    parser.add_argument("--file-size", type=int, help="Uploaded file size in bytes.")
    parser.add_argument("--width", type=int, help="Uploaded image width.")
    parser.add_argument("--height", type=int, help="Uploaded image height.")
    parser.add_argument("--parent-message-id", default="client-created-root")
    parser.add_argument("--model", default="gpt-5-5-thinking")
    parser.add_argument("--message-id", default=str(uuid.uuid4()))
    parser.add_argument("--timezone", help="Timezone name. Defaults to local timezone.")
    parser.add_argument("--timezone-offset-min", type=int, help="Timezone offset in ChatGPT web format.")
    parser.add_argument("--thinking-effort", default="extended")
    parser.add_argument("--dark-mode", action="store_true", default=True)
    parser.add_argument("--light-mode", action="store_true", help="Override dark mode.")
    parser.add_argument("--page-height", type=int, default=1012)
    parser.add_argument("--page-width", type=int, default=1914)
    parser.add_argument("--pixel-ratio", type=int, default=1)
    parser.add_argument("--screen-height", type=int, default=1080)
    parser.add_argument("--screen-width", type=int, default=1920)
    parser.add_argument("--app-name", default="chatgpt.com")
    parser.add_argument("--time-since-loaded", type=int, default=1500)
    return parser


def build_payload(args: argparse.Namespace) -> dict:
    timezone_name, timezone_offset = current_timezone()
    if args.timezone:
        timezone_name = args.timezone
    if args.timezone_offset_min is not None:
        timezone_offset = args.timezone_offset_min

    parts: list[object]
    attachments: list[dict]

    if args.file_id:
        required = {
            "--file-size": args.file_size,
            "--width": args.width,
            "--height": args.height,
        }
        missing = [flag for flag, value in required.items() if value is None]
        if missing:
            raise SystemExit(f"Missing required arguments with --file-id: {', '.join(missing)}")
        parts = [
            {
                "content_type": "image_asset_pointer",
                "asset_pointer": f"sediment://{args.file_id}",
                "size_bytes": args.file_size,
                "width": args.width,
                "height": args.height,
            },
            args.prompt,
        ]
        attachments = [
            {
                "id": args.file_id,
                "size": args.file_size,
                "name": args.file_name,
                "mime_type": args.mime_type,
                "width": args.width,
                "height": args.height,
                "source": "local",
                "is_big_paste": False,
            }
        ]
        content_type = "multimodal_text"
    else:
        parts = [args.prompt]
        attachments = []
        content_type = args.content_type

    return {
        "action": "next",
        "messages": [
            {
                "id": args.message_id,
                "author": {"role": "user"},
                "create_time": datetime.now().timestamp(),
                "content": {
                    "content_type": content_type,
                    "parts": parts,
                },
                "metadata": {
                    "attachments": attachments,
                    "developer_mode_connector_ids": [],
                    "selected_sources": [],
                    "selected_github_repos": [],
                    "selected_all_github_repos": False,
                    "serialization_metadata": {"custom_symbol_offsets": []},
                },
            }
        ],
        "parent_message_id": args.parent_message_id,
        "model": args.model,
        "client_prepare_state": "success",
        "timezone_offset_min": timezone_offset,
        "timezone": timezone_name,
        "conversation_mode": {"kind": "primary_assistant"},
        "enable_message_followups": True,
        "system_hints": [],
        "supports_buffering": True,
        "supported_encodings": ["v1"],
        "client_contextual_info": {
            "is_dark_mode": False if args.light_mode else args.dark_mode,
            "time_since_loaded": args.time_since_loaded,
            "page_height": args.page_height,
            "page_width": args.page_width,
            "pixel_ratio": args.pixel_ratio,
            "screen_height": args.screen_height,
            "screen_width": args.screen_width,
            "app_name": args.app_name,
        },
        "paragen_cot_summary_display_override": "allow",
        "force_parallel_switch": "auto",
        "thinking_effort": args.thinking_effort,
    }


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    payload = build_payload(args)
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()
