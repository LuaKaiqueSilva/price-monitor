import sqlite3


def initialize_database(connection: sqlite3.Connection) -> None:
    """Create the database schema if it does not exist."""

    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            url TEXT NOT NULL UNIQUE,
            current_price TEXT NOT NULL,
            currency TEXT NOT NULL,
            store TEXT NOT NULL,
            created_at TEXT NOT NULL,
            last_updated TEXT
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS price_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_id INTEGER NOT NULL,
            price TEXT NOT NULL,
            recorded_at TEXT NOT NULL,
            FOREIGN KEY(product_id) REFERENCES products(id) ON DELETE CASCADE
        )
    """)

    connection.commit()
