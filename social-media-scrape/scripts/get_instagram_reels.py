#!/usr/bin/env python3
"""Fetch Instagram reels for a public user via Scrape Creators."""

from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request
from typing import Any


BASE_URL = "https://api.scrapecreators.com/v1/instagram/user/reels"
LOCAL_SORT_VALUES = {"plays", "likes", "comments", "newest"}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Fetch public Instagram reels for a user using the Scrape Creators API."
    )
    parser.add_argument("--user-id", help="Instagram user id. Preferred for faster responses.")
    parser.add_argument("--handle", help="Instagram handle.")
    parser.add_argument("--max-id", help="Pagination cursor from a previous response.")
    parser.add_argument(
        "--trim",
        action="store_true",
        help="Request a trimmed response from the API.",
    )
    parser.add_argument(
        "--summary",
        action="store_true",
        help="Print a concise summary instead of full JSON.",
    )
    parser.add_argument(
        "--short",
        action="store_true",
        help="Print a compact JSON view with available text fields and the best video URL.",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=10,
        help="Maximum number of items to print locally. Default: 10.",
    )
    parser.add_argument(
        "--sort-local",
        choices=sorted(LOCAL_SORT_VALUES),
        help="Reorder fetched results locally by plays, likes, comments, or newest.",
    )
    parser.add_argument(
        "--api-key",
        help="API key override. Defaults to SCRAPE_CREATORS_API_KEY.",
    )
    args = parser.parse_args()
    if not args.user_id and not args.handle:
        parser.error("pass either --user-id or --handle")
    return args


def build_url(args: argparse.Namespace) -> str:
    params: dict[str, Any] = {}
    if args.user_id:
        params["user_id"] = args.user_id
    if args.handle:
        params["handle"] = args.handle
    if args.max_id:
        params["max_id"] = args.max_id
    if args.trim:
        params["trim"] = "true"
    return f"{BASE_URL}?{urllib.parse.urlencode(params)}"


def fetch_json(url: str, api_key: str) -> dict[str, Any]:
    request = urllib.request.Request(
        url,
        headers={
            "x-api-key": api_key,
            "accept": "application/json",
            "user-agent": "social-media-scrape-skill/1.0",
        },
        method="GET",
    )
    try:
        with urllib.request.urlopen(request, timeout=60) as response:
            body = response.read().decode("utf-8")
    except urllib.error.HTTPError as exc:
        details = exc.read().decode("utf-8", errors="replace")
        raise SystemExit(f"HTTP {exc.code}: {details}") from exc
    except urllib.error.URLError as exc:
        raise SystemExit(f"Request failed: {exc.reason}") from exc

    try:
        payload = json.loads(body)
    except json.JSONDecodeError as exc:
        raise SystemExit(f"Response was not valid JSON: {exc}") from exc

    if not isinstance(payload, dict):
        raise SystemExit("Unexpected response type: expected a JSON object.")
    return payload


def summarize_item(item: dict[str, Any], index: int) -> str:
    media = item.get("media") or {}
    owner = media.get("owner") or media.get("user") or {}
    video_versions = media.get("video_versions") or []
    video_url = ""
    if video_versions and isinstance(video_versions, list):
        first_version = video_versions[0] or {}
        video_url = first_version.get("url") or ""
    shortcode = media.get("code") or "unknown"
    username = owner.get("username") or "unknown"
    play_count = media.get("play_count")
    if play_count is None:
        play_count = media.get("ig_play_count", 0)
    like_count = media.get("like_count", 0)
    comment_count = media.get("comment_count", 0)
    display_uri = media.get("display_uri") or ""
    return (
        f"{index}. @{username} | shortcode={shortcode} | plays={play_count} | "
        f"likes={like_count} | comments={comment_count}\n"
        f"   thumb: {display_uri}\n"
        f"   video: {video_url}"
    )


def choose_best_video_version(video_versions: list[dict[str, Any]]) -> dict[str, Any]:
    best: dict[str, Any] = {}
    best_score = -1
    for version in video_versions:
        if not isinstance(version, dict):
            continue
        width = version.get("width") or 0
        height = version.get("height") or 0
        score = width * height
        if version.get("url") and score >= best_score:
            best_score = score
            best = version
    return best


def build_short_item(item: dict[str, Any]) -> dict[str, Any]:
    media = item.get("media") or {}
    owner = media.get("owner") or media.get("user") or {}
    clips_metadata = media.get("clips_metadata") or {}
    best_video = choose_best_video_version(media.get("video_versions") or [])
    return {
        "shortcode": media.get("code"),
        "url": media.get("url"),
        "owner": {
            "username": owner.get("username"),
            "full_name": owner.get("full_name"),
            "id": owner.get("id"),
        },
        "text": {
            "caption": None,
            "reusable_text": clips_metadata.get("reusable_text_attribute_string"),
        },
        "stats": {
            "play_count": media.get("play_count"),
            "like_count": media.get("like_count"),
            "comment_count": media.get("comment_count"),
        },
        "video": {
            "best_url": best_video.get("url"),
            "width": best_video.get("width"),
            "height": best_video.get("height"),
            "duration_s": media.get("video_duration"),
        },
    }


def print_short(payload: dict[str, Any], limit: int) -> None:
    items = payload.get("items") or []
    paging_info = payload.get("paging_info") or {}
    output = {
        "status": payload.get("status"),
        "paging_info": {
            "max_id": paging_info.get("max_id"),
            "more_available": paging_info.get("more_available"),
        },
        "items": [build_short_item(item) for item in items[:limit]],
    }
    json.dump(output, sys.stdout, indent=2, ensure_ascii=True)
    sys.stdout.write("\n")


def print_summary(payload: dict[str, Any], limit: int) -> None:
    items = payload.get("items") or []
    paging_info = payload.get("paging_info") or {}
    print(f"status: {payload.get('status')}")
    print(f"max_id: {paging_info.get('max_id')}")
    print(f"more_available: {paging_info.get('more_available')}")
    print(f"items: {len(items)}")
    print()
    for index, item in enumerate(items[:limit], start=1):
        print(summarize_item(item, index))
        print()


def instagram_sort_key(item: dict[str, Any], mode: str) -> int:
    media = item.get("media") or {}
    if mode == "plays":
        return media.get("play_count") or media.get("ig_play_count") or 0
    if mode == "likes":
        return media.get("like_count") or 0
    if mode == "comments":
        return media.get("comment_count") or 0
    if mode == "newest":
        return media.get("taken_at") or 0
    return 0


def maybe_sort_payload(payload: dict[str, Any], mode: str | None) -> dict[str, Any]:
    if not mode:
        return payload
    items = payload.get("items")
    if not isinstance(items, list):
        return payload
    sorted_payload = dict(payload)
    sorted_payload["items"] = sorted(
        items,
        key=lambda item: instagram_sort_key(item, mode),
        reverse=True,
    )
    return sorted_payload


def main() -> None:
    args = parse_args()
    if args.limit < 1:
        raise SystemExit("--limit must be at least 1.")

    api_key = args.api_key or os.environ.get("SCRAPE_CREATORS_API_KEY")
    if not api_key:
        raise SystemExit("Missing API key. Set SCRAPE_CREATORS_API_KEY or pass --api-key.")

    payload = maybe_sort_payload(fetch_json(build_url(args), api_key), args.sort_local)
    if args.short:
        print_short(payload, args.limit)
        return
    if args.summary:
        print_summary(payload, args.limit)
        return

    items = payload.get("items")
    if isinstance(items, list) and len(items) > args.limit:
        payload = dict(payload)
        payload["items"] = items[: args.limit]
        payload["truncated"] = True
    json.dump(payload, sys.stdout, indent=2, ensure_ascii=True)
    sys.stdout.write("\n")


if __name__ == "__main__":
    main()
