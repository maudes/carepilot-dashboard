import streamlit as st
import requests
import json

API_BASE = "http://localhost:8000/api/auth"

st.set_page_config(page_title="Verify")
st.title("Verify")

# 抽出驗證上下文
def get_verification_context():
    mode = st.query_params.get("mode", "register")
    email = st.session_state.get(f"{mode}_email")
    token = st.session_state.get(f"{mode}_token")
    return mode, email, token

mode, email, token = get_verification_context()

# 檢查必要資訊
if not email or not token:
    st.warning("Missing verification info. Please start from login or registration.")
    st.stop()

st.write(f"Verifying **{mode}** for: `{email}`")
otp = st.text_input("Enter the OTP sent to your email:")

# 驗證 OTP
if st.button("Verify"):
    if not otp or len(otp.strip()) < 4:
        st.warning("Please enter a valid OTP.")
    else:
        payload = {
            "token": token,
            "otp": otp.strip()
        }

        with st.spinner("Verifying OTP..."):
            try:
                res = requests.post(f"{API_BASE}/verify?mode={mode}", json=payload)
            except requests.RequestException as e:
                st.error(f"API request failed: {e}")
                st.stop()

        if res.status_code == 200:
            try:
                data = res.json()
                st.session_state["access_token"] = data["access_token"]
                st.session_state["refresh_token"] = data["refresh_token"]
                st.session_state["logged_in"] = True
                st.success(f"{mode.capitalize()} successful! Redirecting...")
                st.switch_page(data.get("redirect_to", "Home"))
            except (json.JSONDecodeError, KeyError):
                st.error("Response format error. Please contact support.")
        else:
            try:
                error = res.json()
                st.error(error.get("detail", "Unknown error"))
            except json.JSONDecodeError:
                st.error(f"Server replied with non-JSON format: {res.status_code}")
                st.code(res.text)
