#!/usr/bin/env python3
"""Build the static ABHAJE site into dist/client without source/output drift."""

from pathlib import Path
import shutil


project = Path(__file__).resolve().parents[1]
client = project / "dist" / "client"
server = project / "dist" / "server"
if client.exists():
    shutil.rmtree(client)
client.mkdir(parents=True)
server.mkdir(parents=True, exist_ok=True)

for pattern in ("*.html", "*.php", "*.css", "*.js"):
    for source in project.glob(pattern):
        shutil.copy2(source, client / source.name)

shutil.copytree(project / "assets", client / "assets")
(server / "index.js").write_text(
    """export default {
  async fetch(request, env) {
    if (!env?.ASSETS?.fetch) return new Response("Site assets unavailable", { status: 503 });
    const response = await env.ASSETS.fetch(request);
    if (response.status !== 404) return response;
    const fallbackUrl = new URL(request.url);
    fallbackUrl.pathname = "/index.html";
    return env.ASSETS.fetch(new Request(fallbackUrl, request));
  }
};
""",
    encoding="utf-8",
)
print(f"Built {len(list(client.rglob('*')))} static entries in {client}")
