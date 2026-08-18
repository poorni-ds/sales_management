import streamlit as st
from Connector import get_connection
from theme import apply_theme, section_header

st.set_page_config(page_title="New Sale | Sales Intelligence Hub", page_icon="🧾", layout="wide")
apply_theme()

# auth
if not st.session_state.get("logged_in", False):
    st.error("Logging out....")
    st.switch_page("login.py")

role = st.session_state.role
branch_id = st.session_state.branch_id

# access
if role not in ["Admin", "Super Admin"]:
    st.error("Only Admin and Super Admin can create New Sales Entry")
    st.stop()

st.title("🧾 New Sale & Payments")

# ---------------------------------------------------------------
# Branch selection for Super Admin — placed BEFORE the sale form
# so that whichever branch is picked here is the branch the new
# sale actually gets created in.
# ---------------------------------------------------------------
if role == "Super Admin":
    DB = get_connection()
    cursor = DB.cursor()

    fetch_query = """
    SELECT branch_id, branch_name
    FROM branch
    """
    cursor.execute(fetch_query)
    branch = cursor.fetchall()

    cursor.close()
    DB.close()

    branch_options = {
        branch_name: branch_id
        for branch_id, branch_name in branch
    }

    selected_branch = st.selectbox(
        "Select Branch",
        branch_options.keys()
    )

    branch_id = branch_options[selected_branch]

# ---------------------------------------------------------------
# Create New Sales Entry — an expander instead of a click-to-toggle
# button, so the form's open/closed state is visually obvious and
# doesn't require a second click to discover.
# ---------------------------------------------------------------
section_header("Create New Sales Entry")

with st.expander(f"➕ New sale for Branch ID {branch_id}", expanded=False):
    with st.form("Sales_Entry_Form"):
        col1, col2 = st.columns(2)
        with col1:
            name = st.text_input("Customer_Name")
            mobile_number = st.text_input("Mobile Number")
        with col2:
            product_name = st.text_input("Product_Name")
        col3, col4 = st.columns(2)
        with col3:
            gross_sales = st.number_input(
                "Gross_sales",
                min_value=0.0,
                step=100.0
            )
        with col4:
            received_amount = st.number_input(
                "Received_amount",
                min_value=0.0,
                step=100.0
            )
        submitted = st.form_submit_button("Add Sales", type="primary")

    # check before insert
    if submitted:
        if not name:
            st.error("Please Enter customer's name")
        elif gross_sales <= 0:
            st.error("Gross Sale must be greater than 0")
        elif received_amount > gross_sales:
            st.error("Received amount must not be greater than the gross sales")
        else:
            DB = get_connection()
            cursor = DB.cursor()
            New_sales_query = """
                INSERT INTO customer_sales(branch_id, name, mobile_number, product_name, gross_sales, received_amount)
                VALUES(%s, %s, %s, %s, %s, %s)
            """
            Values = (
                branch_id,
                name,
                mobile_number,
                product_name,
                gross_sales,
                received_amount
            )
            cursor.execute(New_sales_query, Values)
            DB.commit()
            cursor.close()
            DB.close()
            st.success("Sales entry created successfully! 🎉")

# ---------------------------------------------------------------
# Selecting an existing sale (for payment summary / adding a payment)
# ---------------------------------------------------------------
DB = get_connection()
cursor = DB.cursor(dictionary=True)

select_sales_id_query = """
SELECT
    sale_id,
    name,
    product_name,
    gross_sales,
    received_amount,
    pending_amount
FROM customer_sales
WHERE branch_id = %s
"""

cursor.execute(
    select_sales_id_query,
    (branch_id,)
)

sales = cursor.fetchall()

cursor.close()
DB.close()

if sales:

    section_header("Add a Payment")

    sale_options = {
        f"Sale ID: {sale['sale_id']} - "
        f"{sale['name']} - "
        f"{sale['product_name']}": sale
        for sale in sales
    }

    selected_sale_name = st.selectbox(
        "Select Sale",
        sale_options.keys()
    )

    selected_sale = sale_options[selected_sale_name]

    sale_id = selected_sale["sale_id"]

    with st.container(border=True):
        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric("Gross Sales", f"₹{selected_sale['gross_sales']:,.2f}")

        with col2:
            st.metric("Received Amount", f"₹{selected_sale['received_amount']:,.2f}")

        with col3:
            st.metric("Pending Amount", f"₹{selected_sale['pending_amount']:,.2f}")

        if selected_sale["pending_amount"] > 0:
            progress_fraction = min(
                float(selected_sale["received_amount"]) / float(selected_sale["gross_sales"]),
                1.0,
            )
            st.progress(progress_fraction, text=f"{progress_fraction*100:.0f}% collected")
        else:
            st.success("Fully collected ✅")

    # -----------------------------------------------------------
    # Add Payment Split — only shown when there's a sale selected,
    # since it needs sale_id / selected_sale to exist.
    # -----------------------------------------------------------
    with st.expander("💳 Add Payment Split", expanded=selected_sale["pending_amount"] > 0):

        with st.form("payment_split_form"):

            payment_date = st.date_input("Payment Date")

            amount_paid = st.number_input(
                "Amount Paid",
                min_value=0.0,
                step=100.0
            )

            payment_method = st.selectbox(
                "Payment Method",
                ["Cash", "UPI", "Card", "Bank Transfer"]
            )

            payment_submitted = st.form_submit_button("Add Payment", type="primary")

        if payment_submitted:

            if amount_paid <= 0:
                st.error("Payment amount must be greater than 0")

            elif amount_paid > selected_sale["pending_amount"]:
                st.error("Payment amount cannot be greater than pending amount")

            else:
                DB = get_connection()
                cursor = DB.cursor()

                payment_query = """
                    INSERT INTO payment_split
                    (sale_id, payment_date, amount_paid, payment_method)
                    VALUES (%s, %s, %s, %s)
                """

                values = (
                    sale_id,
                    payment_date,
                    amount_paid,
                    payment_method
                )

                cursor.execute(payment_query, values)
                DB.commit()

                cursor.close()
                DB.close()

                st.success("Payment split added successfully! 🎉")
                st.balloons()

else:
    st.info("No sales found for this branch.")
