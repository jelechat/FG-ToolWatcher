# .tools/database/utils/db_manager.py
# by LECHAT Jérôme; creation date: 09/2026, latest edit: 11/2026
# with the help of OpenCode V2 (code model: Kimi K2.7 Code)

# INTERNAL(S)
import sqlite3
from dataclasses import dataclass
from datetime import datetime, timedelta


@dataclass
class ProductData:
    url: str
    ean: str | None = None
    brand: str | None = None
    mpn: str | None = None
    article_name: str | None = None
    catalog_price_nvat: float | None = None
    catalog_price_vat: float | None = None
    catalog_date: str = ""


class DatabaseManager:
    """ All SQLite database creation, management, and writing. """

    def __init__(self, db_path: str) -> None:
        self.db_path = db_path
        self._conn = sqlite3.connect(db_path, timeout=30)
        self._conn.row_factory = sqlite3.Row
        self._conn.execute("PRAGMA journal_mode=WAL")
        self._conn.execute("PRAGMA busy_timeout=30000")
        self._conn.execute("PRAGMA synchronous=NORMAL")
        self._conn.execute("PRAGMA foreign_keys=ON")

    def init_schema(self) -> None:
        with self._conn:
            self._conn.execute("""
                CREATE TABLE IF NOT EXISTS sitemap_urls (
                    id INTEGER PRIMARY KEY,
                    site_key TEXT NOT NULL,
                    url TEXT NOT NULL,
                    first_seen TEXT NOT NULL,
                    last_seen TEXT NOT NULL,
                    UNIQUE(site_key, url)
                )
            """)
            self._conn.execute("CREATE INDEX IF NOT EXISTS idx_site_key ON sitemap_urls(site_key)")
            self._conn.execute("""
                CREATE TABLE IF NOT EXISTS master_index (
                    ean TEXT PRIMARY KEY,
                    brand TEXT NOT NULL,
                    mpn TEXT NOT NULL,
                    article_name TEXT NOT NULL,
                    UNIQUE(brand, mpn)
                )
            """)
            self._conn.execute("""
                CREATE TABLE IF NOT EXISTS vendor_products (
                    id INTEGER PRIMARY KEY,
                    site_key TEXT NOT NULL,
                    url TEXT NOT NULL,
                    ean TEXT,
                    brand TEXT,
                    mpn TEXT,
                    article_name TEXT,
                    catalog_price_nvat REAL,
                    catalog_price_vat REAL,
                    catalog_date TEXT,
                    last_seen TEXT NOT NULL,
                    UNIQUE(site_key, url)
                )
            """)
            self._conn.execute("CREATE INDEX IF NOT EXISTS idx_vp_site ON vendor_products(site_key)")
            self._conn.execute("CREATE INDEX IF NOT EXISTS idx_vp_ean ON vendor_products(ean)")
            self._conn.execute("CREATE INDEX IF NOT EXISTS idx_vp_mpn ON vendor_products(mpn)")

    def upsert_products(self, site_key: str, rows: list[ProductData]) -> None:
        if not rows:
            return
        now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with self._conn:
            for data in rows:
                ean = data.ean if data.ean not in ("-", "", None) else None
                brand = data.brand if data.brand not in ("-", "", None) else None
                mpn = data.mpn if data.mpn not in ("-", "", None) else None
                article = data.article_name if data.article_name not in ("-", "", None) else None

                if all([ean, mpn, brand, article]):
                    self._conn.execute(
                        "INSERT OR IGNORE INTO master_index (ean, brand, mpn, article_name) VALUES (?, ?, ?, ?)",
                        (ean, brand, mpn, article),
                    )

                self._conn.execute(
                    """
                    INSERT INTO vendor_products (
                        site_key, url, ean, brand, mpn, article_name,
                        catalog_price_nvat, catalog_price_vat, catalog_date, last_seen
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ON CONFLICT(site_key, url) DO UPDATE SET
                        ean = COALESCE(excluded.ean, vendor_products.ean),
                        brand = COALESCE(excluded.brand, vendor_products.brand),
                        mpn = COALESCE(excluded.mpn, vendor_products.mpn),
                        article_name = COALESCE(excluded.article_name, vendor_products.article_name),
                        catalog_price_nvat = excluded.catalog_price_nvat,
                        catalog_price_vat = excluded.catalog_price_vat,
                        catalog_date = excluded.catalog_date,
                        last_seen = excluded.last_seen
                    """,
                    (site_key, data.url, ean, brand, mpn, article,
                     data.catalog_price_nvat, data.catalog_price_vat, data.catalog_date, now_str),
                )

    def sync_sitemap_urls(self, site_key: str, current_urls: set[str]) -> dict:
        now = datetime.now()
        now_str = now.strftime("%Y-%m-%d %H:%M:%S")
        limit_date = (now - timedelta(days=31)).strftime("%Y-%m-%d %H:%M:%S")
        report = {"new": 0, "unchanged": 0, "deactivated": 0}
        with self._conn:
            existing = {row["url"] for row in self._conn.execute(
                "SELECT url FROM sitemap_urls WHERE site_key = ?", (site_key,)
            ).fetchall()}
            for url in current_urls:
                if url not in existing:
                    self._conn.execute(
                        "INSERT INTO sitemap_urls (site_key, url, first_seen, last_seen) VALUES (?, ?, ?, ?)",
                        (site_key, url, now_str, now_str),
                    )
                    report["new"] += 1
                else:
                    report["unchanged"] += 1
                    self._conn.execute(
                        "UPDATE sitemap_urls SET last_seen = ? WHERE site_key = ? AND url = ?",
                        (now_str, site_key, url),
                    )
            cursor = self._conn.execute(
                "DELETE FROM sitemap_urls WHERE site_key = ? AND last_seen < ?",
                (site_key, limit_date),
            )
            report["deactivated"] = cursor.rowcount
        return report

    def get_pending_urls(self, site_key: str) -> list[str]:
        active = {r["url"] for r in self._conn.execute(
            "SELECT url FROM sitemap_urls WHERE site_key = ?", (site_key,)
        ).fetchall()}
        processed = {r["url"] for r in self._conn.execute(
            "SELECT url FROM vendor_products WHERE site_key = ?", (site_key,)
        ).fetchall()}
        return list(active - processed)

    def close(self) -> None:
        self._conn.close()
