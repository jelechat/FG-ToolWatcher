# .tools/database/export_bundle.py
from __future__ import annotations

import argparse
import contextlib
import json
import os
import sqlite3
import sys
import tempfile
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

BASE_DIR = Path(__file__).resolve().parents[2]

SCHEMA = """
PRAGMA foreign_keys = ON;

CREATE TABLE bundle_meta (
    key   TEXT PRIMARY KEY,
    value TEXT NOT NULL
) WITHOUT ROWID;

CREATE TABLE sites (
    site_key  TEXT PRIMARY KEY,
    name      TEXT NOT NULL,
    base_url  TEXT,
    currency  TEXT NOT NULL DEFAULT 'EUR',
    vat_rate  REAL
) WITHOUT ROWID;

CREATE TABLE site_recipes (
    site_key              TEXT PRIMARY KEY REFERENCES sites(site_key),
    recipe_schema_version INTEGER NOT NULL,
    config_json           TEXT NOT NULL,
    updated_at            TEXT NOT NULL
) WITHOUT ROWID;

CREATE TABLE master_index (
    ean          TEXT PRIMARY KEY,
    brand        TEXT NOT NULL,
    mpn          TEXT NOT NULL,
    article_name TEXT NOT NULL,
    UNIQUE(brand, mpn)
);

CREATE TABLE vendor_products (
    site_key TEXT NOT NULL REFERENCES sites(site_key),
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
);

CREATE INDEX idx_vp_ean  ON vendor_products(ean);
CREATE INDEX idx_vp_site ON vendor_products(site_key);
CREATE INDEX idx_vp_mpn  ON vendor_products(mpn);
"""


class ConfigError(Exception):
    """Erreur de validation de websites_beta.json."""


@dataclass(frozen=True)
class ExportReport:
    master_index: int
    vendor_products: int
    sites: int
    recipes: int
    excluded_sites: tuple[str, ...]


def _validate_config(config: object) -> None:
    if not isinstance(config, dict):
        raise ConfigError("root must be an object")

    schema_version = config.get("schema_version")
    try:
        if int(schema_version) != 1:  # type: ignore[arg-type]
            raise ConfigError("schema_version must be 1")
    except (TypeError, ValueError):
        raise ConfigError("schema_version must be 1")

    sites = config.get("sites")
    if not isinstance(sites, dict) or not sites:
        raise ConfigError("sites must be a non-empty object")

    seen: set[str] = set()
    for key, site in sites.items():
        upper_key = key.upper()
        if upper_key in seen:
            raise ConfigError(
                f"sites key conflict: '{key}' differs only by case from another key"
            )
        seen.add(upper_key)

        if not isinstance(site, dict):
            raise ConfigError(f"sites.{key} must be an object")

        enabled = site.get("enabled", True)
        if enabled is not True and enabled is not False:
            raise ConfigError(f"sites.{key}.enabled must be a boolean")
        if enabled is False:
            continue

        name = site.get("name")
        if not isinstance(name, str) or not name:
            raise ConfigError(f"sites.{key}.name must be a non-empty string")

        base_url = site.get("base_url")
        if (
            not isinstance(base_url, str)
            or not base_url.startswith(("http://", "https://"))
        ):
            raise ConfigError(
                f"sites.{key}.base_url must start with http:// or https://"
            )

        if "currency" in site:
            currency = site["currency"]
            if not isinstance(currency, str) or not currency.strip():
                raise ConfigError(f"sites.{key}.currency must be a non-empty string")

        vat_rate = site.get("vat_rate")
        if vat_rate is not None and (
            isinstance(vat_rate, bool)
            or not isinstance(vat_rate, (int, float))
        ):
            raise ConfigError(f"sites.{key}.vat_rate must be numeric")

        if "fields" in site:
            fields = site["fields"]
            if not isinstance(fields, dict) or not fields:
                raise ConfigError(f"sites.{key}.fields must be a non-empty object")

            for field_name, field in fields.items():
                if not isinstance(field, dict):
                    raise ConfigError(
                        f"sites.{key}.fields.{field_name} must be an object"
                    )

                strategies = field.get("strategies")
                if (
                    not isinstance(strategies, list)
                    or not strategies
                    or not all(isinstance(s, str) for s in strategies)
                ):
                    raise ConfigError(
                        f"sites.{key}.fields.{field_name}.strategies "
                        "must be a non-empty list of strings"
                    )


def _load_config(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as f:
        config = json.load(f)
    _validate_config(config)
    return config  # type: ignore[return-value]


def _copy_master_index(src: sqlite3.Connection, dst: sqlite3.Connection) -> int:
    cursor = src.execute(
        "SELECT ean, brand, mpn, article_name FROM master_index"
    )
    total = 0
    insert_sql = (
        "INSERT INTO master_index (ean, brand, mpn, article_name) "
        "VALUES (?, ?, ?, ?)"
    )
    while rows := cursor.fetchmany(5000):
        dst.executemany(insert_sql, rows)
        total += len(rows)
    return total


def _copy_vendor_products(
    src: sqlite3.Connection,
    dst: sqlite3.Connection,
    disabled: set[str],
) -> int:
    if disabled:
        placeholders = ",".join("?" * len(disabled))
        sql = (
            "SELECT site_key, url, ean, brand, mpn, article_name, "
            "catalog_price_nvat, catalog_price_vat, catalog_date, last_seen "
            f"FROM vendor_products WHERE upper(site_key) NOT IN ({placeholders})"
        )
        params = tuple(sorted(disabled))
    else:
        sql = (
            "SELECT site_key, url, ean, brand, mpn, article_name, "
            "catalog_price_nvat, catalog_price_vat, catalog_date, last_seen "
            "FROM vendor_products"
        )
        params = ()

    cursor = src.execute(sql, params)
    total = 0
    insert_sql = (
        "INSERT INTO vendor_products (site_key, url, ean, brand, mpn, "
        "article_name, catalog_price_nvat, catalog_price_vat, catalog_date, "
        "last_seen) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"
    )
    while rows := cursor.fetchmany(5000):
        normalized: list[tuple[object, ...]] = [
            (str(row[0]).upper(), *row[1:]) for row in rows
        ]
        dst.executemany(insert_sql, normalized)
        total += len(normalized)
    return total


def export_bundle(catalog: Path, config: Path, out: Path) -> ExportReport:
    """Projette catalog.db + websites_beta.json vers filon-catalog.db."""
    if not out.suffix:
        raise ValueError(f"--out must have a file extension: {out}")
    if out.resolve() == catalog.resolve():
        raise ValueError(f"--out cannot be the same as --catalog: {out}")
    if out.resolve() == config.resolve():
        raise ValueError(f"--out cannot be the same as --config: {out}")

    cfg = _load_config(config)
    recipe_schema_version = int(cfg["schema_version"])

    sites_cfg: dict[str, Any] = cfg["sites"]
    enabled_beta: dict[str, dict[str, Any]] = {}
    disabled_beta: set[str] = set()
    for key, site in sites_cfg.items():
        upper_key = key.upper()
        if site.get("enabled", True) is False:
            disabled_beta.add(upper_key)
        else:
            enabled_beta[upper_key] = site

    src = sqlite3.connect(
        f"file:{catalog.resolve().as_posix()}?mode=ro",
        uri=True,
        timeout=30,
    )
    tmp: Path | None = None
    build_ok = False
    try:
        src.execute("PRAGMA busy_timeout=30000")
        src.execute("BEGIN")

        catalog_sites = {
            row[0].upper()
            for row in src.execute(
                "SELECT DISTINCT site_key FROM vendor_products"
            ).fetchall()
            if row[0] is not None
        }

        out.parent.mkdir(parents=True, exist_ok=True)
        fd, tmp_path_str = tempfile.mkstemp(
            dir=out.parent, prefix=out.stem + ".", suffix=".tmp.db"
        )
        os.close(fd)
        tmp = Path(tmp_path_str)

        dst = sqlite3.connect(tmp, timeout=30, isolation_level=None)
        try:
            dst.execute("PRAGMA foreign_keys = ON")
            dst.executescript(SCHEMA)

            for key in sorted(enabled_beta):
                site = enabled_beta[key]
                dst.execute(
                    "INSERT INTO sites (site_key, name, base_url, currency, "
                    "vat_rate) VALUES (?, ?, ?, ?, ?)",
                    (
                        key,
                        site["name"],
                        site.get("base_url"),
                        site.get("currency", "EUR"),
                        site.get("vat_rate"),
                    ),
                )

            for key in sorted(catalog_sites - disabled_beta - set(enabled_beta)):
                dst.execute(
                    "INSERT INTO sites (site_key, name, base_url, currency, "
                    "vat_rate) VALUES (?, ?, ?, ?, ?)",
                    (key, key, None, "EUR", None),
                )

            now = datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")

            for key in sorted(enabled_beta):
                site = enabled_beta[key]
                fields = site.get("fields")
                if isinstance(fields, dict) and fields:
                    config_json = json.dumps(
                        site, ensure_ascii=False, separators=(",", ":")
                    )
                    dst.execute(
                        "INSERT INTO site_recipes (site_key, "
                        "recipe_schema_version, config_json, updated_at) "
                        "VALUES (?, ?, ?, ?)",
                        (key, recipe_schema_version, config_json, now),
                    )

            dst.execute("BEGIN")
            master_count = _copy_master_index(src, dst)
            vendor_count = _copy_vendor_products(src, dst, disabled_beta)
            dst.commit()

            all_site_keys = set(enabled_beta) | (catalog_sites - disabled_beta)
            sites_count = len(all_site_keys)
            recipes_count = sum(
                1
                for site in enabled_beta.values()
                if isinstance(site.get("fields"), dict) and site["fields"]
            )

            meta = [
                ("schema_version", "1"),
                ("recipe_schema_version", str(recipe_schema_version)),
                ("source_config", config.name),
                ("source_catalog", catalog.name),
                ("generated_at", now),
                ("count.master_index", str(master_count)),
                ("count.vendor_products", str(vendor_count)),
                ("count.sites", str(sites_count)),
                ("count.recipes", str(recipes_count)),
            ]
            dst.executemany(
                "INSERT INTO bundle_meta (key, value) VALUES (?, ?)", meta
            )
            dst.commit()
        finally:
            dst.close()

        src.execute("ROLLBACK")

        build_ok = True
        try:
            os.replace(tmp, out)
        except OSError as exc:
            raise RuntimeError(
                f"Le fichier construit est dans {tmp} ; "
                f"échec du remplacement final : {exc}"
            ) from exc
    except BaseException:
        if not build_ok and tmp is not None and tmp.exists():
            with contextlib.suppress(OSError):
                tmp.unlink(missing_ok=True)
        raise
    finally:
        src.close()

    return ExportReport(
        master_index=master_count,
        vendor_products=vendor_count,
        sites=sites_count,
        recipes=recipes_count,
        excluded_sites=tuple(sorted(disabled_beta)),
    )


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Exporte une base filon-catalog.db distribuable."
    )
    parser.add_argument(
        "--catalog",
        type=Path,
        default=BASE_DIR / "resources" / "db" / "catalog.db",
        help="Chemin vers catalog.db (lecture seule)",
    )
    parser.add_argument(
        "--config",
        type=Path,
        default=BASE_DIR / "resources" / "data" / "websites_beta.json",
        help="Chemin vers websites_beta.json",
    )
    parser.add_argument(
        "--out",
        type=Path,
        default=BASE_DIR / "resources" / "db" / "client-catalog.db",
        help="Chemin de sortie filon-catalog.db",
    )
    args = parser.parse_args()

    try:
        report = export_bundle(args.catalog, args.config, args.out)
    except ConfigError as exc:
        print(f"websites_beta.json: {exc}", file=sys.stderr)
        raise SystemExit(2) from exc
    except sqlite3.OperationalError as exc:
        print(f"catalog.db introuvable ou non lisible: {exc}", file=sys.stderr)
        raise SystemExit(1) from exc
    except Exception as exc:
        print(f"Erreur: {exc}", file=sys.stderr)
        raise SystemExit(1) from exc

    with contextlib.closing(sqlite3.connect(args.out, timeout=30)) as conn:
        recipe_sites = {
            row[0] for row in conn.execute("SELECT site_key FROM site_recipes")
        }
        all_sites = {
            row[0] for row in conn.execute("SELECT site_key FROM sites")
        }
    sans_recipe = sorted(all_sites - recipe_sites)

    print(f"Export terminé : {args.out}")
    print(f"  master_index    : {report.master_index}")
    print(f"  vendor_products : {report.vendor_products}")
    print(f"  sites           : {report.sites}")
    print(f"  recipes         : {report.recipes}")
    print(f"  exclus          : {', '.join(report.excluded_sites) or '(aucun)'}")
    print(f"  sites sans recette : {', '.join(sans_recipe) or '(aucun)'}")


if __name__ == "__main__":
    main()
