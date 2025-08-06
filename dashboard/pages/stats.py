import streamlit as st

st.title("My Health Statistics")
if not st.session_state.get("logged_in"):
    st.switch_page("login")
