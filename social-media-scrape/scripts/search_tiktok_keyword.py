#!/usr/bin/env python3
"""Search TikTok videos by keyword via Scrape Creators."""

from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request
from typing import Any


BASE_URL = "https://api.scrapecreators.com/v1/tiktok/search/keyword"
DATE_POSTED_VALUES = {
    "yesterday",
    "this-week",
    "this-month",
    "last-3-months",
    "last-6-months",
    "all-time",
}
SORT_BY_VALUES = {"relevance", "most-liked", "date-posted"}
LOCAL_SORT_VALUES = {"plays", "likes", "comments", "shares", "newest"}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Search TikTok videos by keyword using the Scrape Creators API."
    )
    parser.add_argument("--query", required=True, help="Keyword or phrase to search for.")
    parser.add_argument("--date-posted", choices=sorted(DATE_POSTED_VALUES))
    parser.add_argument("--sort-by", choices=sorted(SORT_BY_VALUES))
    parser.add_argument("--region", help="Optional 2-letter region code such as US or GB.")
    parser.add_argument("--cursor", type=int, help="Pagination cursor from a previous response.")
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
        help="Print a compact JSON view with text fields, hashtags, and the best video URL.",
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
        help="Reorder fetched results locally by plays, likes, comments, shares, or newest.",
    )
    parser.add_argument(
        "--api-key",
        help="API key override. Defaults to SCRAPE_CREATORS_API_KEY.",
    )
    return parser.parse_args()


def build_url(args: argparse.Namespace) -> str:
    params: dict[str, Any] = {"query": args.query}
    if args.date_posted:
        params["date_posted"] = args.date_posted
    if args.sort_by:
        params["sort_by"] = args.sort_by
    if args.region:
        params["region"] = args.region
    if args.cursor is not None:
        params["cursor"] = args.cursor
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
    aweme = item.get("aweme_info") or {}
    author = aweme.get("author") or {}
    stats = aweme.get("statistics") or {}
    desc = (aweme.get("desc") or "").replace("\n", " ").strip()
    if len(desc) > 120:
        desc = desc[:117] + "..."
    username = author.get("unique_id") or author.get("nickname") or "unknown"
    aweme_id = aweme.get("aweme_id") or "unknown"
    plays = stats.get("play_count", 0)
    likes = stats.get("digg_count", 0)
    comments = stats.get("comment_count", 0)
    shares = stats.get("share_count", 0)
    url = aweme.get("url") or aweme.get("share_url") or ""
    return (
        f"{index}. @{username} | aweme_id={aweme_id} | plays={plays} | "
        f"likes={likes} | comments={comments} | shares={shares}\n"
        f"   {desc}\n"
        f"   {url}"
    )


def choose_best_url_candidate(candidates: list[dict[str, Any]]) -> str:
    best_url = ""
    best_score = -1
    for candidate in candidates:
        if not isinstance(candidate, dict):
            continue
        width = candidate.get("width") or 0
        height = candidate.get("height") or 0
        score = width * height
        url_source = candidate.get("play_addr") or candidate.get("download_addr") or {}
        if not isinstance(url_source, dict):
            url_source = {}
        url_list = url_source.get("url_list") or []
        url = url_list[0] if url_list else ""
        if url and score >= best_score:
            best_score = score
            best_url = url
    return best_url


def build_short_item(item: dict[str, Any]) -> dict[str, Any]:
    aweme = item.get("aweme_info") or {}
    author = aweme.get("author") or {}
    stats = aweme.get("statistics") or {}
    hashtags = []
    for entry in aweme.get("text_extra") or []:
        if isinstance(entry, dict) and entry.get("type") == 1 and entry.get("hashtag_name"):
            hashtags.append(entry["hashtag_name"])

    video = aweme.get("video") or {}
    video_candidates = []
    for bit_rate in video.get("bit_rate") or []:
        if isinstance(bit_rate, dict):
            video_candidates.append(bit_rate)
    for fallback_key in ("play_addr_h264", "play_addr_bytevc1", "play_addr", "download_no_watermark_addr", "download_addr"):
        fallback = video.get(fallback_key)
        if isinstance(fallback, dict):
            video_candidates.append(
                {
                    "width": video.get("width") or 0,
                    "height": video.get("height") or 0,
                    "play_addr": fallback,
                }
            )

    best_video_url = choose_best_url_candidate(video_candidates)

    return {
        "aweme_id": aweme.get("aweme_id"),
        "url": aweme.get("url") or aweme.get("share_url"),
        "author": {
            "username": author.get("unique_id"),
            "nickname": author.get("nickname"),
            "id": author.get("uid"),
        },
        "text": {
            "caption": aweme.get("desc"),
            "hashtags": hashtags,
            "search_desc": aweme.get("search_desc"),
        },
        "stats": {
            "play_count": stats.get("play_count"),
            "digg_count": stats.get("digg_count"),
            "comment_count": stats.get("comment_count"),
            "share_count": stats.get("share_count"),
        },
        "video": {
            "best_url": best_video_url,
            "duration_ms": video.get("duration"),
            "width": video.get("width"),
            "height": video.get("height"),
        },
    }


def print_short(payload: dict[str, Any], limit: int) -> None:
    items = payload.get("search_item_list") or []
    output = {
        "cursor": payload.get("cursor"),
        "items": [build_short_item(item) for item in items[:limit]],
    }
    json.dump(output, sys.stdout, indent=2, ensure_ascii=True)
    sys.stdout.write("\n")


def print_summary(payload: dict[str, Any], limit: int) -> None:
    items = payload.get("search_item_list") or []
    cursor = payload.get("cursor")
    print(f"cursor: {cursor}")
    print(f"items: {len(items)}")
    print()
    for index, item in enumerate(items[:limit], start=1):
        print(summarize_item(item, index))
        print()


def tiktok_sort_key(item: dict[str, Any], mode: str) -> int:
    aweme = item.get("aweme_info") or {}
    stats = aweme.get("statistics") or {}
    if mode == "plays":
        return stats.get("play_count") or 0
    if mode == "likes":
        return stats.get("digg_count") or 0
    if mode == "comments":
        return stats.get("comment_count") or 0
    if mode == "shares":
        return stats.get("share_count") or 0
    if mode == "newest":
        return aweme.get("create_time") or 0
    return 0


def maybe_sort_payload(payload: dict[str, Any], mode: str | None) -> dict[str, Any]:
    if not mode:
        return payload
    items = payload.get("search_item_list")
    if not isinstance(items, list):
        return payload
    sorted_payload = dict(payload)
    sorted_payload["search_item_list"] = sorted(
        items,
        key=lambda item: tiktok_sort_key(item, mode),
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

    items = payload.get("search_item_list")
    if isinstance(items, list) and len(items) > args.limit:
        payload = dict(payload)
        payload["search_item_list"] = items[: args.limit]
        payload["truncated"] = True
    json.dump(payload, sys.stdout, indent=2, ensure_ascii=True)
    sys.stdout.write("\n")


if __name__ == "__main__":
    main()
