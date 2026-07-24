#!/usr/bin/env python3
"""Verify official text parity, links, preserved assets, and canonical coverage."""

from __future__ import annotations

import hashlib
import json
import re
import sys
from html.parser import HTMLParser
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MANIFEST = json.loads((ROOT / "content" / "original-text-manifest.json").read_text(encoding="utf-8"))
ROUTES = MANIFEST["canonical_routes"]


class TokenParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.current: dict | None = None
        self.tokens: dict[int, str] = {}
        self.links: list[str] = []

    def handle_starttag(self, tag, attrs):
        attr = dict(attrs)
        if tag == "a" and attr.get("href"):
            self.links.append(attr["href"])
        if "data-token-index" in attr:
            self.current = {"index": int(attr["data-token-index"]), "parts": []}

    def handle_data(self, data):
        if self.current is not None:
            self.current["parts"].append(data)

    def handle_endtag(self, tag):
        if self.current is not None and tag in {"a", "p", "span", "h1", "h2", "h3", "h4", "h5", "h6"}:
            value = re.sub(r"\s+", " ", "".join(self.current["parts"])).strip()
            self.tokens[self.current["index"]] = value
            self.current = None


def main() -> None:
    errors: list[str] = []
    pages = {page["source_url"]: page for page in MANIFEST["pages"]}
    all_files = {path.name for path in ROOT.glob("*.html")} | {path.name for path in ROOT.glob("*.php")}

    for source_url, route in ROUTES.items():
        path = ROOT / route
        if not path.exists():
            errors.append(f"missing canonical page: {route}")
            continue
        parser = TokenParser()
        parser.feed(path.read_text(encoding="utf-8"))
        expected = [token["text"] for token in pages[source_url]["tokens"]]
        actual = [parser.tokens.get(index) for index in range(len(expected))]
        if actual != expected:
            mismatch = next((i for i, pair in enumerate(zip(actual, expected)) if pair[0] != pair[1]), None)
            errors.append(f"text mismatch: {route} token {mismatch}")
        for href in parser.links:
            if href.startswith(("http://", "https://", "mailto:", "tel:", "#")):
                continue
            target = href.split("#", 1)[0].split("?", 1)[0]
            if target and target not in all_files and not (ROOT / target).exists():
                errors.append(f"broken local link: {route} -> {href}")

    shell = (ROOT / "page-shell.js").read_text(encoding="utf-8")
    for href in re.findall(r'href="([^"]+)"', shell):
        if href.startswith(("http://", "https://", "mailto:", "tel:", "#")):
            continue
        target = href.split("#", 1)[0]
        if target and not (ROOT / target).exists():
            errors.append(f"broken shell navigation link: {href}")

    aliases = {
        "contact-2.html": "contact.html",
        "contact.php": "contact.html",
        "index-2.html": "index.html",
        "nos-projets-en-cours-2.html": "projets-en-cours.html",
        "nos-realisations.html": "realisations.html",
    }
    for alias, target in aliases.items():
        alias_path = ROOT / alias
        if not alias_path.exists() or f"url={target}" not in alias_path.read_text(encoding="utf-8"):
            errors.append(f"invalid redirect alias: {alias} -> {target}")

    for relative, expected_hash in MANIFEST["preserved_assets"].items():
        actual_hash = hashlib.sha256((ROOT / relative).read_bytes()).hexdigest()
        if actual_hash != expected_hash:
            errors.append(f"preserved asset changed: {relative}")

    home = (ROOT / "index.html").read_text(encoding="utf-8")
    for partner in MANIFEST["partner_links"]:
        if partner not in home:
            errors.append(f"missing partner destination: {partner}")
    if home.count('data-content-origin="custom"') < 4:
        errors.append("custom homepage sections were not preserved")

    if errors:
        print("\n".join(errors))
        return 1
    print(f"Verified {len(ROUTES)} canonical pages with exact source-token parity and valid local links.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
