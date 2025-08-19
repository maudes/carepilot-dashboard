# dashboard/pages/logout.py

import streamlit as st
import requests

st.set_page_config(page_title="Logout")
st.title("Logout")

# 檢查是否已登入且有 access_token
access_token = st.session_state.get("access_token")
email = st.session_state.get("email")

if not st.session_state.get("logged_in") or not access_token:
    st.warning("You are not logged in. Redirecting to login page...")
    st.switch_page("pages/login.py")

# 顯示目前登入帳號
st.markdown(f"Logged in as: `{email}`")

# 登出按鈕
if st.button("Logout"):
    headers = {
        "Authorization": f"Bearer {access_token}"
    }

    try:
        res = requests.post("http://localhost:8000/api/auth/logout", headers=headers)
        if res.status_code == 200:
            st.session_state.clear()
            st.success("You have been logged out successfully.")
            st.rerun()
        else:
            error_msg = res.json().get("message", "Unknown error")
            st.error(f"Logout failed: {error_msg}")
    except Exception as e:
        st.error(f"Logout error: {e}")
