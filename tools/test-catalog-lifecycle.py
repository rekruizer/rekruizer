import copy
import json
import unittest

from services_catalog import load_catalog, mapped_services, mapped_subscriptions, validate_catalog, services_by_slug
from catalog_publication import item_fingerprint, publication_manifest


class CatalogueLifecycleTests(unittest.TestCase):
    def setUp(self):
        self.catalogue, self.presentation = load_catalog(require_local_images=True)

    def test_hide_remove_and_restore_keep_presentation_and_other_services(self):
        service, row = mapped_services(self.catalogue, self.presentation)[0]
        original = copy.deepcopy(self.presentation)
        candidate = copy.deepcopy(self.catalogue)
        source = next(s for s in candidate["services"] if s["id"] == service["id"])
        source["published"] = False
        validate_catalog(candidate, self.presentation)
        self.assertNotIn(service["id"], [s["id"] for s, _ in mapped_services(candidate, self.presentation)])
        source["published"] = True
        self.assertIn(service["id"], [s["id"] for s, _ in mapped_services(candidate, self.presentation)])
        candidate["services"].remove(source)
        validate_catalog(candidate, self.presentation)
        self.assertEqual(self.presentation, original)

    def test_last_variant_removes_page_from_active_routes_and_offers(self):
        candidate = copy.deepcopy(self.catalogue)
        slug = mapped_services(candidate, self.presentation)[0][1]["slug"]
        ids = {r["id"] for r in self.presentation["services"] if r["slug"] == slug}
        for service in candidate["services"]:
            if service["id"] in ids:
                service["published"] = False
        validate_catalog(candidate, self.presentation)
        self.assertNotIn(slug, services_by_slug(candidate, self.presentation))
        self.assertTrue(services_by_slug(candidate, self.presentation))

    def test_hidden_reference_hides_only_its_membership(self):
        if not mapped_subscriptions(self.catalogue, self.presentation):
            self.skipTest("No configured membership in fixture")
        subscription, row = mapped_subscriptions(self.catalogue, self.presentation)[0]
        candidate = copy.deepcopy(self.catalogue)
        next(s for s in candidate["services"] if s["id"] == row["referenceServiceId"])["published"] = False
        self.assertNotIn(subscription["id"], [s["id"] for s, _ in mapped_subscriptions(candidate, self.presentation)])
        self.assertTrue(mapped_services(candidate, self.presentation))

    def test_manifest_describes_only_public_offers_without_editorial_source_or_private_data(self):
        manifest = publication_manifest(self.catalogue, self.presentation)
        self.assertEqual(manifest["catalogHash"], self.catalogue["contentHash"])
        self.assertRegex(manifest["presentationSha"], r"^[0-9a-f]{40}$")
        self.assertTrue(manifest["services"])
        for item in manifest["services"]:
            self.assertEqual(set(item), {"id", "fingerprint"})
            self.assertRegex(item["fingerprint"], r"^[0-9a-f]{64}$")
        service = {"id":"100","name":"Тест","category":"Массаж","priceRub":1000,"durationMinutes":60,"description":"Описание","bookingUrl":"https://example.test/","published":True}
        before = item_fingerprint(service, {}, {})
        self.assertEqual(before, "1fea8976e7290498b58c39071b2e3238e597c1ce1fc7891c70c56490d7a5e672")
        self.assertNotEqual(before, item_fingerprint(dict(service, priceRub=1100), {}, {}))
        self.assertNotEqual(before, item_fingerprint(service, {"imageFile":"other.webp"}, {}))
        self.assertNotEqual(before, item_fingerprint(service, {}, {"title":"Другая страница"}))


if __name__ == "__main__":
    unittest.main()
