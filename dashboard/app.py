import streamlit as st

# Sidebar content
with st.sidebar:
    st.write("All rights reserved © 2025")

if st.session_state.get("logged_in"):
    pages = {
        "Pages": [
            st.Page("pages/home.py", title="CarePilot"),
            st.Page("pages/profile.py", title="My Profile"),
            st.Page("pages/daily.py", title="My Daily Records"),
            st.Page("pages/history.py", title="My History"),
            st.Page("pages/stats.py", title="My Health Statistics"),
            st.Page("pages/logout.py", title="Logout"),
        ]
    }
else:
    pages = {
        "Pages": [
            st.Page("pages/login.py", title="Login"),
            st.Page("pages/register.py", title="Register"),
        ]
    }

pg = st.navigation(pages)
pg.run()