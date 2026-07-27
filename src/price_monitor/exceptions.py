class DuplicateProductError(Exception):
    """Raised when trying to add a product that is already monitored."""


class UnsupportedStoreError(Exception):
    """Raised when no scraper supports the provided URL."""


class ScraperConnectionError(Exception):
    """Raised when the scraper cannot connect to the store."""


class ProductNotFoundError(Exception):
    """Raised when the product page cannot be parsed."""
