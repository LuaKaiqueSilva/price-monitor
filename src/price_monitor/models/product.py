from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal


@dataclass(slots=True)
class Product:
    """Represents a monitored product."""

    id: int | None
    name: str
    url: str
    current_price: Decimal
    currency: str
    store: str
    created_at: datetime
