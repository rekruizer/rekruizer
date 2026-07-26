#!/usr/bin/env python3
"""Download one fully validated services snapshot and its immutable images."""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import ssl
import sys
import tempfile
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any

from services_catalog import (
    CATALOG_IMAGES_DIR,
    CATALOG_PATH,
    CatalogValidationError,
    ROOT,
    load_presentation,
    local_image_path,
    validate_catalog,
)


DEFAULT_CATALOG_URL = (
    "https://denisyuce-services-catalog.den100hero.workers.dev/services-catalog.json"
)


def verified_ssl_context() -> ssl.SSLContext:
    """Use the system CA store, with certifi as a macOS Python fallback."""
    try:
        import certifi  # type: ignore[import-not-found]

        return ssl.create_default_context(cafile=certifi.where())
    except ImportError:
        return ssl.create_default_context()


def download(url: str, *, accept: str, attempts: int = 2) -> tuple[bytes, str]:
    last_error: Exception | None = None
    for attempt in range(attempts):
        try:
            request = urllib.request.Request(
                url,
                headers={
                    "Accept": accept,
                    "User-Agent": "denisyuce.com-services-sync/1.0",
                },
            )
            with urllib.request.urlopen(
                request,
                timeout=30,
                context=verified_ssl_context(),
            ) as response:
                return response.read(), response.headers.get_content_type()
        except (OSError, urllib.error.URLError, urllib.error.HTTPError) as error:
            last_error = error
            if attempt + 1 < attempts:
                time.sleep(2)
    raise RuntimeError(f"Cannot download {url}: {last_error}")


def fetch_catalogue(url: str) -> dict[str, Any]:
    body, content_type = download(url, accept="application/json")
    if content_type not in {"application/json", "text/json"}:
        raise CatalogValidationError(
            f"Catalogue endpoint returned unexpected type {content_type!r}"
        )
    try:
        value = json.loads(body)
    except json.JSONDecodeError as error:
        raise CatalogValidationError(f"Catalogue endpoint returned invalid JSON: {error}") from error
    if not isinstance(value, dict):
        raise CatalogValidationError("Catalogue endpoint returned a non-object JSON value")
    return value


def existing_hash() -> str | None:
    if not CATALOG_PATH.is_file():
        return None
    try:
        value = json.loads(CATALOG_PATH.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    content_hash = value.get("contentHash") if isinstance(value, dict) else None
    return content_hash if isinstance(content_hash, str) else None


def install_catalogue(value: dict[str, Any]) -> bool:
    presentation = load_presentation()
    validate_catalog(value, presentation)
    if existing_hash() == value["contentHash"]:
        # lastCheckedAt changes every day; contentHash changes only when catalogue
        # content changes, so unchanged days must not create noisy Git commits.
        print(f"Services catalogue unchanged: {value['contentHash']}")
        return False

    with tempfile.TemporaryDirectory(prefix="denisyuce-services-") as temp_name:
        temp = Path(temp_name)
        downloaded: dict[Path, Path] = {}
        published_ids = {str(row["id"]) for row in presentation["services"]}
        by_id = {str(service["id"]): service for service in value["services"]}
        for service_id in sorted(published_ids):
            service = by_id[service_id]
            destination = local_image_path(service)
            if destination.is_file():
                data = destination.read_bytes()
                if (
                    len(data) == service["image"]["byteLength"]
                    and hashlib.sha256(data).hexdigest() == service["image"]["sha256"]
                ):
                    continue
            body, content_type = download(
                service["image"]["url"],
                accept="image/avif,image/webp,image/png,image/jpeg,image/*;q=0.8",
            )
            if content_type != service["image"]["contentType"]:
                raise CatalogValidationError(
                    f"Image type mismatch for service {service_id}: {content_type}"
                )
            if len(body) != service["image"]["byteLength"]:
                raise CatalogValidationError(
                    f"Image size mismatch for service {service_id}"
                )
            if hashlib.sha256(body).hexdigest() != service["image"]["sha256"]:
                raise CatalogValidationError(
                    f"Image hash mismatch for service {service_id}"
                )
            temporary_image = temp / destination.name
            temporary_image.write_bytes(body)
            downloaded[destination] = temporary_image

        # Nothing is replaced until every service and every required image has
        # passed validation. The previous snapshot therefore remains deployable.
        CATALOG_IMAGES_DIR.mkdir(parents=True, exist_ok=True)
        for destination, temporary_image in downloaded.items():
            shutil.copyfile(temporary_image, destination)

        temporary_catalogue = temp / "services-catalog.json"
        temporary_catalogue.write_text(
            json.dumps(value, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        CATALOG_PATH.parent.mkdir(parents=True, exist_ok=True)
        temporary_catalogue.replace(CATALOG_PATH)

        referenced = {local_image_path(by_id[service_id]) for service_id in published_ids}
        for path in CATALOG_IMAGES_DIR.iterdir():
            if path.is_file() and path not in referenced:
                path.unlink()

    validate_catalog(value, presentation, require_local_images=True)
    print(
        f"Installed services catalogue {value['contentHash']}: "
        f"{len(presentation['services'])} published services, "
        f"{len(downloaded)} downloaded images"
    )
    return True


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--url",
        default=DEFAULT_CATALOG_URL,
        help="Read-only services-catalog.json endpoint",
    )
    parser.add_argument(
        "--require-remote",
        action="store_true",
        help="Fail instead of retaining the checked-in snapshot when download fails",
    )
    args = parser.parse_args()

    try:
        changed = install_catalogue(fetch_catalogue(args.url))
        print(f"changed={'true' if changed else 'false'}")
    except Exception as error:
        if args.require_remote or not CATALOG_PATH.is_file():
            raise SystemExit(f"Services sync failed; current site was not changed: {error}")
        try:
            presentation = load_presentation()
            current = json.loads(CATALOG_PATH.read_text(encoding="utf-8"))
            validate_catalog(current, presentation, require_local_images=True)
        except Exception as fallback_error:
            raise SystemExit(
                "Services sync failed and the local fallback is invalid: "
                f"{error}; fallback: {fallback_error}"
            )
        print(
            f"WARNING: remote services sync failed; using the last checked-in snapshot: {error}",
            file=sys.stderr,
        )
        print("changed=false")


if __name__ == "__main__":
    main()
