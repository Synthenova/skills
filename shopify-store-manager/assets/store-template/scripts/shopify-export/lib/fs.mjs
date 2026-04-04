import { mkdir, writeFile } from "node:fs/promises";
import path from "node:path";
import { REPO_ROOT } from "../config.mjs";

export function sanitizeFilename(value) {
  return value.replace(/[^a-zA-Z0-9._-]+/g, "_");
}

export async function writeJson(filePath, data) {
  await mkdir(path.dirname(filePath), { recursive: true });
  await writeFile(filePath, `${JSON.stringify(data, null, 2)}\n`, "utf8");
}

export function extensionFromContentType(contentType) {
  const normalized = contentType.split(";")[0].trim().toLowerCase();
  const map = {
    "image/jpeg": ".jpg",
    "image/png": ".png",
    "image/webp": ".webp",
    "image/gif": ".gif",
    "video/mp4": ".mp4",
    "model/gltf-binary": ".glb",
    "model/gltf+json": ".gltf",
  };
  return map[normalized] ?? ".bin";
}

export function extensionFromUrl(url) {
  try {
    const pathname = new URL(url).pathname;
    const ext = path.extname(pathname);
    return ext || null;
  } catch {
    return null;
  }
}

export function safeSegment(value) {
  return value.replace(/[^a-zA-Z0-9_-]+/g, "-").replace(/-+/g, "-").replace(/^-|-$/g, "");
}

export function productFolderPath(handle) {
  return path.join(REPO_ROOT, "products", sanitizeFilename(handle));
}

export function collectionFolderPath(handle) {
  return path.join(REPO_ROOT, "collections", sanitizeFilename(handle));
}

export async function downloadFile(url, destinationPath) {
  const response = await fetch(url);
  if (!response.ok) {
    throw new Error(`Failed to download file ${url}: ${response.status}`);
  }

  const bytes = new Uint8Array(await response.arrayBuffer());
  await mkdir(path.dirname(destinationPath), { recursive: true });
  await writeFile(destinationPath, bytes);

  return {
    contentType: response.headers.get("content-type"),
    size: bytes.byteLength,
  };
}
