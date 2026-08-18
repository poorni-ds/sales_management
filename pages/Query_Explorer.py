import streamlit as st
import pandas as pd
from Connector import get_connection

# auth
if not st.session_state.get("logged_in", False):
    st.error("Please login first!")
    st.switch_page("login.py")

role = st.session_state.role
branch_id = st.session_state.branch_id

st.title("📊 Analytical Query Explorer")
st.caption("Pick a report to run. Only predefined, safe queries are exposed here — "
           "there is no free-text SQL box, so this can't be used to query outside "
           "what your role is allowed to see.")

# ---------------------------------------------------------------
# Every query is parameterized where it needs branch scoping.
# Admin only ever sees queries scoped to their own branch;
# cross-branch comparison queries are Super-Admin only.
# ---------------------------------------------------------------

QUERIES_COMMON = {
    "All my branch's sales": (
        "SELECT * FROM customer_sales WHERE branch_id = %s",
        True,
    ),
    "Open sales only": (
        "SELECT * FROM customer_sales WHERE branch_id = %s AND status = 'Open'",
        True,
    ),
    "Sales with pending amount > 5000": (
        "SELECT * FROM customer_sales WHERE branch_id = %s AND pending_amount > 5000",
        True,
    ),
    "Top 3 highest gross sales": (
        "SELECT * FROM customer_sales WHERE branch_id = %s ORDER BY gross_sales DESC LIMIT 3",
        True,
    ),
    "Monthly sales summary": (
        """SELECT YEAR(date) AS year, MONTH(date) AS month,
                  SUM(gross_sales) AS total_gross,
                  SUM(received_amount) AS total_received
           FROM customer_sales
           WHERE branch_id = %s
           GROUP BY YEAR(date), MONTH(date)
           ORDER BY year, month""",
        True,
    ),
    "Payment method-wise collection": (
        """SELECT ps.payment_method, SUM(ps.amount_paid) AS total_collected
           FROM payment_split ps
           JOIN customer_sales cs ON ps.sale_id = cs.sale_id
           WHERE cs.branch_id = %s
           GROUP BY ps.payment_method""",
        True,
    ),
    "Sales with payment method used": (
        """SELECT cs.sale_id, cs.name, cs.product_name, ps.payment_method, ps.amount_paid
           FROM customer_sales cs
           JOIN payment_split ps ON cs.sale_id = ps.sale_id
           WHERE cs.branch_id = %s""",
        True,
    ),
}

QUERIES_SUPER_ADMIN_ONLY = {
    "All branches": (
        "SELECT * FROM branch",
        False,
    ),
    "All payment splits": (
        "SELECT * FROM payment_split",
        False,
    ),
    "Total gross sales (all branches)": (
        "SELECT SUM(gross_sales) AS total_gross_sales FROM customer_sales",
        False,
    ),
    "Total received amount (all branches)": (
        "SELECT SUM(received_amount) AS total_received FROM customer_sales",
        False,
    ),
    "Total pending amount (all branches)": (
        "SELECT SUM(pending_amount) AS total_pending FROM customer_sales",
        False,
    ),
    "Sale count per branch": (
        """SELECT b.branch_name, COUNT(cs.sale_id) AS total_sales_count
           FROM branch b
           LEFT JOIN customer_sales cs ON b.branch_id = cs.branch_id
           GROUP BY b.branch_name""",
        False,
    ),
    "Average gross sales amount": (
        "SELECT AVG(gross_sales) AS avg_gross_sales FROM customer_sales",
        False,
    ),
    "Branch-wise total gross sales": (
        """SELECT b.branch_name, SUM(cs.gross_sales) AS total_gross
           FROM customer_sales cs
           JOIN branch b ON cs.branch_id = b.branch_id
           GROUP BY b.branch_name
           ORDER BY total_gross DESC""",
        False,
    ),
    "Branch with the highest total gross sales": (
        """SELECT b.branch_name, SUM(cs.gross_sales) AS total_gross
           FROM customer_sales cs
           JOIN branch b ON cs.branch_id = b.branch_id
           GROUP BY b.branch_name
           ORDER BY total_gross DESC
           LIMIT 1""",
        False,
    ),
    "Sales with branch admin name": (
        """SELECT cs.sale_id, cs.name, cs.gross_sales, b.branch_admin_name
           FROM customer_sales cs
           JOIN branch b ON cs.branch_id = b.branch_id""",
        False,
    ),
}

available_queries = dict(QUERIES_COMMON)
if role == "Super Admin":
    available_queries.update(QUERIES_SUPER_ADMIN_ONLY)

selected_label = st.selectbox("Choose a report", list(available_queries.keys()))
sql, needs_branch_param = available_queries[selected_label]

if st.button("Run Query", use_container_width=True):
    DB = get_connection()
    cursor = DB.cursor()

    if needs_branch_param:
        cursor.execute(sql, (branch_id,))
    else:
        cursor.execute(sql)

    rows = cursor.fetchall()
    columns = [col[0] for col in cursor.description]

    cursor.close()
    DB.close()

    df = pd.DataFrame(rows, columns=columns)

    if df.empty:
        st.info("No results for this query.")
    else:
        st.dataframe(df, use_container_width=True, hide_index=True)
