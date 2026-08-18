import streamlit as st
from Connector import get_connection
from security import verify_password
from theme import apply_theme

st.set_page_config(page_title="Sales Intelligence Hub", page_icon="📊", layout="centered")
apply_theme()

#session

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

#getuser

def get_user(username):

    DB = get_connection()
    cursor = DB.cursor()

    query = """
    SELECT user_id, username, password, branch_id, role, email
    FROM users
    WHERE username = %s
    """
#tuple containing a value without it its a variable
    cursor.execute(query, (username,))

    user = cursor.fetchone() #one row at a time

    cursor.close()
    DB.close()

    return user


col_l, col_mid, col_r = st.columns([1, 2, 1])

with col_mid:
    st.title("📊 Sales Intelligence Hub")
    st.caption("Sign in to your branch dashboard")

    with st.container(border=True):
        username = st.text_input("Username", placeholder="Enter your username")
        password = st.text_input("Password", type="password", placeholder="Enter your password")

        login_clicked = st.button("Log In", use_container_width=True, type="primary")

        if login_clicked:
            user = get_user(username)
            if user is None:
                st.error("Username not Found")
            elif verify_password(password, user[2]):
                st.session_state.logged_in = True
                st.session_state.user_id = user[0]
                st.session_state.username = user[1]
                st.session_state.branch_id = user[3]
                st.session_state.role = user[4]
                st.success("Login successful! 🎉")
                st.switch_page("pages/dashboards.py")
            else:
                st.error("Incorrect password ❌")
