from datetime import datetime
from decimal import Decimal
from sqlite3 import Connection, Row

from price_monitor.models import PriceRecord


class PriceHistoryRepository:
    """Repository responsible for price history operations."""

    def __init__(self, connection: Connection) -> None:
        self._connection = connection

    def save(self, record: PriceRecord) -> PriceRecord:
        """Persist a price record."""

        cursor = self._connection.cursor()

        cursor.execute(
            """
            INSERT INTO price_history (
            product_id,
            price,
            recorded_at
            )
            VALUES (?, ?, ?)
             """,
            (
                record.product_id,
                str(record.price),
                record.recorded_at.isoformat(),
            ),
        )

        self._connection.commit()

        return PriceRecord(
            id=cursor.lastrowid,
            product_id=record.product_id,
            price=record.price,
            recorded_at=record.recorded_at,
        )

    def get_by_product(self, product_id: int) -> list[PriceRecord]:
        """Return all price records for a product."""

        cursor = self._connection.cursor()

        cursor.execute(
            """
            SELECT *
            FROM price_history
            WHERE product_id = ?
            ORDER BY recorded_at DESC
            """,
            (product_id,),
        )

        rows = cursor.fetchall()

        return [self._row_to_price_record(row) for row in rows]

    def _row_to_price_record(self, row: Row) -> PriceRecord:
        """Convert a database row into a PriceRecord."""

        return PriceRecord(
            id=row["id"],
            product_id=row["product_id"],
            price=Decimal(row["price"]),
            recorded_at=datetime.fromisoformat(row["recorded_at"]),
        )

    def delete_by_product(self, product_id: int) -> None:
        """Delete all price history of a product."""

        cursor = self._connection.cursor()

        cursor.execute(
            """
            DELETE FROM price_history
            WHERE product_id = ?
            """,
            (product_id,),
        )

        self._connection.commit()
