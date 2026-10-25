import unittest
from decimal import Decimal
from unittest.mock import MagicMock, patch

import requests
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
            ("https://www.pichau.com.br/produto/123", PichauScraper),
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

class StoreParserTests(unittest.TestCase):
    def test_request_failure_logs_store_host_without_product_path(self) -> None:
        url = "https://www.kabum.com.br/produto/private-id"
        session = MagicMock()
        session.__enter__.return_value = session
        session.get.side_effect = Timeout("request timed out")

        with (
            patch(
                "price_monitor.scrapers.base.requests.Session",
                return_value=session,
            ),
            self.assertLogs("price_monitor.scrapers.base", level="WARNING") as log,
            self.assertRaises(ScraperConnectionError),
        ):
            KabumScraper()._download_page(url)

        self.assertIn("kabum.com.br", log.output[0])
        self.assertNotIn("private-id", log.output[0])
        self.assertEqual(session.get.call_count, 1)
        self.assertEqual(session.mount.call_count, 2)
        for call in session.mount.call_args_list:
            adapter = call.args[1]
            self.assertEqual(adapter.max_retries.total, 2)
            self.assertIn(429, adapter.max_retries.status_forcelist)

    def test_http_403_has_a_clear_user_facing_error(self) -> None:
        response = MagicMock(status_code=403)
        response.raise_for_status.side_effect = requests.HTTPError(
            "forbidden", response=response
        )
        session = MagicMock()
        session.__enter__.return_value = session
        session.get.return_value = response

        with (
            patch(
                "price_monitor.scrapers.base.requests.Session",
                return_value=session,
            ),
            self.assertLogs("price_monitor.scrapers.base", level="WARNING"),
            self.assertRaisesRegex(ScraperConnectionError, "HTTP 403"),
        ):
            KabumScraper()._download_page("https://www.kabum.com.br/produto/123")

    def test_parses_kabum_sample_html(self) -> None:
        product = KabumScraper()._parse_page(
            "<h1>Teclado de exemplo</h1><h4 class='text-secondary-500'>R$ 199,90</h4>",
            "https://www.kabum.com.br/produto/123",
        )

        self.assertEqual(product.name, "Teclado de exemplo")
        self.assertEqual(product.price, Decimal("199.90"))

    def test_kabum_uses_json_ld_when_visible_selectors_change(self) -> None:
        html = '''
            <script type="application/ld+json">
            {"@context":"https://schema.org","@graph":[
              {"@type":"Product","name":"SSD estruturado",
               "offers":{"@type":"Offer","price":"349.90"}}
            ]}
            </script>
        '''

        product = KabumScraper()._parse_page(
            html, "https://www.kabum.com.br/produto/123"
        )

        self.assertEqual(product.name, "SSD estruturado")
        self.assertEqual(product.price, Decimal("349.90"))

    def test_terabyte_uses_price_metadata_and_product_name_metadata(self) -> None:
        html = '''
            <meta property="og:title" content="Monitor por metadados">
            <meta property="product:price:amount" content="1.299,90">
        '''

        product = TerabyteScraper()._parse_page(
            html, "https://www.terabyteshop.com.br/produto/123"
        )

        self.assertEqual(product.name, "Monitor por metadados")
        self.assertEqual(product.price, Decimal("1299.90"))

    def test_ignores_malformed_json_ld_and_reports_missing_product(self) -> None:
        html = '<script type="application/ld+json">{invalid}</script>'
        with self.assertRaises(ProductNotFoundError):
            KabumScraper()._parse_page(html, "https://www.kabum.com.br/produto/123")

    def test_empty_store_selectors_fall_back_to_json_ld(self) -> None:
        html = '''
            <h1></h1><h4 class="text-secondary-500"></h4>
            <script type="application/ld+json">
            {"@type":"Product","name":"Produto reserva",
             "offers":{"price":"12.50"}}
            </script>
        '''

        product = KabumScraper()._parse_page(
            html, "https://www.kabum.com.br/produto/123"
        )

        self.assertEqual(product.name, "Produto reserva")
        self.assertEqual(product.price, Decimal("12.50"))

    def test_invalid_or_zero_store_price_uses_a_product_error(self) -> None:
        for price in ("indisponível", "0"):
            with self.subTest(price=price), self.assertRaisesRegex(
                ProductNotFoundError, "Product price"
            ):
                KabumScraper()._parse_page(
                    f'<h1>Produto</h1><h4 class="text-secondary-500">{price}</h4>',
                    "https://www.kabum.com.br/produto/123",
                )

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

    def test_parses_pichau_current_price_selector(self) -> None:
        html = '''
            <h1>Placa de vídeo de exemplo</h1>
            <span class="mui-whrtxo-price_vista_text-smallFontsPricePix">à vista</span>
            <div class="mui-1jk88bq-price_vista-extraSpacePriceVista">
              R$ 239,99
            </div>
            <span class="mui-1vuxjsq-price_vista_additional-smallFontsPricePix">
              no PIX com 15% desconto
            </span>
            <div class="mui-7ie9un-price_total">R$ 282,34</div>
        '''

        product = PichauScraper()._parse_page(
            html, "https://www.pichau.com.br/placa-de-video-exemplo"
        )

        self.assertEqual(product.price, Decimal("239.99"))

    def test_pichau_uses_real_product_metadata_when_markup_changes(self) -> None:
        html = '''
            <meta name="product:price:amount" content="R$ 239.99">
            <script type="application/ld+json">
            {"@type":"Product","name":"Placa Pichau",
             "offers":{"priceCurrency":"BRL","price":"282.34"}}
            </script>
        '''

        product = PichauScraper()._parse_page(
            html, "https://www.pichau.com.br/placa-de-video-exemplo"
        )

        self.assertEqual(product.name, "Placa Pichau")
        self.assertEqual(product.price, Decimal("239.99"))

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
