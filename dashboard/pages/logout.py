import streamlit as st

st.title("Logout")

if st.button("Confirm Logout"):
    st.session_state.clear()
    st.success("Successfully left!")
    st.rerun()
