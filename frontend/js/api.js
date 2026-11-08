/**
 * Call the API and parse JSON.
 *
 * @param {string} path Absolute API path, for example "/health".
 * @param {RequestInit} [options] Standard fetch options.
 * @param {{ onLoading?: (loading: boolean) => void }} [hooks]
 * @returns {Promise<{ ok: boolean, status: number, data: unknown }>}
 */
async function apiRequest(path, options = {}, hooks = {}) {
  const { onLoading } = hooks;
  onLoading?.(true);

  try {
    const response = await fetch(`${API_BASE}${path}`, {
      ...options,
      headers: {
        Accept: "application/json",
        ...(options.headers || {}),
      },
    });

    const contentType = response.headers.get("content-type") || "";
    let data = null;

    if (contentType.includes("application/json")) {
      data = await response.json();
    } else {
      data = await response.text();
    }

    if (!response.ok) {
      const error = new Error(`API ${response.status} for ${path}`);
      error.status = response.status;
      error.data = data;
      throw error;
    }

    return { ok: true, status: response.status, data };
  } finally {
    onLoading?.(false);
  }
}
