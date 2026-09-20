#!/usr/bin/env python3
"""Generate a Meta-compatible RSS catalogue and PNG image derivatives."""

from __future__ import annotations

import shutil
import struct
import subprocess
from pathlib import Path
from xml.etree.ElementTree import Element, ElementTree, SubElement, indent, register_namespace

from services_catalog import (
    ROOT,
    load_catalog,
    local_image_path,
    mapped_services,
    mapped_subscriptions,
)


SITE = "https://denisyuce.com"
OUTPUT_PATH = ROOT / "meta-services-feed.xml"
IMAGE_OUTPUT_DIR = ROOT / "assets" / "meta-services"
GOOGLE_NAMESPACE = "http://base.google.com/ns/1.0"
META_IMAGE_MAX_BYTES = 8 * 1024 * 1024
META_IMAGE_MIN_SIDE = 500
META_IMAGE_SIDE = 1200


def google_tag(name: str) -> str:
    return f"{{{GOOGLE_NAMESPACE}}}{name}"


def add(parent: Element, tag: str, text: object) -> Element:
    element = SubElement(parent, tag)
    element.text = str(text)
    return element


def png_dimensions(path: Path) -> tuple[int, int]:
    header = path.read_bytes()[:24]
    if len(header) != 24 or header[:8] != b"\x89PNG\r\n\x1a\n" or header[12:16] != b"IHDR":
        raise RuntimeError(f"Generated file is not a valid PNG: {path.relative_to(ROOT)}")
    return struct.unpack(">II", header[16:24])


def generate_png_images(rows: list[tuple[dict, dict]]) -> None:
    decoder = shutil.which("dwebp")
    optimizer = shutil.which("pngquant")
    if not decoder:
        raise RuntimeError(
            "dwebp is required to generate Meta PNG images (install the WebP tools package)"
        )
    if not optimizer:
        raise RuntimeError(
            "pngquant is required to optimize Meta PNG images"
        )

    IMAGE_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    expected: set[Path] = set()
    for service, row in rows:
        source = local_image_path(row)
        destination = IMAGE_OUTPUT_DIR / (Path(row["imageFile"]).stem + ".png")
        raw_destination = destination.with_suffix(".raw.png")
        expected.add(destination)
        subprocess.run(
            [
                decoder,
                str(source),
                "-resize",
                str(META_IMAGE_SIDE),
                str(META_IMAGE_SIDE),
                "-o",
                str(raw_destination),
            ],
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.PIPE,
        )
        try:
            subprocess.run(
                [
                    optimizer,
                    "--force",
                    "--strip",
                    "--quality=70-90",
                    "--speed=1",
                    "--output",
                    str(destination),
                    str(raw_destination),
                ],
                check=True,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.PIPE,
            )
        finally:
            raw_destination.unlink(missing_ok=True)
        width, height = png_dimensions(destination)
        if min(width, height) < META_IMAGE_MIN_SIDE:
            raise RuntimeError(
                f"Meta image is too small: {destination.relative_to(ROOT)} "
                f"({width}x{height})"
            )
        if destination.stat().st_size > META_IMAGE_MAX_BYTES:
            raise RuntimeError(
                f"Meta image exceeds 8 MB: {destination.relative_to(ROOT)}"
            )

    for stale in IMAGE_OUTPUT_DIR.glob("*.png"):
        if stale not in expected:
            stale.unlink()


def meta_image_url(row: dict) -> str:
    filename = Path(row["imageFile"]).stem + ".png"
    return f"{SITE}/assets/meta-services/{filename}"


def write_feed(rows: list[tuple[dict, dict]], subscription_ids: set[str]) -> None:
    register_namespace("g", GOOGLE_NAMESPACE)
    root = Element("rss", {"version": "2.0"})
    channel = SubElement(root, "channel")
    add(channel, "title", "Услуги массажа — Денис Пучков")
    add(channel, "link", SITE + "/")
    add(channel, "description", "Каталог услуг массажа в Москве")

    for service, row in rows:
        item = SubElement(channel, "item")
        item_id = str(service["id"])
        is_subscription = item_id in subscription_ids
        page_url = (
            SITE + "/#subscriptions"
            if is_subscription
            else f"{SITE}/services/{row['slug']}/"
        )

        add(item, google_tag("id"), item_id)
        add(item, google_tag("title"), service["name"])
        add(item, google_tag("description"), service["description"])
        add(item, google_tag("availability"), "in stock")
        add(item, google_tag("condition"), "new")

        old_price = row.get("oldPriceRub")
        if isinstance(old_price, int) and old_price > service["priceRub"]:
            add(item, google_tag("price"), f"{old_price:.2f} RUB")
            add(item, google_tag("sale_price"), f"{service['priceRub']:.2f} RUB")
        else:
            add(item, google_tag("price"), f"{service['priceRub']:.2f} RUB")

        add(item, google_tag("link"), page_url)
        add(item, google_tag("image_link"), meta_image_url(row))
        add(item, google_tag("brand"), "Денис Пучков")
        add(item, google_tag("mpn"), row["offerId"])
        # Professional Services catalogues expose this native field in
        # Commerce Manager as "Service category".
        add(item, google_tag("category"), service["category"])
        # Keep the generic product classification for feed compatibility.
        add(item, google_tag("product_type"), service["category"])
        # Professional Services catalogues do not expose product_type as a
        # product-set filter in every Commerce Manager interface. Custom label
        # 0 is consistently available and keeps category-based sets dynamic.
        add(item, google_tag("custom_label_0"), service["category"])

    indent(root, space="  ")
    ElementTree(root).write(OUTPUT_PATH, encoding="UTF-8", xml_declaration=True)


def main() -> None:
    catalogue, presentation = load_catalog(require_local_images=True)
    services = mapped_services(catalogue, presentation)
    subscriptions = mapped_subscriptions(catalogue, presentation)
    rows = services + subscriptions
    if not rows:
        raise SystemExit("No published services for the Meta catalogue")

    generate_png_images(rows)
    write_feed(rows, {str(service["id"]) for service, _row in subscriptions})
    print(
        f"Generated meta-services-feed.xml with {len(rows)} items and "
        f"{len(rows)} PNG images"
    )


if __name__ == "__main__":
    main()
