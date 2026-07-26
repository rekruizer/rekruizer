#!/usr/bin/env python3
"""Generate the Yandex Business YML feed from the canonical services snapshot."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from xml.etree.ElementTree import Element, ElementTree, SubElement, indent
from zoneinfo import ZoneInfo

from services_catalog import ROOT, load_catalog, mapped_services, public_image_path


SITE = "https://denisyuce.com"
MOSCOW_TZ = ZoneInfo("Europe/Moscow")

CONTACT = {
    "region": "Москва, Крылатское, Молодёжная, Кунцево",
    "address": "Москва, Рублёвское шоссе 34к2, INDI",
    "phone": "+7 995 156-80-66",
    "telegram": "https://t.me/+79951568066",
}


@dataclass(frozen=True)
class Category:
    id: str
    name: str


@dataclass(frozen=True)
class Offer:
    id: str
    name: str
    page_url: str
    price: int
    oldprice: int | None
    duration_min: int
    booking_url: str
    picture: str
    description: str
    category_id: str
    category_name: str


def build_offers() -> list[Offer]:
    catalogue, presentation = load_catalog(require_local_images=True)
    category_ids = presentation["categoryIds"]
    offers: list[Offer] = []
    for service, row in mapped_services(catalogue, presentation):
        old_price = row.get("oldPriceRub")
        offers.append(
            Offer(
                id=row["offerId"],
                name=service["name"],
                page_url=f"{SITE}/services/{row['slug']}/",
                price=service["priceRub"],
                oldprice=(
                    old_price
                    if isinstance(old_price, int) and old_price > service["priceRub"]
                    else None
                ),
                duration_min=service["durationMinutes"],
                booking_url=service["bookingUrl"],
                picture=SITE + public_image_path(service),
                description=service["description"],
                category_id=str(category_ids[service["category"]]),
                category_name=service["category"],
            )
        )
    return offers


def add(
    parent: Element,
    tag: str,
    text: object | None = None,
    **attrs: object,
) -> Element:
    element = SubElement(
        parent,
        tag,
        {key: str(value) for key, value in attrs.items()},
    )
    if text is not None:
        element.text = str(text)
    return element


def categories_from_offers(offers: list[Offer]) -> list[Category]:
    seen: set[str] = set()
    categories: list[Category] = []
    for offer in offers:
        if offer.category_id in seen:
            continue
        seen.add(offer.category_id)
        categories.append(Category(id=offer.category_id, name=offer.category_name))
    return categories


def yandex_import_order(offers: list[Offer]) -> list[Offer]:
    # Yandex Business currently displays the latest imported row first.
    return list(reversed(offers))


def write_feed(offers: list[Offer]) -> None:
    generated_at = datetime.now(MOSCOW_TZ).strftime("%Y-%m-%d %H:%M")
    root = Element("yml_catalog", {"date": generated_at})
    shop = add(root, "shop")
    add(shop, "name", "Массаж — Денис Пучков")
    add(shop, "company", "Денис Пучков")
    add(shop, "url", SITE + "/")

    currencies = add(shop, "currencies")
    add(currencies, "currency", id="RUR", rate="1")

    categories = add(shop, "categories")
    for category in categories_from_offers(offers):
        add(categories, "category", category.name, id=category.id)

    offers_element = add(shop, "offers")
    for item in yandex_import_order(offers):
        offer = add(offers_element, "offer", id=item.id, available="true")
        add(offer, "name", item.name)
        add(offer, "url", item.page_url)
        add(offer, "price", item.price)
        if item.oldprice:
            add(offer, "oldprice", item.oldprice)
        add(offer, "currencyId", "RUR")
        add(offer, "categoryId", item.category_id)
        add(offer, "picture", item.picture)
        add(offer, "description", item.description)
        add(
            offer,
            "sales_notes",
            f"{item.duration_min} минут — {item.price:,} ₽".replace(",", " "),
        )
        add(offer, "param", f"{item.duration_min} минут", name="Длительность")
        add(offer, "param", CONTACT["region"], name="Район")
        add(offer, "param", CONTACT["address"], name="Адрес")
        add(offer, "param", CONTACT["phone"], name="Телефон")
        add(offer, "param", CONTACT["telegram"], name="Telegram")
        add(offer, "param", item.booking_url, name="Онлайн-запись")

    indent(root, space="  ")
    ElementTree(root).write(
        ROOT / "services-feed.xml",
        encoding="UTF-8",
        xml_declaration=True,
    )


def main() -> None:
    offers = build_offers()
    if not offers:
        raise SystemExit("No published offers in services catalogue")
    write_feed(offers)
    print(f"Generated services-feed.xml with {len(offers)} offers")


if __name__ == "__main__":
    main()
