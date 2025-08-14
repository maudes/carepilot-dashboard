import streamlit as st

st.set_page_config(page_title="Logout")
st.title("Logout")
if not st.session_state.get("logged_in"):
    st.switch_page("Login")

if st.button("Logout"):
    st.session_state.clear()
    st.success("You're logged out.")
    st.switch_page("Login")
