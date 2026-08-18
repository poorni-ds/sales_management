import streamlit as st
import plotly.graph_objects as go
from database_functions import get_all_branch, get_all_sales, get_admin_sales
from theme import apply_theme, kpi_row, section_header

st.set_page_config(page_title="Analytics | Sales Intelligence Hub", page_icon="📈", layout="wide")
apply_theme()

if not st.session_state.get("logged_in", False):
    st.error("Please login first")
    st.switch_page("login.py")

role = st.session_state.role
branch_id = st.session_state.branch_id

st.title("📈 Branch Analytics")

if role == "Super Admin":

    df = get_all_sales()
    branches = get_all_branch()

    # Branch name -> branch ID (renamed loop variables so this never
    # shadows the outer `branch_id` set from st.session_state above)
    branch_options = {"All Branches": None}
    for b_id, b_name in branches:
        branch_options[b_name] = b_id

    selected_branch = st.selectbox("Select Branch", branch_options.keys())
    selected_branch_id = branch_options[selected_branch]

    if selected_branch_id is None:
        filtered_df = df
    else:
        filtered_df = df[df["branch_id"] == selected_branch_id]

    branch_analysis = filtered_df.groupby("branch_id").agg(
        total_sales=("gross_sales", "sum"),
        total_received=("received_amount", "sum"),
        total_pending=("pending_amount", "sum"),
        transactions=("sale_id", "count")
    ).reset_index()

    branch_analysis["branch_name"] = branch_analysis["branch_id"].map(dict(branches))

    branch_analysis = branch_analysis[
        ["branch_name", "total_sales", "total_received", "total_pending", "transactions"]
    ]

    total_sales = filtered_df["gross_sales"].sum()
    total_received = filtered_df["received_amount"].sum()
    total_pending = filtered_df["pending_amount"].sum()
    total_transactions = len(filtered_df)

    kpi_row([
        {"label": "Total Sales", "value": f"₹{total_sales:,.0f}", "accent": "blue"},
        {"label": "Total Received", "value": f"₹{total_received:,.0f}", "accent": "green"},
        {"label": "Total Pending", "value": f"₹{total_pending:,.0f}", "accent": "amber"},
        {"label": "Transactions", "value": f"{total_transactions}", "accent": "purple"},
    ])

    if not branch_analysis.empty and selected_branch_id is None and len(branch_analysis) > 1:
        section_header("Branch Comparison")
        fig = go.Figure(data=[
            go.Bar(name="Total Sales", x=branch_analysis["branch_name"], y=branch_analysis["total_sales"], marker_color="#2E90FA"),
        ])
        fig.update_layout(
            height=320,
            margin=dict(l=10, r=10, t=20, b=10),
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
        )
        st.plotly_chart(fig, use_container_width=True)

    section_header("Branch Breakdown")
    st.dataframe(
        branch_analysis,
        use_container_width=True,
        hide_index=True,
        column_config={
            "total_sales": st.column_config.NumberColumn("Total Sales", format="₹ %.2f"),
            "total_received": st.column_config.NumberColumn("Total Received", format="₹ %.2f"),
            "total_pending": st.column_config.NumberColumn("Total Pending", format="₹ %.2f"),
        },
    )

elif role == "Admin":
    df = get_admin_sales()
    branches = get_all_branch()
    branch_dict = dict(branches)
    branch_name = branch_dict.get(branch_id, "Unknown Branch")

    st.caption(f"Scope: **{branch_name}**")

    if df.empty:
        st.info("No sales data yet for this branch.")
    else:
        total_sales = df["gross_sales"].sum()
        total_received = df["received_amount"].sum()
        total_pending = df["pending_amount"].sum()
        total_transactions = len(df)

        kpi_row([
            {"label": "Total Sales", "value": f"₹{total_sales:,.0f}", "accent": "blue"},
            {"label": "Total Received", "value": f"₹{total_received:,.0f}", "accent": "green"},
            {"label": "Total Pending", "value": f"₹{total_pending:,.0f}", "accent": "amber"},
            {"label": "Transactions", "value": f"{total_transactions}", "accent": "purple"},
        ])

        branch_sales = df.groupby("branch_id").agg(
            total_sales=("gross_sales", "sum"),
            total_received=("received_amount", "sum"),
            total_pending=("pending_amount", "sum"),
            transactions=("sale_id", "count")
        ).reset_index()

        branch_sales["branch_name"] = branch_sales["branch_id"].map(branch_dict)
        branch_sales = branch_sales[
            ["branch_name", "total_sales", "total_received", "total_pending", "transactions"]
        ]

        section_header("Branch Summary")
        st.dataframe(
            branch_sales,
            use_container_width=True,
            hide_index=True,
            column_config={
                "total_sales": st.column_config.NumberColumn("Total Sales", format="₹ %.2f"),
                "total_received": st.column_config.NumberColumn("Total Received", format="₹ %.2f"),
                "total_pending": st.column_config.NumberColumn("Total Pending", format="₹ %.2f"),
            },
        )
else:
    st.error("Role not found")
