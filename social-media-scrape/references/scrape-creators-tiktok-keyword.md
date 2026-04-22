# Scrape Creators TikTok Keyword Search

Endpoint:

```text
GET https://api.scrapecreators.com/v1/tiktok/search/keyword
```

Authentication:

- Send the API key in the `x-api-key` header.
- For this skill, prefer `SCRAPE_CREATORS_API_KEY`.

Query parameters:

- `query` (required): keyword or phrase
- `date_posted` (optional): `yesterday`, `this-week`, `this-month`, `last-3-months`, `last-6-months`, `all-time`
- `sort_by` (optional): `relevance`, `most-liked`, `date-posted`
- `region` (optional): proxy region, 2-letter country code such as `US`, `GB`, `FR`
- `cursor` (optional): number from the previous response for pagination
- `trim` (optional): boolean

Primary response fields:

- `cursor`: pagination cursor for the next request
- `search_item_list`: array of search results
- `search_item_list[].aweme_info.aweme_id`: TikTok video id
- `search_item_list[].aweme_info.desc`: caption text
- `search_item_list[].aweme_info.statistics`: engagement metrics including `play_count`, `digg_count`, `comment_count`, `share_count`
- `search_item_list[].aweme_info.video`: video metadata and playback URLs
- `search_item_list[].aweme_info.author`: author profile fields
- `search_item_list[].aweme_info.url` or `share_url`: TikTok URL when present

Usage notes:

- Paginate by passing the returned `cursor` back into the next request.
- `region` influences proxy geography and does not guarantee a strict region-only filter.
- Use trimmed responses when the user only needs the main fields; use full responses when downstream extraction needs nested media metadata.
- For a main download URL, prefer the video variant with the largest `width * height` among the available playback/download candidates.
- The skill's `--short` mode keeps text fields such as caption and hashtags plus the selected main video URL.
