import logging
import re
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

logger = logging.getLogger(__name__)


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
            try:
                host = urlsplit(url).hostname or "unknown host"
            except ValueError:
                host = "invalid URL"
            logger.warning("Request to %s failed (%s)", host, type(error).__name__)
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
        """Convert common Brazilian and international price formats to Decimal."""

        cleaned = re.sub(r"[^\d,.]", "", text)
        if not cleaned:
            raise ValueError(f"Price contains no digits: {text!r}")

        last_separator = max(cleaned.rfind("."), cleaned.rfind(","))
        if last_separator == -1:
            return Decimal(cleaned)

        integer_part = re.sub(r"[.,]", "", cleaned[:last_separator])
        fractional_part = cleaned[last_separator + 1 :]
        separators = [character for character in cleaned if character in ".,"]
        groups = re.split(r"[.,]", cleaned)

        # Three trailing digits indicate a thousands group (for example 1.234).
        if len(fractional_part) == 3 and (
            len(separators) == 1
            or (
                len(set(separators)) == 1
                and all(len(group) == 3 for group in groups[1:])
            )
        ):
            return Decimal("".join(groups))

        if not fractional_part:
            raise ValueError(f"Price has no digits after its separator: {text!r}")

        return Decimal(f"{integer_part}.{fractional_part}")
