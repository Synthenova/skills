#!/usr/bin/env bash

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
TEMPLATE_ROOT="$SKILL_ROOT/assets/store-template"
TARGET_DIR="${1:-$PWD}"

mkdir -p "$TARGET_DIR"

mkdir -p \
  "$TARGET_DIR/products" \
  "$TARGET_DIR/collections" \
  "$TARGET_DIR/metafields/definitions" \
  "$TARGET_DIR/metafields/values" \
  "$TARGET_DIR/metaobjects/definitions" \
  "$TARGET_DIR/metaobjects/entries" \
  "$TARGET_DIR/scripts"

cp -R "$TEMPLATE_ROOT/scripts/." "$TARGET_DIR/scripts/"

if [[ ! -f "$TARGET_DIR/.gitignore" ]]; then
  cat > "$TARGET_DIR/.gitignore" <<'EOF'
.DS_Store
node_modules
**/node_modules

.env
.env.*

.cache
**/.cache

build
**/build

app/build
public/build
**/public/build
**/app/build

prisma/dev.sqlite
prisma/dev.sqlite-journal
**/prisma/dev.sqlite
**/prisma/dev.sqlite-journal
database.sqlite

.shopify/*
.shopify.lock
**/.shopify/*
**/.shopify.lock

.react-router/
**/.react-router/

extensions/*/dist
**/extensions/*/dist
EOF
fi

printf 'Initialized Shopify workspace in %s\n' "$TARGET_DIR"
