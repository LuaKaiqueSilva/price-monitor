from price_monitor.exceptions import UnsupportedStoreError
from price_monitor.scrapers.base import BaseScraper
from price_monitor.scrapers.kabum import KabumScraper
from price_monitor.scrapers.pichau import PichauScraper
from price_monitor.scrapers.terabyte import TerabyteScraper

SCRAPERS = (
    KabumScraper,
    TerabyteScraper,
    PichauScraper,
)


class ScraperFactory:
    """Factory responsible for providing the appropriate scraper."""

    @staticmethod
    def get_scraper(url: str) -> BaseScraper:
        """Return a scraper capable of handling the given URL."""

        for scraper in SCRAPERS:
            if scraper.supports(url):
                return scraper()

        raise UnsupportedStoreError(f"No scraper available for URL: {url}")
