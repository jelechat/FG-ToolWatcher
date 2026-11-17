# scratch/filon_resolver/resolver.py
# Prototype isolé de resolver Filon sur Scrapling.

from __future__ import annotations

import html
import re
import warnings
from typing import Any

from scrapling.parser import Selector

STRATEGY_KINDS = ("jsonld", "css", "xpath", "meta", "attr", "text")

_EAN_LENGTHS = (8, 12, 13)
_MPN_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._/+-]{1,49}$")
_EAN_DIGITS_RE = re.compile(r"\d[\d\s-]{6,}\d")
_MPN_LABEL_RE = re.compile(
    r"^(?:réf\.?\s*n°|code article(?: du fournisseur)?|mpn|référence)\s*[:\-]\s*",
    re.IGNORECASE,
)


def _clean_text(text: str | None) -> str | None:
    if text is None:
        return None
    text = html.unescape(text)
    text = " ".join(text.split())
    return text.strip() or None


def strip_prefix(value: str, kind: str) -> str:
    """Retire un préfixe `kind:` déjà présent dans une valeur de source."""
    prefix = f"{kind}:"
    if value.startswith(prefix):
        return value[len(prefix):]
    return value


def normalize_strategy(source: str | dict[str, str]) -> str | None:
    """Convertit une source `{"css": "..."}` en stratégie `css:...`."""
    if isinstance(source, str):
        text = source.strip()
        return text or None
    if not isinstance(source, dict) or len(source) != 1:
        return None
    kind, value = next(iter(source.items()))
    if kind not in STRATEGY_KINDS or not isinstance(value, str):
        return None
    value = strip_prefix(value.strip(), kind)
    if not value:
        return None
    return f"{kind}:{value}"


def _navigate_jsonld(data: Any, path: str) -> Any:
    """Navigue dans un JSON-LD, y compris quand `offers`/`@graph` est une liste."""
    path = path.strip()
    if not path:
        return data

    indexed = re.match(r"^\[(\d+)\]\s*\.?\s*(.*)$", path)
    if indexed:
        if not isinstance(data, list):
            return None
        index = int(indexed.group(1))
        if index >= len(data):
            return None
        return _navigate_jsonld(data[index], indexed.group(2))

    head, _, tail = path.partition(".")

    bracketed = re.match(r"^([^\[\]]+)\[(\d+)\]$", head)
    if bracketed:
        key, index = bracketed.group(1), int(bracketed.group(2))
        node = data.get(key) if isinstance(data, dict) else None
        if not isinstance(node, list) or index >= len(node):
            return None
        return _navigate_jsonld(node[index], tail)

    if isinstance(data, dict):
        node = data.get(head)
        if node is None:
            return None
        return _navigate_jsonld(node, tail)

    if isinstance(data, list):
        if head.isdigit():
            index = int(head)
            if index >= len(data):
                return None
            return _navigate_jsonld(data[index], tail)
        for item in data:
            node = _navigate_jsonld(item, path)
            if node is not None:
                return node
        return None

    return None


def _css_query(page: Selector, selector: str) -> Selector | None:
    result = page.css(selector)
    if result and len(result) > 0:
        return result.first
    return None


def _xpath_query(page: Selector, expr: str) -> Selector | None:
    result = page.xpath(expr)
    if result and len(result) > 0:
        return result.first
    return None


def _meta_query(page: Selector, key: str, value: str) -> Selector | None:
    el = _css_query(page, f"meta[{key}='{value}' i]")
    if el is not None:
        return el
    return _css_query(page, f"meta[{key}='{value}']")


def _attr_query(page: Selector, name: str, value: str) -> Selector | None:
    return _css_query(page, f"[{name}='{value}' i]")


def _find_by_label(page: Selector, label: str) -> Selector | None:
    # `.//` garde la recherche dans le scope ; `//` repartirait de la racine.
    expr = f".//*[contains(text(),{label!r})]"
    result = page.xpath(expr)
    if result and len(result) > 0:
        return result.first
    return None


def _node_text(el: Selector | None) -> str | None:
    if el is None:
        return None
    return _clean_text(el.get_all_text(" "))


def apply_strategy(
    page: Selector,
    jsonld: dict[str, Any],
    strategy: str | dict[str, str],
    scope: Selector | None = None,
) -> str | None:
    normalized = normalize_strategy(strategy)
    if normalized is None:
        return None

    root = scope if scope is not None else page

    if normalized.startswith("jsonld:"):
        path = normalized[len("jsonld:"):]
        value = _navigate_jsonld(jsonld, path)
        return _clean_text(str(value)) if value is not None else None

    if normalized.startswith("css:"):
        rest = normalized[len("css:"):]
        if "::attr(" in rest:
            selector, attr_name = rest.split("::attr(", 1)
            attr_name = attr_name.rstrip(")")
            el = _css_query(root, selector)
            if el is not None:
                return _clean_text(el.attrib.get(attr_name))
            return None
        if "::text" in rest:
            selector = rest.split("::text", 1)[0]
        else:
            selector = rest
        el = _css_query(root, selector)
        return _node_text(el)

    if normalized.startswith("xpath:"):
        expr = normalized[len("xpath:"):]
        el = _xpath_query(root, expr)
        return _node_text(el)

    if normalized.startswith("meta:"):
        rest = normalized[len("meta:"):]
        if "=" not in rest:
            return None
        key, value = rest.split("=", 1)
        # `<meta>` vit dans `<head>` : on interroge toujours la page entière.
        el = _meta_query(page, key, value)
        if el is not None:
            return _clean_text(el.attrib.get("content"))
        return None

    if normalized.startswith("attr:"):
        rest = normalized[len("attr:"):]
        if "::" not in rest:
            return None
        attr_part, mode = rest.split("::", 1)
        if "=" not in attr_part:
            return None
        name, value = attr_part.split("=", 1)
        # Comme `meta:`, un attribut peut vivre hors du scope (itemprop, etc.).
        el = _attr_query(page, name, value)
        if el is None:
            return None
        if mode == "content":
            return _clean_text(el.attrib.get("content"))
        if mode == "text":
            return _node_text(el)
        return None

    if normalized.startswith("text:"):
        rest = normalized[len("text:"):]
        if "->" not in rest:
            return None
        label, action = rest.split("->", 1)
        label = label.strip()
        action = action.strip()
        el = _find_by_label(root, label)
        if el is None:
            return None

        if action == "next":
            return _node_text(el.next)
        if action == "parent":
            return _node_text(el.parent)
        if action == "parent_text":
            return _node_text(el.parent)
        if action == "after":
            # Texte après le libellé dans le même élément.
            text = el.get_all_text(" ")
            idx = text.lower().find(label.lower())
            if idx >= 0:
                return _clean_text(text[idx + len(label):])
            return None
        return None

    return None


def resolve_scope(page: Selector, selector: str | None) -> Selector:
    """Résout le scope CSS ; retombe sur la page avec un avertissement."""
    if not selector:
        return page
    try:
        el = _css_query(page, selector)
    except Exception as exc:  # noqa: BLE001 - sélecteur CSS invalide côté configuration
        warnings.warn(
            f"scope {selector!r} invalide ({exc}); repli sur la page",
            RuntimeWarning,
            stacklevel=2,
        )
        return page
    if el is None:
        warnings.warn(
            f"scope {selector!r} introuvable; repli sur la page",
            RuntimeWarning,
            stacklevel=2,
        )
        return page
    return el


def _ean_checksum_ok(digits: str) -> bool:
    body, check = digits[:-1], int(digits[-1])
    total = 0
    for index, char in enumerate(reversed(body)):
        total += int(char) * (3 if index % 2 == 0 else 1)
    return (10 - total % 10) % 10 == check


def normalize_ean(value: str | None) -> str | None:
    """Extrait un EAN/UPC valide (longueur + checksum) d'une valeur bruitée."""
    text = _clean_text(value)
    if text is None:
        return None
    match = _EAN_DIGITS_RE.search(text)
    if match is None:
        return None
    digits = re.sub(r"\D", "", match.group(0))
    if len(digits) not in _EAN_LENGTHS or not _ean_checksum_ok(digits):
        return None
    return digits


def normalize_mpn(value: str | None, brand: str | None = None) -> str | None:
    """Nettoie un MPN, retire le préfixe de marque et valide le motif."""
    text = _clean_text(value)
    if text is None:
        return None
    text = _MPN_LABEL_RE.sub("", text).strip()
    clean_brand = _clean_text(brand)
    if clean_brand:
        text = re.sub(
            rf"^{re.escape(clean_brand)}(?:\s+|[-–/])",
            "",
            text,
            flags=re.IGNORECASE,
        ).strip()
    if not _MPN_RE.match(text):
        return None
    return text.upper()


def parse_price(value: str | None) -> float | None:
    """Parse un prix européen (`1.968,03 €`, `325,98`, `325.98`)."""
    text = _clean_text(value)
    if text is None:
        return None
    text = (
        text.replace("\u00a0", " ")
        .replace("€", "")
        .replace("EUR", "")
        .strip()
    )
    text = re.sub(r"[^\d,.\-]", "", text)
    if not text:
        return None

    if "," in text and "." in text:
        if text.rfind(",") > text.rfind("."):
            text = text.replace(".", "").replace(",", ".")
        else:
            text = text.replace(",", "")
    elif "," in text:
        if text.count(",") == 1:
            text = text.replace(",", ".")
        else:
            text = text.replace(",", "")

    if text.count(".") > 1:
        head, _, tail = text.rpartition(".")
        text = head.replace(".", "") + "." + tail

    try:
        price = float(text)
    except ValueError:
        return None
    if price <= 0 or price > 100000:
        return None
    return price


def normalize_field_value(
    value: str | None,
    rule: str | None,
    brand: str | None = None,
) -> str | None:
    if rule == "ean":
        return normalize_ean(value)
    if rule == "mpn":
        return normalize_mpn(value, brand)
    if rule == "price":
        price = parse_price(value)
        return str(price) if price is not None else None
    return _clean_text(value)


def resolve_field(
    page: Selector,
    jsonld: dict[str, Any],
    field: dict[str, Any],
    scope: Selector | None = None,
    brand: str | None = None,
) -> str | None:
    """Résout un champ et ignore les candidats vides ou invalides."""
    sources = field.get("sources") or []
    rule = (field.get("validate") or {}).get("type")
    for source in sources:
        value = apply_strategy(page, jsonld, source, scope)
        normalized = normalize_field_value(value, rule, brand)
        if normalized is not None:
            return normalized
    return None


def resolve_record(
    page: Selector,
    jsonld: dict[str, Any],
    fields: dict[str, dict[str, Any]],
    scope_selector: str | None = None,
) -> dict[str, str | None]:
    """Résout tous les champs d'une fiche, la marque d'abord pour le MPN."""
    scope = resolve_scope(page, scope_selector)
    record: dict[str, str | None] = {}

    brand_field = fields.get("brand")
    if brand_field is not None:
        record["brand"] = resolve_field(page, jsonld, brand_field, scope)

    for name, field in fields.items():
        if name == "brand":
            continue
        record[name] = resolve_field(
            page,
            jsonld,
            field,
            scope,
            brand=record.get("brand"),
        )
    return record


def product_identity(
    record: dict[str, str | None],
    site: str,
    url: str,
) -> str:
    """Applique la règle d'identité : ean > mpn:marque:mpn > uid:site:url."""
    ean = record.get("ean")
    if ean:
        return f"ean:{ean}"
    brand = record.get("brand")
    mpn = record.get("mpn")
    if brand and mpn:
        return f"mpn:{brand.upper()}:{mpn.upper()}"
    return f"uid:{site}:{url}"


def resolve(
    page: Selector,
    jsonld: dict[str, Any],
    strategies: list[str | dict[str, str]],
    scope: Selector | None = None,
) -> str | None:
    for strategy in strategies:
        value = apply_strategy(page, jsonld, strategy, scope)
        if value:
            return value
    return None
