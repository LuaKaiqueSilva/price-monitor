from bs4 import BeautifulSoup

from price_monitor.exceptions import ProductNotFoundError, ScraperConnectionError
from price_monitor.models import ProductData
from price_monitor.scrapers.base import BaseScraper


class PichauScraper(BaseScraper):

    @staticmethod
    def supports(url: str) -> bool:
        return BaseScraper._supports_domain(url, "pichau.com.br")

    def scrape(self, url: str) -> ProductData:
        html = self._download_in_browser(url)
        return self._parse_page(html, url)

    def _download_in_browser(self, url: str) -> str:
        """Render the public product page because Pichau rejects plain HTTP clients."""

        try:
            from playwright.sync_api import sync_playwright
        except ImportError as error:
            raise ScraperConnectionError(
                "Pichau needs the optional browser scraper. Install with "
                "`python -m pip install -e '.[pichau]'` and run "
                "`python -m playwright install chromium`."
            ) from error

        try:
            with sync_playwright() as playwright:
                # Pichau serves the product page in a regular browser, but
                # rejects Chromium's headless request with HTTP 403.
                browser = playwright.chromium.launch(headless=False)
                try:
                    page = browser.new_page(locale="pt-BR")
                    response = page.goto(
                        url,
                        wait_until="domcontentloaded",
                        timeout=30_000,
                    )
                    if response is not None and response.status == 403:
                        raise ScraperConnectionError(
                            "Pichau denied access to this product page (HTTP 403)."
                        )
                    page.locator('script[type="application/ld+json"]').first.wait_for(
                        state="attached",
                        timeout=15_000,
                    )
                    return page.content()
                finally:
                    browser.close()
        except ScraperConnectionError:
            raise
        except Exception as error:
            raise ScraperConnectionError(
                "Unable to load the Pichau product page in Chromium."
            ) from error

    def _parse_page(self, html: str, url: str) -> ProductData:
        soup = BeautifulSoup(html, "lxml")

        title = soup.find("h1")
        name = (title.get_text(strip=True) if title else "") or self._fallback_product_name(
            soup
        )
        if not name:
            raise ProductNotFoundError("Product title not found.")

        price_candidates = soup.select(
            'div[class*="extraSpacePriceVista"], div[class*="price_vista"]'
        )
        price_text = next(
            (
                candidate.get_text(" ", strip=True)
                for candidate in price_candidates
                if any(character.isdigit() for character in candidate.get_text())
            ),
            None,
        ) or self._fallback_product_price(soup)
        if not price_text:
            raise ProductNotFoundError("Product price not found.")

        return ProductData(
            name=name,
            price=self._parse_product_price(price_text),
            currency="BRL",
            store="Pichau",
            url=url,
        )
