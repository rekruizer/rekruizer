#!/usr/bin/env python3
"""Regression checks for the generated services site and YML feed."""

from __future__ import annotations

import copy
import re
import unittest
from html import escape
from xml.etree import ElementTree

from services_catalog import (
    CatalogValidationError,
    ROOT,
    load_catalog,
    mapped_catalogue_items,
    mapped_services,
    mapped_subscriptions,
    public_image_path,
    primary_service,
    services_by_slug,
    validate_catalog,
    validate_presentation,
)


class ServicesCatalogueTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.catalogue, cls.presentation = load_catalog(require_local_images=True)
        cls.mapped = mapped_services(cls.catalogue, cls.presentation)
        cls.subscriptions = mapped_subscriptions(cls.catalogue, cls.presentation)
        cls.all_mapped = mapped_catalogue_items(cls.catalogue, cls.presentation)
        cls.grouped = services_by_slug(cls.catalogue, cls.presentation)

    def test_expected_public_services_are_mapped_once(self) -> None:
        self.assertEqual(
            {service["id"] for service in self.catalogue["services"]},
            {
                row["id"]
                for row in self.presentation["services"]
                + self.presentation["subscriptions"]
            },
        )
        self.assertEqual(len(self.mapped), 11)
        self.assertEqual(len(self.subscriptions), 4)
        self.assertEqual(len(self.all_mapped), 15)
        self.assertEqual(
            {service["id"] for service, _row in self.mapped},
            {row["id"] for row in self.presentation["services"]},
        )
        self.assertTrue(all(service["published"] for service, _row in self.mapped))
        self.assertTrue(
            all(service["published"] for service, _row in self.subscriptions)
        )

    def test_unmapped_new_service_fails_closed(self) -> None:
        altered = copy.deepcopy(self.catalogue)
        new_service = copy.deepcopy(altered["services"][0])
        new_service.update(
            {
                "id": "99999999",
                "name": "Unexpected published service",
                "published": True,
            }
        )
        altered["services"].append(new_service)
        with self.assertRaisesRegex(
            CatalogValidationError,
            "unmapped published services",
        ):
            validate_catalog(altered, self.presentation)

    def test_presentation_can_override_a_public_display_name(self) -> None:
        first_row = self.presentation["services"][0]
        altered = copy.deepcopy(self.catalogue)
        raw_service = next(
            service
            for service in altered["services"]
            if service["id"] == first_row["id"]
        )
        raw_service["name"] = "Техническое название из DIKIDI"

        remapped = mapped_services(altered, self.presentation)
        first_service = next(
            service
            for service, row in remapped
            if row["id"] == first_row["id"]
        )

        self.assertEqual(first_service["name"], first_row["displayName"])

    def test_price_tables_contain_each_service_once(self) -> None:
        expected_ids = [service["id"] for service, _row in self.mapped]
        for relative in ("index.html", "services/index.html"):
            source = (ROOT / relative).read_text(encoding="utf-8")
            actual_ids = re.findall(
                r'<div class="price-line" data-service-id="(\d+)"',
                source,
            )
            self.assertEqual(actual_ids, expected_ids, relative)

    def test_detail_pages_use_catalogue_content(self) -> None:
        for slug, rows in self.grouped.items():
            source = (ROOT / "services" / slug / "index.html").read_text(
                encoding="utf-8"
            )
            primary, _primary_row = primary_service(rows)
            for service, _row in rows:
                self.assertIn(f'data-service-id="{service["id"]}"', source)
                self.assertIn(service["name"], source)
            description_section = re.search(
                r'<section class="service-info">\s*<h2>Описание</h2>'
                r'(.*?)<div class="service-accordion">',
                source,
                re.S,
            )
            self.assertIsNotNone(description_section)
            visible_paragraphs = re.findall(
                r"<p>(.*?)</p>", description_section.group(1), re.S
            )
            expected_paragraphs = [
                escape(paragraph, quote=False)
                for paragraph in primary["description"].split("\n\n")
                if paragraph.strip()
            ]
            self.assertEqual(visible_paragraphs, expected_paragraphs)
            if len(rows) > 1:
                self.assertEqual(primary["durationMinutes"], 55)
            self.assertNotIn("service-catalog-summary", source)
            self.assertNotIn("service-catalog-description", source)
            self.assertNotIn(
                "denisyuce-services-catalog.den100hero.workers.dev/service-images/",
                source,
            )

    def test_subscription_cards_use_catalogue_prices(self) -> None:
        source = (ROOT / "index.html").read_text(encoding="utf-8")
        block = re.search(
            r"<!-- subscriptions-catalog:start -->(.*?)"
            r"<!-- subscriptions-catalog:end -->",
            source,
            re.S,
        )
        self.assertIsNotNone(block)
        actual_ids = re.findall(r'data-service-id="(\d+)"', block.group(1))
        self.assertEqual(
            actual_ids,
            [service["id"] for service, _row in self.subscriptions],
        )
        by_id = {service["id"]: service for service in self.catalogue["services"]}
        for service, row in self.subscriptions:
            reference = by_id[row["referenceServiceId"]]
            saving = reference["priceRub"] * row["sessions"] - service["priceRub"]
            self.assertIn(service["name"], block.group(1))
            self.assertIn(service["bookingUrl"].replace("&", "&amp;"), block.group(1))
            self.assertIn(
                f'{service["priceRub"]:,}'.replace(",", " ") + " ₽",
                block.group(1),
            )
            self.assertIn(
                f'{saving:,}'.replace(",", " ") + " ₽",
                block.group(1),
            )

    def test_feed_matches_catalogue(self) -> None:
        root = ElementTree.parse(ROOT / "services-feed.xml").getroot()
        offers = {
            offer.get("id"): offer
            for offer in root.findall("./shop/offers/offer")
        }
        self.assertEqual(
            set(offers),
            {
                row["offerId"]
                for row in self.presentation["services"]
                + self.presentation["subscriptions"]
            },
        )
        for service, row in self.all_mapped:
            offer = offers[row["offerId"]]
            self.assertEqual(offer.findtext("name"), service["name"])
            self.assertEqual(offer.findtext("price"), str(service["priceRub"]))
            self.assertEqual(offer.findtext("description"), service["description"])
            self.assertEqual(
                offer.findtext("picture"),
                "https://denisyuce.com" + public_image_path(service, row),
            )
        for service, row in self.subscriptions:
            offer = offers[row["offerId"]]
            self.assertEqual(offer.findtext("url"), "https://denisyuce.com/#subscriptions")
            params = {
                item.get("name"): item.text for item in offer.findall("param")
            }
            self.assertEqual(params["Количество сеансов"], str(row["sessions"]))

    def test_meta_feed_matches_catalogue_and_uses_local_png_images(self) -> None:
        namespace = {"g": "http://base.google.com/ns/1.0"}
        root = ElementTree.parse(ROOT / "meta-services-feed.xml").getroot()
        items = {
            item.findtext("g:id", namespaces=namespace): item
            for item in root.findall("./channel/item")
        }
        self.assertEqual(
            set(items),
            {service["id"] for service, _row in self.all_mapped},
        )

        for service, row in self.all_mapped:
            item = items[service["id"]]
            self.assertEqual(
                item.findtext("g:title", namespaces=namespace),
                service["name"],
            )
            self.assertEqual(
                item.findtext("g:availability", namespaces=namespace),
                "in stock",
            )
            self.assertEqual(
                item.findtext("g:condition", namespaces=namespace),
                "new",
            )
            self.assertEqual(
                item.findtext("g:custom_label_0", namespaces=namespace),
                service["category"],
            )
            self.assertEqual(
                item.findtext("g:category", namespaces=namespace),
                service["category"],
            )
            image_name = re.sub(r"\.webp$", ".png", row["imageFile"])
            self.assertEqual(
                item.findtext("g:image_link", namespaces=namespace),
                f"https://denisyuce.com/assets/meta-services/{image_name}",
            )
            image_path = ROOT / "assets" / "meta-services" / image_name
            self.assertTrue(image_path.is_file())
            self.assertEqual(image_path.read_bytes()[:8], b"\x89PNG\r\n\x1a\n")
            self.assertLessEqual(image_path.stat().st_size, 8 * 1024 * 1024)

            old_price = row.get("oldPriceRub")
            expected_price = (
                old_price
                if isinstance(old_price, int) and old_price > service["priceRub"]
                else service["priceRub"]
            )
            self.assertEqual(
                item.findtext("g:price", namespaces=namespace),
                f"{expected_price:.2f} RUB",
            )
            expected_sale_price = (
                f"{service['priceRub']:.2f} RUB"
                if expected_price != service["priceRub"]
                else None
            )
            self.assertEqual(
                item.findtext("g:sale_price", namespaces=namespace),
                expected_sale_price,
            )

    def test_all_public_images_are_local_versioned_webp(self) -> None:
        for service, row in self.all_mapped:
            image = public_image_path(service, row)
            self.assertEqual(
                image,
                f"/assets/services/{row['imageFile']}",
            )
            self.assertNotIn("/catalog/", image)

    def test_unsafe_or_missing_local_image_fails_closed(self) -> None:
        unsafe = copy.deepcopy(self.presentation)
        unsafe["services"][0]["imageFile"] = "../outside.webp"
        with self.assertRaisesRegex(CatalogValidationError, "Invalid local WebP"):
            validate_presentation(unsafe)

        missing = copy.deepcopy(self.presentation)
        missing["services"][0]["imageFile"] = "missing-service-image.webp"
        with self.assertRaisesRegex(CatalogValidationError, "Missing local image"):
            validate_catalog(
                self.catalogue,
                validate_presentation(missing),
                require_local_images=True,
            )


if __name__ == "__main__":
    unittest.main()
