#!/usr/bin/env python3
"""Regression checks for the generated services site and YML feed."""

from __future__ import annotations

import copy
import importlib.util
import json
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
    public_site_image_path,
    primary_service,
    services_by_slug,
    validate_catalog,
    validate_presentation,
)


GENERATOR_SPEC = importlib.util.spec_from_file_location(
    "generate_services_site", ROOT / "tools" / "generate-services-site.py"
)
assert GENERATOR_SPEC and GENERATOR_SPEC.loader
GENERATOR = importlib.util.module_from_spec(GENERATOR_SPEC)
GENERATOR_SPEC.loader.exec_module(GENERATOR)


class ServicesCatalogueTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.catalogue, cls.presentation = load_catalog(require_local_images=True)
        cls.mapped = mapped_services(cls.catalogue, cls.presentation)
        cls.subscriptions = mapped_subscriptions(cls.catalogue, cls.presentation)
        cls.all_mapped = mapped_catalogue_items(cls.catalogue, cls.presentation)
        cls.grouped = services_by_slug(cls.catalogue, cls.presentation)

    def test_expected_public_services_are_mapped_once(self) -> None:
        catalogue_ids = {service["id"] for service in self.catalogue["services"]}
        configured_ids = {
            row["id"]
            for row in self.presentation["services"]
            + self.presentation["subscriptions"]
        }
        self.assertEqual(
            {service["id"] for service, _row in self.all_mapped},
            configured_ids & catalogue_ids,
        )
        self.assertEqual(
            {service["id"] for service, _row in self.mapped},
            {row["id"] for row in self.presentation["services"]} & catalogue_ids,
        )
        self.assertTrue(all(service["published"] for service, _row in self.mapped))
        self.assertTrue(
            all(service["published"] for service, _row in self.subscriptions)
        )

    def test_unmapped_new_service_does_not_block_catalogue(self) -> None:
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

    def test_regular_services_follow_dikidi_catalogue_order(self) -> None:
        expected_ids = [
            service["id"]
            for service in self.catalogue["services"]
            if any(
                row["id"] == service["id"]
                for row in self.presentation["services"]
            )
        ]
        altered_presentation = copy.deepcopy(self.presentation)
        altered_presentation["services"].reverse()
        actual_ids = [
            service["id"]
            for service, _row in mapped_services(
                self.catalogue, altered_presentation
            )
        ]
        self.assertEqual(actual_ids, expected_ids)

    def test_price_tables_contain_each_service_once(self) -> None:
        expected_ids = [service["id"] for service, _row in self.mapped]
        for relative in ("index.html", "services/index.html"):
            source = (ROOT / relative).read_text(encoding="utf-8")
            actual_ids = re.findall(
                r'<div class="price-line" data-service-id="(\d+)"',
                source,
            )
            self.assertEqual(actual_ids, expected_ids, relative)

    def test_service_cards_follow_the_first_dikidi_variant(self) -> None:
        source = (ROOT / "services" / "index.html").read_text(encoding="utf-8")
        actual_slugs = re.findall(
            r'<a class="service-list-card" href="/services/([a-z0-9-]+)/">',
            source,
        )
        self.assertEqual(actual_slugs, list(self.grouped))

        rank = {slug: index for index, slug in enumerate(self.grouped)}
        for slug in self.grouped:
            detail = (ROOT / "services" / slug / "index.html").read_text(
                encoding="utf-8"
            )
            related = re.findall(
                r'<a class="other-service-card" href="/services/([a-z0-9-]+)/">',
                detail,
            )
            self.assertEqual(related, sorted(related, key=rank.__getitem__), slug)

    def test_inactive_service_cards_are_removed(self) -> None:
        source = """
        <a class="service-list-card" href="/services/active/"><div>Active</div></a>
        <a class="service-list-card" href="/services/removed/"><div>Removed</div></a>
        <a class="other-service-card" href="/services/removed/"><div>Removed</div></a>
        """
        cleaned = GENERATOR.remove_inactive_service_cards(source, {"active"})
        self.assertIn('/services/active/', cleaned)
        self.assertNotIn('/services/removed/', cleaned)

    def test_detail_pages_use_catalogue_content(self) -> None:
        for slug, rows in self.grouped.items():
            source = (ROOT / "services" / slug / "index.html").read_text(
                encoding="utf-8"
            )
            primary, primary_row = primary_service(rows)
            expected_image = public_site_image_path(primary, primary_row)
            for service, _row in rows:
                self.assertIn(f'data-service-id="{service["id"]}"', source)
                self.assertIn(service["name"], source)
            option_ids = re.findall(
                r'<a class="service-option" data-service-id="(\d+)"',
                source,
            )
            self.assertEqual(
                option_ids,
                [service["id"] for service, _row in rows],
                slug,
            )
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
            hero = re.search(
                r'<div class="service-photo">\s*<img\b[^>]*\bsrc="([^"]+)"',
                source,
            )
            self.assertIsNotNone(hero)
            self.assertEqual(hero.group(1), expected_image)

            schema_match = re.search(
                r'<script type="application/ld\+json" data-seo-schema>'
                r'(.*?)</script>',
                source,
                re.S,
            )
            self.assertIsNotNone(schema_match)
            schema = json.loads(schema_match.group(1))
            self.assertEqual(schema["image"], "https://denisyuce.com" + expected_image)

    def test_service_index_cards_use_site_images(self) -> None:
        source = (ROOT / "services" / "index.html").read_text(encoding="utf-8")
        for slug, rows in self.grouped.items():
            primary, primary_row = primary_service(rows)
            expected_image = public_site_image_path(primary, primary_row)
            card = re.search(
                rf'<a class="service-list-card" href="/services/{re.escape(slug)}/">'
                rf'\s*<img\b[^>]*\bsrc="([^"]+)"',
                source,
            )
            self.assertIsNotNone(card, slug)
            self.assertEqual(card.group(1), expected_image, slug)

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

        for service, row in self.mapped:
            site_image = public_site_image_path(service, row)
            self.assertEqual(
                site_image,
                f"/assets/services/{row['siteImageFile']}",
            )
            self.assertNotRegex(site_image, r"-(?:30|55|90)\.webp$")

    def test_every_service_webp_has_a_png_source(self) -> None:
        source_root = ROOT / "services" / "source-images"
        source_stems = {
            path.stem for path in source_root.glob("*/*.png") if path.is_file()
        }
        public_stems = {
            path.stem for path in (ROOT / "assets" / "services").glob("*.webp")
        }
        self.assertEqual(source_stems, public_stems)

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

        unsafe_site = copy.deepcopy(self.presentation)
        unsafe_site["services"][0]["siteImageFile"] = "../outside.webp"
        with self.assertRaisesRegex(CatalogValidationError, "siteImageFile"):
            validate_presentation(unsafe_site)


if __name__ == "__main__":
    unittest.main()
