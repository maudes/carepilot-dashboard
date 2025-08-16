import streamlit as st
import requests

# 1. 設定頁面 config（這應該是最先做的）
st.set_page_config(page_title="Home")

# 2. 檢查是否登入，否則導向登入頁面
if not st.session_state.get("logged_in"):
    st.error("Please login first.")
    st.switch_page("pages/login.py")

# 3. 顯示主頁內容
st.title("My Health :blue[Gaol]!")
st.write(f"Welcome {st.session_state.get('email', 'User')}, it's your _personal health dashboard_!")

default_goal = "Be Happy & Be Healthy!"
goal = st.text_input("Please enter your health goal: ", value=default_goal)

st.button("save")
