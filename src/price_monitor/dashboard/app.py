import logging
import time
from decimal import Decimal

import pandas as pd
import plotly.express as px
import streamlit as st
from streamlit_autorefresh import st_autorefresh

from price_monitor.database.connection import get_connection
from price_monitor.database.repositories.price_history_repository import (
    PriceHistoryRepository,
)
from price_monitor.database.repositories.product_repository import ProductRepository
from price_monitor.demo import build_demo_data
from price_monitor.exceptions import (
    DuplicateProductError,
    ProductNotFoundError,
    ScraperConnectionError,
    UnsupportedStoreError,
)
from price_monitor.services.product_service import ProductService
from price_monitor.utils.csv_export import build_price_history_csv

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)

@st.cache_resource
def get_product_service() -> ProductService:
    connection = get_connection()
    product_repository = ProductRepository(connection)
    history_repository = PriceHistoryRepository(connection)
    return ProductService(product_repository, history_repository)


def show_update_errors(errors: list[tuple[str, str]]) -> None:
    """Display product update failures in the dashboard."""

    st.warning(f"Updated with {len(errors)} error(s).")

    for product_name, message in errors:
        st.write(f"• **{product_name}**")
        st.caption(message)


# -----------------------------------------------------------------------------
# Sidebar
# -----------------------------------------------------------------------------

st.sidebar.title("⚙️ Settings")

demo_mode = st.sidebar.toggle("Demo mode", value=False, key="demo_mode")
service = None if demo_mode else get_product_service()

auto_update = st.sidebar.toggle(
    "Auto update",
    value=False,
    disabled=demo_mode,
)

refresh_minutes = st.sidebar.selectbox(
    "Refresh interval",
    options=[1, 5, 10, 30],
    index=1,
    format_func=lambda x: f"{x} minute" if x == 1 else f"{x} minutes",
)

st.sidebar.divider()

if "last_update" not in st.session_state:
    st.session_state.last_update = None

# -----------------------------------------------------------------------------
# Auto update
# -----------------------------------------------------------------------------

if auto_update and not demo_mode:
    refresh_count = st_autorefresh(
        interval=refresh_minutes * 60 * 1000,
        key="auto_refresh",
    )

    if refresh_count > 0:
        with st.spinner("Auto updating products..."):
            errors = service.update_all_products()

        st.session_state.last_update = time.strftime("%H:%M:%S")
        if errors:
            show_update_errors(errors)

if demo_mode:
    st.info("Demo mode is on. Sample data is not saved, and store actions are disabled.")

# -----------------------------------------------------------------------------
# Sidebar information
# -----------------------------------------------------------------------------

if demo_mode:
    st.sidebar.caption("Data source: sample data")
elif st.session_state.last_update is None:
    st.sidebar.caption("Last update: Never")
else:
    st.sidebar.caption(f"Last update: {st.session_state.last_update}")

# -----------------------------------------------------------------------------

st.title("Price Monitor")

url = st.text_input(
    "Product URL",
    placeholder="https://www.kabum.com.br/produto/...",
    disabled=demo_mode,
)

if st.button("Add Product", disabled=demo_mode):
    try:
        product = service.add_product(url)

        st.success("Product added successfully!")

    except DuplicateProductError as error:
        st.warning(str(error))

    except UnsupportedStoreError as error:
        st.error(str(error))

    except ScraperConnectionError as error:
        st.error(str(error))

    except ProductNotFoundError as error:
        st.error(str(error))
    except Exception:
        logger.exception("Could not add product")
        st.error("Could not add the product. Check the URL and try again.")

st.subheader("Update Products")

if st.button("🔄 Update All Products", disabled=demo_mode):
    with st.spinner("Updating products..."):
        errors = service.update_all_products()

    st.session_state.last_update = time.strftime("%H:%M:%S")

    if errors:
        show_update_errors(errors)

    else:
        st.success("All products updated successfully!")

if demo_mode:
    products, demo_history = build_demo_data()
else:
    products = service.list_products()
    demo_history = {}

prices = [float(product.current_price) for product in products]

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Products", len(products))

with col2:
    st.metric(
        "Average Price",
        f"R$ {sum(prices)/len(prices):.2f}" if prices else "-",
    )

with col3:
    st.metric(
        "Lowest Price",
        f"R$ {min(prices):.2f}" if prices else "-",
    )

with col4:
    st.metric(
        "Highest Price",
        f"R$ {max(prices):.2f}" if prices else "-",
    )

st.divider()

search_col, sort_col = st.columns([3, 1])

with search_col:
    search = st.text_input(
        "🔍 Search",
        placeholder="Search by product name...",
    )

    if search:
        products = [
            product for product in products if search.lower() in product.name.lower()
        ]


with sort_col:
    sort = st.selectbox(
        "Sort by",
        (
            "Newest",
            "Oldest",
            "Lowest price",
            "Highest price",
            "Name",
        ),
    )
    if sort == "Newest":
        products.sort(
            key=lambda p: p.created_at,
            reverse=True,
        )

    elif sort == "Oldest":
        products.sort(
            key=lambda p: p.created_at,
        )

    elif sort == "Lowest price":
        products.sort(
            key=lambda p: p.current_price,
        )

    elif sort == "Highest price":
        products.sort(
            key=lambda p: p.current_price,
            reverse=True,
        )

    elif sort == "Name":
        products.sort(
            key=lambda p: p.name.lower(),
        )

st.divider()

st.subheader("Monitored Products")

if not products:
    st.info("No monitored products yet.\n\n" "Add your first product above.")

for product in products:
    with st.container(border=True):
        st.markdown(f"### {product.name}")
        colp, cols, cola, coll = st.columns(4)
        with colp:
            st.write("**Price:**")
            st.write(f"R$ {product.current_price}")
        with cols:
            st.write("**Store:**")
            st.write(f"{product.store}")
        with cola:
            st.write("**Added:**")
            st.write(f"{product.created_at.strftime('%d/%m/%Y %H:%M')}")
        with coll:
            st.write("**Last Updated:**")

            if product.last_updated:
                st.write(product.last_updated.strftime("%d/%m/%Y %H:%M"))
            else:
                st.write("-")

        target_reached = (
            product.target_price is not None
            and product.current_price <= product.target_price
        )
        if target_reached:
            st.success(f"Target reached: R$ {product.target_price:.2f}")

        with st.form(f"target_form_{product.id}"):
            target_enabled = st.checkbox(
                "Notify me in the dashboard at my target price",
                value=product.target_price is not None,
                disabled=demo_mode,
                key=f"target_enabled_{product.id}",
            )
            target_value = st.number_input(
                "Target price (R$)",
                min_value=0.01,
                value=float(product.target_price or product.current_price),
                step=10.0,
                disabled=demo_mode or not target_enabled,
                key=f"target_value_{product.id}",
            )
            save_target = st.form_submit_button(
                "Save price target",
                disabled=demo_mode,
            )

        if save_target:
            service.set_target_price(
                product.id,
                Decimal(str(target_value)) if target_enabled else None,
            )
            st.success("Price target saved." if target_enabled else "Price target removed.")
            st.rerun()

        if not demo_mode:
            st.link_button(
                "Open product page",
                product.url,
            )
        col_update, col_remove = st.columns(2)

        with col_update:
            if st.button(
                "🔄 Update",
                key=f"update_{product.id}",
                width="stretch",
                disabled=demo_mode,
            ):

                with st.spinner("Updating product..."):
                    try:
                        service.update_product(product.id)
                        st.session_state.last_update = time.strftime("%H:%M:%S")
                        st.success("Product updated successfully!")
                        st.rerun()

                    except (
                        ScraperConnectionError,
                        ProductNotFoundError,
                    ) as error:
                        st.error(str(error))

        with col_remove:
            if st.button(
                "🗑 Remove",
                key=f"remove_{product.id}",
                width="stretch",
                disabled=demo_mode,
            ):
                service.remove_product(product.id)
                st.success("Product removed successfully!")
                st.rerun()

        with st.expander(
            "📈 Price History",
            expanded=False,
        ):
            history = (
                demo_history[product.id]
                if demo_mode
                else service.get_price_history(product.id)
            )

            if not history:
                st.info("No price history available.")

            else:
                history_df = pd.DataFrame(
                    [
                        {
                            "Date": record.recorded_at,
                            "Price": float(record.price),
                        }
                        for record in history
                    ]
                )

                history_df = history_df.sort_values("Date")
                current_price = history_df["Price"].iloc[-1]
                lowest_price = history_df["Price"].min()
                highest_price = history_df["Price"].max()

                if len(history_df) > 1:
                    previous_price = history_df["Price"].iloc[-2]
                    delta = current_price - previous_price
                else:
                    delta = None

                col_current, col_low, col_high = st.columns(3)

                with col_current:
                    st.metric(
                        "Current Price",
                        f"R$ {current_price:.2f}",
                        delta=None if delta is None else f"{delta:+.2f}",
                    )

                with col_low:
                    st.metric(
                        "Lowest Price",
                        f"R$ {lowest_price:.2f}",
                    )

                with col_high:
                    st.metric(
                        "Highest Price",
                        f"R$ {highest_price:.2f}",
                    )

                fig = px.line(
                    history_df,
                    x="Date",
                    y="Price",
                    markers=True,
                )

                fig.update_traces(
                    line_width=3,
                    marker_size=8,
                )

                fig.update_layout(
                    title="Price History",
                    xaxis_title="Date",
                    yaxis_title="Price (R$)",
                    hovermode="x unified",
                    height=420,
                    margin=dict(l=20, r=20, t=40, b=20),
                )

                st.plotly_chart(
                    fig,
                    width="stretch",
                    key=f"history_chart_{product.id}",
                )
                table_df = history_df.copy()

                table_df["Date"] = table_df["Date"].dt.strftime("%d/%m/%Y %H:%M")

                table_df["Price"] = table_df["Price"].map(
                    lambda value: f"R$ {value:.2f}"
                )

                st.dataframe(
                    table_df,
                    width="stretch",
                    hide_index=True,
                )
                st.download_button(
                    "Download history as CSV",
                    data=build_price_history_csv(product, history),
                    file_name=f"price-history-{product.id or 'demo'}.csv",
                    mime="text/csv",
                    key=f"history_csv_{product.id}",
                )
