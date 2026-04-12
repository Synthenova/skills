---
name: shopify-store-manager
description: Initialize the current folder as a Shopify store workspace and maintain a structured local mirror of store data inside the repo. Use when Codex needs to bootstrap a store repo, organize products, collections, media, metafields, and metaobjects in a consistent layout, or keep exported store state current and easy to work with.
---

# Shopify Store Manager

Use this skill to turn the current folder into a Shopify store workspace with clear structure, stable export conventions, and a predictable local representation of store data.

## Workflow

1. Confirm the current folder is the intended store workspace.
2. Run `scripts/init-store-workspace.sh` from this skill to stamp the current folder with the standard directory layout.
3. Run the exporter from this skill to refresh store data into the target workspace.
4. Work from the exported workspace structure when inspecting products, collections, media, metafields, and metaobjects.
5. Refresh exported store data before making repo decisions that depend on current store state.

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
```

Use one folder per product handle under `products/`. Keep downloaded media under each product's `media/` directory. Keep collections one folder per collection handle under `collections/`. Keep metafield definitions separate from metafield values, and keep metaobject definitions separate from exported entries.

## Workspace Conventions

- Refresh store data into the repo before relying on exported state for decisions.
- Keep local files factual and derived from store state.
- Keep media metadata in `media.json` and actual files in `media/`.
- Preserve Shopify IDs, handles, URLs, alt text, ordering, and collection membership exactly as exported.
- Use the exporter modules in `assets/store-template/scripts/shopify-export/` when extending or patching workspace export behavior.

## Resources

### `scripts/init-store-workspace.sh`

Run this script from inside the skill to initialize any target folder:

```bash
/path/to/skill/scripts/init-store-workspace.sh /path/to/store-workspace
```

If no argument is provided, it initializes the current working directory.

### `assets/store-template/`

Contains the exporter entrypoint and modules used by the skill when writing store data into a target workspace.

### `references/workflow.md`

Read when you need the exact repo conventions for products, collections, media, and metadata exports.
