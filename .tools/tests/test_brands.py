# .tools/tests/test_brands.py
import unittest

from database.utils.brands import BrandRegistry, normalize


class TestBrandNormalize(unittest.TestCase):

    def test_remove_accents_and_symbols(self) -> None:
        self.assertEqual(normalize("BLÅKLÄDER"), "BLAKLADER")
        self.assertEqual(normalize("BLACK+DECKER"), "BLACK DECKER")
        self.assertEqual(normalize("  Makita  "), "MAKITA")


class TestBrandRegistry(unittest.TestCase):

    def _make_registry(self) -> BrandRegistry:
        return BrandRegistry({
            "MAKITA": ["MAKITA"],
            "BLACK & DECKER": ["BLACK+DECKER", "BLACK & DECKER"],
            "MAX": ["MAX"],
        })

    def test_resolve_finds_brand_in_text(self) -> None:
        registry = self._make_registry()
        self.assertEqual(registry.resolve("Perceuse Makita DHP484"), "MAKITA")

    def test_resolve_matches_alias(self) -> None:
        registry = self._make_registry()
        self.assertEqual(registry.resolve("Perceuse BLACK+DECKER BDCDD12"), "BLACK & DECKER")

    def test_resolve_no_false_positive_on_substring(self) -> None:
        registry = self._make_registry()
        self.assertIsNone(registry.resolve("MAX500"))

    def test_is_known(self) -> None:
        registry = self._make_registry()
        self.assertTrue(registry.is_known("MAKITA"))
        self.assertTrue(registry.is_known("makita"))
        self.assertFalse(registry.is_known("INCONNUE"))

    def test_clean_mpn_removes_canonical_brand(self) -> None:
        registry = self._make_registry()
        self.assertEqual(registry.clean_mpn("MAKITA DHP484Z", canonical="MAKITA"), "DHP484Z")

    def test_clean_mpn_does_not_corrupt_substring(self) -> None:
        registry = self._make_registry()
        self.assertEqual(registry.clean_mpn("MAX500", canonical="MAX"), "MAX500")

    def test_clean_mpn_keeps_hyphens(self) -> None:
        registry = self._make_registry()
        self.assertEqual(registry.clean_mpn("195095-7"), "195095-7")

    def test_clean_mpn_empty_returns_none(self) -> None:
        registry = self._make_registry()
        self.assertIsNone(registry.clean_mpn(""))
        self.assertIsNone(registry.clean_mpn("   "))


if __name__ == "__main__":
    unittest.main()
