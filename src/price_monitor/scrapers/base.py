from abc import ABC, abstractmethod

from price_monitor.models import ProductData


class BaseScraper(ABC):
    """Abstract base class for all scrapers."""

    @staticmethod
    @abstractmethod
    def supports(url: str) -> bool:
        """Return True if this scraper supports the given URL."""

    @abstractmethod
    def scrape(self, url: str) -> ProductData:
        """Extract product data from the given URL."""
