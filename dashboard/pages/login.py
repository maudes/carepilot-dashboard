# pages/login.py
import streamlit as st
import requests

st.set_page_config(page_title="Login")
st.title("Login")
email = st.text_input("Email")
if st.button("Send OTP"):
    res = requests.post("http://localhost:8000/api/auth/login-request", json={"email": email})
    if res.status_code == 200:
        st.session_state.otp_email = email
        st.session_state.otp_token = res.json()["token"]
        st.session_state.mode = "login"
        st.switch_page("pages/verify.py")
    else:
        st.error(res.json()["detail"])
