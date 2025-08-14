import streamlit as st


API_BASE = "http://localhost:8000/api/auth"

st.set_page_config(page_title="Register")
st.title("Register")

new_email = st.text_input("Email")
new_OTP = st.text_input("OTP password", type="password")

if st.button("Register"):
    # 模擬註冊成功（不儲存）
    st.success(f"Email: {new_email} has been registered successfully!")
    st.switch_page("login")