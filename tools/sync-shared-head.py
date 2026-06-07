#!/usr/bin/env python3
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
SHARED = (ROOT / "tools" / "shared-head.html").read_text().rstrip()
START = "  <!-- SEO: shared metadata -->"
END = "  <!-- /SEO: shared metadata -->"
PATTERN = re.compile(rf"{re.escape(START)}\n(.*?){re.escape(END)}", re.S)

updated = 0
for path in sorted(ROOT.glob("**/index.html")):
    if ".git" in path.parts:
        continue
    html = path.read_text()
    match = PATTERN.search(html)
    if not match:
        raise SystemExit(f"Shared SEO block not found: {path.relative_to(ROOT)}")

    block = match.group(0)
    canonical = re.search(r'  <link rel="canonical" href="[^"]+" />\n', block)
    if not canonical:
        raise SystemExit(f"Canonical not found inside shared SEO block: {path.relative_to(ROOT)}")

    replacement = f"{START}\n{canonical.group(0)}{SHARED}\n{END}"
    if block != replacement:
        path.write_text(html[:match.start()] + replacement + html[match.end():])
        updated += 1

print(f"Synced shared head in {updated} page(s).")
