import streamlit as st

# 初始化登入狀態
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

# 側邊欄版權資訊
with st.sidebar:
    st.write("All rights reserved © 2025")


# 根據登入狀態決定可見頁面
if st.session_state.logged_in:
    pages = {
        "Pages": [
            st.Page("pages/home.py", title="Home"),
            st.Page("pages/profile.py", title="My Profile"),
            st.Page("pages/daily.py", title="My Daily Record"),
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
            st.Page("pages/verify.py", title="Verify"),
        ]
    }

# 執行導覽
pg = st.navigation(pages)
pg.run()
