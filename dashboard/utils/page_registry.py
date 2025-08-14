# dashboard/utils/page_registry.py

PAGE_TITLES = {
    "login": "Login",
    "register": "Register",
    "verify": "Verify",
    "home": "CarePilot",
    "profile": "My Profile",
    "daily": "My Daily Records",
    "history": "My History",
    "stats": "My Health Statistics",
    "logout": "Logout",
}

def switch_to(key: str):
    import streamlit as st
    title = PAGE_TITLES.get(key)
    if title:
        st.switch_page(title)
    else:
        st.error(f"Page key '{key}' not found.")
