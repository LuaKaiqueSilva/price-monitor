from price_monitor.database.connection import get_connection
from price_monitor.database.repositories.price_history_repository import (
    PriceHistoryRepository,
)
from price_monitor.database.repositories.product_repository import ProductRepository
from price_monitor.services.product_service import ProductService


def main() -> None:
    connection = get_connection()

    product_repository = ProductRepository(connection)
    history_repository = PriceHistoryRepository(connection)

    service = ProductService(
        product_repository,
        history_repository,
    )

    url = input("Enter product URL: ")

    product = service.add_product(url)

    print()
    print("Product added successfully!")
    print(product)


if __name__ == "__main__":
    main()
