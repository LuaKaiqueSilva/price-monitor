import streamlit as st

from price_monitor.database.connection import get_connection
from price_monitor.database.repositories.product_repository import ProductRepository
from price_monitor.services.product_service import ProductService
from dataclasses import asdict

connection = get_connection()
repository = ProductRepository(connection)
service = ProductService(repository)

st.title("Price Monitor")

url = st.text_input(
    "Product URL",
    placeholder="https://www.kabum.com.br/produto/..."
)

if st.button("Add Product"):
    try:
        product = service.add_product(url)

        st.success("Product added successfully!")

        st.write(product)

    except Exception as error:
        st.error(str(error))

products = service.list_products()

st.subheader("Update Products")

if st.button("Update Products"):
    st.warning("This feature is not implemented yet.")

st.subheader("Monitored Products")

rows = [
    {
        "Product": product.name,
        "Price": f"R$ {product.current_price}",
        "Store": product.store,
        "URL": product.url,
        "Added": product.created_at.strftime("%d/%m/%Y %H:%M"),
    }
    for product in products
]

st.dataframe(rows, use_container_width=True)
