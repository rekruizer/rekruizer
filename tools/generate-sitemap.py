#!/usr/bin/env python3
"""Generate sitemap.xml from the final Astro build.

The script uses each page's canonical URL as the source of truth, so the sitemap
matches the URLs declared in HTML and avoids manual maintenance.
"""
from __future__ import annotations

import re
import subprocess
from datetime import datetime
from pathlib import Path
from xml.etree.ElementTree import Element, ElementTree, SubElement, indent, register_namespace
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[1]
SITE_ROOT = ROOT / "dist"
SITE = "https://denisyuce.com"
MOSCOW_TZ = ZoneInfo("Europe/Moscow")
EXCLUDED_FILES = {"404.html"}

CANONICAL_RE = re.compile(r'<link\s+rel="canonical"\s+href="([^"]+)"', re.I)
NOINDEX_RE = re.compile(r'<meta\s+name="robots"\s+content="[^"]*noindex', re.I)


def priority_for_url(url: str) -> str:
    path = url.removeprefix(SITE).strip("/")
    if path == "":
        return "1.0"
    if path == "services":
        return "0.9"
    if path.startswith("services/"):
        return "0.8"
    if path == "muscles" or path.startswith("muscles/"):
        return "0.7"
    if path in {"notes", "quizzes"} or path.startswith(("notes/", "quizzes/")):
        return "0.6"
    if path == "privacy":
        return "0.4"
    return "0.5"


def sort_key(url: str) -> tuple[int, str]:
    path = url.removeprefix(SITE).strip("/")
    top_order = {
        "": 0,
        "muscles": 1,
        "notes": 2,
        "privacy": 3,
        "quizzes": 4,
        "services": 5,
    }
    top = path.split("/", 1)[0] if path else ""
    return (top_order.get(top, 10), path)


def iter_html_pages() -> list[Path]:
    pages: list[Path] = []
    if not SITE_ROOT.is_dir():
        raise RuntimeError("dist is missing; run the Astro build first")
    for path in SITE_ROOT.rglob("*.html"):
        if path.name in EXCLUDED_FILES:
            continue
        pages.append(path)
    return pages


def canonical_for_page(path: Path) -> str | None:
    html = path.read_text(encoding="utf-8")
    if NOINDEX_RE.search(html):
        return None
    match = CANONICAL_RE.search(html)
    if not match:
        return None
    url = match.group(1).strip()
    if not url.startswith(SITE + "/") and url != SITE:
        return None
    return url if url.endswith("/") else url + "/"


def git_lastmod(path: Path, today: str) -> str | None:
    """Use today for working-tree changes, otherwise the path's last Git change."""
    if not path.exists() or not path.is_relative_to(ROOT):
        return None
    relative = path.relative_to(ROOT).as_posix()
    try:
        changed = subprocess.run(
            ["git", "diff", "--quiet", "HEAD", "--", relative],
            cwd=ROOT,
            check=False,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        if changed.returncode == 1:
            return today
        if changed.returncode != 0:
            return None

        result = subprocess.run(
            ["git", "log", "-1", "--format=%cs", "--", relative],
            cwd=ROOT,
            check=True,
            capture_output=True,
            text=True,
        )
    except (OSError, subprocess.CalledProcessError):
        return None

    value = result.stdout.strip()
    return value if re.fullmatch(r"\d{4}-\d{2}-\d{2}", value) else None


def page_dependencies(path: Path) -> list[Path]:
    relative = path.relative_to(SITE_ROOT).as_posix()
    shared_catalogue = [
        ROOT / "assets" / "data" / "services-catalog.json",
        ROOT / "assets" / "data" / "services-presentation.json",
    ]
    shared_astro = [
        ROOT / "src" / "layouts" / "BaseLayout.astro",
        ROOT / "src" / "components" / "Header.astro",
        ROOT / "src" / "components" / "Footer.astro",
    ]
    if relative == "index.html":
        return shared_catalogue + shared_astro + [
            ROOT / "src" / "pages" / "index.astro",
            ROOT / "assets" / "data" / "reviews.json",
        ]
    if relative == "services/index.html" or (
        relative.startswith("services/") and relative.endswith("/index.html")
    ):
        page_source = (
            ROOT / "src" / "pages" / "services" / "index.astro"
            if relative == "services/index.html"
            else ROOT / "src" / "pages" / "services" / "[slug].astro"
        )
        return shared_catalogue + shared_astro + [page_source]
    legacy_source = ROOT / relative
    return [legacy_source] if legacy_source.is_file() else [ROOT / "src" / "pages" / "[...path].astro"]


def lastmod_for_page(path: Path, today: str) -> str | None:
    """Return the newest real change among a page and its visible dependencies."""
    dates = [
        value
        for candidate in page_dependencies(path)
        if (value := git_lastmod(candidate, today)) is not None
    ]
    return max(dates) if dates else None


def build_sitemap() -> None:
    today = datetime.now(MOSCOW_TZ).strftime("%Y-%m-%d")
    urls: dict[str, str | None] = {}
    for page in iter_html_pages():
        url = canonical_for_page(page)
        if not url:
            continue
        lastmod = lastmod_for_page(page, today)
        previous = urls.get(url)
        if previous is None or (lastmod is not None and lastmod > previous):
            urls[url] = lastmod

    register_namespace("", "http://www.sitemaps.org/schemas/sitemap/0.9")
    root = Element("urlset", {"xmlns": "http://www.sitemaps.org/schemas/sitemap/0.9"})
    for url in sorted(urls, key=sort_key):
        item = SubElement(root, "url")
        SubElement(item, "loc").text = url
        if urls[url]:
            SubElement(item, "lastmod").text = urls[url]
        SubElement(item, "priority").text = priority_for_url(url)

    indent(root, space="  ")
    ElementTree(root).write(SITE_ROOT / "sitemap.xml", encoding="UTF-8", xml_declaration=True)
    dated = sum(lastmod is not None for lastmod in urls.values())
    print(f"Generated sitemap.xml with {len(urls)} URLs ({dated} with lastmod)")


if __name__ == "__main__":
    build_sitemap()
