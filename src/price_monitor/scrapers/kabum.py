from bs4 import BeautifulSoup

from price_monitor.exceptions import ProductNotFoundError
from price_monitor.models import ProductData
from price_monitor.scrapers.base import BaseScraper


class KabumScraper(BaseScraper):

    @staticmethod
    def supports(url: str) -> bool:
        return BaseScraper._supports_domain(url, "kabum.com.br")

    def scrape(self, url: str) -> ProductData:
        html = self._download_page(url)
        return self._parse_page(html, url)

    def _parse_page(self, html: str, url: str) -> ProductData:
        soup = BeautifulSoup(html, "lxml")

        title = soup.find("h1")
        name = (
            title.get_text(strip=True) if title else ""
        ) or self._fallback_product_name(soup)
        if not name:
            raise ProductNotFoundError("Product title not found.")

        price = soup.select_one("h4.text-secondary-500")
        price_text = (price.get_text() if price else "") or self._fallback_product_price(soup)
        if not price_text:
            raise ProductNotFoundError("Product price not found.")

        return ProductData(
            name=name,
            price=self._parse_product_price(price_text),
            currency="BRL",
            store="KaBuM",
            url=url,
        )
