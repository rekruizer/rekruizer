#!/usr/bin/env python3
"""Generate sitemap.xml from static HTML pages.

The script uses each page's canonical URL as the source of truth, so the sitemap
matches the URLs declared in HTML and avoids manual maintenance.
"""
from __future__ import annotations

import re
from datetime import datetime
from pathlib import Path
from xml.etree.ElementTree import Element, ElementTree, SubElement, indent, register_namespace
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[1]
SITE = "https://denisyuce.com"
MOSCOW_TZ = ZoneInfo("Europe/Moscow")
EXCLUDED_DIRS = {".git", ".github", ".local", "_site"}
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
    for path in ROOT.rglob("*.html"):
        rel_parts = path.relative_to(ROOT).parts
        if any(part in EXCLUDED_DIRS for part in rel_parts):
            continue
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


def build_sitemap() -> None:
    urls = sorted({url for page in iter_html_pages() if (url := canonical_for_page(page))}, key=sort_key)
    lastmod = datetime.now(MOSCOW_TZ).strftime("%Y-%m-%d")

    register_namespace("", "http://www.sitemaps.org/schemas/sitemap/0.9")
    root = Element("urlset", {"xmlns": "http://www.sitemaps.org/schemas/sitemap/0.9"})
    for url in urls:
        item = SubElement(root, "url")
        SubElement(item, "loc").text = url
        SubElement(item, "lastmod").text = lastmod
        SubElement(item, "priority").text = priority_for_url(url)

    indent(root, space="  ")
    ElementTree(root).write(ROOT / "sitemap.xml", encoding="UTF-8", xml_declaration=True)
    print(f"Generated sitemap.xml with {len(urls)} URLs")


if __name__ == "__main__":
    build_sitemap()
