import streamlit as st
import requests


st.set_page_config(page_title="Home")


# Check Login state
def require_login():
    if not st.session_state.get("logged_in") or not st.session_state.get("access_token"):
        st.warning("You must be logged in to access this page.")
        st.switch_page("pages/login.py")
        st.rerun()


require_login()


# Auto-refresh access token
def auto_refresh(method, url, json=None):
    access_token = st.session_state.get("access_token")
    refresh_token = st.session_state.get("refresh_token")

    headers = {"Authorization": f"Bearer {access_token}"}
    response = requests.request(method, url, headers=headers, json=json)

    if response.status_code == 401 and refresh_token:
        refresh_headers = {"Authorization": f"Bearer {refresh_token}"}
        refresh_res = requests.post("http://localhost:8000/api/auth/token-refresh", headers=refresh_headers)

        if refresh_res.status_code == 200:
            new_token = refresh_res.json().get("access_token")
            st.session_state["access_token"] = new_token
            st.session_state["logged_in"] = True
            st.rerun()  # 重新執行整個 app，下一輪會用新的 access_token
        else:
            st.session_state.clear()
            st.error("Session expired. Please login again.")
            st.switch_page("pages/login.py")
            st.rerun()

    return response


# API endpoint
goal_url = "http://localhost:8000/api/goal/me"


# Get Today's Record
res = auto_refresh("get", goal_url)
user_goal = res.json() if res.status_code == 200 else ""

# Display
st.title("My Health :blue[Goal]!")
st.write(f"Welcome {st.session_state.get('email', 'User')}, it's your _personal health dashboard_!")

default_goal = "Be Happy & Be Healthy!"
goal = st.text_input("Please enter your health goal: ", value=user_goal)

update = st.button("Update")
if update:
    payload = {"goal_text": goal if goal else default_goal}
    res = auto_refresh("put", goal_url, json=payload)
    if res.status_code == 200:
        st.success("Goal updated successfully!")
    else:
        st.error("Failed to update goal. Please try again.")
