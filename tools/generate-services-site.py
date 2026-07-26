#!/usr/bin/env python3
"""Render the checked-in services snapshot into static website pages."""

from __future__ import annotations

import html
import json
import re
from pathlib import Path
from typing import Any

from services_catalog import (
    ROOT,
    format_rubles,
    load_catalog,
    mapped_services,
    primary_service,
    public_image_path,
    services_by_slug,
)


SITE = "https://denisyuce.com"
PRICE_PAGES = [ROOT / "index.html", ROOT / "services" / "index.html"]


def html_text(value: object) -> str:
    return html.escape(str(value), quote=False)


def html_attr(value: object) -> str:
    return html.escape(str(value), quote=True)


def description_html(value: str) -> str:
    paragraphs = [part.strip() for part in re.split(r"\n\s*\n", value) if part.strip()]
    return "".join(
        f"<p>{html_text(part).replace(chr(10), '<br>')}</p>" for part in paragraphs
    )


def replace_once(
    source: str,
    pattern: str,
    replacement: str,
    *,
    label: str,
    flags: int = 0,
) -> str:
    result, count = re.subn(pattern, replacement, source, count=1, flags=flags)
    if count != 1:
        raise RuntimeError(f"Could not replace {label}")
    return result


def price_markup(service: dict[str, Any], row: dict[str, Any]) -> str:
    current = format_rubles(service["priceRub"])
    old_price = row.get("oldPriceRub")
    if isinstance(old_price, int) and old_price > service["priceRub"]:
        return (
            f'<span class="old-price">{format_rubles(old_price)}</span>'
            f'<span class="new-price">{current}</span>'
        )
    return current


def service_goal(row: dict[str, Any], service: dict[str, Any]) -> str:
    return f"service_{row['slug'].replace('-', '_')}_{service['durationMinutes']}_click"


def render_price_rows(
    catalogue: dict[str, Any], presentation: dict[str, Any]
) -> str:
    output: list[str] = []
    previous_category: str | None = None
    category_number = 0
    for service, row in mapped_services(catalogue, presentation):
        category = service["category"]
        if category != previous_category:
            category_number += 1
            output.append(
                f'          <div class="price-category" '
                f'id="price-category-{category_number}">{html_text(category)}</div>'
            )
            previous_category = category
        page_url = f"/services/{row['slug']}/"
        output.extend(
            [
                (
                    f'          <div class="price-line" '
                    f'data-service-id="{service["id"]}" '
                    f'data-service-url="{page_url}">'
                ),
                f'            <a class="price-row-link" href="{page_url}">',
                f'              <div class="price-name">{html_text(service["name"])}</div>',
                (
                    f'              <div class="price-time">'
                    f'{service["durationMinutes"]} мин</div>'
                ),
                f'              <div class="price-cost">{price_markup(service, row)}</div>',
                "            </a>",
                (
                    f'            <a class="price-book" '
                    f'href="{html_attr(service["bookingUrl"])}" '
                    f'data-goal="{service_goal(row, service)}">Записаться</a>'
                ),
                "          </div>",
            ]
        )
    return "\n".join(output)


def unique_categories(
    catalogue: dict[str, Any], presentation: dict[str, Any]
) -> list[str]:
    result: list[str] = []
    for service, _row in mapped_services(catalogue, presentation):
        if service["category"] not in result:
            result.append(service["category"])
    return result


def update_price_page(
    path: Path, catalogue: dict[str, Any], presentation: dict[str, Any]
) -> None:
    source = path.read_text(encoding="utf-8")
    rendered = render_price_rows(catalogue, presentation)
    source = replace_once(
        source,
        r"(?P<start>\s*<!-- services-catalog:start -->).*?"
        r"(?P<end>\s*<!-- services-catalog:end -->)",
        lambda match: (
            f"{match.group('start')}\n{rendered}\n"
            f"          <!-- services-catalog:end -->"
        ),
        label=f"services catalogue block in {path.relative_to(ROOT)}",
        flags=re.S,
    )
    chips = "\n".join(
        f"                <span>{html_text(category)}</span>"
        for category in unique_categories(catalogue, presentation)
    )
    source = replace_once(
        source,
        r'(<div class="price-chips">)\s*.*?\s*(</div>)',
        rf"\1\n{chips}\n              \2",
        label=f"price chips in {path.relative_to(ROOT)}",
        flags=re.S,
    )
    path.write_text(source, encoding="utf-8")


def render_options(rows: list[tuple[dict[str, Any], dict[str, Any]]]) -> str:
    output: list[str] = []
    for service, row in rows:
        old_price = row.get("oldPriceRub")
        if isinstance(old_price, int) and old_price > service["priceRub"]:
            price = (
                f'<span class="service-option-old">{format_rubles(old_price)}</span>'
                f'{format_rubles(service["priceRub"])}'
            )
        else:
            price = format_rubles(service["priceRub"])
        output.extend(
            [
                (
                    f'          <a class="service-option" '
                    f'data-service-id="{service["id"]}" '
                    f'href="{html_attr(service["bookingUrl"])}" '
                    f'data-goal="{service_goal(row, service)}">'
                ),
                f"            <span>{html_text(service['name'])}</span>",
                f'            <span class="text-bold">{price}</span>',
                "            <em>Записаться</em>",
                "          </a>",
            ]
        )
    return "\n".join(output)


def render_descriptions(
    rows: list[tuple[dict[str, Any], dict[str, Any]]]
) -> str:
    if len(rows) == 1:
        return description_html(rows[0][0]["description"])
    return "\n".join(
        (
            f'        <div class="service-catalog-description" '
            f'data-service-id="{service["id"]}">'
            f"<h3>{html_text(service['name'])}</h3>"
            f"{description_html(service['description'])}</div>"
        )
        for service, _row in rows
    )


def update_schema(
    source: str,
    slug: str,
    rows: list[tuple[dict[str, Any], dict[str, Any]]],
) -> str:
    match = re.search(
        r'(<script type="application/ld\+json" data-seo-schema>)(.*?)(</script>)',
        source,
        re.S,
    )
    if not match:
        raise RuntimeError(f"Missing service JSON-LD in /services/{slug}/")
    try:
        schema = json.loads(match.group(2))
    except json.JSONDecodeError as error:
        raise RuntimeError(f"Invalid service JSON-LD in /services/{slug}/: {error}") from error
    primary, primary_row = primary_service(rows)
    if len(rows) == 1:
        schema["name"] = primary["name"]
    schema["description"] = primary["description"]
    schema["image"] = SITE + public_image_path(primary, primary_row)
    schema["offers"] = [
        {
            "@type": "Offer",
            "name": service["name"],
            "price": service["priceRub"],
            "priceCurrency": "RUB",
            "availability": "https://schema.org/InStock",
            "url": service["bookingUrl"],
        }
        for service, _row in rows
    ]
    encoded = json.dumps(schema, ensure_ascii=False, separators=(",", ":")).replace(
        "</", "<\\/"
    )
    return source[: match.start(2)] + encoded + source[match.end(2) :]


def update_detail_page(
    slug: str,
    rows: list[tuple[dict[str, Any], dict[str, Any]]],
) -> None:
    path = ROOT / "services" / slug / "index.html"
    if not path.is_file():
        raise RuntimeError(f"Missing page /services/{slug}/")
    source = path.read_text(encoding="utf-8")
    primary, primary_row = primary_service(rows)
    image_path = public_image_path(primary, primary_row)

    source = replace_once(
        source,
        r'<div class="service-photo">\s*<img\b[^>]*>',
        (
            '<div class="service-photo">\n'
            f'        <img src="{html_attr(image_path)}" '
            f'alt="{html_attr(primary["name"])}" '
            'decoding="async" fetchpriority="high">'
        ),
        label=f"hero image in /services/{slug}/",
        flags=re.S,
    )
    source = replace_once(
        source,
        r'(<div class="service-kicker">).*?(</div>)',
        rf"\g<1>// {html_text(primary['category'])}\g<2>",
        label=f"category kicker in /services/{slug}/",
        flags=re.S,
    )
    if len(rows) == 1:
        source = replace_once(
            source,
            r'(<div class="service-booking-card">.*?<h1>).*?(</h1>)',
            rf"\g<1>{html_text(primary['name'])}\g<2>",
            label=f"service title in /services/{slug}/",
            flags=re.S,
        )
    source = replace_once(
        source,
        r'(<div class="service-booking-card">.*?</h1>\s*)'
        r'(?:<div class="service-catalog-summary">.*?</div>|(?:<p>.*?</p>\s*)+)'
        r'(\s*<div class="service-options">)',
        lambda match: (
            f'{match.group(1)}<div class="service-catalog-summary">'
            f'{description_html(primary["description"])}</div>\n        '
            f'{match.group(2).lstrip()}'
        ),
        label=f"hero description in /services/{slug}/",
        flags=re.S,
    )
    source = replace_once(
        source,
        r'(<div class="service-options">)\s*.*?\s*(</div>)',
        lambda match: (
            f'{match.group(1)}\n{render_options(rows)}\n        {match.group(2)}'
        ),
        label=f"booking options in /services/{slug}/",
        flags=re.S,
    )
    source = replace_once(
        source,
        r'(<section class="service-info">\s*<h2>Описание</h2>)\s*.*?\s*'
        r'(<div class="service-accordion">)',
        lambda match: (
            f"{match.group(1)}\n{render_descriptions(rows)}\n\n        {match.group(2)}"
        ),
        label=f"catalogue descriptions in /services/{slug}/",
        flags=re.S,
    )
    source = replace_once(
        source,
        r'(<meta name="description" content=")[^"]*(" />)',
        rf'\g<1>{html_attr(primary["description"])}\g<2>',
        label=f"meta description in /services/{slug}/",
    )
    source = update_schema(source, slug, rows)
    path.write_text(source, encoding="utf-8")


def update_service_cards(
    path: Path,
    grouped: dict[str, list[tuple[dict[str, Any], dict[str, Any]]]],
) -> None:
    source = path.read_text(encoding="utf-8")
    first_slug = next(iter(grouped))
    for slug, rows in grouped.items():
        primary, primary_row = primary_service(rows)
        image = public_image_path(primary, primary_row)
        list_pattern = (
            rf'(<a class="service-list-card" '
            rf'href="/services/{re.escape(slug)}/">\s*)'
            rf'<img\b[^>]*>'
        )
        source = re.sub(
            list_pattern,
            (
                rf'\g<1><img src="{html_attr(image)}" '
                rf'alt="{html_attr(primary["name"])}" '
                + (
                    'decoding="async" fetchpriority="high">'
                    if slug == first_slug
                    else 'loading="lazy" decoding="async">'
                )
            ),
            source,
            flags=re.S,
        )
        related_pattern = (
            rf'(<a class="other-service-card" '
            rf'href="/services/{re.escape(slug)}/">\s*)'
            rf'<img\b[^>]*>'
        )
        source = re.sub(
            related_pattern,
            (
                rf'\g<1><img src="{html_attr(image)}" '
                rf'alt="{html_attr(primary["name"])}" '
                rf'loading="lazy" decoding="async">'
            ),
            source,
            flags=re.S,
        )

    # On the service index these labels are the visible DIKIDI categories.
    for slug, rows in grouped.items():
        primary, _primary_row = primary_service(rows)
        source = re.sub(
            (
                rf'(<a class="service-list-card" href="/services/{re.escape(slug)}/">'
                rf'.*?<div><span>).*?(</span>)'
            ),
            rf"\g<1>{html_text(primary['category'])}\g<2>",
            source,
            count=1,
            flags=re.S,
        )
    path.write_text(source, encoding="utf-8")


def main() -> None:
    catalogue, presentation = load_catalog(require_local_images=True)
    grouped = services_by_slug(catalogue, presentation)

    for path in PRICE_PAGES:
        update_price_page(path, catalogue, presentation)
    for slug, rows in grouped.items():
        update_detail_page(slug, rows)

    card_pages = [ROOT / "services" / "index.html"] + [
        ROOT / "services" / slug / "index.html" for slug in grouped
    ]
    for path in card_pages:
        update_service_cards(path, grouped)

    print(
        f"Rendered {len(presentation['services'])} services into "
        f"{len(grouped)} service pages from catalogue {catalogue['contentHash']}"
    )


if __name__ == "__main__":
    main()
