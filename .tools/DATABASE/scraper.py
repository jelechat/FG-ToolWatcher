# .tools/database/scraper.py
# by LECHAT Jérôme; creation date: 09/2025, latest edit: 11/2026

# INTERNAL(S)
import json
import logging
import os
import random
import time
from datetime import datetime

# MODULE(S)
from database.utils.brands import BrandRegistry
from database.utils.db_manager import DatabaseManager, ProductData
from database.utils.http_client import HttpClient
from database.utils.resolver import compile_strategy, resolve_field
from database.utils.web_manager import WebsiteManager, jsonld_extractor

# EXTERNAL(S)
from scrapling.parser import Selector

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
LOG = logging.getLogger(__name__)

class ScraperEngine:
    def __init__(self, data: WebsiteManager, website: str, *, db: DatabaseManager | None = None, http: HttpClient | None = None, brands: BrandRegistry | None = None) -> None:
        # === variable(s) ===
        self.data: WebsiteManager = data
        self.website: str = website.lower()

        # === internal variable(s) ===
        self.SITE_CONFIG = self.data.get_site(self.website)
        self.SITE_KEY = website.upper()
        self.COMPILED_FIELDS = {
            name: [compile_strategy(source) for source in field.sources]
            for name, field in self.SITE_CONFIG.fields.items()
        }

        self.unknown_brands: set = set()

        self.DB_PATH: str = os.path.join(BASE_DIR, "resources", "db", "catalog.db")

        # === parameter(s) & option(s) setup for HTTP client ===
        self.REQUESTS_HEADERS: dict[str, str] = {
            'Referer': self.SITE_CONFIG.base_url,
            'Accept-Language': 'fr-FR,fr;q=0.9,en-US;q=0.8,en;q=0.7'
        }
        self.REQUEST_DELAY: float = 1.0
        self.SAVE_COUNTER: int = 0
        self.SAVE_THRESHOLD: int = 10

        # === service(s) ===
        self.BRANDS: BrandRegistry = brands if brands is not None else BrandRegistry.from_json(
            os.path.join(BASE_DIR, "resources", "data", "brands.json")
        )
        self.DB: DatabaseManager = db if db is not None else DatabaseManager(self.DB_PATH)
        self.HTTP: HttpClient = http if http is not None else HttpClient(
            timeout=self.SITE_CONFIG.fetch.timeout,
            retries=self.SITE_CONFIG.fetch.retries,
            headers=self.REQUESTS_HEADERS,
        )

    def __str__(self) -> str:
        return f"[ScapperEngine]: using {self.website} as 'Location' source."


    # === START ===
    def run(self) -> None:
        LOG.info(f"ScraperEngine process started for {self.website}")

        try:
            self.DB.init_schema()

            pending_urls: list[str] = self.DB.get_pending_urls(self.SITE_KEY)
            LOG.info(f"Found {len(pending_urls)} new URL(s) to process for {self.website}")

            products_batch: list[ProductData] = []

            for product_url in pending_urls:
                try:
                    response = self.HTTP.get(product_url)
                    if response.status >= 400:
                        LOG.warning(f"HTTP {response.status} for {product_url}")
                        continue

                    page = Selector(response.body.decode(response.encoding or "utf-8"))
                    data: ProductData | None = self._process_product(page=page, link=product_url)
                    if not data:
                        continue

                    products_batch.append(data)
                    LOG.info(data)

                    self.SAVE_COUNTER += 1

                    if self.SAVE_COUNTER >= self.SAVE_THRESHOLD:
                        self.DB.upsert_products(self.SITE_KEY, products_batch)
                        self.SAVE_COUNTER = 0
                        products_batch = []

                    time.sleep(random.uniform(0.5, 1.5)) # politeness delay

                except Exception as e:  # noqa: BLE001
                    LOG.error(f"Failed processing {product_url}: {e}")
                    continue

            # final save
            if products_batch:
                self.DB.upsert_products(self.SITE_KEY, products_batch)

            # save JSON file of unknown brand(s) for manual review
            if self.unknown_brands:
                review_path = os.path.join(BASE_DIR, "resources", "data", "brands_review.json")
                try:
                    existing_review = []
                    if os.path.exists(review_path):
                        with open(review_path, 'r', encoding='utf-8') as f:
                            try:
                                existing_review = json.load(f)
                            except json.JSONDecodeError:
                                existing_review = []

                    # merging, deduplication, and alphabetical sorting
                    combined = sorted(set(existing_review) | self.unknown_brands)

                    with open(review_path, 'w', encoding='utf-8') as f:
                        json.dump(combined, f, indent=4, ensure_ascii=False)

                    LOG.info(f"Saved {len(self.unknown_brands)} unknown brand(s) for manual review")
                except Exception as e:  # noqa: BLE001
                    LOG.error(f"Failed to save unknown brands: {e}")

            LOG.info(f"ScraperEngine completed for {self.website}")

        finally:
            self.HTTP.close()
            self.DB.close()


    def _process_product(self, page: Selector, link: str) -> ProductData | None:
        """ Extracts product data from a Scrapling page and returns a normalized dataclass. """

        data = ProductData(url=link, catalog_date=datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

        try:
            time.sleep(self.REQUEST_DELAY)

            jsonld_data = jsonld_extractor(page=page)
            scope = page.css(self.SITE_CONFIG.scope).first if self.SITE_CONFIG.scope else None
            resolved: dict[str, str | float | None] = {}

            for field_name, field_config in self.SITE_CONFIG.fields.items():
                validation = (
                    field_config.validate_rules.model_dump()
                    if field_config.validate_rules is not None
                    else None
                )
                result = resolve_field(
                    page=page,
                    jsonld=jsonld_data,
                    compiled_strategies=self.COMPILED_FIELDS[field_name],
                    validate_rules=validation,
                    scope=scope,
                )
                resolved[field_name] = result.value
                if field_config.required and result.value is None:
                    LOG.warning("Required field '%s' missing for %s; attempts=%s", field_name, link, result.attempts)
                    return None

            title = resolved.get("title")
            brand = resolved.get("brand")
            if isinstance(title, str):
                data.article_name = title

            ean = resolved.get("ean")
            if isinstance(ean, str):
                data.ean = ean

            if isinstance(brand, str) and brand:
                data.brand = brand.upper()

            mpn = resolved.get("mpn")
            if isinstance(mpn, str):
                data.mpn = self.BRANDS.clean_mpn(raw=mpn, canonical=data.brand)

            if not data.brand:
                data.brand = self.BRANDS.resolve(data.article_name)
            if data.brand and not self.BRANDS.is_known(data.brand):
                self.unknown_brands.add(data.brand)

            price = resolved.get("price")
            price_config = self.SITE_CONFIG.fields.get("price")
            if not isinstance(price, (int, float)) or price_config is None or price <= 0:
                return None

            if price_config.vat_included is True:
                data.catalog_price_vat = round(float(price), 2)
                data.catalog_price_nvat = round(float(price) / self.SITE_CONFIG.vat_rate, 2)
            elif price_config.vat_included is False:
                data.catalog_price_nvat = round(float(price), 2)
                data.catalog_price_vat = round(float(price) * self.SITE_CONFIG.vat_rate, 2)
            else:
                raise ValueError("Le champ price doit déclarer vat_included=true ou false.")

            return data

        except Exception:
            LOG.exception(f"Error during data extraction for product {link}")

        return None



# === PLAYGROUND ===
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

    # Dictionnaire regroupant tes sites et les URLs à tester
    TEST_URLS = {
        "CLABOTS": [
            "https://www.clabots.be/fr/catalogue/machines/_item/visseuse-12v-dcd703l2t-2x3ah-multi-head",
            "https://www.clabots.be/fr/perceuse-visseuse-bosch-12v-gsr-15-fc"

            # Ajoute un lien Clabots ici...
        ],
        "FIXAMI": [
            "https://www.fixami.be/fr/tronconneuse-sans-fil-makita-duc405z-36v-li-ion-2x-18v-400-mm-brushless-machine-seule.html",
            "https://www.fixami.be/fr/makita-bl1850b-10-batterie-18v-5ah.html",
            "https://www.fixami.be/fr/stealthmounts-sm-bb-mkt-support-de-batterie-pour-makita-18v-lxt-noir.html",
            "https://www.fixami.be/fr/makita-bl1830-lot-de-2-batteries-li-ion-18v-3-0-ah-2-pcs.html"

            # Ajoute d'autres liens Fixami ici...
        ],
        "LECOT": [
            "https://shop.lecot.be/fr-be/soudal-mousse-pu-a-faible-expansion-gunfoam-filetage-750-ml",
            "https://shop.lecot.be/fr-be/makita-set-de-machines-18-v-avec-7-machines-sans-charbon-3-batteries-et-coffrets"

            # Ajoute un lien Lecot ici...
        ],

        #"TOOLNATION": [
            #"https://www.toolnation.fr/festool-578521-scie-sauteuse-sans-fil-psc-e-18-eb-basic-excl-batterie-et-chargeur-en-mallette.html",
            #"https://www.toolnation.fr/makita-ddf492z-perceuse-visseuse-sans-fil-lxt-18v-sans-batteries-et-chargeur-dans-la-boite.html"

            # Ajoute un lien Toolnation ici...
        #]
    }

    print("\n🚀 Lancement des tests multi-sites...\n" + "="*50)

    data: WebsiteManager = WebsiteManager(filepath=os.path.join(BASE_DIR, "resources", "data", "websites_beta.json"))

    for site_key, urls in TEST_URLS.items():
        if not urls:  # On saute le site si tu n'as pas mis de lien à tester
            continue

        print(f"\n⚙️ INITIALISATION DU SCRAPER POUR : {site_key}")
        # On instancie le scraper avec la configuration spécifique au site
        scraper: ScraperEngine = ScraperEngine(data=data, website=site_key)
        scraper.DB.init_schema()

        site_products: list[ProductData] = []

        for url in urls:
            print(f"\n🔗 URL : {url}")

            # On lance l'extraction
            response = scraper.HTTP.get(url, timeout=10)
            page = Selector(response.body.decode(response.encoding or "utf-8"))
            resultat = scraper._process_product(page=page, link=url)

            # On affiche le JSON final
            print("-" * 30)
            print(f"📦 RÉSULTAT ({site_key}) :")
            if resultat is not None:
                site_products.append(resultat)
                print(json.dumps(asdict(resultat), indent=4, ensure_ascii=False))
            else:
                print("None")
            print("=" * 50)

        if site_products:
            scraper.DB.upsert_products(site_key, site_products)
            print(f"💾 {len(site_products)} produit(s) inséré(s) / mis à jour en base pour {site_key}.")

        scraper.HTTP.close()
        scraper.DB.close()
