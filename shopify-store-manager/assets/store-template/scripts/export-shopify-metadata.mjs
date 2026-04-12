#!/usr/bin/env node

import path from "node:path";
import { API_VERSION, REPO_ROOT, resolveShop } from "./shopify-export/config.mjs";
import { writeJson } from "./shopify-export/lib/fs.mjs";
import {
  exportMetafieldDefinitions,
  exportMetafieldValues,
  exportMetaobjects,
} from "./shopify-export/exporters/metadata.mjs";
import {
  exportCollections,
  exportProducts,
} from "./shopify-export/exporters/catalog.mjs";

function parseArgs(argv) {
  const options = { projectRoot: null, store: null };

  for (let index = 0; index < argv.length; index += 1) {
    const arg = argv[index];
    if (arg === "--project-root" || arg === "-p") {
      options.projectRoot = argv[index + 1] ?? null;
      index += 1;
      continue;
    }
    if (arg === "--store" || arg === "-s") {
      options.store = argv[index + 1] ?? null;
      index += 1;
    }
  }

  return options;
}

async function main() {
  const options = parseArgs(process.argv.slice(2));
  const shop = resolveShop(options.store);

  const [
    metafieldDefinitions,
    metafieldValues,
    metaobjects,
    products,
    collections,
  ] = await Promise.all([
    exportMetafieldDefinitions(shop),
    exportMetafieldValues(shop),
    exportMetaobjects(shop),
    exportProducts(shop),
    exportCollections(shop),
  ]);

  const summary = {
    exportedAt: new Date().toISOString(),
    shop,
    apiVersion: API_VERSION,
    projectRoot: REPO_ROOT,
    metafields: {
      definitions: metafieldDefinitions,
      values: metafieldValues,
    },
    metaobjects,
    products,
    collections,
  };

  await writeJson(path.join(REPO_ROOT, "shopify-metadata.snapshot.json"), summary);
  console.log(JSON.stringify(summary, null, 2));
}

main().catch((error) => {
  console.error(error instanceof Error ? error.message : String(error));
  process.exit(1);
});
