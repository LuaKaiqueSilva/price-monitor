import unittest
from decimal import Decimal
from unittest.mock import patch

from requests import Timeout

from price_monitor.exceptions import (
    ProductNotFoundError,
    ScraperConnectionError,
    UnsupportedStoreError,
)
from price_monitor.scrapers.kabum import KabumScraper
from price_monitor.scrapers.pichau import PichauScraper
from price_monitor.scrapers.scraper_factory import ScraperFactory
from price_monitor.scrapers.terabyte import TerabyteScraper


class PriceParsingTests(unittest.TestCase):
    def setUp(self) -> None:
        self.scraper = KabumScraper()

    def test_parses_brazilian_price(self) -> None:
        self.assertEqual(self.scraper._parse_price("R$ 1.234,56"), Decimal("1234.56"))

    def test_parses_dot_decimal_price(self) -> None:
        self.assertEqual(self.scraper._parse_price("R$ 849.99"), Decimal("849.99"))

    def test_parses_comma_decimal_price(self) -> None:
        self.assertEqual(self.scraper._parse_price("R$ 849,99"), Decimal("849.99"))

    def test_parses_repeated_thousands_separators(self) -> None:
        self.assertEqual(self.scraper._parse_price("1.234.567"), Decimal(1_234_567))

    def test_rejects_text_without_a_number(self) -> None:
        with self.assertRaises(ValueError):
            self.scraper._parse_price("Preço indisponível")


class StoreSelectionTests(unittest.TestCase):
    def test_accepts_each_supported_store(self) -> None:
        urls_and_types = (
            ("https://www.kabum.com.br/produto/123", KabumScraper),
            ("https://www.terabyteshop.com.br/produto/123", TerabyteScraper),
        )

        for url, scraper_type in urls_and_types:
            with self.subTest(url=url):
                self.assertIsInstance(ScraperFactory.get_scraper(url), scraper_type)

    def test_rejects_a_supported_domain_in_a_query_string(self) -> None:
        with self.assertRaises(UnsupportedStoreError):
            ScraperFactory.get_scraper("https://example.com/?next=kabum.com.br")

    def test_rejects_a_lookalike_domain(self) -> None:
        with self.assertRaises(UnsupportedStoreError):
            ScraperFactory.get_scraper("https://kabum.com.br.example.org/produto/123")

    def test_rejects_non_http_schemes(self) -> None:
        with self.assertRaises(UnsupportedStoreError):
            ScraperFactory.get_scraper("file://kabum.com.br/produto/123")

    def test_pichau_is_not_enabled_without_verified_live_fetching(self) -> None:
        with self.assertRaises(UnsupportedStoreError):
            ScraperFactory.get_scraper("https://www.pichau.com.br/produto/123")


class StoreParserTests(unittest.TestCase):
    def test_request_failure_logs_store_host_without_product_path(self) -> None:
        url = "https://www.kabum.com.br/produto/private-id"

        with patch(
            "price_monitor.scrapers.base.requests.get",
            side_effect=Timeout("request timed out"),
        ), self.assertLogs("price_monitor.scrapers.base", level="WARNING") as log:
            with self.assertRaises(ScraperConnectionError):
                KabumScraper()._download_page(url)

        self.assertIn("kabum.com.br", log.output[0])
        self.assertNotIn("private-id", log.output[0])

    def test_parses_kabum_sample_html(self) -> None:
        product = KabumScraper()._parse_page(
            "<h1>Teclado de exemplo</h1><h4 class='text-secondary-500'>R$ 199,90</h4>",
            "https://www.kabum.com.br/produto/123",
        )

        self.assertEqual(product.name, "Teclado de exemplo")
        self.assertEqual(product.price, Decimal("199.90"))

    def test_parses_pichau_sample_html(self) -> None:
        scraper = PichauScraper()
        html = """
            <html><body>
              <h1>Processador de exemplo</h1>
              <div class="price_vista">R$ 849,99 no PIX</div>
            </body></html>
        """

        product = scraper._parse_page(html, "https://www.pichau.com.br/produto/123")

        self.assertEqual(product.name, "Processador de exemplo")
        self.assertEqual(product.price, Decimal("849.99"))
        self.assertEqual(product.store, "Pichau")

    def test_parses_terabyte_sample_html(self) -> None:
        product = TerabyteScraper()._parse_page(
            "<h1 class='tit-prod'>Mouse de exemplo</h1>"
            "<p id='valVista'>R$ 89,90</p>",
            "https://www.terabyteshop.com.br/produto/123",
        )

        self.assertEqual(product.name, "Mouse de exemplo")
        self.assertEqual(product.price, Decimal("89.90"))

    def test_terabyte_missing_product_title_is_reported(self) -> None:
        with self.assertRaisesRegex(ProductNotFoundError, "Product title not found"):
            TerabyteScraper()._parse_page(
                "<html><body><p id='valVista'>R$ 10,00</p></body></html>",
                "https://www.terabyteshop.com.br/produto/123",
            )


if __name__ == "__main__":
    unittest.main()
