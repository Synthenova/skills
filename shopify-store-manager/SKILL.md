---
name: shopify-store-manager
description: Initialize the current folder for any Shopify store and manage a Shopify store workspace with standard folders, reusable export scripts, and Admin GraphQL workflows. Use when Codex needs to bootstrap a new Shopify store repo, mirror live store data, export products, collections, media, metafields, or metaobjects, or keep a local store workspace aligned with Shopify as the source of truth.
---

# Shopify Store Manager

Use this skill to turn the current folder into a Shopify store workspace and manage it with Shopify Admin GraphQL.

## Workflow

1. Confirm the current folder is the intended store workspace.
2. Gather Shopify credentials from environment variables or local instructions such as `AGENTS.md`.
3. Run `scripts/init-store-workspace.sh` from this skill to stamp the current folder with the standard directory layout and exporter scripts.
4. Use the copied `scripts/export-shopify-metadata.mjs` entrypoint inside the target workspace to pull live store state into the repo.
5. Treat Shopify Admin as the source of truth at the start of every task. Re-fetch before making decisions about products, collections, media, metafields, or metaobjects.

## Standard Workspace

The bootstrap script creates this layout in the target folder:

```text
collections/
metafields/
  definitions/
  values/
metaobjects/
  definitions/
  entries/
products/
scripts/
  export-shopify-metadata.mjs
  shopify-export/
```

Use one folder per product handle under `products/`. Keep downloaded media under each product's `media/` directory. Keep collections one folder per collection handle under `collections/`.

## Credentials

Prefer environment variables:

```bash
export SHOPIFY_SHOP='your-store.myshopify.com'
export SHOPIFY_ACCESS_TOKEN='shpat_...'
```

or:

```bash
export SHOPIFY_SHOP='your-store.myshopify.com'
export SHOPIFY_CLIENT_ID='...'
export SHOPIFY_CLIENT_SECRET='...'
```

If credentials live in a local file such as `AGENTS.md`, read it carefully and use only the minimum needed values.

## Export Rules

- Always start from live Shopify data before modifying local JSON.
- Keep local files factual. Do not invent sync state like `pending_upload` or `synced`.
- Keep media metadata in `media.json` and actual files in `media/`.
- Preserve Shopify IDs, handles, URLs, alt text, ordering, and collection membership exactly as returned.
- Use the modular exporter in `scripts/shopify-export/` when you need to extend or patch behavior.

## Resources

### `scripts/init-store-workspace.sh`

Run this script from inside the skill to initialize any target folder:

```bash
/path/to/skill/scripts/init-store-workspace.sh /path/to/store-workspace
```

If no argument is provided, it initializes the current working directory.

### `assets/store-template/`

Contains the reusable exporter entrypoint and modules that get copied into the target workspace.

### `references/workflow.md`

Read when you need the exact repo conventions for products, collections, media, and metadata exports.
