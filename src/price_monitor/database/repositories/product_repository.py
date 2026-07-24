from dataclasses import replace
from datetime import datetime
from decimal import Decimal
from sqlite3 import Connection, IntegrityError, Row

from price_monitor.exceptions import DuplicateProductError
from price_monitor.models import Product


class ProductRepository:
    """Repository responsible for Product persistence."""

    def __init__(self, connection: Connection) -> None:
        self._connection = connection

    def _row_to_product(self, row: Row) -> Product:
        """Convert a SQLite row into a Product."""

        return Product(
            id=row["id"],
            name=row["name"],
            url=row["url"],
            current_price=Decimal(row["current_price"]),
            currency=row["currency"],
            store=row["store"],
            created_at=datetime.fromisoformat(row["created_at"]),
        )

    def get_by_id(self, product_id: int) -> Product | None:
        """Return a product by its ID."""

        cursor = self._connection.cursor()

        cursor.execute(
            """
         SELECT *
         FROM products
         WHERE id = ?
         """,
            (product_id,),
        )

        row = cursor.fetchone()

        if row is None:
            return None

        return self._row_to_product(row)

    def save(self, product: Product) -> Product:
        """Persist a product and return it with its generated ID."""

        cursor = self._connection.cursor()
        try:
            cursor.execute(
                """
                INSERT INTO products (
                name,
                url,
                current_price,
                currency,
                store,
                created_at
                )
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    product.name,
                    product.url,
                    str(product.current_price),
                    product.currency,
                    product.store,
                    product.created_at.isoformat(),
                ),
            )

            self._connection.commit()

        except IntegrityError as error:
            raise DuplicateProductError(
                "⚠️ Este produto já está sendo monitorado."
            ) from error

        return replace(
            product,
            id=cursor.lastrowid,
        )

    def get_all(self) -> list[Product]:
        """Return all products."""

        cursor = self._connection.cursor()

        cursor.execute("""
         SELECT *
         FROM products
         ORDER BY id
         """)

        rows = cursor.fetchall()

        return [self._row_to_product(row) for row in rows]

    def delete(self, product_id: int) -> bool:
        """Delete a product by its ID."""

        cursor = self._connection.cursor()

        cursor.execute(
            """
          DELETE FROM products
          WHERE id = ?
          """,
            (product_id,),
        )

        self._connection.commit()

        return cursor.rowcount > 0

    def update(self, product: Product) -> Product:
        """Update an existing product."""

        cursor = self._connection.cursor()

        cursor.execute(
            """
            UPDATE products
            SET name = ?,
            url = ?,
            current_price = ?,
            currency = ?,
            store = ?
            WHERE id = ?
            """,
            (
                product.name,
                product.url,
                str(product.current_price),
                product.currency,
                product.store,
                product.id,
            ),
        )

        self._connection.commit()

        return product
