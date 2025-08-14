import streamlit as st
import requests

st.set_page_config(page_title="Home")
if not st.session_state.get("logged_in"):
    st.error("Please login first.")
    st.switch_page("pages/login.py")

# Main app title - Dashboard
headers = {
    "Authorization": f"Bearer {st.session_state.get('access_token')}"
}
res = requests.get("http://localhost:8000/api/protected", headers=headers)


st.title("My Health :blue[Gaol]!")
st.write(f"Welcome {st.session_state.get('email', 'User')}, it's your _personal health dashboard_!")


default_goal = "Be Happy & Be Healthy!"
goal = st.text_input("Please enter your health goal: ", value=default_goal)

st.button("save")
