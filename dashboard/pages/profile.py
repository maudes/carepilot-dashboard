# dashboard/pages/profile.py

import streamlit as st
import requests

st.set_page_config(page_title="My Profile")
st.title("My Profile")

# 檢查登入狀態
access_token = st.session_state.get("access_token")
if not st.session_state.get("logged_in") or not access_token:
    st.switch_page("pages/login.py")

headers = {
    "Authorization": f"Bearer {access_token}"
}

# 取得個人資料
profile_url = "http://localhost:8000/api/profile/me"
res = requests.get(profile_url, headers=headers)

if res.status_code != 200:
    print(res.status_code)
    st.error("Failed to load profile.")
    st.stop()

profile_data = res.json()

# 顯示並編輯個人資料
with st.form("profile_form"):
    name = st.text_input("Name", value=profile_data.get("name", ""))
    email = st.text_input("Email", value=profile_data.get("email", ""))
    age = st.number_input("Age", value=profile_data.get("age") or 0, min_value=0)
    gender = st.selectbox("Gender", ["", "Male", "Female", "Other"], index=["", "Male", "Female", "Other"].index(profile_data.get("gender", "")))
    bio = st.text_area("Bio", value=profile_data.get("bio", ""))

    submitted = st.form_submit_button("Update Profile")
    if submitted:
        payload = {
            "name": name,
            "email": email,
            "age": age,
            "gender": gender,
            "bio": bio
        }
        update_res = requests.put(profile_url, headers=headers, json=payload)
        if update_res.status_code == 200:
            st.success("Profile updated successfully.")
            st.rerun()
        else:
            st.error(f"Update failed: {update_res.json().get('detail', 'Unknown error')}")

# 危險區塊：刪除帳號
st.markdown("---")
st.subheader("⚠️ Danger Zone")

if st.button("Delete My Account"):
    confirm = st.checkbox("I understand this action is irreversible.")
    if confirm:
        delete_res = requests.delete(profile_url, headers=headers)
        if delete_res.status_code == 200:
            st.session_state.clear()
            st.success("Your account has been deleted.")
            st.rerun()
        else:
            st.error(f"Delete failed: {delete_res.json().get('detail', 'Unknown error')}")
