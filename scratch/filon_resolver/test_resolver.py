# scratch/filon_resolver/test_resolver.py
import unittest
import warnings
from pathlib import Path

from resolver import (
    apply_strategy,
    normalize_ean,
    normalize_mpn,
    parse_price,
    product_identity,
    resolve,
    resolve_field,
    resolve_record,
    resolve_scope,
)
from scrapling.parser import Selector


class TestFilonResolver(unittest.TestCase):

    page: Selector
    jsonld: dict

    @classmethod
    def setUpClass(cls) -> None:
        fixture = Path(__file__).with_name("lecot_fixture.html").read_text(encoding="utf-8")
        cls.page = Selector(fixture)
        cls.jsonld = {}

    def test_css_h1_name(self) -> None:
        value = apply_strategy(self.page, self.jsonld, "css:h1.product-detail-name::text")
        self.assertEqual(value, "Makita DGA506Z Meuleuse dangle sur accu (18V, 125 mm)")

    def test_text_ref_n(self) -> None:
        value = apply_strategy(self.page, self.jsonld, "text:Réf. n° -> next")
        self.assertEqual(value, "DGA506Z")

    def test_text_art_n(self) -> None:
        value = apply_strategy(self.page, self.jsonld, "text:Art. n° -> next")
        self.assertEqual(value, "455002033")

    def test_text_ean(self) -> None:
        value = apply_strategy(self.page, self.jsonld, "text:EAN -> next")
        self.assertEqual(value, "0088381814287")

    def test_text_tension(self) -> None:
        value = apply_strategy(self.page, self.jsonld, "text:Tension nominale -> next")
        self.assertEqual(value, "18 V")

    def test_text_capacite(self) -> None:
        value = apply_strategy(self.page, self.jsonld, "text:Capacité d'accu -> next")
        self.assertEqual(value, "5 Ah")

    def test_css_price(self) -> None:
        value = apply_strategy(self.page, self.jsonld, "css:.product-price-value::text")
        self.assertIsNotNone(value)
        assert value is not None
        self.assertIn("198", value)
        self.assertIn("06", value)

    def test_resolve_returns_first_match(self) -> None:
        value = resolve(self.page, self.jsonld, [
            "css:.missing::text",
            "text:Réf. n° -> next",
        ])
        self.assertEqual(value, "DGA506Z")


EXTRA_HTML = """<!doctype html>
<html>
<head>
  <meta property="product:price:amount" content="1.968,03">
</head>
<body>
  <div class="outside-label">Réf. n°</div><div class="outside-value">FAUX</div>
  <div itemprop="price" content="1968.03"></div>
  <main id="content-main">
    <h1 class="title">Perceuse Makita</h1>
    <span class="bad-ean">0088381752854</span>
    <span class="ean">EAN: 0088381752855</span>
    <span class="supplier">MAKITA WT001GZ</span>
    <div class="label">Réf. n°</div>
    <div class="value">DGA506Z</div>
    <div class="price">1.968,03 €</div>
  </main>
  <h1 class="outside">Hors scope</h1>
</body>
</html>
"""

EXTRA_JSONLD = {
    "name": "Perceuse Makita",
    "brand": {"name": "Makita"},
    "offers": [{"price": "1968.03"}],
    "@graph": [{"name": "Graph"}],
}


class TestFilonResolverDictSources(unittest.TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        cls.page = Selector(EXTRA_HTML)
        cls.jsonld = EXTRA_JSONLD
        cls.scope = resolve_scope(cls.page, "main#content-main")

    def test_dict_css_source(self) -> None:
        value = apply_strategy(
            self.page, self.jsonld, {"css": "h1.title::text"}, self.scope
        )
        self.assertEqual(value, "Perceuse Makita")

    def test_dict_css_does_not_escape_scope(self) -> None:
        value = apply_strategy(
            self.page, self.jsonld, {"css": "h1.outside::text"}, self.scope
        )
        self.assertIsNone(value)

    def test_dict_jsonld_list_fanout(self) -> None:
        value = apply_strategy(self.page, self.jsonld, {"jsonld": "offers.price"})
        self.assertEqual(value, "1968.03")

    def test_dict_jsonld_indexed(self) -> None:
        value = apply_strategy(self.page, self.jsonld, {"jsonld": "@graph.0.name"})
        self.assertEqual(value, "Graph")

    def test_dict_meta_reads_page_outside_scope(self) -> None:
        value = apply_strategy(
            self.page,
            self.jsonld,
            {"meta": "property=product:price:amount"},
            self.scope,
        )
        self.assertEqual(value, "1.968,03")

    def test_dict_attr_reads_page_outside_scope(self) -> None:
        value = apply_strategy(
            self.page,
            self.jsonld,
            {"attr": "itemprop=price::content"},
            self.scope,
        )
        self.assertEqual(value, "1968.03")

    def test_text_label_stays_in_scope(self) -> None:
        value = apply_strategy(
            self.page, self.jsonld, "text:Réf. n° -> next", self.scope
        )
        self.assertEqual(value, "DGA506Z")

    def test_scope_fallback_warns(self) -> None:
        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter("always")
            scope = resolve_scope(self.page, "#missing")
        self.assertIs(scope, self.page)
        self.assertTrue(
            any("introuvable" in str(item.message) for item in caught)
        )

    def test_ean_checksum_rejects_bad_candidate(self) -> None:
        self.assertEqual(normalize_ean("0088381752855"), "0088381752855")
        self.assertIsNone(normalize_ean("0088381752854"))
        self.assertIsNone(normalize_ean("455002033"))

        field = {
            "sources": [
                {"css": ".bad-ean::text"},
                {"css": ".ean::text"},
            ],
            "validate": {"type": "ean"},
        }
        value = resolve_field(self.page, self.jsonld, field, self.scope)
        self.assertEqual(value, "0088381752855")

    def test_mpn_strips_brand_prefix(self) -> None:
        self.assertEqual(normalize_mpn("MAKITA WT001GZ", "Makita"), "WT001GZ")
        self.assertIsNone(normalize_mpn("MAKITA WT001GZ"))

        field = {
            "sources": [{"css": ".supplier::text"}],
            "validate": {"type": "mpn"},
        }
        value = resolve_field(
            self.page, self.jsonld, field, self.scope, brand="Makita"
        )
        self.assertEqual(value, "WT001GZ")

    def test_price_parsing_and_validation(self) -> None:
        self.assertEqual(parse_price("1.968,03 €"), 1968.03)
        self.assertEqual(parse_price("1,968.03"), 1968.03)
        self.assertEqual(parse_price("325.980001"), 325.980001)
        self.assertIsNone(parse_price("Sur demande"))

        field = {
            "sources": [{"meta": "property=product:price:amount"}],
            "validate": {"type": "price"},
        }
        value = resolve_field(self.page, self.jsonld, field, self.scope)
        self.assertEqual(value, "1968.03")

    def test_resolve_record_and_identity(self) -> None:
        fields = {
            "title": {
                "sources": [{"css": "h1.title::text"}],
                "validate": {"type": "text"},
            },
            "brand": {
                "sources": [{"jsonld": "brand.name"}],
                "validate": {"type": "text"},
            },
            "ean": {
                "sources": [
                    {"css": ".bad-ean::text"},
                    {"css": ".ean::text"},
                ],
                "validate": {"type": "ean"},
            },
            "mpn": {
                "sources": [{"css": ".supplier::text"}],
                "validate": {"type": "mpn"},
            },
            "price": {
                "sources": [{"meta": "property=product:price:amount"}],
                "validate": {"type": "price"},
            },
        }
        record = resolve_record(
            self.page, self.jsonld, fields, "main#content-main"
        )
        self.assertEqual(record["title"], "Perceuse Makita")
        self.assertEqual(record["brand"], "Makita")
        self.assertEqual(record["ean"], "0088381752855")
        self.assertEqual(record["mpn"], "WT001GZ")
        self.assertEqual(record["price"], "1968.03")
        self.assertEqual(
            product_identity(record, "klium", "https://example.test/p"),
            "ean:0088381752855",
        )

        record_without_ean = {"brand": "Makita", "mpn": "WT001GZ"}
        self.assertEqual(
            product_identity(record_without_ean, "klium", "https://example.test/p"),
            "mpn:MAKITA:WT001GZ",
        )
        self.assertEqual(
            product_identity({}, "klium", "https://example.test/p"),
            "uid:klium:https://example.test/p",
        )


if __name__ == "__main__":
    unittest.main()
