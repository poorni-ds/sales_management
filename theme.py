import streamlit as st
import pandas as pd


def apply_theme():
    """Kept so every page can still call apply_theme() without edits.
    All actual theming (colors, font) now lives in .streamlit/config.toml —
    Streamlit's own native theming mechanism — instead of injected CSS/HTML,
    so this function intentionally does nothing."""
    pass


def kpi_row(items):
    """items: list of dicts, each with keys: label, value, accent (ignored —
    kept only so existing call sites don't need to change).
    Renders using Streamlit's native st.metric, one per column."""
    cols = st.columns(len(items))
    for col, item in zip(cols, items):
        with col:
            st.metric(item["label"], item["value"])


def section_header(text):
    """Native Streamlit subheader — no HTML."""
    st.subheader(text)


def styled_sales_table(df: pd.DataFrame):
    """Renders a sales-like DataFrame using Streamlit's native interactive
    grid (sortable, resizable columns) with currency formatting and a
    progress bar on pending_amount, and an emoji status marker —
    all native st.dataframe / column_config, no HTML."""
    if df.empty:
        st.info("No records to show.")
        return

    display_df = df.copy()

    if "status" in display_df.columns:
        display_df["status"] = display_df["status"].map(
            {"Open": "🟠 Open", "Close": "🟢 Close"}
        ).fillna(display_df["status"])

    column_config = {}
    for money_col in ["gross_sales", "received_amount"]:
        if money_col in display_df.columns:
            column_config[money_col] = st.column_config.NumberColumn(
                money_col.replace("_", " ").title(), format="₹ %.2f"
            )
    if "pending_amount" in display_df.columns:
        max_pending = max(float(display_df["pending_amount"].max()), 1.0)
        column_config["pending_amount"] = st.column_config.ProgressColumn(
            "Pending Amount",
            format="₹ %.2f",
            min_value=0.0,
            max_value=max_pending,
        )

    st.dataframe(
        display_df,
        use_container_width=True,
        hide_index=True,
        column_config=column_config,
    )
