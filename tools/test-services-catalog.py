#!/usr/bin/env python3
"""Regression checks for the generated services site and YML feed."""

from __future__ import annotations

import copy
import hashlib
import re
import unittest
from xml.etree import ElementTree

from services_catalog import (
    CatalogValidationError,
    ROOT,
    load_catalog,
    mapped_services,
    public_image_path,
    services_by_slug,
    validate_catalog,
    validate_presentation,
)


class ServicesCatalogueTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.catalogue, cls.presentation = load_catalog(require_local_images=True)
        cls.mapped = mapped_services(cls.catalogue, cls.presentation)
        cls.grouped = services_by_slug(cls.catalogue, cls.presentation)

    def test_expected_public_services_are_mapped_once(self) -> None:
        self.assertEqual(
            {service["id"] for service in self.catalogue["services"]},
            {row["id"] for row in self.presentation["services"]},
        )
        self.assertEqual(len(self.mapped), 11)
        self.assertEqual(
            {service["id"] for service, _row in self.mapped},
            {row["id"] for row in self.presentation["services"]},
        )
        self.assertTrue(all(service["published"] for service, _row in self.mapped))

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
            for service, _row in rows:
                self.assertIn(f'data-service-id="{service["id"]}"', source)
                self.assertIn(service["name"], source)
                self.assertIn(service["description"].split("\n", 1)[0], source)
            self.assertNotIn(
                "denisyuce-services-catalog.den100hero.workers.dev/service-images/",
                source,
            )

    def test_feed_matches_catalogue(self) -> None:
        root = ElementTree.parse(ROOT / "services-feed.xml").getroot()
        offers = {
            offer.get("id"): offer
            for offer in root.findall("./shop/offers/offer")
        }
        self.assertEqual(set(offers), {row["offerId"] for row in self.presentation["services"]})
        for service, row in self.mapped:
            offer = offers[row["offerId"]]
            self.assertEqual(offer.findtext("name"), service["name"])
            self.assertEqual(offer.findtext("price"), str(service["priceRub"]))
            self.assertEqual(offer.findtext("description"), service["description"])
            self.assertEqual(
                offer.findtext("picture"),
                "https://denisyuce.com" + public_image_path(service, row),
            )

    def test_all_public_images_are_local_versioned_webp(self) -> None:
        for service, row in self.mapped:
            image = public_image_path(service, row)
            path = ROOT / "assets" / "services" / row["imageFile"]
            expected_hash = hashlib.sha256(path.read_bytes()).hexdigest()[:12]
            self.assertEqual(
                image,
                f"/assets/services/{row['imageFile']}?v={expected_hash}",
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
