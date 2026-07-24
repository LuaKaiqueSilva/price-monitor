import streamlit as st

from price_monitor.database.connection import get_connection
from price_monitor.database.repositories.price_history_repository import (
    PriceHistoryRepository,
)
from price_monitor.database.repositories.product_repository import ProductRepository
from price_monitor.exceptions import DuplicateProductError
from price_monitor.services.product_service import ProductService

connection = get_connection()
product_repository = ProductRepository(connection)
history_repository = PriceHistoryRepository(connection)
service = ProductService(
    product_repository,
    history_repository,
)

st.title("Price Monitor")

url = st.text_input("Product URL", placeholder="https://www.kabum.com.br/produto/...")

if st.button("Add Product"):
    try:
        product = service.add_product(url)

        st.success("Product added successfully!")
        st.write(product)

    except DuplicateProductError as error:
        st.warning(str(error))

    except Exception as error:
        st.error(str(error))
st.subheader("Update Products")

if st.button("🔄 Update All Products"):
    with st.spinner("Updating products..."):
        service.update_all_products()

    st.success("Products updated successfully!")
    st.rerun()

st.subheader("Monitored Products")

products = service.list_products()

st.subheader("Monitored Products")

for product in products:
    with st.container(border=True):
        st.markdown(f"### {product.name}")

        st.write(f"**Price:** R$ {product.current_price}")
        st.write(f"**Store:** {product.store}")
        st.write(f"**Added:** {product.created_at.strftime('%d/%m/%Y %H:%M')}")

        col1, col2 = st.columns(2)

        with col1:
            if st.button(
                "📜 View History",
                key=f"history_{product.id}",
            ):
                history = service.get_price_history(product.id)

                history_rows = [
                    {
                        "Date": record.recorded_at.strftime("%d/%m/%Y %H:%M"),
                        "Price": f"R$ {record.price}",
                    }
                    for record in history
                ]

                st.dataframe(history_rows, use_container_width=True)

        with col2:
            if st.button(
                "🗑 Remove",
                key=f"remove_{product.id}",
            ):
                service.remove_product(product.id)
                st.success("Product removed successfully!")
                st.rerun()
