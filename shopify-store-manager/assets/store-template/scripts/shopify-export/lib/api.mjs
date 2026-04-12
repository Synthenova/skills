import { execFile } from "node:child_process";
import { mkdtemp, readFile, rm } from "node:fs/promises";
import os from "node:os";
import path from "node:path";
import { promisify } from "node:util";
import { API_VERSION } from "../config.mjs";

const execFileAsync = promisify(execFile);

export async function graphql(query, variables = {}, shop) {
  const outputDir = await mkdtemp(path.join(os.tmpdir(), "shopify-store-manager-"));
  const outputFile = path.join(outputDir, "result.json");

  const args = [
    "store",
    "execute",
    "--store",
    shop,
    "--query",
    query,
    "--json",
    "--output-file",
    outputFile,
    "--version",
    API_VERSION,
  ];

  if (Object.keys(variables).length > 0) {
    args.push("--variables", JSON.stringify(variables));
  }

  try {
    await execFileAsync("shopify", args, {
      maxBuffer: 10 * 1024 * 1024,
    });

    const payloadText = await readFile(outputFile, "utf8");
    return JSON.parse(payloadText);
  } catch (error) {
    const stdout = error?.stdout ? `\nSTDOUT:\n${error.stdout}` : "";
    const stderr = error?.stderr ? `\nSTDERR:\n${error.stderr}` : "";
    throw new Error(`Shopify CLI execution failed.${stdout}${stderr}`);
  } finally {
    await rm(outputDir, { recursive: true, force: true });
  }
}

function getConnection(data, key) {
  const connection = data?.[key];
  if (!connection || !Array.isArray(connection.edges)) {
    throw new Error(`Missing connection data for "${key}"`);
  }
  return connection;
}

export async function paginateConnection(query, key, variables, shop) {
  const nodes = [];
  let after = null;

  while (true) {
    const data = await graphql(query, { ...variables, after }, shop);
    const connection = getConnection(data, key);

    nodes.push(...connection.edges.map((edge) => edge.node));

    if (!connection.pageInfo?.hasNextPage) {
      break;
    }

    after = connection.pageInfo.endCursor;
  }

  return nodes;
}
