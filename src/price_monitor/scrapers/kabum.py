from price_monitor.models import ProductData
from price_monitor.scrapers.base import BaseScraper 
from bs4 import BeautifulSoup
from decimal import Decimal

import requests

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 "
        "(X11; Linux x86_64) "
        "AppleWebKit/537.36 "
        "(KHTML, like Gecko) "
        "Chrome/138.0 Safari/537.36"
    )
}

class KabumScraper(BaseScraper):
     
    @staticmethod
    def supports(url: str) -> bool:
        """Return True if the URL belongs to KaBuM."""
        return "kabum.com.br" in url.lower()


    def scrape(self, url: str) -> ProductData:
        html = self._download_page(url)

        return self._parse_page(html, url)

    def _download_page(self, url: str) -> str:
        response = requests.get(
                url,
                headers=HEADERS,
                timeout=10,
        )

        response.raise_for_status()

        return response.text
   

    def _parse_page(self, html: str, url: str) -> ProductData:
        soup = BeautifulSoup(html, "lxml")

        title = soup.find("h1")

        if title is None:
            raise ValueError("Product title not found.")

        price = soup.select_one("h4.text-secondary-500")

        if price is None:
            raise ValueError("Product price not found.")

        return ProductData(
            name=title.get_text(strip=True),
            price=self._parse_price(price.get_text()),
            currency="BRL",         
            store="KaBuM",
            url=url,
        )

    def _parse_price(self, text: str) -> Decimal:
        cleaned = (
            text.replace("R$", "")
            .replace("\xa0", "")
            .replace(".", "")
            .replace(",", ".")
            .strip()
        )

        return Decimal(cleaned)
