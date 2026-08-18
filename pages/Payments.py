import streamlit as st
import plotly.graph_objects as go
from database_functions import get_payment_splits, get_payment_splits_branch, get_all_pending_amount, get_branchwise_pending_amount
from theme import apply_theme, section_header

st.set_page_config(page_title="Payments | Sales Intelligence Hub", page_icon="💰", layout="wide")
apply_theme()

#auth
if not st.session_state.get("logged_in", False):
    st.error("Please login first!")
    st.switch_page("login.py")

#user details
role = st.session_state.role
branch_id = st.session_state.branch_id

st.title("💰 Payments")

tab_splits, tab_pending = st.tabs(["Payment Splits", "Pending Payments"])

with tab_splits:
    if role == "Super Admin":
        df = get_payment_splits()
    elif role == "Admin":
        df = get_payment_splits_branch()
    else:
        df = None
        st.error("Role not Found")

    if df is not None:
        if df.empty:
            st.info("No payments recorded yet.")
        else:
            section_header("Collection by Payment Method")
            method_totals = df.groupby("payment_method")["amount_paid"].sum().reset_index()

            fig = go.Figure(data=[go.Pie(
                labels=method_totals["payment_method"],
                values=method_totals["amount_paid"],
                hole=0.5,
            )])
            fig.update_layout(height=320, margin=dict(l=10, r=10, t=10, b=10))
            st.plotly_chart(fig, use_container_width=True)

            section_header("All Payment Splits")
            st.dataframe(
                df,
                use_container_width=True,
                hide_index=True,
                column_config={
                    "amount_paid": st.column_config.NumberColumn("Amount Paid", format="₹ %.2f"),
                },
            )

with tab_pending:
    if role == "Super Admin":
        pending_df = get_all_pending_amount()
    elif role == "Admin":
        pending_df = get_branchwise_pending_amount()
    else:
        pending_df = None
        st.error("Role not Found")

    if pending_df is not None:
        if pending_df.empty:
            st.success("No pending payments — everything's collected! 🎉")
        else:
            section_header(f"{len(pending_df)} sale(s) with pending balance")
            st.dataframe(
                pending_df,
                use_container_width=True,
                hide_index=True,
                column_config={
                    "pending_amount": st.column_config.ProgressColumn(
                        "Pending Amount",
                        format="₹ %.2f",
                        min_value=0.0,
                        max_value=float(pending_df["pending_amount"].max()),
                    ),
                },
            )
