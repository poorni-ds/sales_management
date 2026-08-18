import streamlit as st
import plotly.graph_objects as go
from Connector import get_connection
from database_functions import get_all_sales, get_payment_splits, get_admin_sales, get_payment_splits_branch
from theme import apply_theme, kpi_row, section_header, styled_sales_table

st.set_page_config(page_title="Dashboard | Sales Intelligence Hub", page_icon="📊", layout="wide")
apply_theme()

if not st.session_state.get("logged_in", False):
    st.error("Logging out....")
    st.switch_page("login.py")

col_title, col_logout = st.columns([8, 1])
with col_title:
    st.title("📊 Sales Analysis Dashboard")
with col_logout:
    st.write("")
    if st.button("Log out", use_container_width=True):
        st.session_state.clear()
        st.switch_page("login.py")

role = st.session_state.role
branch_id = st.session_state.branch_id

if role == "Super Admin":
    df = get_all_sales()
    payment_df = get_payment_splits()
    scope_label = "All Branches"
elif role == "Admin":
    df = get_admin_sales()
    payment_df = get_payment_splits_branch()
    scope_label = "Your Branch"
else:
    df = None
    payment_df = None
    scope_label = "Unknown"

if df is not None and not df.empty:
    total_sales = df["gross_sales"].sum()
    total_received = df["received_amount"].sum()
    total_pending = df["pending_amount"].sum()
    total_transactions = len(df)
    open_count = int((df["status"] == "Open").sum())
    close_count = int((df["status"] == "Close").sum())

    st.caption(f"Scope: **{scope_label}**")

    kpi_row([
        {"label": "Total Sales", "value": f"₹{total_sales:,.0f}", "accent": "blue"},
        {"label": "Total Received", "value": f"₹{total_received:,.0f}", "accent": "green"},
        {"label": "Total Pending", "value": f"₹{total_pending:,.0f}", "accent": "amber"},
        {"label": "Transactions", "value": f"{total_transactions}", "accent": "purple"},
    ])

    section_header("Collections Overview")

    chart_col, status_col = st.columns([2, 1])

    with chart_col:
        fig = go.Figure(data=[
            go.Bar(name="Received", x=["Amount"], y=[total_received], marker_color="#12B76A"),
            go.Bar(name="Pending", x=["Amount"], y=[total_pending], marker_color="#F79009"),
        ])
        fig.update_layout(
            barmode="stack",
            height=280,
            margin=dict(l=10, r=10, t=30, b=10),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
        )
        st.plotly_chart(fig, use_container_width=True)

    with status_col:
        fig2 = go.Figure(data=[go.Pie(
            labels=["Open", "Close"],
            values=[open_count, close_count],
            hole=0.55,
            marker_colors=["#F79009", "#12B76A"],
        )])
        fig2.update_layout(
            height=280,
            margin=dict(l=10, r=10, t=30, b=10),
            showlegend=True,
        )
        st.plotly_chart(fig2, use_container_width=True)

    section_header("Recent Sales")
    styled_sales_table(df.sort_values("sale_id", ascending=False).head(10))

else:
    st.info("No sales data yet — create your first sale from the **Create Sales Entry** page.")
