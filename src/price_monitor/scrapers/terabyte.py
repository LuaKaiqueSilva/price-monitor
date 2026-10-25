from bs4 import BeautifulSoup

from price_monitor.exceptions import ProductNotFoundError
from price_monitor.models import ProductData
from price_monitor.scrapers.base import BaseScraper


class TerabyteScraper(BaseScraper):
    """Scraper for TerabyteShop."""

    @staticmethod
    def supports(url: str) -> bool:
        return BaseScraper._supports_domain(url, "terabyteshop.com.br")

    def scrape(self, url: str) -> ProductData:
        html = self._download_page(url)
        return self._parse_page(html, url)

    def _parse_page(self, html: str, url: str) -> ProductData:
        soup = BeautifulSoup(html, "lxml")

        title = soup.find("h1", class_="tit-prod")
        name = title.get_text(strip=True) if title else self._fallback_product_name(soup)
        if not name:
            raise ProductNotFoundError("Product title not found.")

        price = soup.find("p", id="valVista")
        price_text = price.get_text() if price else self._fallback_product_price(soup)
        if not price_text:
            raise ProductNotFoundError("Product price not found.")

        return ProductData(
            name=name,
            price=self._parse_price(price_text),
            currency="BRL",
            store="Terabyte",
            url=url,
        )
