"""In-memory sample products for previewing the dashboard without scraping."""

from datetime import datetime, timedelta
from decimal import Decimal

from price_monitor.models import PriceRecord, Product


def build_demo_data(
    now: datetime | None = None,
) -> tuple[list[Product], dict[int, list[PriceRecord]]]:
    """Return sample products and histories without writing to the database."""

    now = now or datetime.now()
    samples = (
        (
            "AMD Ryzen 5 5600",
            "KaBuM",
            ("999.90", "949.90", "899.90", "849.99"),
        ),
        (
            "SSD NVMe 1 TB",
            "Terabyte",
            ("459.90", "429.90", "399.90", "419.90"),
        ),
        (
            "Monitor Gamer 24\"",
            "KaBuM",
            ("899.90", "899.90", "849.90", "819.90"),
        ),
    )

    products: list[Product] = []
    histories: dict[int, list[PriceRecord]] = {}

    for product_index, (name, store, prices) in enumerate(samples, start=1):
        product_id = -product_index
        recorded_prices = [
            PriceRecord(
                id=None,
                product_id=product_id,
                price=Decimal(price),
                recorded_at=now - timedelta(days=(len(prices) - index - 1) * 7),
            )
            for index, price in enumerate(prices)
        ]
        histories[product_id] = recorded_prices
        products.append(
            Product(
                id=product_id,
                name=name,
                url="",
                current_price=recorded_prices[-1].price,
                currency="BRL",
                store=store,
                created_at=now - timedelta(days=30),
                last_updated=now - timedelta(minutes=10),
            )
        )

    return products, histories
