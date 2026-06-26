#!/usr/bin/env python3
"""Generate YML feed for Yandex Business from the static site's service content.

The script intentionally uses only Python stdlib so it can run in GitHub Actions
without installing dependencies.
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import datetime
from html import unescape
from pathlib import Path
from typing import Iterable
from urllib.parse import parse_qs, urlencode, urlparse, urlunparse
from xml.etree.ElementTree import Element, ElementTree, SubElement, indent
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[1]
SITE = "https://denisyuce.com"
MOSCOW_TZ = ZoneInfo("Europe/Moscow")

CONTACT = {
    "region": "Москва, Крылатское, Молодёжная, Кунцево",
    "address": "Москва, Рублёвское шоссе 34к2, INDI",
    "phone": "+7 995 156-80-66",
    "telegram": "https://t.me/+79951568066",
}

IMAGE_BY_SLUG_TIME = {
    ("first-visit", "55"): "sale.webp",
    ("back-neck", "30"): "back-neck-30.webp",
    ("face", "30"): "face-30.webp",
    ("classic", "55"): "classic-55.webp",
    ("classic", "90"): "classic-90.webp",
    ("lymph", "55"): "lymph-55.webp",
    ("lymph", "90"): "lymph-90.webp",
    ("relax", "55"): "relax-55.webp",
    ("relax", "90"): "relax-90.webp",
    ("sport", "55"): "sport-55.webp",
    ("sport", "90"): "sport-90.webp",
}

DESCRIPTION_BY_SLUG_TIME = {
    ("first-visit", "55"): "Первый сеанс массажа со скидкой: знакомство с форматом работы, обсуждение запроса и мягкая работа с напряжением в теле.",
    ("back-neck", "30"): "Фокусная работа со спиной, плечевым поясом и шеей. Подходит при ощущении зажатости, усталости и напряжения после работы или нагрузок.",
    ("face", "30"): "Мягкий массаж лица: работа с жевательными мышцами, лбом, висками и шеей. Помогает расслабить лицо и снять напряжение.",
    ("classic", "55"): "Классический массаж для снижения мышечного напряжения, восстановления после нагрузки и ощущения лёгкости в теле.",
    ("classic", "90"): "Расширенный классический массаж 90 минут: больше времени на глубокую и спокойную работу со спиной, ногами, плечами и шеей.",
    ("lymph", "55"): "Мягкий ритмичный лимфодренажный массаж для ощущения лёгкости, снижения общей отёчности и спокойного восстановления.",
    ("lymph", "90"): "Лимфодренажный массаж 90 минут: спокойный формат с большим временем на проработку тела и восстановление.",
    ("relax", "55"): "Спокойный расслабляющий массаж для отдыха, снижения напряжения и восстановления после стресса или интенсивной недели.",
    ("relax", "90"): "Расслабляющий массаж 90 минут: больше времени на медленную, бережную и глубокую работу с напряжением в теле.",
    ("sport", "55"): "Спортивный массаж для людей, которые тренируются или много двигаются. Активный формат для восстановления после нагрузки.",
    ("sport", "90"): "Спортивный массаж 90 минут: расширенная работа с мышцами после тренировок, нагрузки или активного режима.",
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
    duration_min: str
    booking_url: str
    picture: str
    description: str
    category_id: str
    category_name: str


def clean_text(value: str) -> str:
    value = re.sub(r"<[^>]+>", " ", value)
    value = unescape(value)
    return re.sub(r"\s+", " ", value).strip()


def clean_price(value: str) -> int | None:
    digits = re.sub(r"\D+", "", clean_text(value))
    return int(digits) if digits else None


def normalize_booking_url(url: str) -> str:
    """Keep DIKIDI links stable so generated diffs do not reorder query params."""
    parsed = urlparse(unescape(url))
    query = parse_qs(parsed.query, keep_blank_values=True)
    order = ["p", "s", "rl"]
    pairs: list[tuple[str, str]] = []
    for key in order:
        for val in query.pop(key, []):
            pairs.append((key, val))
    for key in sorted(query):
        for val in query[key]:
            pairs.append((key, val))
    return urlunparse(parsed._replace(query=urlencode(pairs)))


def category_id_from_name(name: str, index: int) -> str:
    # Stable ids keep Yandex from creating duplicate categories after feed updates.
    known = {
        "Акции": "1",
        "Массаж по зонам": "2",
        "Классика": "3",
        "Лимфодренажный": "4",
        "Расслабляющий": "5",
        "Спортивный": "6",
    }
    return known.get(name, str(index + 1))


def extract_price_categories(html: str) -> list[tuple[int, Category]]:
    categories: list[tuple[int, Category]] = []
    for index, match in enumerate(re.finditer(r'<div class="price-category"[^>]*>(.*?)</div>', html, re.S)):
        name = clean_text(match.group(1))
        categories.append((match.start(), Category(id=category_id_from_name(name, index), name=name)))
    return categories


def category_for_position(categories: list[tuple[int, Category]], position: int) -> Category:
    current = Category(id="1", name="Массаж")
    for category_position, category in categories:
        if category_position > position:
            break
        current = category
    return current


def extract_rows(html: str) -> Iterable[dict[str, str]]:
    categories = extract_price_categories(html)
    starts = list(re.finditer(r'<div class="price-line" data-service-url="([^"]+)">', html))
    for index, match in enumerate(starts):
        service_url = match.group(1)
        category = category_for_position(categories, match.start())
        block_start = match.end()
        block_end = starts[index + 1].start() if index + 1 < len(starts) else html.find('</section>', block_start)
        block = html[block_start:block_end]
        name = re.search(r'<div class="price-name">(.*?)</div>', block, re.S)
        time = re.search(r'<div class="price-time">(.*?)</div>', block, re.S)
        cost = re.search(r'<div class="price-cost">(.*?)</div>', block, re.S)
        booking = re.search(r'<a class="price-book" href="([^"]+)"', block, re.S)
        if not all([name, time, cost, booking]):
            continue
        old = re.search(r'<span class="old-price">(.*?)</span>', cost.group(1), re.S)
        new = re.search(r'<span class="new-price">(.*?)</span>', cost.group(1), re.S)
        yield {
            "service_url": service_url,
            "name": clean_text(name.group(1)),
            "time": clean_text(time.group(1)),
            "price_raw": clean_text(new.group(1) if new else cost.group(1)),
            "oldprice_raw": clean_text(old.group(1)) if old else "",
            "booking_url": booking.group(1),
            "category_id": category.id,
            "category_name": category.name,
        }


def service_slug(service_url: str) -> str:
    return service_url.strip("/").split("/")[-1]


def service_page_description(slug: str) -> str:
    page = ROOT / "services" / slug / "index.html"
    if not page.exists():
        return ""
    html = page.read_text(encoding="utf-8")
    meta = re.search(r'<meta name="description" content="([^"]+)"', html)
    return clean_text(meta.group(1)) if meta else ""


def build_offers() -> list[Offer]:
    html = (ROOT / "index.html").read_text(encoding="utf-8")
    offers: list[Offer] = []
    for row in extract_rows(html):
        slug = service_slug(row["service_url"])
        duration = re.sub(r"\D+", "", row["time"])
        if not duration:
            continue
        price = clean_price(row["price_raw"])
        if price is None:
            continue
        oldprice = clean_price(row["oldprice_raw"])
        key = (slug, duration)
        picture_name = IMAGE_BY_SLUG_TIME.get(key)
        if not picture_name:
            raise SystemExit(f"No image mapping for service {slug!r}, duration {duration!r}")
        picture_path = ROOT / "assets" / "services" / picture_name
        if not picture_path.exists():
            raise SystemExit(f"Mapped image does not exist: {picture_path.relative_to(ROOT)}")
        description = DESCRIPTION_BY_SLUG_TIME.get(key) or service_page_description(slug)
        offer_id = f"{slug}-{duration}"
        offers.append(
            Offer(
                id=offer_id,
                name=f"{row['name']} — {duration} минут",
                page_url=SITE + row["service_url"],
                price=price,
                oldprice=oldprice,
                duration_min=duration,
                booking_url=normalize_booking_url(row["booking_url"]),
                picture=SITE + "/assets/services/" + picture_name,
                description=description,
                category_id=row["category_id"],
                category_name=row["category_name"],
            )
        )
    return offers


def add(parent: Element, tag: str, text: object | None = None, **attrs: object) -> Element:
    el = SubElement(parent, tag, {key: str(value) for key, value in attrs.items()})
    if text is not None:
        el.text = str(text)
    return el


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
    # In Yandex Business UI imported YML rows are currently shown newest/last first.
    # Feed them in reverse site order so the visible order matches the site price list:
    # Акции → Массаж по зонам → Классика → Лимфодренажный → Расслабляющий → Спортивный.
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

    offers_el = add(shop, "offers")
    for item in yandex_import_order(offers):
        offer = add(offers_el, "offer", id=item.id, available="true")
        add(offer, "name", item.name)
        add(offer, "url", item.page_url)
        add(offer, "price", item.price)
        if item.oldprice:
            add(offer, "oldprice", item.oldprice)
        add(offer, "currencyId", "RUR")
        add(offer, "categoryId", item.category_id)
        add(offer, "picture", item.picture)
        add(offer, "description", item.description)
        add(offer, "sales_notes", f"{item.duration_min} минут — {item.price:,} ₽".replace(",", " "))
        add(offer, "param", f"{item.duration_min} минут", name="Длительность")
        add(offer, "param", CONTACT["region"], name="Район")
        add(offer, "param", CONTACT["address"], name="Адрес")
        add(offer, "param", CONTACT["phone"], name="Телефон")
        add(offer, "param", CONTACT["telegram"], name="Telegram")
        add(offer, "param", item.booking_url, name="Онлайн-запись")

    indent(root, space="  ")
    ElementTree(root).write(ROOT / "services-feed.xml", encoding="UTF-8", xml_declaration=True)


def main() -> None:
    offers = build_offers()
    if not offers:
        raise SystemExit("No offers found in index.html")
    write_feed(offers)
    print(f"Generated services-feed.xml with {len(offers)} offers")


if __name__ == "__main__":
    main()
