# Captured request bodies

## Confirmed attached-image message body

This exact structure was captured from a live ChatGPT web send with an uploaded image and non-empty prompt:

```json
{
  "action": "next",
  "messages": [
    {
      "id": "922e7d1c-2bd0-4e6f-a8c9-3454d1308abc",
      "author": { "role": "user" },
      "create_time": 1777244874.282,
      "content": {
        "content_type": "multimodal_text",
        "parts": [
          {
            "content_type": "image_asset_pointer",
            "asset_pointer": "sediment://file_000000003980720bb63e604b34691383",
            "size_bytes": 52866,
            "width": 1914,
            "height": 1012
          },
          "Use this uploaded image as a reference and generate a high-contrast editorial poster version."
        ]
      },
      "metadata": {
        "attachments": [
          {
            "id": "file_000000003980720bb63e604b34691383",
            "size": 52866,
            "name": "upload-valid.png",
            "mime_type": "image/png",
            "width": 1914,
            "height": 1012,
            "source": "local",
            "is_big_paste": false
          }
        ],
        "developer_mode_connector_ids": [],
        "selected_sources": [],
        "selected_github_repos": [],
        "selected_all_github_repos": false,
        "serialization_metadata": {
          "custom_symbol_offsets": []
        }
      }
    }
  ],
  "parent_message_id": "client-created-root",
  "model": "gpt-5-5-thinking",
  "client_prepare_state": "success",
  "timezone_offset_min": -330,
  "timezone": "Asia/Calcutta",
  "conversation_mode": {
    "kind": "primary_assistant"
  },
  "enable_message_followups": true,
  "system_hints": [],
  "supports_buffering": true,
  "supported_encodings": ["v1"],
  "client_contextual_info": {
    "is_dark_mode": true,
    "time_since_loaded": 1683,
    "page_height": 1012,
    "page_width": 1914,
    "pixel_ratio": 1,
    "screen_height": 1080,
    "screen_width": 1920,
    "app_name": "chatgpt.com"
  },
  "paragen_cot_summary_display_override": "allow",
  "force_parallel_switch": "auto",
  "thinking_effort": "extended"
}
```

## Attachment schema

The uploaded image appears twice:

1. In `content.parts[0]` as the transport pointer ChatGPT sends with the prompt
2. In `metadata.attachments[0]` as descriptive file metadata

Reduced schema:

```json
{
  "content": {
    "content_type": "multimodal_text",
    "parts": [
      {
        "content_type": "image_asset_pointer",
        "asset_pointer": "sediment://file_<id>",
        "size_bytes": 52866,
        "width": 1914,
        "height": 1012
      },
      "<prompt text>"
    ]
  },
  "metadata": {
    "attachments": [
      {
        "id": "file_<id>",
        "size": 52866,
        "name": "upload-valid.png",
        "mime_type": "image/png",
        "width": 1914,
        "height": 1012,
        "source": "local",
        "is_big_paste": false
      }
    ]
  }
}
```

## Practical meaning

- `asset_pointer` is what links the message content to the uploaded ChatGPT file.
- `parts[1]` is the actual human prompt string.
- `attachments` preserves the original browser-side file metadata.

## Plain text notes

This skill includes a text-only builder path, but the strongest guarantee is on the attached-image schema above because it was captured directly from live traffic.
