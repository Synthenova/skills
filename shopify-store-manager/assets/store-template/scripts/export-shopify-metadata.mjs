#!/usr/bin/env node

import path from "node:path";
import { API_VERSION, REPO_ROOT, SHOP, requireEnv } from "./shopify-export/config.mjs";
import { getAccessToken } from "./shopify-export/lib/api.mjs";
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

async function main() {
  requireEnv("SHOPIFY_SHOP", SHOP);
  const accessToken = await getAccessToken();

  const [
    metafieldDefinitions,
    metafieldValues,
    metaobjects,
    products,
    collections,
  ] = await Promise.all([
    exportMetafieldDefinitions(accessToken),
    exportMetafieldValues(accessToken),
    exportMetaobjects(accessToken),
    exportProducts(accessToken),
    exportCollections(accessToken),
  ]);

  const summary = {
    exportedAt: new Date().toISOString(),
    shop: SHOP,
    apiVersion: API_VERSION,
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
