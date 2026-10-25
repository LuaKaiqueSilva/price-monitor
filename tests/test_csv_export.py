import csv
import unittest
from datetime import UTC, datetime
from decimal import Decimal
from io import StringIO

from price_monitor.models import PriceRecord, Product
from price_monitor.utils.csv_export import build_price_history_csv


class PriceHistoryCsvTests(unittest.TestCase):
    def test_exports_sorted_exact_prices_and_product_details(self) -> None:
        product = Product(
            id=8,
            name='SSD, "rápido"',
            url="https://www.kabum.com.br/produto/8",
            current_price=Decimal("299.90"),
            currency="BRL",
            store="KaBuM",
            created_at=datetime(2026, 1, 1, 12, 0, tzinfo=UTC),
            last_updated=None,
        )
        history = [
            PriceRecord(
                2, 8, Decimal("299.90"), datetime(2026, 2, 2, 10, 0, tzinfo=UTC)
            ),
            PriceRecord(
                1, 8, Decimal("349.90"), datetime(2026, 2, 1, 10, 0, tzinfo=UTC)
            ),
        ]

        content = build_price_history_csv(product, history)

        self.assertTrue(content.startswith(b"\xef\xbb\xbf"))
        rows = list(csv.DictReader(StringIO(content.decode("utf-8-sig"))))
        self.assertEqual(len(rows), 2)
        self.assertEqual(rows[0]["product"], 'SSD, "rápido"')
        self.assertEqual(rows[0]["date"], "2026-02-01 10:00:00+00:00")
        self.assertEqual(rows[0]["price"], "349.90")
        self.assertEqual(rows[0]["store"], "KaBuM")
        self.assertEqual(rows[0]["currency"], "BRL")
        self.assertEqual(rows[1]["price"], "299.90")

    def test_empty_history_exports_a_header_only_file(self) -> None:
        product = Product(
            id=1,
            name="Mouse",
            url="https://www.kabum.com.br/produto/1",
            current_price=Decimal("10.00"),
            currency="BRL",
            store="KaBuM",
            created_at=datetime(2026, 1, 1, tzinfo=UTC),
            last_updated=None,
        )

        content = build_price_history_csv(product, [])

        self.assertEqual(
            list(csv.reader(StringIO(content.decode("utf-8-sig")))),
            [["product", "store", "url", "date", "price", "currency"]],
        )


if __name__ == "__main__":
    unittest.main()
