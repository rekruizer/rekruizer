#!/usr/bin/env python3
"""Audit local image assets by dimensions and file size.

No external dependencies: reads PNG/JPEG/WebP dimensions from file headers and
prints the biggest candidates for optimization.
"""
from __future__ import annotations

import argparse
import struct
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".webp", ".avif"}


def human_size(size: int) -> str:
    if size >= 1024 * 1024:
        return f"{size / 1024 / 1024:.1f} MB"
    return f"{size / 1024:.0f} KB"


def png_size(data: bytes) -> tuple[int, int] | None:
    if data[:8] != b"\x89PNG\r\n\x1a\n" or data[12:16] != b"IHDR":
        return None
    return struct.unpack(">II", data[16:24])


def jpg_size(data: bytes) -> tuple[int, int] | None:
    if not data.startswith(b"\xff\xd8"):
        return None
    i = 2
    while i + 9 < len(data):
        if data[i] != 0xFF:
            i += 1
            continue
        marker = data[i + 1]
        i += 2
        if marker in {0xD8, 0xD9}:
            continue
        if i + 2 > len(data):
            return None
        length = struct.unpack(">H", data[i:i + 2])[0]
        if length < 2 or i + length > len(data):
            return None
        if 0xC0 <= marker <= 0xCF and marker not in {0xC4, 0xC8, 0xCC}:
            if i + 7 <= len(data):
                h = struct.unpack(">H", data[i + 3:i + 5])[0]
                w = struct.unpack(">H", data[i + 5:i + 7])[0]
                return w, h
        i += length
    return None


def webp_size(data: bytes) -> tuple[int, int] | None:
    if data[:4] != b"RIFF" or data[8:12] != b"WEBP":
        return None
    chunk = data[12:16]
    if chunk == b"VP8X" and len(data) >= 30:
        w = 1 + int.from_bytes(data[24:27], "little")
        h = 1 + int.from_bytes(data[27:30], "little")
        return w, h
    if chunk == b"VP8 " and len(data) >= 30:
        w = struct.unpack("<H", data[26:28])[0] & 0x3FFF
        h = struct.unpack("<H", data[28:30])[0] & 0x3FFF
        return w, h
    if chunk == b"VP8L" and len(data) >= 25:
        b0, b1, b2, b3 = data[21], data[22], data[23], data[24]
        w = 1 + (((b1 & 0x3F) << 8) | b0)
        h = 1 + (((b3 & 0x0F) << 10) | (b2 << 2) | ((b1 & 0xC0) >> 6))
        return w, h
    return None


def image_size(path: Path) -> tuple[int | None, int | None]:
    data = path.read_bytes()[:65536]
    ext = path.suffix.lower()
    size = None
    if ext == ".png":
        size = png_size(data)
    elif ext in {".jpg", ".jpeg"}:
        size = jpg_size(data)
    elif ext == ".webp":
        size = webp_size(data)
    return size or (None, None)


def recommendation(path: Path, bytes_size: int, w: int | None, h: int | None) -> str:
    rel = path.relative_to(ROOT).as_posix()
    ext = path.suffix.lower()
    if rel.startswith("assets/services/") and ext == ".png" and bytes_size > 500_000:
        return "service PNG: проверить WebP/JPG-копию или более лёгкий экспорт из Figma"
    if ext in {".jpg", ".jpeg"} and bytes_size > 400_000:
        return "JPEG: уменьшить разрешение под реальный размер на странице + progressive quality 88-92"
    if ext == ".png" and bytes_size > 400_000:
        return "PNG: если нет прозрачности — лучше JPG/WebP; если есть — оптимизировать экспорт"
    if ext == ".webp" and bytes_size > 250_000:
        return "WebP: проверить, не слишком ли большое разрешение/качество"
    if w and h and max(w, h) > 1600 and bytes_size > 200_000:
        return "крупное разрешение: проверить реальный размер показа на странице"
    return "ok"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--top", type=int, default=40, help="How many largest files to print")
    args = parser.parse_args()

    rows = []
    for path in ROOT.joinpath("assets").rglob("*"):
        if not path.is_file() or path.suffix.lower() not in IMAGE_EXTS:
            continue
        size = path.stat().st_size
        w, h = image_size(path)
        rows.append((size, path, w, h, recommendation(path, size, w, h)))

    rows.sort(reverse=True, key=lambda item: item[0])
    total = sum(row[0] for row in rows)
    print(f"Images: {len(rows)} files, total {human_size(total)}")
    print()
    print("| Size | Dimensions | File | Recommendation |")
    print("|---:|---:|---|---|")
    for size, path, w, h, rec in rows[:args.top]:
        dims = f"{w}×{h}" if w and h else "?"
        rel = path.relative_to(ROOT).as_posix()
        print(f"| {human_size(size)} | {dims} | `{rel}` | {rec} |")


if __name__ == "__main__":
    main()
