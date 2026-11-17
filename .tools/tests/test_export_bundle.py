# tests/test_export_bundle.py
import sqlite3
from pathlib import Path
from unittest.mock import patch

import pytest
from database.export_bundle import ConfigError, _load_config, export_bundle


def test_currency_null_raises_config_error(tmp_path: Path):
    """A1: Vérifie que 'currency: null' lève une ConfigError avant même l'export."""
    config_path = tmp_path / "config.json"
    config_path.write_text(
        '{"schema_version": 1, "sites": {"TEST": {"name": "Test", "base_url": "https://example.com", "currency": null}}}'
    )

    with pytest.raises(ConfigError, match="currency must be a non-empty string"):
        _load_config(config_path)


@patch("database.export_bundle._copy_master_index")
def test_cleanup_deletes_tmp_on_build_failure(mock_copy, tmp_path: Path):
    """A2: Vérifie que le .tmp.db est supprimé si la copie échoue en cours de route."""
    mock_copy.side_effect = KeyboardInterrupt("Arrêt manuel simulé")

    catalog = tmp_path / "catalog.db"
    with sqlite3.connect(catalog) as c:
        c.execute("CREATE TABLE vendor_products (site_key TEXT)")

    config = tmp_path / "config.json"
    config.write_text(
        '{"schema_version": 1, "sites": {"TEST": {"name": "Test", "base_url": "https://example.com"}}}'
    )

    out = tmp_path / "filon-catalog.db"

    with pytest.raises(KeyboardInterrupt):
        export_bundle(catalog, config, out)

    tmps = list(tmp_path.glob("*.tmp.db"))
    assert len(tmps) == 0, "Le fichier .tmp.db n'a pas été nettoyé après l'échec."


@patch("os.replace")
def test_cleanup_preserves_tmp_on_replace_failure(mock_replace, tmp_path: Path):
    """A2: Vérifie que si le build réussit mais l'atomic replace échoue, le .tmp.db est conservé pour analyse."""
    mock_replace.side_effect = OSError("Permission denied simulée sur le fichier final")

    catalog = tmp_path / "catalog.db"
    with sqlite3.connect(catalog) as c:
        c.execute(
            "CREATE TABLE master_index (ean TEXT, brand TEXT, mpn TEXT, article_name TEXT)"
        )
        c.execute(
            "CREATE TABLE vendor_products (site_key TEXT, url TEXT, ean TEXT, brand TEXT, "
            "mpn TEXT, article_name TEXT, catalog_price_nvat REAL, catalog_price_vat REAL, "
            "catalog_date TEXT, last_seen TEXT)"
        )

    config = tmp_path / "config.json"
    config.write_text(
        '{"schema_version": 1, "sites": {"TEST": {"name": "Test", "base_url": "https://example.com"}}}'
    )

    out = tmp_path / "filon-catalog.db"

    with pytest.raises(RuntimeError, match="échec du remplacement final"):
        export_bundle(catalog, config, out)

    tmps = list(tmp_path.glob("*.tmp.db"))
    assert len(tmps) == 1
    assert tmps[0].exists()
