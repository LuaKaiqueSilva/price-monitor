from dataclasses import dataclass
from decimal import Decimal


@dataclass(slots=True)
class ProductData:
    """Represents the data extracted by a scraper."""

    name: str
    price: Decimal
    currency: str
    store: str
    url: str
