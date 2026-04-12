import path from "node:path";
import { fileURLToPath } from "node:url";

export const SHOP = process.env.SHOPIFY_SHOP ?? null;
export const API_VERSION = process.env.SHOPIFY_API_VERSION ?? null;

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

function readArgValue(flags) {
  for (let index = 0; index < process.argv.length; index += 1) {
    if (flags.includes(process.argv[index])) {
      return process.argv[index + 1] ?? null;
    }
  }
  return null;
}

export const REPO_ROOT = path.resolve(
  readArgValue(["--project-root", "-p"]) ?? process.cwd(),
);

export const FALLBACK_OWNER_TYPES = [
  "ARTICLE",
  "BLOG",
  "COLLECTION",
  "COMPANY",
  "COMPANY_LOCATION",
  "CUSTOMER",
  "LOCATION",
  "MARKET",
  "ORDER",
  "PAGE",
  "PRODUCT",
  "PRODUCTVARIANT",
  "SHOP",
];

export function requireEnv(name, value) {
  if (!value) {
    throw new Error(`Missing required environment variable: ${name}`);
  }
  return value;
}

export function resolveShop(storeArg) {
  return requireEnv("SHOPIFY_SHOP or --store", storeArg ?? SHOP);
}
