# .tools/database/utils/web_manager.py
# by LECHAT Jérôme; creation date: 10/2026, latest change: 11/2026

# INTERNAL(S)
import json
import logging
import os
import re

from database.utils.validator import SiteConfig, WebsiteConfigRoot
from pydantic import ValidationError

# EXTERNAL(S)
from scrapling.parser import Selector

LOG = logging.getLogger(__name__)


class WebsiteManager:

    def __init__(self, filepath: str) -> None:
        # === variable(s) ===
        self.filepath = filepath
        self._config: WebsiteConfigRoot | None = None
        self._load_and_validate()

    def __str__(self) -> str:
        return f"[WebsiteManager]: using {self.filepath} as the reference file."


    # === Public Method(s) ===
    def load(self, website: str) -> dict:
            """
            Loads site-specific configuration from 'websites.json' as well as the different brand(s).

            Fetches the required metadata for the specified site
            (i.e base URLs, sitemap locations, precise HTML selectors, ...).
            """

            TAGS: dict = {}
            TARGET: str = website.upper()

            try:
                with open(self.filepath, encoding="utf-8") as f:
                    CONFIGS = json.load(f)

                TAGS = CONFIGS.get(TARGET)

                if not TAGS:
                    raise KeyError(f"Key value '{TARGET}' not in websites.json")

                return TAGS

            except Exception:
                LOG.exception("An error occurred during the 'load' operation")
                return {}

    def get_site(self, website: str) -> SiteConfig:
        """Return the already validated configuration for one enabled site."""
        target = website.lower()
        if self._config is None or target not in self._config.sites:
            raise KeyError(f"Le site '{target}' n'est pas configuré.")

        site = self._config.sites[target]
        if not site.enabled:
            raise ValueError(f"Le site '{target}' est désactivé.")
        return site

    def add(self, key: str, value: str) -> None:
        """
        Adds site-specific configuration in the 'websites.json'.

        Update the metadata of a specified site (i.e base URLs, sitemap locations, precise HTML selectors, ...)
        in the '.json' file.
        """

    def edit(self, key: str, velue: str) -> None:
        """
        Edits a site-specific configuration in the 'websites.json'.

        Modify the metadata of a specified site (i.e base URLs, sitemap locations, precise HTML selectors, ...)
        in the '.json' file.
        """

    def remove(self, key: str) -> None:
        """
        Removes a site-specific configuration in the 'websites.json'.

        Delete the metadata of a specified site (i.e base URLs, sitemap locations, precise HTML selectors, ...)
        in the '.json' file.
        """

    def _load_and_validate(self) -> None:
        if not os.path.exists(self.filepath):
            raise FileNotFoundError(f"Configuration introuvable: {self.filepath}")

        with open(self.filepath, encoding="utf-8") as f:
            try:
                raw_data = json.load(f)
            except json.JSONDecodeError as e:
                raise ValueError(f"JSON invalide dans {self.filepath}: {e}")

        try:
            self._config = WebsiteConfigRoot(**raw_data)
            LOG.info(f"Configuration validée (v{self._config.schema_version}). {len(self._config.sites)} site(s).")
        except ValidationError as e:
            raise ValueError(f"Erreur de schéma dans {self.filepath} :\n{e}")

# === Public Independant Method(s) ===
def clean_ean(raw: str | None = None) -> str | None:
    """ Standardizes the EAN by removing non-numeric characters. """

    cleaned = "".join(filter(str.isdigit, str(raw)))
    return cleaned if cleaned else None

def parse_price(text: str | None) -> float:
    """ Parses a raw price string into a clean float, automatically handling different thousand and decimal separators. """

    if not text or str(text).strip() in ("", "-", "None"):
        return 0.0

    try:
        clean = re.sub(r"[^\d.,]", "", str(text)) # keeping numbers, ',' & '.' only

        if not clean:
            return 0.0

        # separating logic
        if ',' in clean and '.' in clean:
            if clean.rfind('.') < clean.rfind(','): # ex: 1.234,56
                clean = clean.replace('.', '').replace(',', '.')
            else: # ex: 1,234.56
                clean = clean.replace(',', '')
        elif ',' in clean: # ex: 1234,56
            clean = clean.replace(',', '.')

        return float(clean)

    except (ValueError, TypeError):
        return 0.0

def jsonld_extractor(page: Selector) -> dict:
    """ Scans a Scrapling Selector for Schema.org Product JSON-LD data. """

    for script in page.css('script[type="application/ld+json"]'):
        text = script.css('::text').get()
        if not text:
            continue

        try:
            parsed = json.loads(str(text))
            items = [parsed] if isinstance(parsed, dict) else (parsed if isinstance(parsed, list) else [])

            for item in items:
                if isinstance(item, dict) and item.get("@type") == "Product":
                    return item # data found

        except Exception:  # noqa: BLE001, S112
            continue

    return {} # nothing found

def extract_from_jsonld(jsonld: dict, keywords: list) -> str | None:
    """ Retrieves data from the standard Schema.org JSON-LD object. """

    if not jsonld or not keywords:
        return None

    for path in keywords:
        parts = path.split('.') # i.e: separing "offers.price" to ["offers", "price"]
        current_val: list | dict | None = jsonld

        # navigating the JSON tree
        for part in parts:
            if isinstance(current_val, list) and current_val: # list ?
                current_val = current_val[0]
            if isinstance(current_val, dict): # dict ?
                current_val = current_val.get(part)
            else:
                current_val = None
                break # potentially broken path, taking no risks

        if current_val is not None:
            return str(current_val).strip()

    return None

def extract_heuristic(page: Selector, field: str, keywords: list) -> str | None:
    """
    Attempts to guess the value of a field without prior configuration,
    based on universal patterns (Regex, SEO) and the DOM structure.
    """

    TEXT_RAW_FLAT: str = page.get_all_text(" ")
    TEXT_RAW_STRUCTURED: str = "\n".join(
        line.strip() for line in page.get_all_text("\n").splitlines() if line.strip()
    )

    PATTERN_WORDS = "|".join([re.escape(k) for k in keywords]) if keywords else None

    def _find_by_class(pattern: str) -> Selector | None:
        for el in page.css('[class]'):
            cls = el.attrib.get('class', '')
            if re.search(pattern, cls, re.IGNORECASE):
                return el
        return None

    if field == "ean": # searching EAN
        if PATTERN_WORDS:
            DYNAMIC_PATTERN = r"(?:" + PATTERN_WORDS + r")[\W_]+(\d{13})\b"
            match = re.search(DYNAMIC_PATTERN, TEXT_RAW_STRUCTURED, re.IGNORECASE)
            if match:
                return match.group(1)

        match = re.search(r'\b(\d{13})\b', TEXT_RAW_FLAT)
        if match:
            return match.group(1)

    elif field == "brand": # searching brand
        if PATTERN_WORDS:
            DYNAMIC_PATTERN = r"(?:" + PATTERN_WORDS + r")[\W_]+([^\n]+)"
            match = re.search(DYNAMIC_PATTERN, TEXT_RAW_STRUCTURED, re.IGNORECASE)
            if match:
                return match.group(1).strip()

    elif field == "mpn": # searching mpn
        if PATTERN_WORDS:
            DYNAMIC_PATTERN = r"(?:" + PATTERN_WORDS + r")[\W_]+([A-Z0-9\-]{3,20})\b"
            match = re.search(DYNAMIC_PATTERN, TEXT_RAW_STRUCTURED, re.IGNORECASE)
            if match:
                return match.group(1).strip()

    elif field == "article": # searching article
        if PATTERN_WORDS:
            title_el = _find_by_class(PATTERN_WORDS)
            if title_el:
                text = title_el.get_all_text(" ").strip()
                if text:
                    return text

        h1_text = page.css('h1::text').get()
        if h1_text: # 99% of the time in H1 tag
            return str(h1_text).strip()

    elif field == "price":
        if PATTERN_WORDS:
            DYNAMIC_PATTERN = r"(?:" + PATTERN_WORDS + r")[\s\S]*?(\d+[.,]\d{2})"
            match = re.search(DYNAMIC_PATTERN, TEXT_RAW_STRUCTURED, re.IGNORECASE)
            if match:
                return match.group(1)

            price_el = _find_by_class(PATTERN_WORDS)
            if price_el:
                text = price_el.get_all_text(" ").strip()
                match = re.search(r'\d+[.,]\d{2}', text)
                if match:
                    return match.group()

        meta_prices = page.css('[itemprop="price"]')
        if meta_prices:
            meta_price = meta_prices[0]
            content_val = meta_price.attrib.get('content')
            if content_val:
                if isinstance(content_val, list):
                    content_val = " ".join(content_val)
                return str(content_val).strip()

            text = meta_price.get_all_text(" ").strip()
            match = re.search(r'\d+[.,]\d{2}', text)
            if match:
                return match.group()

    return None

# === PLAYGROUND ===
if __name__ == "__main__":
    data = WebsiteManager(filepath=os.path.join("resources", "data", "websites.json"))
    print(data)

    balises = data.load(website="FIXAMI")
    print(balises)
