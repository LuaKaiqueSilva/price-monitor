from datetime import datetime

from price_monitor.database.repositories.product_repository import ProductRepository
from price_monitor.models import Product
from price_monitor.scrapers.scraper_factory import ScraperFactory


class ProductService:
    """Service responsible for product operations."""

    def __init__(self, repository: ProductRepository) -> None:
        self._repository = repository

    def add_product(self, url: str) -> Product:
        """Scrape and persist a product."""

        scraper = ScraperFactory.get_scraper(url)

        product_data = scraper.scrape(url)

        product = Product(
            id=None,
            name=product_data.name,
            url=product_data.url,
            current_price=product_data.price,
            currency=product_data.currency,
            store=product_data.store,
            created_at=datetime.now(),
        )

        return self._repository.save(product)
