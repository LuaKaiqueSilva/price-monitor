from bs4 import BeautifulSoup

from price_monitor.exceptions import ProductNotFoundError
from price_monitor.models import ProductData
from price_monitor.scrapers.base import BaseScraper


class PichauScraper(BaseScraper):

    @staticmethod
    def supports(url: str) -> bool:
        return BaseScraper._supports_domain(url, "pichau.com.br")

    def scrape(self, url: str) -> ProductData:
        html = self._download_page(url)
        return self._parse_page(html, url)

    def _parse_page(self, html: str, url: str) -> ProductData:
        soup = BeautifulSoup(html, "lxml")

        title = soup.find("h1")

        if title is None:
            raise ProductNotFoundError("Product title not found.")

        price = soup.find(
            "div",
            class_=lambda c: c and "price_vista" in c,
        )

        if price is None:
            raise ProductNotFoundError("Product price not found.")

        return ProductData(
            name=title.get_text(strip=True),
            price=self._parse_price(price.get_text()),
            currency="BRL",
            store="Pichau",
            url=url,
        )
