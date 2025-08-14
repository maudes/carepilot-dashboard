import streamlit as st

st.set_page_config(page_title="My Daily Records")
st.title("My Daily Records")
if not st.session_state.get("logged_in"):
    st.switch_page("Login")
