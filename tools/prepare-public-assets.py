#!/usr/bin/env python3
"""Prepare Astro's generated public directory from canonical repository files.

The repository keeps editable inputs in their historical stable locations so
the admin and sync Workers can update them. Astro receives a clean, explicit
public tree for both local development and production builds.
"""

from __future__ import annotations

import shutil
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"
ASSETS = ROOT / "assets"

ROOT_PUBLIC_FILES = (
    "CNAME",
    "robots.txt",
    "favicon.ico",
    "favicon.svg",
    "favicon-16x16.png",
    "favicon-32x32.png",
    "apple-touch-icon.png",
)
OPTIONAL_GENERATED_FILES = ("services-feed.xml", "meta-services-feed.xml")


def ignore_asset_sources(_directory: str, names: list[str]) -> set[str]:
    ignored = {name for name in names if name == ".DS_Store"}
    ignored.update(name for name in names if name in {"Icon_Pack", "source", "data"})
    return ignored


def copy_file(source: Path, destination: Path, *, required: bool = True) -> None:
    if not source.is_file():
        if required:
            raise RuntimeError(f"Missing public source: {source.relative_to(ROOT)}")
        return
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, destination)


def main() -> None:
    if PUBLIC.exists():
        shutil.rmtree(PUBLIC)
    PUBLIC.mkdir(parents=True)

    shutil.copytree(
        ASSETS,
        PUBLIC / "assets",
        ignore=ignore_asset_sources,
        dirs_exist_ok=True,
    )

    # Reviews are fetched by the browser; catalogue and presentation JSON are
    # build inputs and intentionally stay private to the published artifact.
    copy_file(
        ASSETS / "data" / "reviews.json",
        PUBLIC / "assets" / "data" / "reviews.json",
    )

    for name in ROOT_PUBLIC_FILES:
        copy_file(ROOT / name, PUBLIC / name)
    for name in OPTIONAL_GENERATED_FILES:
        copy_file(ROOT / name, PUBLIC / name, required=False)

    copy_file(ROOT / "reviews" / "reviews.css", PUBLIC / "reviews" / "reviews.css")
    copy_file(ROOT / "reviews" / "reviews.js", PUBLIC / "reviews" / "reviews.js")
    icons = ROOT / "reviews" / "icons"
    if icons.is_dir():
        shutil.copytree(icons, PUBLIC / "reviews" / "icons", dirs_exist_ok=True)

    files = sum(1 for path in PUBLIC.rglob("*") if path.is_file())
    print(f"Prepared {files} public files for Astro")


if __name__ == "__main__":
    main()
