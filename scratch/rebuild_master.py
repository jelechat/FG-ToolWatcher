import sqlite3, os, csv
base = r"C:\Users\ljero\Documents Personnels\.projects\FG-ToolWatcher\resources\db"
db = os.path.join(base, "catalog.db")
csv_path = os.path.join(base, "master_index_conflicts.csv")

conn = sqlite3.connect(db, timeout=30)
conn.row_factory = sqlite3.Row
conn.execute("PRAGMA busy_timeout=30000")
conn.execute("PRAGMA foreign_keys=ON")

# sizes before
def sizes():
    return {
        "db": os.path.getsize(db),
        "wal": os.path.getsize(os.path.join(base, "catalog.db-wal")) if os.path.exists(os.path.join(base, "catalog.db-wal")) else 0,
        "shm": os.path.getsize(os.path.join(base, "catalog.db-shm")) if os.path.exists(os.path.join(base, "catalog.db-shm")) else 0,
    }
before = sizes()
print("before", before)

try:
    conn.execute("BEGIN IMMEDIATE")
    # export conflicts: rows discarded by rn_bmp > 1
    conflict_sql = """
    WITH candidates AS (
      SELECT id, ean, brand, mpn, url,
        CASE WHEN url LIKE '%/fr/%' OR url LIKE '%/fr-be/%' THEN 0 ELSE 1 END AS fr_priority,
        ROW_NUMBER() OVER (PARTITION BY upper(brand), upper(mpn)
            ORDER BY (CASE WHEN url LIKE '%/fr/%' OR url LIKE '%/fr-be/%' THEN 0 ELSE 1 END), ean, id) AS rn_bmp
      FROM vendor_products
      WHERE ean IS NOT NULL AND trim(ean) <> ''
        AND brand IS NOT NULL AND trim(brand) <> ''
        AND mpn IS NOT NULL AND trim(mpn) <> ''
        AND article_name IS NOT NULL AND trim(article_name) <> ''
    ),
    winners AS (
      SELECT upper(brand) AS b, upper(mpn) AS m, ean AS kept_ean
      FROM candidates
      WHERE rn_bmp = 1
    )
    SELECT c.ean AS ean_discarded, c.brand, c.mpn, w.kept_ean AS ean_kept, c.url
    FROM candidates c
    JOIN winners w ON w.b = upper(c.brand) AND w.m = upper(c.mpn)
    WHERE c.rn_bmp > 1
    ORDER BY c.brand, c.mpn, c.id
    """
    rows = conn.execute(conflict_sql).fetchall()
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["ean_discarded", "brand", "mpn", "ean_kept", "url"])
        for r in rows:
            writer.writerow([r["ean_discarded"], r["brand"], r["mpn"], r["ean_kept"], r["url"]])
    print("conflicts exported", len(rows))

    # delete
    conn.execute("DELETE FROM master_index")

    # insert
    insert_sql = """
    WITH candidates AS (
      SELECT ean, brand, mpn, article_name,
        CASE WHEN url LIKE '%/fr/%' OR url LIKE '%/fr-be/%' THEN 0 ELSE 1 END AS fr_priority,
        ROW_NUMBER() OVER (PARTITION BY ean
            ORDER BY (CASE WHEN url LIKE '%/fr/%' OR url LIKE '%/fr-be/%' THEN 0 ELSE 1 END), id) AS rn_ean,
        ROW_NUMBER() OVER (PARTITION BY upper(brand), upper(mpn)
            ORDER BY (CASE WHEN url LIKE '%/fr/%' OR url LIKE '%/fr-be/%' THEN 0 ELSE 1 END), ean, id) AS rn_bmp
      FROM vendor_products
      WHERE ean IS NOT NULL AND trim(ean) <> ''
        AND brand IS NOT NULL AND trim(brand) <> ''
        AND mpn IS NOT NULL AND trim(mpn) <> ''
        AND article_name IS NOT NULL AND trim(article_name) <> ''
    )
    INSERT OR IGNORE INTO master_index (ean, brand, mpn, article_name)
    SELECT ean, brand, mpn, article_name
    FROM candidates
    WHERE rn_ean = 1 AND rn_bmp = 1
    """
    cur = conn.execute(insert_sql)
    print("inserted", cur.rowcount)
    conn.commit()
except Exception as e:
    conn.rollback()
    raise
finally:
    conn.close()

# checkpoint
conn2 = sqlite3.connect(db, timeout=30)
try:
    print("checkpoint", conn2.execute("PRAGMA wal_checkpoint(TRUNCATE)").fetchone())
except Exception as e:
    print("checkpoint error", e)
finally:
    conn2.close()

after = sizes() if False else None
# recompute sizes after
def sizes2():
    return {
        "db": os.path.getsize(db),
        "wal": os.path.getsize(os.path.join(base, "catalog.db-wal")) if os.path.exists(os.path.join(base, "catalog.db-wal")) else 0,
        "shm": os.path.getsize(os.path.join(base, "catalog.db-shm")) if os.path.exists(os.path.join(base, "catalog.db-shm")) else 0,
    }
print("after", sizes2())