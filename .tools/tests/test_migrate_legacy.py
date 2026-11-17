# .tools/tests/test_migrate_legacy.py
import sqlite3
import tempfile
import unittest
from pathlib import Path

from database.migrate_legacy import migrate


class TestMigrateLegacy(unittest.TestCase):

    def _create_old_loader(self, path: Path) -> None:
        with sqlite3.connect(path) as conn:
            conn.execute("""
                CREATE TABLE products (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    site_key TEXT NOT NULL,
                    url TEXT NOT NULL UNIQUE,
                    ean TEXT,
                    mpn TEXT,
                    brand TEXT,
                    article TEXT,
                    catalog_price_htva REAL,
                    catalog_price_ttc REAL,
                    catalog_date TEXT,
                    live_price_htva REAL,
                    live_price_ttc REAL,
                    live_date TEXT,
                    first_seen TEXT,
                    last_seen TEXT,
                    is_active INTEGER DEFAULT 1
                )
            """)
            conn.executemany(
                """
                INSERT INTO products (
                    site_key, url, ean, mpn, brand, article,
                    catalog_price_htva, catalog_price_ttc, catalog_date, is_active
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                [
                    (
                        "CLABOTS",
                        "https://clabots.be/p/1",
                        "1234567890123",
                        "ABC-1",
                        "Bosch",
                        "Perceuse 1",
                        100.0,
                        121.0,
                        "2026-01-01",
                        1,
                    ),
                    (
                        "CLABOTS",
                        "https://clabots.be/p/2",
                        None,
                        "ABC-2",
                        "Makita",
                        "Perceuse 2",
                        50.0,
                        60.5,
                        "2026-01-02",
                        1,
                    ),
                    (
                        "CLABOTS",
                        "https://clabots.be/p/3",
                        "9999999999999",
                        "ABC-3",
                        "Dewalt",
                        "Perceuse 3",
                        75.0,
                        90.75,
                        "2026-01-03",
                        0,
                    ),
                ],
            )

    def _create_old_sitemap(self, path: Path) -> None:
        with sqlite3.connect(path) as conn:
            conn.execute("""
                CREATE TABLE sitemap_urls (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    site_key TEXT NOT NULL,
                    url TEXT NOT NULL,
                    first_seen TEXT NOT NULL,
                    last_seen TEXT NOT NULL,
                    is_active INTEGER DEFAULT 1,
                    UNIQUE(site_key, url)
                )
            """)
            conn.executemany(
                "INSERT INTO sitemap_urls (site_key, url, first_seen, last_seen, is_active) VALUES (?, ?, ?, ?, ?)",
                [
                    ("CLABOTS", "https://clabots.be/p/1", "2026-01-01", "2026-01-01", 1),
                    ("CLABOTS", "https://clabots.be/p/2", "2026-01-02", "2026-01-02", 1),
                    ("CLABOTS", "https://clabots.be/p/3", "2026-01-03", "2026-01-03", 0),
                ],
            )

    def test_migration_maps_fields_and_filters_inactive(self) -> None:
        with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as tmpdir:
            loaders = Path(tmpdir) / "loaders"
            sitemaps = Path(tmpdir) / "sitemaps"
            new_db = Path(tmpdir) / "catalog.db"
            loaders.mkdir()
            sitemaps.mkdir()

            self._create_old_loader(loaders / "CLABOTS_database.db")
            self._create_old_sitemap(sitemaps / "CLABOTS_sitemaps.db")

            report = migrate(loaders, sitemaps, new_db, ["CLABOTS"])

            self.assertEqual(report["products"]["CLABOTS"], 2)
            self.assertEqual(report["sitemaps"]["CLABOTS"]["new"], 2)

            with sqlite3.connect(new_db) as conn:
                conn.row_factory = sqlite3.Row

                products = conn.execute(
                    "SELECT * FROM vendor_products WHERE site_key = ? ORDER BY url", ("CLABOTS",)
                ).fetchall()

                self.assertEqual(len(products), 2)
                self.assertEqual(products[0]["url"], "https://clabots.be/p/1")
                self.assertEqual(products[0]["ean"], "1234567890123")
                self.assertEqual(products[0]["mpn"], "ABC-1")
                self.assertEqual(products[0]["brand"], "Bosch")
                self.assertEqual(products[0]["article_name"], "Perceuse 1")
                self.assertAlmostEqual(products[0]["catalog_price_nvat"], 100.0)
                self.assertAlmostEqual(products[0]["catalog_price_vat"], 121.0)
                self.assertEqual(products[0]["catalog_date"], "2026-01-01")

                self.assertEqual(products[1]["url"], "https://clabots.be/p/2")
                self.assertIsNone(products[1]["ean"])
                self.assertEqual(products[1]["article_name"], "Perceuse 2")

                master = conn.execute("SELECT * FROM master_index").fetchall()
                self.assertEqual(len(master), 1)
                self.assertEqual(master[0]["ean"], "1234567890123")

                sitemap_rows = conn.execute(
                    "SELECT url FROM sitemap_urls WHERE site_key = ? ORDER BY url", ("CLABOTS",)
                ).fetchall()
                urls = {r["url"] for r in sitemap_rows}
                self.assertEqual(urls, {"https://clabots.be/p/1", "https://clabots.be/p/2"})

    def test_migration_does_not_touch_missing_sites(self) -> None:
        with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as tmpdir:
            loaders = Path(tmpdir) / "loaders"
            sitemaps = Path(tmpdir) / "sitemaps"
            new_db = Path(tmpdir) / "catalog.db"
            loaders.mkdir()
            sitemaps.mkdir()

            report = migrate(loaders, sitemaps, new_db, ["MISSING"])

            self.assertNotIn("MISSING", report["products"])
            self.assertNotIn("MISSING", report["sitemaps"])

            with sqlite3.connect(new_db) as conn:
                count = conn.execute("SELECT COUNT(*) FROM vendor_products").fetchone()[0]
                self.assertEqual(count, 0)

    def test_old_databases_are_not_modified(self) -> None:
        with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as tmpdir:
            loaders = Path(tmpdir) / "loaders"
            sitemaps = Path(tmpdir) / "sitemaps"
            new_db = Path(tmpdir) / "catalog.db"
            loaders.mkdir()
            sitemaps.mkdir()

            loader_path = loaders / "CLABOTS_database.db"
            sitemap_path = sitemaps / "CLABOTS_sitemaps.db"
            self._create_old_loader(loader_path)
            self._create_old_sitemap(sitemap_path)

            def count_rows(path: Path, table: str) -> int:
                with sqlite3.connect(path) as conn:
                    return conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]

            before_loader = count_rows(loader_path, "products")
            before_sitemap = count_rows(sitemap_path, "sitemap_urls")

            migrate(loaders, sitemaps, new_db, ["CLABOTS"])

            self.assertEqual(count_rows(loader_path, "products"), before_loader)
            self.assertEqual(count_rows(sitemap_path, "sitemap_urls"), before_sitemap)


if __name__ == "__main__":
    unittest.main()
