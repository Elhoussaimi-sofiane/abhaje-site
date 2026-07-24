export default {
  async fetch(request, env) {
    if (!env?.ASSETS?.fetch) return new Response("Site assets unavailable", { status: 503 });
    const response = await env.ASSETS.fetch(request);
    if (response.status !== 404) return response;
    const fallbackUrl = new URL(request.url);
    fallbackUrl.pathname = "/index.html";
    return env.ASSETS.fetch(new Request(fallbackUrl, request));
  }
};
