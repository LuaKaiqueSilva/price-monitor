import os
import tempfile
import unittest
from pathlib import Path

from streamlit.testing.v1 import AppTest


class DashboardDemoModeTests(unittest.TestCase):
    def test_demo_mode_renders_sample_products_without_creating_database(self) -> None:
        project_root = Path(__file__).resolve().parents[1]
        original_directory = Path.cwd()

        with tempfile.TemporaryDirectory() as temp_directory:
            try:
                os.chdir(temp_directory)
                app = AppTest.from_file(
                    str(project_root / "src/price_monitor/dashboard/app.py")
                )
                app.session_state["demo_mode"] = True
                app.run()

                self.assertEqual(list(app.exception), [])
                self.assertEqual(
                    [metric.value for metric in app.metric if metric.label == "Products"],
                    ["3"],
                )
                self.assertTrue(
                    any("Demo mode is on" in message.value for message in app.info)
                )
                self.assertFalse(Path("data/price_monitor.db").exists())
            finally:
                os.chdir(original_directory)


if __name__ == "__main__":
    unittest.main()
