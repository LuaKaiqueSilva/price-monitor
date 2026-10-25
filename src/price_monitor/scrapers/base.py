from abc import ABC, abstractmethod
from decimal import Decimal
from urllib.parse import urlsplit

import requests

from price_monitor.exceptions import ScraperConnectionError
from price_monitor.models import ProductData

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 "
        "(X11; Linux x86_64) "
        "AppleWebKit/537.36 "
        "(KHTML, like Gecko) "
        "Chrome/138.0 Safari/537.36"
    )
}


class BaseScraper(ABC):
    """Abstract base class for all scrapers."""

    @staticmethod
    @abstractmethod
    def supports(url: str) -> bool:
        """Return True if this scraper supports the given URL."""

    @abstractmethod
    def scrape(self, url: str) -> ProductData:
        """Extract product data from the given URL."""

    def _download_page(self, url: str) -> str:
        """Download the HTML page."""

        try:
            response = requests.get(
                url,
                headers=HEADERS,
                timeout=10,
            )

            response.raise_for_status()

            return response.text

        except requests.RequestException as error:
            raise ScraperConnectionError("Unable to connect to the store.") from error

    @staticmethod
    def _supports_domain(url: str, domain: str) -> bool:
        """Return whether an HTTP(S) URL belongs to the expected domain."""

        try:
            parsed_url = urlsplit(url)
            hostname = parsed_url.hostname
        except ValueError:
            return False

        return (
            parsed_url.scheme.lower() in {"http", "https"}
            and hostname is not None
            and (hostname.lower() == domain or hostname.lower().endswith(f".{domain}"))
        )

    def _parse_price(self, text: str) -> Decimal:
        """Convert Brazilian price text into Decimal."""

        cleaned = (
            text.replace("R$", "")
            .replace("\xa0", "")
            .replace(".", "")
            .replace(",", ".")
            .strip()
        )

        return Decimal(cleaned)
