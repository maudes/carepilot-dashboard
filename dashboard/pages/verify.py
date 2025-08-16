# dashboard/pages/verify.py
import streamlit as st
import requests

st.set_page_config(page_title="Verify")

# 檢查是否有 OTP email 與 token
otp_email = st.session_state.get("otp_email")
otp_token = st.session_state.get("otp_token")
mode = st.session_state.get("mode", "login")

st.title("Verify OTP")

if not otp_email or not otp_token:
    st.warning(
        """
        You need to request an OTP first.
        Please go to Register or Login page to request an OTP before verifying.
        """
    )
    st.stop()

# 顯示 email 註記
st.write(f"Verifying email: `{otp_email}`")

# OTP 輸入與驗證
otp = st.text_input("Enter OTP")
if st.button("Verify"):
    payload = {
        "otp": otp,
        "token": otp_token
    }
    res = requests.post(
        f"http://localhost:8000/api/auth/verify?mode={mode}",
        json=payload
    )
    if res.status_code == 200:
        st.session_state.access_token = res.json()["access_token"]
        st.session_state.logged_in = True
        st.success("Verification successful!")
        # st.switch_page("pages/profile.py")
        st.rerun()
    else:
        st.error(res.json().get("detail", "Verification failed"))
