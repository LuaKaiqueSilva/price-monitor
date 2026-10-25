import sqlite3
import unittest

from price_monitor.database.schema import initialize_database


class DatabaseMigrationTests(unittest.TestCase):
    def test_adds_target_price_to_an_existing_products_table(self) -> None:
        connection = sqlite3.connect(":memory:")
        connection.row_factory = sqlite3.Row
        connection.execute(
            """
            CREATE TABLE products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                url TEXT NOT NULL UNIQUE,
                current_price TEXT NOT NULL,
                currency TEXT NOT NULL,
                store TEXT NOT NULL,
                created_at TEXT NOT NULL,
                last_updated TEXT
            )
            """
        )

        initialize_database(connection)
        columns = {
            row["name"]
            for row in connection.execute("PRAGMA table_info(products)").fetchall()
        }

        self.assertIn("target_price", columns)
        connection.close()


if __name__ == "__main__":
    unittest.main()
