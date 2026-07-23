#!/usr/bin/env python3
"""Crawl abhaje.ma, freeze visible text, generate modern static pages, and verify parity."""

from __future__ import annotations

import argparse
import hashlib
import html
import json
import re
import sys
import time
import unicodedata
import urllib.error
import urllib.parse
import urllib.request
from collections import deque
from html.parser import HTMLParser
from pathlib import Path


ORIGIN = "https://www.abhaje.ma"
START_URL = f"{ORIGIN}/"
MAX_PAGES = 160
USER_AGENT = "Mozilla/5.0 (compatible; ABHAJEContentMigration/1.0)"
SKIP_TAGS = {"head", "script", "style", "noscript", "svg", "template"}
VOID_TAGS = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "param", "source", "track", "wbr"}
FIXED_ROUTES = {
    "/": "index.html",
    "/index.html": "index.html",
    "/Nos%20Realisations.html": "realisations.html",
    "/Nos%20Projets%20en%20cours.html": "projets-en-cours.html",
    "/Routiers.html": "routiers.html",
    "/Batiments.html": "batiments.html",
    "/Siege%20social%20Ouled%20Berhil%20Taroudannt.html": "siege-ouled-berhil.html",
    "/Succursale%20Zone%20Industiel%20Tassila-Agadir.html": "succursale-tassila.html",
    "/Usine%20Ouled%20Berhil.html": "usine-ouled-aissa.html",
}
PRESERVED_ASSETS = [
    "assets/images/project-faculte.jpg",
    "assets/images/project-tribunal.jpg",
    "assets/images/project-fquih.jpg",
    "assets/images/project-sidi-bennour.jpg",
    "assets/images/project-real-smara.jpg",
    "assets/images/project-real-sidi-ifni.jpg",
    "assets/images/project-real-agriculture.jpg",
    "assets/images/project-real-taroudannt.jpg",
    "assets/images/partner-carrier.jpg",
    "assets/images/partner-cat.jpg",
    "assets/images/partner-cimar.jpg",
    "assets/images/partner-sonasid.jpg",
]
PARTNER_LINKS = [
    "https://carriermaroc.ma/",
    "https://www.cat.com/fr_FR.html",
    "https://www.cimentsdumaroc.com/fr",
    "https://www.sonasid.ma/fr/home",
]
CUSTOM_PAGE_FILES = {
    "siege-ouled-berhil.html",
    "succursale-tassila.html",
    "usine-ouled-aissa.html",
}
BROKEN_LOCAL_ROUTES = {
    "https://www.abhaje.ma/Siege%20social%20Ouled%20Berhil%20Taroudannt.html": "siege-ouled-berhil.html",
    "https://www.abhaje.ma/Succursale%20Zone%20Industiel%20Tassila-Agadir.html": "succursale-tassila.html",
    "https://www.abhaje.ma/Usine%20Ouled%20Berhil.html": "usine-ouled-aissa.html",
}


def normalize_text(value: str) -> str:
    return re.sub(r"\s+", " ", html.unescape(value)).strip()


def request_url(url: str) -> tuple[str, str]:
    split = urllib.parse.urlsplit(url)
    encoded_path = urllib.parse.quote(urllib.parse.unquote(split.path), safe="/:@")
    encoded = urllib.parse.urlunsplit((split.scheme, split.netloc, encoded_path, split.query, ""))
    request = urllib.request.Request(encoded, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(request, timeout=30) as response:
        content_type = response.headers.get_content_type()
        if content_type not in {"text/html", "application/xhtml+xml"}:
            raise ValueError(f"non-HTML content type: {content_type}")
        raw = response.read()
        charset = response.headers.get_content_charset() or "utf-8"
        try:
            text = raw.decode(charset, errors="strict")
        except (LookupError, UnicodeDecodeError):
            text = raw.decode("utf-8", errors="replace")
        return response.geturl(), text


def normalize_source_url(base: str, href: str) -> str | None:
    if not href or href.startswith(("mailto:", "tel:", "javascript:", "#")):
        return None
    joined = urllib.parse.urljoin(base, href)
    split = urllib.parse.urlsplit(joined)
    host = split.hostname.lower() if split.hostname else ""
    if host not in {"abhaje.ma", "www.abhaje.ma"}:
        return None
    path = urllib.parse.unquote(split.path or "/")
    extension = Path(path).suffix.lower()
    if extension not in {"", ".html", ".php"}:
        return None
    quoted_path = urllib.parse.quote(path, safe="/:@")
    return urllib.parse.urlunsplit(("https", "www.abhaje.ma", quoted_path, "", ""))


class SourceParser(HTMLParser):
    def __init__(self, base_url: str):
        super().__init__(convert_charrefs=True)
        self.base_url = base_url
        self.stack: list[tuple[str, dict[str, str]]] = []
        self.tokens: list[dict[str, str]] = []
        self.links: list[str] = []
        self.title_parts: list[str] = []
        self.in_title = False

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        tag = tag.lower()
        attr_map = {key.lower(): value or "" for key, value in attrs}
        if tag == "title":
            self.in_title = True
        if tag == "a":
            href = attr_map.get("href", "")
            if href:
                self.links.append(href)
        if tag == "input" and not self._is_skipped():
            input_type = attr_map.get("type", "text").lower()
            visible = attr_map.get("value", "") if input_type in {"submit", "button", "reset"} else attr_map.get("placeholder", "")
            self._add_token(visible, "control", attr_map.get("href", ""))
        if tag not in VOID_TAGS:
            self.stack.append((tag, attr_map))

    def handle_startendtag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        self.handle_starttag(tag, attrs)
        if tag.lower() not in VOID_TAGS:
            self.handle_endtag(tag)

    def handle_endtag(self, tag: str) -> None:
        tag = tag.lower()
        if tag == "title":
            self.in_title = False
        for index in range(len(self.stack) - 1, -1, -1):
            if self.stack[index][0] == tag:
                del self.stack[index:]
                break

    def handle_data(self, data: str) -> None:
        value = normalize_text(data)
        if not value:
            return
        if self.in_title:
            self.title_parts.append(value)
            return
        if self._is_skipped():
            return
        kind = "text"
        href = ""
        for tag, attrs in reversed(self.stack):
            if tag == "a" and not href:
                kind = "link"
                href = attrs.get("href", "")
            elif re.fullmatch(r"h[1-6]", tag):
                kind = tag
                break
            elif tag == "li" and kind == "text":
                kind = "list"
            elif tag in {"label", "button", "option"} and kind == "text":
                kind = "control"
        self._add_token(value, kind, href)

    def _is_skipped(self) -> bool:
        return any(tag in SKIP_TAGS for tag, _ in self.stack)

    def _add_token(self, value: str, kind: str, href: str = "") -> None:
        value = normalize_text(value)
        if not value:
            return
        self.tokens.append({"text": value, "kind": kind, "href": href})

    @property
    def title(self) -> str:
        return normalize_text(" ".join(self.title_parts)) or "ABHAJE FRERES"


def crawl() -> tuple[list[dict], list[dict]]:
    queue = deque([START_URL])
    queued = {START_URL}
    visited: set[str] = set()
    pages: list[dict] = []
    failures: list[dict] = []
    while queue and len(visited) < MAX_PAGES:
        url = queue.popleft()
        if url in visited:
            continue
        visited.add(url)
        try:
            final_url, markup = request_url(url)
            parser = SourceParser(final_url)
            parser.feed(markup)
            canonical = normalize_source_url(final_url, final_url) or final_url
            page = {
                "source_url": canonical,
                "requested_url": url,
                "title": parser.title,
                "tokens": parser.tokens,
                "headings": [token["text"] for token in parser.tokens if re.fullmatch(r"h[1-6]", token["kind"])],
            }
            pages.append(page)
            for href in parser.links:
                target = normalize_source_url(final_url, href)
                if target and target not in queued and target not in visited:
                    queued.add(target)
                    queue.append(target)
        except (urllib.error.HTTPError, urllib.error.URLError, TimeoutError, ValueError) as exc:
            failures.append({"url": url, "error": str(exc)})
        time.sleep(0.04)
    unique: dict[str, dict] = {}
    for page in pages:
        unique.setdefault(page["source_url"], page)
    return sorted(unique.values(), key=lambda item: item["source_url"].lower()), failures


def slugify(path: str) -> str:
    stem = Path(urllib.parse.unquote(path)).stem or "index"
    ascii_stem = unicodedata.normalize("NFKD", stem).encode("ascii", "ignore").decode("ascii")
    slug = re.sub(r"[^a-z0-9]+", "-", ascii_stem.lower()).strip("-")
    return f"{slug or 'page'}.html"


def assign_routes(pages: list[dict]) -> dict[str, str]:
    routes: dict[str, str] = {}
    used: set[str] = set()
    for page in pages:
        path = urllib.parse.urlsplit(page["source_url"]).path or "/"
        encoded_path = urllib.parse.quote(urllib.parse.unquote(path), safe="/:@")
        fixed = FIXED_ROUTES.get(encoded_path) or FIXED_ROUTES.get(path)
        route = fixed or slugify(path)
        candidate = route
        suffix = 2
        while candidate in used:
            candidate = route[:-5] + f"-{suffix}.html"
            suffix += 1
        routes[page["source_url"]] = candidate
        used.add(candidate)
    return routes


def extract_custom_sections(index_markup: str) -> list[str]:
    classes = ["partners", "group-network", "location-section", "contact-cta"]
    sections: list[str] = []
    for class_name in classes:
        pattern = re.compile(
            rf'(<section\b(?=[^>]*class="[^"]*\b{re.escape(class_name)}\b[^"]*")[^>]*>.*?</section>)',
            re.IGNORECASE | re.DOTALL,
        )
        match = pattern.search(index_markup)
        if match:
            section = match.group(1)
            section = re.sub(r'\sdata-custom-section="true"', "", section, flags=re.IGNORECASE)
            section = re.sub(r"<section\b", '<section data-custom-section="true"', section, count=1, flags=re.IGNORECASE)
            sections.append(section)
    return sections


def localize_href(source_url: str, href: str, routes: dict[str, str]) -> str:
    if not href:
        return ""
    if href.startswith("#"):
        return href
    target = normalize_source_url(source_url, href)
    if target and target in routes:
        return routes[target]
    if target and target in BROKEN_LOCAL_ROUTES:
        return BROKEN_LOCAL_ROUTES[target]
    return urllib.parse.urljoin(source_url, href)


def render_token(token: dict[str, str], index: int, source_url: str, routes: dict[str, str]) -> str:
    text = html.escape(token["text"], quote=False)
    kind = token["kind"]
    attrs = f'class="source-token token-{html.escape(kind)}" data-token-index="{index}"'
    if kind == "link":
        href = html.escape(localize_href(source_url, token.get("href", ""), routes), quote=True)
        return f'<a {attrs} href="{href}">{text}</a>'
    if re.fullmatch(r"h[1-6]", kind):
        return f"<{kind} {attrs}>{text}</{kind}>"
    if kind == "list":
        return f"<p {attrs} role=\"listitem\">{text}</p>"
    if kind == "control":
        return f"<span {attrs} role=\"button\">{text}</span>"
    return f"<p {attrs}>{text}</p>"


def render_sections(page: dict, routes: dict[str, str]) -> str:
    tokens = page["tokens"]
    first_heading = next((i for i, token in enumerate(tokens) if re.fullmatch(r"h[1-6]", token["kind"])), len(tokens))
    prefix = "\n".join(render_token(token, i, page["source_url"], routes) for i, token in enumerate(tokens[:first_heading]))
    sections: list[str] = []
    current: list[str] = []
    for index, token in enumerate(tokens[first_heading:], start=first_heading):
        if re.fullmatch(r"h[1-6]", token["kind"]) and current:
            sections.append('<section class="exact-section">' + "\n".join(current) + "</section>")
            current = []
        current.append(render_token(token, index, page["source_url"], routes))
    if current:
        sections.append('<section class="exact-section">' + "\n".join(current) + "</section>")
    return (
        '<header class="exact-header"><div class="container exact-header-flow">'
        + prefix
        + '</div></header><main class="exact-main"><div class="container exact-sections">'
        + "\n".join(sections)
        + "</div></main>"
    )


def render_page(page: dict, routes: dict[str, str], custom_sections: list[str], is_home: bool) -> str:
    title = html.escape(page["title"])
    original_content = render_sections(page, routes)
    custom = ""
    if is_home:
        photo_strip = """
<section class="custom-photo-strip" data-custom-section="true" aria-label="Photographies des projets">
  <div class="container custom-photo-grid">
    <img src="assets/images/project-real-smara.jpg" alt="Internat ES-Smara" loading="lazy">
    <img src="assets/images/project-real-sidi-ifni.jpg" alt="Port de pêche de Sidi Ifni" loading="lazy">
    <img src="assets/images/project-real-agriculture.jpg" alt="Chambre Régionale d’Agriculture" loading="lazy">
    <img src="assets/images/project-real-taroudannt.jpg" alt="Fontaine de Taroudannt" loading="lazy">
  </div>
</section>"""
        custom = photo_strip + "\n" + "\n".join(custom_sections)
    return f"""<!doctype html>
<html lang="fr">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{title}</title>
  <link rel="stylesheet" href="styles.css">
  <link rel="stylesheet" href="home-expansion.css">
  <link rel="stylesheet" href="original-content.css">
</head>
<body data-source-url="{html.escape(page['source_url'], quote=True)}">
{original_content}
{custom}
</body>
</html>
"""


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


class GeneratedTokenParser(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.active_index: str | None = None
        self.buffer: list[str] = []
        self.tokens: list[tuple[int, str]] = []
        self.hrefs: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attr_map = {key: value or "" for key, value in attrs}
        if tag == "a" and attr_map.get("href"):
            self.hrefs.append(attr_map["href"])
        if "data-token-index" in attr_map:
            self.active_index = attr_map["data-token-index"]
            self.buffer = []

    def handle_data(self, data: str) -> None:
        if self.active_index is not None:
            self.buffer.append(data)

    def handle_endtag(self, tag: str) -> None:
        if self.active_index is not None and tag in {"a", "h1", "h2", "h3", "h4", "h5", "h6", "p", "span"}:
            self.tokens.append((int(self.active_index), normalize_text(" ".join(self.buffer))))
            self.active_index = None
            self.buffer = []


def verify(project: Path, manifest: dict) -> list[str]:
    errors: list[str] = []
    for page in manifest["pages"]:
        path = project / page["route"]
        if not path.exists():
            errors.append(f"missing route: {page['route']}")
            continue
        parser = GeneratedTokenParser()
        parser.feed(path.read_text(encoding="utf-8"))
        actual = [text for _, text in sorted(parser.tokens)]
        expected = [token["text"] for token in page["tokens"]]
        if actual != expected:
            errors.append(f"text mismatch: {page['route']} expected={len(expected)} actual={len(actual)}")
        for href in parser.hrefs:
            split = urllib.parse.urlsplit(href)
            if not split.scheme and href.endswith(".html") and not (project / split.path).exists():
                errors.append(f"broken local link in {page['route']}: {href}")
    for relative, expected_hash in manifest["preserved_assets"].items():
        asset = project / relative
        if not asset.exists() or sha256(asset) != expected_hash:
            errors.append(f"preserved asset changed: {relative}")
    homepage = (project / "index.html").read_text(encoding="utf-8")
    for link in PARTNER_LINKS:
        if f'href="{link}"' not in homepage:
            errors.append(f"partner link missing: {link}")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--verify-only", action="store_true")
    args = parser.parse_args()
    project = args.project.resolve()
    manifest_path = project / "content" / "original-text-manifest.json"
    if args.verify_only:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        errors = verify(project, manifest)
        if errors:
            print("\n".join(errors), file=sys.stderr)
            return 1
        print(f"Verified {len(manifest['pages'])} pages with exact source-token parity.")
        return 0

    current_index = (project / "index.html").read_text(encoding="utf-8")
    custom_sections = extract_custom_sections(current_index)
    preserved_hashes = {relative: sha256(project / relative) for relative in PRESERVED_ASSETS}
    pages, failures = crawl()
    routes = assign_routes(pages)
    for page in pages:
        page["route"] = routes[page["source_url"]]
        page["sections"] = page["headings"]
    manifest = {
        "source": START_URL,
        "captured_at_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "page_count": len(pages),
        "failed_urls": failures,
        "preserved_assets": preserved_hashes,
        "partner_links": PARTNER_LINKS,
        "pages": pages,
    }
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    route_map = {page["source_url"]: page["route"] for page in pages}
    (manifest_path.parent / "route-map.json").write_text(
        json.dumps(route_map, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    existing_html = {path.name for path in project.glob("*.html")}
    generated_html = set(route_map.values())
    for page in pages:
        output = project / page["route"]
        output.write_text(
            render_page(page, routes, custom_sections, page["route"] == "index.html"),
            encoding="utf-8",
        )
    for stale in sorted(existing_html - generated_html - CUSTOM_PAGE_FILES):
        if stale != "index.html":
            (project / stale).unlink()
    errors = verify(project, manifest)
    if errors:
        print("\n".join(errors), file=sys.stderr)
        return 1
    print(f"Crawled and generated {len(pages)} successful pages; skipped {len(failures)} failed URLs.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
