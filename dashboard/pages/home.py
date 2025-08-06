import streamlit as st
# Main app title - Dashboard
st.title("My Health :blue[Gaol]!")
st.write(f"Welcome {st.session_state.get('email', 'User')}, it's your _personal health dashboard_!")

if not st.session_state.get("logged_in"):
    st.switch_page("login")

default_goal = "Be Happy & Be Healthy!"
goal = st.text_input("Please enter your health goal: ", value=default_goal)

st.button("save")
