import sqlite3
from pathlib import Path

DATABASE_FILE = Path("data") / "price_monitor.db"


def get_connection() -> sqlite3.Connection:
    """Create and return a SQLite database connection."""

    DATABASE_FILE.parent.mkdir(parents=True, exist_ok=True)

    connection = sqlite3.connect(DATABASE_FILE)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")

    return connection
