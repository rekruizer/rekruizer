#!/usr/bin/env python3
"""Install a validated services snapshot using explicit local WebP images."""

from __future__ import annotations

import argparse
import json
import os
import ssl
import sys
import tempfile
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any

from services_catalog import (
    CATALOG_PATH,
    CatalogValidationError,
    load_presentation,
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
            headers = {
                "Accept": accept,
                "User-Agent": "denisyuce.com-services-sync/1.0",
            }
            read_token = os.environ.get(
                "SERVICES_CATALOG_READ_TOKEN"
            ) or os.environ.get("CATALOG_READ_SECRET")
            if read_token:
                headers["X-Services-Catalog-Token"] = read_token
            request = urllib.request.Request(
                url,
                headers=headers,
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


def existing_snapshot_matches(
    remote: dict[str, Any], presentation: dict[str, Any]
) -> bool:
    if not CATALOG_PATH.is_file():
        return False
    try:
        current = json.loads(CATALOG_PATH.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return False
    if not isinstance(current, dict):
        return False
    expected_ids = {
        str(row["id"])
        for row in presentation["services"] + presentation["subscriptions"]
    }
    current_services = current.get("services")
    if not isinstance(current_services, list):
        return False
    current_ids = {
        str(service.get("id"))
        for service in current_services
        if isinstance(service, dict)
    }
    return (
        current.get("contentHash") == remote["contentHash"]
        and current_ids == expected_ids
    )


def install_catalogue(value: dict[str, Any]) -> bool:
    presentation = load_presentation()
    validate_catalog(value, presentation)
    if existing_snapshot_matches(value, presentation):
        current = json.loads(CATALOG_PATH.read_text(encoding="utf-8"))
        validate_catalog(current, presentation, require_local_images=True)
        # lastCheckedAt changes every day; contentHash changes only when catalogue
        # content changes, so unchanged days must not create noisy Git commits.
        print(f"Services catalogue unchanged: {value['contentHash']}")
        return False

    presentation_rows = presentation["services"] + presentation["subscriptions"]
    published_ids = {str(row["id"]) for row in presentation_rows}
    public_value = {
        **value,
        "services": [
            service
            for service in value["services"]
            if str(service["id"]) in published_ids
        ],
    }
    validate_catalog(public_value, presentation, require_local_images=True)

    with tempfile.TemporaryDirectory(prefix="denisyuce-services-") as temp_name:
        temp = Path(temp_name)
        temporary_catalogue = temp / "services-catalog.json"
        temporary_catalogue.write_text(
            json.dumps(public_value, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        CATALOG_PATH.parent.mkdir(parents=True, exist_ok=True)
        temporary_catalogue.replace(CATALOG_PATH)

    validate_catalog(public_value, presentation, require_local_images=True)
    print(
        f"Installed services catalogue {value['contentHash']}: "
        f"{len(presentation_rows)} published services and subscriptions, "
        f"{len(presentation_rows)} local WebP images"
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
