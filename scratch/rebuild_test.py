import sqlite3, os
base = r"C:\Users\ljero\Documents Personnels\.projects\FG-ToolWatcher\resources\db"
db = os.path.join(base, "catalog.db")
conn = sqlite3.connect(db)
conn.execute("PRAGMA foreign_keys=ON")
# candidate CTE
sql = """
WITH candidates AS (
  SELECT
    id, ean, brand, mpn, article_name, url,
    CASE WHEN url LIKE '%/fr/%' OR url LIKE '%/fr-be/%' THEN 0 ELSE 1 END AS fr_priority,
    ROW_NUMBER() OVER (PARTITION BY ean ORDER BY (CASE WHEN url LIKE '%/fr/%' OR url LIKE '%/fr-be/%' THEN 0 ELSE 1 END), id) AS rn_ean,
    ROW_NUMBER() OVER (PARTITION BY upper(brand), upper(mpn) ORDER BY (CASE WHEN url LIKE '%/fr/%' OR url LIKE '%/fr-be/%' THEN 0 ELSE 1 END), ean, id) AS rn_bmp
  FROM vendor_products
  WHERE ean IS NOT NULL AND trim(ean) <> ''
    AND brand IS NOT NULL AND trim(brand) <> ''
    AND mpn IS NOT NULL AND trim(mpn) <> ''
    AND article_name IS NOT NULL AND trim(article_name) <> ''
)
SELECT COUNT(*) FROM candidates WHERE rn_ean=1 AND rn_bmp=1
"""
print("new master count", conn.execute(sql).fetchone())
# conflicts discarded by rn_bmp > 1
sql2 = """
WITH candidates AS (
  SELECT id, ean, brand, mpn, article_name, url,
    ROW_NUMBER() OVER (PARTITION BY upper(brand), upper(mpn) ORDER BY (CASE WHEN url LIKE '%/fr/%' OR url LIKE '%/fr-be/%' THEN 0 ELSE 1 END), ean, id) AS rn_bmp
  FROM vendor_products
  WHERE ean IS NOT NULL AND trim(ean) <> ''
    AND brand IS NOT NULL AND trim(brand) <> ''
    AND mpn IS NOT NULL AND trim(mpn) <> ''
    AND article_name IS NOT NULL AND trim(article_name) <> ''
)
SELECT COUNT(*) FROM candidates WHERE rn_bmp > 1
"""
print("conflicts", conn.execute(sql2).fetchone())
# distinct ean complete
print("ean nonnull", conn.execute("SELECT COUNT(*) FROM vendor_products WHERE ean IS NOT NULL AND trim(ean)<>''").fetchone())
print("distinct ean", conn.execute("SELECT COUNT(DISTINCT ean) FROM vendor_products WHERE ean IS NOT NULL AND trim(ean)<>''").fetchone())
conn.close()