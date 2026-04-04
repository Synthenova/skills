import path from "node:path";
import { API_VERSION, REPO_ROOT, SHOP } from "../config.mjs";
import { graphql, paginateConnection } from "../lib/api.mjs";
import {
  collectionFolderPath,
  downloadFile,
  extensionFromContentType,
  extensionFromUrl,
  productFolderPath,
  safeSegment,
  sanitizeFilename,
  writeJson,
} from "../lib/fs.mjs";

export async function exportProducts(accessToken) {
  const listQuery = `
    query ListProducts($after: String) {
      products(first: 250, after: $after) {
        pageInfo {
          hasNextPage
          endCursor
        }
        edges {
          node {
            id
            handle
          }
        }
      }
    }
  `;

  const detailQuery = `
    query GetProduct($id: ID!) {
      product(id: $id) {
        id
        title
        handle
        descriptionHtml
        vendor
        productType
        status
        tags
        createdAt
        updatedAt
        seo {
          title
          description
        }
        options {
          id
          name
          optionValues {
            id
            name
          }
        }
        featuredMedia {
          __typename
          ... on MediaImage { id }
          ... on Video { id }
          ... on ExternalVideo { id }
          ... on Model3d { id }
        }
        collections(first: 100) {
          edges {
            node {
              id
              title
              handle
            }
          }
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
        media(first: 250) {
          edges {
            node {
              __typename
              ... on MediaImage {
                id
                alt
                status
                image {
                  url
                  width
                  height
                }
              }
              ... on Video {
                id
                alt
                status
                sources {
                  url
                  mimeType
                  format
                  height
                  width
                }
              }
              ... on ExternalVideo {
                id
                alt
                status
                embeddedUrl
                host
                originUrl
              }
              ... on Model3d {
                id
                alt
                status
                sources {
                  url
                  mimeType
                  format
                  filesize
                }
              }
            }
          }
        }
        variants(first: 250) {
          edges {
            node {
              id
              title
              sku
              barcode
              price
              compareAtPrice
              inventoryQuantity
              taxable
              inventoryPolicy
              selectedOptions {
                name
                value
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
    }
  `;

  const productRefs = await paginateConnection(listQuery, "products", {}, accessToken);
  const manifestEntries = [];

  for (const productRef of productRefs) {
    const detailData = await graphql(detailQuery, { id: productRef.id }, accessToken);
    const product = detailData.product;
    const folder = productFolderPath(product.handle);
    const mediaFolder = path.join(folder, "media");

    const collectionRefs = product.collections.edges.map((edge) => edge.node);
    const productMetafields = product.metafields.edges.map((edge) => edge.node);
    const variants = product.variants.edges.map((edge) => {
      const variant = edge.node;
      return {
        id: variant.id,
        title: variant.title,
        sku: variant.sku,
        barcode: variant.barcode,
        price: variant.price,
        compareAtPrice: variant.compareAtPrice,
        inventoryQuantity: variant.inventoryQuantity,
        taxable: variant.taxable,
        inventoryPolicy: variant.inventoryPolicy,
        selectedOptions: variant.selectedOptions,
        metafields: variant.metafields.edges.map((metafieldEdge) => metafieldEdge.node),
      };
    });

    const mediaRecords = [];
    let mediaPosition = 1;

    for (const edge of product.media.edges) {
      const media = edge.node;
      let sourceUrl = null;
      let width = null;
      let height = null;
      let mimeType = null;

      if (media.__typename === "MediaImage") {
        sourceUrl = media.image?.url ?? null;
        width = media.image?.width ?? null;
        height = media.image?.height ?? null;
      } else if (media.__typename === "Video") {
        const source = media.sources?.[0] ?? null;
        sourceUrl = source?.url ?? null;
        width = source?.width ?? null;
        height = source?.height ?? null;
        mimeType = source?.mimeType ?? null;
      } else if (media.__typename === "Model3d") {
        const source = media.sources?.[0] ?? null;
        sourceUrl = source?.url ?? null;
        mimeType = source?.mimeType ?? null;
      }

      const record = {
        id: media.id,
        type: media.__typename,
        alt: media.alt ?? null,
        status: media.status ?? null,
        position: mediaPosition,
        sourceUrl,
        embeddedUrl: media.embeddedUrl ?? null,
        originUrl: media.originUrl ?? null,
        host: media.host ?? null,
        width,
        height,
        mimeType,
        localFile: null,
      };

      if (sourceUrl) {
        const ext = extensionFromUrl(sourceUrl) ?? (mimeType ? extensionFromContentType(mimeType) : ".bin");
        const fileName = `${String(mediaPosition).padStart(2, "0")}-${safeSegment(media.id.split("/").pop() ?? "media")}${ext}`;
        const destination = path.join(mediaFolder, fileName);
        const fileInfo = await downloadFile(sourceUrl, destination);

        record.localFile = `media/${fileName}`;
        record.mimeType = record.mimeType ?? fileInfo.contentType;
        record.size = fileInfo.size;
      }

      mediaRecords.push(record);
      mediaPosition += 1;
    }

    const productDoc = {
      id: product.id,
      title: product.title,
      handle: product.handle,
      descriptionHtml: product.descriptionHtml,
      vendor: product.vendor,
      productType: product.productType,
      status: product.status,
      tags: product.tags,
      createdAt: product.createdAt,
      updatedAt: product.updatedAt,
      seo: product.seo,
      options: product.options.map((option) => ({
        id: option.id,
        name: option.name,
        values: option.optionValues.map((value) => value.name),
      })),
      featuredMediaId: product.featuredMedia?.id ?? null,
    };

    await writeJson(path.join(folder, "product.json"), productDoc);
    await writeJson(path.join(folder, "variants.json"), variants);
    await writeJson(path.join(folder, "collections.json"), collectionRefs);
    await writeJson(path.join(folder, "metafields.json"), productMetafields);
    await writeJson(path.join(folder, "media.json"), mediaRecords);

    manifestEntries.push({
      id: product.id,
      title: product.title,
      handle: product.handle,
      folder: `./${sanitizeFilename(product.handle)}`,
      variantCount: variants.length,
      mediaCount: mediaRecords.length,
      collectionCount: collectionRefs.length,
    });
  }

  const manifest = {
    exportedAt: new Date().toISOString(),
    shop: SHOP,
    apiVersion: API_VERSION,
    totalCount: manifestEntries.length,
    products: manifestEntries,
  };

  await writeJson(path.join(REPO_ROOT, "products", "index.json"), manifest);
  return manifest;
}

export async function exportCollections(accessToken) {
  const listQuery = `
    query ListCollections($after: String) {
      collections(first: 250, after: $after) {
        pageInfo {
          hasNextPage
          endCursor
        }
        edges {
          node {
            id
            handle
          }
        }
      }
    }
  `;

  const detailQuery = `
    query GetCollection($id: ID!) {
      collection(id: $id) {
        id
        title
        handle
        descriptionHtml
        updatedAt
        sortOrder
        templateSuffix
        seo {
          title
          description
        }
        image {
          url
          width
          height
        }
        ruleSet {
          appliedDisjunctively
          rules {
            column
            relation
            condition
          }
        }
        products(first: 250) {
          edges {
            node {
              id
              title
              handle
            }
          }
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
  `;

  const collectionRefs = await paginateConnection(listQuery, "collections", {}, accessToken);
  const manifestEntries = [];

  for (const collectionRef of collectionRefs) {
    const detailData = await graphql(detailQuery, { id: collectionRef.id }, accessToken);
    const collection = detailData.collection;
    const folder = collectionFolderPath(collection.handle);
    const mediaFolder = path.join(folder, "media");
    const products = collection.products.edges.map((edge) => edge.node);
    const metafields = collection.metafields.edges.map((edge) => edge.node);
    const media = [];

    if (collection.image?.url) {
      const ext = extensionFromUrl(collection.image.url) ?? ".bin";
      const fileName = `01-collection-image${ext}`;
      const destination = path.join(mediaFolder, fileName);
      const fileInfo = await downloadFile(collection.image.url, destination);
      media.push({
        type: "IMAGE",
        sourceUrl: collection.image.url,
        width: collection.image.width ?? null,
        height: collection.image.height ?? null,
        localFile: `media/${fileName}`,
        mimeType: fileInfo.contentType,
        size: fileInfo.size,
      });
    }

    const collectionDoc = {
      id: collection.id,
      title: collection.title,
      handle: collection.handle,
      descriptionHtml: collection.descriptionHtml,
      updatedAt: collection.updatedAt,
      sortOrder: collection.sortOrder,
      templateSuffix: collection.templateSuffix,
      seo: collection.seo,
      ruleSet: collection.ruleSet,
    };

    await writeJson(path.join(folder, "collection.json"), collectionDoc);
    await writeJson(path.join(folder, "products.json"), products);
    await writeJson(path.join(folder, "metafields.json"), metafields);
    await writeJson(path.join(folder, "media.json"), media);

    manifestEntries.push({
      id: collection.id,
      title: collection.title,
      handle: collection.handle,
      folder: `./${sanitizeFilename(collection.handle)}`,
      productCount: products.length,
      mediaCount: media.length,
    });
  }

  const manifest = {
    exportedAt: new Date().toISOString(),
    shop: SHOP,
    apiVersion: API_VERSION,
    totalCount: manifestEntries.length,
    collections: manifestEntries,
  };

  await writeJson(path.join(REPO_ROOT, "collections", "index.json"), manifest);
  return manifest;
}
