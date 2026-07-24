#!/usr/bin/env python3
"""Generate the canonical ABHAJE static pages from the frozen live-site text."""

from __future__ import annotations

import hashlib
import html
import json
import re
import subprocess
import urllib.parse
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE_COMMIT = "635e08c"
MANIFEST_PATH = ROOT / "content" / "original-text-manifest.json"
ROUTE_MAP_PATH = ROOT / "content" / "route-map.json"

CANONICAL_ROUTES = {
    "https://www.abhaje.ma/": "index.html",
    "https://www.abhaje.ma/Activites%20Domaine.html": "activites-domaine.html",
    "https://www.abhaje.ma/AMENAGEMENT%20EXTERIEURS%20ET%20EPSACES%20VERT.html": "amenagement-exterieurs-et-epsaces-vert.html",
    "https://www.abhaje.ma/Batiments.html": "batiments.html",
    "https://www.abhaje.ma/contact.html": "contact.html",
    "https://www.abhaje.ma/Electricite%20et%20Lustrerie.html": "electricite-et-lustrerie.html",
    "https://www.abhaje.ma/Enrob%C3%A9s%20routiers.html": "enrobes-routiers.html",
    "https://www.abhaje.ma/Etanch%C3%A9it%C3%A9.html": "etancheite.html",
    "https://www.abhaje.ma/faculte%20Agadir.html": "faculte-agadir.html",
    "https://www.abhaje.ma/Gros%20oeuvres.html": "gros-oeuvres.html",
    "https://www.abhaje.ma/Lot%20Secondaires.html": "lot-secondaires.html",
    "https://www.abhaje.ma/Lot%20Techniques.html": "lot-techniques.html",
    "https://www.abhaje.ma/Menuiserie%20en%20Bois%20et%20Aluminium.html": "menuiserie-en-bois-et-aluminium.html",
    "https://www.abhaje.ma/Menuiserie%20en%20Metallique.html": "menuiserie-en-metallique.html",
    "https://www.abhaje.ma/Nos%20lieux.html": "nos-lieux.html",
    "https://www.abhaje.ma/Nos%20Projets%20en%20cours.html": "projets-en-cours.html",
    "https://www.abhaje.ma/Nos%20Projets.html": "nos-projets.html",
    "https://www.abhaje.ma/Nos%20Realisations.html": "realisations.html",
    "https://www.abhaje.ma/Ouvrage%20d%27art%20routier.html": "ouvrage-d-art-routier.html",
    "https://www.abhaje.ma/Peinture.html": "peinture.html",
    "https://www.abhaje.ma/Plomberie%20et%20Sanitaire.html": "plomberie-et-sanitaire.html",
    "https://www.abhaje.ma/Profil.html": "profil.html",
    "https://www.abhaje.ma/Province%20de%20Fqih%20Ben%20Salh.html": "province-de-fqih-ben-salh.html",
    "https://www.abhaje.ma/Province%20de%20Sidi%20Bennour.html": "province-de-sidi-bennour.html",
    "https://www.abhaje.ma/Rev%C3%AAtement%20de%20Sol%20et%20Mur.html": "revetement-de-sol-et-mur.html",
    "https://www.abhaje.ma/Routiers.html": "routiers.html",
    "https://www.abhaje.ma/Terrasement.html": "terrasement.html",
    "https://www.abhaje.ma/Travaux%20Routiere.html": "travaux-routiere.html",
    "https://www.abhaje.ma/Tribunal%20Agadir.html": "tribunal-agadir.html",
    "https://www.abhaje.ma/Ventilation%20et%20Climatisation.html": "ventilation-et-climatisation.html",
}

DUPLICATE_ROUTES = {
    "https://www.abhaje.ma/index.html": "index.html",
    "https://www.abhaje.ma/contact.php": "contact.html",
    "https://www.abhaje.ma/Nos%20Projets%20en%20cours_2.html": "projets-en-cours.html",
}

CUSTOM_LOCATION_ROUTES = {
    "https://www.abhaje.ma/Siege%20social%20Ouled%20Berhil%20Taroudannt.html": "siege-ouled-berhil.html",
    "https://www.abhaje.ma/Succursale%20Zone%20Industiel%20Tassila-Agadir.html": "succursale-tassila.html",
    "https://www.abhaje.ma/Usine%20Ouled%20Aissa.html": "usine-ouled-aissa.html",
    "https://www.abhaje.ma/Usine%20Ouled%20Berhil.html": "usine-ouled-aissa.html",
}

ROUTE_TITLES = {
    "index.html": "ABHAJE FRERES",
    "activites-domaine.html": "Activites Domaine",
    "amenagement-exterieurs-et-epsaces-vert.html": "AMENAGEMENT EXTERIEURS ET EPSACES VERT",
    "batiments.html": "Batiment",
    "contact.html": "Contact",
    "electricite-et-lustrerie.html": "Electricite et Lustrerie",
    "enrobes-routiers.html": "Enrobés routiers",
    "etancheite.html": "Etanchéité",
    "faculte-agadir.html": "La facultés de Médecine à Agadir",
    "gros-oeuvres.html": "Gros oeuvres",
    "lot-secondaires.html": "Lot Secondaires",
    "lot-techniques.html": "Lot Techniques",
    "menuiserie-en-bois-et-aluminium.html": "Menuiserie en Bois et Aluminium",
    "menuiserie-en-metallique.html": "Menuiserie en Metallique",
    "nos-lieux.html": "Nos lieux",
    "nos-projets.html": "Nos Projets",
    "ouvrage-d-art-routier.html": "Ouvrage d'art routier",
    "peinture.html": "Peinture",
    "plomberie-et-sanitaire.html": "Plomberie et Sanitaire",
    "profil.html": "Profil",
    "projets-en-cours.html": "Nos Projets en cours",
    "province-de-fqih-ben-salh.html": "Province de Fqih Ben Salh",
    "province-de-sidi-bennour.html": "Province de Sidi Bennour",
    "realisations.html": "Nos Réalisations",
    "revetement-de-sol-et-mur.html": "Revetement de Sol et Mur",
    "routiers.html": "Routiers",
    "terrasement.html": "Terrasement",
    "travaux-routiere.html": "Travaux Routiere",
    "tribunal-agadir.html": "Tribunal de Premiere Instance D'Agadir",
    "ventilation-et-climatisation.html": "Ventilation et Climatisation",
}

NAV_GROUPS = {
    "nos-projets.html": "projects",
    "realisations.html": "projects",
    "projets-en-cours.html": "projects",
    "faculte-agadir.html": "projects",
    "tribunal-agadir.html": "projects",
    "province-de-fqih-ben-salh.html": "projects",
    "province-de-sidi-bennour.html": "projects",
    "nos-lieux.html": "locations",
}

ACTIVITY_ROUTES = {
    "activites-domaine.html", "routiers.html", "terrasement.html", "travaux-routiere.html",
    "ouvrage-d-art-routier.html", "enrobes-routiers.html", "batiments.html", "gros-oeuvres.html",
    "etancheite.html", "lot-techniques.html", "electricite-et-lustrerie.html",
    "ventilation-et-climatisation.html", "plomberie-et-sanitaire.html", "lot-secondaires.html",
    "revetement-de-sol-et-mur.html", "peinture.html", "menuiserie-en-bois-et-aluminium.html",
    "menuiserie-en-metallique.html", "amenagement-exterieurs-et-epsaces-vert.html",
}

PAGE_IMAGES = {
    "index.html": [
        "project-faculte.jpg", "project-tribunal.jpg", "project-fquih.jpg", "project-sidi-bennour.jpg"
    ],
    "realisations.html": [
        "project-real-smara.jpg", "project-real-sidi-ifni.jpg",
        "project-real-agriculture.jpg", "project-real-taroudannt.jpg"
    ],
    "projets-en-cours.html": [
        "project-faculte.jpg", "project-tribunal.jpg", "project-fquih.jpg", "project-sidi-bennour.jpg"
    ],
    "faculte-agadir.html": ["project-faculte.jpg"],
    "tribunal-agadir.html": ["project-tribunal.jpg"],
    "province-de-fqih-ben-salh.html": ["project-fquih.jpg"],
    "province-de-sidi-bennour.html": ["project-sidi-bennour.jpg"],
}

PRESERVED_ASSETS = [
    "project-faculte.jpg", "project-tribunal.jpg", "project-fquih.jpg", "project-sidi-bennour.jpg",
    "project-real-smara.jpg", "project-real-sidi-ifni.jpg", "project-real-agriculture.jpg",
    "project-real-taroudannt.jpg", "partner-carrier.jpg", "partner-cat.jpg",
    "partner-cimar.jpg", "partner-sonasid.jpg",
]

SIDEBAR_MARKERS = {
    "ABHAJE FRERES", "Categories", "Support/Aide", "Support/Help", "blog récents",
    "blog r�cents", "Nos Solutions", "Galeries", "Site Archives", "Nos experiences !",
}


def load_frozen_manifest() -> dict:
    raw = subprocess.check_output(
        ["git", "show", f"{SOURCE_COMMIT}:content/original-text-manifest.json"],
        cwd=ROOT,
    )
    return json.loads(raw)


def extract_custom_sections(markup: str) -> list[str]:
    sections = []
    for class_name in ("partners", "group-network", "location-section", "contact-cta"):
        pattern = re.compile(
            rf'(<section\b(?=[^>]*class="[^"]*\b{class_name}\b[^"]*")[^>]*>.*?</section>)',
            re.I | re.S,
        )
        match = pattern.search(markup)
        if match:
            section_markup = re.sub(
                r'\sdata-content-origin="custom"',
                "",
                match.group(1),
                flags=re.I,
            )
            section = re.sub(
                r"<section\b",
                '<section data-content-origin="custom"',
                section_markup,
                count=1,
                flags=re.I,
            )
            sections.append(section)
    return sections


def normalize_source_url(base: str, href: str) -> str | None:
    if not href or href.startswith(("mailto:", "tel:", "javascript:", "#")):
        return None
    joined = urllib.parse.urljoin(base, href)
    split = urllib.parse.urlsplit(joined)
    if (split.hostname or "").lower() not in {"abhaje.ma", "www.abhaje.ma"}:
        return None
    path = urllib.parse.quote(urllib.parse.unquote(split.path or "/"), safe="/:@")
    return urllib.parse.urlunsplit(("https", "www.abhaje.ma", path, "", ""))


def localize_href(source_url: str, href: str, routes: dict[str, str]) -> tuple[str, bool]:
    if not href:
        return "#", True
    if href.startswith("#"):
        return href, True
    target = normalize_source_url(source_url, href)
    if target:
        if target in routes:
            return routes[target], True
        if target in CUSTOM_LOCATION_ROUTES:
            return CUSTOM_LOCATION_ROUTES[target], True
        return "#", False
    return urllib.parse.urljoin(source_url, href), True


def render_token(token: dict, index: int, source_url: str, routes: dict[str, str]) -> str:
    text = html.escape(token["text"], quote=False)
    kind = token["kind"]
    common = (
        f'class="source-token token-{html.escape(kind)}" '
        f'data-token-index="{index}" data-content-origin="{html.escape(source_url, quote=True)}"'
    )
    if kind == "link":
        href, valid = localize_href(source_url, token.get("href", ""), routes)
        inert = "" if valid else ' data-inert-link="true" aria-disabled="true"'
        return f'<a {common} href="{html.escape(href, quote=True)}"{inert}>{text}</a>'
    if re.fullmatch(r"h[1-6]", kind):
        return f"<{kind} {common}>{text}</{kind}>"
    if kind == "control":
        return f'<span {common} role="button" aria-disabled="true">{text}</span>'
    role = ' role="listitem"' if kind == "list" else ""
    return f"<p {common}{role}>{text}</p>"


def group_tokens(tokens: list[dict], start_index: int) -> list[list[tuple[int, dict]]]:
    groups: list[list[tuple[int, dict]]] = []
    current: list[tuple[int, dict]] = []
    for index, token in enumerate(tokens[start_index:], start=start_index):
        is_heading = bool(re.fullmatch(r"h[1-6]", token["kind"]))
        has_non_heading = any(not re.fullmatch(r"h[1-6]", item["kind"]) for _, item in current)
        if is_heading and current and has_non_heading:
            groups.append(current)
            current = []
        current.append((index, token))
    if current:
        groups.append(current)
    return groups


def group_heading(group: list[tuple[int, dict]]) -> str:
    return next(
        (token["text"] for _, token in group if re.fullmatch(r"h[1-6]", token["kind"])),
        "",
    )


def render_group(group: list[tuple[int, dict]], source_url: str, routes: dict[str, str], sidebar: bool) -> str:
    heading = group_heading(group)
    is_form = heading in {"Envoyer un message", "Laisse Votre Comentaire", "Laisse Votre Commentaire"}
    body = "\n".join(render_token(token, index, source_url, routes) for index, token in group)
    tag = "form" if is_form else "section"
    form_attrs = ' action="#" onsubmit="return false"' if is_form else ""
    classes = "source-card source-card-sidebar" if sidebar else "source-card"
    return (
        f'<{tag}{form_attrs} class="{classes}" data-source-section="{html.escape(heading, quote=True)}" '
        f'data-content-origin="{html.escape(source_url, quote=True)}" data-reveal>{body}</{tag}>'
    )


def render_source_content(page: dict, route: str, routes: dict[str, str]) -> str:
    tokens = page["tokens"]
    source_url = page["source_url"]
    chrome_end = min(39, len(tokens))
    chrome = "\n".join(render_token(token, index, source_url, routes) for index, token in enumerate(tokens[:chrome_end]))
    groups = group_tokens(tokens, chrome_end)

    sidebar_at = len(groups)
    for index, group in enumerate(groups):
        if index > 0 and group_heading(group) in SIDEBAR_MARKERS:
            sidebar_at = index
            break
    main_groups = groups[:sidebar_at]
    sidebar_groups = groups[sidebar_at:]

    main_markup = "\n".join(render_group(group, source_url, routes, False) for group in main_groups)
    sidebar_markup = "\n".join(render_group(group, source_url, routes, True) for group in sidebar_groups)
    sidebar_column = f'<aside class="source-sidebar">{sidebar_markup}</aside>' if sidebar_markup else ""

    image_markup = ""
    images = PAGE_IMAGES.get(route, [])
    if images:
        figures = "".join(
            f'<figure><img src="assets/images/{name}" alt="" loading="lazy"></figure>' for name in images
        )
        image_markup = (
            '<section class="preserved-photo-strip" data-content-origin="custom">'
            f'<div class="container preserved-photo-grid">{figures}</div></section>'
        )

    return f"""
      <section class="legacy-chrome" aria-label="Navigation et outils du site original">
        <div class="container legacy-chrome-flow">{chrome}</div>
      </section>
      {image_markup}
      <section class="source-content">
        <div class="container source-layout">
          <div class="source-primary">{main_markup}</div>
          {sidebar_column}
        </div>
      </section>
    """


def render_page(page: dict, route: str, routes: dict[str, str], custom_sections: list[str]) -> str:
    title = ROUTE_TITLES[route]
    nav_group = NAV_GROUPS.get(route, "activities" if route in ACTIVITY_ROUTES else "")
    custom = "\n".join(custom_sections) if route == "index.html" else ""
    source = html.escape(page["source_url"], quote=True)
    body = render_source_content(page, route, routes)
    return f"""<!doctype html>
<html lang="fr">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="description" content="ABHAJE FRERES — {html.escape(title, quote=True)}">
  <title>{html.escape(title)} | ABHAJE FRERES</title>
  <link rel="stylesheet" href="styles.css">
  <link rel="stylesheet" href="navigation.css">
  <link rel="stylesheet" href="content-pages.css">
  <link rel="stylesheet" href="original-content.css">
  <link rel="stylesheet" href="home-expansion.css">
  <link rel="stylesheet" href="animations.css">
</head>
<body data-nav-group="{nav_group}" data-source-url="{source}">
  <div id="site-shell-header"></div>
  <main class="page-main">
    <section class="page-hero source-page-hero">
      <div class="container">
        <p class="page-breadcrumb">ABHAJE FRERES <span></span> {html.escape(title)}</p>
        <h1>{html.escape(title)}</h1>
      </div>
    </section>
    {body}
    {custom}
  </main>
  <div id="site-shell-footer"></div>
  <script src="page-shell.js"></script>
  <script src="navigation.js"></script>
  <script src="page-animations.js"></script>
</body>
</html>
"""


def redirect_page(target: str) -> str:
    return f"""<!doctype html>
<html lang="fr"><head><meta charset="utf-8"><meta http-equiv="refresh" content="0;url={target}">
<link rel="canonical" href="{target}"><title>ABHAJE FRERES</title></head>
<body><script>location.replace({json.dumps(target)});</script></body></html>
"""


def main() -> None:
    manifest = load_frozen_manifest()
    current_home = (ROOT / "index.html").read_text(encoding="utf-8")
    custom_sections = extract_custom_sections(current_home)
    if len(custom_sections) != 4:
        raise SystemExit(f"Expected 4 preserved custom homepage sections, found {len(custom_sections)}")

    pages_by_url = {page["source_url"]: page for page in manifest["pages"]}
    routes = {**CANONICAL_ROUTES, **DUPLICATE_ROUTES}
    route_manifest = {
        "source": manifest["source"],
        "captured_at_utc": manifest["captured_at_utc"],
        "canonical_routes": CANONICAL_ROUTES,
        "duplicate_routes": DUPLICATE_ROUTES,
        "custom_location_routes": CUSTOM_LOCATION_ROUTES,
        "excluded_empty_routes": [
            "https://www.abhaje.ma/Peche%20de%20Sidi%20Ifni.html",
            "https://www.abhaje.ma/Si%C3%A8ge%20CRA.html",
            "https://www.abhaje.ma/Smara.html",
        ],
    }

    manifest["canonical_page_count"] = len(CANONICAL_ROUTES)
    manifest["canonical_routes"] = CANONICAL_ROUTES
    manifest["duplicate_routes"] = DUPLICATE_ROUTES
    manifest["preserved_assets"] = {
        f"assets/images/{name}": hashlib.sha256((ROOT / "assets" / "images" / name).read_bytes()).hexdigest()
        for name in PRESERVED_ASSETS
    }

    MANIFEST_PATH.parent.mkdir(exist_ok=True)
    MANIFEST_PATH.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    ROUTE_MAP_PATH.write_text(json.dumps(route_manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    for source_url, route in CANONICAL_ROUTES.items():
        markup = render_page(pages_by_url[source_url], route, routes, custom_sections)
        markup = "\n".join(line.rstrip() for line in markup.splitlines()) + "\n"
        (ROOT / route).write_text(
            markup,
            encoding="utf-8",
        )

    aliases = {
        "contact-2.html": "contact.html",
        "contact.php": "contact.html",
        "index-2.html": "index.html",
        "nos-projets-en-cours-2.html": "projets-en-cours.html",
        "nos-realisations.html": "realisations.html",
    }
    for alias, target in aliases.items():
        (ROOT / alias).write_text(redirect_page(target), encoding="utf-8")

    for obsolete in ("peche-de-sidi-ifni.html", "siege-cra.html", "smara.html"):
        path = ROOT / obsolete
        if path.exists():
            path.unlink()

    print(f"Generated {len(CANONICAL_ROUTES)} canonical pages and {len(aliases)} redirect aliases.")


if __name__ == "__main__":
    main()
