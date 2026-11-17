# rebuild_tables.py — retire AUTOINCREMENT de vendor_products et sitemap_urls
import sqlite3

DB_PATH = "resources/db/catalog.db"
BACKUP_PATH = "resources/db/catalog.db.bak"


def main() -> None:
    # 1) sauvegarde cohérente (inclut le WAL)
    src = sqlite3.connect(DB_PATH)
    try:
        dst = sqlite3.connect(BACKUP_PATH)
        try:
            src.backup(dst)
        finally:
            dst.close()
    finally:
        src.close()

    # 2) reconstruction des deux tables
    conn = sqlite3.connect(DB_PATH)
    try:
        with conn:
            # --- vendor_products ---
            conn.execute("""
                CREATE TABLE vendor_products_new (
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
            conn.execute("""
                INSERT INTO vendor_products_new
                    (site_key, url, ean, brand, mpn, article_name,
                     catalog_price_nvat, catalog_price_vat, catalog_date, last_seen)
                SELECT site_key, url, ean, brand, mpn, article_name,
                       catalog_price_nvat, catalog_price_vat, catalog_date, last_seen
                FROM vendor_products
            """)
            conn.execute("DROP TABLE vendor_products")
            conn.execute("ALTER TABLE vendor_products_new RENAME TO vendor_products")
            conn.execute("CREATE INDEX idx_vp_site ON vendor_products(site_key)")
            conn.execute("CREATE INDEX idx_vp_ean ON vendor_products(ean)")
            conn.execute("CREATE INDEX idx_vp_mpn ON vendor_products(mpn)")

            # --- sitemap_urls ---
            conn.execute("""
                CREATE TABLE sitemap_urls_new (
                    id INTEGER PRIMARY KEY,
                    site_key TEXT NOT NULL,
                    url TEXT NOT NULL,
                    first_seen TEXT NOT NULL,
                    last_seen TEXT NOT NULL,
                    UNIQUE(site_key, url)
                )
            """)
            conn.execute("""
                INSERT INTO sitemap_urls_new (site_key, url, first_seen, last_seen)
                SELECT site_key, url, first_seen, last_seen
                FROM sitemap_urls
            """)
            conn.execute("DROP TABLE sitemap_urls")
            conn.execute("ALTER TABLE sitemap_urls_new RENAME TO sitemap_urls")
            conn.execute("CREATE INDEX idx_site_key ON sitemap_urls(site_key)")

        # 3) vérifs
        for table in ("vendor_products", "sitemap_urls"):
            count = conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
            max_id = conn.execute(f"SELECT MAX(id) FROM {table}").fetchone()[0]
            print(f"{table}: {count} lignes, id max = {max_id}")
    finally:
        conn.close()


if __name__ == "__main__":
    main()
