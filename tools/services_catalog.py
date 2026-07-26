"""Shared validation and presentation helpers for the services catalogue."""

from __future__ import annotations

import hashlib
import json
import re
from collections import defaultdict
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent.parent
CATALOG_PATH = ROOT / "assets" / "data" / "services-catalog.json"
PRESENTATION_PATH = ROOT / "assets" / "data" / "services-presentation.json"
SERVICE_IMAGES_DIR = ROOT / "assets" / "services"

CONTENT_TYPE_EXTENSIONS = {
    "image/jpeg": "jpg",
    "image/png": "png",
    "image/webp": "webp",
    "image/avif": "avif",
}


class CatalogValidationError(RuntimeError):
    pass


def _read_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise CatalogValidationError(f"Cannot read {path.relative_to(ROOT)}: {error}") from error
    if not isinstance(value, dict):
        raise CatalogValidationError(f"{path.relative_to(ROOT)} must contain a JSON object")
    return value


def validate_presentation(value: dict[str, Any]) -> dict[str, Any]:
    if value.get("schemaVersion") != 1:
        raise CatalogValidationError("Unsupported services-presentation schemaVersion")
    category_ids = value.get("categoryIds")
    rows = value.get("services")
    if not isinstance(category_ids, dict) or not category_ids:
        raise CatalogValidationError("services-presentation has no categoryIds")
    if not isinstance(rows, list) or not rows:
        raise CatalogValidationError("services-presentation has no services")

    ids: set[str] = set()
    offer_ids: set[str] = set()
    image_files: set[str] = set()
    primary_slugs: set[str] = set()
    for row in rows:
        if not isinstance(row, dict):
            raise CatalogValidationError("Invalid services-presentation row")
        service_id = str(row.get("id", ""))
        slug = row.get("slug")
        offer_id = row.get("offerId")
        image_file = row.get("imageFile")
        if not re.fullmatch(r"\d+", service_id):
            raise CatalogValidationError(f"Invalid DIKIDI id in presentation: {service_id!r}")
        if not isinstance(slug, str) or not re.fullmatch(r"[a-z0-9-]+", slug):
            raise CatalogValidationError(f"Invalid page slug for service {service_id}")
        if not isinstance(offer_id, str) or not re.fullmatch(r"[a-z0-9-]+", offer_id):
            raise CatalogValidationError(f"Invalid feed offerId for service {service_id}")
        if not isinstance(image_file, str) or not re.fullmatch(
            r"[a-z0-9-]+\.webp", image_file
        ):
            raise CatalogValidationError(
                f"Invalid local WebP imageFile for service {service_id}"
            )
        if service_id in ids or offer_id in offer_ids or image_file in image_files:
            raise CatalogValidationError(
                "Duplicate service id, offerId or imageFile in presentation"
            )
        ids.add(service_id)
        offer_ids.add(offer_id)
        image_files.add(image_file)
        if row.get("primaryForPage"):
            if slug in primary_slugs:
                raise CatalogValidationError(f"More than one primary service for /services/{slug}/")
            primary_slugs.add(slug)
        old_price = row.get("oldPriceRub")
        if old_price is not None and (not isinstance(old_price, int) or old_price <= 0):
            raise CatalogValidationError(f"Invalid oldPriceRub for service {service_id}")

    slugs = {str(row["slug"]) for row in rows}
    missing_primary = slugs - primary_slugs
    if missing_primary:
        raise CatalogValidationError(
            f"Missing primaryForPage for: {', '.join(sorted(missing_primary))}"
        )
    return value


def validate_catalog(
    value: dict[str, Any],
    presentation: dict[str, Any],
    *,
    require_local_images: bool = False,
) -> dict[str, Any]:
    if value.get("schemaVersion") != 1 or value.get("provider") != "DIKIDI":
        raise CatalogValidationError("Unsupported services catalogue schema or provider")
    content_hash = value.get("contentHash")
    if not isinstance(content_hash, str) or not re.fullmatch(r"[a-f0-9]{64}", content_hash):
        raise CatalogValidationError("Catalogue has an invalid contentHash")
    services = value.get("services")
    if not isinstance(services, list) or not services:
        raise CatalogValidationError("Catalogue has no services")

    by_id: dict[str, dict[str, Any]] = {}
    for service in services:
        if not isinstance(service, dict):
            raise CatalogValidationError("Catalogue contains an invalid service")
        service_id = str(service.get("id", ""))
        if not re.fullmatch(r"\d+", service_id) or service_id in by_id:
            raise CatalogValidationError(f"Invalid or duplicate service id: {service_id!r}")
        for field in ("category", "name", "description", "bookingUrl"):
            if not isinstance(service.get(field), str) or not service[field].strip():
                raise CatalogValidationError(
                    f"Service {service_id} has an invalid {field}"
                )
        if not service["bookingUrl"].startswith("https://"):
            raise CatalogValidationError(f"Service {service_id} has an unsafe bookingUrl")
        duration = service.get("durationMinutes")
        price = service.get("priceRub")
        if not isinstance(duration, int) or duration <= 0 or duration > 240:
            raise CatalogValidationError(f"Service {service_id} has an invalid duration")
        if not isinstance(price, int) or price < 0:
            raise CatalogValidationError(f"Service {service_id} has an invalid price")
        if not isinstance(service.get("published"), bool):
            raise CatalogValidationError(f"Service {service_id} has no published flag")
        image = service.get("image")
        if not isinstance(image, dict):
            raise CatalogValidationError(f"Service {service_id} has no image metadata")
        image_hash = image.get("sha256")
        content_type = image.get("contentType")
        byte_length = image.get("byteLength")
        image_url = image.get("url")
        if not isinstance(image_hash, str) or not re.fullmatch(r"[a-f0-9]{64}", image_hash):
            raise CatalogValidationError(f"Service {service_id} has an invalid image hash")
        if content_type not in CONTENT_TYPE_EXTENSIONS:
            raise CatalogValidationError(f"Service {service_id} has an unsupported image type")
        if not isinstance(byte_length, int) or byte_length < 1024 or byte_length > 8 * 1024 * 1024:
            raise CatalogValidationError(f"Service {service_id} has an invalid image size")
        if not isinstance(image_url, str) or not image_url.startswith("https://"):
            raise CatalogValidationError(f"Service {service_id} has an invalid image URL")
        by_id[service_id] = service

    mapped_ids = {str(row["id"]) for row in presentation["services"]}
    published_ids = {
        service_id for service_id, service in by_id.items() if service["published"]
    }
    if published_ids != mapped_ids:
        missing = sorted(mapped_ids - published_ids)
        unexpected = sorted(published_ids - mapped_ids)
        details = []
        if missing:
            details.append(f"missing published services: {', '.join(missing)}")
        if unexpected:
            details.append(f"unmapped published services: {', '.join(unexpected)}")
        raise CatalogValidationError("; ".join(details))

    catalogue_categories = {by_id[service_id]["category"] for service_id in mapped_ids}
    missing_categories = catalogue_categories - set(presentation["categoryIds"])
    if missing_categories:
        raise CatalogValidationError(
            f"Missing stable category ids for: {', '.join(sorted(missing_categories))}"
        )

    if require_local_images:
        rows_by_id = {
            str(row["id"]): row for row in presentation["services"]
        }
        for service_id in mapped_ids:
            path = local_image_path(rows_by_id[service_id])
            if not path.is_file():
                raise CatalogValidationError(
                    f"Missing local image: {path.relative_to(ROOT)}"
                )
            data = path.read_bytes()
            if len(data) < 1024 or len(data) > 8 * 1024 * 1024:
                raise CatalogValidationError(
                    f"Invalid local WebP size: {path.relative_to(ROOT)}"
                )
            if data[:4] != b"RIFF" or data[8:12] != b"WEBP":
                raise CatalogValidationError(
                    f"Invalid local WebP content: {path.relative_to(ROOT)}"
                )
    return value


def load_presentation() -> dict[str, Any]:
    return validate_presentation(_read_json(PRESENTATION_PATH))


def load_catalog(*, require_local_images: bool = True) -> tuple[dict[str, Any], dict[str, Any]]:
    presentation = load_presentation()
    catalogue = validate_catalog(
        _read_json(CATALOG_PATH),
        presentation,
        require_local_images=require_local_images,
    )
    return catalogue, presentation


def mapped_services(
    catalogue: dict[str, Any], presentation: dict[str, Any]
) -> list[tuple[dict[str, Any], dict[str, Any]]]:
    by_id = {str(service["id"]): service for service in catalogue["services"]}
    return [(by_id[str(row["id"])], row) for row in presentation["services"]]


def services_by_slug(
    catalogue: dict[str, Any], presentation: dict[str, Any]
) -> dict[str, list[tuple[dict[str, Any], dict[str, Any]]]]:
    result: dict[str, list[tuple[dict[str, Any], dict[str, Any]]]] = defaultdict(list)
    for service, row in mapped_services(catalogue, presentation):
        result[str(row["slug"])].append((service, row))
    return dict(result)


def primary_service(
    rows: list[tuple[dict[str, Any], dict[str, Any]]]
) -> tuple[dict[str, Any], dict[str, Any]]:
    return next((item for item in rows if item[1].get("primaryForPage")), rows[0])


def local_image_path(row: dict[str, Any]) -> Path:
    return SERVICE_IMAGES_DIR / str(row["imageFile"])


def public_image_path(
    service: dict[str, Any], row: dict[str, Any]
) -> str:
    if str(service["id"]) != str(row["id"]):
        raise CatalogValidationError("Service and local image mapping ids do not match")
    path = local_image_path(row)
    digest = hashlib.sha256(path.read_bytes()).hexdigest()[:12]
    return "/" + path.relative_to(ROOT).as_posix() + f"?v={digest}"


def format_rubles(value: int) -> str:
    return f"{value:,}".replace(",", " ") + " ₽"
