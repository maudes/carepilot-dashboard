import streamlit as st

st.set_page_config(page_title="My Health Statistics")
st.title("My Health Statistics")
if not st.session_state.get("logged_in"):
    st.switch_page("pages/login.py")
