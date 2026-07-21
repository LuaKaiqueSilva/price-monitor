from price_monitor.database.connection import get_connection
from price_monitor.database.repositories.product_repository import ProductRepository
from price_monitor.services.product_service import ProductService


def main() -> None:
    connection = get_connection()

    repository = ProductRepository(connection)

    service = ProductService(repository)

    url = input("Enter product URL: ")

    product = service.add_product(url)

    print()
    print("Product added successfully!")
    print(product)


if __name__ == "__main__":
    main()
