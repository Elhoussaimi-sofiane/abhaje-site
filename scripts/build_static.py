#!/usr/bin/env python3
"""Build the static ABHAJE site into dist/client without source/output drift."""

from pathlib import Path
import shutil


project = Path(__file__).resolve().parents[1]
client = project / "dist" / "client"
if client.exists():
    shutil.rmtree(client)
client.mkdir(parents=True)

for pattern in ("*.html", "*.css", "*.js"):
    for source in project.glob(pattern):
        shutil.copy2(source, client / source.name)

shutil.copytree(project / "assets", client / "assets")
print(f"Built {len(list(client.rglob('*')))} static entries in {client}")
