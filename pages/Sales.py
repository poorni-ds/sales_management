import streamlit as st
from database_functions import get_all_sales, get_admin_sales
from theme import apply_theme, section_header, styled_sales_table

st.set_page_config(page_title="Sales | Sales Intelligence Hub", page_icon="🧾", layout="wide")
apply_theme()

if not st.session_state.get("logged_in", False):
    st.error("Please login first ! ")
    st.switch_page("login.py")

if st.session_state.logged_in:
    role = st.session_state.role

st.title("🧾 Sales Records")

df = None
if role == "Super Admin":
    df = get_all_sales()
elif role == "Admin":
    df = get_admin_sales()
else:
    st.error("Role not found")

if df is not None:

    if df.empty:
        st.info("No sales records yet.")
    else:
        filter_col1, filter_col2 = st.columns([1, 2])

        with filter_col1:
            status_choice = st.selectbox("Status", ["All", "Open", "Close"])

        with filter_col2:
            search_term = st.text_input("Search by customer name or product", placeholder="e.g. Chennai, DA, Ramesh")

        filtered_df = df.copy()

        if status_choice != "All":
            filtered_df = filtered_df[filtered_df["status"] == status_choice]

        if search_term:
            mask = (
                filtered_df["name"].astype(str).str.contains(search_term, case=False, na=False)
                | filtered_df["product_name"].astype(str).str.contains(search_term, case=False, na=False)
            )
            filtered_df = filtered_df[mask]

        section_header(f"{len(filtered_df)} of {len(df)} sales shown")
        styled_sales_table(filtered_df)
