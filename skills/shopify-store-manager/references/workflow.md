# Shopify Store Workspace

## Product Folder

Each product lives in a folder named after the product handle:

```text
products/<product-handle>/
  product.json
  variants.json
  collections.json
  metafields.json
  media.json
  media/
```

`product.json` stores the main product record.

`variants.json` stores all variants for that product.

`collections.json` stores collection membership references.

`metafields.json` stores product-level metafields.

`media.json` stores Shopify media metadata and local file mappings.

`media/` stores downloaded media assets.

## Collection Folder

Each collection lives in a folder named after the collection handle:

```text
collections/<collection-handle>/
  collection.json
  products.json
  metafields.json
  media.json
  media/
```

## Global Metadata Folders

```text
metafields/
  definitions/
  values/
metaobjects/
  definitions/
  entries/
```

These folders hold global store-level snapshots.

## Source Of Truth

Shopify Admin API is always the source of truth at the beginning of the task.

The local repo is a structured mirror plus local assets. Re-fetch before planning changes.
