import streamlit as st

st.title("🔐 Login")

email = st.text_input("Email")
OTP_password = st.text_input("OTP password", type="password")

if st.button("Login"):
    if email == "admin" and OTP_password == "1234":
        st.session_state["logged_in"] = True
        st.session_state["email"] = email
        st.success("Welcome!")
        st.rerun()
    else:
        st.error("Failed. Please check your email and OTP password again.")
