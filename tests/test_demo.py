import unittest
from datetime import datetime
from decimal import Decimal

from price_monitor.demo import build_demo_data


class DemoDataTests(unittest.TestCase):
    def test_demo_products_have_matching_histories(self) -> None:
        now = datetime(2026, 10, 25, 12, 0)

        products, histories = build_demo_data(now)

        self.assertEqual(len(products), 3)
        self.assertEqual(set(histories), {product.id for product in products})
        for product in products:
            self.assertLess(product.id, 0)
            self.assertEqual(
                product.current_price,
                histories[product.id][-1].price,
            )
            self.assertEqual(len(histories[product.id]), 4)

        self.assertEqual(products[0].current_price, Decimal("849.99"))


if __name__ == "__main__":
    unittest.main()
