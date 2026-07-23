from price_monitor.scrapers.base import BaseScraper
from price_monitor.scrapers.fake_scraper import FakeScraper
from price_monitor.scrapers.exceptions import UnsupportedStoreError
from price_monitor.scrapers.kabum import KabumScraper


class ScraperFactory:
    """Factory responsible for providing the appropriate scraper."""

    @staticmethod
    def get_scraper(url: str) -> BaseScraper:
        """Return a scraper capable of handling the given URL."""

        if KabumScraper.supports(url):
            return KabumScraper()

        if FakeScraper.supports(url):
            return FakeScraper()

        raise UnsupportedStoreError(
            f"No scraper available for URL: {url}"
        )
