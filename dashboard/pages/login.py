import streamlit as st
import requests
from utils.page_registry import switch_to

API_BASE = "http://localhost:8000/api/auth"

st.set_page_config(page_title="Login")
st.title("Login")

# 輸入 email
email = st.text_input("Enter your email:")

# 點擊按鈕請求 OTP
if st.button("Get one-time-password"):
    if not email:
        st.warning("Please enter your email before requesting OTP.")
    else:
        with st.spinner("Requesting OTP..."):
            try:
                res = requests.post(f"{API_BASE}/login-request", json={"email": email})
            except requests.RequestException as e:
                st.error(f"API request failed: {e}")
                st.stop()

        # 顯示回應內容（debug 用）
        st.write("Status:", res.status_code)
        st.write("Headers:", dict(res.headers))
        st.write("Body:", res.text)

        if res.status_code == 200:
            try:
                data = res.json()
            except ValueError:
                st.error("Invalid JSON response from server.")
                st.stop()

            # 儲存 email 與 token
            st.session_state["login_email"] = email
            st.session_state["login_token"] = data.get("token")

            # 設定跳轉模式（讓 verify.py 知道是 login）
            st.query_params.update({"mode": "login"})

            # 設定跳轉 flag
            st.session_state["go_to_verify"] = True
            st.success(f"OTP sent to {email}. Redirecting to verification...")
            st.rerun()
        else:
            try:
                error_detail = res.json().get("detail", "Unknown error")
            except ValueError:
                error_detail = f"Invalid JSON response: {res.text}"
            st.error(error_detail)
