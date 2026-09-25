#!/usr/bin/env python3
"""Small release gate for the Astro output and legacy URL parity."""

from __future__ import annotations

import re
import json
from pathlib import Path


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

    print(f"Verified {len(actual)} Astro pages and static shared layout")


if __name__ == "__main__":
    main()
