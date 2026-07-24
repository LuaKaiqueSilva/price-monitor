class DuplicateProductError(Exception):
    """Raised when trying to add a product that is already monitored."""


class ProductNotFoundError(Exception):
    """Raised when a product cannot be found."""
