import json
import logging
import re
from abc import ABC, abstractmethod
from decimal import Decimal
from urllib.parse import urlsplit

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

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
RETRY_POLICY = Retry(
    total=2,
    connect=2,
    read=2,
    status=2,
    backoff_factor=0.25,
    status_forcelist=(429, 500, 502, 503, 504),
    allowed_methods=frozenset({"GET"}),
    raise_on_status=False,
)


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
            with requests.Session() as session:
                adapter = HTTPAdapter(max_retries=RETRY_POLICY)
                session.mount("http://", adapter)
                session.mount("https://", adapter)
                response = session.get(
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
            if error.response is not None and error.response.status_code == 403:
                message = "The store denied access to this page (HTTP 403)."
            else:
                message = "Unable to connect to the store."
            raise ScraperConnectionError(message) from error

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

    @staticmethod
    def _json_ld_products(soup) -> list[dict]:
        """Return Product objects found in schema.org JSON-LD scripts."""

        products: list[dict] = []

        def visit(value) -> None:
            if isinstance(value, list):
                for item in value:
                    visit(item)
            elif isinstance(value, dict):
                product_type = value.get("@type", [])
                if isinstance(product_type, str):
                    product_type = [product_type]
                if "Product" in product_type:
                    products.append(value)
                for key in ("@graph", "mainEntity", "itemListElement"):
                    if key in value:
                        visit(value[key])

        for script in soup.select('script[type="application/ld+json"]'):
            try:
                visit(json.loads(script.string or script.get_text()))
            except (json.JSONDecodeError, TypeError):
                continue
        return products

    def _fallback_product_name(self, soup) -> str | None:
        """Read a product name from metadata or structured data."""

        for selector, attribute in (
            ('meta[property="og:title"]', "content"),
            ('meta[itemprop="name"]', "content"),
        ):
            tag = soup.select_one(selector)
            if tag and tag.get(attribute):
                return tag[attribute].strip()

        for product in self._json_ld_products(soup):
            name = product.get("name")
            if isinstance(name, str) and name.strip():
                return name.strip()
        return None

    def _fallback_product_price(self, soup) -> str | None:
        """Read a price from common metadata or a Product's JSON-LD offers."""

        for selector, attribute in (
            ('meta[property="product:price:amount"]', "content"),
            ('meta[itemprop="price"]', "content"),
            ('meta[property="og:price:amount"]', "content"),
        ):
            tag = soup.select_one(selector)
            if tag and tag.get(attribute):
                return tag[attribute].strip()

        def offer_price(offers) -> str | None:
            if isinstance(offers, dict):
                price = offers.get("price") or offers.get("lowPrice")
                if price is not None:
                    return str(price)
                return offer_price(offers.get("offers"))
            if isinstance(offers, list):
                for offer in offers:
                    price = offer_price(offer)
                    if price is not None:
                        return price
            return None

        for product in self._json_ld_products(soup):
            price = offer_price(product.get("offers"))
            if price:
                return price
        return None
