"""Public, non-sensitive evidence of the catalogue actually built into the site."""
from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone

from services_catalog import ROOT, mapped_catalogue_items


def item_fingerprint(service: dict, row: dict, page: dict | None) -> str:
    page = page or {}
    fields = [
        service["id"], service["name"], service.get("categoryId", ""), service["category"],
        service["priceRub"], service.get("priceMaxRub"), service["durationMinutes"],
        service["description"], service["bookingUrl"], service.get("bookingAction", ""),
        service.get("sessions"), service.get("referenceServiceId", ""), service["published"],
        row.get("slug", ""), row.get("offerId", ""), row.get("metaItemId", ""),
        row.get("imageFile", ""), row.get("siteImageFile", ""), row.get("displayName", ""),
        row.get("groupLabel", ""), row.get("oldPriceRub"), bool(row.get("primaryForPage")),
        bool(row.get("featured")), page.get("title", ""), page.get("cardTitle", ""),
        page.get("cardDescription", ""), page.get("description", ""),
    ]
    encoded = json.dumps(fields, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def publication_manifest(catalogue: dict, presentation: dict) -> dict:
    content = (ROOT / "assets/data/services-presentation.json").read_bytes()
    presentation_sha = hashlib.sha1(b"blob " + str(len(content)).encode() + b"\0" + content).hexdigest()
    source_by_id = {str(service["id"]): service for service in catalogue["services"]}
    return {
        "schemaVersion": 1,
        "catalogHash": catalogue["contentHash"],
        "presentationSha": presentation_sha,
        "builtAt": datetime.now(timezone.utc).isoformat(),
        "services": [
            {"id": str(item["id"]), "fingerprint": item_fingerprint(
                source_by_id[str(item["id"])], row, presentation["pages"].get(row.get("slug", ""))
            )}
            for item, row in mapped_catalogue_items(catalogue, presentation)
        ],
    }
