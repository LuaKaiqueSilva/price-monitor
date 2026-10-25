import tempfile
import unittest
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from unittest.mock import patch

from price_monitor.database.connection import get_connection


class DatabaseConnectionTests(unittest.TestCase):
    def test_connection_can_be_used_by_a_streamlit_rerun_thread(self) -> None:
        with tempfile.TemporaryDirectory() as temp_directory:
            database_file = Path(temp_directory) / "price_monitor.db"
            with patch(
                "price_monitor.database.connection.DATABASE_FILE", database_file
            ):
                connection = get_connection()

            try:
                with ThreadPoolExecutor(max_workers=1) as executor:
                    result = executor.submit(
                        lambda: connection.execute("SELECT 1").fetchone()[0]
                    ).result()
                self.assertEqual(result, 1)
            finally:
                connection.close()


if __name__ == "__main__":
    unittest.main()
