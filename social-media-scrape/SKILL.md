---
name: social-media-scrape
description: Search and fetch public social media data through supported scraping APIs. Use when Codex needs to collect TikTok search results by keyword, fetch Instagram user reels, inspect captions/authors/video metadata, paginate through result sets, or summarize public social media search output. Trigger this skill for requests about Scrape Creators, TikTok keyword search, Instagram reels, social media scraping helpers, or building/reusing scripts that call these endpoints.
---

# Social Media Scrape

Use the bundled script for live API calls instead of rewriting request code each time.

## Quick Start

1. Ensure `SCRAPE_CREATORS_API_KEY` is set.
2. Read the relevant reference file if you need parameter or response details.
3. Run one of:

```bash
python3 scripts/search_tiktok_keyword.py --query "kansas city chiefs"
python3 scripts/get_instagram_reels.py --handle "adrianhorning" --summary
```

## TikTok Keyword Search

Use `scripts/search_tiktok_keyword.py` for `GET /v1/tiktok/search/keyword`.

Common flags:

- `--query`: required keyword or phrase
- `--date-posted`: `yesterday`, `this-week`, `this-month`, `last-3-months`, `last-6-months`, or `all-time`
- `--sort-by`: `relevance`, `most-liked`, or `date-posted`
- `--region`: 2-letter country code such as `US`
- `--cursor`: pagination cursor from a previous response
- `--trim`: request trimmed API output
- `--limit`: cap how many items are printed locally
- `--sort-local`: reorder fetched results locally by `plays`, `likes`, `comments`, `shares`, or `newest`
- `--summary`: print a concise table instead of raw JSON
- `--short`: print compact JSON with text fields, hashtags, and the highest-quality video URL
- `--api-key`: override `SCRAPE_CREATORS_API_KEY` for one-off runs

Examples:

```bash
python3 scripts/search_tiktok_keyword.py --query "super bowl" --summary
python3 scripts/search_tiktok_keyword.py --query "super bowl" --sort-local likes --short --limit 3
python3 scripts/search_tiktok_keyword.py --query "super bowl" --short --limit 3
python3 scripts/search_tiktok_keyword.py --query "travel tips" --sort-by most-liked --date-posted this-month --limit 5 --summary
python3 scripts/search_tiktok_keyword.py --query "street food" --cursor 10 --trim
```

## Instagram Reels

Use `scripts/get_instagram_reels.py` for `GET /v1/instagram/user/reels`.

Pass either `--user-id` or `--handle`. Prefer `--user-id` when you already have it because the API responds faster.

Common flags:

- `--user-id`: Instagram user id
- `--handle`: Instagram handle
- `--max-id`: pagination cursor from a previous response
- `--trim`: request trimmed API output
- `--limit`: cap how many items are printed locally
- `--sort-local`: reorder fetched results locally by `plays`, `likes`, `comments`, or `newest`
- `--summary`: print a concise table instead of raw JSON
- `--short`: print compact JSON with available text fields and the highest-quality video URL
- `--api-key`: override `SCRAPE_CREATORS_API_KEY` for one-off runs

Examples:

```bash
python3 scripts/get_instagram_reels.py --handle "adrianhorning" --summary
python3 scripts/get_instagram_reels.py --handle "adrianhorning" --sort-local plays --short --limit 3
python3 scripts/get_instagram_reels.py --handle "adrianhorning" --short --limit 3
python3 scripts/get_instagram_reels.py --user-id "2700692569" --limit 5
python3 scripts/get_instagram_reels.py --user-id "2700692569" --max-id "QVFC..." --trim --summary
```

## Working Rules

- Prefer the environment variable over hardcoding API keys.
- Keep the raw JSON when downstream work needs full `aweme_info`, `statistics`, `video`, or `author` fields.
- Use `--summary` only when the user wants a quick readout.
- Use `--short` when the user wants only essential text fields plus a main high-quality video URL.
- Use `--sort-local` when the API does not expose the ranking you want, or when you want a different local presentation of the fetched page.
- Preserve and reuse the response `cursor` when fetching additional pages.
- Treat region as proxy placement, not a strict content filter.
- Instagram reels do not include captions from this endpoint; do not promise them in summaries.
- Preserve and reuse `paging_info.max_id` when fetching additional Instagram reels pages.
- Prefer `user_id` over `handle` for Instagram when both are available.
- For main video selection, choose the video variant with the largest `width * height`; if dimensions are missing, fall back to the last best URL seen.
- For Instagram, omit thumbnails from `--short`; for TikTok, keep text plus the selected video URL only.

## References

- Read `references/scrape-creators-tiktok-keyword.md` for endpoint details, parameter values, and response structure.
- Read `references/scrape-creators-instagram-reels.md` for Instagram reels parameters, paging fields, and response structure.
