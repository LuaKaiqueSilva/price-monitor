from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal


@dataclass(slots=True)
class PriceRecord:
    """Represents a historical price record for a product."""

    id: int | None
    product_id: int
    price: Decimal
    recorded_at: datetime
