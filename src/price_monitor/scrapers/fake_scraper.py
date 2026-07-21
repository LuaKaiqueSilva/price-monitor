from decimal import Decimal

from price_monitor.models import ProductData
from price_monitor.scrapers.base import BaseScraper


class FakeScraper(BaseScraper):
    """Fake scraper used during development."""

    @staticmethod
    def supports(url: str) -> bool:
        """Fake scraper accepts any URL."""
        return True

    def scrape(self, url: str) -> ProductData:
        """Return fake product data."""

        return ProductData(
            name="RTX 4060",
            price=Decimal("1999.90"),
            currency="BRL",
            store="Kabum",
            url=url,
        )
