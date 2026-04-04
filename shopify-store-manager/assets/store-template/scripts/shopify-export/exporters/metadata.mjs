import path from "node:path";
import { API_VERSION, FALLBACK_OWNER_TYPES, REPO_ROOT, SHOP } from "../config.mjs";
import { graphql, paginateConnection } from "../lib/api.mjs";
import { sanitizeFilename, writeJson } from "../lib/fs.mjs";

const RESOURCE_EXPORTS = [
  {
    fileName: "SHOP.json",
    rootKey: "shop",
    query: `
      query GetShopMetafields {
        shop {
          id
          name
          metafields(first: 250) {
            edges {
              node {
                id
                namespace
                key
                type
                value
                definition {
                  id
                  name
                }
              }
            }
          }
        }
      }
    `,
    normalize(data) {
      const shop = data.shop;
      return {
        resourceType: "SHOP",
        count: shop.metafields.edges.length,
        resources: [
          {
            id: shop.id,
            title: shop.name,
            metafields: shop.metafields.edges.map((edge) => edge.node),
          },
        ],
      };
    },
  },
  {
    fileName: "PRODUCT.json",
    rootKey: "products",
    query: `
      query GetProductMetafields($after: String) {
        products(first: 250, after: $after) {
          pageInfo {
            hasNextPage
            endCursor
          }
          edges {
            node {
              id
              title
              handle
              updatedAt
              metafields(first: 250) {
                edges {
                  node {
                    id
                    namespace
                    key
                    type
                    value
                    definition {
                      id
                      name
                    }
                  }
                }
              }
            }
          }
        }
      }
    `,
    title(node) {
      return node.title;
    },
  },
  {
    fileName: "PRODUCTVARIANT.json",
    rootKey: "productVariants",
    query: `
      query GetProductVariantMetafields($after: String) {
        productVariants(first: 250, after: $after) {
          pageInfo {
            hasNextPage
            endCursor
          }
          edges {
            node {
              id
              title
              sku
              updatedAt
              product {
                id
                title
              }
              metafields(first: 250) {
                edges {
                  node {
                    id
                    namespace
                    key
                    type
                    value
                    definition {
                      id
                      name
                    }
                  }
                }
              }
            }
          }
        }
      }
    `,
    title(node) {
      return `${node.product?.title ?? "Unknown Product"} / ${node.title}`;
    },
  },
  {
    fileName: "COLLECTION.json",
    rootKey: "collections",
    query: `
      query GetCollectionMetafields($after: String) {
        collections(first: 250, after: $after) {
          pageInfo {
            hasNextPage
            endCursor
          }
          edges {
            node {
              id
              title
              handle
              updatedAt
              metafields(first: 250) {
                edges {
                  node {
                    id
                    namespace
                    key
                    type
                    value
                    definition {
                      id
                      name
                    }
                  }
                }
              }
            }
          }
        }
      }
    `,
    title(node) {
      return node.title;
    },
  },
  {
    fileName: "PAGE.json",
    rootKey: "pages",
    query: `
      query GetPageMetafields($after: String) {
        pages(first: 250, after: $after) {
          pageInfo {
            hasNextPage
            endCursor
          }
          edges {
            node {
              id
              title
              handle
              updatedAt
              metafields(first: 250) {
                edges {
                  node {
                    id
                    namespace
                    key
                    type
                    value
                    definition {
                      id
                      name
                    }
                  }
                }
              }
            }
          }
        }
      }
    `,
    title(node) {
      return node.title;
    },
  },
  {
    fileName: "BLOG.json",
    rootKey: "blogs",
    query: `
      query GetBlogMetafields($after: String) {
        blogs(first: 250, after: $after) {
          pageInfo {
            hasNextPage
            endCursor
          }
          edges {
            node {
              id
              title
              handle
              updatedAt
              metafields(first: 250) {
                edges {
                  node {
                    id
                    namespace
                    key
                    type
                    value
                    definition {
                      id
                      name
                    }
                  }
                }
              }
            }
          }
        }
      }
    `,
    title(node) {
      return node.title;
    },
  },
  {
    fileName: "ARTICLE.json",
    rootKey: "articles",
    query: `
      query GetArticleMetafields($after: String) {
        articles(first: 250, after: $after, reverse: true) {
          pageInfo {
            hasNextPage
            endCursor
          }
          edges {
            node {
              id
              title
              handle
              updatedAt
              blog {
                id
                title
              }
              metafields(first: 250) {
                edges {
                  node {
                    id
                    namespace
                    key
                    type
                    value
                    definition {
                      id
                      name
                    }
                  }
                }
              }
            }
          }
        }
      }
    `,
    title(node) {
      return node.blog?.title ? `${node.blog.title} / ${node.title}` : node.title;
    },
  },
];

async function fetchOwnerTypes(accessToken) {
  const query = `
    query GetMetafieldOwnerTypes {
      __type(name: "MetafieldOwnerType") {
        enumValues {
          name
        }
      }
    }
  `;

  try {
    const data = await graphql(query, {}, accessToken);
    const values = data?.__type?.enumValues?.map((value) => value.name) ?? [];
    return values.length ? values : FALLBACK_OWNER_TYPES;
  } catch {
    return FALLBACK_OWNER_TYPES;
  }
}

export async function exportMetafieldDefinitions(accessToken) {
  const query = `
    query GetMetafieldDefinitions($ownerType: MetafieldOwnerType!, $after: String) {
      metafieldDefinitions(first: 250, ownerType: $ownerType, after: $after) {
        pageInfo {
          hasNextPage
          endCursor
        }
        edges {
          node {
            id
            name
            namespace
            key
            description
            ownerType
            type {
              name
            }
            validations {
              name
              value
            }
          }
        }
      }
    }
  `;

  const ownerTypes = await fetchOwnerTypes(accessToken);
  const byOwnerType = [];

  for (const ownerType of ownerTypes) {
    const definitions = await paginateConnection(
      query,
      "metafieldDefinitions",
      { ownerType },
      accessToken,
    );

    const snapshot = { ownerType, count: definitions.length, definitions };
    byOwnerType.push(snapshot);

    await writeJson(
      path.join(REPO_ROOT, "metafields", "definitions", `${ownerType}.json`),
      snapshot,
    );
  }

  const allDefinitions = byOwnerType.flatMap((entry) => entry.definitions);

  const manifest = {
    exportedAt: new Date().toISOString(),
    shop: SHOP,
    apiVersion: API_VERSION,
    totalCount: allDefinitions.length,
    ownerTypes: byOwnerType.map((entry) => ({
      ownerType: entry.ownerType,
      count: entry.count,
      file: `./${entry.ownerType}.json`,
    })),
  };

  await writeJson(path.join(REPO_ROOT, "metafields", "definitions", "index.json"), manifest);
  await writeJson(path.join(REPO_ROOT, "metafields", "definitions", "all.json"), {
    ...manifest,
    definitions: allDefinitions,
  });

  return manifest;
}

export async function exportMetaobjects(accessToken) {
  const definitionsQuery = `
    query GetMetaobjectDefinitions($after: String) {
      metaobjectDefinitions(first: 250, after: $after) {
        pageInfo {
          hasNextPage
          endCursor
        }
        edges {
          node {
            id
            name
            type
            description
            displayNameKey
            fieldDefinitions {
              key
              name
              description
              required
              type {
                name
              }
              validations {
                name
                value
              }
            }
          }
        }
      }
    }
  `;

  const entriesQuery = `
    query GetMetaobjectsByType($type: String!, $after: String) {
      metaobjects(type: $type, first: 250, after: $after) {
        pageInfo {
          hasNextPage
          endCursor
        }
        edges {
          node {
            id
            type
            handle
            displayName
            status
            updatedAt
            fields {
              key
              type
              value
            }
          }
        }
      }
    }
  `;

  const definitions = await paginateConnection(definitionsQuery, "metaobjectDefinitions", {}, accessToken);

  const definitionsManifest = {
    exportedAt: new Date().toISOString(),
    shop: SHOP,
    apiVersion: API_VERSION,
    totalCount: definitions.length,
    definitions: definitions.map((definition) => ({
      id: definition.id,
      name: definition.name,
      type: definition.type,
      file: `./${sanitizeFilename(definition.type)}.json`,
    })),
  };

  await writeJson(path.join(REPO_ROOT, "metaobjects", "definitions", "index.json"), definitionsManifest);
  await writeJson(path.join(REPO_ROOT, "metaobjects", "definitions", "all.json"), {
    ...definitionsManifest,
    definitions,
  });

  for (const definition of definitions) {
    await writeJson(
      path.join(REPO_ROOT, "metaobjects", "definitions", `${sanitizeFilename(definition.type)}.json`),
      definition,
    );
  }

  const entrySnapshots = [];

  for (const definition of definitions) {
    const entries = await paginateConnection(entriesQuery, "metaobjects", { type: definition.type }, accessToken);
    const snapshot = {
      type: definition.type,
      name: definition.name,
      count: entries.length,
      entries,
    };

    entrySnapshots.push(snapshot);
    await writeJson(
      path.join(REPO_ROOT, "metaobjects", "entries", `${sanitizeFilename(definition.type)}.json`),
      snapshot,
    );
  }

  const entriesManifest = {
    exportedAt: new Date().toISOString(),
    shop: SHOP,
    apiVersion: API_VERSION,
    totalTypes: entrySnapshots.length,
    totalEntries: entrySnapshots.reduce((sum, snapshot) => sum + snapshot.count, 0),
    types: entrySnapshots.map((snapshot) => ({
      type: snapshot.type,
      count: snapshot.count,
      file: `./${sanitizeFilename(snapshot.type)}.json`,
    })),
  };

  await writeJson(path.join(REPO_ROOT, "metaobjects", "entries", "index.json"), entriesManifest);
  await writeJson(path.join(REPO_ROOT, "metaobjects", "entries", "all.json"), {
    ...entriesManifest,
    entriesByType: entrySnapshots,
  });

  return {
    definitions: definitionsManifest,
    entries: entriesManifest,
  };
}

export async function exportMetafieldValues(accessToken) {
  const snapshots = [];

  for (const resource of RESOURCE_EXPORTS) {
    let snapshot;

    if (resource.rootKey === "shop") {
      const data = await graphql(resource.query, {}, accessToken);
      snapshot = resource.normalize(data);
    } else {
      const nodes = await paginateConnection(resource.query, resource.rootKey, {}, accessToken);
      const resources = nodes.map((node) => ({
        id: node.id,
        title: resource.title?.(node) ?? node.title ?? node.handle ?? node.id,
        handle: node.handle ?? null,
        updatedAt: node.updatedAt ?? null,
        metafields: node.metafields.edges.map((edge) => edge.node),
      }));

      snapshot = {
        resourceType: resource.fileName.replace(".json", ""),
        count: resources.reduce((sum, entry) => sum + entry.metafields.length, 0),
        resourceCount: resources.length,
        resources,
      };
    }

    snapshots.push({
      resourceType: snapshot.resourceType,
      count: snapshot.count,
      resourceCount: snapshot.resources.length,
      file: `./${resource.fileName}`,
    });

    await writeJson(path.join(REPO_ROOT, "metafields", "values", resource.fileName), snapshot);
  }

  const manifest = {
    exportedAt: new Date().toISOString(),
    shop: SHOP,
    apiVersion: API_VERSION,
    resourceTypes: snapshots,
    totalMetafields: snapshots.reduce((sum, snapshot) => sum + snapshot.count, 0),
  };

  await writeJson(path.join(REPO_ROOT, "metafields", "values", "index.json"), manifest);
  return manifest;
}
