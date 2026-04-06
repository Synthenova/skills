import { API_VERSION, CLIENT_ID, CLIENT_SECRET, SHOP, requireEnv } from "../config.mjs";

export async function getAccessToken() {
  if (process.env.SHOPIFY_ACCESS_TOKEN) {
    return process.env.SHOPIFY_ACCESS_TOKEN;
  }

  const shop = requireEnv("SHOPIFY_SHOP", SHOP);
  const clientId = requireEnv("SHOPIFY_CLIENT_ID", CLIENT_ID);
  const clientSecret = requireEnv("SHOPIFY_CLIENT_SECRET", CLIENT_SECRET);

  const response = await fetch(`https://${shop}/admin/oauth/access_token`, {
    method: "POST",
    headers: {
      Accept: "application/json",
      "Content-Type": "application/x-www-form-urlencoded",
    },
    body: new URLSearchParams({
      client_id: clientId,
      client_secret: clientSecret,
      grant_type: "client_credentials",
    }),
  });

  const payload = await response.json();
  if (!response.ok || !payload.access_token) {
    throw new Error(
      `Failed to fetch Shopify access token: ${JSON.stringify(payload)}`,
    );
  }

  return payload.access_token;
}

export async function graphql(query, variables = {}, accessToken) {
  const shop = requireEnv("SHOPIFY_SHOP", SHOP);
  const response = await fetch(
    `https://${shop}/admin/api/${API_VERSION}/graphql.json`,
    {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-Shopify-Access-Token": accessToken,
      },
      body: JSON.stringify({ query, variables }),
    },
  );

  const payload = await response.json();

  if (!response.ok) {
    throw new Error(
      `Shopify GraphQL request failed (${response.status}): ${JSON.stringify(payload)}`,
    );
  }

  if (payload.errors?.length) {
    throw new Error(`Shopify GraphQL errors: ${JSON.stringify(payload.errors)}`);
  }

  return payload.data;
}

function getConnection(data, key) {
  const connection = data?.[key];
  if (!connection || !Array.isArray(connection.edges)) {
    throw new Error(`Missing connection data for "${key}"`);
  }
  return connection;
}

export async function paginateConnection(query, key, variables, accessToken) {
  const nodes = [];
  let after = null;

  while (true) {
    const data = await graphql(query, { ...variables, after }, accessToken);
    const connection = getConnection(data, key);

    nodes.push(...connection.edges.map((edge) => edge.node));

    if (!connection.pageInfo?.hasNextPage) {
      break;
    }

    after = connection.pageInfo.endCursor;
  }

  return nodes;
}
