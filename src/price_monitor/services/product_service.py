import logging
from datetime import datetime
from decimal import Decimal

from price_monitor.database.repositories.price_history_repository import (
    PriceHistoryRepository,
)
from price_monitor.database.repositories.product_repository import ProductRepository
from price_monitor.models import PriceRecord, Product
from price_monitor.scrapers.scraper_factory import ScraperFactory

logger = logging.getLogger(__name__)


class ProductService:
    """Service responsible for product operations."""

    def __init__(
        self,
        product_repository: ProductRepository,
        history_repository: PriceHistoryRepository,
    ) -> None:
        self._product_repository = product_repository
        self._history_repository = history_repository

    def add_product(self, url: str) -> Product:
        """Scrape and persist a new product."""

        scraper = ScraperFactory.get_scraper(url)
        product_data = scraper.scrape(url)

        now = datetime.now()
        product = Product(
            id=None,
            name=product_data.name,
            url=product_data.url,
            current_price=product_data.price,
            currency=product_data.currency,
            store=product_data.store,
            created_at=now,
            last_updated=now,
        )

        saved_product = self._product_repository.save(product)
        self._history_repository.save(
            PriceRecord(
                id=None,
                product_id=saved_product.id,
                price=saved_product.current_price,
                recorded_at=now,
            )
        )

        return saved_product

    def list_products(self) -> list[Product]:
        """Return all monitored products."""

        return self._product_repository.get_all()

    def update_product(self, product_id: int) -> Product:
        """Update a monitored product."""

        product = self._product_repository.get_by_id(product_id)

        if product is None:
            raise ValueError("Product not found.")

        scraper = ScraperFactory.get_scraper(product.url)
        product_data = scraper.scrape(product.url)

        product.last_updated = datetime.now()
        old_price = product.current_price
        new_price = product_data.price

        product.name = product_data.name
        product.current_price = product_data.price
        product.currency = product_data.currency
        product.store = product_data.store

        self._product_repository.update(product)

        if old_price != new_price:
            record = PriceRecord(
                id=None,
                product_id=product.id,
                price=product.current_price,
                recorded_at=datetime.now(),
            )

            self._history_repository.save(record)

        return product

    def update_all_products(self) -> list[tuple[str, str]]:
        """Update all monitored products.

        Returns:
            List of (product_name, error_message) for failed updates.
        """

        errors: list[tuple[str, str]] = []

        products = self.list_products()

        for product in products:
            try:
                self.update_product(product.id)

            except Exception as error:
                logger.exception(
                    "Product update failed: id=%s name=%r",
                    product.id,
                    product.name,
                )
                errors.append(
                    (
                        product.name,
                        str(error),
                    )
                )

        return errors

    def get_price_history(
        self,
        product_id: int,
    ) -> list[PriceRecord]:
        """Return the price history of a product."""

        return self._history_repository.get_by_product(product_id)

    def set_target_price(self, product_id: int, target_price: Decimal | None) -> Product:
        """Set or clear a product's price target."""

        product = self._product_repository.get_by_id(product_id)
        if product is None:
            raise ValueError("Product not found.")
        if target_price is not None and target_price <= 0:
            raise ValueError("Target price must be greater than zero.")
        product.target_price = target_price
        return self._product_repository.update(product)

    def remove_product(self, product_id: int) -> bool:
        """Remove a monitored product."""

        return self._product_repository.delete(product_id)
