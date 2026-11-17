# .tools/database/utils/brands.py
import json
import re
import unicodedata


def normalize(text: str) -> str:
    """Majuscules, sans accents, symboles remplacés par espaces, espaces simples."""
    ascii_text = unicodedata.normalize("NFKD", text).encode("ASCII", "ignore").decode("utf-8")
    ascii_text = re.sub(r"[^A-Za-z0-9]+", " ", ascii_text.upper())
    return " ".join(ascii_text.split())


class BrandRegistry:
    """Charge brands.json (source de vérité) et expose des lookups rapides."""

    def __init__(self, brands: dict[str, list[str]]) -> None:
        self._lookup: dict[str, str] = {}
        for canonical, aliases in brands.items():
            for alias in aliases:
                self._lookup.setdefault(normalize(alias), canonical)
            self._lookup.setdefault(normalize(canonical), canonical)

    @classmethod
    def from_json(cls, path: str) -> "BrandRegistry":
        with open(path, encoding="utf-8") as f:
            return cls(json.load(f))

    def resolve(self, text: str | None) -> str | None:
        """Retrouve la marque canonique dans un texte (limites de mot, alias les plus longs d'abord)."""
        if not text:
            return None
        text_norm = normalize(text)
        for alias in sorted(self._lookup, key=len, reverse=True):
            if re.search(rf"\b{re.escape(alias)}\b", text_norm):
                return self._lookup[alias]
        return None

    def is_known(self, name: str | None) -> bool:
        if not name:
            return True
        return normalize(name) in self._lookup

    def clean_mpn(self, raw: str | None, canonical: str | None = None) -> str | None:
        if not raw:
            return None
        cleaned = " ".join(str(raw).upper().split())
        if canonical:
            brand = re.escape(normalize(canonical))
            cleaned = re.sub(rf"\b{brand}\b", "", cleaned, flags=re.IGNORECASE)
            cleaned = " ".join(cleaned.split())
        return cleaned or None
