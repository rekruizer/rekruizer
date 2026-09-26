#!/usr/bin/env python3
"""Convert checked-in service PNG sources to optimized public WebP files."""

from __future__ import annotations

import re
import shutil
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
SOURCE_DIR = ROOT / "assets" / "source" / "services"
OUTPUT_DIR = ROOT / "assets" / "services"
SOURCE_GROUPS = (SOURCE_DIR / "site", SOURCE_DIR / "catalog")
WEBP_QUALITY = 82


def source_images() -> list[Path]:
    images = sorted(path for group in SOURCE_GROUPS for path in group.glob("*.png"))
    if not images:
        raise RuntimeError(f"No PNG sources found in {SOURCE_DIR.relative_to(ROOT)}")

    stems: set[str] = set()
    for path in images:
        if not re.fullmatch(r"[a-z0-9-]+", path.stem):
            raise RuntimeError(f"Unsafe source image name: {path.relative_to(ROOT)}")
        if path.stem in stems:
            raise RuntimeError(f"Duplicate source image name: {path.stem}.png")
        stems.add(path.stem)
        if path.read_bytes()[:8] != b"\x89PNG\r\n\x1a\n":
            raise RuntimeError(f"Invalid PNG source: {path.relative_to(ROOT)}")
    return images


def main() -> None:
    encoder = shutil.which("cwebp")
    if not encoder:
        raise RuntimeError("cwebp is required to generate service WebP images")

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    images = source_images()
    for source in images:
        destination = OUTPUT_DIR / f"{source.stem}.webp"
        subprocess.run(
            [
                encoder,
                "-quiet",
                "-q",
                str(WEBP_QUALITY),
                "-m",
                "6",
                "-sharp_yuv",
                "-mt",
                str(source),
                "-o",
                str(destination),
            ],
            check=True,
        )

    print(
        f"Generated {len(images)} WebP images from "
        f"{SOURCE_DIR.relative_to(ROOT)} at quality {WEBP_QUALITY}"
    )


if __name__ == "__main__":
    main()
