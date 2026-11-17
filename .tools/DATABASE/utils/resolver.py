# .tools/utils/resolver.py

# INTERNAL(S)
import html
import re
from dataclasses import dataclass

# EXTERNAL(S)
from scrapling.parser import Selector


# === AST(s) ===
@dataclass(frozen=True)
class JsonLd: path: tuple[str | int, ...]

@dataclass(frozen=True)
class Meta: key: str; value: str

@dataclass(frozen=True)
class Attr: name: str; value: str; extract: str

@dataclass(frozen=True)
class Css: selector: str

@dataclass(frozen=True)
class XPath: expr: str

@dataclass(frozen=True)
class TextLabel: label: str; action: str

STRATEGY = JsonLd | Meta | Attr | Css | XPath | TextLabel

@dataclass(frozen=True)
class FieldResult:
    value: str | float | None
    strategy_used: STRATEGY | None
    attempts: tuple[tuple[STRATEGY, object | None, str | None], ...]

# === COMPILER ===
_JSONLD_TOKEN_RE = re.compile(r"([A-Za-z0-9_@-]+)|\[(\d+)\]")

def compile_strategy(raw: str | dict[str, str]) -> STRATEGY:
    if isinstance(raw, dict):
        kind, body = next(iter(raw.items()))
    else:
        if ":" not in raw: raise ValueError(f"':' missing: {raw!r}")
        kind, _, body = raw.partition(":")

    body = body.strip()

    match kind:
        case "jsonld":
            tokens = []
            for word, idx in _JSONLD_TOKEN_RE.findall(body):
                if word: tokens.append(word)
                elif idx: tokens.append(int(idx))
            if not tokens: raise ValueError(f"Chemin invalide : {body!r}")
            return JsonLd(tuple(tokens))
        case "css":
            return Css(selector=body)
        case "xpath":
            return XPath(expr=body)
        case "meta":
            key, val = body.split("=", 1)
            return Meta(key=key.strip(), value=val.strip())
        case "attr":
            main, sep, extract = body.rpartition("::")
            if not sep or extract not in ("content", "text") or "=" not in main:
                raise ValueError(f"Syntaxe attr invalide : {body!r}")
            name, val = main.split("=", 1)
            return Attr(name=name.strip(), value=val.strip(), extract=extract)
        case "text":
            if "->" not in body:
                raise ValueError(f"Syntaxe text invalide : {body!r}")
            label, action = map(str.strip, body.split("->", 1))
            if action not in ("next", "parent", "after"):
                raise ValueError(f"Action text inconnue : {action!r}")
            return TextLabel(label=label, action=action)
        case _:
            raise ValueError(f"Type inconnu : {kind!r}")

# --- MOTEUR D'EXÉCUTION SCRAPLING ---
def _clean_text(text: str | None) -> str | None:
    return " ".join(html.unescape(text).split()).strip() if text else None

def _node_text(el: Selector | None) -> str | None:
    return _clean_text(el.get_all_text(" ")) if el else None

def _xpath_literal(v: str) -> str:
    if "'" not in v: return f"'{v}'"
    if '"' not in v: return f'"{v}"'
    return "concat(" + ", \"'\", ".join(f"'{p}'" for p in v.split("'")) + ")"

def execute_strategy(page: Selector, jsonld: dict[str, object], strategy: STRATEGY, scope: Selector | None = None) -> str | None:
    root = scope if scope is not None else page
    match strategy:
        case JsonLd(path):
            current: object = jsonld
            for token in path:
                if isinstance(token, str):
                    if not isinstance(current, dict):
                        return None
                    current = current.get(token)
                elif isinstance(token, int):
                    if not isinstance(current, list):
                        return None
                    next_value: object | None = None
                    for index, item in enumerate(current):
                        if index == token:
                            next_value = item
                            break
                    current = next_value
                else:
                    return None
                if current is None:
                    return None
            return _clean_text(str(current))

        case Css(selector):
            if "::attr(" in selector or "::text" in selector:
                return _clean_text(root.css(selector).get())
            return _node_text(root.css(selector).first)

        case XPath(expr):
            if "/@" in expr or "/text()" in expr:
                return _clean_text(root.xpath(expr).get())
            return _node_text(root.xpath(expr).first)

        case Meta(key, value):
            return _clean_text(root.css(f"meta[{key}='{value}' i]::attr(content)").get())

        case Attr(name, value, extract):
            if extract == "content": return _clean_text(root.css(f"[{name}='{value}' i]::attr(content)").get())
            return _node_text(root.css(f"[{name}='{value}' i]").first)

        case TextLabel(label, action):
            safe_label = _xpath_literal(label)
            el = root.xpath(f"//*[contains(text(), {safe_label})]").first if root.xpath(f"//*[contains(text(), {safe_label})]") else None
            if not el: return None

            match action:
                case "next": return _node_text(el.next)
                case "parent": return _node_text(el.parent)
                case "after":
                    text = el.get_all_text(" ")
                    idx = text.lower().find(label.lower())
                    return _clean_text(text[idx + len(label):]) if idx >= 0 else None
    return None

# --- PARSEUR INTERNE ET VALIDATEUR ---
def _parse_price_strict(text: str | int | float) -> float:
    if not text or str(text).strip() in ("", "-", "None"):
        raise ValueError("Prix vide.")
    clean = re.sub(r"[^\d.,]", "", str(text))
    if not clean: raise ValueError("Aucun chiffre trouvé.")

    if ',' in clean and '.' in clean:
        if clean.rfind('.') < clean.rfind(','): clean = clean.replace('.', '').replace(',', '.')
        else: clean = clean.replace(',', '')
    elif ',' in clean:
        clean = clean.replace(',', '.')

    try: return float(clean)
    except ValueError: raise ValueError(f"Conversion impossible : {clean}")

def _validate_ean13_checksum(ean: str) -> bool:
    if not ean.isdigit() or len(ean) != 13: return False
    digits = [int(x) for x in ean]
    checksum = (10 - sum(d * (3 if i % 2 else 1) for i, d in enumerate(digits[:-1])) % 10) % 10
    return checksum == digits[-1]

def process_and_validate(raw_val: str, rules: dict[str, object] | None) -> str | float:
    val_type = rules.get("type") if rules else "text"

    if val_type == "price":
        value = _parse_price_strict(raw_val)
    elif val_type == "ean":
        value = "".join(filter(str.isdigit, str(raw_val)))
        if not value: raise ValueError("Aucun chiffre dans l'EAN.")
    else:
        value = " ".join(str(raw_val).split()).strip()

    if not rules: return value

    if val_type == "ean":
        if not isinstance(value, str):
            raise ValueError("La valeur EAN n'est pas du texte.")
        if len(value) not in (8, 13):
            raise ValueError("Longueur EAN invalide")
        if len(value) == 13 and not _validate_ean13_checksum(value):
            raise ValueError("Checksum EAN invalide")
    elif val_type in ("text", "mpn"):
        if not isinstance(value, str):
            raise ValueError(f"La valeur extraite pour '{val_type}' n'est pas un texte.")
        if val_type == "mpn" and not value.strip():
            raise ValueError("MPN vide.")

    return value

def resolve_field(page, jsonld, compiled_strategies, validate_rules=None, scope=None) -> FieldResult:
    attempts = []
    for strategy in compiled_strategies:
        raw_val = execute_strategy(page, jsonld, strategy, scope)
        if raw_val is None:
            attempts.append((strategy, None, "Introuvable"))
            continue
        try:
            final_val = process_and_validate(raw_val, validate_rules)
            attempts.append((strategy, raw_val, "Success"))
            return FieldResult(value=final_val, strategy_used=strategy, attempts=tuple(attempts))
        except ValueError as e:
            attempts.append((strategy, raw_val, str(e)))

    return FieldResult(value=None, strategy_used=None, attempts=tuple(attempts))
