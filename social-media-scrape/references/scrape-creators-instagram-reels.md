# Scrape Creators Instagram Reels

Endpoint:

```text
GET https://api.scrapecreators.com/v1/instagram/user/reels
```

Authentication:

- Send the API key in the `x-api-key` header.
- For this skill, prefer `SCRAPE_CREATORS_API_KEY`.

Query parameters:

- `user_id` (optional): Instagram user id; preferred for faster responses
- `handle` (optional): Instagram handle
- `max_id` (optional): pagination cursor from the previous response
- `trim` (optional): boolean

Response structure:

- `items`: array of reel entries
- `items[].media.code`: reel shortcode
- `items[].media.play_count`: Instagram-only reel plays
- `items[].media.like_count`: like count
- `items[].media.comment_count`: comment count
- `items[].media.video_versions[]`: downloadable video variants and URLs
- `items[].media.display_uri`: thumbnail image URL
- `items[].media.owner` or `items[].media.user`: owner information
- `paging_info.max_id`: cursor for the next page
- `paging_info.more_available`: whether more pages exist
- `status`: API status

Usage notes:

- This endpoint does not return reel captions.
- Play counts exclude cross-posted Facebook views.
- Prefer `user_id` instead of `handle` when available.
- Paginate by passing `paging_info.max_id` back as `max_id`.
- For a main download URL, prefer the `video_versions[]` entry with the largest `width * height`.
- `display_uri` is the main thumbnail URL, but the skill's `--short` mode intentionally omits thumbnails.
