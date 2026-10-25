import csv
from io import StringIO

from price_monitor.models import PriceRecord, Product


def build_price_history_csv(product: Product, history: list[PriceRecord]) -> bytes:
    """Build an Excel-friendly CSV containing one product's price history."""

    output = StringIO(newline="")
    writer = csv.writer(output)
    writer.writerow(
        ("product", "store", "url", "date", "price", "currency")
    )
    for record in sorted(history, key=lambda item: item.recorded_at):
        writer.writerow(
            (
                product.name,
                product.store,
                product.url,
                record.recorded_at.isoformat(sep=" "),
                str(record.price),
                product.currency,
            )
        )
    return output.getvalue().encode("utf-8-sig")
