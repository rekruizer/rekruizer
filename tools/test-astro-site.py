#!/usr/bin/env python3
"""Small release gate for the Astro output and legacy URL parity."""

from __future__ import annotations

import re
import json
from pathlib import Path
from xml.etree import ElementTree


ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "dist"
LEGACY_ROOTS = ("documents", "muscles", "notes", "quizzes", "reviews", "url")


def expected_pages() -> set[str]:
    pages = {"index.html", "404.html", "services/index.html"}
    presentation = json.loads((ROOT / "assets" / "data" / "services-presentation.json").read_text(encoding="utf-8"))
    pages.update(f"services/{slug}/index.html" for slug in presentation["pages"])
    for directory in LEGACY_ROOTS:
        pages.update(
            path.relative_to(ROOT).as_posix()
            for path in (ROOT / directory).rglob("index.html")
        )
    return pages


def main() -> None:
    actual = {
        path.relative_to(DIST).as_posix()
        for path in DIST.rglob("*.html")
    }
    expected = expected_pages()
    assert actual == expected, (
        f"route mismatch: missing={sorted(expected - actual)}, "
        f"unexpected={sorted(actual - expected)}"
    )

    for relative in sorted(actual):
        source = (DIST / relative).read_text(encoding="utf-8")
        assert "<title>" in source, relative
        assert "data-site-header" not in source, relative
        assert "data-site-footer" not in source, relative
        if relative not in {"404.html", "reviews/index.html"} and not relative.startswith("url/"):
            assert re.search(r'<link rel="canonical" href="https://denisyuce\.com/', source), relative

    for relative in ("index.html", "services/index.html", "services/classic/index.html", "notes/index.html"):
        source = (DIST / relative).read_text(encoding="utf-8")
        assert '<header class="site-header">' in source, relative
        assert "<footer>" in source, relative

    not_found = (DIST / "404.html").read_text(encoding="utf-8")
    assert '<header class="site-header">' in not_found
    assert "<footer>" in not_found
    assert 'name="robots" content="noindex, follow"' in not_found
    assert 'rel="canonical"' not in not_found

    for source_page in (ROOT / "url").glob("*/index.html"):
        relative = source_page.relative_to(ROOT)
        built = (DIST / relative).read_text(encoding="utf-8")
        assert 'name="robots" content="noindex, nofollow' in built, relative
        assert 'rel="canonical"' not in built, relative
        assert (
            'http-equiv="refresh"' in built
            or "Эта ссылка была отключена" in built
        ), relative

    for required in (
        "CNAME",
        "robots.txt",
        "favicon.svg",
        "assets/site.css",
        "assets/site.js",
        "assets/data/reviews.json",
        "services-feed.xml",
        "meta-services-feed.xml",
        "reviews/reviews.css",
        "reviews/reviews.js",
    ):
        assert (DIST / required).is_file(), f"missing public file: {required}"

    for private_input in (
        "assets/data/services-catalog.json",
        "assets/data/services-presentation.json",
        "assets/source",
    ):
        assert not (DIST / private_input).exists(), f"published build input: {private_input}"

    indexable: set[str] = set()
    for relative in actual:
        source = (DIST / relative).read_text(encoding="utf-8")
        if re.search(r'<meta\s+name="robots"\s+content="[^"]*noindex', source, re.I):
            continue
        canonical = re.search(
            r'<link\s+rel="canonical"\s+href="([^"]+)"',
            source,
            re.I,
        )
        assert canonical is not None, f"indexable page has no canonical: {relative}"
        indexable.add(canonical.group(1))

    sitemap = ElementTree.parse(DIST / "sitemap.xml")
    namespace = {"s": "http://www.sitemaps.org/schemas/sitemap/0.9"}
    sitemap_urls = {
        item.text
        for item in sitemap.findall("s:url/s:loc", namespace)
        if item.text
    }
    assert sitemap_urls == indexable, (
        f"sitemap mismatch: missing={sorted(indexable - sitemap_urls)}, "
        f"unexpected={sorted(sitemap_urls - indexable)}"
    )

    print(f"Verified {len(actual)} Astro pages and static shared layout")


if __name__ == "__main__":
    main()
