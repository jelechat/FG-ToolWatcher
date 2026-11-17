# Unit tests for database.utils.http_client.HttpClient and engines.

import gzip
import io
import unittest
from typing import Self, cast
from unittest.mock import MagicMock, patch

from database.scraper import ScraperEngine
from database.sitemaps import SitemapEngine
from database.utils.brands import BrandRegistry
from database.utils.db_manager import DatabaseManager, ProductData
from database.utils.http_client import HttpClient, HttpError, Response
from database.utils.web_manager import extract_heuristic, jsonld_extractor
from lxml import etree
from scrapling.parser import Selector


class _FakeSession:
    def __init__(self, page: MagicMock | None, **kwargs: object) -> None:
        self._page = page
        self.entered = 0
        self.exited = 0
        self.calls: list[tuple[str, dict[str, object]]] = []

    def get(self, url: str, **kwargs: object) -> object:
        self.calls.append((url, kwargs))
        return self._page

    def __enter__(self) -> Self:
        self.entered += 1
        return self

    def __exit__(self, *exc: object) -> None:
        self.exited += 1


class TestHttpClient(unittest.TestCase):

    def _make_page(self, **overrides: object) -> MagicMock:
        page = MagicMock()
        page.status = 200
        page.body = b"ok"
        page.headers = {}
        page.url = "https://example.com"
        page.encoding = "utf-8"
        for key, value in overrides.items():
            setattr(page, key, value)
        return page

    def _patch_session(self, page: MagicMock | None = None) -> tuple[_FakeSession, MagicMock]:
        mock_session_cls = MagicMock(return_value=_FakeSession(page))
        return mock_session_cls.return_value, mock_session_cls

    def test_get_returns_normalized_response(self) -> None:
        page = self._make_page(body=b"hello", headers={"Content-Type": "text/html"})

        fake_session, mock_session_cls = self._patch_session(page)

        with patch("database.utils.http_client.FetcherSession", mock_session_cls):
            client = HttpClient(timeout=10, headers={"X-Test": "1"})
            response = client.get("https://example.com/page")

        self.assertEqual(response.status, 200)
        self.assertEqual(response.body, b"hello")
        self.assertEqual(response.headers, {"Content-Type": "text/html"})
        self.assertEqual(response.url, "https://example.com")
        self.assertEqual(len(fake_session.calls), 1)
        self.assertEqual(fake_session.calls[0], ("https://example.com/page", {"timeout": 10, "headers": None}))

    def test_session_is_reused(self) -> None:
        page = self._make_page()

        fake_session, mock_session_cls = self._patch_session(page)

        with patch("database.utils.http_client.FetcherSession", mock_session_cls):
            client = HttpClient()
            client.get("https://example.com/a")
            client.get("https://example.com/b")

        self.assertEqual(mock_session_cls.call_count, 1)
        self.assertEqual(fake_session.entered, 1)
        self.assertEqual(len(fake_session.calls), 2)

    def test_close_is_idempotent(self) -> None:
        page = self._make_page()

        fake_session, mock_session_cls = self._patch_session(page)

        with patch("database.utils.http_client.FetcherSession", mock_session_cls):
            client = HttpClient()
            client.close()
            client.close()
            client.close()

            self.assertEqual(fake_session.exited, 0)

            client.get("https://example.com")
            client.close()
            client.close()

            self.assertEqual(fake_session.exited, 1)

    def test_context_manager_closes_session(self) -> None:
        page = self._make_page()

        fake_session, mock_session_cls = self._patch_session(page)

        with (
            patch("database.utils.http_client.FetcherSession", mock_session_cls),
            HttpClient() as client,
        ):
            client.get("https://example.com")

        self.assertEqual(fake_session.exited, 1)

    def test_response_raise_for_status(self) -> None:
        response_ok = Response(200, b"ok", {}, "https://example.com")
        response_ok.raise_for_status()  # no exception

        response_err = Response(404, b"not found", {}, "https://example.com/missing")
        with self.assertRaises(HttpError) as ctx:
            response_err.raise_for_status()

        self.assertEqual(ctx.exception.status, 404)
        self.assertEqual(ctx.exception.url, "https://example.com/missing")


class TestScraperEngineProcessProduct(unittest.TestCase):

    def _make_engine(self) -> ScraperEngine:
        engine = ScraperEngine.__new__(ScraperEngine)
        engine.website = "TEST"
        engine.JSONLD = False
        engine.JSONLD_KEYWORDS = {}
        engine.REGEX_KEYWORDS = {}
        engine.VAT = True
        engine.VAT_RATE = 1.21
        engine.REQUEST_DELAY = 0.0
        engine.UNKNOWN_BRANDS = set()
        engine.brands = BrandRegistry({"BOSCH": ["BOSCH"]})
        return engine

    def test_process_product_returns_none_on_exception(self) -> None:
        engine = self._make_engine()
        page = MagicMock()
        page.get_all_text.side_effect = RuntimeError("parser boom")

        result = ScraperEngine._process_product(engine, page, "https://example.com")

        self.assertIsNone(result)

    def test_process_product_none_price_when_no_price(self) -> None:
        html = "<html><body><h1>Perceuse</h1><p>1234567890123</p></body></html>"
        page = Selector(html)
        engine = self._make_engine()

        result = ScraperEngine._process_product(engine, page, "https://example.com")

        self.assertIsInstance(result, ProductData)
        assert result is not None
        self.assertIsNone(result.catalog_price_vat)
        self.assertIsNone(result.catalog_price_nvat)
        self.assertNotEqual(result.catalog_price_vat, 0.0)
        self.assertNotEqual(result.catalog_price_nvat, 0.0)

    def test_process_product_calculates_price_when_extracted(self) -> None:
        html = '<html><body><h1>Perceuse</h1><span itemprop="price">121,00</span></body></html>'
        page = Selector(html)
        engine = self._make_engine()
        engine.REGEX_KEYWORDS = {"price": []}

        result = ScraperEngine._process_product(engine, page, "https://example.com")

        self.assertIsInstance(result, ProductData)
        assert result is not None
        self.assertEqual(result.catalog_price_vat, 121.0)
        nvat = result.catalog_price_nvat
        assert nvat is not None
        self.assertAlmostEqual(nvat, 100.0, places=2)


class TestWebManagerExtraction(unittest.TestCase):

    def test_jsonld_extractor_product(self) -> None:
        html = """
        <html>
            <script type="application/ld+json">
            {
                "@type": "Product",
                "name": "Perceuse Bosch",
                "gtin13": "1234567890123",
                "mpn": "GSB18V-55",
                "brand": {"name": "Bosch"},
                "offers": {"price": "99.99"}
            }
            </script>
        </html>
        """
        page = Selector(html)
        data = jsonld_extractor(page)

        self.assertEqual(data.get("name"), "Perceuse Bosch")
        self.assertEqual(data.get("gtin13"), "1234567890123")
        self.assertEqual(data.get("mpn"), "GSB18V-55")
        self.assertEqual(data.get("brand", {}).get("name"), "Bosch")
        self.assertEqual(data.get("offers", {}).get("price"), "99.99")

    def test_extract_heuristic_meta_price(self) -> None:
        html = '<html><body><meta itemprop="price" content="45,50"></body></html>'
        page = Selector(html)
        price = extract_heuristic(page, "price", [])

        self.assertEqual(price, "45,50")

    def test_extract_heuristic_css_only_price(self) -> None:
        html = '<html><body><div class="product-price"> Prix : 89,95 EUR </div></body></html>'
        page = Selector(html)
        price = extract_heuristic(page, "price", ["prix"])

        self.assertEqual(price, "89,95")

    def test_extract_heuristic_text_label(self) -> None:
        html = """
        <html><body>
            <h1>Perceuse sans fil</h1>
            <p class="ean-label">EAN : 1234567890123</p>
            <p class="mpn-label">Référence : ABC-123-X</p>
        </body></html>
        """
        page = Selector(html)
        ean = extract_heuristic(page, "ean", ["EAN"])
        mpn = extract_heuristic(page, "mpn", ["Référence"])
        article = extract_heuristic(page, "article", [])

        self.assertEqual(ean, "1234567890123")
        self.assertEqual(mpn, "ABC-123-X")
        self.assertEqual(article, "Perceuse sans fil")


class TestSitemapEngine(unittest.TestCase):

    def _make_engine(self) -> SitemapEngine:
        engine = SitemapEngine.__new__(SitemapEngine)
        engine.website = "TEST"
        engine.DOMAIN = "example.com"
        engine.SITEMAP_INDEX = ["https://www.example.com/sitemap.xml"]
        engine.URL_PREFIXES = ()
        engine.REQUEST_DELAY = 0.0
        engine.REQUESTS_HEADERS = {
            "Referer": "https://www.example.com/",
            "Accept-Language": "fr-FR,fr;q=0.9",
        }
        engine.HTTP = MagicMock()
        return engine

    def _make_response(self, body: bytes, status: int = 200, headers: dict[str, str] | None = None, url: str = "https://example.com") -> Response:
        return Response(status=status, body=body, headers=headers or {}, url=url)

    def test_filter_fr_accepted(self) -> None:
        engine = self._make_engine()
        engine.URL_PREFIXES = ("https://www.example.com/fr/",)
        url = "https://www.example.com/fr/product/1"
        self.assertEqual(SitemapEngine._filter(engine, url), url)

    def test_filter_nl_root_rejected(self) -> None:
        engine = self._make_engine()
        engine.URL_PREFIXES = ("https://www.example.com/fr/",)
        self.assertIsNone(SitemapEngine._filter(engine, "https://www.example.com/nl"))

    def test_filter_segments_nl_de_en_rejected(self) -> None:
        engine = self._make_engine()
        engine.URL_PREFIXES = ("https://www.example.com/fr/",)
        for seg in ("nl", "de", "en"):
            url = f"https://www.example.com/{seg}/product/1"
            self.assertIsNone(SitemapEngine._filter(engine, url), seg)

    def test_filter_no_prefixes_unchanged(self) -> None:
        engine = self._make_engine()
        engine.URL_PREFIXES = ()
        url = "https://www.example.com/fr/product/1"
        self.assertEqual(SitemapEngine._filter(engine, url), url)
        self.assertIsNone(SitemapEngine._filter(engine, "https://www.example.com/nl/product/1"))

    def test_filter_prefix_without_trailing_slash(self) -> None:
        engine = self._make_engine()
        engine.URL_PREFIXES = ("https://www.example.com/fr",)
        url = "https://www.example.com/fr/product/1"
        self.assertEqual(SitemapEngine._filter(engine, url), url)

    def test_filter_uppercase_scheme_host_accepted(self) -> None:
        engine = self._make_engine()
        engine.URL_PREFIXES = ("https://www.example.com/fr/",)
        url = "HTTPS://WWW.EXAMPLE.COM/fr/product/1"
        self.assertEqual(SitemapEngine._filter(engine, url), url)

    def test_filter_url_prefixes_string_raises(self) -> None:
        import tempfile, os, json
        d = tempfile.mkdtemp()
        path = os.path.join(d, "websites.json")
        with open(path, "w", encoding="utf-8") as f:
            json.dump({"TEST": {"domain": "example.com", "sitemap_index": [], "url_prefixes": "https://www.example.com/fr/"}}, f)
        from database.utils.web_manager import WebsiteManager
        wm = WebsiteManager(file=path)
        with self.assertRaises(ValueError):
            SitemapEngine(wm, "TEST")

    def test_filter_empty_prefixes_no_filtering(self) -> None:
        engine = self._make_engine()
        engine.URL_PREFIXES = ()
        url = "https://evil.example.com/x" if False else "https://www.example.com/milwaukee-foo.html"
        # with no prefixes, host/segment rules still apply; just ensure no prefix rejection
        # empty list should not reject based on prefix
        engine2 = self._make_engine()
        engine2.URL_PREFIXES = ()
        self.assertIsNotNone(SitemapEngine._filter(engine2, "https://www.example.com/fr/product/1"))

    def test_filter_rejects_non_fr_prefix(self) -> None:
        engine = self._make_engine()
        engine.URL_PREFIXES = ("https://www.example.com/fr/",)
        self.assertIsNone(SitemapEngine._filter(engine, "https://www.example.com/milwaukee-foo.html"))

    def test_filter_rejects_uppercase_nl_segment(self) -> None:
        engine = self._make_engine()
        engine.URL_PREFIXES = ("https://www.example.com/fr/",)
        self.assertIsNone(SitemapEngine._filter(engine, "https://www.example.com/NL/product/1"))

    def test_resolve_index_with_namespace(self) -> None:
        xml = b"""<?xml version="1.0" encoding="UTF-8"?>
        <sitemapindex xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
            <sitemap>
                <loc>https://www.example.com/sitemap-products.xml</loc>
            </sitemap>
        </sitemapindex>"""
        product_xml = b"""<?xml version="1.0" encoding="UTF-8"?>
        <urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
            <url><loc>https://www.example.com/fr/product/1</loc></url>
            <url><loc>https://www.example.com/fr/product/2</loc></url>
        </urlset>"""
        engine = self._make_engine()

        def fake_fetch(url: str) -> bytes | None:
            if "index" in url:
                return xml
            return product_xml

        engine._fetch_raw = fake_fetch  # type: ignore[method-assign]
        urls = SitemapEngine._resolve(engine, "https://www.example.com/sitemap.xml", set())

        self.assertEqual(urls, [
            "https://www.example.com/fr/product/1",
            "https://www.example.com/fr/product/2",
        ])

    def test_fetch_raw_decompresses_gzip(self) -> None:
        xml = b"<urlset><url><loc>https://www.example.com/fr/product/1</loc></url></urlset>"
        buf = io.BytesIO()
        with gzip.GzipFile(fileobj=buf, mode="wb") as gz:
            gz.write(xml)
        compressed = buf.getvalue()

        engine = self._make_engine()

        with patch("database.sitemaps.HttpClient") as mock_client_cls:
            engine.HTTP = mock_client_cls.return_value
            cast(MagicMock, engine.HTTP).get.return_value = self._make_response(body=compressed)
            result = SitemapEngine._fetch_raw(engine, "https://www.example.com/sitemap.xml.gz")

        self.assertEqual(result, xml)

    def test_is_safe_url(self) -> None:
        engine = self._make_engine()
        engine.DOMAIN = "example.com"

        self.assertTrue(SitemapEngine._is_safe_url(engine, "https://example.com/sitemap.xml"))
        self.assertTrue(SitemapEngine._is_safe_url(engine, "http://www.example.com/sitemap.xml"))
        self.assertTrue(SitemapEngine._is_safe_url(engine, "https://sub.example.com/sitemap.xml"))
        self.assertFalse(SitemapEngine._is_safe_url(engine, "https://evil.com/sitemap.xml"))
        self.assertFalse(SitemapEngine._is_safe_url(engine, "file:///etc/passwd"))
        self.assertFalse(SitemapEngine._is_safe_url(engine, "http://user@example.com/"))
        self.assertFalse(SitemapEngine._is_safe_url(engine, "http://127.0.0.1/sitemap.xml"))
        self.assertFalse(SitemapEngine._is_safe_url(engine, "https://example.com:6379/x"))

    def test_gunzip_size_cap(self) -> None:
        from database.sitemaps import _gunzip

        data = b"x" * 200
        buf = io.BytesIO()
        with gzip.GzipFile(fileobj=buf, mode="wb") as gz:
            gz.write(data)
        compressed = buf.getvalue()

        with self.assertRaises(ValueError):
            _gunzip(compressed, max_bytes=100)

        result = _gunzip(compressed, max_bytes=500)
        self.assertEqual(result, data)

    def test_resolve_ignores_unsafe_urls(self) -> None:
        xml = b"""<?xml version="1.0" encoding="UTF-8"?>
        <sitemapindex xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
            <sitemap><loc>https://www.example.com/sitemap-products.xml</loc></sitemap>
            <sitemap><loc>http://127.0.0.1/sitemap.xml</loc></sitemap>
        </sitemapindex>"""
        product_xml = b"""<?xml version="1.0" encoding="UTF-8"?>
        <urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
            <url><loc>https://www.example.com/fr/product/1</loc></url>
            <url><loc>file:///etc/passwd</loc></url>
        </urlset>"""
        engine = self._make_engine()
        engine.DOMAIN = "example.com"

        fetched: list[str] = []

        def fake_fetch(url: str) -> bytes | None:
            fetched.append(url)
            if "index" in url:
                return xml
            return product_xml

        engine._fetch_raw = fake_fetch  # type: ignore[method-assign]
        urls = SitemapEngine._resolve(engine, "https://www.example.com/sitemap.xml", set())

        self.assertEqual(urls, ["https://www.example.com/fr/product/1"])
        self.assertNotIn("http://127.0.0.1/sitemap.xml", fetched)
        self.assertNotIn("file:///etc/passwd", fetched)

    def test_xml_parser_defends_against_xxe(self) -> None:
        from database.sitemaps import _XML_PARSER

        raw = b"""<?xml version="1.0" encoding="UTF-8"?>
        <!DOCTYPE urlset [<!ENTITY xxe SYSTEM "file:///nonexistent_xxe_file">]>
        <urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
            <url><loc>https://www.example.com/p/&xxe;</loc></url>
        </urlset>"""

        # Must parse without error and must not resolve the external entity.
        root = etree.fromstring(raw, _XML_PARSER)
        loc = root.find(".//{http://www.sitemaps.org/schemas/sitemap/0.9}loc")
        assert loc is not None
        self.assertEqual(loc.text, "https://www.example.com/p/")

    def test_resolve_ignores_comments_and_pis(self) -> None:
        xml = b"""<?xml version="1.0" encoding="UTF-8"?>
        <?xml-stylesheet type="text/xsl" href="style.xsl"?>
        <urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
            <!-- this is a comment -->
            <url><loc>https://www.example.com/fr/product/1</loc></url>
        </urlset>"""
        engine = self._make_engine()
        engine.DOMAIN = "example.com"

        def fake_fetch(url: str) -> bytes | None:
            return xml

        engine._fetch_raw = fake_fetch  # type: ignore[method-assign]
        urls = SitemapEngine._resolve(engine, "https://www.example.com/sitemap.xml", set())

        self.assertEqual(urls, ["https://www.example.com/fr/product/1"])

    def test_resolve_returns_empty_on_malformed_xml(self) -> None:
        engine = self._make_engine()
        engine.DOMAIN = "example.com"

        def fake_fetch(url: str) -> bytes | None:
            return b"<urlset><url><loc>https://www.example.com/p/1</loc></url>"

        engine._fetch_raw = fake_fetch  # type: ignore[method-assign]
        urls = SitemapEngine._resolve(engine, "https://www.example.com/sitemap.xml", set())

        self.assertEqual(urls, [])

    def test_fetch_raw_gzip_bomb_returns_none(self) -> None:
        import database.sitemaps as sitemaps_module

        engine = self._make_engine()

        with patch("database.sitemaps.HttpClient") as mock_client_cls:
            engine.HTTP = mock_client_cls.return_value
            cast(MagicMock, engine.HTTP).get.return_value = self._make_response(body=gzip.compress(b"x" * 1000))

            original_max = sitemaps_module.MAX_DECOMPRESSED_BYTES
            try:
                sitemaps_module.MAX_DECOMPRESSED_BYTES = 100
                result = SitemapEngine._fetch_raw(engine, "https://www.example.com/sitemap.xml.gz")
            finally:
                sitemaps_module.MAX_DECOMPRESSED_BYTES = original_max

        self.assertIsNone(result)

    def test_fetch_raw_oversized_body_returns_none(self) -> None:
        import database.sitemaps as sitemaps_module

        engine = self._make_engine()

        with patch("database.sitemaps.HttpClient") as mock_client_cls:
            engine.HTTP = mock_client_cls.return_value
            cast(MagicMock, engine.HTTP).get.return_value = self._make_response(body=b"x" * 200)

            original_max = sitemaps_module.MAX_SITEMAP_BYTES
            try:
                sitemaps_module.MAX_SITEMAP_BYTES = 100
                result = SitemapEngine._fetch_raw(engine, "https://www.example.com/sitemap.xml")
            finally:
                sitemaps_module.MAX_SITEMAP_BYTES = original_max

        self.assertIsNone(result)


class TestDatabaseManager(unittest.TestCase):

    def test_init_schema_upsert_and_get_pending_urls(self) -> None:
        db = DatabaseManager(":memory:")
        db.init_schema()

        db.sync_sitemap_urls("TEST", {"https://example.com/p/1", "https://example.com/p/2"})
        db.upsert_products(
            "TEST",
            [
                ProductData(
                    url="https://example.com/p/1",
                    ean="1234567890123",
                    brand="BOSCH",
                    mpn="GSB18V",
                    article_name="Perceuse",
                    catalog_price_vat=121.0,
                    catalog_price_nvat=100.0,
                    catalog_date="2026-11-03 12:00:00",
                )
            ],
        )

        pending = db.get_pending_urls("TEST")

        self.assertEqual(pending, ["https://example.com/p/2"])
        db.close()


if __name__ == "__main__":
    unittest.main()
