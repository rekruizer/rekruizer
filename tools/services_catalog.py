"""Shared validation and presentation helpers for the services catalogue."""

from __future__ import annotations

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
    if value.get("schemaVersion") not in {1, 2}:
        raise CatalogValidationError("Unsupported services-presentation schemaVersion")
    category_ids = value.get("categoryIds")
    pages = value.get("pages")
    rows = value.get("services")
    subscription_rows = value.get("subscriptions")
    if not isinstance(category_ids, dict) or not category_ids:
        raise CatalogValidationError("services-presentation has no categoryIds")
    if not isinstance(pages, dict) or not pages:
        raise CatalogValidationError("services-presentation has no pages")
    if not isinstance(rows, list) or not rows:
        raise CatalogValidationError("services-presentation has no services")
    if not isinstance(subscription_rows, list):
        raise CatalogValidationError("services-presentation has no subscriptions")

    ids: set[str] = set()
    offer_ids: set[str] = set()
    primary_slugs: set[str] = set()
    for row in rows:
        if not isinstance(row, dict):
            raise CatalogValidationError("Invalid services-presentation row")
        service_id = str(row.get("id", ""))
        slug = row.get("slug")
        offer_id = row.get("offerId")
        image_file = row.get("imageFile")
        site_image_file = row.get("siteImageFile")
        if not re.fullmatch(r"\d+", service_id):
            raise CatalogValidationError(f"Invalid service id in presentation: {service_id!r}")
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
        if not isinstance(site_image_file, str) or not re.fullmatch(
            r"[a-z0-9-]+\.webp", site_image_file
        ):
            raise CatalogValidationError(
                f"Invalid local WebP siteImageFile for service {service_id}"
            )
        if service_id in ids or offer_id in offer_ids:
            raise CatalogValidationError(
                "Duplicate service id or offerId in presentation"
            )
        ids.add(service_id)
        offer_ids.add(offer_id)
        if row.get("primaryForPage"):
            if slug in primary_slugs:
                raise CatalogValidationError(f"More than one primary service for /services/{slug}/")
            primary_slugs.add(slug)
        old_price = row.get("oldPriceRub")
        if old_price is not None and (not isinstance(old_price, int) or old_price <= 0):
            raise CatalogValidationError(f"Invalid oldPriceRub for service {service_id}")
        display_name = row.get("displayName")
        if display_name is not None and (
            not isinstance(display_name, str)
            or not display_name.strip()
            or len(display_name) > 160
        ):
            raise CatalogValidationError(f"Invalid displayName for service {service_id}")

    featured_subscriptions = 0
    regular_ids = set(ids)
    for row in subscription_rows:
        if not isinstance(row, dict):
            raise CatalogValidationError("Invalid subscription presentation row")
        service_id = str(row.get("id", ""))
        offer_id = row.get("offerId")
        image_file = row.get("imageFile")
        sessions = row.get("sessions")
        reference_service_id = str(row.get("referenceServiceId", ""))
        if not re.fullmatch(r"\d+|abonement:[1-9]\d*", service_id):
            raise CatalogValidationError(
                f"Invalid subscription id: {service_id!r}"
            )
        if not isinstance(offer_id, str) or not re.fullmatch(r"[a-z0-9-]+", offer_id):
            raise CatalogValidationError(
                f"Invalid feed offerId for subscription {service_id}"
            )
        if not isinstance(image_file, str) or not re.fullmatch(
            r"[a-z0-9-]+\.webp", image_file
        ):
            raise CatalogValidationError(
                f"Invalid local WebP imageFile for subscription {service_id}"
            )
        if not isinstance(sessions, int) or isinstance(sessions, bool) or sessions <= 1:
            raise CatalogValidationError(
                f"Invalid session count for subscription {service_id}"
            )
        if reference_service_id not in regular_ids:
            raise CatalogValidationError(
                f"Invalid reference service for subscription {service_id}"
            )
        if service_id in ids or offer_id in offer_ids:
            raise CatalogValidationError(
                "Duplicate service id or offerId in presentation"
            )
        ids.add(service_id)
        offer_ids.add(offer_id)
        if row.get("featured"):
            featured_subscriptions += 1

    if featured_subscriptions > 1:
        raise CatalogValidationError("More than one featured subscription")

    slugs = {str(row["slug"]) for row in rows}
    for slug in slugs:
        page = pages.get(slug)
        if not isinstance(page, dict):
            raise CatalogValidationError(f"Missing page content for /services/{slug}/")
        for field, maximum in (
            ("title", 120),
            ("cardTitle", 120),
            ("cardDescription", 300),
            ("description", 5000),
        ):
            text = page.get(field)
            if not isinstance(text, str) or not text.strip() or len(text) > maximum:
                raise CatalogValidationError(
                    f"Invalid {field} for /services/{slug}/"
                )
        field_sources = page.get("fieldSources")
        if field_sources is not None:
            if not isinstance(field_sources, dict):
                raise CatalogValidationError(
                    f"Invalid fieldSources for /services/{slug}/"
                )
            for field in ("title", "cardTitle", "cardDescription", "description"):
                source = field_sources.get(field)
                if not isinstance(source, dict) or source.get("type") not in {
                    "manual",
                    "dikidi",
                    "yclients",
                }:
                    raise CatalogValidationError(
                        f"Invalid source for {field} in /services/{slug}/"
                    )
                if source["type"] in {"dikidi", "yclients"} and not re.fullmatch(
                    r"\d+", str(source.get("serviceId", ""))
                ):
                    raise CatalogValidationError(
                        f"Missing source service for {field} in /services/{slug}/"
                    )
    missing_primary = slugs - primary_slugs
    if missing_primary:
        raise CatalogValidationError(
            f"Missing primaryForPage for: {', '.join(sorted(missing_primary))}"
        )
    all_rows = rows + subscription_rows
    meta_ids = [str(row.get("metaItemId", row["id"])) for row in all_rows]
    if len(set(meta_ids)) != len(meta_ids) or any(not re.fullmatch(r"[a-zA-Z0-9:_-]{1,100}", item) for item in meta_ids):
        raise CatalogValidationError("Invalid or duplicate stable Meta item ids")
    if value.get("schemaVersion") == 2:
        if value.get("provider") != "YCLIENTS":
            raise CatalogValidationError("Version 2 presentation requires an explicit YCLIENTS provider")
        source_categories = value.get("sourceCategoryIds")
        if not isinstance(source_categories, dict) or not source_categories or any(
            not re.fullmatch(r"(?:abonement-category:)?[1-9]\d*", str(key)) or not re.fullmatch(r"[1-9]\d*", str(item))
            for key, item in source_categories.items()
        ):
            raise CatalogValidationError("Invalid YCLIENTS to stable feed category mapping")
    return value


def validate_catalog(
    value: dict[str, Any],
    presentation: dict[str, Any],
    *,
    require_local_images: bool = False,
) -> dict[str, Any]:
    if (value.get("schemaVersion"), value.get("provider")) not in {(1, "DIKIDI"), (2, "YCLIENTS")}:
        raise CatalogValidationError("Unsupported services catalogue schema or provider")
    if value.get("provider") != presentation.get("provider", "DIKIDI"):
        raise CatalogValidationError("Catalogue and presentation providers do not match; migration must be paired")
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
        if not re.fullmatch(r"\d+|abonement:[1-9]\d*", service_id) or service_id in by_id:
            raise CatalogValidationError(f"Invalid or duplicate service id: {service_id!r}")
        if value["provider"] == "YCLIENTS":
            kind = service.get("entityType")
            source_id = str(service.get("sourceId", ""))
            if kind not in {"service", "subscription"} or not re.fullmatch(r"[1-9]\d*", source_id):
                raise CatalogValidationError(f"Service {service_id} has invalid YCLIENTS identity")
            if service_id != (f"abonement:{source_id}" if kind == "subscription" else source_id):
                raise CatalogValidationError(f"Service {service_id} has inconsistent entity identity")
            category_pattern = r"abonement-category:[1-9]\d*" if kind == "subscription" else r"[1-9]\d*"
            if not re.fullmatch(category_pattern, str(service.get("categoryId", ""))):
                raise CatalogValidationError(f"Service {service_id} has no source category id")
        for field in ("category", "name", "bookingUrl"):
            if not isinstance(service.get(field), str) or not service[field].strip():
                raise CatalogValidationError(
                    f"Service {service_id} has an invalid {field}"
                )
        if not isinstance(service.get("description"), str):
            raise CatalogValidationError(
                f"Service {service_id} has an invalid description"
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
        # Older snapshots include an image copied from DIKIDI. It is accepted
        # for backwards compatibility but never used by the website. The
        # checked-in PNG source library is the only image source of truth.
        image = service.get("image")
        if image is not None and not isinstance(image, dict):
            raise CatalogValidationError(f"Service {service_id} has invalid legacy image metadata")
        by_id[service_id] = service

    mapped_ids = {
        str(row["id"])
        for row in presentation["services"] + presentation["subscriptions"]
    }
    # New DIKIDI services are allowed. Until an image is selected in the site
    # presentation they remain visible as an admin task instead of blocking an
    # otherwise healthy catalogue deployment. Stale presentation rows are also
    # allowed so a removed service can disappear without losing its settings.
    available_mapped_ids = mapped_ids & set(by_id)
    unpublished_mapped_ids = {
        service_id
        for service_id in available_mapped_ids
        if not by_id[service_id]["published"]
    }
    available_mapped_ids -= unpublished_mapped_ids

    catalogue_categories = {
        by_id[service_id]["category"] for service_id in available_mapped_ids
    }
    missing_categories = catalogue_categories - set(presentation["categoryIds"]) if value["provider"] == "DIKIDI" else {
        by_id[service_id]["categoryId"] for service_id in available_mapped_ids
        if by_id[service_id]["categoryId"] not in presentation["sourceCategoryIds"]
    }
    if missing_categories:
        raise CatalogValidationError(
            f"Missing stable category ids for: {', '.join(sorted(missing_categories))}"
        )

    for row in presentation["subscriptions"]:
        if str(row["id"]) not in by_id:
            continue
        subscription = by_id[str(row["id"])]
        reference = by_id.get(str(row["referenceServiceId"]))
        if value["provider"] == "YCLIENTS":
            if subscription.get("entityType") != "subscription" or subscription.get("sessions") != row["sessions"] or subscription.get("referenceServiceId") != row["referenceServiceId"]:
                raise CatalogValidationError(f"Subscription {subscription['id']} facts differ from its presentation mapping")
        elif not (
            subscription["category"].casefold().startswith("абонемент")
            or subscription["name"].casefold().startswith("абонемент")
        ):
            raise CatalogValidationError(
                f"Service {subscription['id']} is not a subscription"
            )
        if reference is None:
            continue
        if subscription["durationMinutes"] != reference["durationMinutes"]:
            raise CatalogValidationError(
                f"Subscription {subscription['id']} duration does not match "
                f"reference service {reference['id']}"
            )
        regular_total = reference["priceRub"] * row["sessions"]
        if value["provider"] == "DIKIDI" and subscription["priceRub"] > regular_total:
            raise CatalogValidationError(
                f"Subscription {subscription['id']} costs more than separate sessions"
            )

    if require_local_images:
        all_rows = presentation["services"] + presentation["subscriptions"]
        rows_by_id = {str(row["id"]): row for row in all_rows}
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
        for row in presentation["services"]:
            path = local_site_image_path(row)
            if not path.is_file():
                raise CatalogValidationError(
                    f"Missing local site image: {path.relative_to(ROOT)}"
                )
            data = path.read_bytes()
            if len(data) < 1024 or len(data) > 8 * 1024 * 1024:
                raise CatalogValidationError(
                    f"Invalid local site WebP size: {path.relative_to(ROOT)}"
                )
            if data[:4] != b"RIFF" or data[8:12] != b"WEBP":
                raise CatalogValidationError(
                    f"Invalid local site WebP content: {path.relative_to(ROOT)}"
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
    presentation_by_id = {
        str(row["id"]): row for row in presentation["services"]
    }
    result: list[tuple[dict[str, Any], dict[str, Any]]] = []
    # The catalogue is stored in the provider's display order. Presentation metadata
    # decides how an item is rendered, but must not become a second ranking
    # system for ordinary services.
    for source_service in catalogue["services"]:
        row = presentation_by_id.get(str(source_service["id"]))
        if row is None or not source_service["published"]:
            continue
        service = source_service
        display_name = row.get("displayName")
        if isinstance(display_name, str):
            service = {**service, "name": display_name}
        # A source row is a bookable variant (for example 55 or 90 minutes),
        # not a separate editorial entity. All variants linked to the same
        # site page therefore publish the same canonical description. The raw
        # source copy stays in services-catalog.json and is available in the
        # admin as an optional source when editing the common page text.
        page = presentation["pages"].get(str(row["slug"]), {})
        page_description = str(page.get("description", "")).strip()
        service = {**service, "description": page_description}
        result.append((service, row))
    return result


def mapped_subscriptions(
    catalogue: dict[str, Any], presentation: dict[str, Any]
) -> list[tuple[dict[str, Any], dict[str, Any]]]:
    by_id = {str(service["id"]): service for service in catalogue["services"]}
    result: list[tuple[dict[str, Any], dict[str, Any]]] = []
    for row in presentation["subscriptions"]:
        service = by_id.get(str(row["id"]))
        if service is None or not service["published"]:
            continue
        if str(row["referenceServiceId"]) not in by_id:
            continue
        if not service.get("description", "").strip():
            service = {
                **service,
                "description": (
                    f"{service['name']}. Продолжительность — "
                    f"{service['durationMinutes']} минут."
                ),
            }
        if row.get("groupLabel"):
            service = {**service, "description": f"{row['groupLabel']}. {service['description']}"}
        result.append((service, row))
    return result


def stable_category_id(service: dict[str, Any], presentation: dict[str, Any]) -> str:
    """Renaming a source category must not change its external feed identity."""
    if presentation.get("provider") == "YCLIENTS":
        return str(presentation["sourceCategoryIds"][service["categoryId"]])
    return str(presentation["categoryIds"][service["category"]])


def mapped_catalogue_items(
    catalogue: dict[str, Any], presentation: dict[str, Any]
) -> list[tuple[dict[str, Any], dict[str, Any]]]:
    return mapped_services(catalogue, presentation) + mapped_subscriptions(
        catalogue, presentation
    )


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


def local_site_image_path(row: dict[str, Any]) -> Path:
    return SERVICE_IMAGES_DIR / str(row["siteImageFile"])


def public_image_path(
    service: dict[str, Any], row: dict[str, Any]
) -> str:
    if str(service["id"]) != str(row["id"]):
        raise CatalogValidationError("Service and local image mapping ids do not match")
    path = local_image_path(row)
    return "/" + path.relative_to(ROOT).as_posix()


def public_site_image_path(
    service: dict[str, Any], row: dict[str, Any]
) -> str:
    if str(service["id"]) != str(row["id"]):
        raise CatalogValidationError("Service and site image mapping ids do not match")
    path = local_site_image_path(row)
    return "/" + path.relative_to(ROOT).as_posix()


def format_rubles(value: int) -> str:
    return f"{value:,}".replace(",", " ") + " ₽"
