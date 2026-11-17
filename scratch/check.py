import sqlite3, os
base = r"C:\Users\ljero\Documents Personnels\.projects\FG-ToolWatcher\resources\db"
db = os.path.join(base, "catalog.db")
c = sqlite3.connect(db)
print("integrity", c.execute("PRAGMA integrity_check").fetchone())
print("vp", c.execute("SELECT COUNT(*) FROM vendor_products").fetchone())
print("fixami", c.execute("SELECT COUNT(*) FROM vendor_products WHERE site_key='FIXAMI'").fetchone())
print("fixami_fr", c.execute("SELECT COUNT(*) FROM vendor_products WHERE site_key='FIXAMI' AND url LIKE '%/fr/%'").fetchone())
print("master", c.execute("SELECT COUNT(*) FROM master_index").fetchone())
print("wal size", os.path.getsize(os.path.join(base,"catalog.db-wal")) if os.path.exists(os.path.join(base,"catalog.db-wal")) else 0)
print("shm size", os.path.getsize(os.path.join(base,"catalog.db-shm")) if os.path.exists(os.path.join(base,"catalog.db-shm")) else 0)
print("db size", os.path.getsize(db))
c.close()