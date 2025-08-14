import streamlit as st

st.set_page_config(page_title="My History")
st.title("My History")
if not st.session_state.get("logged_in"):
    st.switch_page("Login")
