import streamlit as st

st.title("My History")
if not st.session_state.get("logged_in"):
    st.switch_page("login")
