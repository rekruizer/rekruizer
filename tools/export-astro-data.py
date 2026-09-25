#!/usr/bin/env python3
"""Export the validated services snapshot for the Astro presentation layer."""

from __future__ import annotations

import json
from decimal import Decimal
from pathlib import Path

from services_catalog import (
    ROOT,
    format_rubles,
    load_catalog,
    mapped_services,
    mapped_subscriptions,
    primary_service,
    public_site_image_path,
    services_by_slug,
)


OUTPUT = ROOT / "src" / "generated" / "services.json"


def per_session(total: int, sessions: int) -> str:
    value = (Decimal(total) / Decimal(sessions)).quantize(Decimal("0.01"))
    if value == value.to_integral():
        return format_rubles(int(value))
    whole, fraction = f"{value:.2f}".split(".")
    return f"{int(whole):,}".replace(",", " ") + f",{fraction} ₽"


def service_item(service: dict, row: dict) -> dict:
    return {
        "id": str(service["id"]),
        "name": service["name"],
        "category": service["category"],
        "durationMinutes": service["durationMinutes"],
        "priceRub": service["priceRub"],
        "price": format_rubles(service["priceRub"]),
        "oldPriceRub": row.get("oldPriceRub"),
        "oldPrice": format_rubles(row["oldPriceRub"]) if row.get("oldPriceRub") else None,
        "bookingUrl": service["bookingUrl"],
        "slug": row["slug"],
        "goal": f"service_{row['slug'].replace('-', '_')}_{service['durationMinutes']}_click",
        "image": public_site_image_path(service, row),
        "primaryForPage": bool(row.get("primaryForPage")),
    }


def main() -> None:
    catalogue, presentation = load_catalog(require_local_images=True)
    grouped = services_by_slug(catalogue, presentation)
    services = [service_item(service, row) for service, row in mapped_services(catalogue, presentation)]
    groups = []
    for slug, rows in grouped.items():
        primary, primary_row = primary_service(rows)
        groups.append(
            {
                "slug": slug,
                "page": presentation["pages"][slug],
                "category": primary["category"],
                "image": public_site_image_path(primary, primary_row),
                "imageAlt": primary["name"],
                "services": [service_item(service, row) for service, row in rows],
            }
        )

    by_id = {str(service["id"]): service for service in catalogue["services"]}
    subscriptions = []
    for service, row in mapped_subscriptions(catalogue, presentation):
        sessions = int(row["sessions"])
        reference = by_id[str(row["referenceServiceId"])]
        saving = reference["priceRub"] * sessions - service["priceRub"]
        subscriptions.append(
            {
                "id": str(service["id"]),
                "name": service["name"],
                "durationMinutes": service["durationMinutes"],
                "bookingUrl": service["bookingUrl"],
                "sessions": sessions,
                "featured": bool(row.get("featured")),
                "price": format_rubles(service["priceRub"]),
                "perSession": per_session(service["priceRub"], sessions),
                "regularPrice": format_rubles(reference["priceRub"]),
                "saving": format_rubles(saving),
                "goal": f"service_sub_{sessions}_{service['durationMinutes']}_click",
            }
        )

    payload = {
        "contentHash": catalogue["contentHash"],
        "categories": list(dict.fromkeys(service["category"] for service, _ in mapped_services(catalogue, presentation))),
        "services": services,
        "groups": groups,
        "subscriptions": subscriptions,
    }
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Exported {len(services)} services and {len(groups)} pages for Astro")


if __name__ == "__main__":
    main()
