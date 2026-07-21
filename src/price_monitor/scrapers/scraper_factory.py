from price_monitor.scrapers.base import BaseScraper
from price_monitor.scrapers.fake_scraper import FakeScraper
from price_monitor.scrapers.exceptions import UnsupportedStoreError

class ScraperFactory:
    """Factory responsible for providing the appropriate scraper."""

    @staticmethod
    def get_scraper(url: str) -> BaseScraper:
        """Return a scraper capable of handling the given URL."""

        if FakeScraper.supports(url):
            return FakeScraper()

        raise UnsupportedStoreError(
            f"No scraper available for URL: {url}"
        )
