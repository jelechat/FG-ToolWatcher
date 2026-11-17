import argparse
import logging
import os
from concurrent.futures import ProcessPoolExecutor, as_completed

from database.scraper import ScraperEngine
from database.sitemaps import SitemapEngine
from database.utils.web_manager import WebsiteManager

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITES = ["clabots", "fixami", "klium", "lecot", "toolnation"]

FORMAT = "%(asctime)s [%(processName)s] %(message)s"


def _data() -> WebsiteManager:
    return WebsiteManager(os.path.join(BASE_DIR, "resources", "data", "websites_beta.json"))


def run_sitemap(site: str, level: int) -> None:
    logging.basicConfig(level=level, format=FORMAT, datefmt="%H:%M:%S")
    SitemapEngine(data=_data(), website=site).run()


def run_loader(site: str, level: int) -> None:
    logging.basicConfig(level=level, format=FORMAT, datefmt="%H:%M:%S")
    ScraperEngine(data=_data(), website=site).run()


def run_phase(worker, sites: list[str], level: int, label: str) -> None:
    with ProcessPoolExecutor(max_workers=len(sites)) as executor:
        futures = {executor.submit(worker, site, level): site for site in sites}
        for future in as_completed(futures):
            site = futures[future]
            try:
                future.result()
                logging.info(f"[{site}] {label} terminé")
            except Exception:
                logging.exception(f"[{site}] {label} échoué")


def main() -> None:
    parser = argparse.ArgumentParser(description="FG-ToolWatcher — pipeline")
    parser.add_argument("--site", help="un seul site (ex: FIXAMI)")
    parser.add_argument("--sitemap", action="store_true", help="fetch les sitemaps")
    parser.add_argument("--loader", action="store_true", help="scrape les produits")
    parser.add_argument("--debug", action="store_true")
    args = parser.parse_args()

    level = logging.DEBUG if args.debug else logging.INFO
    sites = [args.site.lower()] if args.site else SITES

    # par défaut : cycle complet (sitemap puis loader)
    do_sitemap = args.sitemap or not (args.sitemap or args.loader)
    do_loader = args.loader or not (args.sitemap or args.loader)

    if do_sitemap:
        run_phase(run_sitemap, sites, level, "sitemap")
    if do_loader:
        run_phase(run_loader, sites, level, "loader")


if __name__ == "__main__":
    main()
