# .tools/database/migrate_legacy.py
# One-shot : importe les vieilles DB (old/Loaders, old/Sitemaps) vers catalog.db.
import sqlite3
from pathlib import Path

from database.utils.db_manager import DatabaseManager, ProductData

BASE_DIR = Path(__file__).resolve().parents[3]

DEFAULT_LOADERS = BASE_DIR / ".tools/database/old/Loaders/db"
DEFAULT_SITEMAPS = BASE_DIR / ".tools/database/old/Sitemaps/db"
DEFAULT_NEW_DB = BASE_DIR / "resources/db/catalog.db"
SITES = ["CLABOTS", "FIXAMI", "KLIUM", "LECOT", "TOOLNATION"]


def migrate(old_loaders: Path, old_sitemaps: Path, new_db: Path, sites: list[str]) -> dict:
    db = DatabaseManager(str(new_db))
    db.init_schema()

    report: dict = {"sitemaps": {}, "products": {}}

    for site in sites:
        sitemap_db = old_sitemaps / f"{site}_sitemaps.db"
        if sitemap_db.exists():
            with sqlite3.connect(sitemap_db) as conn:
                rows = conn.execute(
                    "SELECT url FROM sitemap_urls WHERE site_key = ? AND is_active = 1", (site,)
                ).fetchall()
            urls = {r[0] for r in rows}
            report["sitemaps"][site] = db.sync_sitemap_urls(site, urls)

    for site in sites:
        products_db = old_loaders / f"{site}_database.db"
        if products_db.exists():
            with sqlite3.connect(products_db) as conn:
                conn.row_factory = sqlite3.Row
                rows = conn.execute(
                    """SELECT url, ean, mpn, brand, article,
                              catalog_price_htva, catalog_price_ttc, catalog_date
                       FROM products WHERE is_active = 1"""
                ).fetchall()
            products = [
                ProductData(
                    url=r["url"],
                    ean=r["ean"],
                    mpn=r["mpn"],
                    brand=r["brand"],
                    article_name=r["article"],
                    catalog_price_nvat=r["catalog_price_htva"],
                    catalog_price_vat=r["catalog_price_ttc"],
                    catalog_date=r["catalog_date"] or "",
                )
                for r in rows
            ]
            db.upsert_products(site, products)
            report["products"][site] = len(products)

    db.close()
    return report


def main() -> None:
    result = migrate(DEFAULT_LOADERS, DEFAULT_SITEMAPS, DEFAULT_NEW_DB, SITES)
    print(result)


if __name__ == "__main__":
    main()
