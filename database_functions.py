from Connector import get_connection
import streamlit as st
import pandas as pd

def get_all_sales():
    DB = get_connection()
    cursor = DB.cursor()
    get_all_sales_query = """
Select * from customer_sales
"""
    cursor.execute(get_all_sales_query)
    data = cursor.fetchall()
    column = [column[0] for column in cursor.description]
    cursor.close()
    DB.close()
    return pd.DataFrame(data, columns = column)

def get_admin_sales():
    DB = get_connection()
    cursor = DB.cursor()

    get_admin_sales_query = """
select * from customer_sales
where branch_id = %s
"""
    cursor.execute(get_admin_sales_query,(st.session_state.branch_id,))
    data = cursor.fetchall()
    column = [column[0] for column in cursor.description]
    cursor.close()
    DB.close()
    return pd.DataFrame(data, columns = column)

def get_payment_splits():
    DB = get_connection()
    cursor = DB.cursor()
    get_payment_splits_query = """
select * from payment_split
"""
    cursor.execute(get_payment_splits_query)
    data = cursor.fetchall()
    column = [column[0] for column in cursor.description]
    cursor.close()
    DB.close()
    return pd.DataFrame(data, columns = column)

def get_payment_splits_branch():
    DB = get_connection()
    cursor = DB.cursor()
    get_payment_splits_branch_query = """
select ps.* from payment_split ps
join customer_sales cs
on ps.sale_id = cs.sale_id
where branch_id = %s
"""
    cursor.execute(get_payment_splits_branch_query, (st.session_state.branch_id,))
    data = cursor.fetchall()
    column = [column[0] for column in cursor.description]
    cursor.close()
    DB.close()
    return pd.DataFrame(data, columns = column)
def get_all_branch():
    DB = get_connection()
    cursor = DB.cursor()

    get_all_branch_query = """
SELECT branch_id, branch_name from branch
"""
    cursor.execute(get_all_branch_query)
    data = cursor.fetchall()
    cursor.close()
    DB.close()
    return data

def get_all_pending_amount():
    DB = get_connection()
    cursor = DB.cursor()
    get_all_pending_amount_query = """
select cs.sale_id, b.branch_name, cs.name, cs.product_name, cs.pending_amount
from customer_sales cs
join branch b on cs.branch_id = b.branch_id
where cs.pending_amount > 0
order by cs.pending_amount desc
"""
    cursor.execute(get_all_pending_amount_query)
    data = cursor.fetchall()
    columns = [column[0] for column in cursor.description]
    cursor.close()
    DB.close()
    return pd.DataFrame(data, columns=columns)

def get_branchwise_pending_amount():
    DB = get_connection()
    cursor = DB.cursor()
    get_branchwise_pending_amount_query = """
select sale_id, name, product_name, pending_amount
from customer_sales
where branch_id = %s
and pending_amount > 0
order by pending_amount desc
"""
    cursor.execute(get_branchwise_pending_amount_query,(st.session_state.branch_id,))
    data = cursor.fetchall()
    columns = [column[0] for column in cursor.description]
    cursor.close()
    DB.close()
    return pd.DataFrame(data, columns=columns)