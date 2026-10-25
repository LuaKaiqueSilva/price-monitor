import sqlite3
import unittest
from decimal import Decimal
from unittest.mock import patch

from price_monitor.database.repositories.price_history_repository import (
    PriceHistoryRepository,
)
from price_monitor.database.repositories.product_repository import ProductRepository
from price_monitor.database.schema import initialize_database
from price_monitor.models import ProductData
from price_monitor.services.product_service import ProductService


class FakeScraper:
    def __init__(self, data: ProductData) -> None:
        self.data = data

    def scrape(self, url: str) -> ProductData:
        return self.data


def product_data(price: str) -> ProductData:
    return ProductData(
        name="Example product",
        price=Decimal(price),
        currency="BRL",
        store="KaBuM",
        url="https://www.kabum.com.br/produto/123",
    )


class ProductServiceTests(unittest.TestCase):
    def setUp(self) -> None:
        self.connection = sqlite3.connect(":memory:")
        self.connection.row_factory = sqlite3.Row
        self.connection.execute("PRAGMA foreign_keys = ON")
        initialize_database(self.connection)

        self.products = ProductRepository(self.connection)
        self.history = PriceHistoryRepository(self.connection)
        self.service = ProductService(self.products, self.history)

    def tearDown(self) -> None:
        self.connection.close()

    def add_product(self):
        with patch(
            "price_monitor.services.product_service.ScraperFactory.get_scraper",
            return_value=FakeScraper(product_data("849.99")),
        ):
            return self.service.add_product("https://www.kabum.com.br/produto/123")

    def test_add_product_records_its_initial_price(self) -> None:
        product = self.add_product()

        self.assertIsNotNone(product.id)
        records = self.service.get_price_history(product.id)
        self.assertEqual(len(records), 1)
        self.assertEqual(records[0].price, Decimal("849.99"))

    def test_update_records_history_when_price_changes(self) -> None:
        product = self.add_product()
        with patch(
            "price_monitor.services.product_service.ScraperFactory.get_scraper",
            return_value=FakeScraper(product_data("799.99")),
        ):
            updated = self.service.update_product(product.id)

        self.assertEqual(updated.current_price, Decimal("799.99"))
        self.assertEqual(
            [record.price for record in self.service.get_price_history(product.id)],
            [Decimal("799.99"), Decimal("849.99")],
        )

    def test_update_does_not_duplicate_history_when_price_is_unchanged(self) -> None:
        product = self.add_product()
        with patch(
            "price_monitor.services.product_service.ScraperFactory.get_scraper",
            return_value=FakeScraper(product_data("849.99")),
        ):
            self.service.update_product(product.id)

        self.assertEqual(len(self.service.get_price_history(product.id)), 1)

    def test_remove_product_also_removes_price_history(self) -> None:
        product = self.add_product()

        self.assertTrue(self.service.remove_product(product.id))
        self.assertEqual(self.service.get_price_history(product.id), [])

    def test_update_all_logs_a_failed_product_and_continues(self) -> None:
        self.add_product()
        with patch(
            "price_monitor.services.product_service.ScraperFactory.get_scraper",
            return_value=FakeScraperError(),
        ), self.assertLogs(
            "price_monitor.services.product_service", level="ERROR"
        ) as captured:
            errors = self.service.update_all_products()

        self.assertEqual(errors, [("Example product", "Store is unavailable")])
        self.assertIn("Product update failed", captured.output[0])


class FakeScraperError:
    def scrape(self, url: str) -> ProductData:
        raise RuntimeError("Store is unavailable")


if __name__ == "__main__":
    unittest.main()
