import streamlit as st

st.set_page_config(page_title="My Profile")
st.title("My Profile")
if not st.session_state.get("logged_in"):
    st.switch_page("pages/login.py")
