# .tools/database/sitemaps.py
# by LECHAT Jérôme; creation date: 09/2025, latest edit: 11/2026

# INTERNAL(S)
import gzip
import io
import logging
import os
import time
from urllib.parse import unquote, urlsplit

# MODULE(S)
from database.utils.db_manager import DatabaseManager
from database.utils.http_client import HttpClient
from database.utils.web_manager import WebsiteManager

# EXTERNAL(S)
from lxml import etree

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
LOG = logging.getLogger(__name__)

MAX_SITEMAP_BYTES = 100 * 1024 * 1024
MAX_DECOMPRESSED_BYTES = 50 * 1024 * 1024
_CHUNK_SIZE = 1024 * 1024

_XML_PARSER = etree.XMLParser(
    resolve_entities=False,
    no_network=True,
    load_dtd=False,
    huge_tree=False,
    remove_comments=True,
    remove_pis=True,
)


def _gunzip(data: bytes, max_bytes: int | None = None) -> bytes:
    """Decompress gzip data with a byte limit to avoid gzip bombs."""

    limit = MAX_DECOMPRESSED_BYTES if max_bytes is None else max_bytes

    out = io.BytesIO()
    total = 0
    with gzip.GzipFile(fileobj=io.BytesIO(data)) as gz:
        while True:
            chunk = gz.read(_CHUNK_SIZE)
            if not chunk:
                break
            total += len(chunk)
            if total > limit:
                raise ValueError(f"Decompressed sitemap exceeds {limit} bytes")
            out.write(chunk)
    return out.getvalue()


class SitemapEngine:
    """
    Executes the full sitemap processing pipeline for the target website.

    This method orchestrates the complete workflow:
    1. Retrieves and resolves all sitemap URLs defined in the configuration.
    2. Filters the collected links based on domain and exclusion rules.
    3. Synchronizes the discovered URLs with the local SQLite database,
        tracking discovery status and updates.

    Returns:
        dict: A report dictionary containing counts of 'new', 'reactivated',
                'deactivated', and 'unchanged' URLs if successful.
        None: If the operation fails or no URLs are retrieved.
    """

    def __init__(self, data: WebsiteManager, website: str, *, db: DatabaseManager | None = None, http: HttpClient | None = None) -> None:
        # === variable(s) ===
        self.website: str = website
        self.data: WebsiteManager = data

        # === internal variable(s) ===
        self.SITE_CONFIG = self.data.get_site(website)
        self.website = website.lower()
        self.SITE_KEY = website.upper()
        self.BASE_URL: str = self.SITE_CONFIG.base_url
        self.DOMAIN: str = (urlsplit(self.BASE_URL).hostname or "").lower()
        if self.DOMAIN.startswith("www."):
            self.DOMAIN = self.DOMAIN[4:]
        self.SITEMAP_INDEX: list[str] = list(self.SITE_CONFIG.sitemaps)
        self.PRODUCT_URL_PATTERNS = self.SITE_CONFIG.product_url_patterns
        self.EXCLUDE_URL_PATTERNS = self.SITE_CONFIG.exclude_url_patterns

        self.DB_PATH: str = os.path.join(BASE_DIR, "resources", "db", "catalog.db")

        self.REQUEST_DELAY: float = 1.0

        # === parameter(s) & option(s) setup for HTTP client ===
        self.REQUESTS_HEADERS: dict[str, str] = {
            'Referer': self.BASE_URL,
            'Accept-Language': 'fr-FR,fr;q=0.9,en-US;q=0.8,en;q=0.7',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
            'Connection': 'keep-alive'
        }

        self.HTTP: HttpClient = http if http is not None else HttpClient(
            timeout=self.SITE_CONFIG.fetch.timeout,
            retries=self.SITE_CONFIG.fetch.retries,
            headers=self.REQUESTS_HEADERS,
        )
        self.DB: DatabaseManager = db if db is not None else DatabaseManager(self.DB_PATH)

    def __str__(self) -> str:
        return f"[SitemapEngine]: using {self.website} as 'Location' source."


    # === Private Method(s) ===
    def _is_safe_url(self, url: str) -> bool:
        """Validate scheme, host and port against the configured domain (SSRF guard)."""

        try:
            parsed = urlsplit(url)
            port = parsed.port
        except ValueError:
            return False

        if parsed.scheme not in ("http", "https"):
            return False

        if port is not None and port not in (80, 443):
            return False

        netloc = parsed.netloc
        if "@" in netloc:
            return False

        host = netloc.split(":", 1)[0].lower()
        if not host:
            return False

        domain = self.DOMAIN.lower()
        if not domain:
            return False

        return bool(host == domain or host == f"www.{domain}" or host.endswith(f".{domain}"))

    def _fetch_raw(self, url: str) -> bytes | None:
        """ Downloads a sitemap (plain XML or .gz) and returns raw bytes. """

        try:
            response = self.HTTP.get(url)
            response.raise_for_status()

            time.sleep(self.REQUEST_DELAY)

            body: bytes = response.body
            if len(body) > MAX_SITEMAP_BYTES:
                LOG.warning(f"[{self.website}] Sitemap too large for {url}: {len(body)} bytes")
                return None

            if url.endswith(".gz"):
                return _gunzip(body)
            return body

        except Exception:
            LOG.exception(f"[{self.website}] Fetch failed for {url}.")

        LOG.warning(f"[{self.website}] No responses for {url}.")
        return None

    def _filter(self, url: str) -> str | None:
        """ Excludes non-product URL(s). """

        if not self._is_safe_url(url):
            return None

        if self.PRODUCT_URL_PATTERNS and not any(pattern.search(url) for pattern in self.PRODUCT_URL_PATTERNS):
            return None
        if any(pattern.search(url) for pattern in self.EXCLUDE_URL_PATTERNS):
            return None

        return url

    def _resolve(self, url: str, seen: set[str], depth: int = 0) -> list[str]:
        """
        Resolves a single sitemap URL into a flat list of product URLs.

        If the sitemap is itself an index (contains <sitemap> entries),
        recurses into each child sitemap. If it's a urlset (contains
        <url>/<loc> entries), returns those URLs directly.
        """

        if url in seen:
            return []
        seen.add(url)

        if depth > 5:
            LOG.warning(f"Max recursion depth reached at {url} for {self.website}, stopping...")
            return []

        raw: bytes | None = self._fetch_raw(url)
        if raw is None:
            return []

        try:
            root = etree.fromstring(raw, _XML_PARSER)
        except (etree.XMLSyntaxError, ValueError, OSError):
            LOG.warning(f"[{self.website}] Ignoring malformed sitemap: {url}")
            return []

        def _local_name(tag: str) -> str:
            return tag.rsplit("}", 1)[-1]

        # sitemap containing other sitemap(s)
        child_sitemaps: list[str] = []
        for sitemap in root.iter():
            if not isinstance(sitemap.tag, str):
                continue
            if _local_name(sitemap.tag) != "sitemap":
                continue
            for loc in sitemap:
                if not isinstance(loc.tag, str):
                    continue
                if _local_name(loc.tag) == "loc" and loc.text:
                    child_url = loc.text.strip()
                    if self._is_safe_url(child_url):
                        child_sitemaps.append(child_url)
                    else:
                        LOG.warning(f"[{self.website}] Ignoring unsafe sitemap URL: {child_url}")

        if child_sitemaps:
            urls: list[str] = []
            for child in child_sitemaps:
                urls.extend(self._resolve(child, seen, depth + 1))

            LOG.info(f"{url} is an index with {len(child_sitemaps)} child sitemap(s) for {self.website}")
            return urls

        # sitemap containing product URL(s)
        product_urls: list[str] = []
        for url_el in root.iter():
            if not isinstance(url_el.tag, str):
                continue
            if _local_name(url_el.tag) != "url":
                continue
            for loc in url_el:
                if not isinstance(loc.tag, str):
                    continue
                if _local_name(loc.tag) == "loc" and loc.text:
                    product_url = unquote(loc.text.strip())
                    if self._is_safe_url(product_url):
                        product_urls.append(product_url)
                    else:
                        LOG.warning(f"[{self.website}] Ignoring unsafe product URL: {product_url}")

        LOG.info(f"{url} is a urlset with {len(product_urls)} URL(s) for {self.website}")
        return product_urls

    # === Public Method(s) ===
    def get_all_urls(self) -> list[str]:
        """ Returns the deduplicated, filtered list of product URLs for this site. """

        if not self.SITEMAP_INDEX:
            LOG.warning(f"[{self.website}] No entry_points configured.")
            return []

        seen_sitemaps: set[str] = set()
        all_urls: list[str] = []
        for entry in self.SITEMAP_INDEX:
            all_urls.extend(self._resolve(entry, seen_sitemaps))

        deduped = sorted({filtered for u in all_urls if (filtered := self._filter(u)) is not None})

        LOG.info(f"{len(deduped)} unique product URL(s) found for {self.website}")
        return deduped

    # === START ===
    def run(self) -> dict | None:
        LOG.info(f"SitemapEngine process started for {self.website}")

        self.DB.init_schema()

        try:
            urls = self.get_all_urls()
            if not urls:
                LOG.warning(f"No URL(s) found for {self.website}.")
                return None

            report = self.DB.sync_sitemap_urls(self.SITE_KEY, set(urls))

            LOG.info(f"SitemapEngine completed for {self.website}: {report}")
            return report

        except Exception as e:  # noqa: BLE001
            LOG.error(f"An error occured for {self.website}: {e}")
            return None

        finally:
            self.HTTP.close()
            self.DB.close()
