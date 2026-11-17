# clean_articles.py — décode les entités HTML dans article_name
import html
import sqlite3

DB_PATH = "resources/db/catalog.db"   # à lancer depuis la racine du repo
TABLES = ["vendor_products", "master_index"]


def main() -> None:
    conn = sqlite3.connect(DB_PATH)
    total = 0
    try:
        for table in TABLES:
            rows = conn.execute(f"SELECT rowid, article_name FROM {table}").fetchall()
            for rowid, article in rows:
                if article and "&" in article:          # entité potentielle
                    cleaned = html.unescape(article)
                    if cleaned != article:
                        conn.execute(
                            f"UPDATE {table} SET article_name = ? WHERE rowid = ?",
                            (cleaned, rowid),
                        )
                        total += 1
        conn.commit()
        print(f"{total} article(s) nettoyé(s)")
    finally:
        conn.close()


if __name__ == "__main__":
    main()
