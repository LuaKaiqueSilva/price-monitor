class UnsupportedStoreError(Exception):
    """Raised when no scraper supports the provided URL."""


class DuplicateProductError(Exception):
    """Raised when trying to add a product that already exists."""
