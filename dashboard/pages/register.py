# dashboard/pages/register.py
import streamlit as st
import requests

st.set_page_config(page_title="Register")
st.title("Register")
email = st.text_input("Email")
if st.button("Send OTP"):
    res = requests.post("http://localhost:8000/api/auth/register-request", json={"email": email})
    if res.status_code == 200:
        st.session_state.otp_email = email
        st.session_state.otp_token = res.json()["token"]
        st.session_state.mode = "register"
        st.success("OTP sent successfully!")
        st.switch_page("pages/verify.py")
    else:
        st.error(res.json().get("detail", "Failed to send OTP"))
